<div align="center">

# 🛡️ Recon

### Real-Time Ethereum Fraud Detection via Graph Neural Networks

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-%23EE4C2C.svg?logo=PyTorch&logoColor=white)](https://pytorch.org/)
[![React](https://img.shields.io/badge/react-Vite-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)

**Recon** is a production-ready Web3 machine learning pipeline that uses a **Graph Neural Network (GNN)** to detect fraudulent Ethereum wallets in real-time.

[Live Application](https://eth-wallet-fraud-detector.vercel.app) • [Report Bug](#) • [Request Feature](#)

</div>

---

## 📺 Dashboard

<div align="center">
  <img src="https://via.placeholder.com/900x500/090c0b/00e676?text=Recon+Ethereum+Dashboard+Screenshot" alt="Recon Dashboard" style="border-radius: 8px; border: 1px solid #1e2b22;" />
</div>

---

## 🎯 Use Cases

- 🔐 **DeFi Protocol Security**  
  Screen wallets in real-time to prevent smart contract exploits.

- ⚠️ **AML & Compliance**  
  Risk scoring for exchanges and fiat on-ramps.

- 📊 **Web3 Forensics**  
  Detect sybil clusters and laundering patterns.

- 📈 **Retail Wallet Protection**  
  Help users avoid scams before sending funds.

---

## ✨ Key Features

### 🧠 Graph Neural Network (GNN)
- 3-layer **GCN** using PyTorch Geometric  
- Uses k-NN (k=5) to model wallet relationships  

### 🔍 Real-Time Feature Engineering
- Pulls live data from Etherscan  
- Generates **45-feature vector** aligned with training schema  

### ⚡ Dockerized Backend
- FastAPI inference server  
- CPU-optimized PyTorch container  

### 🎨 Modern UI
- React + Tailwind CSS  
- Animated scanning + dynamic risk scoring  

---

## 🧠 Machine Learning Model

- Trained on **Kaggle Ethereum Fraud Dataset (~10k wallets)**  
- Extracts **45 behavioral features**, including:
  - Time between transactions  
  - Network breadth (unique addresses)  
  - Value variance (fraud pattern detection)  

- Uses **weighted Negative Log-Likelihood (NLL)** to handle class imbalance  

---

## 🏗️ Architecture

### Backend (`backend/`)

| File | Description |
|------|------------|
| `main.py` | FastAPI server + inference pipeline |
| `etherscan_client.py` | Fetches blockchain data |
| `feature_engineering.py` | Builds 45-feature dataset |
| `graph_feature_engineering.py` | Constructs GNN graph |
| `gnn_training.py` | Model + training logic |
| `Dockerfile` | Container configuration |

### Frontend (`frontend/`)
- React 19 + Vite  
- Tailwind CSS  
- SPA architecture  
- Deployed via Vercel  

---

## 🔧 Tech Stack

### ML / Backend
- FastAPI  
- PyTorch + PyG  
- Pandas, Scikit-learn  
- Python 3.12  

### Frontend
- React  
- Vite  
- Tailwind CSS  

### Infrastructure
- Docker  
- Render (backend)  
- Vercel (frontend)  
- Git Monorepo  

---

## 🚀 Getting Started

### Prerequisites
- Docker Desktop  
- Node.js 18+  
- Etherscan API Key → https://etherscan.io/apis  

---

## 🐳 Local Development

### 1. Clone Repository

```bash
git clone https://github.com/your-username/recon.git
cd recon
```
### 2. Setup Environment Variables
Create a .env file inside the backend/ folder:
```bash
ETHERSCAN_API_KEY=your_actual_api_key_here
```

### 3. Run the Backend (Docker)
```bash
cd backend
docker build -t recon-api .
docker run -p 8000:8000 --env-file .env recon-api
```
### 4. Run the Frontend (Node)
```bash
cd frontend
npm install
npm run dev
```

## ☁️ Deployment
- Backend (Render)
- Connect repo
- Set root directory: backend
- Add environment variables
- Deploy via Docker
- Frontend (Vercel)
- Import repo
- Set root directory: frontend
- Update API URL before deploy

##📋 API Reference
- GET /analyze/{ethereum_address}

- Query Params

- max_records (default: 200)
- Example Response
```bash
{
  "wallet_address": "0x123...",
  "prediction": "Fraudulent/Suspicious",
  "fraud_probability_percent": 94.2,
  "normal_txs_analyzed": 150,
  "erc20_txs_analyzed": 50,
  "top_features": {
    "Total Txs": 200,
    "ETH Balance": 1.4502,
    "ERC20 Txs": 50
  }
}
```

##📄 License
This project is licensed under the MIT License
