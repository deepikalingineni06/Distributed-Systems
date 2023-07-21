"""
server_a.py
-----------
    This middlware server open two socket connections
    for inbound traffic from `Server B` and to share
    response as outbound traffic towards `Server A`
"""

import os
from sys import stderr, exit
import shutil
from time import localtime, strftime
from hashlib import md5
from socket import gethostname, gethostbyname
from socket import AF_INET, SOCK_STREAM, error

from socket import socket
from signal import signal, SIGINT

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# GLOBAL CONFIGS
HOST_NAME = gethostname()
HOST_IP = gethostbyname(HOST_NAME)
PORT_A = 8080
PORT_B = 8081
CLIENT_ARGS = (HOST_IP, PORT_A)
SERVER_ARGS = (HOST_IP, PORT_B)
BUFF = 4096
MAX_CONNS = 10
WATCH_DIR = os.path.join(os.getcwd(), "directory_a")
REMOTE_DIR = os.path.join(os.getcwd(), "directory_b")


def ls(directory=os.getcwd()):
    """
    ls(directory):
    --------------
        Lists files under given directory
        Default: directory=os.getcwd()
    """
    fs = dict()
    for f in os.listdir(directory):
        fs[f] = dict()
        fs[f]["name"] = os.path.split(f)[-1]
        f_info = os.stat(os.path.join(WATCH_DIR, f))
        file_size, mod_tstamp = f_info.st_size, f_info.st_mtime
        fs[f]["size"] = f"{file_size} bytes"
        fs[f]["time"] = strftime("%c", localtime(mod_tstamp))
    return [f["name"].ljust(30) + f["size"] + f["time"].rjust(30) for _, f in fs.items()]

def diff(f1, f2):
    """
    diff(file_name_1, file_name_2):
    -------------------------------
        === Checksum validation ===
           If both file are same:
               return False
           Else:
               return True
    """
    with open(f1, mode="rb") as fh1:
        h1 = md5(fh1.read()).hexdigest()
    with open(f2, mode="rb") as fh2:
        h2 = md5(fh2.read()).hexdigest()
    return h1 != h2

def sync():
    """
    sync():
    ---------------------------------------------
        Initializes synchronization
        between <server_a> & <server_b>
    """
    for local_file in os.listdir(WATCH_DIR):
        src = os.path.join(WATCH_DIR, local_file)
        dst = os.path.join(REMOTE_DIR, local_file)
        shutil.copyfile(src, dst)
    print("[+] Servers in synchronization")
 
def on_created(event):
    """
    _create_event(event):
    ---------------------
        Handles file create event under <WATCH_DIR>
    """
    file = event.src_path.split("/")[-1]
    # Ignore syncing configuration files
    if file[0] == ".":
        return None
    elif os.path.isdir(file):
        return None
    dest = os.path.join(REMOTE_DIR, file)
    if os.path.exists(event.src_path):
        shutil.copyfile(event.src_path, dest)
        print(f"[+] CREATED: {file}")

def on_deleted(event):
    """
    _delete_event(event):
    ---------------------
        Handles file delete event under <WATCH_DIR>
    """
    file = event.src_path.split("/")[-1]
    # Ignore syncing configuration files
    if file[0] == ".":
        return None
    elif os.path.isdir(file):
        return None
    remote_file = os.path.join(REMOTE_DIR, file)
    try:
        os.remove(remote_file)
    except FileNotFoundError:
        pass
    print(f"[+] DELETED: {file}")

def on_modified(event):
    """
    _modify_event(event):
    ---------------------
        Handles file modify event under <WATCH_DIR>
    """
    file = event.src_path.split("/")[-1]
    if file[0] == ".":
        return None
    elif os.path.isdir(file):
        return None
    dest = os.path.join(REMOTE_DIR, file)
    if os.path.exists(dest):
        if diff(event.src_path, dest):
            shutil.copyfile(event.src_path, dest)
            print(f"[+] MODIFIDED: {file}")
    else:
        on_created(event)

def turn_off_server(_sig, _):
    """
    turn_off_server(signal, frame):
    -------------------------------
        Kill server process gracefully
    """
    print("\n" + "=" * 20, " EOS ", "=" * 20)
    exit(0)

signal(SIGINT, turn_off_server)

if __name__ == "__main__":
    # Get <event_handler> object
    event_handler = FileSystemEventHandler()
    # Sync before event context defination
    sync()
    # Assign helper functions for watchdog events
    event_handler.on_created  = on_created
    event_handler.on_deleted  = on_deleted
    event_handler.on_modified = on_modified

    # Get <traker> object
    tracker = Observer()
    tracker.schedule(event_handler=event_handler,
            path=WATCH_DIR,
            recursive=True)

    with socket(AF_INET, SOCK_STREAM) as client_sock:
        try:
            # Serve <client> on request
            client_sock.bind(CLIENT_ARGS)
        except error as e:
            print("[ERROR]:", e, file=stderr)
            exit(1)
        finally:
            # On successfull connection with <client>
            client_sock.listen(MAX_CONNS)
            print(f"[+] Listening on port for <client>: {PORT_A}")

        tracker.start() # Start Tracking
        try:
            print(f"[+] Listening on port for <server>: {PORT_B}")
            while True:
                connection, _address = client_sock.accept() # Accept connections
                with socket(AF_INET, SOCK_STREAM) as server_sock:
                    try:
                        server_sock.connect(SERVER_ARGS)
                    except error as e:
                        print("[ERROR]:", e, file=stderr)
                        exit(1)
                    finally:
                        # On successfull connection with <server>
                        server_response = server_sock.recv(BUFF)
                        print("[+] SUCCESS: File list revecived from server_b")

                    # Fetching both lists
                    local_directory_files = ls(directory=WATCH_DIR)
                    _ = server_response.decode().splitlines()

                    print("[+] Responded to client")
                    connection.send(bytes("\n".join(
                        sorted(local_directory_files)) + "\n",
                        "utf-8")) # Send sorted list to client
        except Exception as ex:
            tracker.stop()
            print("[-] Tracker STOPPED due to SIGINT/overload")
            print("[ERROR DETAILS]:", ex)
        tracker.join() # Wait until it's stopped
