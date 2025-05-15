#!/usr/bin/env python
"""
Blockchain-Based Inventory Management System
Environment check script

This script verifies that all required components and dependencies 
are present and correctly configured.
"""
import os
import sys
import importlib
import platform

def check_python_version():
    """Check Python version is at least 3.7"""
    print(f"Python version: {platform.python_version()}")
    if sys.version_info < (3, 7):
        print("⚠️ WARNING: Python version should be at least 3.7")
        return False
    print("✅ Python version OK")
    return True

def check_required_modules():
    """Check if all required modules can be imported"""
    required_modules = [
        "flask",
        "werkzeug",
        "Crypto",  # From pycryptodome
    ]
    
    all_present = True
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✅ Module '{module}' is installed")
        except ImportError:
            print(f"❌ Module '{module}' is missing")
            all_present = False
    
    return all_present

def check_project_structure():
    """Check if key project files and directories exist"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check for required files and directories
    required_items = {
        "src/main/app.py": "Main application",
        "templates": "HTML templates directory",
        "database": "Database directory",
        "requirements.txt": "Dependencies file",
        "rsa_utils.py": "RSA cryptography module",
        "harn_multisig.py": "Harn multisignature module",
        "pkg_keys.py": "PKG keys module",
        "consensus_protocol.py": "Consensus protocol module",
    }
    
    all_found = True
    for item, description in required_items.items():
        path = os.path.join(current_dir, item)
        if os.path.exists(path):
            print(f"✅ Found {description}: {item}")
        else:
            print(f"❌ Missing {description}: {item}")
            all_found = False
    
    return all_found

def main():
    """Run all checks and report status"""
    print("=" * 50)
    print("Blockchain Inventory System - Environment Check")
    print("=" * 50)
    
    python_ok = check_python_version()
    print("\n")
    
    modules_ok = check_required_modules()
    print("\n")
    
    structure_ok = check_project_structure()
    print("\n")
    
    # Overall status
    if python_ok and modules_ok and structure_ok:
        print("✅ All checks passed! The environment is correctly set up.")
        print("You can run the application with: python run.py")
    else:
        print("⚠️ Some checks failed. Please address the issues above before running the application.")
    
    print("=" * 50)

if __name__ == "__main__":
    main() 