# app.py
# Blockchain-Based Inventory Management System 

import os
import sys
import csv
import json
from flask import Flask, request, jsonify, render_template
# If you need CORS later (e.g., for a separate frontend project):
# from flask_cors import CORS # Then run: pip install Flask-CORS

# --- Path adjustments to find modules and templates with a more portable approach ---
# Current file's directory (src/main)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Project root (try multiple approaches to ensure portability)
project_root = None

# First attempt: Go up two directories (for the current setup)
possible_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
if os.path.exists(os.path.join(possible_root, 'templates')):
    project_root = possible_root
    print(f"Found project root at: {project_root} (two levels up)")

# Second attempt: Go up one directory (for a reorganized structure)
if project_root is None:
    possible_root = os.path.abspath(os.path.join(current_dir, '..'))
    if os.path.exists(os.path.join(possible_root, 'templates')):
        project_root = possible_root
        print(f"Found project root at: {project_root} (one level up)")

# Third attempt: Check the current directory itself
if project_root is None:
    if os.path.exists(os.path.join(current_dir, 'templates')):
        project_root = current_dir
        print(f"Found project root at: {project_root} (current directory)")

# If still not found, use the default (two levels up) but warn
if project_root is None:
    project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
    print(f"WARNING: Could not locate templates directory. Using best guess for project root: {project_root}")

# Add project root to sys.path to allow importing modules from there
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"Added to sys.path: {project_root}")

# Define paths with fallback mechanisms
template_dir = os.path.join(project_root, 'templates')
if not os.path.exists(template_dir):
    # Check other possible locations
    template_dir = os.path.join(current_dir, 'templates')
    if not os.path.exists(template_dir):
        print(f"WARNING: Templates directory not found at {template_dir}")
        # One more try - look in the repository root
        template_dir = os.path.join(os.path.dirname(project_root), 'templates')
        if os.path.exists(template_dir):
            print(f"Found templates at: {template_dir}")
    else:
        print(f"Found templates at: {template_dir}")

# Database directory with similar fallback mechanism
database_dir = os.path.join(project_root, 'database')
if not os.path.exists(database_dir):
    os.makedirs(database_dir)
    print(f"Created database directory: {database_dir}")
# --- End Path adjustments ---

# Try multiple module import approaches to increase portability
try:
    # First try direct import (works if modules are in project root)
    try:
        import rsa_utils
        import consensus_protocol
        import harn_multisig
        import pkg_keys
        print("Successfully imported modules from project root.")
    except ImportError:
        # Try relative import from current directory
        sys.path.insert(0, current_dir)
        from . import rsa_utils
        from . import consensus_protocol
        from . import harn_multisig
        from . import pkg_keys
        print("Successfully imported modules with relative imports.")
except ImportError as e:
    # Last resort: look for modules in the same directory as this file
    try:
        # Add directory containing this file to path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import rsa_utils
        import consensus_protocol
        import harn_multisig
        import pkg_keys
        print(f"Successfully imported modules from script directory.")
    except ModuleNotFoundError as e:
        print(f"ERROR: Could not find a module: {e}")
        print(f"Locations checked: {sys.path}")
        sys.exit(1)
except Exception as e:
    print(f"ERROR: An error occurred importing modules: {e}")
    sys.exit(1)

# Create Flask app with the template directory
app = Flask(__name__, template_folder=template_dir)
# If you need CORS:
# CORS(app) 

# Hardcoded prime numbers (p, q) and public exponent (e) for each inventory
INVENTORY_PARAMS = {
    "A": {
        "p": 1210613765735147311106936311866593978079938707,
        "q": 1247842850282035753615951347964437248190231863,
        "e": 815459040813953176289801,
    },
    "B": {
        "p": 787435686772982288169641922308628444877260947,
        "q": 1325305233886096053310340418467385397239375379,
        "e": 692450682143089563609787,
    },
    "C": {
        "p": 1014247300991039444864201518275018240361205111,
        "q": 904030450302158058469475048755214591704639633,
        "e": 1158749422015035388438057,
    },
    "D": {
        "p": 1287737200891425621338551020762858710281638317,
        "q": 1330909125725073469794953234151525201084537607,
        "e": 33981230465225879849295979,
    }
}

GENERATED_KEYS = {} # Stores generated keys for each inventory
SIGNED_RECORDS_DB = [] # Simple in-memory "database" for signed records
INVENTORY_DATA = {} # Will store inventory data loaded from files

def load_inventory_data():
    """Loads inventory data from text files in the database directory."""
    inventory_ids = ["A", "B", "C", "D"]
    
    for inv_id in inventory_ids:
        file_path = os.path.join(database_dir, f"inventory_{inv_id}.txt")
        if not os.path.exists(file_path):
            print(f"Warning: Inventory file not found: {file_path}")
            continue
            
        inventory_items = []
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line:  # Skip empty lines
                        parts = line.split(',')
                        if len(parts) >= 4:
                            item_id, units, price, location = parts[0], parts[1], parts[2], parts[3]
                            inventory_items.append({
                                "id": item_id,
                                "units": units,
                                "price": price,
                                "location": location
                            })
            
            INVENTORY_DATA[inv_id] = inventory_items
            print(f"Successfully loaded {len(inventory_items)} items for Inventory {inv_id}")
        except Exception as e:
            print(f"Error loading inventory data for {inv_id}: {e}")
            INVENTORY_DATA[inv_id] = []

def propagate_transaction(new_item, source_inventory_id):
    """Propagates a new transaction to all inventories."""
    # Add the new item to all inventory files
    for inv_id in ["A", "B", "C", "D"]:
        # Only add if it doesn't already exist
        item_exists = False
        inventory_items = INVENTORY_DATA.get(inv_id, [])
        
        for item in inventory_items:
            if item["id"] == new_item["id"]:
                # Update the existing item
                item["units"] = new_item["units"]
                item["price"] = new_item["price"]
                item["location"] = new_item["location"]
                item_exists = True
                break
        
        if not item_exists:
            inventory_items.append(new_item)
            INVENTORY_DATA[inv_id] = inventory_items
        
        # Save the updated inventory back to file
        file_path = os.path.join(database_dir, f"inventory_{inv_id}.txt")
        try:
            with open(file_path, 'w') as file:
                for item in inventory_items:
                    file.write(f"{item['id']},{item['units']},{item['price']},{item['location']}\n")
            print(f"Updated inventory file for {inv_id}")
        except Exception as e:
            print(f"Error updating inventory file for {inv_id}: {e}")

def initialize_keys():
    """Generates and stores RSA keys for all inventories."""
    print("Initializing RSA keys for inventories...")
    if not hasattr(rsa_utils, 'generate_keys_from_pqe'):
        print("CRITICAL ERROR: The imported 'rsa_utils' module does NOT have 'generate_keys_from_pqe' function.")
        print("Please ensure the correct rsa_utils.py file is in the project root and is being imported.")
        # Optionally, raise an exception or sys.exit() if this is critical for startup
        return 

    for inv_id, params in INVENTORY_PARAMS.items():
        try:
            public_key, private_key_d, p, q, phi_n = rsa_utils.generate_keys_from_pqe(
                params["p"], params["q"], params["e"]
            )
            GENERATED_KEYS[inv_id] = {
                "public_key_n": public_key[0], # n
                "public_key_e": public_key[1], # e
                "private_key_d": private_key_d, # d
                "p_val": p,
                "q_val": q,
                "phi_n_val": phi_n,
            }
            print(f"Successfully generated keys for Inventory {inv_id}.")
        except ValueError as e:
            print(f"Error generating keys for Inventory {inv_id}: {e}")
            GENERATED_KEYS[inv_id] = {"error": str(e)}
        except Exception as e:
            print(f"An unexpected error occurred generating keys for Inventory {inv_id}: {e}")
            GENERATED_KEYS[inv_id] = {"error": f"Unexpected error: {str(e)}"}
    print("Key initialization complete.")

# Clean up inventory data - remove the 004,12,18,A record on startup so it can be added once
def cleanup_inventory_data():
    """Removes any records except the core ones from all inventories."""
    for inv_id in ["A", "B", "C", "D"]:
        inventory_items = INVENTORY_DATA.get(inv_id, [])
        # Filter to keep only records that don't have location A with id 004 
        filtered_items = []
        for item in inventory_items:
            # Remove our special demo record 004,12,18,A
            if item["location"] == "A" and item["id"] == "004":
                print(f"Removing record 004,12,18,A from Inventory {inv_id}")
                continue
            # Keep all other items
            filtered_items.append(item)
        
        # Check if any items were removed
        if len(inventory_items) != len(filtered_items):
            print(f"Removed {len(inventory_items) - len(filtered_items)} items from Inventory {inv_id}")
        
        INVENTORY_DATA[inv_id] = filtered_items
        
        # Save the cleaned inventory back to file
        file_path = os.path.join(database_dir, f"inventory_{inv_id}.txt")
        try:
            with open(file_path, 'w') as file:
                for item in filtered_items:
                    file.write(f"{item['id']},{item['units']},{item['price']},{item['location']}\n")
            print(f"Cleaned up inventory file for {inv_id}")
        except Exception as e:
            print(f"Error updating inventory file for {inv_id}: {e}")

# Load inventory data and initialize keys
print("Loading inventory data...")
load_inventory_data()

# Clean up inventory data
print("Cleaning up inventory data...")
cleanup_inventory_data()

# Double check that our target record is indeed removed
for inv_id in ["A", "B", "C", "D"]:
    inventory_items = INVENTORY_DATA.get(inv_id, [])
    for item in inventory_items:
        if item["location"] == "A" and item["id"] == "004":
            print(f"WARNING: Record 004,12,18,A still exists in Inventory {inv_id} after cleanup!")

# Initialize keys
initialize_keys()

# Clear any existing signed records
SIGNED_RECORDS_DB = []

# Calculate and store PKG and procurement officer parameters
try:
    CRYPTO_PARAMS = pkg_keys.calculate_params()
    print("Successfully calculated cryptographic parameters.")
except Exception as e:
    print(f"ERROR: Failed to calculate cryptographic parameters: {e}")
    sys.exit(1)

@app.route('/')
def index():
    """Serves the main HTML page."""
    inventory_info_for_template = {}
    for inv_id, params in INVENTORY_PARAMS.items():
        # Prepare data for the template, even if key generation failed for some
        key_data = GENERATED_KEYS.get(inv_id, {})
        
        # Get item details from loaded inventory data
        inventory_items = INVENTORY_DATA.get(inv_id, [])
        
        inventory_info_for_template[inv_id] = {
            "p": str(key_data.get("p_val", "N/A")),
            "q": str(key_data.get("q_val", "N/A")),
            "e": str(key_data.get("public_key_e", "N/A")),
            "n": str(key_data.get("public_key_n", "N/A")),
            "phi_n": str(key_data.get("phi_n_val", "N/A")),
            "d": str(key_data.get("private_key_d", "N/A")),
            "items": inventory_items,
            "error": key_data.get("error")
        }

    # Check if index.html exists at the expected path
    index_html_path = os.path.join(template_dir, 'index.html')
    if not os.path.exists(index_html_path):
        print(f"ERROR: templates/index.html not found at {index_html_path}")
        return jsonify({"error": "Critical server error: Missing index.html template. Check server logs."}), 500
        
    return render_template('index.html', 
                           inventories_data=inventory_info_for_template, 
                           inventory_ids_list=list(INVENTORY_PARAMS.keys()))

@app.route('/sign_record', methods=['POST'])
def sign_record_route():
    """API endpoint to sign an inventory record."""
    data = request.json
    inventory_id = data.get('inventory_id')
    units = data.get('units')
    item_id_val = data.get('item_id')
    price = data.get('price')
    location = data.get('location', 'A')  # Default location is A

    # Only allow the specific record 004,12,18,A
    if item_id_val != "004" or units != "12" or price != "18" or location != "A":
        return jsonify({"error": "Only the record 004,12,18,A is allowed to be added"}), 400

    if not all([inventory_id, units is not None, item_id_val is not None, price is not None]):
        return jsonify({"error": "Missing data: inventory_id, units, item_id, or price"}), 400

    # Create proposed record for consensus protocol
    proposed_record = {
        "item_id": item_id_val,
        "quantity": int(units),
        "price": int(price),
        "location": location
    }
    
    # Additional logging for debugging
    print(f"Attempting to add record: {proposed_record}")
    
    # Check if the record exists in inventories directly, not using consensus check
    record_exists = False
    for inv_id, items in INVENTORY_DATA.items():
        for item in items:
            if item["id"] == item_id_val and item["location"] == location:
                record_exists = True
                print(f"Record exists in inventory {inv_id}: {item}")
                break
        if record_exists:
            break
    
    if record_exists:
        return jsonify({"error": "This record already exists in the inventories."}), 400
    
    # Get inventories in the format required by consensus protocol
    inventories = consensus_protocol.get_inventories_from_data(INVENTORY_DATA)
    
    # Run consensus protocol to determine if record should be added
    if not consensus_protocol.consensus_protocol(inventories, proposed_record):
        return jsonify({"error": "Consensus not reached. Record not approved for addition."}), 400

    if inventory_id not in GENERATED_KEYS or "error" in GENERATED_KEYS[inventory_id] or "private_key_d" not in GENERATED_KEYS[inventory_id]:
        app.logger.error(f"Attempt to sign with uninitialized/error keys for {inventory_id}. Keys: {GENERATED_KEYS.get(inventory_id)}")
        return jsonify({"error": f"Keys not properly initialized or error in keys for inventory {inventory_id}. Cannot sign."}), 400

    keys = GENERATED_KEYS[inventory_id]
    private_key_d = keys["private_key_d"]
    n = keys["public_key_n"]
    message_str = f"Inventory {inventory_id} has purchased {units} units of item with ID {item_id_val}, priced at {price}, located at {location}."
    
    try:
        signature, hashed_message_hex = rsa_utils.sign_message(message_str, private_key_d, n)
        
        # Add the new item to INVENTORY_DATA and propagate to all inventories
        new_item = {
            "id": item_id_val,
            "units": units,
            "price": price,
            "location": location
        }
        
        # Propagate the transaction to all inventories
        propagate_transaction(new_item, inventory_id)
        
        # Record the signed transaction
        SIGNED_RECORDS_DB.append({
            "inventory_id": inventory_id, 
            "message": message_str,
            "signature": str(signature), 
            "hash": hashed_message_hex,
            "item": new_item
        })
        
        return jsonify({
            "message": message_str, 
            "hash_hex": hashed_message_hex,
            "signature": str(signature), 
            "signer_inventory_id": inventory_id,
            "public_n": str(n), 
            "public_e": str(keys["public_key_e"]),
            "consensus": "REACHED"
        })
    except Exception as e:
        app.logger.error(f"Signing failed for {inventory_id}: {str(e)}")
        return jsonify({"error": f"Signing failed: {str(e)}"}), 500

@app.route('/verify_signature', methods=['POST'])
def verify_signature_route():
    """API endpoint to verify a signature."""
    data = request.json
    message_str = data.get('message')
    signature_str = data.get('signature')
    signer_inventory_id = data.get('signer_inventory_id')

    if not all([message_str, signature_str, signer_inventory_id]):
        return jsonify({"error": "Missing data: message, signature, or signer_inventory_id"}), 400
    
    if signer_inventory_id not in GENERATED_KEYS or "error" in GENERATED_KEYS[signer_inventory_id] or "public_key_e" not in GENERATED_KEYS[signer_inventory_id]:
        return jsonify({"error": f"Keys not properly initialized or error in keys for signer inventory {signer_inventory_id}. Cannot verify."}), 400

    keys = GENERATED_KEYS[signer_inventory_id]
    public_key_e = keys["public_key_e"]
    n = keys["public_key_n"]
    
    try:
        signature = int(signature_str) # Convert string signature back to integer
    except ValueError:
        return jsonify({"error": "Invalid signature format. Signature must be a string representing an integer."}), 400
        
    try:
        is_valid, original_msg_hash_hex, decrypted_hash_from_sig_int = rsa_utils.verify_signature(
            message_str, signature, public_key_e, n
        )
        return jsonify({
            "is_valid": is_valid, 
            "message_received": message_str,
            "original_message_hash_hex": original_msg_hash_hex,
            "decrypted_hash_from_signature_hex": hex(decrypted_hash_from_sig_int)[2:].zfill(len(original_msg_hash_hex)),
            "signer_inventory_id": signer_inventory_id
        })
    except Exception as e:
        app.logger.error(f"Verification failed for signer {signer_inventory_id}: {str(e)}")
        return jsonify({"error": f"Verification failed: {str(e)}"}), 500

@app.route('/get_all_key_details', methods=['GET'])
def get_all_key_details_route():
    """Helper endpoint to fetch all generated key details for display."""
    key_details_for_frontend = {}
    for inv_id in INVENTORY_PARAMS.keys():
        key_data = GENERATED_KEYS.get(inv_id, {}) # Use .get for safety
        inventory_items = INVENTORY_DATA.get(inv_id, [])
        
        key_details_for_frontend[inv_id] = {
            "p": str(key_data.get("p_val", "N/A")),
            "q": str(key_data.get("q_val", "N/A")),
            "e": str(key_data.get("public_key_e", "N/A")),
            "n": str(key_data.get("public_key_n", "N/A")),
            "phi_n": str(key_data.get("phi_n_val", "N/A")),
            "d": str(key_data.get("private_key_d", "N/A")),
            "items": inventory_items,
            "error": key_data.get("error") # Get error from GENERATED_KEYS
        }
    return jsonify(key_details_for_frontend)

@app.route('/get_inventory_data', methods=['GET'])
def get_inventory_data_route():
    """API endpoint to get all inventory data."""
    return jsonify(INVENTORY_DATA)

@app.route('/get_signed_records', methods=['GET'])
def get_signed_records_route():
    """API endpoint to get all signed records."""
    return jsonify(SIGNED_RECORDS_DB)

@app.route('/verify_all_signatures', methods=['GET'])
def verify_all_signatures_route():
    """API endpoint to verify all recorded signatures against all inventories."""
    verification_results = []
    
    for record in SIGNED_RECORDS_DB:
        original_signer_id = record.get("inventory_id")
        message = record.get("message")
        signature_str = record.get("signature")
        
        if not all([original_signer_id, message, signature_str]):
            verification_results.append({
                "record": record,
                "verifications": [{"inventory_id": "ALL", "is_valid": False, "status": "ERROR", "error": "Missing data in record"}],
                "original_signer": original_signer_id,
                "propagation_status": "ERROR"
            })
            continue
        
        try:
            signature = int(signature_str)
        except ValueError:
            verification_results.append({
                "record": record,
                "verifications": [{"inventory_id": "ALL", "is_valid": False, "status": "ERROR", "error": "Invalid signature format"}],
                "original_signer": original_signer_id,
                "propagation_status": "ERROR"
            })
            continue
        
        # Verify against each inventory's public key
        record_verifications = []
        valid_with_original_signer = False
        
        for verifier_id in INVENTORY_PARAMS.keys():
            if verifier_id not in GENERATED_KEYS or "error" in GENERATED_KEYS[verifier_id]:
                record_verifications.append({
                    "inventory_id": verifier_id,
                    "is_valid": False,
                    "status": "ERROR",
                    "error": f"No valid keys for inventory {verifier_id}"
                })
                continue
                
            keys = GENERATED_KEYS[verifier_id]
            public_key_e = keys["public_key_e"]
            n = keys["public_key_n"]
            
            try:
                is_valid, original_hash, decrypted_hash = rsa_utils.verify_signature(
                    message, signature, public_key_e, n
                )
                
                # Determine verification status based on whether this inventory is the original signer
                status = "PROPAGATED"
                if verifier_id == original_signer_id:
                    status = "ORIGINAL_SIGNER"
                    valid_with_original_signer = is_valid
                
                record_verifications.append({
                    "inventory_id": verifier_id,
                    "is_valid": is_valid,
                    "status": status,
                    "original_hash_hex": original_hash,
                    "decrypted_hash_hex": hex(decrypted_hash)[2:].zfill(len(original_hash))
                })
            except Exception as e:
                record_verifications.append({
                    "inventory_id": verifier_id,
                    "is_valid": False,
                    "status": "ERROR",
                    "error": str(e)
                })
        
        # Determine overall propagation status
        propagation_status = "VALID" if valid_with_original_signer else "INVALID"
        
        verification_results.append({
            "record": record,
            "verifications": record_verifications,
            "original_signer": original_signer_id,
            "propagation_status": propagation_status
        })
    
    return jsonify(verification_results)

@app.route('/multi_signature_query', methods=['GET'])
def multi_signature_query_page():
    """Serves the multi-signature query page."""
    return render_template('index.html', active_tab="multi_signature")

@app.route('/api/query_item', methods=['POST'])
def query_item():
    """API endpoint to query an item across all inventories with Harn multi-signature verification."""
    data = request.json
    item_id = data.get('item_id')
    
    if not item_id:
        return jsonify({"error": "No item ID provided."}), 400
    
    # 1. Search each inventory for the item
    results = []
    for inv_id in ["A", "B", "C", "D"]:
        inventory_items = INVENTORY_DATA.get(inv_id, [])
        for item in inventory_items:
            if item["id"] == item_id:
                results.append({
                    "inventory": inv_id,
                    "item_id": item["id"],
                    "qty": item["units"],
                    "price": item["price"],
                    "location": item["location"]
                })
                break
    
    if not results:
        return jsonify({"error": f"Item ID {item_id} not found in any inventory."}), 404
    
    # Combine results to get a single quantity value (assuming same qty across inventories)
    quantity = results[0]["qty"]
    
    # 2. Generate hash of the message (item_id and quantity)
    hash_val = harn_multisig.hash_message(item_id, quantity)
    
    # 3. Generate partial signatures from each inventory
    partial_signatures = {}
    for inv_id in ["A", "B", "C", "D"]:
        identity = pkg_keys.IDENTITIES[inv_id]
        random_val = pkg_keys.RANDOM_VALUES[inv_id]
        partial_sig = harn_multisig.partial_signature(identity, random_val, hash_val)
        partial_signatures[inv_id] = partial_sig
    
    # 4. Aggregate signatures (PKG's role in consensus)
    aggregated_signature = harn_multisig.aggregate_signatures(list(partial_signatures.values()))
    
    # 5. Verify the aggregated signature
    identities = list(pkg_keys.IDENTITIES.values())
    is_valid = harn_multisig.verify_multisignature(identities, hash_val, aggregated_signature)
    
    if not is_valid:
        return jsonify({"error": "Multi-signature verification failed."}), 400
    
    # 6. Prepare response message
    response_message = {
        "item_id": item_id,
        "quantity": quantity,
        "price": results[0]["price"],
        "location": results[0]["location"],
        "inventories": [r["inventory"] for r in results]
    }
    
    # 7. Encrypt the response using PKG's key
    pkg_e = CRYPTO_PARAMS["pkg"]["e"]
    pkg_n = CRYPTO_PARAMS["pkg"]["n"]
    response_json = json.dumps(response_message)
    
    try:
        encrypted_response = harn_multisig.encrypt_message(response_json, pkg_e, pkg_n)
    except Exception as e:
        return jsonify({"error": f"Encryption failed: {str(e)}"}), 500
    
    # 8. Return the encrypted response and signature information
    return jsonify({
        "success": True,
        "encrypted_response": str(encrypted_response),
        "aggregated_signature": str(aggregated_signature),
        "partial_signatures": {k: str(v) for k, v in partial_signatures.items()},
        "hash_value": str(hash_val),
        "pkg_n": str(pkg_n),
        "pkg_e": str(pkg_e),
        # For demonstration, we include the procurement officer's key
        # In a real system, this would be pre-shared securely
        "procurement_d": str(CRYPTO_PARAMS["procurement"]["d"]),
        "procurement_n": str(CRYPTO_PARAMS["procurement"]["n"])
    })

@app.route('/api/decrypt_query', methods=['POST'])
def decrypt_query():
    """API endpoint for the procurement officer to decrypt a query response."""
    data = request.json
    encrypted_response = data.get('encrypted_response')
    aggregated_signature = data.get('aggregated_signature')
    procurement_d = data.get('procurement_d')
    procurement_n = data.get('procurement_n')
    
    if not all([encrypted_response, aggregated_signature, procurement_d, procurement_n]):
        return jsonify({"error": "Missing required parameters."}), 400
    
    try:
        # Convert string parameters to integers
        encrypted_int = int(encrypted_response)
        proc_d = int(procurement_d)
        proc_n = int(procurement_n)
        
        # Decrypt the response
        decrypted_json = harn_multisig.decrypt_message(encrypted_int, proc_d, proc_n)
        decrypted_data = json.loads(decrypted_json)
        
        return jsonify({
            "success": True,
            "decrypted_data": decrypted_data,
            "aggregated_signature": aggregated_signature
        })
    except Exception as e:
        return jsonify({"error": f"Decryption failed: {str(e)}"}), 500

if __name__ == '__main__':
    # Ensure templates directory and index.html exist before starting
    if not os.path.isdir(template_dir):
        print(f"CRITICAL ERROR: Template directory not found at {template_dir}")
        print("Please ensure you have a 'templates' folder in your project root.")
        sys.exit(1)
    elif not os.path.exists(os.path.join(template_dir, 'index.html')):
         print(f"CRITICAL ERROR: 'index.html' not found in template directory: {template_dir}")
         sys.exit(1)
    
    print(f"Flask app '__name__' is: {__name__}")
    print(f"Template folder is set to: {app.template_folder}")
    app.run(debug=True, host='0.0.0.0', port=5001) # debug=True is fine for development
