import base64
import os
import platform
import re
import shlex
import signal
import socket
import subprocess
import sys
import textwrap
import time
from argparse import ArgumentParser
from enum import Enum, auto
from pathlib import Path
from sys import argv
from typing import IO

from client__paths import (
    live_sim_folder,
    testbench_folder,
    top_folder,
    waveforms_folder,
)
from colorama import Fore, Style
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

def waveform_sim(input_files: list[NamedFile], output_path: Path, folder_name: str):
    global sock

    command = WaveformSimCommand(output_path.name, input_files)
    t1 = time.time()
    send_command(command)

    result = receive_error_or_ack(sock)
    t2 = time.time()
    match result:
        case ErrorMessage(content):
            if content.strip().startswith("SRVRSEZ:"):
                print(f"{Fore.RED}{content.strip()[len("SRVERSEZ"):]}{Style.RESET_ALL}")
            else:
                print(f"Server returned error message:\n{textwrap.indent(colorize(content, f"verilog/live_sim/{folder_name}"), "  ")}")
                if (man_url := get_url(content)) is not None:
                    print(f"See Verilator's manual at {man_url}")
        case AckMessage():
            print(f"{Fore.GREEN}Successfully ran testbench simulation in {round((t2 - t1), 3)}s. See output at {clickable_filepath(output_path, 2)}{Style.RESET_ALL}")
            file_message = big_receive(sock).decode()
            output_file = deserialize_dataclass(file_message, NamedFile)
            output_file.to_disk(waveforms_folder)
    

def build_live_sim(input_files: list[NamedFile], folder_name: str):
    global sock

    command = BuildLiveCommand(input_files)
    t1 = time.time()
    send_command(command)

    result = receive_error_or_ack(sock)
    t2 = time.time()
    match result:
        case ErrorMessage(content):
            print(f"Server returned error message:\n{textwrap.indent(colorize(content, f"verilog/live_sim/{folder_name}"), "  ")}")
            if (man_url := get_url(content)) is not None:
                print(f"See Verilator's manual at {man_url}")
        case AckMessage():
            print(f"{Fore.GREEN}Successfully built live simulation in {round((t2 - t1), 3)}s. Run with start_live_sim{Style.RESET_ALL}")

def start_live_sim():
    global app

    command = StartLiveCommand()
    send_command(command)

    result = receive_error_or_ack(sock)
    match result:
        case ErrorMessage(content): # known to be plain text hardcoded message
            print(f"{Fore.RED}{content}{Style.RESET_ALL}")
        case AckMessage():
            print("Server started simulation. Launching GUI now.")
            # Run gui in a subprocess (fork) and give it the socket we already have
            if not is_windows:
                subprocess.run(f"uv run ./python/gui__main.py {sock.fileno()}", shell=True, close_fds=False)
            else: # Windows requires fancy code; must use Popen because child must receive input after its creation
                live_sim_process = subprocess.Popen("uv run ./python/gui__main.py", stdin=subprocess.PIPE, shell=True, close_fds=False)
                child_pipe: IO[bytes] = live_sim_process.stdin # pyright: ignore[reportAssignmentType]
                shareable_socket = sock.share(live_sim_process.pid)
                child_pipe.write(base64.b64encode(shareable_socket))
                child_pipe.close() # send EOF before wait
                live_sim_process.wait()

class SuggestMode(Enum):
    NONE = auto()
    TB = auto()
    LIVE = auto()

def is_overwrite(text: str):
    return len(text) >= 2 and "-overwrite".startswith(text) and len(text) <= len("-overwrite")

def suggest_folders(path: Path):
    return [thing for thing in os.listdir(path) if path.joinpath(thing).is_dir()]

def filter_start(li: list[str], text: str):
    return [x for x in li if x.startswith(text)]

def commands_completer(text: str, state: int):
    '''Matches signature expected'''
    # if help and/or exit are included, output is spaced super wonky.
    options: list[str] = ["build_live_sim", "waveform_sim", "start_live_sim"]

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
            case ["build_live_sim", *_] if current_word == 1:
                suggest_mode = SuggestMode.LIVE
            case ["waveform_sim", *_] if current_word == 1:
                suggest_mode = SuggestMode.TB
                # adding -overwrite suggestion at end wasn't working, TODO: fix

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

def colorize(err: str, folder: str | None = None):
    # TODO: this would make the listed filenames match the host's paths and
        # clickable and awesome
        # however bc argparse is used this need annoying refactor
    if folder is not None:
        err = re.sub(r"user_inputs/", folder + "/", err)
    # put last line with total error info at top, and cut off the make error if there is one
    err = re.sub(r"\n*(?P<otherstuff>(\n|.)*)%Error: (?P<lasterr>Exiting due to.*)\n.*", f"{Style.BRIGHT}{Fore.MAGENTA}\\g<lasterr>:\n{Style.RESET_ALL}\\g<otherstuff>", err, flags=re.MULTILINE)
    # indent all lines after first
    lines = err.splitlines()
    err = lines[0] + "\n" + textwrap.indent("\n".join(lines[1:]), "  ")
    # remove lines that tell you to use a command e.g. ': ... Suggest see manual; fix the duplicates, or use --top-module to select top.'
    err = re.sub(r"( {8} *:.*use --(\w*)+(-\w*)* to.*\n)*", "", err, flags=re.MULTILINE)
    # remove Verilator manual line
    err = re.sub(r"^.*the manual at.*$\n", "", err, flags=re.MULTILINE)
    # color the individual error/warning lines and replace % with a space
    err = re.sub(r"%(?P<title>\w*(-\w*)?): (?P<content>.*\n( {8} *:.*\n)*)", f"{Fore.RED}{Style.BRIGHT} \\g<title>:{Style.RESET_ALL} {Fore.RED}{r"\g<content>"}{Style.RESET_ALL}", err)
    # color the line markers and the subsequent number-less pipe lines
    err = re.sub(r"(?P<front1>(\d| )*\|)(?P<content>.*)\n(?P<front2>(\d| )*\|)(?P<content2>.*)", f"{Fore.CYAN}{r"\g<front1>"}{Style.RESET_ALL}{r"\g<content>"}\n{Fore.CYAN}{r"\g<front2>"}{Style.BRIGHT}{Fore.MAGENTA}{r"\g<content2>"}{Style.RESET_ALL}", err)
    return err.rstrip()

def get_url(err: str):
    attempt = re.search(r"manual at (https://[^ ]*)", err)
    if attempt is not None:
        return attempt.group(1)
    return None

class CommandSetupError(Exception):
    pass

class ContinueException(Exception):
    pass

def check_vcd_name(filename: str):
    if filename.split(".")[-1] != "vcd":
        raise ContinueException(f"{filename} should end with .vcd")
    if filename != Path(filename).name:
        # will ultimately save directly to a defined output folder
        raise ContinueException(f'{filename} is a path, not a pure name (e.g. "wave.vcd")')
def is_verilog(filename: str):
    extension = filename.split(".")[-1]
    return extension == "v"# or extension == "sv"

def crawl_input_directory(front_target: str, containing_folder: Path, folder_name: str):
    folder = Path(*containing_folder.joinpath(folder_name).parts[-3:])
    try:
        all_filenames = os.listdir(folder)
    except FileNotFoundError:
        raise ContinueException(f"./{folder} does not exist")
    except NotADirectoryError:
        raise ContinueException(f"./{folder} is a file, not a folder")

    v_filenames = [name for name in all_filenames if is_verilog(name)]

    if len(v_filenames) == 0:
        raise ContinueException(f"./{folder} contains no Verilog (.v) files")
    else:
        try:
            v_filenames.remove(front_target)
        except ValueError:
            raise ContinueException(f"./{folder} lacks a {front_target} file.")
        v_filenames.insert(0, front_target) # put at front to indicate top to Verilator
        
    file_paths = [Path(folder, name) for name in v_filenames]

    return [NamedFile.from_fp(open(file_path, "r"), close_after=True) for file_path in file_paths]

def clickable_filepath(filepath: Path, depth: int):
    return f"./{Path(*filepath.parts[-depth:])}"

if __name__ == "__main__":
    is_mac = (platform.system() == "Darwin")
    is_linux = (platform.system() == "Linux")
    is_windows = (platform.system() == "Windows")

    if sys.prefix == sys.base_prefix: # if not in a venv give some guidance
        print("It appears this is being run without using the right uv environment; exiting.")
        if Path(os.getcwd()) != top_folder: # if in the wrong folder give command to get there, too
            print(f"To get to the proper folder run:\n\tcd {shlex.quote(str(top_folder))}")
            print("Then launch the program with:\n\tuv run ./python/client__shell.py")
        else:
            print("Instead run it from here with:\n\tuv run ./python/client__shell.py")
        print("For more info, view the README: https://github.com/TheHarmonicRealm/fpga-sim#Graphical-FPGA-Simulator")
        # TODO: include exported HTML version of README for offline usage?
        exit(1)
    try:
        socket_port = int(argv[1])
        docker_mode = False
    except IndexError: # No argument passed
        docker_mode = True
        print("Launching Docker container.")
        # Launch docker:
        #   preexec_fn is part of ignoring ctrl-C
        if not is_windows:
            process = subprocess.Popen("docker run -p 0:9834 fpga-sim-server:v1", text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setpgrp)
        else: # unavailable on Windows. TODO: figure out equivalent code to ignore on Windows
            process = subprocess.Popen("docker run -p 0:9834 fpga-sim-server:v1", text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        # wait until first print-out
        out_pipe: IO[str] = process.stdout # pyright: ignore[reportAssignmentType]
        out_pipe.readline()

        print("Docker container started successfully. Launching client.")
        try:
            socket_port = int(get_latest_container_port())
        except RuntimeError as e:
            print(e)
            exit(1)
    except ValueError:
        print(f"Could not convert {argv[1]} to a port number. Exiting.")
        exit(1)


    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.set_inheritable(True)
        try:
            sock.connect(("127.0.0.1", socket_port))
            if len(sock.recv(2048).decode()) == 0:
                raise ConnectionError("Not refused, but failed")
        except (ConnectionError, ConnectionRefusedError) as e:
            if docker_mode:
                print("Auto-started container rejected connection for some reason.")
                print("Quitting. Try running again; if it fails again, please contact the developer!")
            else:
                print(f"Failed to connect to the native server that may be running at port {socket_port}. Make sure it is running and that the port number matches what it output!")
            print(f"Original exception: {e}")
            exit(1)

        if docker_mode:
            print(f"Connected to automatically-started Docker container running at port {socket_port}")
        else:
            print(f"Connected to native server running at port {socket_port}")

        if is_mac or is_linux: # no readline on Windows, unfortunately!
            import readline
            readline.set_completer(commands_completer)
            readline.parse_and_bind("bind ^I rl_complete" if is_mac else "tab: complete")
            print("Suggestions and autocomplete are available with tab!")
        else:
            print("Run help or ? to see available commands!")
            

        app = None

        signal.signal(signal.SIGINT, signal.SIG_IGN) # ignore ctrl-C

        while True:
            command_string = input("> ").strip()

            words = shlex.split(command_string)
            if len(words) == 0:
                continue

            command = words[0]
            args = words[1:]

            try:
                match command:
                    case "waveform_sim":
                        match args:
                            case [folder, filename, *_]:
                                waveforms_folder.mkdir(exist_ok=True)
                                check_vcd_name(filename)
                                output_path = waveforms_folder.joinpath(filename)

                                overwrite = False

                                if(len(args) == 3):
                                    if(is_overwrite(args[2])):
                                        overwrite = True
                                    else:
                                        raise ContinueException(f'Last arg should be -overwrite or a clipping of that.')
                                elif len(args) > 3:
                                    raise ContinueException(f'Only 2 or 3 args expected.')
                                
                                if (not overwrite) and output_path.is_file():
                                    raise ContinueException(f'Cannot overwrite existing file {clickable_filepath(output_path, 1)}; pass -ov option if you wish to allow overwriting.')

                                files = crawl_input_directory("tb.v", testbench_folder, folder)
                                waveform_sim(files, output_path, folder)
                            case _:
                                raise ContinueException("Args: <folder> <filename.vcd> [-ov]")
                    case "build_live_sim":
                        match args:
                            case [folder]:
                                files = crawl_input_directory("top.v", live_sim_folder, folder)
                                build_live_sim(files, folder)
                            case _:
                                raise ContinueException("Args: <folder>")
                    case "start_live_sim":
                        if len(args) != 0:
                            raise ContinueException("Should be given no args")
                        start_live_sim()
                    case "exit" | "quit":
                        exit(0)
                    case "help" | "?" | "-h":
                        print("Available commands: \n* build_live_sim <folder>\n* waveform_sim <folder> <filename.vcd> [-overwrite]\n* start_live_sim\n* exit")
                    case _:
                        print(f"Unrecognized command: {command}"
                        "\n\nAvailable commands: \n* build_live_sim\n* waveform_sim\n* start_live_sim\n* help")
            except ContinueException as e:
                print(f"{Fore.RED}{e}{Style.RESET_ALL}")
                continue # when help is called or a bad argument is passed
