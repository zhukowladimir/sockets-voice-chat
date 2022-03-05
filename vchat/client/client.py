import argparse
import socket
import threading
import pyaudio
import sys
import os

# a crutch for import from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from message import *


class Client:
    def __init__(self, ip: str, port: int):
        self.sock : socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server : tuple[str, int] = (ip, port)
        self.keep_working : threading.Event = threading.Event()
        self.keep_going :threading.Event = threading.Event()

        self.connected = False
        self.buffer_size = 4096

        try:
            self.connect_to_server()
        except Exception as ex:
            print(f'EXCEPTION: INIT - {ex}')
            return

        self.keep_working.set()
        self.keep_going.set()

        self.chunk_size = 512
        audio_format = pyaudio.paInt16
        channels = 1
        rate = 20000

        self.p = pyaudio.PyAudio()
        self.playing_stream = self.p.open(format=audio_format, channels=channels, rate=rate, output=True, frames_per_buffer=self.chunk_size)
        self.recording_stream = self.p.open(format=audio_format, channels=channels, rate=rate, input=True, frames_per_buffer=self.chunk_size)
        
        # start threads
        self.receive_thread = threading.Thread(target=self.receive_server_data).start()
        self.send_audiodata_to_server()
    
    def connect_to_server(self) -> bool:
        while True:
            self.name = input('Enter your nickname: ')
            self.sock.sendto(msg_serialization(HelloMessage(name=self.name)), self.server)

            ans = receive_msg(self.sock, self.server)

            if ans is None:
                self.kill()
                raise Exception('smth went wrong, no answer')
            if ans.type == MsgType.ACK.value:
                print(f'Welcome to the Server, {self.name}')
                self.connected = True
                break
            elif ans and ans.type == MsgType.NACK.value:
                print(f'Something went wrong: {ans.text}')
            else:
                print('WTF:', ans)
        
        return True
        
    def kill(self):
        if self.sock:
            self.sock.shutdown(socket.SHUT_RDWR)
        self.keep_working.clear()

    def receive_server_data(self):
        while self.keep_working.is_set():
            try:
                msg = receive_msg(self.sock)
                # print(f'LOG: RECEIVER - {msg}')
                if msg is None:
                    self.kill()
                    return
                if msg.type == MsgType.AUDIO.value:
                    self.playing_stream.write(msg.audio)
                elif msg.type == MsgType.INFO.value:
                    print(msg.text)
            except (Exception, KeyboardInterrupt) as ex:
                print(f'EXCEPTION: RECEIVER - {ex}')
                self.kill()
                return

    def send_audiodata_to_server(self):
        while self.keep_going.is_set():
            try:
                data = self.recording_stream.read(self.chunk_size)
                msg = AudioMessage(audio=data, src=self.name)
                self.sock.sendall(msg_serialization(msg))
            except (Exception, KeyboardInterrupt) as ex:
                print(f'EXCEPTION: SENDER - {ex}')
                self.kill()
                if self.receive_thread:
                    self.receive_thread.join()
                break


def receive_msg(sock: socket.socket) -> Optional[Message]:
    try:
        length = int(sock.recvfrom(HEADER_SIZE)[0].decode())
        data = sock.recvfrom(length)[0]
        return msg_deserialization(data)
    except Exception as ex:
        # print(f'EXCEPTION: RCV_MSG - {ex}')
        return None


def createArgParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('ip', nargs='?', default='127.0.1.1')
    parser.add_argument('port', nargs='?', default=8888)
    return parser

if __name__ == '__main__':
    args = createArgParser().parse_args()
    client = Client(args.ip, args.port)
