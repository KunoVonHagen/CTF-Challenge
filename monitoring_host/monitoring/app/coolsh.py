import socket
import random
from sympy import isprime, mod_inverse
import subprocess
import threading
import os


def generate_large_prime(bits):
    while True:
        num = random.getrandbits(bits)
        if isprime(num):
            return num


def generate_keypair(bits, e=65537):
    p = generate_large_prime(bits // 2)
    q = generate_large_prime(bits // 2)
    n = p * q
    phi = (p - 1) * (q - 1)

    while gcd(e, phi) != 1:
        e = random.randrange(2, phi)

    # Compute d
    d = mod_inverse(e, phi)

    return (e, n), (d, n)


def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def rsa_encrypt_block(m, public_key):
    e, n = public_key
    return pow(m, e, n)


def rsa_decrypt_block(c, private_key):
    d, n = private_key
    return pow(c, d, n)


def rsa_encrypt(message: bytes, public_key) -> bytes:
    ciphertext = b''
    block_size = (public_key[1].bit_length() - 1) // 8

    for i in range(0, len(message), block_size):
        block = int.from_bytes(message[i:i + block_size], byteorder='big')
        encrypted_block = rsa_encrypt_block(block, public_key)
        ciphertext += encrypted_block.to_bytes(block_size + 1, byteorder='big')

    return ciphertext


def rsa_decrypt(encrypted_blocks: bytes, private_key) -> bytes:
    message = b''
    block_size = (private_key[1].bit_length() - 1) // 8

    for i in range(0, len(encrypted_blocks), block_size + 1):
        encrypted_block = int.from_bytes(encrypted_blocks[i:i + block_size + 1], byteorder='big')
        decrypted_block = rsa_decrypt_block(encrypted_block, private_key)
        message += decrypted_block.to_bytes(block_size, byteorder='big').lstrip(b'\x00')

    return message


def read_encrypted(conn, sk):
    encrypted_blocks = read_with_length(conn)
    return rsa_decrypt(encrypted_blocks, sk)


def send_encrypted(conn, message, pk):
    encrypted_message = rsa_encrypt(message, pk)
    send_with_length(conn, encrypted_message)


def read_with_length(conn):
    length = int.from_bytes(conn.recv(4), byteorder='big')
    buffer = b''

    while length > 0:
        data = conn.recv(min(4096, length))
        buffer += data
        length -= len(data)

    return buffer


def send_with_length(conn, message):
    length = len(message).to_bytes(4, byteorder='big')
    conn.sendall(length + message)


class ShellServerConnection(threading.Thread):
    def __init__(self, conn, client_public_key, pk, sk):
        threading.Thread.__init__(self)
        self.conn = conn
        self.client_public_key = client_public_key
        self.pk = pk
        self.sk = sk

    def read_and_send(self, proc_fd):
        while True:
            data = proc_fd.read(4096)
            if not data:
                break
            send_encrypted(self.conn, data, self.client_public_key)

    def run(self):
        while True:
            try:
                send_encrypted(self.conn, b'$ ', self.client_public_key)
                command = read_encrypted(self.conn, self.sk).decode()
                if command == 'exit':
                    print(f"Connection closed by client: {self.client_public_key}")
                    self.conn.close()
                    break

                proc = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                stdout_thread = threading.Thread(target=self.read_and_send, args=(proc.stdout,))
                stderr_thread = threading.Thread(target=self.read_and_send, args=(proc.stderr,))

                stdout_thread.start()
                stderr_thread.start()

                stdout_thread.join()
                stderr_thread.join()

            except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
                print(f"Connection closed by client: {self.client_public_key}")
                self.conn.close()
                break

            except Exception as e:
                send_encrypted(self.conn, str(e).encode(), self.client_public_key)







class ShellServer:
    def __init__(self,
                 host: str,
                 port: int,
                 username: str,
                 password: str,
                 pk: tuple = None,
                 sk: tuple = None,
                 keysize: int = 2048,
                 allowed_public_keys: list = []):
        """
        Create a new shell server that listens on the given host and port.
        Use .start() to start the server.

        :param host: The host to bind the server to.
        :type host: str
        :param port: The port to bind the server to.
        :type port: int
        :param username: The username for password authentication.
        :type username: str
        :param password: The password for password authentication.
        :type password: str
        :param pk: The public key the server should use (public_exponent, modulus).
        :type pk: tuple[int, int]
        :param sk: The private key the server should use (private_exponent, modulus).
        :type sk: tuple[int, int]
        :param keysize: The keysize for the RSA keypair if no keypair is provided.
        :type keysize: int
        :param allowed_public_keys: A list of public keys that are allowed to connect with public key authentication.
        :type allowed_public_keys: list[tuple[int, int]]
        """
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.incomming_connections = []
        self.shell_connections = []
        self.shell_credentials = {'username': username, 'password': password}
        if pk is None or sk is None:
            self.public_key, self.private_key = generate_keypair(keysize)

        self.allowed_public_keys = allowed_public_keys

    def start(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        print("Listening on {}:{}".format(self.host, self.port))
        while True:
            conn, _ = self.socket.accept()
            c = NewServerConnection(conn, self)
            c.start()

            for c in self.incomming_connections:
                if not c.is_alive():
                    self.incomming_connections.remove(c)

            for c in self.shell_connections:
                if not c.is_alive():
                    self.shell_connections.remove(c)

    def close(self):
        for c in self.incomming_connections:
            c.socket.close()

        for c in self.shell_connections:
            c.socket.close()

        self.socket.close()

    def __del__(self):
        self.close()


class NewServerConnection(threading.Thread):
    def __init__(self, conn, shell_server: ShellServer):
        threading.Thread.__init__(self)
        self.conn = conn
        self.pk = shell_server.public_key
        self.sk = shell_server.private_key
        self.shell_credentials = shell_server.shell_credentials
        self.allowed_public_keys = shell_server.allowed_public_keys
        self.shell_server = shell_server

    def run(self):
        send_with_length(self.conn, b'Provide your public key for encrypted communication\nPublic exponent: ')
        public_exponent = int.from_bytes(read_with_length(self.conn), byteorder='big')
        send_with_length(self.conn, b'Modulus: ')
        modulus = int.from_bytes(read_with_length(self.conn), byteorder='big')
        client_public_key = (public_exponent, modulus)

        print("established connection with public key: ", client_public_key)

        send_with_length(self.conn, b'I will now send my public key as well (exponent, modulus):\n'
                         + bytes(str(self.pk), 'utf-8')
                         + b'\nRead all following messages using your private key and'
                         + b' communicate with me using my public key from now on\n')

        send_encrypted(self.conn, b'Select a method of authentication\n'
                       + b'1. Password\n'
                       + b'2. Public Key\n', client_public_key)
        method = read_encrypted(self.conn, self.sk).decode()

        if method == '1':
            send_encrypted(self.conn, b'Provide your username: ', client_public_key)
            username = read_encrypted(self.conn, self.sk).decode()
            send_encrypted(self.conn, b'Provide your password: ', client_public_key)
            password = read_encrypted(self.conn, self.sk).decode()

            if username == self.shell_credentials['username'] and password == self.shell_credentials['password']:
                send_encrypted(self.conn, b'Authentication successful!\n\n'
                               + b'Welcome to the cool shell!\n\n'
                               + b'Every line where you can enter'
                               + b' a new command will start with "$ " '
                               + b'starting with the next message.'
                               + b' Just keep receiving until you see it again.', client_public_key)
                c = ShellServerConnection(self.conn, client_public_key, self.pk, self.sk)
                self.shell_server.shell_connections.append(c)
                c.start()

            else:
                send_encrypted(self.conn, b'Authentication failed!\n', client_public_key)
                self.conn.close()

        elif method == '2':
            if client_public_key in self.allowed_public_keys:
                send_encrypted(self.conn, b'Authentication successful!\n\n'
                               + b'Welcome to the cool shell!\n\n'
                               + b'Every line where you can enter'
                               + b' a new command will start with "$ "'
                               + b' starting with the next message.'
                               + b' Just keep receiving until you see it again.', client_public_key)
                c = ShellServerConnection(self.conn, client_public_key, self.pk, self.sk)
                self.shell_server.shell_connections.append(c)
                c.start()

            else:
                send_encrypted(self.conn, b'Authentication failed\n', client_public_key)
                self.conn.close()


class ShellClient:
    def __init__(self,
                 host: str,
                 port: int,
                 username: str = None,
                 password: str = None,
                 pk: tuple = None,
                 sk: tuple = None,
                 pk_authentication: bool = False,
                 keysize: int = 2048):
        """
        Establish a connection to a shell server.
        use .start() to start the shell.

        :param host: The host to connect to
        :param port: The port to connect to
        :param pk: The public key the client should use (public_exponent, modulus)
        :param sk: The private key the client should use (private_exponent, modulus)
        :param username: The username for password authentication
        :param password: The password for password authentication
        :param pk_authentication: Whether to use public key authentication
        :param keysize: The keysize for the RSA keypair if no keypair is provided
        """

        self.host = host
        self.port = port
        self.pk_authentication = pk_authentication
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if pk_authentication:
            if pk is None or sk is None:
                raise ValueError("Public and private key must be provided for public key authentication")
            self.pk = pk
            self.sk = sk
        else:
            if username is None or password is None:
                raise ValueError("Username and password must be provided for password authentication")
            self.username = username
            self.password = password
            if pk is None or sk is None:
                self.pk, self.sk = generate_keypair(keysize)

    def close(self):
        self.socket.close()

    def __del__(self):
        self.close()

    def start(self):
        """
        Connect to the server and start the shell
        """
        self.socket.connect((self.host, self.port))

        read_with_length(self.socket)
        send_with_length(self.socket, self.pk[0].to_bytes(self.pk[1].bit_length() // 8 + 1, byteorder='big'))
        # Provide your public key for encrypted communication
        # Public exponent: public_exponent
        read_with_length(self.socket)
        send_with_length(self.socket, self.pk[1].to_bytes(self.pk[1].bit_length() // 8 + 1, byteorder='big'))
        # Modulus: modulus
        server_pk_message = read_with_length(self.socket).decode()
        # I will now send my public key as well (exponent, modulus): (public_key)
        server_pk_info = server_pk_message.split('\n')[1].replace('(', '').replace(')', '')
        server_pk = (int(server_pk_info.split(",")[0]), int(server_pk_info.split(",")[1]))

        print("established connection with public key: ", server_pk)

        read_encrypted(self.socket, self.sk)
        # Select a method of authentication
        # 1. Password
        # 2. Public Key

        if not self.pk_authentication:
            send_encrypted(self.socket, b'1', server_pk)
            read_encrypted(self.socket, self.sk)
            # Provide your username:
            send_encrypted(self.socket, self.username.encode(), server_pk)
            read_encrypted(self.socket, self.sk)
            # Provide your password:
            send_encrypted(self.socket, self.password.encode(), server_pk)
            success = read_encrypted(self.socket, self.sk).decode()

        else:
            send_encrypted(self.socket, b'2', server_pk)
            success = read_encrypted(self.socket, self.sk).decode()

        if success == 'Authentication failed!\n':
            self.close()
            raise ValueError("Authentication failed")

        while True:
            while (message := read_encrypted(self.socket, self.sk)) != b'$ ':
                print(message.decode(errors='ignore'), end='')

            print("$ ", end='')
            command = input()
            if command == 'exit':
                send_encrypted(self.socket, command.encode(), server_pk)
                break
            send_encrypted(self.socket, command.encode(), server_pk)

        self.close()
