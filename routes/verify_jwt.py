from utils import verify_tokens, _json_response

def verify_jwt_route(event):
    auth_header = event.get("headers", {}).get("authorization", "")
    token = auth_header.split(" ")[1] if auth_header.startswith("Bearer ") else None
    payload = verify_tokens(token) if token else None
    
    if payload:
        return _json_response(200, {"message": "JWT is valid", "payload": payload})
    else:
        return _json_response(401, {"message": "Invalid or expired JWT"})   