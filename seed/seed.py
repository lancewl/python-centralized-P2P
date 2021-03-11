import os
import socket
import json

IP = socket.gethostbyname(socket.gethostname())
PORT = 4456
ADDR = (IP, PORT)
FORMAT = "utf-8"
SIZE = 1024

def connectIndexingServer():
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect(ADDR)

    files = os.listdir("./")
    register_data = {
        "action": "REGISTER",
        "filelist": files
    }
    register_json = json.dumps(register_data)
    conn.send(register_json.encode(FORMAT))

    while True:
        data = conn.recv(SIZE).decode(FORMAT)
        json_data = json.loads(data)

        if json_data["type"] == "INIT":
            print(json_data["msg"])
        
        elif json_data["type"] == "QUERY-RES":
            print(json_data["msg"])

        user_input = input("> ")
        user_input = user_input.split(" ")
        action = user_input[0]

        if action == "QUERY":
            conn.send(json.dumps({"action": "QUERY", "file": user_input[1]}).encode(FORMAT))
        elif action == "LOGOUT":
            conn.send(json.dumps({"action": "LOGOUT"}).encode(FORMAT))
            break

    print("Disconnected from the server.")
    conn.close()

if __name__ == "__main__":
    connectIndexingServer()