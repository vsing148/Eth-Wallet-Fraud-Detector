import os
import requests
import time
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

API_KEY = os.getenv("ETHERSCAN_API_KEY")
BASE_URL = "https://api.etherscan.io/v2/api"
print("API Key loaded successfully." if API_KEY else "API Key missing!")

def get_transaction_history(address, max_records = 1000):
    """ 
    address (str): The Ethereum wallet address (starts with 0x)
    max_records (int): Number of recent transactions to pull
    returns: A list of transaction dictionaries, or an empty list if it fails.
    """

    if not API_KEY:
        print("Error: Etherscan API key not found. Please check your .env file.")
        return []

    # These parameters tell Etherscan exactly what we want
    params = {
        'chainid': '1',            # Required for V2 API (1 = Ethereum Mainnet)
        'module': 'account',
        'action': 'txlist',
        'address': address,
        'startblock': 0,
        'endblock': 99999999,      # Search up to the latest block
        'page': 1,
        'offset': max_records,     # Limit results to save bandwidth
        'sort': 'desc',            # Get newest transactions first
        'apikey': API_KEY
    }

    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        # Check if the API call was successful
        if data['status'] == '1':
            print(f"Successfully fetched {len(data['result'])} transactions.")
            return data['result']
        else:
            print(f"Etherscan API Error: {data.get('message')} - {data.get('result')}")
            return []
    except Exception as e:
        print(f"A network error occurred: {e}")
        return []

def get_erc20_history(wallet_address: str, max_records: int = 200):
    """Fetches ERC-20 token transfer events for a given wallet."""
    url = "https://api.etherscan.io/api"
    params = {
        "module": "account",
        "action": "tokentx",
        "address": wallet_address,
        "page": 1,
        "offset": max_records,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "desc",
        "apikey": API_KEY
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if data.get("status") == "1":
            return data.get("result", [])
        return []
    except Exception as e:
        print(f"Error fetching ERC20 data: {e}")
        return []

if __name__ == "__main__":
    test_address = "0xF977814e90dA44bFA03b6295A0616a897441aceC"
    
    print(f"Fetching data for: {test_address}...")
    transactions = get_transaction_history(test_address, max_records=5)
    
    # Print out a few details for the first 5 transactions
    for i in transactions:
        # Convert Wei to ETH for readability
        eth_value = int(i['value']) / 10**18 
        print(f"\nTx Hash: {i['hash']}")
        print(f"From: {i['from']}")
        print(f"To: {i['to']}")
        print(f"Value: {eth_value} ETH")