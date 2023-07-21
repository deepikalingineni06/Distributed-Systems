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
from sys import stderr, exit # for error handling

# CONSTANTS
HOST_IP = gethostbyname(gethostname())
PORT_A = 8080
BUFF = 4096

print("Press [Enter] to continue")
print("Type [q] to quit")

while input(f"{HOST_IP}:").lower() != "q":
    with socket(AF_INET, SOCK_STREAM) as out_bound_socket:
        try:
            out_bound_socket.connect((HOST_IP, PORT_A))
        except error as e:
            print("[ERROR]:", e, file=stderr)
            exit(1)
    
        resp = out_bound_socket.recv(BUFF)
        msg = str(resp, "UTF-8")
        print(msg)
