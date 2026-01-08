import dataclasses as dc
from threading import Event
from typing import Literal, overload, override

import gui__constants as c
from gui__states import InputState, OutputState
from PySide6.QtCore import QSize, Qt, QTimer, Signal, Slot
from PySide6.QtGui import QColor, QKeyEvent, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QGridLayout,
    QHBoxLayout,
    QLayout,
    QMainWindow,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


def choose_number(number: int) -> OutputState.Cathode:
    try:
        number = number % 10 # Cut down to 1 digit
        return getattr(c.NumberStates, f"number_{number}")
    except NameError:
        raise ValueError(f"Invalid number {number} passed to choose_number()")

def set_color(button: QPushButton | QRadioButton, color: str | QColor):
    '''Sets the most relevant color of the given widget using palettes.
    May expand to more widgets at some point eventually.'''

    palette = button.palette() # Copy original palette to modify

    if isinstance(color, str): # Construct QColor if given string
        color = QColor(color)

    match button:
        case QPushButton():
            role = QPalette.ColorRole.Button
        case QRadioButton():
            role = QPalette.ColorRole.Base
        case _:
            raise TypeError(f"set_color() given bad-type widget {button}")

    palette.setColor(role, color) # Modify palette copy
    button.setPalette(palette) # Apply modified palette

class EmptyWindow(QMainWindow):
    def __init__(self, title: str):
        super().__init__()
        self.setWindowTitle(title)

        self.main_layout = QVBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)
        self.show()
        self.shift_pressed = Event()

    @override
    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if key == Qt.Key.Key_Shift:
            self.shift_pressed.set()
    @override
    def keyReleaseEvent(self, event: QKeyEvent):
        key = event.key()
        if key == Qt.Key.Key_Shift:
            self.shift_pressed.clear()

# Narrow type so type checker is happy with vbox/hbox calls
@overload
def __box_factory(*stuff: QLayout | QWidget, vertical: Literal[True], no_margins: bool = True) -> QVBoxLayout: ...
@overload
def __box_factory(*stuff: QLayout | QWidget, vertical: Literal[False], no_margins: bool = True)  -> QHBoxLayout: ...

def __box_factory(*stuff: QLayout | QWidget, vertical: bool, no_margins: bool = True):
    box = QVBoxLayout() if vertical else QHBoxLayout()
    for item in stuff:
        if isinstance(item, QLayout):
            box.addLayout(item)
        elif isinstance(item, QWidget):
            box.addWidget(item)
        else:
            raise TypeError(f"__box_factory() (helper to [vbox|hbox]_factory) passed non-layout/widget {item} of type {type(item)}!")
    if no_margins:
        box.setContentsMargins(0, 0, 0, 0)
    return box

def vbox_factory(*stuff: QLayout | QWidget, no_margins: bool = True) -> QVBoxLayout:
    return __box_factory(*stuff, vertical=True, no_margins=no_margins)

def hbox_factory(*stuff: QLayout | QWidget, no_margins: bool = True) -> QHBoxLayout:
    return __box_factory(*stuff, vertical=False, no_margins=no_margins)

def make_checkbox():
    checkbox = QCheckBox()
    checkbox.setFixedSize(c.Sizes.light)
    return checkbox

def make_push_button():
    push_button = QPushButton()
    push_button.setFixedSize(c.Sizes.light)
    return push_button

def make_app(argv: list[str] = []):
    app = QApplication(argv)
    app.setStyle("fusion")
    return app

# The below four classes are at least for now only used inside BoardComponents.
#  I don't see much use for them in the chrome (except for maybe LightDisplay).
class StickyButton(QPushButton):
    sticky_press = Signal()
    sticky_release = Signal()
    def __init__(self, shift_pressed: Event):
        super().__init__()
        self.setFixedSize(c.Sizes.light)
        self.setCheckable(True)
        self.released.connect(self.maybe_uncheck)
        self.shift_pressed = shift_pressed

        self.pressed.connect(self.handle_press_emit)
        self.toggled.connect(self.handle_release_emit)

    def handle_press_emit(self):
        if not self.isChecked():
            self.sticky_press.emit()

    def handle_release_emit(self, now_checked: bool):
        if not now_checked:
            self.sticky_release.emit()
    
    def maybe_uncheck(self):
        if self.isChecked() and not self.shift_pressed.is_set():
            self.setChecked(False)

class LightDisplay(QPushButton):
    def __init__(self, *,
                size: QSize | None = c.Sizes.light,
                on_color: QColor | str = c.Colors.Light.on,
                off_color: QColor | str = c.Colors.Light.off,
                fade_time: int = c.light_fade_time):
        super().__init__()
        self.light_on = False
        self.setDisabled(True)

        self.on_color = QColor(on_color)
        self.off_color = QColor(off_color)
        set_color(self, self.off_color)
        
        if size is not None:
            self.setFixedSize(size)

        self.off_timer = QTimer(interval=fade_time, singleShot=True)
        self.off_timer.timeout.connect(lambda: set_color(self, self.off_color))

    def set_light(self, light_on: bool):
        if self.light_on != light_on: # Avoid redundant color setting
            self.light_on = light_on
            if self.light_on:
                self.off_timer.stop()
                set_color(self, self.on_color)
            else:
                self.off_timer.start()

# TODO: much redundancy. Probably some way to make a subclass of
#  QAbstractButton both of these classes multiple-inherit from?
#  But ideally these will eventually not be button subclasses anyway.
class CircleLightDisplay(QRadioButton):
    def __init__(self, *,
                on_color: QColor | str = c.Colors.Light.on,
                off_color: QColor | str = c.Colors.Light.off,
                fade_time: int = c.light_fade_time):
        super().__init__()
        self.light_on = False
        self.setDisabled(True)

        self.on_color = QColor(on_color)
        self.off_color = QColor(off_color)
        set_color(self, self.off_color)

        self.off_timer = QTimer(interval=fade_time, singleShot=True)
        self.off_timer.timeout.connect(lambda: set_color(self, self.off_color))
        # Intentionally lacks size parameter. Radio buttons just crop if given
        #  smaller size and do not expand with a larger one

    def set_light(self, light_on: bool):
        if self.light_on != light_on:
            self.light_on = light_on
            if self.light_on:
                self.off_timer.stop()
                set_color(self, self.on_color)
            else:
                self.off_timer.start()


#   AAAA
#  F    B
#   GGGG
#  E    C
#   DDDD

class SevenSegmentLight:
    def __init__(self):
        super().__init__()
        self.layout = QGridLayout()

        self.CA = LightDisplay(size=c.Sizes.horz_light, on_color=c.Colors.Segment.on, off_color=c.Colors.Segment.off, fade_time=c.segment_fade_time)
        self.CB = LightDisplay(size=c.Sizes.vert_light, on_color=c.Colors.Segment.on, off_color=c.Colors.Segment.off, fade_time=c.segment_fade_time)
        self.CC = LightDisplay(size=c.Sizes.vert_light, on_color=c.Colors.Segment.on, off_color=c.Colors.Segment.off, fade_time=c.segment_fade_time)
        self.CD = LightDisplay(size=c.Sizes.horz_light, on_color=c.Colors.Segment.on, off_color=c.Colors.Segment.off, fade_time=c.segment_fade_time)
        self.CE = LightDisplay(size=c.Sizes.vert_light, on_color=c.Colors.Segment.on, off_color=c.Colors.Segment.off, fade_time=c.segment_fade_time)
        self.CF = LightDisplay(size=c.Sizes.vert_light, on_color=c.Colors.Segment.on, off_color=c.Colors.Segment.off, fade_time=c.segment_fade_time)
        self.CG = LightDisplay(size=c.Sizes.horz_light, on_color=c.Colors.Segment.on, off_color=c.Colors.Segment.off, fade_time=c.segment_fade_time)
        self.DP = CircleLightDisplay(on_color=c.Colors.Segment.radio_on, off_color=c.Colors.Segment.off, fade_time=c.segment_fade_time)

        self.layout.addWidget(self.CA, 0, 1) # horizontal bits
        self.layout.addWidget(self.CG, 2, 1)
        self.layout.addWidget(self.CD, 4, 1)
        self.layout.addWidget(self.CF, 1, 0) # left edge
        self.layout.addWidget(self.CE, 3, 0)
        self.layout.addWidget(self.CB, 1, 2) # right edge
        self.layout.addWidget(self.CC, 3, 2)
        self.layout.addWidget(self.DP, 4, 3) # dot

        self.layout.addItem(QSpacerItem(10, 0, QSizePolicy.Policy.Fixed), 4, 4)

        self.light_on = False
        self.current_setting = dc.replace(c.NumberStates.all_off)

    def set_lights(self, new_lights: OutputState.Cathode):
        for target, setting in dc.asdict(new_lights).items():
            light: LightDisplay | CircleLightDisplay = getattr(self, target)
            light.set_light(setting)
        self.current_setting = dc.replace(new_lights)

class BoardComponents:
    class FourDigits(QWidget):
        state_changed = Signal(OutputState.Anode, OutputState.Cathode)
        def __init__(self):
            super().__init__()
            self.digits = [SevenSegmentLight() for _ in range(4)]
            self.current_anodes = OutputState.Anode()
            self.current_pattern = dc.replace(c.NumberStates.all_off)

            self.layout_hook = hbox_factory(*[digit.layout for digit in self.digits])
            self.layout_hook.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding))
            self.setLayout(self.layout_hook)

        @Slot(OutputState.Anode)
        def set_anodes(self, new_anodes: OutputState.Anode, *, refresh: bool): 
            self.current_anodes = dc.replace(new_anodes)
            if refresh:
                self._refresh()

        @Slot(OutputState.Cathode)
        def set_cathodes(self, new_lights: OutputState.Cathode, *, refresh: bool): 
            self.current_pattern = dc.replace(new_lights) # Inverted from active low on server side
            if refresh:
                self._refresh()

        def _refresh(self):
            for anode, digit in zip(dc.astuple(self.current_anodes), self.digits):
                if anode: # Board is active low but inversion happens on server side
                    digit.set_lights(self.current_pattern)
                else:
                    digit.set_lights(c.NumberStates.all_off)
            self.state_changed.emit(self.current_anodes, self.current_pattern)

    class Switches(QWidget):
        state_changed = Signal(InputState.Switches)
        def __init__(self):
            super().__init__()
            self.checkboxes = [make_checkbox() for _ in range(0, 16)]
            layout_hook = hbox_factory(*self.checkboxes, no_margins=True)

            layout_hook.addItem(QSpacerItem(10, 0, QSizePolicy.Policy.Expanding))
            self.setLayout(layout_hook)

            for checkbox in self.checkboxes:
                checkbox.toggled.connect(lambda: self.state_changed.emit(self.__get_input_state()))

        @Slot(InputState.Switches)
        def set_input_state(self, new_state: InputState.Switches):
            # Block the 16 auto-emits and do a manual emit with new state
            self.blockSignals(True)
            for state, checkbox in zip(dc.astuple(new_state), self.checkboxes):
                checkbox.setChecked(state)
            self.blockSignals(False)
            self.state_changed.emit(self.__get_input_state())

        def __get_input_state(self) -> InputState.Switches:
            return InputState.Switches(*[checkbox.isChecked() for checkbox in self.checkboxes])

    class Lights(QWidget):
        state_changed = Signal(OutputState.Lights)
        def __init__(self):
            super().__init__()
            self.lights = [LightDisplay() for _ in range(0, 16)]
            layout_hook = hbox_factory(*self.lights, no_margins=True)
            layout_hook.addItem(QSpacerItem(10, 0, QSizePolicy.Policy.Expanding))
            self.setLayout(layout_hook)
        
        @Slot(OutputState.Lights)
        def set_output_state(self, new_state: OutputState.Lights):
            for state, light in zip(dc.astuple(new_state), self.lights):
                light.set_light(state)
            self.state_changed.emit(self.__get_output_state())
        
        def __get_output_state(self) -> OutputState.Lights:
            return OutputState.Lights(*[light.light_on for light in self.lights])

    class Buttons(QWidget):
        state_changed = Signal(InputState.Buttons)
        def __init__(self, shift_pressed: Event) -> None:
            super().__init__()
            layout_hook = QGridLayout()
            self.setLayout(layout_hook)

            self.BTNU = StickyButton(shift_pressed)
            self.BTND = StickyButton(shift_pressed)
            self.BTNL = StickyButton(shift_pressed)
            self.BTNR = StickyButton(shift_pressed)
            self.BTNC = StickyButton(shift_pressed)

            self.buttons_list = [self.BTNU, self.BTND, self.BTNL, self.BTNR, self.BTNC]

            for button in self.buttons_list:
                button.sticky_press.connect(lambda b=button: self.state_changed.emit(self.get_input_state(b)))
                button.sticky_release.connect(lambda: self.state_changed.emit(self.get_input_state()))

            layout_hook.addWidget(self.BTNU, 0, 1)
            layout_hook.addWidget(self.BTND, 2, 1)
            layout_hook.addWidget(self.BTNL, 1, 0)
            layout_hook.addWidget(self.BTNR, 1, 2)
            layout_hook.addWidget(self.BTNC, 1, 1)
            layout_hook.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding), 0, 3)

        def get_input_state(self, button: StickyButton | None = None) :
            output_list = [b.isChecked() if b is not button else True for b in self.buttons_list]
            return InputState.Buttons(*output_list)