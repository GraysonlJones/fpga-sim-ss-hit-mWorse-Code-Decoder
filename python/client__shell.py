import os
import platform
import readline
import socket
from functools import partial
from pathlib import Path

from gui__states import InputState, OutputState, WholeInputState, WholeOutputState
from gui__main import run_app
from shared__util import (
    AnyCommand,
    BuildLiveCommand,
    NamedFile,
    StartLiveCommand,
    WaveformSimCommand,
    ErrorMessage,
    AckMessage,
    receive_error_or_ack,
    serialize_dataclass,
    send_message,
    big_receive
)
import gui__constants as c


class VerilogGatherError(RuntimeError):
    '''Raised by get_verilog_from_folder if anything bad happens.
    That function will print the relevant message.'''
    pass

def is_verilog(filename: str):
    extension = filename.split(".")[-1]
    return extension == "v" or extension == "sv"


def print_function_error(caller: str, message: str):
    print(f'{caller}(): {message}')

def get_verilog_from_folder(folder: str, caller: str):
    print_error = partial(print_function_error, caller)
    try:
        all_filenames = os.listdir(folder)
    except FileNotFoundError:
        print_error(f'folder argument "{folder}" does not exist')
        raise VerilogGatherError
    except NotADirectoryError:
        print_error(f'folder argument "{folder}" is a file, not a folder')
        raise VerilogGatherError

    v_filenames = [name for name in all_filenames if is_verilog(name)]
    file_paths = [Path(folder, name) for name in v_filenames]

    if len(file_paths) == 0:
        print_error(f'{folder} contains no .v/.sv files. Please make sure '
            'that all input files have the proper extensions.')
        raise VerilogGatherError

    # TODO: Is there a possible exception where a file can't be read?
    #   For now can catch generic Exception and print, and tell user to contact me
    return [NamedFile.from_fp(open(file_path, "r"), close_after=True) for file_path in file_paths]

def send_command(command: AnyCommand):
    str_command = serialize_dataclass(command)
    sock.send(type(command).CODE.encode())
    send_message(str_command, sock)

def build_live_sim(folder: str):
    global sock
    print_error = partial(print_function_error, "build_live_sim")
    try:
        files = get_verilog_from_folder(folder, "build_live_sim")
    except VerilogGatherError:
        return
    except Exception as e:
        print_error(f"Unexpected exception: {e}. "
              "Please contact developer.")
        return
    
    for file in files:
        if file.name == "top.v":
            break
    else:
        print_error("No file named top.v. Top module MUST be named top.v.")
        return

    command = BuildLiveCommand(files)
    send_command(command)

    result = receive_error_or_ack(sock)
    match result:
        case ErrorMessage(content):
            print_error(f"server returned error message: {content}")
        case AckMessage():
            print_error(f"Build is good!")
        case _:
            print_error(f"unexpected response {result}")

def start_live_sim():
    global sock
    global app
    print_error = partial(print_function_error, "start_live_sim")

    command = StartLiveCommand()
    send_command(command)
    # TODO: server will send its socket to the Verilator executable
    #   This side sends its socket to the GUI.
    #       Qt must be run in the main thread. Not sure if you can
    #       just make a new QApp, run it, exit, and then continue,
    #       or if a secondary process is needed.
    #   When app quits, send some quit message from this function
    #       then return to shell loop

    # app starts as None (declared in main), and run_app() returns a
    #   QApplication instance which is then reused in future runs.
    #   Deleting the app and creating a new one each time is messier.
    result = receive_error_or_ack(sock)
    match result:
        case ErrorMessage(content):
            print_error(f"server returned error message: {content}")
        case AckMessage():
            print_error(f"launching simulation successfully!")
            app = run_app(sock, app)
        case _:
            print_error(f"unexpected response {result}")

def waveform_sim(output_filename: str, folder: str):
    global sock
    print_error = partial(print_function_error, "waveform_sim")

    if output_filename.split(".")[-1] != "vcd":
        print_error(f"output filename should be a .vcd")
        return
    name_as_path = Path(output_filename)
    if output_filename != name_as_path.name:
        # will ultimately save directly to a defined output folder
        print_error(f"output filename should be a name, not a path")
        return
    
    # TODO: make absolute/better-defined
    output_folder = Path("./waveforms/")
    output_folder.mkdir(exist_ok=True)
    
    output_path = Path(output_folder, output_filename)

    try:
        files = get_verilog_from_folder(folder, "waveform_sim")
    except VerilogGatherError:
        return
    except Exception as e:
        print_error(f"unexpected exception: {e}. "
            "Please contact developer.")
        return

    try:
        fp = open(output_path, "x")
    except FileExistsError:
        print_error(f'output file "{output_path}" already exists')
        return
    

    command = WaveformSimCommand(str(output_path), files)
    send_command(command)
    fp.write(f"Output for waveform with input {files} would be here!")

    # Convert command to JSON
    # TODO:
    #  Await response
    #  If good, populate output location
    #   Result will be a NamedFile. Just call its to_disk and we're good.
    #  If bad, delete fp and print error message
    # response = big_receive(sock).decode()
    # match response:
    #     case _:
    #         pass
    fp.close()

if __name__ == "__main__":
    # tab complete on Mac and Linux
    # TODO: Windows code. Seemed more complex.
    # TODO: add code to also autocomplete the three commands at start of line?
    app = None
    if platform.system() == "Darwin":
        readline.parse_and_bind("bind ^I rl_complete")
    elif platform.system() == "Linux":
        readline.parse_and_bind("tab: complete")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect(("127.0.0.1", 9834))
        while True:
            try:
                command_string = input("> ").strip()
            except KeyboardInterrupt:
                print("exit (Ctrl+C)")
                exit(0)
            words = command_string.split(" ")
            words[0] = words[0].lower()
            match words:
                case ["build_live_sim", folder]:
                    build_live_sim(folder)
                case ["start_live_sim"]:
                    start_live_sim()
                case ["waveform_sim", output_filename, folder]:
                    print("waveform", output_filename, folder)
                    waveform_sim(output_filename, folder)
                case ["build_live_sim", *_]:
                    print("Proper usage: build_live_sim <input_directory>")
                case ["start_live_sim", *_]:
                    print("Proper usage: start_live_sim")
                case ["waveform_sim", *_]:
                    print("Proper usage: waveform_sim <output_filename.vcd> <input_directory>")
                case ["exit"]:
                    exit(0)
                case [*e]:
                    print(f'Unexpected input "{" ".join(e)}"')