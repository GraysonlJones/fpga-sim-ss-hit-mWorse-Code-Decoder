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

According to [Verilator's installation instructions](https://verilator.org/guide/latest/install.html#os-requirements),
"Verilator is developed and has primary testing on Ubuntu, with additional
testing on Apple OS-X, FreeBSD and Windows MSVC". Therefore, if you have bad
performance
(an in-GUI framerate counter to check it is something I will likely add)
it *should* be possible to install Verilator natively, copy the files listed in
the Dockerfile's `COPY` line into a folder outside of the client project, and
run the server natively on your own computer. Success is not guaranteed, and
I also don't know that performance will necessarily improve. If you get
most of the way there and run into problems, feel free to contact me about it
and I may be able to help.


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