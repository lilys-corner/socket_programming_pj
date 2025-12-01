#!/usr/bin/env python3
# -*- coding: utf-8 -*-

## Create the server side of the application
import signal
# import libraries
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

    # dictionary to map files with their original names and their server-stored paths
    uploaded = {}
    current_client_dir = SERVER_PATH # Initialize current directory for this client thread

    while True:
        try:
            data =  conn.recv(SIZE).decode(FORMAT)
            if not data: # Client disconnected
                print(f"{addr} disconnected unexpectedly.")
                break

            data_parts = data.split("@")
            cmd = data_parts[0]

            send_response_prefix = "OK@"

            if cmd == "LOGOUT":
                break

            elif cmd == "TASK":
                send_data = send_response_prefix
                send_data += "LOGOUT from the server.\n"
                send_data += "UPLOAD a file to the server.\n"
                send_data += "DOWNLOAD a file from the server.\n"
                send_data += "DELETE a file from the server.\n"
                send_data += "DIR to list files in current directory.\n"
                send_data += "SUBFOLDER to manage subfolders (CREATE, DELETE, LIST, CHANGE).\n"
                send_data += "ANALYZE to get performance data.\n"

                conn.send(send_data.encode(FORMAT))

            elif cmd == "UPLOAD":
                conn.send(f"{send_response_prefix}Ready to receive the file.\n".encode(FORMAT))

                filename = conn.recv(SIZE).decode(FORMAT).strip()
                filesize = conn.recv(SIZE).decode(FORMAT).strip()

                conn.send(f"{send_response_prefix}File size received {filesize} bytes.\n".encode(FORMAT))

                # checks if the file has already been uploaded
                if (filename in uploaded):
                    # if it's been uploaded, send a 1 to client to let it know
                    conn.send(f"{send_response_prefix}File received successfully. 1\n".encode(FORMAT))

                    # receive if user wants to overwrite it (Y/N)
                    ans = conn.recv(SIZE).decode(FORMAT)

                    # if user wants to overwrite, upload file again
                    if (ans == "Y"):
                        t1 = time()
                        # receive data, copy it
                        new_filename = uploaded[filename] # full path is stored here
                        received_data = 0
                        with open(new_filename, "wb") as fo:
                            while received_data < int(filesize):
                                data_chunk = conn.recv(SIZE)
                                if not data_chunk:
                                    break
                                fo.write(data_chunk)
                                received_data += len(data_chunk)
                            fo.close()

                        t2 = time()
                        upload_time = t2 - t1
                        write_a_file("upload_time.txt", upload_time)

                        up_rate = ((float(filesize) / 1024) / 1024) * upload_time
                        write_a_file("up_rate.txt", up_rate)

                        # tell yourself that you got it w/ location
                        print(f"File {filename} received from {addr} (overwritten)")

                        # send final confirmation
                        conn.send(f"{send_response_prefix}File {filename} overwritten.\n".encode(FORMAT))

                    # if user doesn't want to overwrite, end
                    else:
                        conn.send(f"{send_response_prefix}File {filename} not overwritten.\n".encode(FORMAT))

                # if file not already uploaded, upload the filee
                else:
                    t1 = time()
                    # send confirmation, client_1 receives it
                    conn.send(f"{send_response_prefix}File received successfully.\n".encode(FORMAT))

                    # receive data, copy it
                    file_type = filename[-4:]
                    global TCOUNTER, ACOUNTER, VCOUNTER # Access global counters
                    new_filename_base = ""
                    if (file_type == ".txt"):
                        new_filename_base = f"TS{TCOUNTER:03d}"
                        TCOUNTER += 1
                    elif (file_type == ".mp3"):
                        new_filename_base = f"AS{ACOUNTER:03d}"
                        ACOUNTER += 1
                    else:
                        new_filename_base = f"VS{VCOUNTER:03d}"
                        VCOUNTER += 1

                    new_filename = os.path.join(SERVER_PATH, new_filename_base)

                    received_data = 0
                    with open(new_filename, "wb") as fo:
                        while received_data < int(filesize):
                            data_chunk = conn.recv(SIZE)
                            if not data_chunk:
                                break
                            fo.write(data_chunk)
                            received_data += len(data_chunk)
                        fo.close()

                    t2 = time()
                    upload_time = t2 - t1
                    write_a_file("upload_time.txt", upload_time)

                    up_rate = ((float(filesize) / 1024) / 1024) * upload_time
                    write_a_file("up_rate.txt", up_rate)

                    # add uploaded file to the uploaded list so we know we have it
                    uploaded[filename] = new_filename # Store original name to server full path mapping

                    # tell yourself that you got it w/ location
                    print(f"File {filename} received from {addr} as {new_filename}")

                    # send final confirmation
                    conn.send(f"{send_response_prefix}File {filename} uploaded as {new_filename} successfully.\n".encode(FORMAT))

            elif cmd == "DOWNLOAD":
                conn.send(f"{send_response_prefix}Ready to receive the filename for download.\n".encode(FORMAT))

                filename_to_download = conn.recv(SIZE).decode(FORMAT).strip()

                if filename_to_download in uploaded:
                    server_full_path = uploaded[filename_to_download] # This is the full path on the server

                    if not os.path.exists(server_full_path):
                        # File was once uploaded but now physically missing. Signal '1' to client.
                        conn.send(f"ERROR@Server file {filename_to_download} not found. 1\n".encode(FORMAT))
                        continue # Continue to next command from client

                    # File found and exists. Send a message without '1'.
                    conn.send(f"{send_response_prefix}Sending file {filename_to_download}.\n".encode(FORMAT))
                    sleep(0.1) # Small delay to ensure client receives this before size

                    filesize = os.path.getsize(server_full_path) # STORES FILE SIZE
                    conn.send(str(filesize).encode(FORMAT)) # Send file size
                    sleep(0.1) # Small delay

                    # For client's `new_filename = client.recv(SIZE).decode(FORMAT)`
                    conn.send(f"downloaded_{filename_to_download}".encode(FORMAT)) # Send a suggested save name to client

                    t1 = time()
                    with open(server_full_path,"rb") as fo:
                        while True:
                            data_chunk = fo.read(SIZE)
                            if not data_chunk:
                                break
                            conn.sendall(data_chunk)
                        fo.close()

                    t2 = time()
                    dnload_time = t2 - t1
                    write_a_file("dnload_time.txt", dnload_time)

                    dn_rate = ((float(filesize) / 1024) / 1024) * dnload_time
                    write_a_file("dn_rate.txt", dn_rate)

                    sleep(0.1)

                    print(f"Sent {server_full_path} to {addr}.")

                    conn.send(f"{send_response_prefix}File {filename_to_download} has been sent.\n".encode(FORMAT))

                else:
                    # File not in uploaded list. Client must get '1' in response.
                    conn.send(f"ERROR@File {filename_to_download} is unable to be downloaded: it has not been uploaded. 1\n".encode(FORMAT))

            elif cmd == "DELETE":
                conn.send(f"{send_response_prefix}Ready to receive filename for deletion.\n".encode(FORMAT))

                filename_to_delete = conn.recv(SIZE).decode(FORMAT).strip()

                if filename_to_delete in uploaded:
                    server_full_path = uploaded[filename_to_delete] # This is the full path on the server
                    if os.path.exists(server_full_path):
                        os.remove(server_full_path)
                        del uploaded[filename_to_delete]
                        conn.send(f"{send_response_prefix}File {filename_to_delete} successfully deleted.\n".encode(FORMAT))
                    else:
                        conn.send(f"{send_response_prefix}Server file not found for {filename_to_delete} (entry exists but file is gone).\n".encode(FORMAT))
                else:
                    conn.send(f"{send_response_prefix}File {filename_to_delete} unable to be deleted: not found in uploaded list.\n".encode(FORMAT))

            elif cmd == "DIR":
                conn.send(f"{send_response_prefix}Directory listing requested.\n".encode(FORMAT)) # Server sends ready signal

                try:
                    files_and_dirs = os.listdir(current_client_dir)
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
                conn.send(f"{send_response_prefix}Ready for subfolder action.\n".encode(FORMAT)) # Server sends ready signal

                client_sub_action_data = conn.recv(SIZE).decode(FORMAT)
                sub_action_parts = client_sub_action_data.split("@")
                sub_action = sub_action_parts[0]
                sub_path = sub_action_parts[1] if len(sub_action_parts) > 1 else ""

                response_messages = []

                if sub_action == "CREATE":
                    full_path = os.path.join(current_client_dir, sub_path)
                    try:
                        if os.path.exists(full_path):
                            response_messages.append("Folder already exists!")
                        else:
                            os.makedirs(full_path)
                            response_messages.append("Folder created successfully.")
                    except OSError as e:
                        response_messages.append(f"Error creating folder: {e}")

                elif sub_action == "DELETE":
                    full_path = os.path.join(current_client_dir, sub_path)
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
                    full_path = os.path.join(current_client_dir, sub_path)
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
                        if current_client_dir != SERVER_PATH:
                            current_client_dir = os.path.dirname(current_client_dir)
                            response_messages.append(f"Changed directory to: {os.path.basename(current_client_dir)}")
                        else:
                            response_messages.append("Already at the root directory.")
                    else:
                        new_potential_path = os.path.join(current_client_dir, sub_path)
                        if os.path.isdir(new_potential_path):
                            current_client_dir = new_potential_path
                            response_messages.append(f"Changed directory to: {sub_path} (now {current_client_dir})")
                        else:
                            response_messages.append("Directory not found or is not a directory.")
                else:
                    response_messages.append("Invalid subfolder action.")

                # Send all response messages and then EOF
                for msg in response_messages:
                    conn.send(f"{send_response_prefix}{msg}\n".encode(FORMAT))
                    sleep(0.01) # Small delay for client to catch up
                conn.send("EOF".encode(FORMAT)) # End of response for subfolder command

            elif cmd == "ANALYZE":
                conn.send(f"{send_response_prefix}Analysis request received\n".encode(FORMAT))
                sleep(0.1) # Small delay

                analysis_files = ["connection_time.txt", "upload_time.txt", "up_rate.txt", "dnload_time.txt", "dn_rate.txt"]
                for af in analysis_files:
                    if os.path.isfile(af):
                        with open(af,"r") as fo:
                            data_content = fo.read().strip()
                            if not data_content:
                                conn.send(f"{send_response_prefix}Cannot analyze {af}: File is empty. 1\n".encode(FORMAT))
                            else:
                                conn.send(f"{send_response_prefix}Analyzing {af}: {data_content}\n".encode(FORMAT))
                    else:
                        conn.send(f"{send_response_prefix}Cannot analyze {af}: File does not exist. 1\n".encode(FORMAT))
                    sleep(0.1) # Small delay

                conn.send(f"{send_response_prefix}Analysis complete.\n".encode(FORMAT))

            else:
                conn.send(f"{send_response_prefix}There is no option for {cmd}.\nPlease try again or type TASK for help.\n".encode(FORMAT))

        except Exception as e:
            print(f"Error handling client {addr}: {e}")
            conn.send(f"ERROR@Server error: {e}\n".encode(FORMAT))
            break # Exit loop on error

    print(f"{addr} disconnected")
    conn.close()

def main():
    print("Starting the server")
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM) ## used IPV4 and TCP connection
    server.bind(ADDR) # bind the address
    server.listen() ## start listening
    print(f"server is listening on {IP}: {PORT}")

    # Ensure SERVER_PATH exists
    os.makedirs(SERVER_PATH, exist_ok=True)

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
