'''
Start with run_app call
'''

import dataclasses as dc
import socket
import threading

import gui__constants as c
from gui__qt_util import BoardComponents, EmptyWindow, make_app
from gui__states import InputState, OutputState, WholeInputState, WholeOutputState
from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QApplication
from shared__util import big_receive, deserialize_dataclass


class MainWindow(EmptyWindow):
    input_changed = Signal(WholeInputState)
    output_changed = Signal(WholeOutputState)
    close_signal = Signal()
    def __init__(self, sock: socket.socket):
        super().__init__("FPGA board view")
        self.sock = sock

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
        self.output_changed.connect(self.set_output_state)
        self.close_signal.connect(self.quit_program)

        t = threading.Thread(target=lambda: listen(self), daemon=True)
        t.start()

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

    @Slot()
    def quit_program(self):
        # print("Fetching app instance")
        app: QApplication = QApplication.instance() # pyright: ignore[reportAssignmentType]
        # print("Closing window")
        self.close()
        # print("Closing app")
        app.exit()
        # print("Closed app")

def listen(window: MainWindow):
    sock = window.sock
    while True:
        response = big_receive(sock).decode()

        if response == "exit":
            print("Server sent exit")
            break
        else:
            print(f"received: {response}")
            output_state = deserialize_dataclass(response, WholeOutputState)
            print(output_state)
            window.output_changed.emit(output_state)
    print("Telling app to close")
    window.close_signal.emit()
    # On return, run_app() returns and client resumes shell loop

def run_app(sock: socket.socket, app: QApplication | None):
    if app is None:
        app = make_app()
    window = MainWindow(sock)
    app.exec()
    return app