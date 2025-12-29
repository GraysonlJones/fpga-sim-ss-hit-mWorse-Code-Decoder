'''Accessed from both the client and server programs'''
from __future__ import annotations

import ast
import dataclasses as dc
import os
import socket
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, TextIO

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

def serialize_dataclass(input: DataclassInstance) -> dict:
    '''Turns any dataclass into a dict.'''
    if dc.is_dataclass(input) and not isinstance(input, type):
        return dc.asdict(input)
    else:
        raise TypeError(f"{input} is not a dataclass")

def deserialize_dataclass[T: DataclassInstance](input: str, dc_type: type[T]) -> T:
    '''Attempts to turn the string input into a dict then into
    an instance of the given dataclass type'''
    if dc.is_dataclass(dc_type) and isinstance(dc_type, type):
        # evaluate string to dict. like eval() but safer
        input_dict: dict = ast.literal_eval(input)
        return dc_type(**input_dict)
    else:
        raise TypeError

@dataclass
class NamedFile:
    name: str
    content: str

    def to_disk(self, directory: Path = Path(".")):
        with open(Path.joinpath(directory.joinpath(self.name)), "w") as fp:
            fp.write(self.content)

    @classmethod
    def from_fp(cls, fp: TextIO, *, close_after: bool):
        output = NamedFile(os.path.basename(fp.name), fp.read())
        if close_after:
            fp.close()
        return output

@dataclass
class BuildLiveCommand:
    files: list[NamedFile]

    CODE: ClassVar[str] = "BL"

@dataclass
class StartLiveCommand:

    CODE: ClassVar[str] = "SL"

@dataclass
class WaveformSimCommand:
    output_filename: str
    files: list[NamedFile]

    CODE: ClassVar[str] = "WS"

AnyCommand = BuildLiveCommand | StartLiveCommand |WaveformSimCommand

class UnexpectedTermination(Exception):
    pass
class NormalTermination(Exception):
    pass
class BadHeader(Exception):
    pass

# Credit https://stackoverflow.com/a/17668009/
def big_receive(sock: socket.socket):
    '''Safely receives up to 10 GB after a
    a 10-byte ASCII number header.'''
    length_bytes = sock.recv(10)
    if not length_bytes: # disconnected, returned empty array
        raise NormalTermination
    try:
        expected_length = int(length_bytes.decode())
    except ValueError:
        raise BadHeader(f"{length_bytes}")
    data = bytearray() # mutable equivalent of bytes type
    while len(data) < expected_length:
        packet = sock.recv(expected_length - len(data))
        if not packet:
            raise UnexpectedTermination
        data.extend(packet)
    return data

def send_message(message: str, sock: socket.socket):
    message = f"{len(message):010}{message}"
    sock.send(message.encode())