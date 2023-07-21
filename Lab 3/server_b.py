


"""
server_b.py
-----------
    This backedn server open a single out-bond socket
    connection for communicating with `Server A` and
    share a list of files under its WATCH DIRECTORY
"""

import os
from sys import stderr, exit
import shutil
from hashlib import md5
from socket import (
        gethostbyname,
        gethostname,
        AF_INET,
        SOCK_STREAM,
        error)

from socket import socket
from signal import signal, SIGINT

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

##### DEFAULT CONFIGURATIONS #####
HOST_NAME = gethostname()
HOST_IP = gethostbyname(HOST_NAME)
PORT_B = 8081
SERVER_CONFIGS = (HOST_IP, PORT_B)
BUFFER_SIZE = 2048 * 2
MAX_CONNS = 10
WATCH_DIR = os.path.join(os.getcwd(), "directory_b")
REMOTE_DIR = os.path.join(os.getcwd(), "directory_a")
##################################

# ==== Helper function(s) ==== #
def ls(directory=os.getcwd()):
    fs = dict()
    for f in os.listdir(directory):
        fs[f] = dict()
        fs[f]["name"] = os.path.split(f)[-1]
        fs[f]["size"] = f"{os.path.getsize(os.path.join(WATCH_DIR, f))} bytes"
        fs[f]["time"] = str(os.path.getmtime(os.path.join(WATCH_DIR, f))) # Last modified time
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
    print(":OK")

def _create_event(event):
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

def _delete_event(event):
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
        if os.access(remote_file, os.W_OK):
            os.remove(remote_file)
    except FileNotFoundError:
        pass
    print(f"[+] DELETED: {file}")

def _modify_event(event):
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
        if diff(event.src_path, dest) and os.access(dest, os.W_OK):
            try:
                shutil.copyfile(event.src_path, dest)
                print(f"[+] MODIFIDED: {file}")
            except PermissionError:
                print(f"[...] MODIFICATION QUEUED: {file} - locked")
    else: _create_event(event)

def turn_off_server(_sig, _):
    print("\n" + "=" * 20, " EOS ", "=" * 20)
    exit(1)

signal(SIGINT, turn_off_server)

if __name__ == "__main__":
    # Get <event_handler> object
    event_handler =  FileSystemEventHandler()
    # Sync before event context defination
    sync()

    # Assign helper functions for watchdog events
    event_handler.on_created  = _create_event
    event_handler.on_deleted  = _delete_event
    event_handler.on_modified = _modify_event

    # Get <traker> object
    tracker = Observer()
    tracker.schedule(event_handler=event_handler,
            path=WATCH_DIR,
            recursive=True)

    tracker.start() # Start Tracking
    with socket(AF_INET, SOCK_STREAM) as server_sock:
        try:
            # Serve <middleware server> on request
            server_sock.bind(SERVER_CONFIGS)
        except error as e:
            print("[ERROR]:", e, file=stderr)
            exit(0)
        finally:
            # On successfull connection with <middleware server>
            server_sock.listen(MAX_CONNS)
            # ^^^ Deals with multi-threading under the hood
            print(f"[+] Listening on port for <middleware server>: {PORT_B}")
    
        try:
            while True:
                connection, _address = server_sock.accept() # Accept connections
                response = "\n".join(ls(WATCH_DIR))
                connection.send(bytes(response + "\n", "UTF-8")) # Send sorted list to client
                print(":LIST SENT\n")
        except:
            tracker.stop()
            print("[-] Tracker STOPPED due to SIGINT/overload")
        tracker.join() # Wait until it's stopped
