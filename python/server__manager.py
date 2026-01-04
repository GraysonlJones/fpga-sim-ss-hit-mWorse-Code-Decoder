import ast
import dataclasses as dc
import socket
import subprocess
import time
from os import makedirs, environ
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

def bool_list_to_int(bl: list[bool]):
    return sum(int(b) << i for i, b in enumerate(reversed(bl)))

def int_to_bool_list(num: int, width: int):
    partial_list = [bool(int(c)) for c in bin(num)[2:]]
    false_prefix = [False] * (width - len(partial_list))
    return false_prefix + partial_list

def flat_input_dict(input_state: WholeInputState) -> dict[str, int]:
    switches: list[bool] = list(dc.asdict(input_state.switches).values())
    return {
        "UB": int(input_state.buttons.BTNU),
        "DB": int(input_state.buttons.BTND),
        "LB": int(input_state.buttons.BTNL),
        "RB": int(input_state.buttons.BTNR),
        "CB": int(input_state.buttons.BTNC),
        "Switches": bool_list_to_int(switches)
    }

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
                    input_string = str(flat_input_dict(as_dc))
                except Exception as e:
                    print(f"Failure with input {inp}: e")
                    continue

        in_pipe.write(input_string + "\n")
        in_pipe.flush()

        output_string = out_pipe.readline().strip()
        if output_string != "":
            output_dict: dict[str, int] = ast.literal_eval(output_string)
            new_segment = list(reversed(int_to_bool_list(output_dict["Segment"], 7))) # FPGA is G-A
            new_dp = int_to_bool_list(output_dict["DP"], 1)
            new_anode = int_to_bool_list(output_dict["Anode"], 4)
            new_lights = int_to_bool_list(output_dict["Lights"], 16)

            output_state = WholeOutputState(
                lights=OutputState.Lights(*new_lights),
                anode=OutputState.Anode(*new_anode),
                cathode=OutputState.Cathode(*(new_segment + new_dp)),
            )
            # print(f"Shell: Sending {output_state}")x
            send_message(serialize_dataclass(output_state), conn)
    # TODO: properly close process. Writing "exit\n" and calling process.wait() hangs forever...

def try_make(files: list[NamedFile]):
    '''Runs make with the given list of NamedFiles, saving them to
    a folder first. Assumes that the client has checked that there is one
    called top.v.'''
    makedirs(Path("./user_inputs"), exist_ok=True)
    for file in files:
        file.to_disk(Path("./user_inputs"))
    
    names = [file.name for file in files]
    try:
        names.remove("top.v")
    except ValueError:
        return ErrorMessage(f"Lacking a top.v. Client should have caught this.")
    names.insert(0, "top.v") # put at front to indicate top to Verilator

    # List is passed in as an environment variable
    filenames_str = " ".join([f"./user_inputs/{name}" for name in names])
    # Must append to existing environment or Verilator fails
    envvars = environ.copy() | {"COMPILE_FILES": filenames_str}

    proc = subprocess.run(["make"], stderr=subprocess.PIPE, env=envvars)

    match proc.returncode:
        case 0:
            return AckMessage()
        case other:
            return ErrorMessage(f"\n\n{proc.stderr.decode()}")

def build_live(sock: socket.socket, files: list[NamedFile]):
    result = try_make(files)
    sock.send(result.CODE.encode())
    send_message(serialize_dataclass(result), sock)

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(("0.0.0.0", 9834))
        server_sock.listen()

        # PERHAPS: Have a rule that the top module MUST be called Vtop
        #   I certainly could get around the name-finding thing with code, but
        #   it would be good for the users' learning, debugging experience etc
        #   to have a clear idea which one is the top module.

        conn, addr = server_sock.accept()
        while True:
            # TODO: maybe, instead of fixed-size header codes,
            #   prefix dataclass serializations with type name?
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
            # print(command)

            match command:
                case BuildLiveCommand(files):
                    build_live(conn, files)
                    pass
                case StartLiveCommand():
                    live_sim(conn)
                    pass
                case WaveformSimCommand(name, files):
                    # waveform_sim(conn, name, files)
                    pass
