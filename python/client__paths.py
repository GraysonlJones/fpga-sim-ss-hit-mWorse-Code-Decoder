from pathlib import Path

top_folder = Path(__file__).resolve().parent.parent # i.e. fpga-sim/
waveforms_folder = top_folder.joinpath("waveforms") # fpga-sim/waveforms/