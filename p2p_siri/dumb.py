import os
import socket

import logging
import threading
import pickle

from math import ceil

# Constants
PEERS_DIR = './Nodes/'
PEER_TIMEOUT = 2

# File Class
class File:
    chunk_size = 4096

    def __init__(self, name_of_file: str, landlord: str):
        self.name_of_file = name_of_file
        self.path = "./Nodes/" + landlord + "/" + name_of_file

# full_data_available Class
class full_data_available(File):
    def __init__(self, name_of_file: str, landlord: str):
        super().__init__(name_of_file, landlord)
        self.size = self.get_size(self.path)
        self.n_chunks = ceil(self.size / self.chunk_size)
        self.fp = open(self.path, 'rb')

    def fetch_chunck_number(self, chunk_number):
        return self.fetch_chunck(chunk_number * self.chunk_size)

    def fetch_chunck(self, offset):
        self.fp.seek(offset, 0)
        chunk = self.fp.read(self.chunk_size)
        return chunk

    @staticmethod
    def get_size(path):
        return os.path.getsize(path)

# full_data_available_not_available Class
class full_data_available_not_available(File):
    def __init__(self, name_of_file, landlord, size):
        super().__init__(name_of_file, landlord)
        self.size = size
        self.n_chunks = ceil(self.size / self.chunk_size)
        self.chuncks_req = [i for i in range(self.n_chunks)]
        self.received_chunks = {}
        self.fp = open(self.path, 'wb')

    def fetch_required(self):
        self.chuncks_req = []
        for i in range(self.n_chunks):
            if i not in self.received_chunks:
                self.chuncks_req.append(i)
        return self.chuncks_req

    def lodge_the_chunck(self, buf, chunk_number):
        self.received_chunks[chunk_number] = buf

    def lodge_the_file(self):
        if not self.fetch_required():
            with open(self.path, 'wb') as filep:
                for i in range(self.n_chunks):
                    filep.write(self.received_chunks[i])


class Peer:
    s: socket.socket
    peers: list
    peers_connections: dict
    port: int
    manager_port = 1233
    addr: tuple
    available_files: dict

    def __init__(self, port_no: int, name: str, ip_addr='127.0.0.1'):
        self.port = port_no
        self.name = name
        self.directory = PEERS_DIR + name + "/"

        if not os.path.isdir(self.directory):
            os.mkdir(self.directory)

        self.available_files = {}
        for f in os.listdir(self.directory):
            self.available_files[f] = full_data_available(f, self.name)

        self.s = socket.socket()

        self.addr = (ip_addr, port_no)
        self.peers_connections = {}
        self.my_socket = socket.socket()
        self.my_socket.bind((ip_addr, self.port))

    def make_connection_with_smart(self):
        self.s.connect(('localhost', self.manager_port))
        msg = self.s.recv(512).decode()
        if msg == 'Hi':
            self.s.send(pickle.dumps(self.addr))

    def receive(self):
        while True:
            try:
                msg = self.s.recv(512)

                msg = pickle.loads(msg)
                if msg != "Hey":
                    self.peers = msg['peers']
                    logging.info(f"available peers are {self.peers}")
                    print(f"********* Currently Connected Peers in the Network are {self.peers}  ********")
            except ConnectionAbortedError:
                print("********* Closing Connection with the Manager *********")
                break

    def update_peers(self):
        try:
            msg = b"find_peer_nodes"
            self.s.send(msg)
        except Exception:
            print("********* Sorry, I can't find the list of connected peers *********")

    def __del__(self):
        self.s.close()
        self.my_socket.close()

    def close_connection(self):
        self.s.send(b"close")
        self.s.close()
        self.my_socket.close()

    def inter_connect_with_peers_in_network(self):
        self.my_socket.listen(10)
        try:
            while True:
                c, addr = self.my_socket.accept()
                self.peers_connections[addr] = {"connection": c}
                listen_peers_thread = threading.Thread(target=self.hear_to_other_dumb_peer, args=(c, addr))
                listen_peers_thread.start()
        except OSError as e:
            print(e.errno)

    def hear_to_other_dumb_peer(self, c: socket.socket, addr):
        while True:
            try:
                msg = pickle.loads(c.recv(2048))

                if msg['type'] == 'request_file':
                    req_file_name = msg['data']
                    if req_file_name in self.available_files:
                        file_details = pickle.dumps({
                            "type": "available_file",
                            "data": {
                                "filesize": str(self.available_files[req_file_name].size)
                            }
                        })

                        c.send(file_details)

                if msg['type'] == 'request_chunk':
                    file_name = msg['data']['name_of_file']
                    chunk_number = msg['data']['chunk_number']
                    chunk = self.available_files[file_name].fetch_chunck_number(chunk_number)
                    ret_msg = pickle.dumps({
                        "type": "response_chunk",
                        "data": {
                            "chunk_number": chunk_number,
                            "name_of_file": file_name,
                            "chunk": chunk
                        }
                    })

                    c.send(ret_msg)
            except EOFError:
                pass

    def join_to_other_dumb_peer(self, addr):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect(addr)
            logging.info(f"Connected to Peer {addr}")
        except:
            print("********* Sorry!! I couldn't connect you to  ", addr)
        return sock

    def connect_and_fetch_file_details(self, addr, file_name, file_details: dict):
        c = self.join_to_other_dumb_peer(addr)
        msg = pickle.dumps({
            "type": "request_file",
            "data": file_name
        })
        c.send(msg)
        c.settimeout(PEER_TIMEOUT)
        try:
            msg = pickle.loads(c.recv(512))

            if msg['type'] == "available_file":
                file_details['size'] = msg['data']['filesize']
                file_details['peers_with_file'].append(addr)

        except socket.timeout:
            print("********* Sorry! No response from socket *********")

        c.close()

    def fetch_peers_possessing_files(self, file_name: str):
        running_thread = []
        file_details = {
            "size": None,
            "peers_with_file": []
        }
        for p in self.peers:
            if p != self.addr:
                get_details_thread = threading.Thread(target=self.connect_and_fetch_file_details,
                                                      args=(p, file_name, file_details))
                running_thread.append(get_details_thread)
                running_thread[-1].start()

        for threads in running_thread:
            threads.join()

        return file_details

    def fetch_specific_chuck_from_dumb(self, name_of_file, peer_addr, chunk_number, incomp_file: full_data_available_not_available):
        c = self.join_to_other_dumb_peer(peer_addr)
        msg = pickle.dumps({
            "type": "request_chunk",
            "data": {
                "name_of_file": name_of_file,
                "chunk_number": chunk_number
            }
        })
        c.send(msg)
        c.settimeout(PEER_TIMEOUT)
        try:
            msg = pickle.loads(c.recv(4096))

            if msg['type'] == "response_chunk":
                incomp_file.lodge_the_chunck(msg['data']['chunk'], chunk_number)

        except socket.timeout:
            print(f" Sorry!! The dumb peer {peer_addr} coulnot tranfer")

        logging.info(f"received the chunk {chunk_number}/{incomp_file.n_chunks} from {peer_addr}")
        print(f"(FYI) I am fetching the chunk {chunk_number} of{incomp_file.n_chunks} from the peer{peer_addr}")

        c.close()

    def download_file(self, name_of_file):
        file_details = self.fetch_peers_possessing_files(name_of_file)
        logging.info(f"{file_details}")
        if file_details['size'] is None:
            print("File not found")
            return
        receiving_file = full_data_available_not_available(name_of_file, self.name, int(file_details['size']))

        while receiving_file.fetch_required():
            self.update_peers()
            peers_with_file = self.fetch_peers_possessing_files(name_of_file)['peers_with_file']
            if not peers_with_file:
                print(f"there are no peers with file {name_of_file}")
                del receiving_file
                return

            chuncks_req = receiving_file.fetch_required()
            i = 0
            running_threads = []
            for peer in peers_with_file:
                if i < len(chuncks_req):
                    get_chunk_thread = threading.Thread(
                        target=self.fetch_specific_chuck_from_dumb,
                        args=(name_of_file, peer, chuncks_req[i], receiving_file)
                    )
                    running_threads.append(get_chunk_thread)
                    get_chunk_thread.start()
                    i += 1
                else:
                    break

            for thread in running_threads:
                thread.join()

        receiving_file.lodge_the_file()
        self.available_files[name_of_file] = full_data_available(name_of_file, self.name)
        print(f"received {name_of_file}")

# Function to start a peer
def initialize_dumb_peer(port_no, name):
    p = Peer(port_no, name)
    p.make_connection_with_smart()
    receive_thread = threading.Thread(target=p.receive)
    receive_thread.start()
    connect_peers_thread = threading.Thread(target=p.inter_connect_with_peers_in_network)
    connect_peers_thread.start()
    return p

if __name__ == "__main__":
    try:
        print("********** Welcome to the Network **********")
        print("In order to become a member of your Network Please enter Your Details")
        port_no = int(input("Please input your port number: "))
        name = input("Please input your name: ")
        logging.basicConfig(filename="temp/" + name + '.log', encoding='utf-8', level=logging.DEBUG)
        p = initialize_dumb_peer(port_no, name)
        connected = 1
        print(f"Hi Peer, your existing files are : {list(p.available_files.keys())}")
        print("Please choose an option to perform a function according to the menu list given below : ")
        print("Enter 0 to exit the network")
        print("Enter 1 to become a part of this Peer to Peer Network")
        print("Enter 2 to find the already present nodes in the network")
        print("Enter 3 to search for a file and get it from the peers in the network")
        print("Enter 4 to see the list of files that I have which can be shared to other users in the network")
        print("Enter 5 to exit the program\n\n")

        while True:
            inp = input(">")
            if inp == '0':
                if connected:
                    p.close_connection()
                    del p
                    connected = 0
                else:
                    print("You are not connceted to the network")

            if inp == '1':
                if not connected:
                    p = initialize_dumb_peer(port_no, name)
                    connected = 1
                else:
                    print("No need to connect as you are already in sync with the network")

            if inp == "find_peer_nodes" or inp == '2':
                update_peers_thread = threading.Thread(target=p.update_peers)
                update_peers_thread.start()
                update_peers_thread.join()
                print(f"The currently connected peers in the p2p network are: {p.peers}")

            if inp == "find_files" or inp == '3':
                file_name = input("Enter file name : ")
                p.download_file(file_name)

            if inp == 'my_available_files' or inp == '4':
                print(f"The files present at your end  are: {list(p.available_files.keys())}")

            if inp == 'end' or inp == '5':
                os._exit(0)
    except KeyboardInterrupt:
        os._exit(0)
