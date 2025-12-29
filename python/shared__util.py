'''Accessed from both the client and server programs'''
from __future__ import annotations

import ast
import dataclasses as dc
import os
import socket
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, TextIO

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

def is_dc_type(input: Any):
    return dc.is_dataclass(input) and isinstance(input, type)

def is_dc_instance(input: Any):
    return dc.is_dataclass(input) and not isinstance(input, type)

def serialize_dataclass(input: DataclassInstance) -> str:
    '''Turns a dataclass into a string representation of a dict.

    See `deserialize_dataclass()` for acceptable types list (dataclasses and
    Python literal structures).'''
    if is_dc_instance(input): # TODO: recursively check that fields are all appropriate and throw type error otherwise
        return str(dc.asdict(input))
    else:
        raise TypeError(f"{input} is not a dataclass")

def deserialize_dataclass[T: DataclassInstance](input: str, dc_type: type[T]) -> T:
    '''Attempts to turn the string input into a dict then recursively into
    an instance of the given dataclass type.

    CAUTION: For safety, uses `ast.literal_eval()`, so it only works properly
    if every field is one of:
    * dataclass subtype
    * Python literal structure, meaning, according to docstring:
        * string
        * bytes
        * number
        * tuple
        * list
        * dict
        * set
        * boolean
        * None
    '''
    if is_dc_type(dc_type):
        # evaluate string to dict. like eval() but safer
        input_dict: dict = ast.literal_eval(input)
        dc_out = dc_type(**input_dict)
        for field in dc.fields(dc_type):
            field_type: type = field.type # pyright: ignore[reportAssignmentType]
            if is_dc_type(field_type): # if dataclass, recurse
                dict_str = str(getattr(dc_out, field.name)) # must convert back to string for literal_eval
                setattr(dc_out, field.name, deserialize_dataclass(dict_str, field_type))
        return dc_out
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