# rsa_utils.py
# Location: /Users/luth/Downloads/blockchain tech a2 code/rsa_utils.py
import hashlib

def gcd(a, b):
    """
    Computes the greatest common divisor (GCD) of two integers a and b
    using the Euclidean algorithm.
    """
    while b:
        a, b = b, a % b
    return a

def extended_gcd(a, b):
    """
    Computes the extended Euclidean algorithm.
    Returns a tuple (gcd, x, y) such that a*x + b*y = gcd.
    """
    if a == 0:
        return b, 0, 1
    d, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return d, x, y

def mod_inverse(e, phi):
    """
    Computes the modular multiplicative inverse of e modulo phi.
    Returns d such that (e * d) % phi = 1.
    Raises ValueError if the modular inverse does not exist.
    """
    d, x, _ = extended_gcd(e, phi)
    if d != 1:
        raise ValueError(f"Modular inverse does not exist for e={e}, phi={phi} (gcd is {d})")
    return x % phi

def power(base, exp, mod):
    """
    Computes (base^exp) % mod using the right-to-left binary method
    for modular exponentiation. This is efficient for large numbers.
    """
    res = 1
    base %= mod
    while exp > 0:
        if exp % 2 == 1:  # If exp is odd
            res = (res * base) % mod
        base = (base * base) % mod  # Square the base
        exp //= 2  # Integer division by 2
    return res

def generate_keys_from_pqe(p, q, e_val):
    """
    Generates RSA public and private keys from given p, q, and e.
    p, q: Large prime numbers.
    e_val: Public exponent.
    Returns: (public_key, private_key_exponent, p, q, phi_n)
             public_key = (n, e_val)
    """
    if p == q: # Should not happen with good primes
        raise ValueError("p and q cannot be equal.")
    
    n = p * q
    phi_n = (p - 1) * (q - 1)

    # Validate e_val: 1 < e_val < phi_n and gcd(e_val, phi_n) == 1
    if not (1 < e_val < phi_n):
        raise ValueError(f"e must be > 1 and < phi_n. e={e_val}, phi_n={phi_n}")
    if gcd(e_val, phi_n) != 1:
        raise ValueError(f"e ({e_val}) is not coprime with phi_n ({phi_n}). GCD is {gcd(e_val, phi_n)}")

    d_val = mod_inverse(e_val, phi_n)
    
    public_key = (n, e_val)
    private_key_exponent = d_val 
    
    return public_key, private_key_exponent, p, q, phi_n

def sign_message(message_str, private_key_d, n):
    """
    Signs a message string using the RSA private key.
    1. Hashes the message (SHA-256).
    2. Converts hash to an integer.
    3. Computes signature S = H^d mod n.
    Returns the signature (integer) and the hex digest of the hash.
    """
    sha256 = hashlib.sha256()
    sha256.update(message_str.encode('utf-8'))
    hashed_message_hex = sha256.hexdigest()
    
    hashed_message_int = int(hashed_message_hex, 16)
    
    if hashed_message_int >= n:
        raise ValueError("Hash value is too large for RSA modulus n.")

    signature = power(hashed_message_int, private_key_d, n)
    return signature, hashed_message_hex

def verify_signature(message_str, signature, public_key_e, n):
    """
    Verifies an RSA signature.
    1. Hashes the message (SHA-256).
    2. Converts hash to an integer H'.
    3. Computes H_verified = S^e mod n (decrypts signature).
    4. Compares H' with H_verified.
    Returns True if valid, False otherwise, along with original hash (hex) and decrypted hash (int).
    """
    sha256 = hashlib.sha256()
    sha256.update(message_str.encode('utf-8'))
    hashed_message_hex = sha256.hexdigest()
    hashed_message_int = int(hashed_message_hex, 16)
    
    decrypted_hash_int = power(signature, public_key_e, n)
    
    return hashed_message_int == decrypted_hash_int, hashed_message_hex, decrypted_hash_int
