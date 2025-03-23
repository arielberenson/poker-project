import json


def create_message(message_type, data1, data2):
    return json.dumps({
        "type": message_type,
        "data1": data1,
        "data2": data2,
    })


def extract_json(data):
    """Extract a complete JSON object from the data, handling nested structures."""
    # Use a stack to track the opening and closing braces
    stack = 0
    start_idx = 0
    for i, char in enumerate(data):
        if char == '{':  # Opening brace
            if stack == 0:
                start_idx = i
            stack += 1
        elif char == '}':  # Closing brace
            stack -= 1
            if stack == 0:  # Found a complete JSON object
                return data[i + 1:], data[start_idx:i + 1]  # Return the remaining data and the JSON object
    return data, ""  # If no complete JSON is found, return the data unprocessed


def send_to_all(recipients, m):
    for recipient in recipients:
        try:
            us = recipient.get_user()
            us.get_socket().sendall(m.encode('utf-8'))
        except Exception as e:
            recipient.get_socket().sendall(m.encode('utf-8'))
