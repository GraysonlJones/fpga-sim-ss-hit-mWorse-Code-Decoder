import os
import platform
import readline
import shlex
import socket
import subprocess
from argparse import ArgumentParser
from enum import Enum, auto
from pathlib import Path

from client__parsers import (
    ContinueException,
    attempt_parse_and_run,
    build_parser,
    start_parser,
    wavef_parser,
)
from client__paths import live_sim_folder, testbench_folder, waveforms_folder
from gui__main import run_app
from shared__util import (
    AckMessage,
    AnyCommand,
    BuildLiveCommand,
    ErrorMessage,
    NamedFile,
    StartLiveCommand,
    WaveformSimCommand,
    big_receive,
    deserialize_dataclass,
    receive_error_or_ack,
    send_message,
    serialize_dataclass,
)


def print_parser_error(parser: ArgumentParser, message: str):
    print(parser.format_usage())
    print(message)

def send_command(command: AnyCommand):
    global sock
    str_command = serialize_dataclass(command)
    sock.send(type(command).CODE.encode())
    send_message(str_command, sock)

def waveform_sim(output_filename: str, input_files: list[NamedFile], overwrite: bool):
    waveforms_folder.mkdir(exist_ok=True)
    
    output_path = Path(waveforms_folder, output_filename)

    if (not overwrite) and output_path.is_file():
        print(f'Cannot overwrite existing file "{output_path}"; pass -ov option if you wish to allow overwriting.')
        return

    command = WaveformSimCommand(output_filename, input_files)
    send_command(command)

    result = receive_error_or_ack(sock)
    match result:
        case ErrorMessage(content):
            print(f"Sent files to server, but it returned an error message: {content}")
            return
        case AckMessage():
            print(f"Successfully ran testbench simulation. See output at waveforms/{output_filename}")
    file_message = big_receive(sock).decode()
    output_file = deserialize_dataclass(file_message, NamedFile)
    output_file.to_disk(waveforms_folder)
    

def build_live_sim(input_files: list[NamedFile]):
    global sock

    command = BuildLiveCommand(input_files)
    send_command(command)

    result = receive_error_or_ack(sock)
    match result:
        case ErrorMessage(content):
            print(f"Server returned error message: {content}")
        case AckMessage():
            print(f"Successfully built live simulation. Run with {start_parser.prog}.")

def start_live_sim():
    global app

    command = StartLiveCommand()
    send_command(command)

    result = receive_error_or_ack(sock)
    match result:
        case ErrorMessage(content):
            print(f"Server returned error message: {content}")
        case AckMessage():
            print(f"Server started simulation. Launching GUI now.")
            app = run_app(sock, app)

class SuggestMode(Enum):
    NONE = auto()
    TB = auto()
    LIVE = auto()

def is_overwrite(text: str):
    return "-overwrite".startswith(text) and len(text) <= len("-overwrite")

def suggest_folders(path: Path):
    return [thing for thing in os.listdir(path) if path.joinpath(thing).is_dir()]

def filter_start(li: list[str], text: str):
    return [x for x in li if x.startswith(text)]

def commands_completer(text: str, state: int):
    '''Matches signature expected'''
    # if help and/or exit are included, output is spaced super wonky.
    options: list[str] = [build_parser.prog, start_parser.prog, wavef_parser.prog]

    full_line = readline.get_line_buffer().lstrip()

    shlexd = shlex.split(full_line)

    current_word = max(len(shlexd) - 1, 0) # start at 0. both 1 and 0 tokens = word 0

    # must check emptiness first or the function will except, with readline silencing the error
    if full_line != "" and full_line[-1] == " " and len(shlexd) > 0: # treat trailing space a new word being started
        current_word += 1

    matches = [] # default value

    if current_word == 0: # empty line/one word maybe partially typed
        matches = filter_start(options, full_line)
    else:
        suggest_mode = SuggestMode.NONE
        match shlexd:
            case [build_parser.prog, *_] if current_word == 1:
                suggest_mode = SuggestMode.LIVE
            case [wavef_parser.prog, arg1, arg2, *_] if is_overwrite(arg1) or is_overwrite(arg2) and current_word == 3:
                suggest_mode = SuggestMode.TB
            case [wavef_parser.prog, arg1, *_] if not is_overwrite(arg1) and current_word == 2:
                suggest_mode = SuggestMode.TB

        try:
            last_term = shlexd[current_word]
        except IndexError:
            last_term = ""

        if suggest_mode == suggest_mode.LIVE:
            matches = filter_start(suggest_folders(live_sim_folder), last_term)
        elif suggest_mode == suggest_mode.TB:
            matches = filter_start(suggest_folders(testbench_folder), last_term)
    try:
        return matches[state]
    except IndexError:
        return None
    
def get_latest_container_port():
    '''Gets the port of the latest-started Docker server container.
    Error if there are no containers open or if Docker seems to be unopened.'''
    # Command prints string with 0 or more lines of this if successful:
    #   '{container hex id}|0.0.0.0:{port}->9834/tcp, [::]:{port}->9834/tcp'
    proc = subprocess.run('docker ps --format "{{.ID}}|{{.Ports}}" --filter "ancestor=fpga-sim-server:v1"', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    match proc.returncode:
        case 0:
            output = proc.stdout.decode()
            for line in output.splitlines():
                port_string = line.split("|")[1]
                start = len("0.0.0.0:")
                end = port_string.find("->9834")
                return port_string[start:end]
            else:
                raise RuntimeError(f"No container for the server was found running; make sure that you started one, and that it was built with the exact command specified in the instructions.")
        case _:
            raise RuntimeError(f"docker ps command failed; make sure that Docker Desktop is installed and is open.")

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            socket_port = int(get_latest_container_port())
        except RuntimeError as e:
            print(e)
            exit(1)

        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect(("127.0.0.1", socket_port))
        if len(sock.recv(2048).decode()) == 0:
            print("Container rejected connection! Make sure there is not another client script running already connected to it; there must be one container running for every client.")
            exit(1)
        else:
            print(f"Connected to Docker container running at port {socket_port}.")

        is_mac = (platform.system() == "Darwin")
        is_linux = (platform.system() == "Linux")

        if is_mac or is_linux: # no readline on Windows, unfortunately!
            import readline
            readline.set_completer(commands_completer)
            readline.parse_and_bind("bind ^I rl_complete" if is_mac else "tab: complete")
            print("Suggestions and autocomplete are available with tab!")
        else:
            print("Run help or ? to see available commands!")
            

        app = None

        while True:
            try:
                command_string = input("> ").strip()
            except KeyboardInterrupt:
                print("exit (Ctrl+C)")
                exit(0)

            words = shlex.split(command_string)
            if len(words) == 0:
                continue

            command = words[0]
            args = words[1:]

            try:
                match command:
                    case wavef_parser.prog:
                        attempt_parse_and_run(wavef_parser, args, waveform_sim)
                    case build_parser.prog:
                        attempt_parse_and_run(build_parser, args, build_live_sim)
                    case start_parser.prog:
                        attempt_parse_and_run(start_parser, args, start_live_sim)
                    case "exit" | "quit":
                        exit()
                    case "help" | "?" | "-h":
                        print("Available commands: \n* build_live_sim\n* waveform_sim\n* start_live_sim\n* exit")
                    case _:
                        print(f"Unrecognized command: {command}"
                        "\n\nAvailable commands: \n* build_live_sim\n* waveform_sim\n* start_live_sim\n* help")
            except ContinueException:
                continue # when help is called or a bad argument is passed
