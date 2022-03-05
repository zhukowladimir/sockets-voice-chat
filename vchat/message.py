from dataclasses import dataclass
from dataclasses_json import dataclass_json
from enum import Enum
from typing import Optional
from base64 import b64decode, b64encode
import ormsgpack
import socket

class MsgType(Enum):
    AUDIO = 1
    HELLO = 2
    ACK = 3
    NACK = 4
    INFO = 5

HEADER_SIZE = 10


@dataclass
class Message:
    type: Optional[int] = None

@dataclass
class AudioMessage(Message):
    audio: bytes = b''
    src: str = ''
    def __post_init__(self):
        self.type = MsgType.AUDIO.value

@dataclass
class HelloMessage(Message):
    name: str = ''
    def __post_init__(self):
        self.type = MsgType.HELLO.value

@dataclass
class AckMessage(Message):
    def __post_init__(self):
        self.type = MsgType.ACK.value

@dataclass
class NackMessage(Message):
    text: str = ''
    def __post_init__(self):
        self.type = MsgType.NACK.value

@dataclass
class InfoMessage(Message):
    text: str = ''
    def __post_init__(self):
        self.type = MsgType.INFO.value


def msg_serialization(msg: Message) -> bytes: 
    data = ormsgpack.packb(msg)
    return f'{len(data):<{HEADER_SIZE}}'.encode() + data

def msg_deserialization(msg: bytes) -> Message:
    try:
        data = ormsgpack.unpackb(msg)
    except Exception as ex:
        print(f'EXCEPTION: MSG_DESER - {ex}')
        print(msg)

    if data['type'] != MsgType.AUDIO.value:
        print('Log: got msg', data)

    if data['type'] == MsgType.AUDIO.value:
        return AudioMessage(**data)
    elif data['type'] == MsgType.HELLO.value:
        return HelloMessage(**data)
    elif data['type'] == MsgType.ACK.value:
        return AckMessage(**data)
    elif data['type'] == MsgType.NACK.value:
        return NackMessage(**data)
    elif data['type'] == MsgType.INFO.value:
        return InfoMessage(**data)


def receive_msg(sock: socket.socket) -> Optional[Message]:
    try:
        length = int(sock.recv(HEADER_SIZE).decode())
        data = sock.recv(length)
        return msg_deserialization(data)
    except Exception as ex:
        # print(f'EXCEPTION: RCV_MSG - {ex}')
        return None

# print(msg_deserialization(msg_serialization(AudioMessage(1, b'sdf324lK23', 'zusty'))[10:]))