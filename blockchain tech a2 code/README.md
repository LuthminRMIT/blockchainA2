

# Blockchain Inventory System with RSA Digital Signatures

This application demonstrates a blockchain-inspired inventory management system that uses RSA digital signatures to sign and verify transactions, with a consensus protocol to validate additions to the inventory. The system simulates distributed ledger concepts by ensuring that all inventory nodes (A, B, C, D) maintain identical copies of the data.

## Table of Contents
- [System Overview](#system-overview)
- [RSA Digital Signature Implementation](#rsa-digital-signature-implementation)
- [Consensus Protocol](#consensus-protocol)
- [Technical Implementation](#technical-implementation)
- [How to Run](#how-to-run)
- [Demo Walkthrough](#demo-walkthrough)

## System Overview

This system simulates 4 inventory databases (A, B, C, D) that maintain synchronized records using blockchain concepts:

1. **Digital Signatures**: Every transaction is cryptographically signed using RSA
2. **Transaction Propagation**: Changes propagate to all inventories
3. **Consensus Mechanism**: New records require majority approval (3 out of 4 nodes)
4. **Signature Verification**: Any node can verify the authenticity of transactions

![System Overview](https://raw.githubusercontent.com/yourusername/blockchain-inventory/main/docs/system-overview.png)

## RSA Digital Signature Implementation

### Key Generation
Each inventory node has its own RSA key pair:
- **Public Key (e, n)**: Used by others to verify signatures
- **Private Key (d, n)**: Used by the inventory to sign its transactions

For security and performance demonstration, the system uses predetermined primes:
```python
# Example of one inventory's parameters
"A": {
    "p": 1210613765735147311106936311866593978079938707,
    "q": 1247842850282035753615951347964437248190231863,
    "e": 815459040813953176289801,
}
```

### Signing Process
When an inventory (e.g., Inventory A) creates a new record:
1. A message string is generated describing the transaction
2. The message is hashed using SHA-256
3. The hash is signed using the inventory's private key (d)
4. The signature, original message, and public key details are stored

```
Sign(hash) = hash^d mod n
```

### Verification Process
When verifying a signature:
1. The received message is hashed using SHA-256
2. The signature is "decrypted" using the signer's public key (e)
3. The decrypted hash is compared with the computed hash
4. If they match, the signature is valid

```
Verify(signature) = signature^e mod n
```

## Consensus Protocol

For a new record to be added to the distributed inventory system:

1. An inventory node proposes a new record (e.g., item 004 with 12 units at price 18)
2. All nodes vote on whether to accept the record based on predefined rules
3. If at least 3 out of 4 nodes approve, consensus is reached
4. The record is then added to all inventory databases

### Voting Logic
The current implementation uses a simple rule:
- If item quantity is less than 50, vote ACCEPT
- Otherwise, vote REJECT

```python
def simulate_vote(inventory_name, proposed_record):
    # Simulate simple logic for voting: accept if quantity is under 50
    return True if proposed_record["quantity"] < 50 else False
```

### Preventing Duplicates
The system checks for duplicate records by comparing item IDs and locations to ensure that each record is unique.

## Technical Implementation

### Backend (Flask)
- `app.py`: Main Flask application controlling all routes and logic
- `rsa_utils.py`: RSA cryptographic utilities for key generation, signing, and verification
- `consensus_protocol.py`: Implements the consensus logic for record approval

### Data Storage
- Simple text files store inventory data in CSV format
- In-memory storage for signed records
- RSA keys are generated at startup and stored in memory

### Frontend
- Interactive HTML/JS interface to demonstrate the blockchain concepts
- Real-time updates of inventory tables
- Automatic verification of all records against all inventories
- Visual highlighting of newly added records

## How to Run

1. Make sure you have Python 3.7+ installed
2. Install required packages:
   ```
   pip install flask
   ```
3. Run the application:
   ```
   python src/main/app.py
   ```
4. Open your browser to:
   ```
   http://localhost:5001
   ```

## Demo Walkthrough

1. **View Initial Inventories**: All four inventories (A, B, C, D) are displayed with their current records
2. **Add New Record**: The form is pre-filled with record "004,12,18,A"
3. **Sign & Propagate**: Click the button to sign the record with the selected inventory's private key
4. **See Propagation**: The record is propagated to all inventories
5. **Verify Authenticity**: The "Automatic Verification" section shows which inventory signed the record and verifies all signatures
6. **Detect Tampering**: Any attempt to modify a record would invalidate its signature

---

This application is for educational and demonstration purposes to showcase the fundamental concepts behind blockchain technology, digital signatures, and distributed consensus mechanisms.

