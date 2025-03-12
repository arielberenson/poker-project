import firebase_admin
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


def check_username(item):
    users_ref = initialize_firebase()  # Ensure Firebase is initialized and get reference

    # Query the users to check if the username exists
    existing_users = users_ref.order_by_child('username').equal_to(item).get()
    return bool(not existing_users)  # Returns True if the username exists, else False


def add_to_db(item):
    users_ref = initialize_firebase()  # Ensure Firebase is initialized and get reference
    # Adding user with a unique ID using push() instead of set() which overwrites data
    users_ref.push({
        'username': item[0],
        'password': item[1]
    })
