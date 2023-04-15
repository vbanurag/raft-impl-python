import ast
from dataclasses import dataclass
from socket import *
import threading
from src.message_pass import *
from src.key_value_store import KeyValueStore
from src.config import server_nodes
from src.parsing import respond, address_of, with_return_address, broadcast
import time


@dataclass
class Server:
    name: str
    leader: bool
    port: int = 10000


    def __post_init__(self):
        self.key_value_store = KeyValueStore(server_name=self.name)
        self.key_value_store.catchup()
        self.term = self.key_value_store.get_latest_term()

    def send(self, message, to_server_address):
        print(f"connecting to {to_server_address[0]} port {to_server_address[1]}")

        peer_socket = socket(AF_INET, SOCK_STREAM)

        try:
            peer_socket.connect(to_server_address)
            encoded_message = message.encode('utf-8')

            try:
                print(f"sending {encoded_message} to {to_server_address}")
                send_message(peer_socket, encoded_message)
                time.sleep(0.5)
                peer_socket.close()
            except Exception as e:
                print(f"closing socket due to {str(e)}")
                peer_socket.close()
        except OSError as e:
            print("Bad file descriptor, supposedly: " + str(e))
        except ConnectionRefusedError as e:
            print(f"Ope, looks like {to_server_address[0]} port {to_server_address[1]} isn't up right now")


    def start(self):
        server_address = ('localhost', self.port)

        f = open("logs/server_registry.txt", "a")
        f.write(self.name + " localhost " + str(self.port) + '\n')
        f.close()

        print("starting up on " + str(server_address[0]) + " port " + str(server_address[1]))

        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server_socket.bind(server_address)
        self.server_socket.listen(1)

        while True:
            connection, client_address = self.server_socket.accept()
            print("connection from " + str(client_address))

            threading.Thread(target=self.manage_messaging, args=(connection, self.key_value_store)).start()

    def prove_aliveness(self):
        if self.leader:
            print("prove_aliveness happening")
            broadcast(self, with_return_address(self, "append_entries []"))

    def manage_messaging(self, connection, kvs):
        start = time.time()

        try:
            while True:
                operation = recv_messsage(connection)

                if operation:
                    destination, response = respond(self, kvs, operation)

                    if response == '':
                        break

                    if destination == "client":
                        send_message(connection, response.encode('utf-8'))
                    else:
                        self.send(response, to_server_address=address_of(destination))

                else:
                    print("no more data")
                    break

        finally:
            connection.close()
