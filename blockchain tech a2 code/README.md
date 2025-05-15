# Project Summary & Key Points

This project is a Python/Flask web application that simulates a distributed inventory management system using blockchain-inspired cryptographic techniques. It demonstrates secure record propagation, consensus, and query verification using custom cryptographic implementations.

---

## Detailed Technical Summary with Code Snippets

### 1. System Architecture
- **Backend:** Python 3 + Flask (REST API, business logic, cryptography)
- **Frontend:** HTML (Tailwind CSS), JavaScript (AJAX for API calls, UI logic)
- **Data Storage:** Plaintext files in `database/` for each inventory node (A, B, C, D)
- **No external cryptographic libraries** are used for signing or verification; all such logic is implemented manually.

---

## Setup & Installation (Updated for Portability)

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Quick Start (Running from GitHub)

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/blockchain-inventory-system.git
   cd blockchain-inventory-system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify your environment**
   ```bash
   python check_environment.py
   ```
   This script will check that all dependencies and files are correctly installed.

4. **Run the application**
   ```bash
   python run.py
   ```

5. **Access the web interface**
   Open [http://localhost:5001](http://localhost:5001) in your browser

### Alternative Methods

#### Using Setup Tools
If you want to install the application as a package:
```bash
pip install -e .
python run.py
```

#### Running from Source Directory
If you're developing or modifying the code:
```bash
cd src/main
python app.py
```

### Project Structure
```
blockchain-inventory-system/
├── database/                # Database files for inventory nodes
├── src/                     # Source code
│   └── main/                # Main application code
│       └── app.py           # Flask application
├── templates/               # HTML templates
├── requirements.txt         # Python dependencies
├── run.py                   # Runner script with portable configuration
├── setup.py                 # Package configuration
└── README.md                # This file
```

### Troubleshooting
- If you see import errors, ensure you're running from the project root
- If database files are missing, they will be created automatically on first run
- Check log output for helpful messages about which paths are being checked

---

### 2. Core Modules and Their Roles

#### a. `app.py` (Main Application)
- **Flask app** that exposes all endpoints and orchestrates the workflows.
- **Key endpoints:**
  - `/sign_record`: Accepts a new inventory record, checks for duplicates, runs consensus, signs, and propagates.
  - `/verify_signature`: Verifies a digital signature for a record.
  - `/verify_all_signatures`: Verifies all signed records against all inventories.
  - `/api/query_item`: Handles multi-signature queries (Harn's scheme).
  - `/api/decrypt_query`: Allows the Procurement Officer to decrypt a query result.
  - `/get_inventory_data`, `/get_signed_records`, `/get_all_key_details`: Data endpoints for the frontend.
- **Data structures:**
  ```python
  INVENTORY_DATA = {}  # Dict of inventory items per node
  GENERATED_KEYS = {}  # Dict of RSA key pairs per node
  SIGNED_RECORDS_DB = []  # List of signed record objects
  ```
- **Example: Adding a signed record (from `/sign_record` endpoint):**
  ```python
  # Check for duplicates
  for inv_id, items in INVENTORY_DATA.items():
      for item in items:
          if item["id"] == item_id_val and item["location"] == location:
              record_exists = True
              break
  # Run consensus
  if not consensus_protocol.consensus_protocol(inventories, proposed_record):
      return jsonify({"error": "Consensus not reached."}), 400
  # Sign the message
  signature, hashed_message_hex = rsa_utils.sign_message(message_str, private_key_d, n)
  # Propagate to all inventories
  propagate_transaction(new_item, inventory_id)
  ```

#### b. `rsa_utils.py` (Custom RSA Implementation)
- **Key functions:**
  ```python
  def generate_keys_from_pqe(p, q, e):
      # ...
      return public_key, private_key_exponent, p, q, phi_n

  def sign_message(message_str, private_key_d, n):
      # Hash message, sign with private key
      signature = power(hashed_message_int, private_key_d, n)
      return signature, hashed_message_hex

  def verify_signature(message_str, signature, public_key_e, n):
      # Decrypt signature, compare hashes
      is_valid = (hashed_message_int == decrypted_hash_int)
      return is_valid, hashed_message_hex, decrypted_hash_int
  ```
- **Manual modular arithmetic:**
  ```python
  def mod_inverse(e, phi):
      # Extended Euclidean algorithm
  def power(base, exp, mod):
      # Right-to-left binary method
  ```

#### c. `harn_multisig.py` (Harn's Multi-Signature Implementation)
- **Key functions:**
  ```python
  def hash_message(item_id, qty):
      # Hashes the query for signing
  def partial_signature(identity, random_val, hash_val):
      # Each node generates a partial signature
  def aggregate_signatures(partials):
      # Aggregates all partials into a multi-signature
  def verify_multisignature(identities, hash_val, aggregated_sig):
      # Verifies the aggregated signature
  def encrypt_message(message, e, n):
      # Manual RSA encryption
  def decrypt_message(cipher, d, n):
      # Manual RSA decryption
  ```
- **Example: Multi-signature query aggregation:**
  ```python
  # In app.py, /api/query_item endpoint
  hash_val = harn_multisig.hash_message(item_id, quantity)
  partial_signatures = {}
  for inv_id in ["A", "B", "C", "D"]:
      identity = pkg_keys.IDENTITIES[inv_id]
      random_val = pkg_keys.RANDOM_VALUES[inv_id]
      partial_sig = harn_multisig.partial_signature(identity, random_val, hash_val)
      partial_signatures[inv_id] = partial_sig
  aggregated_signature = harn_multisig.aggregate_signatures(list(partial_signatures.values()))
  is_valid = harn_multisig.verify_multisignature(list(pkg_keys.IDENTITIES.values()), hash_val, aggregated_signature)
  ```

#### d. `pkg_keys.py` (Key Parameters)
- **Stores hardcoded primes, exponents, and identities for all nodes and the PKG.**
- **Provides:**
  ```python
  def calculate_params():
      # Computes n, phi, d for PKG and Procurement Officer
  def mod_inverse(e, phi):
      # Manual modular inverse
  ```

#### e. `consensus_protocol.py`
- **Implements a simple consensus protocol:**
  ```python
  def consensus_protocol(inventories, proposed_record):
      # All nodes must approve a new record before it is added and signed
  ```

---

### 3. Cryptographic Workflows

#### A. RSA Digital Signature & Propagation
```python
# User submits a new record (only 004,12,18,A allowed for demo)
# Duplicate check
for inv_id, items in INVENTORY_DATA.items():
    for item in items:
        if item["id"] == item_id_val and item["location"] == location:
            record_exists = True
            break
# Consensus
if not consensus_protocol.consensus_protocol(inventories, proposed_record):
    return jsonify({"error": "Consensus not reached."}), 400
# Signing
signature, hashed_message_hex = rsa_utils.sign_message(message_str, private_key_d, n)
# Propagation
propagate_transaction(new_item, inventory_id)
# Verification (automatic, across all inventories)
for record in SIGNED_RECORDS_DB:
    for verifier_id in INVENTORY_PARAMS.keys():
        is_valid, _, _ = rsa_utils.verify_signature(message, signature, public_key_e, n)
```

#### B. Harn's Multi-Signature Query
```python
# Officer submits a query for an item ID
hash_val = harn_multisig.hash_message(item_id, quantity)
# Each node generates a partial signature
partial_signatures = {}
for inv_id in ["A", "B", "C", "D"]:
    identity = pkg_keys.IDENTITIES[inv_id]
    random_val = pkg_keys.RANDOM_VALUES[inv_id]
    partial_sig = harn_multisig.partial_signature(identity, random_val, hash_val)
    partial_signatures[inv_id] = partial_sig
# Aggregate and verify
aggregated_signature = harn_multisig.aggregate_signatures(list(partial_signatures.values()))
is_valid = harn_multisig.verify_multisignature(list(pkg_keys.IDENTITIES.values()), hash_val, aggregated_signature)
# Encrypt result for officer
encrypted_response = harn_multisig.encrypt_message(response_json, pkg_e, pkg_n)
# Officer decrypts
decrypted_json = harn_multisig.decrypt_message(encrypted_int, proc_d, proc_n)
```

---

### 4. Data Flow & Structures
- **Inventory Data:** Stored as CSV lines in `database/inventory_X.txt` (fields: id, units, price, location).
- **Keys:** Generated at startup and stored in `GENERATED_KEYS` (in-memory).
- **Signed Records:** Stored in `SIGNED_RECORDS_DB` (in-memory, can be extended to persistent storage).
- **Frontend:** Fetches data and triggers actions via AJAX calls to Flask endpoints.

---

### 5. Frontend (UI/UX)
- **`templates/index.html`:**
  - **Tab 1:** RSA Signing & Propagation
    - Add a record, view inventory tables, see signing/verification results.
    - Visual feedback for consensus, propagation, and signature status.
  - **Tab 2:** Multi-Signature Query
    - Submit a query, view the multi-signature process, see encrypted and decrypted results.
    - Step-by-step visualization of the cryptographic workflow.

---

### 6. Security & Educational Value
- **All cryptographic signing and verification is custom-coded** (no external libraries for these).
- **Consensus and propagation** mimic blockchain principles, ensuring distributed trust.
- **Multi-signature queries** provide strong, distributed verification and privacy.
- **Automatic verification** and UI feedback help users understand the cryptographic processes.
- **Educational:** The code is structured and commented for learning, with clear separation of cryptographic, consensus, and application logic.

---

### 7. How to Extend
- Add more inventory nodes or change the consensus protocol.
- Implement persistent storage for signed records.
- Expand the multi-signature scheme for more complex queries or access control.
- Integrate with real blockchain or distributed ledger technologies for production use.

---

## Key Components & Workflows

### 1. RSA Digital Signature & Propagation System
- **Purpose:** Ensures that inventory records are securely signed, approved by consensus, and propagated to all inventory nodes.
- **How it works:**
  - **Key Generation:** Each inventory node (A, B, C, D) has its own RSA key pair, generated from hardcoded primes and exponents.
  - **Record Addition:** Only a specific record (`004,12,18,A`) can be added for demonstration. The system checks for duplicates before proceeding.
  - **Consensus Protocol:** Before a record is added, all nodes must approve it via a consensus protocol (see `consensus_protocol.py`).
  - **Signing:** The record is signed using the private key of the initiating inventory node (see `rsa_utils.py`).
  - **Propagation:** The signed record is propagated to all inventory files, ensuring consistency.
  - **Verification:** The system can automatically verify all signatures across all inventories to detect tampering.

### 2. Harn's Identity-Based Multi-Signature Query System
- **Purpose:** Allows a Procurement Officer to securely query inventory data, with results verified by a multi-signature scheme and encrypted for privacy.
- **How it works:**
  - **Query Submission:** The officer submits a query for an item ID.
  - **Partial Signatures:** Each inventory node generates a partial signature using Harn's scheme (see `harn_multisig.py`).
  - **Aggregation:** The partial signatures are aggregated into a single multi-signature.
  - **Verification:** The aggregated signature is verified to ensure all nodes participated.
  - **Encryption:** The result is encrypted using the PKG's public key and can only be decrypted by the Procurement Officer.
  - **Decryption:** The officer decrypts the result using their private key.

---

## Key Files and Their Roles

- **`app.py`**: Main Flask app. Handles all API endpoints, orchestrates consensus, signing, propagation, and query logic.
- **`rsa_utils.py`**: Implements RSA key generation, signing, and verification from scratch (no external crypto libraries).
- **`harn_multisig.py`**: Implements Harn's multi-signature scheme, including manual modular arithmetic and encryption/decryption.
- **`pkg_keys.py`**: Stores cryptographic parameters and provides a manual modular inverse function.
- **`consensus_protocol.py`**: Implements the consensus protocol for approving new records.
- **`database/`**: Contains inventory data files for each node.
- **`templates/index.html`**: The web UI, with two tabs for the two cryptographic workflows.

---

## Security & Implementation Highlights

- **No external cryptographic libraries** are used for signing or verification. All such operations are implemented from scratch.
- **Consensus protocol** ensures that no single node can unilaterally add records, simulating a blockchain-like approval process.
- **Automatic verification** of signatures across all inventories helps detect tampering or inconsistencies.
- **Multi-signature scheme** ensures that queries are only valid if all nodes participate, and results are encrypted for privacy.
- **UI/UX**: The web interface is modern, with clear separation between the two cryptographic workflows and visual feedback for all actions.

---

## How to Use

1. **Start the server** (`python app.py` in `src/main`).
2. **Open the web UI** at [http://localhost:5001](http://localhost:5001).
3. **RSA Tab:** Add and propagate a signed record, then verify signatures.
4. **Multi-Signature Tab:** Query an item, view the multi-signature process, and decrypt the result as the Procurement Officer.

---

## Key Points

- **All cryptographic signing and verification is custom-coded.**
- **Consensus and propagation mimic blockchain principles.**
- **Multi-signature queries provide strong, distributed verification.**
- **The system is educational and demonstrates core blockchain and cryptographic concepts in a clear, interactive way.**

---
