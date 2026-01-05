set -e # Quit if step 1 fails
verilator --binary --timing --trace $COMPILE_FILES
./obj_dir/Vtb