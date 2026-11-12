"""
Security helpers: password hashing and JWT token creation/decoding.
Explained in plain English for the viva.
"""
import datetime
import jwt
import bcrypt
from backend.app.platform.config import get_secret_key

# The algorithm used to sign the token (industry-standard symmetric signing)
ALGORITHM = "HS256"
# How many minutes a token stays valid before the user must log in again
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def hash_password(plain_password: str) -> str:
    """
    Hash a plain-text password using bcrypt so we never store the real password.
    bcrypt automatically adds a random salt and is slow on purpose to resist brute force.
    """
    # Encode the string to bytes, then let bcrypt do the hashing
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
    # Return as a string so SQLAlchemy can store it in a VARCHAR column
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Check if a plain-text password matches the stored hash.
    Returns True if they match, False otherwise.
    """
    # bcrypt.checkpw re-hashes the plain password with the same salt and compares
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def create_access_token(data: dict) -> str:
    """
    Create a signed JWT (JSON Web Token) containing the given data.
    A JWT has three parts: header, payload, signature — all base64-encoded.
    The signature is created with our SECRET_KEY so only we can verify it.
    """
    # Copy the data so we do not modify the caller's dict
    to_encode = data.copy()
    # Set the expiry time (exp is a standard JWT claim)
    expire = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    # Encode and sign the token
    token = jwt.encode(to_encode, get_secret_key(), algorithm=ALGORITHM)
    return token


def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT token. Raises jwt.PyJWTError if invalid or expired.
    Returns the payload dict if the token is valid.
    """
    # jwt.decode checks the signature and expiry automatically
    payload = jwt.decode(token, get_secret_key(), algorithms=[ALGORITHM])
    return payload
