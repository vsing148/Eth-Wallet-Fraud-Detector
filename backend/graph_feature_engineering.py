import pandas as pd
import numpy as np
import torch
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import kneighbors_graph
from torch_geometric.data import Data

def load_and_build_graph(csv_path="transaction_dataset.csv", k_neighbors=5):
    print("Loading Kaggle dataset...")
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: Could not find {csv_path}. Did you download it from Kaggle?")
        return None, None

    # We clean the data by dropping columns that are not predictive
    cols_to_drop = [
        'Unnamed: 0', 
        'Index', 
        'Address', 
        'ERC20 most sent token type', 
        'ERC20_most_rec_token_type'
    ]
    df = df.drop(columns=[col for col in cols_to_drop if col in df.columns])

    # Tensors cannot contain text
    df = df.select_dtypes(exclude=['object'])

    # Fill missing values with 0
    df = df.fillna(0)

    # The Kaggle dataset uses 'FLAG' as the target variable (0 = Normal, 1 = Fraud)
    y_raw = df['FLAG'].values
    X_raw = df.drop(columns=['FLAG']).values

    # Scale between 0 and 1 to train network
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)

    x = torch.tensor(X_scaled, dtype=torch.float)
    y = torch.tensor(y_raw, dtype=torch.long)

    print("Building the Graph using Scikit-Learn (Bypassing torch-cluster)...")
    
    # Use Scikit-Learn to find the connections (returns a SciPy sparse matrix)
    A = kneighbors_graph(X_scaled, n_neighbors=k_neighbors, mode='connectivity', include_self=False)
    
    # Convert the SciPy matrix into PyTorch edge_index format [2, num_edges]
    coo = A.tocoo()
    edge_index = torch.tensor(np.vstack((coo.row, coo.col)), dtype=torch.long)

    # Create PyTorch geometric dataset
    graph_data = Data(x=x, edge_index=edge_index, y=y)

    print(f"\nGraph built successfully!")
    print(f"Nodes (Wallets): {graph_data.num_nodes}")
    print(f"Edges (Connections): {graph_data.num_edges}")
    print(f"Features per node: {graph_data.num_node_features}")
    
    return graph_data, scaler

if __name__ == "__main__":
    # Test the pipeline
    graph, scaler = load_and_build_graph()