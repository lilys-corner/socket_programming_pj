#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Author : Ayesha S. Dina

import os
import socket
import threading
from time import time

IP = "localhost"
PORT = 4450
ADDR = (IP,PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_PATH = "server"

COUNTER = 1

### to handle the clients
def handle_client (conn,addr):

    print(f"[NEW CONNECTION] {addr} connected.")
    conn.send("OK@Welcome to the server".encode(FORMAT))
    
    # list to track uploaded files
    uploaded = []
    
    # list to track subdirectories (for later)

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
            send_data += "DOWNLOAD a file from the server.\n"
            send_data += "DELETE a file from the server.\n"

            conn.send(send_data.encode(FORMAT))

        elif cmd == "UPLOAD":
            # send to client_1 that you're ready
            send_data += "Ready to receive the file.\n"
            conn.send(send_data.encode(FORMAT))
            
            # get filename
            filename = conn.recv(SIZE).decode(FORMAT).strip()
            
            global COUNTER
            
            # checks if the file has already been uploaded
            if (filename in uploaded):
                # if it's been uploaded, send a 1 to client to let it know
                send_data = "File received successfully. 1\n"
                conn.send(send_data.encode(FORMAT))
                
                # receive if user wants to overwrite it (Y/N)
                ans = conn.recv(SIZE).decode(FORMAT)
                
                # if user wants to overwrite, upload file again
                if (ans == "Y"):
                    # receive data, copy it
                    new_filename = "TS" + ("%03d" % COUNTER)
                    with open(new_filename, "w") as fo:
                        while True:
                            data = conn.recv(SIZE).decode(FORMAT)
                            if not data:
                                break
                            if data == "EOF":
                                break
                            fo.write(data)
                        fo.close()
                    COUNTER += 1
                    
                    # tell yourself that you got it w/ location
                    print(f"File {filename} received from {addr}")
                    
                    # send final confirmation
                    send_data = f"OK@File {filename} overwritten.\n"
                    conn.send(send_data.encode(FORMAT))
                
                # if user doesn't want to overwrite, end
                else:
                    send_data = f"OK@File {filename} not overwritten.\n"
                    conn.send(send_data.encode(FORMAT))
            
            # if file not already uploaded, upload the filee
            else:
                # send confirmation, client_1 receives it
                send_data = "File received successfully.\n"
                conn.send(send_data.encode(FORMAT))
                
                # receive data, copy it
                new_filename = "TS" + ("%03d" % COUNTER)
                with open(new_filename, "w") as fo:
                    while True:
                        data = conn.recv(SIZE).decode(FORMAT)
                        if not data:
                            break
                        if data == "EOF":
                            break
    
                        fo.write(data)
                    fo.close()
                COUNTER += 1
                
                # add uploaded file to the uploaded list so we know we have it
                uploaded.append(filename)
                
                # tell yourself that you got it w/ location
                print(f"File {filename} received from {addr}")
                
                # send final confirmation
                send_data = f"OK@File {filename} uploaded as {new_filename} successfully.\n"
                conn.send(send_data.encode(FORMAT))
        
        # TO DO
        elif cmd == "DOWNLOAD":
            # send to client_1 that you're ready
            send_data += "Ready to receive the file.\n"
            conn.send(send_data.encode(FORMAT))
            
            # get filename
            filename = conn.recv(SIZE).decode(FORMAT).strip()
            
            if (filename in uploaded):
                continue
                ### IMPLEMENT SENDING FILE TO CLIENT
                
            else:
                send_data = "File received successfully. 1\n"
                conn.send(send_data.encode(FORMAT))
                
                send_data = f"OK@File {filename} is unable to be downloaded: does not exist.\n"
                conn.send(send_data.encode(FORMAT))
        
        elif cmd == "DELETE":
            # send to client_1 that you're ready
            send_data += "Ready to receive the file.\n"
            conn.send(send_data.encode(FORMAT))
            
            # get filename
            filename = conn.recv(SIZE).decode(FORMAT).strip()
            
            # if file exists in server, delete it
            if (filename in uploaded):
                uploaded.remove(filename)
                
                send_data = f"OK@File {filename} successfully deleted.\n"
                conn.send(send_data.encode(FORMAT))
            
            # if file does not exist in server, do nothing and say it doesn't exist
            else:
                send_data = f"OK@File {filename} unable to be deleted: does not exist.\n"
                conn.send(send_data.encode(FORMAT))
            
        # TO DO
        elif cmd == "DIR":
            continue
        
        # TO DO
        elif cmd == "SUBFOLDER":
            continue
        
        elif cmd == "ANALYZE":
            send_data = f"OK@Please only use the ANALYZE function using analysis.py.\n"
            conn.send(send_data.encode(FORMAT))
            
        elif cmd == "AN1ANALYZE":
            send_data += "Analysis request received"
            conn.send(send_data.encode(FORMAT))
            
            if (os.path.isfile("connection_time.txt") == True):
                with open("connection_time.txt","r") as fo:
                    data = fo.read(SIZE)
                    if not data:
                        send_data = "File is empty. 1"
                        conn.send(send_data.encode(FORMAT))
                        send_data = "OK@Server connection time does not exist."
                        conn.send(send_data.encode(FORMAT))
                    else:
                        send_data = "Analyzing connection time..."
                        conn.send(send_data.encode(FORMAT))
                        # continues past this if/else!!!, will analyze other things. Leave this part alone, make more if/thens below
            else:
                send_data = "File does not exist. 1"
                conn.send(send_data.encode(FORMAT))
                
                send_data = "OK@Server connection time does not exist."
                conn.send(send_data.encode(FORMAT))
            # confirm that files are there, analysis.py will save them to dictionary
        
        else:
            if "AN1" not in cmd:
                send_data = f"OK@There is no option for {cmd}. Please try again or type TASK for help.\n"
                conn.send(send_data.encode(FORMAT))
            else:
                send_data = f"OK@There is no option for {cmd[3:]}. Please type ANALYZE to analyze performance data.\n"
                conn.send(send_data.encode(FORMAT))


    print(f"{addr} disconnected")
    conn.close()

def write_conn_time(conn_time):
    with open("connection_time.txt", "w") as fo:
        fo.write(str(conn_time))
        fo.close()

def main():
    print("Starting the server")
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM) ## used IPV4 and TCP connection
    server.bind(ADDR) # bind the address
    server.listen() ## start listening
    print(f"server is listening on {IP}: {PORT}")
    os.system("start cmd /k python analysis.py")
    while True:
        conn, addr = server.accept() ### accept a connection from a client
        t1 = time()
        thread = threading.Thread(target = handle_client, args = (conn, addr)) ## assigning a thread for each client
        thread.start()
        t2 = time()
        conn_time = t2 - t1
        print(f"Connection time: {conn_time}")
        write_conn_time(conn_time)


if __name__ == "__main__":
    main()
