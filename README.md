# Graphical FPGA Simulator

***Note:** Assumes some terminal familiarity. Instructions for students would be
much more detailed.

Supports MacOS 13+, Windows 10/11, and Linux.
See [Qt's docs](https://doc.qt.io/qt-6/supported-platforms.html) for some
specifics on OS support. This was developed on a Mac, and for now, with
autocomplete currently unavailable on Windows, the experience is best on
Mac/Linux.

Attribution: The client runs on Python 3.13 with PySide6, with
another Python 3.13 program invoking Verilator on the server. The server
runs in an Ubuntu container.

Note for Linux users: Qt support varies by distribution and window manager;
Ubuntu 22.04 with no intentional major changes to the configuration is the only
one I have tested on, but I think that any Debian or Ubuntu-based distribution
should be able to run this without difficulty
(Linux Mint and of course Debian being the most prominent of those).


## Required software

* **git** to download this repository
    * [git installation instructions](https://git-scm.com/install/windows)
* **uv** to set up the Python environment
    * [uv installation instructions](https://docs.astral.sh/uv/getting-started/installation/)
* **Docker Desktop** to run the server-side code. Not needed if running in [native mode](#native-mode).
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

* **Docker must be open when building the image and every time the program
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
    On my fairly fast Mac and Windows laptops, it took about 8 to 9 minutes
    to do the full process with most parts uncached. On a less powerful
    computer I am sure it can take much longer; I intend to look into
    distributing prebuilt Docker images when this is more stable.

    Docker has a great caching system so, if the server code needs to be updated
    and the image rebuilt, all steps before copying that file will be skipped,
    for a much shorter total build time (in my experience, under 5 seconds).

3. Run the program from the terminal, in `fpga-sim`:

    ```
    uv run ./python/client__shell.py
    ```

    This will take a little bit the first time, as uv must
    set up a virtual environment. After this, the command should not have any
    unusual startup delay.

    **You cannot run the script with a different command**, as the Python
    version must be correct and PySide6 must be available.

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

### Native mode

While Ubuntu is the primary target for Verilator, it also compiles on
Mac (both Clang and G++) and Windows, and some other systems;
see [Verilator's install instructions](https://verilator.org/guide/latest/install.html#os-requirements) for more info.

If Verilator is installed on your computer, this program has an alternative mode
to run the server directly without Docker.
This likely has better performance on computers with little RAM.

I would not recommend this as the default method for students because installing
Verilator is intimidating if you are new to terminals.

On Mac, using the built-in Clang to compile Verilog, this works smoothly, with
the requirements I needed downloaded from brew, and I am sure it works well on
most Linux distributions.
Windows support for Verilator appears to be more rough; if you attempt to
install Verilator and natively run the server on any platform, please let me
know about your experience, successful or not!

Using this mode:
1. From the top fpga-sim folder, set up the server with:

    ```
    uv run python/setup_host_server.py <path>
    ```

    With no arguments, this will place the server in `fpga-sim/host_server`, or
    it otherwise will place it in `<path>/host_server`.
    A rule enforced by my setup script, which cannot be circumvented, is that
    **the path must contain no spaces**, because GNU make is used by the server.
    This script will also fail with a warning if Verilator has not yet been
    installed.

2. Open the server's folder in a new terminal. The only dependencies for the
    server are included with Python, so just use the `python3.13` alias that uv
    automatically created when setting up the fpga-sim folder's environment:

    ```
    python3.13 server__manager.py
    ```

    The server will print the port number it is running at.

3. Run the client from the fpga-sim project, the same way as described in
    the main instructions' step 3, but pass the port number as its third
    argument. The program will detect this and connect to the native server you
    opened, rather than starting up a docker container.

    The script should operate the same, except that when the server is stopped
    the last-built live sim persists rather than being lost on closing it.