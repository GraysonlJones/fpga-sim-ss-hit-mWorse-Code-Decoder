import readline  # For input() side effect
import socket

from shared__util import (
    BuildLiveCommand,
    StartLiveCommand,
    WaveformSimCommand,
    deserialize_dataclass,
)


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

def header_to_dc(header: str):
    match header:
        case BuildLiveCommand.CODE:
            return BuildLiveCommand
        case StartLiveCommand.CODE:
            return StartLiveCommand
        case WaveformSimCommand.CODE:
            return WaveformSimCommand
        case _:
            raise ValueError(header)


if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(("0.0.0.0", 9834))
        server_sock.listen()

        conn, addr = server_sock.accept()
        while True:
            header = conn.recv(2)
            dc_type = header_to_dc(header.decode())
            try:
                message = big_receive(conn)
            except UnexpectedTermination:
                print("Connection terminated after sending length value, without sending full message")
                exit(1)
            except NormalTermination:
                print("Connection disconnected normally")
                exit(0)
            except BadHeader as e:
                print(f"Connection sent invalid header {str(e)}")
                exit(0)
            dict_str = message.decode()
            print(deserialize_dataclass(dict_str, dc_type))