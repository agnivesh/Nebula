import socket
import threading
import struct
import uuid

AGENTS = {}   # agent_id: socket
TUNNELS = {}  # tunnel_id: (client_conn, agent_id, threading.Event)

def recv_exact(sock, n):
    buf = b''
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("Connection closed")
        buf += chunk
    return buf

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

def handle_agent(conn):
    agent_id = str(uuid.uuid4())
    try:
        AGENTS[agent_id] = conn
        print(f"Agent connected: {agent_id}")
        while True:
            msg = conn.recv(1024)
            if not msg:
                break
            print(f"[Agent {agent_id}] {msg.decode().strip()}")
    except Exception as e:
        print(f"Agent error: {e}")
    finally:
        AGENTS.pop(agent_id, None)
        conn.close()

def handle_data_tunnel(conn):
    try:
        tunnel_id = conn.recv(1024).decode().strip()
        if tunnel_id not in TUNNELS:
            print(f"Unknown tunnel ID: {tunnel_id}")
            conn.close()
            return

        client_conn, agent_id, ready_event = TUNNELS.pop(tunnel_id)
        ready_event.set()

        print(f"Tunnel {tunnel_id} connected")

        threading.Thread(target=pipe, args=(client_conn, conn)).start()
        threading.Thread(target=pipe, args=(conn, client_conn)).start()

    except Exception as e:
        print(f"Data tunnel error: {e}")
        conn.close()

def handle_socks4_conn(conn):
    try:
        header = recv_exact(conn, 8)
        vn, cd, dstport, dstip = struct.unpack("!BBH4s", header)
        if vn != 0x04 or cd != 0x01:
            conn.close()
            return

        # Read USERID (null-terminated)
        """
        userid = b''
        while True:
            byte = conn.recv(1)
            if not byte or byte == b'\x00':
                break
            userid += byte

        dest_ip = socket.inet_ntoa(dstip)
        dest = f"{dest_ip}:{dstport}"
        """

        userid = b''
        while True:
            byte = conn.recv(1)
            if not byte or byte == b'\x00':
                break
            userid += byte

        # If IP is 0.0.0.x and x != 0, expect SOCKS4a hostname
        hostname = None
        if dstip[:3] == b'\x00\x00\x00' and dstip[3] != 0:
            hostname = b''
            while True:
                byte = conn.recv(1)
                if not byte or byte == b'\x00':
                    break
                hostname += byte
            dest = f"{hostname.decode()}:{dstport}"
        else:
            dest_ip = socket.inet_ntoa(dstip)
            dest = f"{dest_ip}:{dstport}"

        print(f"SOCKS4 request to {dest}")

        if not AGENTS:
            conn.sendall(b"\x00\x5B\x00\x00\x00\x00\x00\x00")
            conn.close()
            return

        agent_id, agent_conn = next(iter(AGENTS.items()))
        tunnel_id = str(uuid.uuid4())
        ready = threading.Event()
        TUNNELS[tunnel_id] = (conn, agent_id, ready)

        agent_conn.sendall(f"FORWARD {tunnel_id} {dest}\n".encode())

        if not ready.wait(timeout=5):
            print("Agent didn't connect in time")
            conn.sendall(b"\x00\x5B\x00\x00\x00\x00\x00\x00")
            conn.close()
            TUNNELS.pop(tunnel_id, None)
            return

        conn.sendall(b"\x00\x5A\x00\x00\x00\x00\x00\x00")  # SOCKS4 success
    except Exception as e:
        print(f"SOCKS4 error: {e}")
        conn.close()

def start_server(socksport, mgmtsport, listeningport):
    # Accept agent control connections
    threading.Thread(target=lambda: listen_on(mgmtsport, handle_agent)).start()

    # Accept tunnel connections
    threading.Thread(target=lambda: listen_on(listeningport, handle_data_tunnel)).start()

    # Accept SOCKS4 proxy requests
    listen_on(socksport, handle_socks4_conn)

def listen_on(port, handler):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("0.0.0.0", port))
        s.listen()
        print(f"Socks4a Proxy Listening on port {port}")
        while True:
            conn, _ = s.accept()
            threading.Thread(target=handler, args=(conn,)).start()

def main(socksport, mgmtsport, listeningport):
    threading.Thread(start_server(socksport=socksport, mgmtsport=mgmtsport, listeningport=listeningport)).start()
