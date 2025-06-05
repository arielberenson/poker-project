import firebase_admin
import time
from firebase_admin import credentials
from firebase_admin import db


def initialize_firebase():
    # Initialize Firebase only if not already initialized
    if not firebase_admin._apps:
        cred = credentials.Certificate("key.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://poker-users-6edad-default-rtdb.europe-west1.firebasedatabase.app/'
        })

    # You can define the reference globally if needed for other operations
    ref = db.reference('py/')
    users_ref = ref.child('users')
    return users_ref
