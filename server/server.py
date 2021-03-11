import os
import sys
import socket
import threading
import json

IP = socket.gethostbyname(socket.gethostname())
PORT = 5000
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_DATA_PATH = "./"

peer_table = {}
cond = threading.Condition()

def clientHandler(conn, addr):
    global peer_table
    global cond
    full_addr = addr[0] + ":" + str(addr[1])

    print(f"[NEW CONNECTION] {addr} connected.")
    conn.send(json.dumps({"type": "OK", "msg": "Welcome to indexing server!"}).encode(FORMAT))

    while True:
        data = conn.recv(SIZE).decode(FORMAT)

        if not data:
            # delete record in peer_table when data = None, client has disconnected
            print(f"[UNREGISTER] {full_addr} unrigistered")
            cond.acquire()
            del peer_table[full_addr]
            cond.release()
            break

        json_data = json.loads(data)

        if json_data["action"] == "REGISTER":
            # register file list from peers
            print(f"[REGISTER] {full_addr} registerd")
            cond.acquire()
            peer_table[full_addr] = json_data["filelist"]
            # print(peer_table)
            cond.release()
        
        elif json_data["action"] == "QUERY":
            # query for a file
            query_file = json_data["file"]
            print(f"[QUERY] {full_addr} query {query_file}")
            res = []
            cond.acquire()
            for peer, filelist in peer_table.items():
                if peer != full_addr and query_file in filelist:
                    res.append(peer)
            cond.release()
            conn.send(json.dumps({"type": "QUERY-RES", "msg": res, "file": query_file}).encode(FORMAT))

    conn.close()

def startIndexingServer():
    print("[STARTING] Indexing Server is starting")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] Indexing Server is listening on {IP}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=clientHandler, args=(conn, addr))
        thread.daemon = True
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

if __name__ == "__main__":
    try:
        startIndexingServer()
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Indexing server is down")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)