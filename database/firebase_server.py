from database.firebase_shared import *
import socket
import hashlib
import os
import base64


def hash_password_with_salt(password):
    salt = os.urandom(16)
    salted = salt + password.encode()
    hashed = hashlib.sha256(salted).hexdigest()
    salt_str = base64.b64encode(salt).decode()  # To store in Firebase
    return hashed, salt_str


def verify_password(password, stored_hash, stored_salt_str):
    salt = base64.b64decode(stored_salt_str.encode())
    hash_to_check = hashlib.sha256(salt + password.encode()).hexdigest()
    return hash_to_check == stored_hash


def update_server_ip():
    initialize_firebase()

    # Get local IP of the server
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
        print(local_ip)
    except socket.gaierror:
        print("Failed to get local IP")
        return False

    # Upload the IP and timestamp to Firebase
    ref = db.reference('py/server_status')  # You can adjust this path
    ref.set({
        'ip': local_ip,
        'last_updated': time.time()
    })

    print(f"[+] Uploaded server IP {local_ip} to Firebase")
    return True


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
        stored_hash = user_data.get('password_hash')
        stored_salt = user_data.get('salt')

        if stored_hash and stored_salt:
            if verify_password(password, stored_hash, stored_salt):
                return True

    return False  # No matching user found


def add_to_db(username, password, chips=1000):
    users_ref = initialize_firebase()  # Ensure Firebase is initialized and get reference
    # Adding user with a unique ID using push() instead of set() which overwrites data
    hashed_pw, salt = hash_password_with_salt(password)
    users_ref.push({
        'username': username,
        'password_hash': hashed_pw,
        'salt': salt,
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
