from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def encode_value(value):
    if isinstance(value, list):
        if not value:
            formatted_value = b"\x03"  # Represent empty list
        elif isinstance(value[0], dict):
            formatted_value = b"\x03".join(
                [b"\x06".join([sub_key.encode() + b"\x07" + sub_value.encode() for sub_key, sub_value in item.items()])
                 for item in value]
            ) + b"\x03"
        else:
            formatted_value = b"\x03".join([item.encode() for item in value]) + b"\x03"
    elif isinstance(value, bool):
        formatted_value = b"\x04" if value else b"\x05"
    else:
        formatted_value = value.encode()

    return formatted_value


def custom_encode(result):
    formatted_result = b""

    for key, value in result.items():
        formatted_value = encode_value(value)
        formatted_result += key.encode() + b"\x02" + formatted_value + b"\x01"

    if b"\x01" in formatted_result:
        formatted_result = formatted_result[:-1]

    return formatted_result


def decode_value(encoded_value):
    if b"\x03" in encoded_value:
        parts = encoded_value.split(b"\x03")
        if len(parts) == 2 and parts[0] == b'':  # Empty list case
            return []
        if b"\x06" in parts[0]:
            # List of dictionaries
            decoded_list = []
            for part in parts:
                if part:
                    dict_items = part.split(b"\x06")
                    decoded_dict = {item.split(b"\x07")[0].decode(): item.split(b"\x07")[1].decode() for item in
                                    dict_items}
                    decoded_list.append(decoded_dict)
            return decoded_list
        else:
            # List of strings
            return [item.decode() for item in parts if item]
    elif encoded_value == b"\x04":
        return True
    elif encoded_value == b"\x05":
        return False
    else:
        return encoded_value.decode()


def custom_decode(encoded_result):
    result = {}
    if encoded_result.endswith(b"\x01"):
        encoded_result = encoded_result[:-1]

    key_values = encoded_result.split(b"\x01")

    for key_value in key_values:
        key, value = key_value.split(b"\x02", 1)
        result[key.decode()] = decode_value(value)

    return result


def read_with_length(conn, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    length = int.from_bytes(conn.recv(4), byteorder='big')
    buffer = b''

    while length > 0:
        data = conn.recv(length)
        buffer += data
        length -= len(data)

    plaintext = unpad(cipher.decrypt(buffer), AES.block_size)
    return plaintext


def send_with_length(conn, message, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(message, AES.block_size))
    length = len(ciphertext).to_bytes(4, byteorder='big')
    conn.sendall(length + ciphertext)
