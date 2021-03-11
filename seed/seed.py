import os
import socket
import threading
import json

IP = socket.gethostbyname(socket.gethostname())
PORT = 5000
ADDR = (IP, PORT)
FORMAT = "utf-8"
SIZE = 1024

def downloadHandler(conn, addr):
    full_addr = addr[0] + ":" + str(addr[1])

    data = conn.recv(SIZE).decode(FORMAT)
    json_data = json.loads(data)
    filename = json_data["file"]

    print(f"[UPLOADING] {full_addr} is downloading {filename}.")

    f = open (filename, "rb")
    l = f.read(SIZE)
    while (l):
        conn.send(l)
        l = f.read(SIZE)
    conn.close()

def seedServer():
    print("[STARTING] Seed Server is starting")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP, 50004))
    server.listen()
    print(f"[LISTENING] Seed Server is listening on {IP}:{50001}.")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=downloadHandler, args=(conn, addr))
        thread.start()

def connectIndexingServer():
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.bind((IP, 50003))
    conn.connect(ADDR)

    files = os.listdir("./")
    register_data = {
        "action": "REGISTER",
        "filelist": files
    }
    register_json = json.dumps(register_data)
    conn.send(register_json.encode(FORMAT))

    isvalid = True

    while True:
        if isvalid:
            data = conn.recv(SIZE).decode(FORMAT)
            json_data = json.loads(data)

            if json_data["type"] == "INIT":
                print(json_data["msg"])
            
            elif json_data["type"] == "QUERY-RES":
                query_file = json_data["file"]
                if len(json_data["msg"]) > 0:
                    for seed in json_data["msg"]:
                        print(seed)
                    print("Choose a seed to download:")
                    user_input = input("> ")
                    user_input = user_input.split(":")
                    download_addr = (user_input[0], int(user_input[1])+1)
                    
                    downloader = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    downloader.connect(download_addr)

                    downloader.send(json.dumps({"file": query_file}).encode(FORMAT))

                    l = downloader.recv(1024)

                    f = open(query_file,'wb') #open in binary
                    while (l):
                            f.write(l)
                            l = downloader.recv(1024)
                    f.close()
                    downloader.close()
                else:
                    print("No seeds found for the file.")

        user_input = input("> ")
        user_input = user_input.split(" ")
        action = user_input[0]
        isvalid = True

        if action == "QUERY" and len(user_input) > 1:
            conn.send(json.dumps({"action": "QUERY", "file": user_input[1]}).encode(FORMAT))
        elif action == "LOGOUT":
            conn.send(json.dumps({"action": "LOGOUT"}).encode(FORMAT))
            break
        else:
            print("Input action is invalid!")
            isvalid = False

    print("Disconnected from the server.")
    conn.close()

if __name__ == "__main__":
    thread = threading.Thread(target=seedServer)
    thread.start()
    connectIndexingServer()