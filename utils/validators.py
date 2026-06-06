import re

def validate_email(email):
    if not email or not isinstance(email, str):
        return False
    return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email))

def validate_password(password):
    if not password or not isinstance(password, str):
        return False
    return len(password) >= 8

def validate_username(username):
    if not username or not isinstance(username, str):
        return False
    return bool(re.match(r'^[a-zA-Z0-9_]{3,20}$', username))