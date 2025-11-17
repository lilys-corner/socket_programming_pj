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
        # response from the server
        data = client.recv(SIZE).decode(FORMAT)
        cmd, msg = data.split("@")
        if cmd == "OK":
            print(f"{msg}")
        elif cmd == "DISCONNECTED":
            print(f"{msg}")
            break
        
        # send data to the server
        data = input("> ") 
        data = data.split(" ")
        cmd = data[0]

        if cmd == "TASK":
            client.send(cmd.encode(FORMAT))

        elif cmd == "LOGOUT":
            client.send(cmd.encode(FORMAT))
            break
      

        elif cmd == "UPLOAD":
            filename = input("Enter the filename to upload: ")
            client.send(cmd.encode(FORMAT))
            
            
            
            client.recv(SIZE).decode(FORMAT)  ## ready to receive

            client.send(filename.encode(FORMAT))

            client.recv(SIZE).decode(FORMAT)  ## file received

            with open(filename,"r") as fo:
                data = fo.read(SIZE)
                while data:
                    client.send(data.encode(FORMAT))
                    data = fo.read(SIZE)
            client.send("EOF".encode(FORMAT))  ## indicate end of file
            print(f"File {filename} uploaded to the server.")
            #all this ^ does something but idk how succesfully it actually works
            '''
            fi = open(filename,"r")
            data = fi.read()
            while data:
                client.send(data.encode(FORMAT))
                data = fi.read()
            fi.close()
            '''

        elif cmd == "DOWNLOAD":
            continue
        
        elif cmd == "DELETE":
            continue

        elif cmd == "DIR":
            continue

        elif cmd == "SUBFOLDER":
            continue


    print("Disconnected from the server.")
    client.close() ## close the connection

if __name__ == "__main__":
    main()
