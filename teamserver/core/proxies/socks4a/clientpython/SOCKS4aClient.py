import socket
import struct
import threading

def client_connect(server_host, server_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_host, server_port))
    print(f"[+] Connected to proxy server {server_host}:{server_port}")

    while True:
        # Read destination info
        header = b""
        while len(header) < 2:
            chunk = sock.recv(2 - len(header))
            if not chunk:
                raise Exception("Connection closed by server")
            header += chunk
        port = struct.unpack(">H", header)[0]

        domain = b""
        while True:
            byte = sock.recv(1)
            if byte == b'\x00':
                break
            domain += byte
        dest_host = domain.decode()

        print(f"[+] Connecting to {dest_host}:{port}")

        try:
            remote = socket.create_connection((dest_host, port))
            sock.sendall(b'\x00')  # Success
        except Exception as e:
            sock.sendall(b'\x01')  # Failure
            continue

        # Full-duplex relay
        def forward(src, dst):
            try:
                while True:
                    data = src.recv(4096)
                    if not data:
                        break
                    dst.sendall(data)
            finally:
                src.close()
                dst.close()

        threading.Thread(target=forward, args=(sock, remote)).start()
        threading.Thread(target=forward, args=(remote, sock)).start()

if __name__ == "__main__":
    client_connect("127.0.0.1", 9090)
