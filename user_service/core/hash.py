import bcrypt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a hashed one using bcrypt directly.
    """
    # Encode both the plain password and the hashed password into bytes
    password_bytes = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    
    # Use bcrypt's checkpw function to compare them
    return bcrypt.checkpw(password_bytes, hashed_password_bytes)


def get_password_hash(password: str) -> str:
    """
    Hashes a plain password using bcrypt directly.
    """
    # Encode the password into bytes
    password_bytes = password.encode('utf-8')
    
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    
    # Decode the hashed bytes back into a string to store in the database
    return hashed_bytes.decode('utf-8')