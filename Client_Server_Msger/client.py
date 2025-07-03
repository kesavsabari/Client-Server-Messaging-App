# client.py
# This is the client part. It connects to the server.
# You can send messages or files to other users.

import socket
import threading
import json
import os

HOST = '127.0.0.1'  # Server address
PORT = 5555         # Server port

name = input("Your name: ")  # Ask user for their name

# This runs in the background to listen for messages from the server
def listen(sock):
    while True:
        try:
            data = sock.recv(65536).decode()
            if not data:
                break
            msg = json.loads(data)
            if msg['type'] == 'msg':
                print(f"\n[{msg['from']}] {msg['data']}")
            elif msg['type'] == 'file':
                fname = msg['filename']
                content = msg['filedata'].encode('latin1')
                with open("got_" + fname, "wb") as f:
                    f.write(content)
                print("\nGot file:", fname)
            elif msg['type'] == 'error':
                print("\nError:", msg['data'])
        except:
            break

# Connect to the server
c = socket.socket()
c.connect((HOST, PORT))

# Tell server our name
first = {"type": "register", "username": name}
c.send(json.dumps(first).encode())

# Start the background thread to listen
threading.Thread(target=listen, args=(c,), daemon=True).start()

# Main loop: send messages or files
while True:
    to = input("\nSend to: ")  # Who to send to
    text = input("Message (or /file path): ")

    if text.startswith("/file "):
        path = text[6:]
        if os.path.isfile(path):
            with open(path, "rb") as f:
                data = f.read()
            msg = {
                "type": "file",
                "from": name,
                "to": to,
                "filename": os.path.basename(path),
                "filedata": data.decode('latin1')
            }
            c.send(json.dumps(msg).encode())
            print("Sent file:", path)
        else:
            print("No such file")
    else:
        # Normal text message
        msg = {"type": "msg", "from": name, "to": to, "data": text}
        c.send(json.dumps(msg).encode())
