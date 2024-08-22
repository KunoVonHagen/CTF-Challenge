import socket
import threading
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


class DatabaseServer:
    def __init__(self, ip, port, actions, key, iv):
        self.actions = actions
        self.ip = ip
        self.port = port
        self.key = key
        self.iv = iv

    def add_action(self, action, function):
        if action in self.actions:
            raise ValueError("Action already exists")
        self.actions[action] = function

    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.ip, self.port))
        server.listen(5)

        while True:
            conn, addr = server.accept()
            print("New connection from", addr)
            db_connection = DatabaseConnection(conn, self.actions, self.key, self.iv)
            db_connection.start()

class DatabaseConnection(threading.Thread):
    def __init__(self, socket:socket.socket, actions, key, iv):
        threading.Thread.__init__(self)
        self.socket = socket
        self.actions = actions
        self.actions.update({"exit": self.exit})
        self.running = True
        self.key = key
        self.iv = iv

    def exit(self):
        send_with_length(self.socket, "Exiting".encode(), self.key, self.iv)
        self.socket.close()
        self.running = False

    def run(self):
        while self.running:
            data = read_with_length(self.socket, self.key, self.iv)
            action, args = data.split(b"\x00")
            action = action.decode()
            args = args.split(b"\x01")
            kwargs = {}
            if len(args) >= 1:
                for arg in args:
                    if arg != b"":
                        key, value = arg.split(b"\x02")
                        kwargs[key.decode()] = value.decode()


            if action in self.actions:
                try:
                    print(f"Executing action {action} with args {kwargs}")
                    result = self.actions[action](**kwargs)

                    formatted_result = b""
                    for key, value in result.items():
                        if isinstance(value, list):
                            formatted_value = b"\x03".join([item.encode() for item in value]) + b"\x03"

                        elif isinstance(value, bool):
                            formatted_value = b"\x04" if value else b"\x05"

                        else:
                            formatted_value = value.encode()

                        formatted_result += key.encode() + b"\x02" + formatted_value + b"\x01"

                    if b"\x01" in formatted_result:
                        formatted_result = formatted_result[:-1]

                    send_with_length(self.socket, formatted_result, self.key, self.iv)

                except Exception as e:
                    send_with_length(self.socket, str(e).encode(), self.key, self.iv)
                    print(f"Error while executing action {action}: {e}")

            else:
                send_with_length(self.socket, "Action not found".encode(), self.key, self.iv)
                print(f"Action {action} not found")
