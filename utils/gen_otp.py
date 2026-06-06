from passlib.handlers.pbkdf2 import pbkdf2_sha256
from datetime import datetime, timezone
import secrets

def generate_otp():
    """Generate a random OTP of specified length."""
    otp = secrets.randbelow(900000) + 100000  # Generate a 6-digit OTP
    hash = pbkdf2_sha256.hash(str(otp))
    return {
        "otp": otp,
        "hash": hash,
        "created_at": datetime.now(timezone.utc)
    }
