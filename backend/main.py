from fastapi import FastAPI, HTTPException
import torch
import joblib
import pandas as pd
import numpy as np
import re
from fastapi.middleware.cors import CORSMiddleware

# Import our live data pipeline
from etherscan_client import get_transaction_history, get_erc20_history
from feature_engineering import extract_kaggle_features

# Import our GNN architecture
from gnn_training import FraudGNN

app = FastAPI(title="Ethereum GNN Live Inference API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows any frontend to connect
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Setup: Load the scaler and the model
try:
    scaler = joblib.load('kaggle_scaler.joblib')
    num_kaggle_features = len(scaler.mean_) # Will be 45
    
    model = FraudGNN(num_features=num_kaggle_features)
    # weights_only=True is a modern PyTorch security best practice
    model.load_state_dict(torch.load('gnn_fraud_model.pt', weights_only=True))
    model.eval() # Set model to inference mode
    print(f"GNN Model and Scaler loaded! Expecting {num_kaggle_features} features.")
except Exception as e:
    print(f"Startup Warning: {e}. Ensure you ran gnn_training.py first.")

def is_valid_eth_address(address: str) -> bool:
    """Validates that a string is a properly formatted Ethereum address."""
    return bool(re.match(r'^0x[a-fA-F0-9]{40}$', address))

@app.get("/")
def read_root():
    return {"message": "GNN Live Inference Server. Go to /docs to test it out!"}

@app.get("/analyze/{wallet_address}")
def analyze_wallet(wallet_address: str, max_records: int = 200):
    if not is_valid_eth_address(wallet_address):
        raise HTTPException(status_code=400, detail="Invalid Ethereum address format.")

    # Fetch BOTH live Normal and ERC20 data
    raw_normal_txs = get_transaction_history(wallet_address, max_records=max_records)
    raw_erc20_txs = get_erc20_history(wallet_address, max_records=max_records)
    
    if not raw_normal_txs and not raw_erc20_txs:
        raise HTTPException(status_code=404, detail="No transactions found on chain.")

    # Extract perfectly mapped Kaggle Features
    try:
        features_df = extract_kaggle_features(wallet_address, raw_normal_txs, raw_erc20_txs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting features: {str(e)}")

    # Ensure we have exactly 45 features in the right order
    expected_columns = list(scaler.feature_names_in_) if hasattr(scaler, 'feature_names_in_') else features_df.columns
    features_ordered = features_df[expected_columns].values

    # Normalize and convert to PyTorch Tensor
    scaled_features = scaler.transform(features_ordered)
    x_new = torch.tensor(scaled_features, dtype=torch.float)

    # Graph Inference (Still using self-loop for API speed)
    edge_index_new = torch.tensor([[0], [0]], dtype=torch.long)

    with torch.no_grad():
        log_probs = model(x_new, edge_index_new)
        probs = torch.exp(log_probs)[0] 
        fraud_probability = round(probs[1].item() * 100, 2)
        prediction = 1 if probs[1].item() > 0.5 else 0

    return {
        "wallet_address": wallet_address,
        "prediction": "Fraudulent/Suspicious" if prediction == 1 else "Normal",
        "fraud_probability_percent": fraud_probability,
        "normal_txs_analyzed": len(raw_normal_txs) if raw_normal_txs else 0,
        "erc20_txs_analyzed": len(raw_erc20_txs) if raw_erc20_txs else 0,
        "top_features": {
            # Wrapped Pandas/NumPy types in Python's native int() and float() to prevent JSON crashes!
            "Total Txs": int(features_df['total transactions (including tnx to create contract'].iloc[0]),
            "ETH Balance": float(features_df['total ether balance'].iloc[0]),
            "ERC20 Txs": int(features_df['Total ERC20 tnxs'].iloc[0])
        }
    }