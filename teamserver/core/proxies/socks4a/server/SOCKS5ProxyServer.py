import socket
import struct
import threading
import uuid

AGENTS = {}
TUNNELS = {}

def handle_control(conn, addr):
    agent_id = str(addr)
    AGENTS[agent_id] = conn
    print(f"Agent connected: {agent_id}")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
    finally:
        del AGENTS[agent_id]
        conn.close()

def handle_data_listener():
    sock = socket.socket()
    sock.bind(('0.0.0.0', 9001))
    sock.listen()
    print("Data channel on port 9001")
    while True:
        conn, _ = sock.accept()
        threading.Thread(target=handle_data_tunnel, args=(conn,)).start()

def handle_data_tunnel(conn):
    tunnel_id = conn.recv(1024).decode().strip()
    if tunnel_id not in TUNNELS:
        conn.close()
        return
    client_conn, _ = TUNNELS.pop(tunnel_id)
    threading.Thread(target=pipe, args=(client_conn, conn)).start()
    threading.Thread(target=pipe, args=(conn, client_conn)).start()

def pipe(src, dst):
    try:
        while True:
            data = src.recv(4096)
            if not data:
                break
            dst.sendall(data)
    finally:
        src.close()
        dst.close()

def socks5_proxy(listen_port):
    sock = socket.socket()
    sock.bind(("0.0.0.0", listen_port))
    sock.listen(100)
    print(f"SOCKS5 proxy listening on port {listen_port}")

    while True:
        client_conn, _ = sock.accept()
        threading.Thread(target=handle_socks5_conn, args=(client_conn,)).start()

def recv_exact(sock, n):
    buf = b''
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("Connection closed while reading data")
        buf += chunk
    return buf

def handle_socks5_conn(conn):
    try:
        # SOCKS5 handshake
        header = recv_exact(conn, 2)
        ver, nmethods = header[0], header[1]
        _ = recv_exact(conn, nmethods)  # ignore methods
        conn.sendall(b"\x05\x00")  # No auth

        # SOCKS5 request
        request = recv_exact(conn, 4)
        ver, cmd, _, atyp = struct.unpack("!BBBB", request)

        if atyp == 1:  # IPv4
            print(atyp)
            addr = socket.inet_ntoa(recv_exact(conn, 4))
        elif atyp == 3:  # Domain
            print(atyp)
            domain_len = recv_exact(conn, 1)[0]
            addr = recv_exact(conn, domain_len).decode()
        else:
            print("Unsupported address type")
            conn.close()
            return

        port = struct.unpack('!H', recv_exact(conn, 2))[0]
        dest = f"{addr}:{port}"

        print(f"SOCKS request to {dest}")

        # Choose any available agent
        if not AGENTS:
            print("No agents available")
            conn.close()
            return
        agent_id, agent_conn = next(iter(AGENTS.items()))

        tunnel_id = str(uuid.uuid4())
        TUNNELS[tunnel_id] = (conn, agent_id)

        # Send forwarding request to agent
        agent_conn.sendall(f"FORWARD {tunnel_id} {dest}\n".encode())

        # Reply success to SOCKS5
        reply = b"\x05\x00\x00\x01" + b"\x00\x00\x00\x00" + b"\x00\x00"
        conn.sendall(reply)

    except Exception as e:
        print(f"SOCKS error: {e}")
        conn.close()


def main():
    threading.Thread(target=handle_data_listener, daemon=True).start()

    ctrl_socket = socket.socket()
    ctrl_socket.bind(("0.0.0.0", 9000))  # control channel
    ctrl_socket.listen(10)
    threading.Thread(target=socks5_proxy, args=(1080,), daemon=True).start()
    print("Control channel on port 9000")

    while True:
        conn, addr = ctrl_socket.accept()
        threading.Thread(target=handle_control, args=(conn, addr)).start()

if __name__ == "__main__":
    main()
