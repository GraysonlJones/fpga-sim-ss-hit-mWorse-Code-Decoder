from pathlib import Path

top_folder = Path(__file__).resolve().parent.parent  # i.e. fpga-sim/
waveforms_folder = top_folder.joinpath("waveforms")  # fpga-sim/waveforms/
verilog_folder = top_folder.joinpath("verilog")  # fpga-sim/verilog/
live_sim_folder = verilog_folder.joinpath("live_sim")
testbench_folder = verilog_folder.joinpath("testbench")
