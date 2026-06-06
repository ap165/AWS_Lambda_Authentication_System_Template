## This file is responsible for loading all configuration values from the .env file and making them available as constants that can be imported throughout the application. This centralizes configuration management and keeps sensitive information out of the codebase.

## **Note: Make sure to create a .env file in the root of your project with the following variables:**
## MONGO_URI=your_mongodb_connection_string
## SMTP_HOST=your_smtp_host
## SMTP_PORT=your_smtp_port
## SMTP_USERNAME=your_smtp_username
## SMTP_PASSWORD=your_smtp_password
## JWT_SECRET=your_jwt_secret_key
## SMTP_FROM_EMAIL=your_email_address_for_sending_emails
import os

if os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()

# SMTP Configuration - these will be used in the main.py file for sending OTP emails
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT"), 465)  # Default to 465 if not set
SMTP_USER = os.getenv("SMTP_USERNAME")
SMTP_PASS = os.getenv("SMTP_PASSWORD")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL")

# JWT Configuration - these will be used in the utils/_jwt.py file for generating and verifying JWTs
JWT_SECRET = os.getenv("JWT_SECRET")

# MongoDB Configuration - these will be used in the create_db.py and main.py files
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
# MongoDB Collections
users_collection = "users" 
otp_collection = "otp"