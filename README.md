# 🔐 AWS Lambda Authentication System Template

A production-ready, serverless authentication system built on **AWS Lambda**, **MongoDB**, and **Python**. Designed as a reusable template for any application that needs secure user authentication out of the box.

---

## ✨ Features

- **User Registration** — with email OTP verification
- **Login** — via password or OTP
- **JWT Authentication** — HS512 signed tokens with 60-day expiry
- **OTP System** — cryptographically secure 6-digit OTPs with 10-minute expiry and automatic TTL cleanup
- **Password Reset** — full OTP-based reset flow
- **Email Notifications** — login alerts, OTP emails, welcome emails, password change alerts
- **Lazy Loading** — routes loaded on demand for cold start optimization
- **Single MongoDB Connection** — shared across all routes via centralized `db.py`
- **Security First** — `pbkdf2_sha256` password hashing, `secrets` module for OTP, OTP invalidated after use

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Runtime | Python 3.x |
| Compute | AWS Lambda |
| Database | MongoDB (via PyMongo) |
| Auth | PyJWT (HS512) |
| Password Hashing | passlib (pbkdf2_sha256) |
| Email | smtplib (SMTP_SSL) |
| OTP Generation | Python `secrets` module |

---

## 📁 Project Structure

```
project/
├── lambda_function.py          # Entry point — routing dispatch table
├── config.py                   # Environment variable loader
├── create_db.py                # MongoDB collection + index setup script
├── .env                        # Environment variables (never commit this)
├── requirements.txt            # Python dependencies
├── packages/                   # Bundled dependencies for Lambda
│
├── routes/                     # Route handlers (lazy loaded)
│   ├── __init__.py
│   ├── register.py             # POST /register
│   ├── login.py                # POST /login
│   ├── send_otp.py             # POST /send_otp
│   ├── send_login_otp.py       # POST /send_login_otp
│   ├── send_reset_otp.py       # POST /send_reset_otp
│   ├── reset_password.py       # POST /reset_password
│   └── verify_jwt.py           # POST /verify_jwt
│
├── utils/                      # Shared utilities
│   ├── __init__.py             # Exports all utilities
│   ├── db.py                   # MongoDB connection (single instance)
│   ├── gen_otp.py              # Secure OTP generator
│   ├── send_email.py           # SMTP email sender
│   ├── _jwt.py                 # JWT generation and verification
│   └── response.py             # Standardized JSON response helper
│
└── email_templates/            # HTML email templates
    ├── otp.html                # Registration OTP
    ├── login_otp.html          # Login OTP
    ├── pass_reset_otp.html     # Password reset OTP
    ├── login.html              # New login alert
    ├── welcome.html            # Welcome email
    └── password_changed.html   # Password changed alert
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.x
- MongoDB Atlas account (or local MongoDB)
- SMTP email account (Gmail, Zoho, etc.)
- AWS account with Lambda + API Gateway

### 1. Clone the repository

```bash
git clone https://github.com/ap165/AWS_Lambda_Authentication_System_Template.git
cd AWS_Lambda_Authentication_System_Template
```

### 2. Install dependencies

```bash
pip install -r requirements.txt -t packages/
```

### 3. Create your `.env` file

```env
MONGO_URI=your_mongodb_connection_string
DB_NAME=your_database_name
SMTP_HOST=your_smtp_host
SMTP_PORT=465
SMTP_USERNAME=your_smtp_username
SMTP_PASSWORD=your_smtp_password
SMTP_FROM_EMAIL=yourdomain.com
JWT_SECRET=your_super_secret_key
```

### 4. Set up MongoDB collections

```bash
python create_db.py
```

This creates the `users` and `otp` collections with the correct indexes:
- Unique index on `otp.email`
- TTL index on `otp.expires_at` for automatic OTP cleanup

### 5. Test locally

```bash
python lambda_function.py
```

The entry point has a built-in test event — modify `test_event` in `lambda_function.py` to test different routes.

---

## 📖 API Reference

### Base URL
```
https://your-api-gateway-url.amazonaws.com
```

---

### `POST /send_otp`
Send a registration OTP to an email address.

**Request Body:**
```json
{
    "email": "user@example.com",
    "username": "johndoe"
}
```

**Response:**
```json
{
    "message": "OTP sent successfully."
}
```

---

### `POST /register`
Register a new user. Requires a valid OTP sent via `/send_otp`.

**Request Body:**
```json
{
    "userId": "johndoe",
    "email": "user@example.com",
    "name": "John Doe",
    "password": "SecurePass@123",
    "otp": "482910"
}
```

**Response:**
```json
{
    "message": "User created successfully.",
    "user_id": "64f1a2b3c4d5e6f7a8b9c0d1",
    "token": "eyJhbGciOiJIUzUxMiJ9..."
}
```

---

### `POST /login`
Login via password or OTP. Sends a login alert email on success.

**Request Body (password login):**
```json
{
    "email": "user@example.com",
    "password": "SecurePass@123"
}
```

**Request Body (OTP login):**
```json
{
    "username": "johndoe",
    "otp": "482910"
}
```

**Response:**
```json
{
    "username": "johndoe",
    "email": "user@example.com",
    "name": "John Doe",
    "token": "eyJhbGciOiJIUzUxMiJ9..."
}
```

---

### `POST /send_login_otp`
Send a login OTP to a registered user's email.

**Request Body:**
```json
{
    "email": "user@example.com"
}
```

---

### `POST /verify_jwt`
Verify a JWT token.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "message": "JWT is valid",
    "payload": {
        "userId": "64f1a2b3c4d5e6f7a8b9c0d1",
        "exp": 1780123037
    }
}
```

---

### `POST /send_reset_otp`
Send a password reset OTP.

**Request Body:**
```json
{
    "email": "user@example.com"
}
```

---

### `POST /reset_password`
Reset password using a valid OTP.

**Request Body:**
```json
{
    "email": "user@example.com",
    "otp": "482910",
    "new_password": "NewSecurePass@123"
}
```

**Response:**
```json
{
    "message": "Password reset successful."
}
```

---

## ☁️ AWS Deployment

### 1. Package your code

```bash
zip -r deployment.zip . -x "*.git*" -x ".env" -x "email_templates/*"
```

### 2. Upload to Lambda

1. Go to AWS Lambda → Create Function
2. Runtime: **Python 3.x**
3. Upload your `deployment.zip`
4. Set handler to: `lambda_function.lambda_handler`

### 3. Set environment variables

In Lambda → Configuration → Environment Variables, add all variables from your `.env` file.

### 4. Set up API Gateway

1. Create an **HTTP API** in API Gateway
2. Add routes matching the endpoints above
3. Link each route to your Lambda function
4. Deploy the API

---

## 🔒 Security

- Passwords hashed with `pbkdf2_sha256` (never stored in plain text)
- OTPs generated using Python's `secrets` module (cryptographically secure)
- OTPs are **single-use** — deleted immediately after verification
- OTPs auto-expire after **10 minutes** via MongoDB TTL index
- JWT tokens signed with **HS512** algorithm
- JWT tokens expire after **60 days**
- Login alert emails sent on every new sign-in

---

## 🗄️ MongoDB Schema

### `users` collection
```json
{
    "_id": "ObjectId",
    "userId": "string (unique)",
    "email": "string (unique)",
    "name": "string",
    "passwordHash": "string",
    "status": "string",
    "created_at": "string (ISO 8601)",
    "updated_at": "string (ISO 8601)"
}
```

### `otp` collection
```json
{
    "_id": "ObjectId",
    "email": "string (unique index)",
    "otp_hash": "string",
    "expires_at": "datetime (TTL index)"
}
```

---

## ⚠️ Disclaimer

Make sure to:
- Never commit your `.env` file
- Rotate your `JWT_SECRET` if compromised
- Use a strong, random `JWT_SECRET` in production
- Enable MongoDB Atlas IP whitelisting

---

## 📜 License

This project is open source and available under the MIT License.

---

Made with ❤️ by [ap165](https://github.com/ap165)
