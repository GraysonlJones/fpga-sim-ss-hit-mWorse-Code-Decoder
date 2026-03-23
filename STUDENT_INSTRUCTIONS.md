# Student instructions

[Link back to README](README.md)

These instructions go over the basics of using a terminal, a very useful and
important skill (and not extremely complicated). Please read them
thoroughly and **don't just ask an LLM how to do all of this stuff!**

Do not miss [the section about CPU architectures](#identifying-processor-architecture),
which is required information to select the correct software downloads.

## What is a terminal?

```sh
Last login: Mon Nov 11 05:58:34 on ttys000
gompei@goatbook ~ >
```

A terminal emulator application provides a text-based command-line interface.
Each operating system has a different name for its terminal, though they are
fundamentally quite similar:

* **MacOS**: use the Terminal app, which runs Zsh by default.
* **Windows**: use Windows Terminal (built-in in Windows 11, and [available on
Windows 10](https://apps.microsoft.com/detail/9n0dx20hk701)), and make sure
PowerShell is the selected mode.
If you for some reason cannot use it, the regular PowerShell app has the same
core functionality.
    * Note that PowerShell is internally quite different from Bash and Zsh, but
    its aliases make it compatible to the extent it is used here.
* **Linux**: use whatever the built-in is. The name varies by desktop environment,
though almost any will internally use Zsh or Bash. <kbd>ctrl</kbd>-<kbd>alt</kbd>-<kbd>T</kbd> will open
the terminal on many distributions.
    * Some information here may be inaccurate on Linux.

## Using the terminal

Typing a line in and then pressing enter prompts the computer to parse your
input into a program name and a list of arguments separated by spaces.
Multi-word arguments can be entered by wrapping in single-quotes, escaping
inner single-quotes with `\'`
(e.g. `'Gompei\'s house'` parses to `Gompei's house`).

Terminal emulators provide, among other capabilities, history and
autocompletion. Pressing up/down on the keyboard cycles through previously-run
commands and puts them unentered on the current line. Pressing tab/shift-tab
while partway through typing the name of a command or file cycles through
suggestions. To clear the current line, press <kbd>ctrl</kbd>-<kbd>U</kbd> on
Mac/Linux, or escape on PowerShell. On Mac, press <kbd>cmd</kbd>-<kbd>K</kbd>
to clear previous lines, or run the `clear` command on the other terminals.

When a line is entered, the terminal runs the named program, giving it access to
all the user arguments, and prints its output as it runs.

For example, if you have a command on your computer with this format:

```
tell_time [-twentyfourhour] <place>
```

You could run it like `tell_time 'Bismarck, ND"'` and get back
`02:30:53 p.m.`, or run it as `tell_time -twentyfourhour 'Bismarck, ND'` to
get `14:30:53`.

### Basic terminal commands

The terminal always has a "working directory" (directory is a synonym for folder).
For example, when you open it, your emulator likely starts in `~`, which is
an alias for your current user's "home directory". Relative filepaths are always
from the working directory; `.` is an alias for it, while `..` is an alias for
its parent.

Terminals provide a set of built-in commands (e.g. `cd`) and OS-provided
utilities (e.g. `open`), which are accessible regardless of your current working
directory. There are a large number
(e.g. see a [list of Linux's Bash builtins and utilities](https://ss64.com/bash/)),
but here is a list of some key ones, which all have PowerShell aliases, and
should cover what you need to use this program:

#### ls
`ls` lists the files in the current working directory. For example, in `~`,
you could see:

```
Applications
Desktop
Documents
Downloads
Public
```

#### cd \<folder name>
`cd` changes your working directory to the provided location. You can use
absolute or relative paths.
Continuing the example for `ls`, from the `~` home folder you can switch to Documents in multiple ways:
* `cd ./Documents`
* `cd ~/Documents`
* `cd ../../Users/gompei/Documents`

#### pwd
`pwd` ("print working directory") prints the current working directory's
absolute filepath (starting with a `/`, which indicates the "root" of the
filesystem).

#### mkdir \<new folder name\>
`mkdir` ("make directory") makes a new directory of a given name. For example,
`mkdir 'Gompei\'s homework'`.

#### touch \<new filename\>
`touch` makes a new file of a given name. For example,
`touch 'Gompei\'s homework/paper_1.tex'`.

#### cat \<filename\>
`cat` ("concatenate" — see [cat (Unix) on Wikipedia](https://en.wikipedia.org/wiki/Cat_(Unix)))
prints the contents of a file to the screen. E.g. `cat ./info.txt`.

#### sudo \<command\>
`sudo` ("[super user](https://en.wikipedia.org/wiki/Superuser) do") prompts for
your password then executes a single command with the root user's full
permissions, similarly to "run as administrator" in Windows Explorer.
This is necessary for some modifications to your computer's settings.
The inner command receives its arguments as if "sudo" were not in front of it.

#### man \<command name\>
`man` opens (generally internally using the LESS viewer) a help page for a
given command.
Scroll with the arrow keys/scroll wheel and exit with <kbd>q</kbd>.

#### open \<filename\>
`open` does what it sounds like: it opens a given file or folder in the relevant
program. For example, `open ~/Documents` would open the file browser, while
`open info.txt` might open a text editor. Note that PowerShell equivalent
is `start`, and on Linux this is just a common alias so you might need to
run it as `xdg-open`.

#### rm
`rm` (remove) deletes a file without putting it in the trash, e.g. `rm ECE_sux.html`.
It can delete folders with `rm -r <name>` (`-r` meaning recursive).
**Be careful with this one!**

There is a ton more to the terminal but you should be good to go from here for
the setup of the simulator if you follow those instructions closely.


## Identifying processor architecture
Every computer's CPU has a specific instruction set architecture (ISA).
Some of the required software needs you to select the correct version.
This software supports two architectures. I know the naming conventions are
confusing but it's just something you need to get used to:
   - **x86-64**, a.k.a. AMD64, x64, x86, x86_64, or Intel.
   - **AArch64**, a.k.a. ARM64, ARM, or (Mac-only) Apple Silicon.

How to identify, by OS:
- Mac: any Mac from the M1 on, released late 2020, is ARM, while older Macs
(back to 2006) are Intel.
    - Run `arch` in Terminal to check
- Windows: the vast majority of Windows PCs are x86. Some laptops are ARM,
almost all of which have Snapdragon chips.
    - Run the below command to check. Output will be `ARM 64-bit Processor`
    if on ARM, or `64-bit` if on x86.
```
(Get-CimInstance Win32_operatingsystem).OSArchitecture
```
- Linux: If you are on Linux, you *probably* know your architecture, but check
with `uname -m` in your terminal if unsure.