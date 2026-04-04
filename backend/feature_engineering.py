import pandas as pd
import numpy as np

# These are the exact 45 cleaned column names our PyTorch scaler expects
KAGGLE_COLUMNS = [
    'Avg min between sent tnx', 'Avg min between received tnx',
    'Time Diff between first and last (Mins)', 'Sent tnx', 'Received Tnx',
    'Number of Created Contracts', 'Unique Received From Addresses',
    'Unique Sent To Addresses', 'min value received', 'max value received',
    'avg val received', 'min val sent', 'max val sent', 'avg val sent',
    'min value sent to contract', 'max val sent to contract',
    'avg value sent to contract', 'total transactions (including tnx to create contract',
    'total Ether sent', 'total ether received', 'total ether sent contracts', 
    'total ether balance', 'Total ERC20 tnxs', 'ERC20 total Ether received',
    'ERC20 total ether sent', 'ERC20 total Ether sent contract',
    'ERC20 uniq sent addr', 'ERC20 uniq rec addr', 'ERC20 uniq sent addr.1', 
    'ERC20 uniq rec contract addr', 'ERC20 avg time between sent tnx', 
    'ERC20 avg time between rec tnx', 'ERC20 avg time between rec 2 tnx', 
    'ERC20 avg time between contract tnx', 'ERC20 min val rec', 'ERC20 max val rec', 
    'ERC20 avg val rec', 'ERC20 min val sent', 'ERC20 max val sent', 
    'ERC20 avg val sent', 'ERC20 min val sent contract', 'ERC20 max val sent contract',
    'ERC20 avg val sent contract', 'ERC20 uniq sent token name', 'ERC20 uniq rec token name'
]
 
def extract_kaggle_features(wallet_address: str, normal_txs: list, erc20_txs: list):
    """Maps live Etherscan JSON into the exact 45 features required by the Kaggle GNN."""
    
    wallet_address = wallet_address.lower()
    
    # 1. Initialize our feature row with absolute zeros (matches df.fillna(0))
    features = {col: 0.0 for col in KAGGLE_COLUMNS}
    
    # --- PROCESS NORMAL ETH TRANSACTIONS ---
    if normal_txs:
        df = pd.DataFrame(normal_txs)
        df['value'] = df['value'].astype(float) / 1e18 # Convert Wei to ETH
        df['timeStamp'] = pd.to_datetime(df['timeStamp'].astype(int), unit='s')
        
        sent = df[df['from'].str.lower() == wallet_address]
        received = df[df['to'].str.lower() == wallet_address]
        contracts = df[df['contractAddress'] != ""] # Approximating contract creations
        
        features['total transactions (including tnx to create contract'] = len(df)
        features['Sent tnx'] = len(sent)
        features['Received Tnx'] = len(received)
        features['Number of Created Contracts'] = len(contracts)
        
        if len(df) > 1:
            time_diff = (df['timeStamp'].max() - df['timeStamp'].min()).total_seconds() / 60
            features['Time Diff between first and last (Mins)'] = time_diff

        if not received.empty:
            features['Unique Received From Addresses'] = received['from'].nunique()
            features['min value received'] = received['value'].min()
            features['max value received'] = received['value'].max()
            features['avg val received'] = received['value'].mean()
            features['total ether received'] = received['value'].sum()
            features['Avg min between received tnx'] = received['timeStamp'].diff().dt.total_seconds().mean() / 60 or 0
            
        if not sent.empty:
            features['Unique Sent To Addresses'] = sent['to'].nunique()
            features['min val sent'] = sent['value'].min()
            features['max val sent'] = sent['value'].max()
            features['avg val sent'] = sent['value'].mean()
            features['total Ether sent'] = sent['value'].sum()
            features['Avg min between sent tnx'] = sent['timeStamp'].diff().dt.total_seconds().mean() / 60 or 0

        features['total ether balance'] = features['total ether received'] - features['total Ether sent']

    # --- PROCESS ERC20 TOKEN TRANSACTIONS ---
    if erc20_txs:
        token_df = pd.DataFrame(erc20_txs)
        token_df['value'] = token_df['value'].astype(float) / 1e18 # Approximate normalization
        token_df['timeStamp'] = pd.to_datetime(token_df['timeStamp'].astype(int), unit='s')
        
        token_sent = token_df[token_df['from'].str.lower() == wallet_address]
        token_rec = token_df[token_df['to'].str.lower() == wallet_address]
        
        features['Total ERC20 tnxs'] = len(token_df)
        features['ERC20 uniq sent token name'] = token_sent['tokenName'].nunique() if not token_sent.empty else 0
        features['ERC20 uniq rec token name'] = token_rec['tokenName'].nunique() if not token_rec.empty else 0
        
        if not token_rec.empty:
            features['ERC20 total Ether received'] = token_rec['value'].sum()
            features['ERC20 max val rec'] = token_rec['value'].max()
            features['ERC20 min val rec'] = token_rec['value'].min()
            features['ERC20 avg val rec'] = token_rec['value'].mean()
            features['ERC20 uniq rec addr'] = token_rec['from'].nunique()
            features['ERC20 avg time between rec tnx'] = token_rec['timeStamp'].diff().dt.total_seconds().mean() / 60 or 0
            
        if not token_sent.empty:
            features['ERC20 total ether sent'] = token_sent['value'].sum()
            features['ERC20 max val sent'] = token_sent['value'].max()
            features['ERC20 min val sent'] = token_sent['value'].min()
            features['ERC20 avg val sent'] = token_sent['value'].mean()
            features['ERC20 uniq sent addr'] = token_sent['to'].nunique()
            features['ERC20 uniq sent addr.1'] = token_sent['to'].nunique() # Dataset duplicate anomaly
            features['ERC20 avg time between sent tnx'] = token_sent['timeStamp'].diff().dt.total_seconds().mean() / 60 or 0

    # Fill any calculation NaNs with 0 (division by zero protections)
    df_result = pd.DataFrame([features]).fillna(0)
    return df_result