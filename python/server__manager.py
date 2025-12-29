import readline  # For input() side effect
import socket

import gui__constants as c  # For live sim test loop
from gui__states import (  # For live sim loop
    InputState,
    OutputState,
    WholeInputState,
    WholeOutputState,
)
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
    serialize_dataclass,
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

def live_sim(sock: socket.socket):
    while True:
        try:
            x = input()
            if x == "exit":
                send_message(x, sock)
                break
            else:
                x = eval(x)
            if not isinstance(x, WholeOutputState):
                raise ValueError
        except:
            continue
        m = serialize_dataclass(x)
        print(m)
        send_message(m, sock)

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(("0.0.0.0", 9834))
        server_sock.listen()

        conn, addr = server_sock.accept()
        while True:
            header = conn.recv(2)
            if header == b'':
                print("Connection disconnected normally")
                exit(0)
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
            command = deserialize_dataclass(dict_str, dc_type)
            print(command)

            match command:
                case BuildLiveCommand(files):
                    # build_live(conn, files)
                    pass
                case StartLiveCommand():
                    live_sim(conn)
                    pass
                case WaveformSimCommand(name, files):
                    # waveform_sim(conn, name, files)
                    pass
