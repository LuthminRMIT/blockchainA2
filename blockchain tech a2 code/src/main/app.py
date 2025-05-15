# app.py
# Location: /Users/luth/Downloads/blockchain tech a2 code/src/main/app.py

import os
import sys
import csv
from flask import Flask, request, jsonify, render_template
# If you need CORS later (e.g., for a separate frontend project):
# from flask_cors import CORS # Then run: pip install Flask-CORS

# --- Path adjustments to find rsa_utils.py and templates ---
# Current file's directory (src/main)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Project root directory (parent of src/main, which is 'blockchain tech a2 code')
project_root = os.path.abspath(os.path.join(current_dir, '..', '..')) # Go up two levels

# Add project root to sys.path to allow importing rsa_utils from there
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"Added to sys.path: {project_root}") # For debugging path issues

# Define the path to the templates folder (project_root/templates)
template_dir = os.path.join(project_root, 'templates')
# Define the path to the database folder
database_dir = os.path.join(project_root, 'database')
# --- End Path adjustments ---

# Now import rsa_utils and consensus_protocol
try:
    import rsa_utils 
    print("Successfully imported rsa_utils.") # For debugging
    import consensus_protocol
    print("Successfully imported consensus_protocol.")
except ModuleNotFoundError as e:
    print(f"ERROR: Could not find a module: {e}")
    print(f"Ensure both rsa_utils.py and consensus_protocol.py are in the project root: {project_root}")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: An error occurred importing modules: {e}")
    sys.exit(1)


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
