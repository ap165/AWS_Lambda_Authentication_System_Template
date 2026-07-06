import json
from passlib.hash import pbkdf2_sha256
from utils import generate_jwt, send_email, _json_response, users_col, otp_col


with open("./email_templates/login.html", "r") as f:
    login_template = f.read()

def login(event):
    try:
        data = json.loads(event["body"])
        requestContext = event.get("requestContext", {})
        IP_ADDRESS = requestContext.get("http", {}).get("sourceIp", "Unknown IP")
        LOGIN_TIME = requestContext.get("time", "Unknown Time")
        email = data.get("email")
        password = data.get("password")
        
        if not email:
            username = data.get("username")
            user = users_col.find_one({"userId": username})
        else:
            user = users_col.find_one({"email": email})
        
        if not user:
            return _json_response(401, {"message": "Invalid Credentials."})
        password_valid = pbkdf2_sha256.verify(password, user.get("passwordHash")) if password else False
        
        if not password:
            otp = data.get("otp")
            otpHash = otp_col.find_one({"email": user.get("email")}, {"otp_hash": 1}) if user.get("email") else None
            otpMatch = otpHash and pbkdf2_sha256.verify(str(otp), otpHash["otp_hash"])
            if not user or not otpMatch:
                return _json_response(401, {"message": "Invalid credentials"})
            otp_col.delete_one({"email": user["email"]})
        
        elif not user or not password_valid:
            return _json_response(401, {"message": "Invalid credentials"})
        
        
        jwt_token = generate_jwt(str(user["_id"]))
        send_email(
            "no-reply",
            user["email"],
            "New Login Detected",
            login_template.replace("{{USER_NAME}}", user["userId"]).replace("{{IP_ADDRESS}}", IP_ADDRESS).replace("{{LOGIN_TIME}}", LOGIN_TIME)
        )
        
        return _json_response(200, {
            "username": user["userId"],
            "email": user["email"],
            "name": user["name"],
            "token": jwt_token
        })
    
    except Exception as e:
        return _json_response(500, {"message": "An error occurred during login", "error": str(e)})