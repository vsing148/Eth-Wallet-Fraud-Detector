import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
import joblib

# Import our graph builder
from graph_feature_engineering import load_and_build_graph
class FraudGNN(torch.nn.Module):
    # 3 layer Graph CNN

    def __init__(self, num_features, hidden_channels=128):
        super(FraudGNN, self).__init__()
        # First Layer: Input to Hidden
        self.conv1 = GCNConv(num_features, hidden_channels)
        # Second Layer: Hidden to Hidden (Extra capacity for complex patterns)
        self.conv2 = GCNConv(hidden_channels, hidden_channels)
        # Third Layer: Hidden to Output (2 classes: Normal vs Fraud)
        self.conv3 = GCNConv(hidden_channels, 2)
    
    def forward(self, x, edge_index):
        # Layer 1
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=0.5, training=self.training)
        
        # Layer 2
        x = self.conv2(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=0.5, training=self.training)
        
        # Layer 3
        x = self.conv3(x, edge_index)
        return F.log_softmax(x, dim=1)

def train_gnn():
    data, scaler = load_and_build_graph()
    if data is None: return

    # Saves the scaler to normalize live API data
    joblib.dump(scaler, 'kaggle_scaler.joblib')

    # Moves the model to GPU if available
    # Sets up the Model, Optimizer, and Loss Function
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') 
    model = FraudGNN(num_features=data.num_node_features).to(device) 
    data = data.to(device) 


    # Test/Train Split in Pytorch
    num_nodes = data.num_nodes
    indices = torch.randperm(num_nodes)
    train_mask = torch.zeros(num_nodes, dtype=torch.bool)
    train_mask[indices[:int(0.8 * num_nodes)]] = True
    test_mask = ~train_mask

    # Penalize the model heavily if it misclassifies the minority 'Fraud' class
    train_labels = data.y[train_mask]
    num_normal = (train_labels == 0).sum().item()
    num_fraud = (train_labels == 1).sum().item()
    total_train = len(train_labels)

    # Weight formula: Total Samples / (Number of Classes * Class Samples)
    weight_normal = total_train / (2.0 * num_normal)
    weight_fraud = total_train / (2.0 * num_fraud)
    class_weights = torch.tensor([weight_normal, weight_fraud], dtype=torch.float).to(device)

    # Adam optimizer with a learning rate of 0.01 and weight decay of 5e-4
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=5e-4)

    print(f"\n--- Starting Enhanced GNN Training ---")
    print(f"Training on {total_train} nodes. Applied Fraud Weight: {weight_fraud:.2f}x")
    
    model.train()
    # Increased epochs from 100 to 400 to allow deeper convergence
    for epoch in range(1, 401): 
        optimizer.zero_grad()
        out = model(data.x, data.edge_index) 
        
        # Pass the calculated class weights to the loss function
        loss = F.nll_loss(out[train_mask], data.y[train_mask], weight=class_weights)
        loss.backward()
        optimizer.step()

        if epoch % 25 == 0:
            print(f'Epoch: {epoch:03d}, Loss: {loss:.4f}')

    # Evaluate Accuracy
    model.eval()
    pred = model(data.x, data.edge_index).argmax(dim=1)
    
    # Calculate overall accuracy
    correct = (pred[test_mask] == data.y[test_mask]).sum()
    acc = int(correct) / int(test_mask.sum())
    
    print(f'\nFinal Test Accuracy: {acc:.4f}')

    # Export the trained weights
    torch.save(model.state_dict(), 'gnn_fraud_model.pt')
    print("Model saved to 'gnn_fraud_model.pt'")

if __name__ == "__main__":
    train_gnn()