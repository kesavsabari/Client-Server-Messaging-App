# server.py
# This is the server part of the chat app.
# It waits for people to join, keeps track of them, and passes their messages.

import socket
import threading
import json

HOST = '127.0.0.1'   # This computer
PORT = 5555          # Port number to listen on

users = {}  # Save who is connected: {username: their socket}

# This function talks to one person
def client_thread(conn):
    name = None  # Will be the user's name
    try:
        # First message must tell us the username
        data = conn.recv(1024).decode()
        info = json.loads(data)
        if info['type'] == 'register':
            name = info['username']
            users[name] = conn
            print(name, "joined")

        # Keep listening for messages
        while True:
            data = conn.recv(65536).decode()
            if not data:
                break
            msg = json.loads(data)
            if msg['type'] == 'msg' or msg['type'] == 'file':
                to = msg['to']
                if to in users:
                    # Send the message or file to the right person
                    users[to].send(json.dumps(msg).encode())
                else:
                    # Tell sender that person is not online
                    err = {"type": "error", "data": to + " not online"}
                    conn.send(json.dumps(err).encode())
    except:
        print("error with", name)
    finally:
        # Remove this user when they leave
        if name in users:
            del users[name]
        conn.close()
        print(name, "left")

# Make a socket and start listening
s = socket.socket()
s.bind((HOST, PORT))
s.listen()
print("Server started on", HOST, PORT)

# Keep accepting new people
while True:
    conn, addr = s.accept()
    threading.Thread(target=client_thread, args=(conn,)).start()
