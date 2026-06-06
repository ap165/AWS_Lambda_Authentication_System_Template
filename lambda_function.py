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
    

if __name__ == "__main__":
    # For local testing
    test_event = {
    "version": "2.0",
    "routeKey": "POST /send_reset_otp",
    "rawPath": "/send_reset_otp",
    "rawQueryString": "",
    "headers": {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "content-length": "127",
        "content-type": "application/json",
        "host": "lo0rdwswbh.execute-api.ap-southeast-1.amazonaws.com",
        "postman-token": "2bfc58f2-ccc6-486e-9e4b-0fae55fe6a46",
        "user-agent": "PostmanRuntime/7.54.0",
        "x-amzn-trace-id": "Root=1-6a1a859d-41d97bb51de2dc6a38e29704",
        "x-forwarded-for": "45.64.239.1",
        "x-forwarded-port": "443",
        "x-forwarded-proto": "https"
    },
    "requestContext": {
        "accountId": "201037000894",
        "apiId": "lo0rdwswbh",
        "domainName": "lo0rdwswbh.execute-api.ap-southeast-1.amazonaws.com",
        "domainPrefix": "lo0rdwswbh",
        "http": {
            "method": "POST",
            "path": "/send_reset_otp",
            "protocol": "HTTP/1.1",
            "sourceIp": "45.64.239.1",
            "userAgent": "PostmanRuntime/7.54.0"
        },
        "requestId": "eKnQsjy0SQ0EMGQ=",
        "routeKey": "POST /send_reset_otp",
        "stage": "$default",
        "time": "30/May/2026:06:37:17 +0000",
        "timeEpoch": 1780123037659
    },
    "body": "{\"username\": \"ap1650\"}",
}

    print(lambda_handler(test_event, None))