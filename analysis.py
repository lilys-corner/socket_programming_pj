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

analysis_dict = {}

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
        
        if cmd == "ANALYZE":
            client.send(cmd.encode(FORMAT))
            
            client.recv(SIZE).decode(FORMAT) # receive "analysis req received"
            
            if ("1" not in client.recv(SIZE).decode(FORMAT)):
                # download connection time to dictionary
                with open("connection_time.txt","r") as fo:
                    data = fo.read(SIZE)
                    analysis_dict["conn_"] = data
                    fo.close()
                print("Connection time: " + analysis_dict["conn_"] + " seconds")
            else:
                analysis_dict["conn_"] = ""
                print("Cannot analyze: nothing has connected to the server yet.")
            
            if ("1" not in client.recv(SIZE).decode(FORMAT)):
                # download upload time to the dictionary
                with open("upload_time.txt", "r") as fo:
                    data = fo.read(SIZE)
                    analysis_dict["up_"] = data
                    fo.close()
                print("Upload time: " + analysis_dict["up_"] + " seconds")
            else:
                analysis_dict["up_"] = ""
                print("Cannot analyze: nothing has been uploaded yet, or the last file uploaded is empty.")
                
            if ("1" not in client.recv(SIZE).decode(FORMAT)):
                # download upload time to the dictionary
                with open("up_rate.txt", "r") as fo:
                    data = fo.read(SIZE)
                    analysis_dict["up_r"] = data
                    fo.close()
                print("Upload rate: " + analysis_dict["up_r"] + " MB per second")
            else:
                analysis_dict["up_r"] = ""
                print("Cannot analyze: nothing has been uploaded yet, or the last file uploaded is empty.")
            
            if ("1" not in client.recv(SIZE).decode(FORMAT)):
                # download upload time to the dictionary
                with open("dnload_time.txt", "r") as fo:
                    data = fo.read(SIZE)
                    analysis_dict["down_"] = data
                    fo.close()
                print("Download time: " + analysis_dict["down_"] + " seconds")
            else:
                analysis_dict["down_"] = ""
                print("Cannot analyze: nothing has been downloaded yet, or the last file downloaded is empty.")
            
            if ("1" not in client.recv(SIZE).decode(FORMAT)):
                # download upload time to the dictionary
                with open("dn_rate.txt", "r") as fo:
                    data = fo.read(SIZE)
                    analysis_dict["down_r"] = data
                    fo.close()
                print("Download rate: " + analysis_dict["down_r"] + " MB per second")
            else:
                analysis_dict["down_r"] = ""
                print("Cannot analyze: nothing has been downloaded yet, or the last file downloaded is empty.")
            
            with open("analysis_data.txt", "w") as fo:
                    if (analysis_dict["conn_"]):
                        fo.write("Connection time: " + analysis_dict["conn_"] + " seconds\n")
                    if (analysis_dict["up_"]):
                        fo.write("Upload time: " + analysis_dict["up_"] + " seconds\n")
                    if (analysis_dict["up_r"]):
                        fo.write("Upload rate: " + analysis_dict["up_r"] + " MB per second\n")
                    if (analysis_dict["down_"]):
                        fo.write("Download time: " + analysis_dict["down_"] + " seconds\n")
                    if (analysis_dict["down_r"]):
                        fo.write("Download rate: " + analysis_dict["down_r"] + " MB per second\n")
                    fo.close()

        else:
            cmd = "AN1" + cmd
            client.send(cmd.encode(FORMAT))
            



    print("Disconnected from the server.")
    client.close() ## close the connection

if __name__ == "__main__":
    main()
