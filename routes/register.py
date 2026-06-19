import json
from datetime import datetime, timezone
from passlib.hash import pbkdf2_sha256
from utils import generate_jwt, send_email, _json_response, users_col, otp_col, validate_username, validate_email, validate_password

welcome_template = ""
with open("./email_templates/welcome.html", "r") as f:
    welcome_template = f.read()

def register_user(event):
    try:
        body = json.loads(event.get("body"))
        userId = body.get("userId")
        email = body.get("email")
        name = body.get("name")
        password = body.get("password")
        otp = body.get("otp")

        if not validate_email(email):
            return _json_response(400, {"message": "Invalid email address."})
        if not validate_password(str(password)):
            return _json_response(400, {"message": "Password must be at least 8 characters."})
        if not validate_username(userId):
            return _json_response(400, {"message": "Username must be 3-20 characters, letters/numbers/underscore only."})

        # Check if user with same email or username already exists
        existing_user = users_col.find_one({
            "$or": [
                {"email": email},
                {"userId": userId}
            ]
        })

        # Verify OTP
        otpHash = otp_col.find_one({"email": email}, {"otp_hash": 1})

        otpHash = otpHash["otp_hash"] if otpHash else None
        if not otpHash or not pbkdf2_sha256.verify(str(otp), otpHash):
            return _json_response(400, {
                "message": "Invalid or expired OTP."
            })
        

        if existing_user:
            return _json_response(400, {
                "message": "User with this email or username already exists."
            })

        otp_col.delete_one({"email": email})
        
        hashed_password = pbkdf2_sha256.hash(password)
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        new_user = {
            "userId": userId,
            "email": email,
            "name": name,
            "passwordHash": hashed_password,
            "status": "inactive",
            "created_at": now,
            "updated_at": now
        }
        result = users_col.insert_one(new_user)

        send_email("no-reply", email, "Welcome to Quiet Spaces!", welcome_template.replace("{{USER_NAME}}", userId))

        token = generate_jwt(str(result.inserted_id))

        return _json_response(201, {
            "message": "User created successfully.",
            "user_id": str(result.inserted_id),
            "token": token
        })

    except Exception as e:
        return _json_response(500, {
            "message": "An error occurred while creating the user.",
            "error": str(e)
        })
