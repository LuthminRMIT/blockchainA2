#!/usr/bin/env python
"""
Blockchain-Based Inventory Management System
Runner script for easy portable execution
"""
import os
import sys

# Adjust the Python path to ensure all modules are found regardless of where the script is run from
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import the app from src/main
sys.path.insert(0, os.path.join(current_dir, 'src', 'main'))
from app import app

if __name__ == "__main__":
    print("Starting Blockchain-Based Inventory Management System...")
    print(f"Python path: {sys.path}")
    print(f"Working directory: {os.getcwd()}")
    
    # Make sure the database directory exists
    database_dir = os.path.join(current_dir, 'database')
    if not os.path.exists(database_dir):
        os.makedirs(database_dir)
        print(f"Created database directory: {database_dir}")
    
    # Run the Flask application
    app.run(host="0.0.0.0", port=5001, debug=True) 