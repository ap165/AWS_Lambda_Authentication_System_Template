from utils import generate_otp, send_email, _json_response, users_col, otp_col
from datetime import datetime, timezone, timedelta
import json

template = ""
with open("email_templates/pass_reset_otp.html", "r") as f:
    template = f.read()

def send_reset_otp(event):
    try:
        body = json.loads(event.get("body", "{}"))
        email = body.get("email")
        username = body.get("username")

        user = users_col.find_one({
            "$or" : [
                {"email": email},
                {"userId": username}
            ]
        })

        if not user:
            if email:
                return _json_response(400, {"message": "No user found with this email."})
            else:
                return _json_response(400, {"message": "No user found with this username."})
        
        otp_data = generate_otp()
        otp_col.update_one(
                {"email": user["email"]}, 
                {"$set": {
                    "otp_hash": otp_data["hash"],
                    "expires_at": datetime.now(timezone.utc) + timedelta(minutes=10)
                }},
                upsert=True
            )
        
        send_email("no-reply", user["email"], "OTP for password reset", template.replace("{{USER_NAME}}", user["userId"]).replace("{{OTP_CODE}}", str(otp_data["otp"])))

        return _json_response(200, {"message": "OTP sent successfully."})
    
    except Exception as e:
        return _json_response(500, {"message": "An error occurred while sending OTP", "error": str(e)})
