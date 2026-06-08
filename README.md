# 🔐 AWS Lambda Authentication System Template

A production-ready, serverless authentication system built on **AWS Lambda**, **MongoDB**, and **Python**. Designed as a reusable template for any application that needs secure user authentication out of the box.

---

## ✨ Features

- **User Registration** — with email OTP verification
- **Login** — via password or OTP
- **JWT Authentication** — HS512 signed tokens with 60-day expiry
- **OTP System** — cryptographically secure 6-digit OTPs with 10-minute expiry and automatic TTL cleanup
- **Password Reset** — full OTP-based reset flow with email notification
- **Email Notifications** — login alerts, OTP emails, welcome emails, password change alerts
- **Lazy Loading** — routes loaded on demand for cold start optimization
- **Single MongoDB Connection** — shared across all routes via centralized `db.py`
- **Rate Limiting** — per-email and per-IP request limiting via MongoDB
- **Request Size Limiting** — 400 byte body limit to prevent abuse
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
| CI/CD | GitHub Actions |

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
├── email_templates/            # HTML email templates
│   ├── otp.html                # Registration OTP
│   ├── login_otp.html          # Login OTP
│   ├── pass_reset_otp.html     # Password reset OTP
│   ├── login.html              # New login alert
│   ├── welcome.html            # Welcome email
│   └── password_changed.html   # Password changed alert
│
└── .github/
    └── workflows/
        └── deploy.yml          # GitHub Actions CI/CD pipeline
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

### Authentication Flow

```
Registration:  /send_otp → /register
Login:         /login (password) or /send_login_otp → /login (otp)
Password Reset:/send_reset_otp → /reset_password
Protected:     /verify_jwt (Bearer token in header)
```

---

### `POST /send_otp`
Send a registration OTP to verify email ownership before registration.

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

**Response `201`:**
```json
{
    "message": "User created successfully.",
    "user_id": "64f1a2b3c4d5e6f7a8b9c0d1",
    "token": "eyJhbGciOiJIUzUxMiJ9..."
}
```

---

### `POST /login`
Login via password or OTP. Sends a login alert email on every successful login.

**Request Body (password login):**
```json
{
    "email": "user@example.com",
    "password": "SecurePass@123"
}
```

**Request Body (OTP login — requires `/send_login_otp` first):**
```json
{
    "username": "johndoe",
    "otp": "482910"
}
```

**Response `200`:**
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
Send a login OTP to a registered user's email for passwordless login.

**Request Body:**
```json
{
    "email": "user@example.com"
}
```

or

```json
{
    "username": "johndoe"
}
```

**Response `200`:**
```json
{
    "message": "Login OTP sent successfully."
}
```

---

### `POST /verify_jwt`
Verify a JWT token and confirm the user exists in the database.

**Headers:**
```
Authorization: Bearer <token>
```

**Response `200`:**
```json
{
    "message": "JWT is valid",
    "payload": {
        "userId": "64f1a2b3c4d5e6f7a8b9c0d1",
        "username": "johndoe"
    }
}
```

**Response `401`:**
```json
{
    "message": "Invalid or expired JWT"
}
```

---

### `POST /send_reset_otp`
Send a password reset OTP to a registered user's email.

**Request Body:**
```json
{
    "email": "user@example.com"
}
```

or

```json
{
    "username": "johndoe"
}
```

**Response `200`:**
```json
{
    "message": "OTP sent successfully."
}
```

---

### `POST /reset_password`
Reset password using a valid OTP from `/send_reset_otp`. Sends a password changed alert email on success.

**Request Body:**
```json
{
    "email": "user@example.com",
    "otp": "482910",
    "new_password": "NewSecurePass@123"
}
```

or with username:

```json
{
    "username": "johndoe",
    "otp": "482910",
    "new_password": "NewSecurePass@123"
}
```

**Response `200`:**
```json
{
    "message": "Password reset successful."
}
```

---

## 🧪 Testing with Postman

A Postman collection is included in the repository (`meditationAPP_postman_collection.json`).

1. Open Postman
2. Click **Import** → select the collection file
3. Update the base URL to your API Gateway URL
4. Test routes in this order:
   - `send_otp` → `register` → `login` → `verify_jwt`
   - `send_login_otp` → `login` (OTP)
   - `send_reset_otp` → `reset_password`

---

## ☁️ AWS Deployment

### Manual Deployment

**1. Package your code**
```bash
zip -r deployment.zip . -x "*.git*" -x ".env"
```

**2. Upload to Lambda**
1. Go to AWS Lambda → Create Function
2. Runtime: **Python 3.x**
3. Upload your `deployment.zip`
4. Set handler to: `lambda_function.lambda_handler`

**3. Set environment variables**

In Lambda → Configuration → Environment Variables, add all variables from your `.env` file.

**4. Set up API Gateway**
1. Create an **HTTP API** in API Gateway
2. Add routes matching the endpoints above
3. Link each route to your Lambda function
4. Deploy the API

---

### Automatic Deployment (GitHub Actions CI/CD)

Every push to `main` automatically deploys to Lambda.

**Setup:**

Add these secrets to your GitHub repo (Settings → Secrets → Actions):

| Secret | Description |
|--------|-------------|
| `AWS_ACCESS_KEY_ID` | AWS IAM access key |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM secret key |
| `AWS_REGION` | e.g. `ap-southeast-1` |
| `LAMBDA_FUNCTION_NAME` | Your Lambda function name |

Then just push:
```bash
git add .
git commit -m "your message"
git push origin main
```

GitHub Actions will install dependencies, zip, deploy, and clean up old Lambda versions automatically. 🚀

---

## 🔒 Security

- Passwords hashed with `pbkdf2_sha256` (never stored in plain text)
- OTPs generated using Python's `secrets` module (cryptographically secure)
- OTPs are **single-use** — deleted immediately after verification
- OTPs auto-expire after **10 minutes** via MongoDB TTL index
- JWT tokens signed with **HS512** algorithm
- JWT tokens expire after **60 days**
- JWT verification checks user existence in DB — deleted/banned users rejected instantly
- Login alert emails sent on every new sign-in
- Password change alert emails sent on every reset
- Request body limited to **400 bytes** to prevent abuse
- Lambda concurrency limited to prevent DDoS cost attacks

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
    "status": "string (active | banned)",
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
    "expires_at": "datetime (TTL index — auto deleted after 10 min)"
}
```

---

## ⚠️ Important Notes

- Never commit your `.env` file
- Rotate your `JWT_SECRET` if compromised — all existing tokens will be invalidated
- Use a strong, random `JWT_SECRET` in production (min 32 characters)
- Enable MongoDB Atlas IP whitelisting for extra security
- Set Lambda reserved concurrency to cap costs during attacks

---

## 📜 License

This project is open source and available under the MIT License.

---

Made with ❤️ by [ap165](https://github.com/ap165)