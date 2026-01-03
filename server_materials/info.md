This is, for now, a "model folder" for what goes on the server

* On the real server, server__manager.py is in this folder with all required
dependencies. It is in the main python folder for development/testing purposes.

* The user_inputs folder is where the server copies Verilog files to.
* Makefile and Makefile_obj.mak are used for compilation
* obj_dir is where Verilator puts executables and generated code
* simulator_driver.cpp is passed every time the build process happens.
It flips the clock every time a message (blank or containing a new
input state) is received. Clock speeds of e.g. 40 MHz like the real FPGA
are unattainable, but, with a fading effect so the lights aren't extremely
flickery, even 60 Hz is fine.