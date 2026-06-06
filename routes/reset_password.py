import json
from datetime import datetime, timezone
from utils import send_email, _json_response, users_col, otp_col
from passlib.hash import pbkdf2_sha256

template = ""
with open("email_templates/password_changed.html", "r") as f:
    template = f.read()

def reset_password(event):
    try:
        body = json.loads(event.get("body", "{}"))
        username = body.get("username")
        email = body.get("email")
        otp = body.get("otp")
        new_password = body.get("new_password")

        requestContext = event.get("requestContext", {})
        LOGIN_TIME = requestContext.get("time", "Unknown Time")
        IP_ADDRESS = requestContext.get("http", {}).get("sourceIp", "Unknown IP")

        user = users_col.find_one({
            "$or": [
                {"email": str(email)},
                {"userId": str(username)}
            ]
        })

        if not user:
            return _json_response(400, {"message": "No user found."})

        otpHash = otp_col.find_one({"email": user["email"]}, {"otp_hash": 1})
        otp_col.delete_one({"email": user["email"]})
        otp_valid = otpHash and pbkdf2_sha256.verify(str(otp), otpHash["otp_hash"])

        if otp_valid:
            new_passwordHash = pbkdf2_sha256.hash(new_password)
            users_col.update_one(
                {"email": user["email"]},
                {"$set": {
                    "passwordHash": new_passwordHash,
                    "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                }},
            )
            send_email(
                "no-reply",
                user["email"],
                "Password Reset Detected",
                template.replace("{{USER_NAME}}", user["userId"]).replace("{{IP_ADDRESS}}", IP_ADDRESS).replace("{{LOGIN_TIME}}", LOGIN_TIME)
            )
            return _json_response(200, {"message": "Password reset successful."})

        else:
            return _json_response(400, {"message": "Invalid OTP"})

    except Exception as e:
        return _json_response(500, {"message": "An error occurred while resetting password", "error": str(e)})