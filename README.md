# Graphical FPGA Simulator

**Note:** Assumes some terminal familiarity. Instructions for students would be
much more detailed.

Supports MacOS 13+, Linux, and Windows 10/11.
See [Qt's docs](https://doc.qt.io/qt-6/supported-platforms.html) for some
specifics on OS support. This was developed on a Mac, and for now, with
autocomplete currently unavailable on Windows, the experience is best on
Mac/Linux. Otherwise there should be no feature differences, aside from lack
of dark mode on Windows because it is quite low-contrast there. It does not
have much Linux testing but compatibility for the Python APIs used is very
high with Mac.

Attribution: The client runs on Python 3.14 with PySide6, with
another Python program invoking Verilator on the server. The server
runs in an Ubuntu container.

Note for Linux users: Qt support varies by distribution and window manager;
Ubuntu 22.04 with no intentional major changes to the configuration is the only
one I have tested on, but I think that any Debian or Ubuntu-based distribution
should be able to run this without difficulty
(Linux Mint and of course Debian being the most prominent of those).


> [!NOTE]  
> **Identifying your processor's architecture**
> Every computer's CPU has a specific instruction set architecture (ISA).
Some of the required software needs you to select the correct version.
These mostly support two architectures, one of which almost
any personal computer is running on. I know the naming conventions are
confusing but it's just something you need to get used to:
>   - **x86-64**, a.k.a. AMD64, x64, x86, x86_64, or Intel.
>   - **AArch64**, a.k.a. ARM64, ARM, or (Mac-only) Apple Silicon.
>
> How to identify, by OS:
>   - Mac: any Mac from the M1 on, released late 2020, is ARM, while older Macs
>   (back to 2006) are Intel.
>       - Run `arch` in Terminal to check.
>   - Windows: the vast majority of Windows PCs are x86. Some laptops are ARM,
>   almost all of which have Snapdragon chips.
>       - Run `[System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture`
>       in PowerShell to check.
>   - Linux: I am sure that, if you are on Linux, you know your architecture.
>       - If you don't: run `uname -m` in your terminal.


## Required software
> [!CAUTION]  
> The recommended programs are trustworthy†, but please do not download random
things via the terminal without thinking about it.
The internet is a scary place!

* **git** to download this repository. Check if already installed with
`git --version`.
    * Windows: [git install instructions for Windows](https://git-scm.com/install/windows).
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
* **Visual Studio Code** (or another IDE)
    * All platforms: [Visual Studio Code download page](https://code.visualstudio.com/Download)
        * I am using [this Verilog syntax highlighting extension](https://marketplace.visualstudio.com/items?itemName=mshr-h.VerilogHDL)
* **VaporView** or **GTKWave** (or waveform viewer supporting VCDs)
    * Highly recommended, and integrated into VSCode: [VaporView](https://marketplace.visualstudio.com/items?itemName=lramseyer.vaporview).
    * GTKWave (less pretty, without IDE integration, though it has the benefits
    of launching its own window):
        * [GTKWave for Linux](https://gtkwave.github.io/gtkwave/install/unix_linux.html)
        * [GTKWave for Mac](https://gtkwave.github.io/gtkwave/install/mac.html)
        * [GTKWave for Windows](https://gtkwave.github.io/gtkwave/install/win.html)

## Installation and usage

1. Download materials and set up Docker:

* Clone this git repository:

`git clone https://github.com/TheHarmonicRealm/fpga-sim.git`
* Open the folder it makes in your IDE. For VSCode you can do:

`code ./fpga-sim`

* Download the appropriate docker image (ARM or x86) from Canvas.
Put it in the `fpga-sim` folder.

* Open Docker Desktop. Wait for the start screen, which says something like
"loading Docker Engine", to finish. You might be prompted to sign in and make
an account the first time (TODO: check if true).

> [!Note]  
> Docker must be open when building the image and when running the simulator
program. They will visibly fail if it is not.

2. Load Docker image. From the `fpga-sim` directory
(the IDE's integrated terminal is convenient and will start in the right place;
open it with <kbd>ctrl</kbd>+<kbd>`</kbd> in VSCode) run the appropriate one of:
    ```
    docker load < fpga_sim_image_ARM.tar
    ```
    or 
    ```
    docker load < fpga_sim_image_x86.tar
    ```

    If you do not have access to my Docker images, you can build it yourself,
    though it will take a while (~10 minutes on my nice Mac and Windows laptops):

    ```
    docker buildx build -t fpga-sim-server:v1 .
    ```

    * If you are an instructor who wants to use this, you can recreate the x86
    and ARM images yourself with this command, which builds both at once
    using emulation (I have only run this on ARM Mac):

        ```
        docker buildx build --platform linux/amd64,linux/arm64 -t fpga-sim-server:v1 .
        ```

        This took quite a long time when both ran at once from a clean slate.
        It may go faster if you first build it for just your platform using the
        regular build command so the cache will be reused, rather than running
        both in parallel and having them starve each other for RAM.


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
and `help` to list the commands.
Do not press <kbd>ctrl</kbd>+<kbd>C</kbd> (normally quit for terminal apps);
on Mac/Linux, it is intentionally ignored to avoid an improper exit,
while on Windows it closes the program with errors.

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
    * To allow running programs closer to what you can run on a real board,
    the plus-shaped buttons will stay pressed if you are holding shift when you
    release the mouse.
    * This window can be quit normally with the window's X button or with
    <kbd>ctrl</kbd>+<kbd>W</kbd>
    (Mac: <kbd>⌘</kbd>+<kbd>Q</kbd> or <kbd>⌘</kbd>+<kbd>W</kbd>).
    It can be paused and unpaused with <kbd>P</kbd>.

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
    * If the program is run in VSCode's terminal and VaporView is installed,
    the waveform will open in that automatically. If it is not installed, or
    it is run outside of VSCode, the program will look for GTKWave as a backup.
        * VSCode only reports whether the extension is installed, so the
        program will still try to use VaporView if it is disabled.
            * Options to override the opening behavior don't exist yet.
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

†No warranty given by developer, etc.