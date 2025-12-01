# Author : Ayesha S. Dina

import os
import socket


# IP = "192.168.1.101" #"localhost"
IP = "localhost"
PORT = 4450
ADDR = (IP,PORT)
SIZE = 1024 ## byte .. buffer size
FORMAT = "utf-8"
SERVER_DATA_PATH = "server_data"

def main():
    
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect(ADDR)
    while True:  ### multiple communications
        data = client.recv(SIZE).decode(FORMAT)
        cmd, msg = data.split("@")
        if cmd == "OK":
            print(f"{msg}")
        elif cmd == "DISCONNECTED":
            print(f"{msg}")
            break
        
        data = input("> ") 
        data = data.split(" ")
        cmd = data[0]

        if cmd == "TASK":
            client.send(cmd.encode(FORMAT))

        elif cmd == "LOGOUT":
            client.send(cmd.encode(FORMAT))
            break
        
        elif cmd == "UPLOAD":
            # send to server that cmd is UPLOAD so it chooses UPLOAD of its functions 
            client.send(cmd.encode(FORMAT))
            
            # receive "ready to receive" to continue
            client.recv(SIZE).decode(FORMAT)
            
            # send filename to be saved in the server 
            filename = input("Enter the filename to upload: ")
            client.send(filename.encode(FORMAT))
            

            fsize = os.path.getsize(filename) # STORES FILE SIZE
            client.send(str(fsize).encode(FORMAT))
            
            client.recv(SIZE).decode(FORMAT) # size confirm

            # receive "file received" or "file received 1" to see if it's already uploaded
            rec = client.recv(SIZE).decode(FORMAT)

            # if file is already uploaded
            if ("1" in rec):
                # ask if user wants to overwrite it, send it to server
                ans = input(f"File {filename} already exists. Would you like to overwrite it? (Y/N)\n> ")
                client.send(ans.encode(FORMAT))
                
                # if their answer was Y, send file contents
                if (ans == "Y"):
                    with open(filename,"rb") as fo:
                        while True:
                            data = fo.read(SIZE)
                            if not data:
                                client.send(data)
                                break
                            client.sendall(data)
                        fo.close()
                
                # if their answer was N, do nothing
            
            # if file is not already uploaded, send file contents
            else:
                with open(filename,"rb") as fo:
                    while True:
                        data = fo.read(SIZE)
                        if not data:
                            client.send(data)
                            break
                        client.sendall(data)
                    fo.close()
    
    # TO DO
        elif cmd == "DOWNLOAD":
            # send to server that cmd is DOWNLOAD so it chooses DOWNLOAD of its functions 
            client.send(cmd.encode(FORMAT))
            
            # receive "ready to send" to continue
            client.recv(SIZE).decode(FORMAT)
            
            # send filename to be sent from the server
            filename = input("Enter the filename to download: ")
            client.send(filename.encode(FORMAT))
            
            if ("1" not in client.recv(SIZE).decode(FORMAT)):
                fsize = client.recv(SIZE).decode(FORMAT).strip() # STORES FILE SIZE
                
                new_filename = client.recv(SIZE).decode(FORMAT)
                
                received_data = 0
                with open(new_filename, "wb") as fo: # problem
                    while received_data < int(fsize):
                        data = client.recv(SIZE)
                        if not data:
                            break
                        fo.write(data)
                        received_data += len(data)
                    fo.close()
        
        elif cmd == "DELETE":
            # send to server that cmd is DELETE so it chooses DELETE of its functions 
            client.send(cmd.encode(FORMAT))
            
            # receive "ready to receive" to continue
            client.recv(SIZE).decode(FORMAT)
            
            # ask user what to delete
            filename = input("Enter the filename to delete: ")
            client.send(filename.encode(FORMAT))
        
        elif cmd == "DIR":
            client.send(cmd.encode(FORMAT))
            print("\n--- DIRECTORY LISTING ---")

            while True:
                chunk = client.recv(SIZE).decode(FORMAT)

                if chunk == "EOF":
                    break

                print(chunk)

            print("--- END OF LISTING ---\n")
        
        elif cmd == "SUBFOLDER":
            client.send(cmd.encode(FORMAT))
            client.recv(SIZE).decode(FORMAT)

            print("\nChoose action:")
            print("1) CREATE folder")
            print("2) DELETE folder")
            print("3) LIST folder")
            print("4) CHANGE directory\n")

            action = input("Enter option number: ")

            if action == "1":
                path = input("Enter directory name to create: ")
                client.send(f"CREATE@{path}".encode(FORMAT))

            elif action == "2":
                path = input("Enter directory name to delete: ")
                client.send(f"DELETE@{path}".encode(FORMAT))

            elif action == "3":
                path = input("Enter directory to list: ")
                client.send(f"LIST@{path}".encode(FORMAT))

            elif action == "4":
                path = input("Enter new working directory: ")
                client.send(f"CHANGE@{path}".encode(FORMAT))

            else:
                client.send("INVALID".encode(FORMAT))

            # receive full feedback or directory listing
            while True:
                resp = client.recv(SIZE).decode(FORMAT)
                if resp == "EOF":
                    break
                print(resp)
        
        else:
            client.send(cmd.encode(FORMAT))
      


    print("Disconnected from the server.")
    client.close() ## close the connection

if __name__ == "__main__":
    main()
