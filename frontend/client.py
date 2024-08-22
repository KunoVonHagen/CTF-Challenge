import socket
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

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


class DatabaseClient:
    def __init__(self, host:str, port:int, key:bytes, iv:bytes):
        self.host = host
        self.port = port
        self.key = key
        self.iv = iv
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

    def request(self, action: str, **kwargs):
        message = action.encode() + b"\x00" + b"\x01".join([b"%s\x02%s" % (key.encode(), value.encode()) for key, value in kwargs.items()])
        send_with_length(self.socket, message, self.key, self.iv)
        response = read_with_length(self.socket, self.key, self.iv)
        formatted_response = {}

        for kv_pair in response.split(b"\x01"):
            key, value = kv_pair.split(b"\x02")
            key = key.decode()
            if b"\x03" in value:
                value = list(map(bytes.decode, value.split(b"\x03")))[:-1]
            elif value == b"\x04" or value == b"\x05":
                value = (value == b"\x04")
            else:
                value = value.decode()

            formatted_response[key] = value

        return formatted_response

    def close(self):
        self.socket.close()
