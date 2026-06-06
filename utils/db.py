from config import DB_NAME, MONGO_URI, users_collection, otp_collection
from pymongo import MongoClient

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client[DB_NAME]
users_col = db[users_collection]
otp_col = db[otp_collection]

