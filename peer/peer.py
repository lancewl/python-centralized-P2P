import os
import sys
import socket
import threading
import json
import click

FORMAT = "utf-8"
SIZE = 1024

def downloadFile(addr, filename):
    # Download file from other peer
    downloader = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    downloader.connect(addr)

    downloader.send(json.dumps({"file": filename}).encode(FORMAT))

    l = downloader.recv(1024)

    f = open(filename,'wb') #open in binary
    while (l):
            f.write(l)
            l = downloader.recv(1024)
    f.close()
    downloader.close()

def uploadHandler(conn, addr):
    full_addr = addr[0] + ":" + str(addr[1])

    data = conn.recv(SIZE).decode(FORMAT)
    json_data = json.loads(data)
    filename = json_data["file"]

    print(f"[UPLOADING] {full_addr} is downloading {filename}")

    f = open (filename, "rb")
    l = f.read(SIZE)
    while (l):
        conn.send(l)
        l = f.read(SIZE)
    conn.close()

def peerServer(peer_server_addr):
    print("[STARTING] Peer Server is starting")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(peer_server_addr)
    server.listen()
    print(f"[LISTENING] Peer Server is listening on {peer_server_addr[0]}:{str(peer_server_addr[1])}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=uploadHandler, args=(conn, addr))
        thread.start()

def connectIndexingServer(client_bind_addr, server_addr):
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.bind(client_bind_addr)
    conn.connect(server_addr)

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

            if json_data["type"] == "OK":
                print(json_data["msg"])
            
            elif json_data["type"] == "QUERY-RES":
                query_file = json_data["file"]
                if len(json_data["msg"]) > 0:
                    for peer in json_data["msg"]:
                        print(peer)
                    print("Choose a peer to download:")
                    user_input = input("> ")
                    user_input = user_input.split(":")
                    download_addr = (user_input[0], int(user_input[1])+1)
                    
                    downloadFile(download_addr, query_file)
                else:
                    print("No peers found for the file.")

        user_input = input("> ")
        user_input = user_input.split(" ")
        action = user_input[0]
        isvalid = True

        if action == "QUERY" and len(user_input) > 1:
            conn.send(json.dumps({"action": "QUERY", "file": user_input[1]}).encode(FORMAT))
        elif action == "EXIT":
            break
        else:
            print("Input action is invalid!")
            isvalid = False

    print("Disconnected from the server.")
    conn.close()

@click.command()
@click.argument('port')
@click.option('--dir',
              default="./",
              help='Serving directory relative to current directory')
@click.option('--server',
              default="127.0.0.1:5000",
              help='Indexing server address')
def main(port, dir, server):
    target_dir = os.path.join(os.path.dirname(__file__), dir)
    os.chdir(target_dir)

    port = int(port)
    localhost = socket.gethostbyname(socket.gethostname())
    peer_server_addr = (localhost, port + 1)
    client_bind_addr = (localhost, port)
    server_addr = server.split(":")
    server_addr = (server_addr[0], int(server_addr[1]))
    thread = threading.Thread(target=peerServer, args=(peer_server_addr,))
    thread.daemon = True
    thread.start()
    connectIndexingServer(client_bind_addr, server_addr)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)