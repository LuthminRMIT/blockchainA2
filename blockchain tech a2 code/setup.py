from setuptools import setup, find_packages

setup(
    name="blockchain-inventory-system",
    version="1.0.0",
    description="A blockchain-based inventory management system with RSA digital signatures and Harn's multi-signature scheme",
    author="Blockchain Tech Team",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Flask>=2.3.3",
        "Werkzeug>=2.3.7",
        "pycryptodome>=3.19.0",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.7",
) 