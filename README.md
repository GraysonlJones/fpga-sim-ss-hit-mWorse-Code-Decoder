# Graphical FPGA Simulator

***Note:** Assumes some terminal familiarity. Instructions for students would be
much more detailed.*

Supports Mac, Windows, and Linux (at least Ubuntu out of the box should work
once the software is added).

Attribution: The client runs on Python 3.13 with PySide6, with
another Python 3.13 program invoking Verilator on the server.


## Required software

* **git** to download this repository
    * [git installation instructions](https://git-scm.com/install/windows)
* **uv** to set up the Python environment
    * [uv installation instructions](https://docs.astral.sh/uv/getting-started/installation/)
* **Docker Desktop** to run the server-side code.
    * [Docker installation page](https://www.docker.com/products/docker-desktop/).
    This may take a while (I think it took 5-10 minutes for me on Windows on
    fast internet).
* **Visual Studio Code** (or another IDE)
    * [Visual Studio Code download page](https://code.visualstudio.com/Download)
        * I am using [this Verilog syntax highlighting extension](https://marketplace.visualstudio.com/items?itemName=mshr-h.VerilogHDL)
        and [this VCD waveform viewer extension](https://marketplace.visualstudio.com/items?itemName=lramseyer.vaporview)
        * Python extensions may be needed to have it automatically handle
        virtual environments. I am not super sure about this.

## Installation and usage

1. Clone this git repository and open the folder in your IDE.

2. Build Docker image. From the `fpga-sim` directory:
    ```
    docker build -t fpga-sim-server:v1 .
    ````

    This will take a while (maybe 5-15 minutes), as this involves building
    Verilator from source in a VM. This only needs to happen once.

3. Start the server:

    ```
    docker run -p 9834:9834 fpga-sim-server:v1
    ```

    This must happen before starting the client, or the client will not have
    something to connect to. Every time you quit the client, the server
    will terminate, so you will have to run this again.

    I recommend opening it in a system terminal outside of the IDE to easily
    have it in a separate window you can switch back and forth with. It does
    not matter what folder your terminal is in when you run this command.

    If the server is ever stuck with no client connected, quit with `ctrl+C`.

4. Run the client from the terminal, in `fpga-sim`:

    ```
    uv run ./python/client__shell.py
    ```

    This will take a little bit the first time, as uv must
    set up a virtual environment. After this, the command should not have any
    unusual startup delay.

    **You cannot run the script with a different command**, as the Python
    version must be correct and PySide6 must be available.

5. The client gives you a command-line interface (CLI). You can run three
specific commands here, along with `exit` to quit the client and server:

* `build_live_sim <input_directory>`
    * All `.v` files in the given directory (subfolders ignored)
    will be sent to the server to try to build for live simulation.
    * The top module must be called `top`. All filenames must match their
    module names (i.e. `top` ↔︎ `top.v`, etc).
        * An example is in `./examples/ex_live/`.
            * The inputs and outputs of the top module must match this exactly!

* `start_live_sim`
    * If a live simulation build has succeeded during this session,
    this will start it. It will open up a window where you can interact
    with the program as if it were a real FPGA.
    * The window **MUST** be closed with the in-window quit button, rather
    than quitting its app or the window's X button. Otherwise, the session
    will crash and you will need to start the server and client again.
        * Preventing bad closures is a TODO. I think it is doable.
    
* `waveform_sim <output_filename.vcd> <input_directory>`
    * Just like `build_live_sim`, it will search the input folder for
    `.v` files. There must be a `tb` module/file. Same rule about matching
    file/module names as with the other command.
    * The output will go to the provided file in `./waveforms/`. If
    it already exists, it will not run the command, to prevent an accidental
    overwrite.
        * An example is in `./examples/ex_tb/`.
* Mac/Linux-only: in the CLI, tab autocomplete works for files/folders within
this folder and below (Python's `readline` package is not on Windows).