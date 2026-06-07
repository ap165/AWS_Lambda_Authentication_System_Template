from utils import verify_tokens, _json_response, users_col
from bson import ObjectId

def verify_jwt_route(event):
    auth_header = event.get("headers", {}).get("authorization", "")
    parts = auth_header.split(" ")
    token = parts[1] if len(parts) == 2 and parts[0] == "Bearer" else None
    payload = verify_tokens(token) if token else None
    if not payload:
        return _json_response(401, {"message": "Invalid or expired JWT"})  
    
    try:
        user = users_col.find_one(
            {"_id": ObjectId(payload["userId"])},
            {"_id": 1, "userId": 1, "status": 1}  # only fetch what you need
        )
    except Exception:
        return _json_response(401, {"message": "Invalid or expired JWT"})
     
    if not user: 
        return _json_response(401, {"message": "Invalid or expired JWT"})
    
    if user.get("status") == "banned":
        return _json_response(403, {"message": "Account suspended."})
    
    return _json_response(200, {
        "message": "JWT is valid",
        "payload": {
            "userId": str(user["_id"]),
            "username": user["userId"]
        }
    })