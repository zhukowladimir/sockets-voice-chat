import argparse
from dataclasses import dataclass
import select
import socket
import threading
from typing import Optional
import sys
import os

# a crutch for import from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from message import *


@dataclass
class Connection:
    client: socket.socket
    addr: socket.AddressInfo
    thread: Optional[threading.Thread] = None
    name: Optional[str] = None

    keep_going: threading.Event = None
    keep_working: threading.Event = None
    

    def __post_init__(self):
        self.keep_working = threading.Event()
        self.keep_going = threading.Event()
        self.keep_working.set()
        self.keep_going.set()

    def _get_name(self) -> bool:
        msg = self.recv_msg()
        if msg is None:
            return False
        self.name = msg.name
        return True
    
    def _leave(self):
        print(f'Client {self.name} was left')
        self.client.shutdown(socket.SHUT_RDWR)
        self.keep_working.clear()
        # if self.thread:
        #     self.thread.join()

    def recv_msg(self) -> Optional[Message]:
        return receive_msg(self.client)


class Server:
    def __init__(self, port: int):
        self.ip = socket.gethostbyname(socket.gethostname())
        self.port = port

        self.broadcast_mutex: threading.Lock = threading.Lock()

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind((self.ip, self.port))
        except Exception as ex:
            print(f'EXCEPTION: INIT - {ex}')
            return
        
        self.connections: dict[str, Connection] = {}
        self.accept_connections()
    
    def delete_connection(self, connection: Connection):
        del self.connections[connection.name]
        connection._leave()

    def accept_connections(self):
        self.sock.listen(69)

        print(f'Running on IP: {self.ip}')
        print(f'Running on port: {self.port}')
        
        while True:
            connection = Connection(*self.sock.accept())
            flag = connection._get_name()
            while flag and connection.name in self.connections:
                connection.client.send(msg_serialization(NackMessage(text='Sorry, this nickname is already taken :(')))
                flag = connection._get_name()
            if not flag:
                continue

            connection.client.send(msg_serialization(AckMessage()))
            self.broadcast(connection, InfoMessage(text=f'{connection.name} joined!'))
            connection.thread = threading.Thread(target=self.handle_client, args=(connection, ))
            self.connections[connection.name] = connection
            connection.thread.start()

            print(self.connections)
        
    def broadcast(self, src: Connection, msg: Message):
        self.broadcast_mutex.acquire()

        for connection in [cnctn for name, cnctn in self.connections.items() if name != src.name and cnctn.client != self.sock]:
            try:
                connection.client.send(msg_serialization(msg))
            except socket.error as err:
                self.delete_connection(connection)
            except Exception as ex:
                print(f'EXCEPTION: BROADCAST - {ex}')
        
        self.broadcast_mutex.release()
            

    def handle_client(self, connection: Connection):
        while connection.keep_working.is_set():
            connection.keep_going.wait()
            try:
                msg = connection.recv_msg()
                if msg is None:
                    self.delete_connection(connection)
                    return
                self.broadcast(connection, msg)
            except Exception as ex:
                print(f'EXCEPTION: HANDLE - {ex}')
                self.delete_connection(connection)
                return


def createArgParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('port', nargs='?', default=8888)
    return parser

if __name__ == '__main__':
    args = createArgParser().parse_args()
    server = Server(args.port)
