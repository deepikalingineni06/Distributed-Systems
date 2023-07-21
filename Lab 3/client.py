


"""
client.py
---------
    Requests `Server A` for combined list of files
    under directory_a and the list obtained from
    `Server B` of files under `directory_b`
"""

from socket import gethostname, gethostbyname # for IP
from socket import AF_INET, SOCK_STREAM, error # for socket creation
from socket import socket # for socket connection
from sys import argv, stderr, exit # for client command and error handling

# CONSTANTS
HOST_IP = gethostbyname(gethostname())
PORT_A = 8080
BUFF = 4096

def fetch_command():
    """Returns a <bit vector> to send
    <server_a> via a UDP socket"""
    command = "X"
    if _len:=len(argv) == 3:
        command = " ".join(argv[1:])
        command = command.replace("-", "")
    elif _len > 3:
        print("[ERROR]:", "Improper usage of parameter", file=stderr)
        exit(1)
    elif _len == 2:
        print("[ERROR]:", "Parameter not enough to process", file=stderr)
        exit(1)
    return bytes(command, "UTF-8")

with socket(AF_INET, SOCK_STREAM) as out_bound_socket:
    try:
        out_bound_socket.connect((HOST_IP, PORT_A))
        out_bound_socket.send(fetch_command()) # Send client's command to <server_a>
        resp = out_bound_socket.recv(BUFF)
        msg = str(resp, "UTF-8")
        for i, line in enumerate(msg.splitlines()):
            print(f"[{i}]\t{line}")
    except error as e:
        print("[ERROR]:", e, file=stderr)
        exit(1)
