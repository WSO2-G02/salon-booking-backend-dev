"""
Script to generate a secure secret key for JWT token encryption
Run this once and save the output to your .env file
"""
import secrets

def generate_secret_key(length=64):
    """
    Generate a cryptographically secure secret key
    
    Args:
        length: Number of bytes for the key (default: 64)
    
    Returns:
        A hex-encoded secret key string
    """
    return secrets.token_hex(length)

if __name__ == "__main__":
    secret_key = generate_secret_key()
    print("=" * 80)
    print("JWT SECRET KEY")
    print("=" * 80)
    print(f"\n{secret_key}\n")
    print("=" * 80)
    print("IMPORTANT: Save this key securely in your .env file as JWT_SECRET_KEY")
    print("Do NOT commit this key to version control!")
    print("=" * 80)

# 