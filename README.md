# Graphical FPGA Simulator

This is a program for students learning Verilog, using [Verilator](https://verilator.org) as its
backend. It provides a friendly command-line interface to run Verilog code, both in testbenches and
to drive interactive simulations. It uses Python, PySide6 (Qt), and Docker (to run Verilator in an Ubuntu VM).

<img width="500" alt="GIF demonstrating live simulation" src="https://github.com/user-attachments/assets/b557681d-6a7e-4934-9ae3-26ab077222f0" />

Primary development is on Mac, with some testing on Windows and Ubuntu.
It is essentially identical across platforms, except that Windows lacks tab
autocompletion; there are no known major platform-specific issues aside from
this, and it will run at full speed on most compatible computers.
I recommend running this on Mac or Linux over Windows if you have a choice.

## System requirements

Updated March 21, 2026, based on [Qt's requirements](https://doc.qt.io/qt-6/supported-platforms.html)
and Docker's. Docker is the bounding dependency for all of these; if you obtain
an older version, it may work on unsupported operating systems.
[Native mode](#native-mode) does not require Docker, though it requires
more advanced computer skills to set up.

* **Mac**:
    * MacOS 14 Sonoma, 15 Sequoia, or 26 Tahoe
        * Docker supports the last two versions of MacOS (see [Docker's Mac requirements](https://docs.docker.com/desktop/setup/install/mac-install/#system-requirements)).
    * All models that can run Sonoma have at least 8GB of RAM, which is sufficient.

* **Windows**:
    * Windows 11 version 22H2 (build 22631) or higher
        * Docker supports the currently-serviced versions of Windows 11 (see [Docker's Windows requirements](https://docs.docker.com/desktop/setup/install/windows-install/#system-requirements)).
    * 8GB of RAM.

* **Linux**:
    * Minimum 4GB of RAM.
    * See these two links for information about Linux support:
        * [Docker Engine's supported distributions](https://docs.docker.com/engine/install/)
        * [Docker Desktop's system requirements](https://docs.docker.com/desktop/setup/install/linux/#general-system-requirements) (which are presumably less than or equal to those of Engine)

> [!Important]  
> Students: please read [the student-targeted instructions](STUDENT_INSTRUCTIONS.md) before continuing.

## Required software

> [!Caution]
> The recommended programs are trustworthy†, but please do not download random
software without thinking about it. The internet is a scary place!

* **git** to download this repository. Check if already installed with
`git --version`.
    * Windows: [git install instructions for Windows](https://git-scm.com/install/windows).
    * Mac: use `xcode-select --install`. This gets you various tools including git. Note that you may need to run `sudo xcodebuild -license accept`
    (which will prompt for your password) sometimes when your computer updates
    in order to re-accept Apple's TOS and use git.
    * Linux: [git install instructions for Linux](https://git-scm.com/install/linux)
    (lists various package manager commands) 

<!-- TODO: maybe cut out git and make a release on GitHub that people just download? -->

* **uv** to set up the Python environment. Check if it is already installed (unlikely)
with `uv --version`.
    * Mac/Windows:
        * First try `python3 -m pip uv` (common on Mac or Linux),
        `py -m pip uv` (Windows), or `python -m pip uv`, which would install it via
        Python's built-in package manager.
            * If none of those work, use
            [uv's standalone installer](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer).
    * Linux: use [uv's standalone installer](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer)

* **Docker** to run the server-side code. Not needed if running in [native mode](#native-mode).
    * Windows and Mac: install [Docker Desktop](https://www.docker.com/products/docker-desktop/).
    Same architecture situation as git, using the name AMD64 here instead of X64.
    This may take a while (took 5-10 minutes for me on Windows on
    fast internet).
        * **Windows note**:
            * When installation is done, Docker will prompt you to restart.
            * On first launch after installation, you will likely have to run
            a command in the terminal to update Windows Subsystem for Linux
            (WSL).
    * Linux: install [Docker Engine](https://docs.docker.com/engine/install/);
    Docker Desktop is unnecessary for this software, and the core "engine"
    has support for more distributions. Setup with apt, as described on Docker's
    site, was very easy for me on Ubuntu.
        * You must follow the [post-install instructions](https://docs.docker.com/engine/install/linux-postinstall#manage-docker-as-a-non-root-user)
        and make Docker usable as a non-root user for my software to be able to
        access it. I had to restart in order for these to apply, though it seems
        to vary for some systems.
* **Visual Studio Code** (or another IDE)
    * All platforms: [Visual Studio Code download page](https://code.visualstudio.com/Download)
    * Also: install a syntax highlighter.
    I use [this Verilog extension](https://marketplace.visualstudio.com/items?itemName=mshr-h.VerilogHDL), though there there may be better ones out there!
* **VaporView** or **GTKWave** (or another waveform viewer supporting VCDs)
    * Highly recommended, and integrated into VSCode: [VaporView](https://marketplace.visualstudio.com/items?itemName=lramseyer.vaporview).
    * [GTKWave](https://gtkwave.github.io/gtkwave/index.html) is less pretty,
    without IDE integration, though it has the benefits of launching its own
    window. It may be annoying to get running on Windows.

## Installation and usage

1. Download materials and set up Docker:

* Clone this git repository:

```
git clone https://github.com/TheHarmonicRealm/fpga-sim.git
```

* Open the folder it makes in your IDE. For VSCode you can do:

```
code ./fpga-sim
```

* Download the appropriate Docker image (i.e. choose ARM or x86) from Canvas.
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
    docker load -i fpga_sim_image_x86.tar
    ```
    or 
    ```
    docker load -i fpga_sim_image_ARM.tar
    ```

    
<details>

<summary>Building if images are unavailable</summary>

If you do not have access to my Docker images, you can build it yourself,
though it will take a while (~10 minutes on my nice Mac and Windows laptops):

```
docker buildx build -t fpga-sim-server:v1 .
```

If you are an instructor who wants to use this, you can recreate the x86
and ARM images yourself with this command, which builds both at once
using emulation (I have only run this on ARM Mac):

```
docker buildx build --platform linux/amd64,linux/arm64 -t fpga-sim-server:v1 .
```

This took quite a long time when both ran at once from a clean slate.
It will go faster if you first build it for just your platform using the
regular build command so the cache will be reused, rather than running
both in parallel and having them starve each other for RAM. To create tarfiles, subsequently run these two commands:

```
docker image save --output fpga_sim_image_x86.tar fpga-sim-server --platform linux/amd64
```
and
```
docker image save --output fpga_sim_image_ARM.tar fpga-sim-server --platform linux/arm64
```

</details>


3. Run the program from the terminal, in `fpga-sim`:

    ```
    uv run ./python/client__shell.py
    ```

    This will take a little bit the first time, as uv must
    set up a virtual environment, which involves downloading packages
    and possibly a new Python version. After the first time,
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

Note that where an argument is shown in angle brackets (<>), you are replace
its value with your own, **without brackets.**
For example, `print <name>` would be called as `print Goddard`,
NOT `print <Goddard>`.

The commands listed in the below sections are to be run within the CLI after
starting it up.

### Waveform testbench simulation
Place your testbench and modules in a new folder within the `verilog/testbench`
folder. The top testbench module must be called `tb`; see
`verilog/testbench/ex_tb` for a barebones example you can use as a template.
The folder and module names must contain only underscores and letters.
There are a couple things to note about what your modules must look like:

* As in the provided example the lines
`$dumpfile("$DUMP_FILENAME");` and `$dumpvars(0, tb);` must be the first
things in your `initial begin` block.
* `$display` statements will not be forwarded back to the user.
* End your testbench with `$stop`, like the example; using `$finish`, or not
having an ending command, will crash the simulator.

All filenames must match their module names (i.e. `lights` ↔︎ `lights.v`, etc).
This rule goes for live simulation, too.

Run the testbench with `waveform_sim <input_directory> <output_filename.vcd> [-overwrite]`.
This may take a few minutes.

If `-overwrite`, or any shortening of it (`-o` or longer), is provided as the
third argument, the output file will be overwritten if it already exists.
Otherwise, an error is printed if it already exists, to avoid accidents.
The first time you run this, it will have you choose which waveform viewer, if
any, to automatically open waveforms in. You can later change your setting
by deleting the file `python/waveform_viewer_choice.txt` and running the
program again.

* **Example call:** `build_live_sim ex_tb wave.vcd`
* **Example call (allowing overwrite):** `build_live_sim ex_tb wave.vcd -ov`

### Live simulation
Place your modules in a new folder within the `verilog/live_sim` folder.
The top module must be called `top`, and must have inputs and outputs matching
the example in `verilog/live_sim/ex_live`. The folder and module names must
contain only underscores and letters.

Do not include `$display` statements anywhere in your code. These will crash
the simulator. (There are probably other commands like this that can break it.)

Build your simulation with: `build_live_sim <input_directory_name>`,
for example calling as `build_live_sim ex_live` to build the provided example.
This may take a few minutes.

Run your simulation with `start_live_sim`. Note that, if you build a simulation,
then close the app, the simulation must be built again in order to run it;
compiled modules are not preserved between runs of the program. This will open
a visual window running your model. Notes about it:

* On some platforms, this window might not automatically go the front,
so if you don't see anything after a couple seconds check your window
switcher.
* The plus-shaped buttons will stay pressed if you are holding shift when
you release the mouse.
* This window can be quit normally with the window's X button or with
<kbd>ctrl</kbd>+<kbd>W</kbd>
(Mac: <kbd>⌘</kbd>+<kbd>Q</kbd> or <kbd>⌘</kbd>+<kbd>W</kbd>).
It can be paused and unpaused with <kbd>P</kbd> or the button at the bottom.

* **Mac/Linux-only**: in the CLI, if you press tab you can get suggestions and
autocomplete for commands, and, in the second argument position, folder names
for `waveform_sim`/`build_live_sim`. There is also up/down history browsing
like in a real shell.
    * There is a third-party library for readline I want to eventually add
    so Windows has a better experience.

## Updating the software

Use `git pull` to update the project. This will not modify your waveform viewer
settings or delete your code. However, if you have modified any of the project's
source files, you should revert your changes before pulling.

The Docker image will change sometimes. When a change is made
to the code that requires an update to the Docker image, I will change the code
to check the image's version. The code will fail on startup and tell you they
do not match if you update the code without loading a required new version
of the image. The process to load a new version of the image is the same as
to load the first time. **The current Docker image version is v1.**

### Native mode

While Ubuntu is the primary target for Verilator, it also compiles on
Mac (both Clang and G++) and Windows, and some other systems;
see [Verilator's install instructions](https://verilator.org/guide/latest/install.html#os-requirements)
for information about compiling it.

If Verilator is installed on your computer, this program has an alternative mode
to run the server directly without Docker.

**This mode is not recommended for students without previous terminal experience.**

<details>

<summary>Native mode instructions</summary>

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
    the last-built live sim persists rather than being lost on closing.

</details>

---
†No warranty given by developer, etc.
