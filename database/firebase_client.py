from database.firebase_shared import *


def get_server_ip_from_firebase():
    initialize_firebase()
    ref = db.reference('py/server_status/ip')
    return ref.get()
