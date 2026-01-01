import dataclasses as dc
import readline  # For input() side effect
import socket
import subprocess
import time
from pathlib import Path
from typing import IO

from gui__states import (  # For live sim loop
    OutputState,
    WholeInputState,
    WholeOutputState,
)
from shared__util import (
    AckMessage,
    BadHeader,
    BuildLiveCommand,
    ErrorMessage,
    NamedFile,
    NormalTermination,
    StartLiveCommand,
    UnexpectedTermination,
    WaveformSimCommand,
    big_receive,
    deserialize_dataclass,
    header_to_dc,
    send_message,
    serialize_dataclass,
)


def to_string(inp: WholeInputState):
    '''Converts a WholeInputState to a string that server can read:

    "UB,X|DB,X|LB,X|RB,X|CB,X|switches,XXXXXXXXXXXXXXXX" with X being 1 or 0
    
    TODO: This is super clunky!'''
    def bool_list_to_str(bool_list: list[bool]):
        return "".join([str(int(b)) for b in bool_list])
    strings = [
        f"UB,{int(inp.buttons.BTNU)}",
        f"DB,{int(inp.buttons.BTND)}",
        f"LB,{int(inp.buttons.BTNL)}",
        f"RB,{int(inp.buttons.BTNR)}",
        f"CB,{int(inp.buttons.BTNC)}",
        f"switches,{bool_list_to_str(list(reversed(dc.asdict(inp.switches).values())))}"
    ]
    return "|".join(strings)


def to_output_state(inp: str):
    '''Converts a string sent from the server to a WholeOutputState.
    Similar to to_string:

    "segment,XXXXXXX|dp,X|anode,XXXX|lights,XXXXXXXXXXXXXXXX|"

    TODO: This is also super clunky!
    '''
    def str_to_bool_list(inp_str: str, inv: bool = False):
        if not inv:
            return [(not bool(int(char))) for char in inp_str]
        else:
            return [(bool(int(char))) for char in inp_str]
    parts = inp[:-1].split("|")
    _, seg_str = parts[0].split(",")
    _, dp_str = parts[1].split(",")
    _, an_str = parts[2].split(",")
    _, led_str = parts[3].split(",")
    led = str_to_bool_list(led_str)
    seg = list(reversed(str_to_bool_list(seg_str))) + str_to_bool_list(dp_str)
    an = str_to_bool_list(an_str)
    return WholeOutputState(
        lights=OutputState.Lights(*led), 
        anode=OutputState.Anode(*an),
        cathode=OutputState.Cathode(*seg))

def live_sim(sock: socket.socket):
    sock.send(AckMessage.CODE.encode())
    send_message(serialize_dataclass(AckMessage()), sock)

    process = subprocess.Popen("./obj_dir/Vtop", text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    in_pipe: IO[str] = process.stdin # pyright: ignore[reportAssignmentType]
    out_pipe: IO[str] = process.stdout # pyright: ignore[reportAssignmentType]
    time.sleep(1)
    
    while(True):
        inp = big_receive(conn).decode()
        match inp:
            case "exit":
                print("Client requested live sim exit")
                send_message("exit", conn)
                time.sleep(1)
                print("Returning to main command loop")
                break
            case "": # Give sim process empty line to indicate no new input
                input_string = ""
            case _: # Otherwise input must be dataclass string
                try: # Try to convert; if it fails print error rather than crash
                    as_dc = deserialize_dataclass(inp, WholeInputState)
                    if type(as_dc) != WholeInputState:
                        raise RuntimeError(f"{as_dc} is not InputState!")
                    input_string = to_string(as_dc)
                except Exception as e:
                    print(f"Failure with input {inp}: e")
                    continue

        in_pipe.write(input_string + "\n")
        in_pipe.flush()

        new_output = out_pipe.readline().strip()
        if new_output != "":
            send_message(serialize_dataclass(to_output_state(new_output)), conn)
    # TODO: properly close process. Writing "exit\n" and calling process.wait() hangs forever...

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
