import argparse
import os
from argparse import ArgumentError, ArgumentParser
from collections.abc import Callable
from functools import partial
from pathlib import Path
from typing import Any

from client__paths import live_sim_folder, testbench_folder
from shared__util import NamedFile


class ContinueException(Exception):
    pass

def attempt_parse_and_run(parser: ArgumentParser, args: list[str], run_fn: Callable):
    try:
        arg_namespace = parser.parse_args(args)
    except ArgumentError as e:
        with_period = str(e).removesuffix(".") + "."
        print(with_period, f"\nCall {parser.prog} -h to view help!")
        raise ContinueException
    except SystemExit as e: # i.e. help
        raise ContinueException

    run_fn(*vars(arg_namespace).values())

def raise_argument_error(arg_name: str, arg_val: Any, message: str):
    raise ArgumentError(None, f"{arg_name} \"{arg_val}\" {message}")

def is_verilog(filename: str):
    extension = filename.split(".")[-1]
    return extension == "v"# or extension == "sv"

def crawl_input_directory(front_target: str, containing_folder: Path, folder_name: str):
    
    folder = containing_folder.joinpath(folder_name)
    raise_argerr = partial(raise_argument_error, "input_directory", Path(*folder.parts[-3:]))
    try:
        all_filenames = os.listdir(folder)
    except FileNotFoundError:
        raise_argerr(f"does not exist")
    except NotADirectoryError:
        raise_argerr(f"is a file, not a folder")

    v_filenames = [name for name in all_filenames if is_verilog(name)]

    if len(v_filenames) == 0:
        raise_argerr(f"contains no .v files. Please make sure that all input files have the proper extensions.")
    else:
        try:
            v_filenames.remove(front_target)
        except ValueError:
            raise_argerr(f"lacks a {front_target} file.")
        v_filenames.insert(0, front_target) # put at front to indicate top to Verilator
        
    file_paths = [Path(folder, name) for name in v_filenames]

    return [NamedFile.from_fp(open(file_path, "r"), close_after=True) for file_path in file_paths]


def check_vcd_name(filename: str):
    raise_argerr = partial(raise_argument_error, "output_filename", filename)
    if filename.split(".")[-1] != "vcd":
        raise_argerr(f"is not a .vcd")
    if filename != Path(filename).name:
        # will ultimately save directly to a defined output folder
        raise_argerr(f'is a path, not a pure name (e.g. "wave.vcd")')

    return filename

# Output of type function: all .v files from folder, with top.v at front of list
build_parser = ArgumentParser("build_live_sim", exit_on_error=False, description="Sends all Verilog files found in the given directory to the server and attempts to synthesize code for live simulation.")
build_parser.add_argument("input_directory", help="Name of a directory within verilog/live_sim/ containing .v files for a single synthesizable design. The top module must be named top. Press tab to list available folders (Mac/Linux-only).", type=partial(crawl_input_directory, "top.v", live_sim_folder))


start_parser = argparse.ArgumentParser("start_live_sim", exit_on_error=False, description="Starts an interactive GUI running the most recently successfully built live simulation module.")

# Output and checks of type function:
#   * all .v files from folder, with tb.v at front of list
#   * unchanged VCD filename. Verifies that it is just e.g. x.vcd, not waveforms/x.vcd
#       NO CHECK FOR IF IT EXISTS! Must happen after because it depends on -ov!!!
#   * Whether the VCD can be overwritten
wavef_parser = ArgumentParser("waveform_sim", exit_on_error=False, description="Sends all Verilog files found in the given directory to the server and attempts to run them as a testbench, outputting the waveform result to the provided file.")
wavef_parser.add_argument("output_filename", help="Name of a .vcd file to be created in the waveforms file, where the output of the simulation will be stored.", type=check_vcd_name)
wavef_parser.add_argument("input_directory", help="Name of a directory within verilog/testbench/ containing .v files for a single testbench design. The top simulation module must be named tb. Press tab to list available folders (Mac/Linux-only).", type=partial(crawl_input_directory, "tb.v", testbench_folder))
wavef_parser.add_argument("-ov", "--overwrite", action="store_true", help="Allow overwriting the passed VCD file with the new run's output if it already exists.")