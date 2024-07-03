#Libraries Imported
import os
import socket
import time
import threading
import pickle

# Constants
CONNECTION_TEST_TIME_INTERVAL_IN_SECONDS = 1
SERVER_IP = ''
PORT = 1233

class PeerManager:
    def __init__(self):
        #creates a new socket object using IPV-AF_INET and TCP as the transport communication protocol-SOCK_STREAM. his socket will be used for listening to incoming connections from other peers.
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # binds the server socket to a specific IP address (SERVER_IP) and port number (PORT). This is the address and port where the server will listen for incoming connection requests from peer nodes.       
        self.server_socket.bind((SERVER_IP, PORT))
        # sets the server socket to the listening state, allowing it to accept incoming connection requests. The argument 10 specifies the maximum number of queued connections that can be waiting to be accepted. In this case, it allows up to 10 pending connections in the server's queue.
        self.server_socket.listen(10)
    #    his line initializes an empty dictionary called connections. This dictionary will be used to store information about connected peer nodes, including their socket objects and peer addresses.
        self.connections = {}
        # This attribute will later hold a reference to a thread that handles incoming connection requests from peers.
        self.accept_thread = None
        # This attribute will later hold a reference to a thread responsible for broadcasting information about available peers to connected peers.
        self.broadcast_thread = None

#closing a peer connection on user's request/termmination of thread
    def __del__(self):
        self.server_socket.close()

#Periodically check after the set interval if the socket connection still holds to be true
    def is_socket_closed(self, sock):
        try:
            obj = pickle.dumps('Hey')
            sock.send(obj)
        except socket.error:
            return True
        except BlockingIOError:
            return False
        except ConnectionResetError:
            return True
        except Exception as e:
            return True
        return False

    def accept_connections(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            client_socket.send(b'Hi')
            client_socket.settimeout(2)
            peer_address = pickle.loads(client_socket.recv(512))
            self.connections[addr] = (client_socket, peer_address)
            print(f"*********** Current Connections *********** {addr, peer_address}")
            recv_msg_thread = threading.Thread(target=self.receive_message, args=(client_socket, addr))
            recv_msg_thread.start()
            self.start_broadcast_thread()

    def receive_message(self, client_socket, addr):
        while True:
            client_socket.settimeout(10000)
            try:
                msg = client_socket.recv(512).decode()
                if msg == 'close':
                    print(f"*********** Closing the Connection ***********: {addr}")
                    self.connections.pop(addr)
                    self.start_broadcast_thread()
                    break
                if msg == 'get_peers':
                    peers_msg = pickle.dumps({
                        "type": "peers",
                        "peers": [x[1] for a, x in self.connections.items()]
                    })
                    client_socket.send(peers_msg)
            except Exception as e:
                print(f"*********** Problem from  {addr}: {e} ***********")
                break
#This method continuously monitors the status of connections in the peer-to-peer network by periodically checking for closed or problematic connections. 
# If any issues are detected, it removes the problematic connections and initiates the broadcasting of updated peer information to ensure that all peers 
# in the network are aware of the current state of connections. This helps maintain the health and reliability of the network.


    def periodic_connection_test(self):
        while True:
            closed_connections = [addr for addr, (sock, _) in self.connections.items() if self.is_socket_closed(sock)]
            for addr in closed_connections:
                self.connections.pop(addr)
            if closed_connections:
                self.start_broadcast_thread()
            time.sleep(CONNECTION_TEST_TIME_INTERVAL_IN_SECONDS)


#initiate the broadcasting of peer information to all connected peers by launching a separate thread to handle this task. By doing so, the program can continue its other operations while the broadcasting thread runs in the background, ensuring efficient and non-blocking communication in the peer-to-peer network.
    def start_broadcast_thread(self):
        self.broadcast_thread = threading.Thread(target=self.broadcast_peers)
        self.broadcast_thread.start()


#ending a list of connected peers to all the currently connected peer nodes in the peer-to-peer network
    def broadcast_peers(self):
        peers_msg = pickle.dumps({
            "type": "peers",
            "peers": [x[1] for a, x in self.connections.items()]
        })
        for addr, (client_socket, _) in self.connections.items():
            client_socket.send(peers_msg)


#  the run(self) method sets up and starts two threads: one for accepting incoming connections and another for periodically testing and maintaining the status of existing connections.
    def run(self):
        self.accept_thread = threading.Thread(target=self.accept_connections)
        self.accept_thread.start()
        periodic_conn_test_thread = threading.Thread(target=self.periodic_connection_test)
        periodic_conn_test_thread.start()



# creates an instance of the PeerManager class
# The run() method is responsible for starting the server, accepting connections, and managing the network.
#allows the user to exit the program by typing 'c' or 'close'. It also handles the case where the user interrupts the program with Ctrl+C.
if __name__ == "__main__":
    try:
        manager = PeerManager()
        manager.run()
        print("*********** Welcome to the Peer to Peer Network ***********")
        print("No current connectionns avaiable. Setup the network. Only the smart node exists as of now")
        user_input = input()
        if user_input == 'c' or user_input == 'close':
            os._exit(0)
    except KeyboardInterrupt:
        os._exit(0)
