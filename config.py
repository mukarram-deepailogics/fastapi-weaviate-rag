import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS")

cred = credentials.Certificate(FIREBASE_CREDENTIALS)
firebase_admin.initialize_app(cred)
db = firestore.client()

def get_all_users():
    users_ref = db.collection("users")
    docs = users_ref.stream()
    users = [doc.to_dict() for doc in docs]
    return users if users else {"message": "No users found"}