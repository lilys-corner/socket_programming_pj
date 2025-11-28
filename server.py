#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Author : Ayesha S. Dina

import os
import socket
import threading

IP = "localhost"
PORT = 4450
ADDR = (IP,PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_PATH = "server"

### to handle the clients
def handle_client (conn,addr):

    print(f"[NEW CONNECTION] {addr} connected.")
    conn.send("OK@Welcome to the server".encode(FORMAT))
    
    uploaded = []

    while True:
        data =  conn.recv(SIZE).decode(FORMAT)
        data = data.split("@")
        cmd = data[0]
       
        send_data = "OK@"

        if cmd == "LOGOUT":
            break

        elif cmd == "TASK": 
            send_data += "LOGOUT from the server.\n"
            send_data += "UPLOAD a file to the server.\n"

            conn.send(send_data.encode(FORMAT))

        elif cmd == "UPLOAD":
            send_data += "Ready to receive the file.\n"
            conn.send(send_data.encode(FORMAT))
            # send to client_1 that you're ready
            
            print("Here")
            
            filename = conn.recv(SIZE).decode(FORMAT).strip()
            # get filename

            send_data = "File received successfully.\n"
            conn.send(send_data.encode(FORMAT))
            # send confirmation, client_1 receives it
            
            with open(filename, "w") as fo:
                while True:
                    data = conn.recv(SIZE).decode(FORMAT)
                    if not data:
                        break
                    if data == "EOF":
                        break

                    fo.write(data)
            # receive data, copy it
            fo.close()
            
            print(f"File {filename} received from {addr}")
            # tell yourself that you got it w/ location
            
            send_data = f"OK@File {filename} uploaded successfully.\n"
            conn.send(send_data.encode(FORMAT))
            # send final confirmation
        
        # TO DO
        elif cmd == "DOWNLOAD":
            continue
        # TO DO
        elif cmd == "DELETE":
            continue
        # TO DO
        elif cmd == "DIR":
            continue
        # TO DO
        elif cmd == "SUBFOLDER":
            continue


    print(f"{addr} disconnected")
    conn.close()


def main():
    print("Starting the server")
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM) ## used IPV4 and TCP connection
    server.bind(ADDR) # bind the address
    server.listen() ## start listening
    print(f"server is listening on {IP}: {PORT}")
    while True:
        conn, addr = server.accept() ### accept a connection from a client
        thread = threading.Thread(target = handle_client, args = (conn, addr)) ## assigning a thread for each client
        thread.start()


if __name__ == "__main__":
    main()
