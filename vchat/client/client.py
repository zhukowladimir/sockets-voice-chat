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
        self.sock : socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.target_ip : str = ip
        self.target_port : int = port
        self.keep_working : threading.Event = threading.Event()
        self.keep_going :threading.Event = threading.Event()

        self.keep_working.set()
        self.keep_going.set()

        try:
            self.sock.connect((self.target_ip, self.target_port))
        except Exception as ex:
            print(f'EXCEPTION: INIT - {ex}')
            return

        self.chunk_size = 1024
        audio_format = pyaudio.paInt16
        channels = 1
        rate = 20000

        self.p = pyaudio.PyAudio()
        self.playing_stream = self.p.open(format=audio_format, channels=channels, rate=rate, output=True, frames_per_buffer=self.chunk_size)
        self.recording_stream = self.p.open(format=audio_format, channels=channels, rate=rate, input=True, frames_per_buffer=self.chunk_size)
        
        while True:
            self.name = input('Enter your nickname: ')
            self.sock.send(msg_serialization(HelloMessage(name=self.name)))

            ans = receive_msg(self.sock)
            if ans and ans.type == MsgType.ACK.value:
                print(f'Welcome to the Server, {self.name}')
                break
            elif ans and ans.type == MsgType.NACK.value:
                print(f'Something went wrong: {ans.text}')
            else:
                print('WTF:', ans)

        # start threads
        self.receive_thread = threading.Thread(target=self.receive_server_data).start()
        self.send_audiodata_to_server()

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



def createArgParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('ip', nargs='?', default='127.0.1.1')
    parser.add_argument('port', nargs='?', default=8888)
    return parser

if __name__ == '__main__':
    args = createArgParser().parse_args()
    client = Client(args.ip, args.port)
