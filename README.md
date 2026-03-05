# Graphical FPGA Simulator

***Note:** Assumes some terminal familiarity. Instructions for students would be
much more detailed.

Supports MacOS 13+, Windows 10/11, and Linux.
See [Qt's docs](https://doc.qt.io/qt-6/supported-platforms.html) for some
specifics on OS support. This was developed on a Mac, and for now, with
autocomplete currently unavailable on Windows, the experience is best on
Mac/Linux.

Attribution: The client runs on Python 3.14 with PySide6, with
another Python program invoking Verilator on the server. The server
runs in an Ubuntu container.

Note for Linux users: Qt support varies by distribution and window manager;
Ubuntu 22.04 with no intentional major changes to the configuration is the only
one I have tested on, but I think that any Debian or Ubuntu-based distribution
should be able to run this without difficulty
(Linux Mint and of course Debian being the most prominent of those).


## Required software
> [!IMPORTANT]  
> uv and git are trustworthy, but do generally do not download random things via the terminal. The internet is a scary place!

* **git** to download this repository. Check if already installed with
`git --version`.
    * Windows: [git install instructions for Windows](https://git-scm.com/install/windows).
        * If you are unsure if your CPU is x64 (aka x86-64 or AMD64):
        run `[System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture` in PowerShell. This will print out either "Arm64" or "X64".
        Select the corresponding standalone installer option from the linked
        page.
    * Mac: use `xcode-select --install`. This gets you various tools including git. Note that you may need to run `sudo xcodebuild -license accept`
    (which will prompt for your password) sometimes when your computer updates
    in order to re-accept Apple's TOS and use git.
    * Linux: [git install instructions for Linux](https://git-scm.com/install/linux)
    (lists various package manager commands) 

<!-- TODO: maybe cut out git and make a release on GitHub that people just download? -->

* **uv** to set up the Python environment. Check if already installed (unlikely)
with `uv --version`.
    * All platforms: [uv installation instructions](https://docs.astral.sh/uv/getting-started/installation/)
        * First try `pip install uv` (try `pip3 install uv` if that doesn't work)
        which installs it via Python's built-in package manager.
            * If that doesn't work, [uv's standalone installer](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer) will work. Follow
            the instructions there


* **Docker Desktop** to run the server-side code. Not needed if running in [native mode](#native-mode).
    * All platforms: [Docker installation page](https://www.docker.com/products/docker-desktop/).
    Same architecture situation as git, using the name AMD64 here instead of X64.
    This may take a while (took 5-10 minutes for me on Windows on
    fast internet).
* **Visual Studio Code** (or another IDE, and a VCD waveform viewer)
    * All platforms: [Visual Studio Code download page](https://code.visualstudio.com/Download)
        * I am using [this Verilog syntax highlighting extension](https://marketplace.visualstudio.com/items?itemName=mshr-h.VerilogHDL)
        and [this VCD waveform viewer extension](https://marketplace.visualstudio.com/items?itemName=lramseyer.vaporview)

## Installation and usage

1. Download materials and set up Docker:

* Clone this git repository:

`git clone https://github.com/TheHarmonicRealm/fpga-sim.git`
* Open the folder it makes in your IDE. For VSCode you can do:

`code ./fpga-sim`

* Download `docker_cache.zip` from Canvas.
TODO: host somewhere public too!!
Unzip it and copy the `docker_cache` folder to `fpga-sim`. That folder
should directly contain two folders and two files.

* Open Docker Desktop. Wait for the start screen, which says something like
"loading Docker Engine", to finish. You might be prompted to sign in and make
an account the first time (TODO: check if true).

> [!NOTE]  
> Docker must be open when building the image and when running the simulator
program. They will visibly fail if it is not.

2. Build Docker image. From the `fpga-sim` directory
(the IDE's integrated terminal is convenient and will start in the right place;
open it with <kbd>ctrl</kbd>+<kbd>`</kbd> in VSCode):
    ```
    docker buildx build --cache-to type=local,dest=./docker_cache --cache-from type=local,src=./docker_cache -t fpga-sim-server:v1 . 
    ```

    This step uses Docker's caching feature to create an image from the
    downloaded materials. It requires an internet connection.
    The `docker_cache` folder is unnecessary after this step, so you
    can delete it. Later, if the server code is ever changed, you can
    rebuild it with this command:

    ```
    docker buildx build -t fpga-sim-server:v1 .
    ```

    On my computer, I ran another command to create Docker images for both
    x86 and ARM — which would take ~10 minutes to do directly on my fast 
    computers, and much longer on a slow one — and this is the cache generated.
    The point of this is to, if the code changes and the Docker images need to
    be rebuilt, allow you to run this same command and skip the long steps
    that run before copying the code over.

3. Run the program from the terminal, in `fpga-sim`:

    ```
    uv run ./python/client__shell.py
    ```

    This will take a little bit the first time, as uv must
    set up a virtual environment, which involves downloading packages and possibly a new Python version. After the first time,
    the program is still run with this command and should not have any
    unusual startup delay.

    **You cannot run the script with a different command**, as the Python
    version must be correct and the packages must be available.

4. The client gives you a command-line interface (CLI). You can run three
specific commands here, along with `exit` to quit the client and server,
and `help` to list the commands. The standard ctrl-C exit shortcut is ignored
as it caused problems if done after launching the Qt window.

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
    * The window **MUST** be closed with the quit button at the bottom, or with
    Ctrl+W (CMD+W on Mac). Quitting in any other way (e.g. CMD+Q or the built-in
    menu bar quit item on Mac) will crash the program.
        * The window's X button is set to be grayed out, but preventing other
        ways of closing improperly is harder.
    * To allow running programs closer to what you can run on a real board,
    the plus-shaped buttons will stay pressed if you are holding shift when you
    release the mouse.

* `waveform_sim <input_directory> <output_filename.vcd> [-overwrite]`
    * Like `build_live_sim` but using `verilog/testbench`. The driving
    testbench module must similiarly be named `tb` both with the module/file.
    * The output will go to the provided file in `./waveforms/`. If
    it already exists, it will not run the command, to prevent an accidental
    overwrite.
        * `ex_tb` is a provided example. Note the required lines
        `$dumpfile("$DUMP_FILENAME");` and `$dumpvars(0, tb);` which must
        be unmodified.
    * If `-overwrite`, or any shortening of it (`-o` or longer),
    is provided as the third argument, the output file will be overwritten if
    it already exists. Otherwise, an error is printed if it already exists,
    to avoid accidents.
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
    server are included with Python, so uv is unnecessary here. Just run it
    with the `python3.14` alias that uv automatically created when setting up
    the client venv:

    ```
    python3.14 server__manager.py
    ```

    The server will print the port number it is running at.

3. Run the client from the fpga-sim project, the same way as described in
    the main instructions' step 3, but pass the port number as its third
    argument. The program will detect this and connect to the native server you
    opened, rather than starting up a docker container.

    The script should operate the same, except that when the server is stopped
    the last-built live sim persists rather than being lost on closing it.