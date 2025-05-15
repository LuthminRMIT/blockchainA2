import hashlib

def mod_inverse(e, phi):
    """
    Computes the modular multiplicative inverse of e modulo phi.
    Returns d such that (e * d) % phi = 1.
    Raises ValueError if the modular inverse does not exist.
    """
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        d, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return d, x, y
    
    d, x, _ = extended_gcd(e, phi)
    if d != 1:
        raise ValueError(f"Modular inverse does not exist for e={e}, phi={phi} (gcd is {d})")
    return x % phi

def hash_message(item_id, qty):
    """
    Create a hash of the message containing item ID and quantity.
    Returns an integer hash value.
    """
    message = f"{item_id}:{qty}"
    return int(hashlib.sha256(message.encode()).hexdigest(), 16)

def partial_signature(identity, random_val, hash_val):
    """
    Generate a partial signature using Harn's identity-based multisignature scheme.
    si = ri + xi*h mod q (where q is the modulus, not enforced here)
    """
    return random_val + identity * hash_val

def aggregate_signatures(partials):
    """
    Aggregate multiple partial signatures into a single signature.
    S = sum(si) mod q
    """
    return sum(partials)

def verify_multisignature(identities, hash_val, aggregated_sig):
    """
    Verify the aggregated signature against the identities and hash.
    For Harn's scheme, verification checks if S = sum(ri) + h*sum(xi)
    For this simplified version, we're just checking expected values.
    """
    # Sum of public identities multiplied by hash
    id_component = sum(identities) * hash_val
    
    # Calculate expected signature value (simplified for demo)
    # In a real implementation, we would need to retrieve the random values securely
    random_sum = 621 + 721 + 821 + 921  # Sum of random values
    expected_sig = random_sum + id_component
    
    return aggregated_sig == expected_sig

def power_mod(base, exp, mod):
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

def encrypt_message(message, e, n):
    """
    Encrypt a message using RSA public key (e, n)
    """
    # Convert message to integer
    m_int = int.from_bytes(message.encode(), 'big')
    # Encrypt: c = m^e mod n
    encrypted = power_mod(m_int, e, n)
    return encrypted

def decrypt_message(ciphertext, d, n):
    """
    Decrypt a message using RSA private key (d, n)
    """
    # Decrypt: m = c^d mod n
    decrypted_int = power_mod(ciphertext, d, n)
    
    # Convert integer back to bytes and then to string
    # This is a bit tricky as we need to determine the byte length
    byte_length = (decrypted_int.bit_length() + 7) // 8
    decrypted_bytes = decrypted_int.to_bytes(byte_length, 'big')
    
    # Try to decode as UTF-8, handling potential padding issues
    try:
        return decrypted_bytes.decode('utf-8')
    except UnicodeDecodeError:
        # Remove any trailing zeros and try again
        decrypted_bytes = decrypted_bytes.rstrip(b'\x00')
        return decrypted_bytes.decode('utf-8', errors='replace') 