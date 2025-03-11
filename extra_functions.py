import json


def create_message(message_type, data1, data2):
    return json.dumps({
        "type": message_type,
        "data1": data1,
        "data2": data2,
    })


def send_to_all(recipients, m):
    for recipient in recipients:
        try:
            us = recipient.get_user()
            us.get_socket().sendall(m.encode('utf-8'))
        except Exception as e:
            recipient.get_socket().sendall(m.encode('utf-8'))
