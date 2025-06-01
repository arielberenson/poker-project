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


def check_username(username):
    users_ref = initialize_firebase()  # Ensure Firebase is initialized and get reference

    # Query the users to check if the username exists
    existing_users = users_ref.order_by_child('username').equal_to(username).get()
    return bool(not existing_users)  # Returns True if the username exists, else False


def check_user_credentials(username, password):
    users_ref = initialize_firebase()  # Ensure Firebase is initialized and get reference

    # Query the database for the given username
    matching_users = users_ref.order_by_child('username').equal_to(username).get()

    for user_data in matching_users.values():
        if user_data.get('password') == password:
            # TO DELETE :::::::
            if user_data.get('username')[0] == 'a':
                update_chips(username, 20)
            elif user_data.get('username')[0] == 'b':
                update_chips(username, 100)
            # TO DELETE ::::::
            return True  # Found a matching username and password

    return False  # No matching user found


def add_to_db(username, password, chips=1000):
    users_ref = initialize_firebase()  # Ensure Firebase is initialized and get reference
    # Adding user with a unique ID using push() instead of set() which overwrites data
    # TO DELETE:::
    if username[0] == 'a':
        chips = 20
    elif username[0] == 'b':
        chips = 100
    # TO DELETE:::
    users_ref.push({
        'username': username,
        'password': password,
        'chips': chips
    })


def update_chips(username, new_chip_value):
    users_ref = initialize_firebase()  # Ensure Firebase is initialized and get reference

    # Query the users to find the user by username
    matching_users = users_ref.order_by_child('username').equal_to(username).get()

    # If the user exists, update the chips value
    for user_id, user_data in matching_users.items():
        # Update the chips value for the found user
        user_ref = users_ref.child(user_id)
        user_ref.update({'chips': new_chip_value})
        return True  # Successfully updated the chips

    return False  # Username not found


def fetch_data(username, type):
    users_ref = initialize_firebase()
    # Query the users to find the user by username
    matching_users = users_ref.order_by_child('username').equal_to(username).get()

    # If the user exists, update the chips value
    for user_id, user_data in matching_users.items():
        return user_data.get(type)
