# COMPUTER NETWORKS (CNT3004-04) FINAL PROJECT
# FILE SHARING SYSTEM
# Qinhe Yu, Hailey Schluter, Hayley Kintner, Micaela Predestin

import signal
import hashlib
import shutil
import sys

import os
import socket
import threading
from time import time, sleep

IP = "localhost"
PORT = 4450
ADDR = (IP,PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_PATH = "server"

TCOUNTER = 1
ACOUNTER = 1
VCOUNTER = 1

def write_a_file(filename, value):
    with open(filename, "w") as fo:
        fo.write(str(value))
        fo.close()

### to handle the clients
def handle_client (conn,addr):

    print(f"[NEW CONNECTION] {addr} connected.")
    conn.send("OK@Welcome to the server".encode(FORMAT))
    
    # dictionary to map files with their uploaded counterparts
    uploaded = {}
    
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
            
            filesize = conn.recv(SIZE).decode(FORMAT).strip() # STORES FILE SIZE
            
            global TCOUNTER
            global ACOUNTER
            global VCOUNTER
            
            send_data = f"File size received {filesize} bytes.\n"
            conn.send(send_data.encode(FORMAT))
            
            # checks if the file has already been uploaded
            if (filename in uploaded):
                # if it's been uploaded, send a 1 to client to let it know
                send_data = "File received successfully. 1\n"
                conn.send(send_data.encode(FORMAT))
                
                # receive if user wants to overwrite it (Y/N)
                ans = conn.recv(SIZE).decode(FORMAT)
                
                # if user wants to overwrite, upload file again
                if (ans == "Y"):
                    t1 = time()
                    # receive data, copy it
                    new_filename = uploaded[filename]
                    received_data = 0
                    with open(new_filename, "wb") as fo:
                        while received_data < int(filesize):
                            data = conn.recv(SIZE)
                            if not data:
                                break
                            fo.write(data)
                            received_data += len(data)
                        fo.close()
                    
                    t2 = time()
                    upload_time = t2 - t1
                    write_a_file("upload_time.txt", upload_time)
                    
                    up_rate = ((float(filesize) / 1024) / 1024) * upload_time
                    write_a_file("up_rate.txt", up_rate)
                    
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
                t1 = time()
                # send confirmation, client_1 receives it
                send_data = "File received successfully.\n"
                conn.send(send_data.encode(FORMAT))
                
                # receive data, copy it
                file_type = filename[-4:]
                if (file_type == ".txt"):
                    new_filename = "TS" + ("%03d" % TCOUNTER)
                elif (file_type == ".mp3"):
                    new_filename = "AS" + ("%03d" % ACOUNTER)
                else:
                    new_filename = "VS" + ("%03d" % VCOUNTER)
                    
                received_data = 0
                with open(new_filename, "wb") as fo:
                    while received_data < int(filesize):
                        data = conn.recv(SIZE)
                        if not data:
                            break
                        fo.write(data)
                        received_data += len(data)
                    fo.close()
                
                t2 = time()
                upload_time = t2 - t1
                write_a_file("upload_time.txt", upload_time)
                
                up_rate = ((float(filesize) / 1024) / 1024) * upload_time
                write_a_file("up_rate.txt", up_rate)
                
                if (file_type == ".txt"):
                    TCOUNTER += 1
                elif (file_type == ".mp3"):
                    ACOUNTER += 1
                else:
                    VCOUNTER += 1
                
                # add uploaded file to the uploaded list so we know we have it
                uploaded[filename] = new_filename
                
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
                file_type = filename[-4:]
                if (file_type == ".txt"):
                    new_filename = uploaded[filename] + "_download.txt"
                elif (file_type == ".mp3"):
                    new_filename = uploaded[filename] + "_download.mp3"
                else:
                    new_filename = uploaded[filename] + "_download.mp4"
                
                t1 = time()
                
                send_data = "File received successfully.\n"
                conn.send(send_data.encode(FORMAT))
                
                filesize = os.path.getsize(uploaded[filename]) # STORES FILE SIZE
                conn.send(str(filesize).encode(FORMAT))
                
                conn.send(new_filename.encode(FORMAT))
                
                with open(uploaded[filename],"rb") as fo:
                    while True:
                        data = fo.read(SIZE)
                        if not data:
                            conn.send(data)
                            break
                        conn.sendall(data)
                    fo.close()
                
                t2 = time()
                dnload_time = t2 - t1
                write_a_file("dnload_time.txt", dnload_time)
                
                dn_rate = ((float(filesize) / 1024) / 1024) * dnload_time
                write_a_file("dn_rate.txt", dn_rate)
                
                sleep(0.1)
                    
                print(f"Sent {new_filename} to {addr}.")
                    
                send_data = f"OK@File {filename} has been downloaded as {new_filename}.\n"
                conn.send(send_data.encode(FORMAT))
                
            else:
                send_data = "File received successfully. 1\n"
                conn.send(send_data.encode(FORMAT))
                
                send_data = f"OK@File {filename} is unable to be downloaded: it has not been uploaded.\n"
                conn.send(send_data.encode(FORMAT))
        
        elif cmd == "DELETE":
            # send to client_1 that you're ready
            send_data += "Ready to receive the file.\n"
            conn.send(send_data.encode(FORMAT))
            
            # get filename
            filename = conn.recv(SIZE).decode(FORMAT).strip()
            
            # if file exists in server, delete it
            if (filename in uploaded):
                os.remove(uploaded[filename])
                del uploaded[filename]
                
                send_data = f"OK@File {filename} successfully deleted.\n"
                conn.send(send_data.encode(FORMAT))
            
            # if file does not exist in server, do nothing and say it doesn't exist
            else:
                send_data = f"OK@File {filename} unable to be deleted: does not exist.\n"
                conn.send(send_data.encode(FORMAT))
            
        elif cmd == "DIR":
            global SERVER_PATH
            conn.send("OK@Directory listing requested.\n".encode(FORMAT)) # Server sends ready signal

            try:
                files_and_dirs = os.listdir(SERVER_PATH)
                if not files_and_dirs:
                    conn.send("No items in current directory.\n".encode(FORMAT))
                else:
                    for item in files_and_dirs:
                        conn.send((item + "\n").encode(FORMAT))
                        sleep(0.01) # Small delay to ensure client can process chunks
            except OSError as e:
                conn.send(f"Error listing directory: {e}\n".encode(FORMAT))
            conn.send("EOF".encode(FORMAT)) # End of listing signal

        elif cmd == "SUBFOLDER":
            conn.send("OK@Ready for subfolder action.\n".encode(FORMAT)) # Server sends ready signal

            client_sub_action_data = conn.recv(SIZE).decode(FORMAT)
            sub_action_parts = client_sub_action_data.split("@")
            sub_action = sub_action_parts[0]
            sub_path = sub_action_parts[1] if len(sub_action_parts) > 1 else ""

            response_messages = []

            if sub_action == "CREATE":
                full_path = os.path.join(SERVER_PATH, sub_path)
                try:
                    if os.path.exists(full_path):
                        response_messages.append("Folder already exists!")
                    else:
                        os.makedirs(full_path)
                        response_messages.append("Folder created successfully.")
                except OSError as e:
                    response_messages.append(f"Error creating folder: {e}")

            elif sub_action == "DELETE":
                full_path = os.path.join(SERVER_PATH, sub_path)
                try:
                    if not os.path.exists(full_path):
                        response_messages.append("Folder not found.")
                    elif not os.path.isdir(full_path):
                        response_messages.append("Path is not a directory.")
                    else:
                        shutil.rmtree(full_path)
                        response_messages.append("Folder deleted successfully.")
                except OSError as e:
                    response_messages.append(f"Error deleting folder: {e}")

            elif sub_action == "LIST":
                full_path = os.path.join(SERVER_PATH, sub_path)
                try:
                    if not os.path.exists(full_path):
                        response_messages.append("Folder not found.")
                    elif not os.path.isdir(full_path):
                        response_messages.append("Path is not a directory.")
                    else:
                        files_in_folder = os.listdir(full_path)
                        if not files_in_folder:
                            response_messages.append(f"Folder '{sub_path}' is empty.")
                        else:
                            response_messages.append(f"Files in '{sub_path}':")
                            response_messages.extend(files_in_folder) # Add each file/dir as a separate message or join.

                except OSError as e:
                    response_messages.append(f"Error listing folder: {e}")

            elif sub_action == "CHANGE":
                if sub_path == "..":
                    # Prevent going above the initial SERVER_PATH
                    if SERVER_PATH != SERVER_PATH:
                        SERVER_PATH = os.path.dirname(SERVER_PATH)
                        response_messages.append(f"Changed directory to: {os.path.basename(SERVER_PATH)}")
                    else:
                        response_messages.append("Already at the root directory.")
                else:
                    new_potential_path = os.path.join(SERVER_PATH, sub_path)
                    if os.path.isdir(new_potential_path):
                        SERVER_PATH = new_potential_path
                        response_messages.append(f"Changed directory to: {sub_path} (now {SERVER_PATH})")
                    else:
                        response_messages.append("Directory not found or is not a directory.")
            else:
               response_messages.append("Invalid subfolder action.")

            # Send all response messages and then EOF
            for msg in response_messages:
                conn.send(f"OK@{msg}\n".encode(FORMAT))
                sleep(0.01) # Small delay for client to catch up
            conn.send("EOF".encode(FORMAT)) # End of response for subfolder command
        
        elif cmd == "ANALYZE":
            send_data += "Analysis request received\n"
            conn.send(send_data.encode(FORMAT))
            
            if (os.path.isfile("connection_time.txt") == True):
                with open("connection_time.txt","r") as fo:
                    data = fo.read(SIZE)
                    if not data:
                        send_data = "Cannot analyze: File is empty. 1\n"
                        conn.send(send_data.encode(FORMAT))
                    else:
                        send_data = "Analyzing connection time...\n"
                        conn.send(send_data.encode(FORMAT))
            else:
                send_data = "Cannot analyze: File does not exist. 1\n"
                conn.send(send_data.encode(FORMAT))
            
            sleep(0.1)
            
            if (os.path.isfile("upload_time.txt") == True):
                with open("upload_time.txt","r") as fo:
                    data = fo.read(SIZE)
                    if not data:
                        send_data = "Cannot analyze: File is empty. 1\n"
                        conn.send(send_data.encode(FORMAT))
                        print("Cannot analyze: File is empty. 1\n")
                    else:
                        send_data = "Analyzing upload time...\n"
                        conn.send(send_data.encode(FORMAT))
                        print("Analyzing upload time...\n")
            else:
                send_data = "Cannot analyze: File does not exist. 1\n"
                conn.send(send_data.encode(FORMAT))
                print("Cannot analyze: File is empty. 1\n")
            
            sleep(0.1)
            
            if (os.path.isfile("up_rate.txt") == True):
                with open("up_rate.txt","r") as fo:
                    data = fo.read(SIZE)
                    if not data:
                        send_data = "Cannot analyze: File is empty. 1\n"
                        conn.send(send_data.encode(FORMAT))
                    else:
                        send_data = "Analyzing upload rate...\n"
                        conn.send(send_data.encode(FORMAT))
            else:
                send_data = "Cannot analyze: File does not exist. 1\n"
                conn.send(send_data.encode(FORMAT))
            
            sleep(0.1)
            
            if (os.path.isfile("dnload_time.txt") == True):
                with open("dnload_time.txt","r") as fo:
                    data = fo.read(SIZE)
                    if not data:
                        send_data = "Cannot analyze: File is empty. 1\n"
                        conn.send(send_data.encode(FORMAT))
                    else:
                        send_data = "Analyzing download time...\n"
                        conn.send(send_data.encode(FORMAT))
            else:
                send_data = "Cannot analyze: File does not exist. 1\n"
                conn.send(send_data.encode(FORMAT))
            
            sleep(0.1)
            
            if (os.path.isfile("dn_rate.txt") == True):
                with open("dn_rate.txt","r") as fo:
                    data = fo.read(SIZE)
                    if not data:
                        send_data = "Cannot analyze: File is empty. 1\n"
                        conn.send(send_data.encode(FORMAT))
                    else:
                        send_data = "Analyzing download rate...\n"
                        conn.send(send_data.encode(FORMAT))
            else:
                send_data = "Cannot analyze: File does not exist. 1\n"
                conn.send(send_data.encode(FORMAT))
            
            sleep(0.1)
            
            send_data = "OK@Analysis complete.\n"
            conn.send(send_data.encode(FORMAT))
            

        else:
            if "AN1" not in cmd:
                send_data = f"OK@There is no option for {cmd}.\nPlease try again or type TASK for help.\n"
                conn.send(send_data.encode(FORMAT))
            else:
                send_data += f"There is no option for {cmd[3:]}.\nPlease type ANALYZE to analyze performance data.\n"
                conn.send(send_data.encode(FORMAT))


    print(f"{addr} disconnected")
    conn.close()

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
        write_a_file("connection_time.txt", conn_time)

if __name__ == "__main__":
    main()
