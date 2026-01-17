# Graphical FPGA Simulator

***Note:** Assumes some terminal familiarity. Instructions for students would be
much more detailed.*

Supports MacOS 13+, Windows 10/11, and Linux.
See [Qt's docs](https://doc.qt.io/qt-6/supported-platforms.html) for some
specifics on OS support. This was developed on a Mac, and for now, with
autocomplete currently unavailable on Windows, the experience is best on
Mac/Linux.

Attribution: The client runs on Python 3.13 with PySide6, with
another Python 3.13 program invoking Verilator on the server. The server
runs in an Ubuntu container.

Note for Linux: Qt support varies by distribution and window manager; Ubuntu
22.04 with no intentional major changes to the configuration is the only one I
have tested on, but I think that any Debian or Ubuntu-based distribution should
be able to run this without difficulty
(Linux Mint and of course Debian being the most prominent of those).


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

## Installation and usage

1. Clone this git repository and open the folder in your IDE.
Open Docker Desktop.

* **Docker must be open when building the image and every time the server
is running.**

2. Build Docker image. From the `fpga-sim` directory:
    ```
    docker build -t fpga-sim-server:v1 .
    ````

    This step requires internet, as it is downloading the base Docker Ubuntu
    image and then within the VM it is creating running commands to download
    software. Make sure you are on a decent connection, or it will be slowed
    down.

    The build process this launches takes quite a while.
    I don't have a "clean start" time estimate, but the longest step, building
    Verilator from source, takes about 6 minutes on my fast MacBook Pro.

    Docker has a great caching system so, if the server code needs to be updated
    and the image rebuilt, all steps before copying that file will be skipped,
    for a much shorter total build time (in my experience under 10 seconds).

3. Run the program from the terminal, in `fpga-sim`:

    ```
    uv run ./python/client__shell.py
    ```

    This will take a little bit the first time, as uv must
    set up a virtual environment. After this, the command should not have any
    unusual startup delay.

    **You cannot run the script with a different command**, as the Python
    version must be correct and PySide6 must be available.

    * While Ubuntu is the primary target for Verilator, it compiles on
    Mac (Clang or G++) and MSVC (Windows), and some other systems;
    see [Verilator's install instructions](https://verilator.org/guide/latest/install.html#os-requirements) for more info.
    If it is installed on your computer, this program has an alternative mode
    to run the server natively.
    This likely has better performance on computers with little RAM and
    Verilator is a much smaller download than Docker Desktop.

        I have not had any issues running the server directly on Mac, with
        Verilator built from source using Clang, but I would not recommend it as
        the default method for students because installing Verilator is
        intimidating you are new to terminals.
        * If using this mode, first run `python/setup_host_server.py` to set up
        the server folder. With no arguments it will place it in
        `fpga-sim/host_server`, or if passed a path it will create a folder
        exactly at `<that path>/host_server` with the same contents.
            * A really annoying rule enforced by my setup script is that the
            path the server is placed at must contain no spaces, due to
            GNU make, which is used to invoke Verilator. There is no
            way around this other than using a different path.
        * Run `python3.13 server__manager.py`
        (no non-stdlib package dependencies so no need for environment setup).
        It will start up a server and print out a port number; run the client
        script as you would normally, but pass the port number as its argument.

4. The client gives you a command-line interface (CLI). You can run three
specific commands here, along with `exit` to quit the client and server,
and `help` to get formal help. Each command can also be run as `command -h` to
see specific help. List of commands:

* `build_live_sim <input_directory>`
    * Directory name is appended to `verilog/live_sim` then searched.
    All `.v` files there (subfolders ignored).
    will be sent to the server to try to build for live simulation.
    * The top module must be called `top`. All filenames must match their
    module names (i.e. `top` ↔︎ `top.v`, etc).
        * An example is in `ex_live`.
            * The inputs and outputs of the top module must match this exactly!

* `start_live_sim`
    * If a live simulation build has succeeded during this session,
    this will start it. It will open up a window where you can interact
    with the program as if it were a real FPGA.
    * The window **MUST** be closed with the quit button at the bottom, rather
    than by quitting its app or with the window's X button. Otherwise, the
    session will crash and you will need to start the server and client again.
        * Preventing bad closures is a TODO. Graying out the X button should be
        easy, but preventing quitting might not be possible.
    * To allow running programs closer to what you can run on a real board,
    the plus-shaped buttons will stay pressed if you are holding shift when you
    release the mouse.

* `waveform_sim [-ov] <output_filename.vcd> <input_directory>`
    * Like `build_live_sim` but using `verilog/testbench`. The driving
    testbench module must similiarly be `tb` module/file.
    * The output will go to the provided file in `./waveforms/`. If
    it already exists, it will not run the command, to prevent an accidental
    overwrite.
        * `ex_tb` is a provided example.
    * If `-ov` flag is present, the output file can be overwritten. Otherwise
    an error will be printed if it already exists, to avoid accidents.
* Mac/Linux-only: in the CLI, if you press tab you can get suggestions and
autocomplete for commands, and, in the ending position, folder names for
`waveform_sim`/`build_live_sim`. The terminal also has up/down history
browsing.
    * There is a third-party library for readline I want to eventually add
    so Windows has a better experience.