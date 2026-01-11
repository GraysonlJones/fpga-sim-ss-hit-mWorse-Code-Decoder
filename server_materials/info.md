This folder contains non-Python files copied into the server by the Dockerfile:

* `simulator_driver.cpp` is linked with compiled live simulator designs.
It has a loop of reading stdin for either an empty line or a Python dict string
representing a new input state, running a frame of simulation, and printing the
new output state in Python dict string format to stdout. Every frame it flips
the main clock.

* `Makefile` (and `Makefile_obj`), based on a passed environment variable,
compiles a live simulation executable.

* `Waveform_Run.sh`, using the same environment variable format as the makefile,
compiles a testbench design and runs it. Saving of output to a file is triggered
by a call in the user-provided testbench. 