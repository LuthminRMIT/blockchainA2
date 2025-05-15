# consensus_protocol.py

def load_inventory_records(file_path):
    inventories = {}
    current_inventory = None
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.endswith(':'):
                current_inventory = line[:-1]
                inventories[current_inventory] = []
            elif line and not line.startswith('#') and current_inventory:
                item_id, qty, price, loc = line.split(',')
                inventories[current_inventory].append({
                    "item_id": item_id,
                    "quantity": int(qty),
                    "price": int(price),
                    "location": loc
                })
    return inventories


def simulate_vote(inventory_name, proposed_record):
    # Simulate simple logic for voting: accept if quantity is under 50
    return True if proposed_record["quantity"] < 50 else False


def consensus_protocol(inventories, proposed_record):
    print(f"Proposed new record: {proposed_record}")
    approvals = 0
    for inv in inventories:
        vote = simulate_vote(inv, proposed_record)
        print(f"{inv} voted {'ACCEPT' if vote else 'REJECT'}")
        if vote:
            approvals += 1
    consensus = approvals >= 3  # 3 out of 4 must approve
    print(f"Consensus {'REACHED' if consensus else 'FAILED'} ({approvals}/4 approved)")
    return consensus


def save_updated_records(inventories, output_path):
    with open(output_path, 'w') as f:
        for inv, records in inventories.items():
            f.write(f"{inv}:\n")
            for r in records:
                f.write(f"{r['item_id']},{r['quantity']},{r['price']},{r['location']}\n")
            f.write("\n")


# Modified for integration with Flask app
def check_record_exists(inventories, proposed_record):
    """Check if the record already exists in any inventory."""
    for inv, records in inventories.items():
        for record in records:
            if (record['item_id'] == proposed_record['item_id'] and 
                record['location'] == proposed_record['location']):
                return True
    return False


def get_inventories_from_data(inventory_data):
    """Convert app's INVENTORY_DATA format to consensus protocol format."""
    inventories = {}
    for inv_id, items in inventory_data.items():
        inventories[f"Inventory {inv_id}"] = []
        for item in items:
            inventories[f"Inventory {inv_id}"].append({
                "item_id": item["id"],
                "quantity": int(item["units"]),
                "price": int(item["price"]),
                "location": item["location"]
            })
    return inventories


if __name__ == "__main__":
    # This code runs when the script is called directly
    file_path = "inventory_records.txt"  # Make sure this file is in the same folder
    inventories = load_inventory_records(file_path)

    # Simulated new record submission by Inventory A
    new_record = {
        "item_id": "005",
        "quantity": 15,
        "price": 22,
        "location": "A"
    }

    if consensus_protocol(inventories, new_record):
        for inv in inventories:
            inventories[inv].append(new_record)

        updated_file = "inventory_records_updated.txt"
        save_updated_records(inventories, updated_file)
        print(f"\n New record added and saved to '{updated_file}'")
    else:
        print("\n Consensus not reached. Record not added.") 