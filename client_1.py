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
            client.send(cmd.encode(FORMAT))
            # send to server that cmd is UPLOAD so it chooses UPLOAD of its functions 
            
            client.recv(SIZE).decode(FORMAT)
            # receive "ready to receive" to continue
            
            filename = input("Enter the filename to upload: ")
            client.send(filename.encode(FORMAT))
            # send filename to be saved in the server 

            client.recv(SIZE).decode(FORMAT)
            # receive "file received" to continue

            with open(filename,"r") as fo:
                data = fo.read(SIZE)
                while data:
                    client.send(data.encode(FORMAT))
                    data = fo.read(SIZE)
            client.send("EOF".encode(FORMAT))
            # EOF indicates end of file
            fo.close()
        
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
      


    print("Disconnected from the server.")
    client.close() ## close the connection

# DO MAIN 

if __name__ == "__main__":
    main()
