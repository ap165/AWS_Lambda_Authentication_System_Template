import jwt
from datetime import datetime, timedelta, timezone
from config import JWT_SECRET

def generate_jwt(user_id):
    payload = {
        "userId": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=60)  # Token expires in 60 days
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS512")
    return token


def verify_tokens(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS512"])
        return payload
    except Exception as e:
        print(f"JWT verification failed: {e}")
        return None
