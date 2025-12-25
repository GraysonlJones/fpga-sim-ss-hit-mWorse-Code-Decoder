'''
Currently just sets up a window. Next step is to test
some inter-process connection with this.
'''

import dataclasses as dc

from PySide6.QtCore import Signal, Slot

from qt_util import BoardComponents, EmptyWindow, make_app
from states import InputState, OutputState, WholeInputState, WholeOutputState


class MainWindow(EmptyWindow):
    input_changed = Signal(WholeInputState)
    def __init__(self):
        super().__init__("FPGA board view")

        self.output_state = WholeOutputState(lights=OutputState.Lights(), anode=OutputState.Anode(), cathode=OutputState.Cathode())
        self.input_state = WholeInputState(buttons=InputState.Buttons(), switches=InputState.Switches())

        self.plus_buttons = BoardComponents.Buttons(self.shift_pressed)
        self.four_digits = BoardComponents.FourDigits()
        self.lights_line = BoardComponents.Lights()
        self.switches_line = BoardComponents.Switches()

        self.main_layout.addWidget(self.plus_buttons)
        self.main_layout.addWidget(self.four_digits)
        self.main_layout.addWidget(self.lights_line)
        self.main_layout.addWidget(self.switches_line)

        self.switches_line.state_changed.connect(lambda x: self.update_input_state(switches=x))
        self.plus_buttons.state_changed.connect(lambda x: self.update_input_state(buttons=x))

        self.input_changed.connect(lambda x: print(x))

    @Slot(WholeOutputState)
    def set_output_state(self, new_output_state: WholeOutputState):
        self.lights_line.set_output_state(new_output_state.lights)
        self.four_digits.set_anodes(new_output_state.anode, refresh=False)
        self.four_digits.set_cathodes(new_output_state.cathode, refresh=True)
        self.output_state = dc.replace(new_output_state)

    def update_input_state(self, *, buttons: InputState.Buttons | None = None, switches: InputState.Switches | None = None):
        if buttons is not None:
            self.input_state.buttons = dc.replace(buttons)
        if switches is not None:
            self.input_state.switches = dc.replace(switches)
        self.input_changed.emit(self.input_state)



app = make_app()
window = MainWindow()
app.exec()