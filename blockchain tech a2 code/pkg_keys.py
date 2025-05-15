# PKG and Key Parameters for Harn Multi-signature and RSA

# PKG parameters
PKG_PARAMS = {
    "p": 1004162036461488639338597000466705179253226703,
    "q": 950133741151267522116252385927940618264103623,
    "e": 973028207197278907211
}

# Procurement Officer parameters
PROCUREMENT_PARAMS = {
    "p": 1080954735722463992988394149602856332100628417,
    "q": 1158106283320086444890911863299879973542293243,
    "e": 106506253943651610547613
}

# Identity values for each inventory
IDENTITIES = {
    "A": 126,
    "B": 127,
    "C": 128,
    "D": 129
}

# Random values for Harn multi-signature
RANDOM_VALUES = {
    "A": 621,
    "B": 721,
    "C": 821,
    "D": 921
}

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

def calculate_params():
    """Calculate derived parameters like n, phi(n), and d for both PKG and Procurement Officer"""
    result = {}
    
    # Calculate PKG parameters
    pkg_n = PKG_PARAMS["p"] * PKG_PARAMS["q"]
    pkg_phi = (PKG_PARAMS["p"] - 1) * (PKG_PARAMS["q"] - 1)
    pkg_d = mod_inverse(PKG_PARAMS["e"], pkg_phi)
    
    result["pkg"] = {
        "n": pkg_n,
        "phi_n": pkg_phi,
        "d": pkg_d,
        "e": PKG_PARAMS["e"]
    }
    
    # Calculate Procurement Officer parameters
    proc_n = PROCUREMENT_PARAMS["p"] * PROCUREMENT_PARAMS["q"]
    proc_phi = (PROCUREMENT_PARAMS["p"] - 1) * (PROCUREMENT_PARAMS["q"] - 1)
    proc_d = mod_inverse(PROCUREMENT_PARAMS["e"], proc_phi)
    
    result["procurement"] = {
        "n": proc_n,
        "phi_n": proc_phi,
        "d": proc_d,
        "e": PROCUREMENT_PARAMS["e"]
    }
    
    return result

if __name__ == "__main__":
    # Test calculation of parameters
    params = calculate_params()
    for entity, values in params.items():
        print(f"{entity.upper()} Parameters:")
        for key, value in values.items():
            print(f"  {key}: {value}") 