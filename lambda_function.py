import sys, os, json, importlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "packages"))
from utils import _json_response

ROUTES = {
    # Define routes and their corresponding handler functions
    ("/register", "POST"):       ("routes.register", "register_user"), # parameters: userId, email, name, password, otp
    ("/send_otp", "POST"):       ("routes.send_otp", "send_otp"), # parameters: username, email
    ("/send_login_otp", "POST"): ("routes.send_login_otp", "send_login_otp"), # parameters: username, email
    ("/login", "POST"):          ("routes.login", "login"), # parameters: email or username, password or otp
    ("/verify_jwt", "POST"):     ("routes.verify_jwt", "verify_jwt_route"), # parameters: Authorization header
    ("/send_reset_otp", "POST"):  ("routes.send_reset_otp", "send_reset_otp"), # parameters: email or username
    ("/reset_password", "POST"):  ("routes.reset_password", "reset_password") # parameters: email or username, new_password, otp
}

def lambda_handler(event, context):
    rc = event.get("requestContext", {}).get("http", {})
    key = (rc.get("path"), rc.get("method"))
    body = event.get("body")

    if body and len(body) > 400: ## body size can't exceed 400 bytes
        return _json_response(400, {"message": "Request body too large."})


    # Simple welcome message for root path
    if key[0] == "/" and key[1] in ["GET", "POST"]:
        return _json_response(200, {"message": "Welcome to the Authentication API!"})
    
    route = ROUTES.get(key)
    if not route:
        return _json_response(404, {"message": "Route not found"})
    
    module_name, func_name = route
    try:
        module = importlib.import_module(module_name)
        func = getattr(module, func_name)
        return func(event)
    except Exception as e:
        return _json_response(500, {"message": "An error occurred while processing the request.", "error": str(e)})
    
