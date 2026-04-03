set -e # Quit if step 1 fails
# see Makefile lint_flags definition for some explanation
verilator --lint-only --timing -Werror-NULLPORT -I./user_inputs $COMPILE_FILES
verilator --binary --timing --trace -I./user_inputs $COMPILE_FILES
./obj_dir/Vtb