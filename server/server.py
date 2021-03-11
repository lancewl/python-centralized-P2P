import os
import socket
import threading
import json

IP = socket.gethostbyname(socket.gethostname())
PORT = 4456
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_DATA_PATH = "./"

seed_table = {}
cond = threading.Condition()

def client_handler(conn, addr):
    global seed_table
    global cond
    full_addr = addr[0] + ":" + str(addr[1])

    print(f"[NEW CONNECTION] {addr} connected.")
    conn.send(json.dumps({"type": "INIT", "msg": "Welcome to indexing server!"}).encode(FORMAT))

    while True:
        data = conn.recv(SIZE).decode(FORMAT)
        json_data = json.loads(data)

        if json_data["action"] == "REGISTER":
            # register file list from seeds
            print(f"[REGISTER] {full_addr} registerd")
            cond.acquire()
            seed_table[full_addr] = json_data["filelist"]
            # print(seed_table)
            cond.release()
        
        elif json_data["action"] == "QUERY":
            # query for a file
            query_file = json_data["file"]
            print(f"[QUERY] {full_addr} query {query_file}")
            res = []
            cond.acquire()
            for seed, filelist in seed_table.items():
                if seed != full_addr and query_file in filelist:
                    res.append(seed)
            cond.release()
            conn.send(json.dumps({"type": "QUERY-RES", "msg": res}).encode(FORMAT))
        
        elif json_data["action"] == "LOGOUT":
            # delete record in seed_table when disconnect
            print(f"[UNREGISTER] {full_addr} unrigistered")
            cond.acquire()
            del seed_table[full_addr]
            cond.release()
            break

    conn.close()

def startIndexingServer():
    print("[STARTING] Server is starting")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] Server is listening on {IP}:{PORT}.")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=client_handler, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

if __name__ == "__main__":
    startIndexingServer()