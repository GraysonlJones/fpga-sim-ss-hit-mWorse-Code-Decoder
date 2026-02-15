set -e # Quit if step 1 fails
verilator --binary --timing --trace -I./user_inputs $COMPILE_FILES
./obj_dir/Vtb