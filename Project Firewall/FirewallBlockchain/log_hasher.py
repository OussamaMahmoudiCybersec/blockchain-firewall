import os
import django
import hashlib
from web3 import Web3
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FirewallBlockchain.settings')
django.setup()

from logs.models import FirewallLog

# Connect to Ganache (GUI default port: 7545)
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))

# Load ABI from Truffle build
with open('C:\\Users\\Moonlight\\Downloads\\PFE\\Project Firewall\\FirewallBlockchain\\LogHashStorage.json') as f:
    contract_json = json.load(f)
    abi = contract_json['abi']

# Use the deployed contract address (update with your actual address)
contract_address = Web3.to_checksum_address('0xe8B282EF76A9b61f1240d933737FeDc5f9f43f45')

contract = w3.eth.contract(address=contract_address, abi=abi)

# Use the first Ganache account
account = w3.eth.accounts[0]

def hash_log(log):
    data = f"{log.id}|{log.timestamp}|{log.source_ip}|{log.destination_ip}|{log.protocol}|{log.action}"
    return hashlib.sha256(data.encode()).hexdigest()

def send_hashes_to_ethereum():
    logs = FirewallLog.objects.all()
    for log in logs:
        log_hash = hash_log(log)
        tx_hash = contract.functions.storeLogHash(log.id, log_hash).transact({'from': account})
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Stored hash for log {log.id}: {log_hash} | TX: {tx_hash.hex()}")

if __name__ == "__main__":
    send_hashes_to_ethereum()
