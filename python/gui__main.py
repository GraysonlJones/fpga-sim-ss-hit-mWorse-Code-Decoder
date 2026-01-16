'''
Start with run_app call
'''

import dataclasses as dc
import socket
import threading
import time
from statistics import mean

from gui__qt_util import BoardComponents, EmptyWindow, make_app
from gui__states import InputState, OutputState, WholeInputState, WholeOutputState
from PySide6.QtCore import QTimer, Signal, Slot
from PySide6.QtWidgets import QApplication, QLabel, QPushButton
from shared__util import (
    big_receive,
    deserialize_dataclass,
    send_message,
    serialize_dataclass,
)


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

        self.quit_button = QPushButton("Quit!")
        self.quit_button.pressed.connect(self.ready_quit)

        self.main_layout.addWidget(self.quit_button)

        self.paused = False

        self.pause_play_button = QPushButton("Pause")
        self.pause_play_button.pressed.connect(self.pause_play)

        self.main_layout.addWidget(self.pause_play_button)


        self.switches_line.state_changed.connect(lambda x: self.update_input_state(switches=x))
        self.plus_buttons.state_changed.connect(lambda x: self.update_input_state(buttons=x))

        self.latest: None | WholeInputState = None

        self.should_quit = False

        self.input_changed.connect(self.update_latest)
        self.output_changed.connect(self.set_output_state)
        self.close_signal.connect(self.quit_program)

        self.update_timer = QTimer(interval=17)
        self.update_timer.timeout.connect(self.update_server)
        self.update_timer.start()

        self.last_few_fps: list[float] = []
        self.last_time = time.time()
        self.fps_counter = QLabel("__.__/60 FPS")
        self.main_layout.addWidget(self.fps_counter)

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
    
    def ready_quit(self):
        self.should_quit = True

    @Slot()
    def quit_program(self):
        # print("Quitting")
        # print("Fetching app instance")
        app: QApplication = QApplication.instance() # pyright: ignore[reportAssignmentType]
        # print("Closing window")
        self.close()
        # print("Closing app")
        app.exit()
        print("Closed app")

    def update_server(self):
        if not self.should_quit:
            if not self.paused:
                if self.latest is not None:
                    send_message(serialize_dataclass(self.latest), self.sock)
                    self.latest = None
                else:
                    send_message("", self.sock)
                new_time = time.time()

                self.last_few_fps.append(1/(new_time - self.last_time))
                if len(self.last_few_fps) == 10:
                    self.fps_counter.setText(f"<code>{mean(self.last_few_fps):.2f}/60</code> FPS")
                    self.last_few_fps.clear()
                self.last_time = new_time
            else:
                self.fps_counter.setText(f"<code>__.__/60</code> FPS (paused)")
                self.last_few_fps.clear() # While paused, times are meaningless
                self.last_time = time.time()
        else:
            self.update_timer.stop()
            send_message("exit", self.sock)


    def update_latest(self, new_latest: WholeInputState):
        self.latest = new_latest

    def pause_play(self):
        self.paused = not self.paused
        if self.paused:
            self.pause_play_button.setText("Play")
        else:
            self.pause_play_button.setText("Pause")


def listen(window: MainWindow):
    sock = window.sock
    while True:
        response = big_receive(sock).decode()

        if response == "exit":
            # print(f"{response}: time to exit")
            break
        else:
            # print(f"received: {response}")
            output_state = deserialize_dataclass(response, WholeOutputState)
            # TODO: add some kind of like, blinking indicator every time we get a new state to indicate that things aren't frozen?
            window.output_changed.emit(output_state)
    # print("Telling app to close")
    window.close_signal.emit()

def run_app(sock: socket.socket, app: QApplication | None):
    if app is None:
        app = make_app()
        print("Spawned a new QApplication")
    else:
        print("Reusing app")
    window = MainWindow(sock)
    window.raise_() # Put window on front. Necessary when reusing app
    app.exec()
    return app