import readline  # For input() side effect
import socket

from shared__util import (
    BadHeader,
    BuildLiveCommand,
    NormalTermination,
    StartLiveCommand,
    UnexpectedTermination,
    WaveformSimCommand,
    big_receive,
    deserialize_dataclass,
    send_message,
    serialize_dataclass
)

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