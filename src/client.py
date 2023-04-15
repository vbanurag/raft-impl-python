import socket
from dataclasses import dataclass

from src.message_pass import *

@dataclass
class Client:
    server_port: int = 10000

    def start(self):
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the Socket to the port where the server is listeneing
        server_address = ('localhost', self.server_port)
        print(f"connecting to {server_address[0]} port {server_address[1]}")
        self.sock.connect(server_address)

        running = True
        while running:
            try:
                # send data
                msg = input("Please type your message: \n")
                print(f"Sending ... {msg}")
                send_message(self.sock, msg.encode("utf-8"))

                data = recv_messsage(self.sock)
                print(f"recieved data ... {data}")
            finally:
                print(f"Closing Socket")
                self.sock.close()
                running = False
