import socket
from db_library import send_with_length, read_with_length, custom_decode

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

        return custom_decode(response)

    def close(self):
        self.socket.close()
