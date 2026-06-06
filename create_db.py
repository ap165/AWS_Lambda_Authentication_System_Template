from pymongo import MongoClient
from config import MONGO_URI, DB_NAME, users_collection, otp_collection


client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client[DB_NAME]

# Create users collection
if users_collection not in db.list_collection_names():
    db.create_collection(users_collection)
    print("Users collection created.")
else:
    print("Users collection already exists.")

#create otp collection
if otp_collection not in db.list_collection_names():
    db.create_collection(otp_collection)
    otp_col = db[otp_collection]
    otp_col.create_index(
        [("email", 1)],
        unique=True
    )
    otp_col.create_index(
        "expires_at",
        expireAfterSeconds=0
    )
    print("OTP collection created.")
else:
    print("OTP collection already exists.")
