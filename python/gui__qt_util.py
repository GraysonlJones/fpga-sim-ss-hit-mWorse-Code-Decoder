import dataclasses as dc
from threading import Event
from typing import Literal, overload, override

import gui__constants as c
from gui__states import InputState, OutputState
from PySide6.QtCore import (
    Property,
    QPropertyAnimation,
    QRect,
    QSequentialAnimationGroup,
    QSize,
    Qt,
    QTimer,
    Signal,
    Slot,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QGuiApplication,
    QKeyEvent,
    QPainter,
    QPalette,
    QPen,
)
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QGridLayout,
    QHBoxLayout,
    QLayout,
    QMainWindow,
    QProxyStyle,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QSpacerItem,
    QStyle,
    QStyleOption,
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

def mix_colors(color1: QColor, color2: QColor):
    # Finds the "middle color" of two colors through simple averaging.
    # Not perception adjusted or anything.
    return QColor(round(color1.red()/2 + color2.red()/2), round(color1.green()/2 + color2.green()/2), round(color1.blue()/2 + color2.blue()/2))

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

class AppStyle(QProxyStyle):
    '''Applied to checkboxes in `make_switch_checkbox()` to make them look like
    vertical binary switches.'''
    def __init__(self) -> None:
        super().__init__("fusion")

    @override
    def pixelMetric(self, metric, option=None, widget=None):
        match metric: # modify size of checkboxes
            case QStyle.PixelMetric.PM_IndicatorWidth:
                return c.Sizes.switch.width()
            case QStyle.PixelMetric.PM_IndicatorHeight:
                return c.Sizes.switch.height()

        return super().pixelMetric(metric, option, widget)

    @override
    def drawPrimitive(self, element: QStyle.PrimitiveElement, option: QStyleOption, painter: QPainter, widget: QWidget | None = None):
        match element:
            case QStyle.PrimitiveElement.PE_FrameFocusRect if isinstance(widget, SwitchCheckbox):
                pass # don't dim checkboxes
            case QStyle.PrimitiveElement.PE_IndicatorCheckBox if isinstance(widget, SwitchCheckbox):
                # to vary for dark mode use this to check:
                if QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Light:
                    back_brush = QBrush("#eee")
                    pen = QPen("#000")
                    on_brush = QBrush("#cce")
                    off_brush = QBrush("#aaa")
                else:
                    back_brush = QBrush("#111")
                    pen = QPen("#fff")
                    on_brush = QBrush("#99b")
                    off_brush = QBrush("#333")

                pen.setWidthF(.5)
                painter.setPen(pen)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)

                bg_rect = QRect(1, 1, c.Sizes.switch.width() - 2, c.Sizes.switch.height() - 2)

                # move top box up or down and color depending on state
                if option.state & QStyle.StateFlag.State_On: # state seems to be missing from type hints
                    indicator_rect = QRect(3, 3, c.Sizes.switch.width() - 6, c.Sizes.switch.width() - 6)
                    front_brush = on_brush
                else:
                    indicator_rect = QRect(3, 3 + c.Sizes.switch.height() - c.Sizes.switch.width(), c.Sizes.switch.width() - 6, c.Sizes.switch.width() - 6)
                    front_brush = off_brush

                if option.state & QStyle.StateFlag.State_HasFocus:
                    painter.setPen(QPen("#3ea0ec"))

                painter.setBrush(back_brush)
                painter.drawRoundedRect(bg_rect, 1, 1)
                painter.setPen(pen)
                painter.setBrush(front_brush)
                painter.drawRoundedRect(indicator_rect, 1, 1)
            case _:
                super().drawPrimitive(element, option, painter, widget)
    
    @override
    def drawControl(self, element: QStyle.ControlElement, option: QStyleOption, painter: QPainter, /, widget: QWidget | None = ...) -> None:
        match element:
            case QStyle.ControlElement.CE_PushButton if isinstance(widget, StickyButton):
                pen = QPen()
                pen.setWidthF(.5)

                # Light mode: black outline; bright when off; somewhat darker pale blue when on
                if QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Light:
                    pen.setColor("#000")
                    on_brush = QBrush("#cce")
                    off_brush = QBrush("#eee")
                # Dark mode: white outline; dark when off; brighter pale blue when on
                else:
                    pen.setColor("#fff")
                    on_brush = QBrush("#99b")
                    off_brush = QBrush("#333")

                # unlike natural Qt buttons, our buttons are down on click.
                #   so draw using union of that and whether they are checked
                is_pressed_in = widget.isDown() or (option.state & QStyle.StateFlag.State_On)

                if is_pressed_in:
                    brush_to_use = on_brush
                else:
                    brush_to_use = off_brush

                # must draw focus indicator ourself — just make outline blue
                if option.state & QStyle.StateFlag.State_HasFocus:
                    if QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Light:
                        pen.setColor("#3ea0ec")
                    else: # brighter color for dark mode
                        pen.setColor("#90cfff")
                        if is_pressed_in: # very hard to see focus around blue buttons so make pen wider
                            pen.setWidthF(1.1)

                # bounding box is 14 x 14 but use 1 less on each side to do rounded square
                bg_rect = QRect(1, 1, 12, 12)

                painter.setPen(pen)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)

                painter.setBrush(brush_to_use)
                painter.drawRoundedRect(bg_rect, 1, 1)
            case _:
                super().drawControl(element, option, painter, widget)

def make_app(argv: list[str] = []):
    app = QApplication(argv)
    app.setStyle(AppStyle())
    return app

# The below classes are used inside BoardComponents.

class SwitchCheckbox(QCheckBox):
    '''Checkbox that has the appearance of a vertical on/off switch, if
    style is applied'''
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(c.Sizes.switch)

class StickyButton(QPushButton):
    '''Button with somewhat custom style that stays down if shift is held when
    released. Style is overridden in AppStyle, mainly because the default's
    state is quite hard to read in dark mode on both Mac and Windows 11.'''
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
    '''Misused QPushButton used to emulate a light with a fade effect.'''
    def __init__(self, *,
                size: QSize | None = c.Sizes.light,
                on_color: QColor | str = c.Colors.Light.on,
                off_color: QColor | str = c.Colors.Light.off,
                off_time: int = c.light_off_time,
                fade_delay_time: int = c.light_fade_delay_time,
                fade_on: bool = True):
        super().__init__()

        self.on_color = QColor(on_color)
        self.off_color = QColor(off_color)
        self.light_on = False
        self.setDisabled(True)
        set_color(self, self.off_color)
        
        if size is not None:
            self.setFixedSize(size)

        self._bg_color = self.on_color

        # TODO: maybe dynamically modify animations so start value matches
        # current value. But this is really not a big deal!!
        self.off_animation = QSequentialAnimationGroup()
        self.off_animation.insertPause(0, fade_delay_time)
        off_fade = QPropertyAnimation(self, b"bg_color")
        off_fade.setStartValue(self.on_color)
        off_fade.setEndValue(self.off_color)
        off_fade.setDuration(off_time - fade_delay_time)
        self.off_animation.addAnimation(off_fade)

        self.fade_on = fade_on

        if fade_on:
            # no fade delay
            self.on_animation = QPropertyAnimation(self, b"bg_color")
            self.on_animation.setStartValue(self.off_color)
            self.on_animation.setEndValue(self.on_color)
            self.on_animation.setDuration(off_time//2)

    def set_light(self, light_on: bool):
        if self.light_on != light_on: # Avoid redundant color setting
            self.light_on = light_on
            if self.light_on:
                self.off_animation.stop()
                if self.fade_on:
                    self.on_animation.start()
                else:
                    set_color(self, self.on_color)
            else:
                if self.fade_on:
                    self.on_animation.stop()
                self.off_animation.start()

    @Property(QColor)
    def bg_color(self):
        return self._bg_color
    
    @bg_color.setter
    def bg_color(self, val: QColor):
        self._bg_color = val
        
        palette = self.palette() # Copy original palette to modify
        palette.setColor(QPalette.ColorRole.Button, val) # Modify palette copy
        self.setPalette(palette) # Apply modified palette

# TODO: much redundancy. Probably some way to make a subclass of
#  QAbstractButton both of these classes multiple-inherit from?
#  But ideally these will eventually not be button subclasses anyway.
class CircleLightDisplay(QRadioButton):
    '''Like LightDisplay but with a QRadioButton to be circular. Currently
    just using squares for this purpose to  and might get rid of this.'''
    def __init__(self, *,
                on_color: QColor | str = c.Colors.Light.on,
                off_color: QColor | str = c.Colors.Light.off,
                off_time: int = c.segment_off_time,
                fade_delay_time: int = c.segment_fade_delay_time):
        super().__init__()
        self.light_on = False
        self.setDisabled(True)

        self.on_color = QColor(on_color)
        self.off_color = QColor(off_color)
        set_color(self, self.off_color)

        self.off_timer = QTimer(interval=off_time, singleShot=True)
        self.off_timer.timeout.connect(lambda: set_color(self, self.off_color))
        self.fade_timer = QTimer(interval=fade_delay_time, singleShot=True)
        self.fade_timer.timeout.connect(lambda: set_color(self, mix_colors(self.on_color, self.off_color)))

        # Intentionally lacks size parameter. Radio buttons just crop if given
        #  smaller size and do not expand with a larger one

    def set_light(self, light_on: bool):
        if self.light_on != light_on:
            self.light_on = light_on
            if self.light_on:
                self.fade_timer.stop()
                self.off_timer.stop()
                set_color(self, self.on_color)
            else:
                self.fade_timer.start()
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

        self.CA = LightDisplay(size=c.Sizes.horz_light, on_color=c.Colors.Segment.on, off_color=c.Colors.Segment.off, fade_delay_time=c.segment_fade_delay_time, off_time=c.segment_off_time, fade_on=False)
        self.CB = LightDisplay(size=c.Sizes.vert_light, on_color=c.Colors.Segment.on, off_color=c.Colors.Segment.off, fade_delay_time=c.segment_fade_delay_time, off_time=c.segment_off_time, fade_on=False)
        self.CC = LightDisplay(size=c.Sizes.vert_light, on_color=c.Colors.Segment.on, off_color=c.Colors.Segment.off, fade_delay_time=c.segment_fade_delay_time, off_time=c.segment_off_time, fade_on=False)
        self.CD = LightDisplay(size=c.Sizes.horz_light, on_color=c.Colors.Segment.on, off_color=c.Colors.Segment.off, fade_delay_time=c.segment_fade_delay_time, off_time=c.segment_off_time, fade_on=False)
        self.CE = LightDisplay(size=c.Sizes.vert_light, on_color=c.Colors.Segment.on, off_color=c.Colors.Segment.off, fade_delay_time=c.segment_fade_delay_time, off_time=c.segment_off_time, fade_on=False)
        self.CF = LightDisplay(size=c.Sizes.vert_light, on_color=c.Colors.Segment.on, off_color=c.Colors.Segment.off, fade_delay_time=c.segment_fade_delay_time, off_time=c.segment_off_time, fade_on=False)
        self.CG = LightDisplay(size=c.Sizes.horz_light, on_color=c.Colors.Segment.on, off_color=c.Colors.Segment.off, fade_delay_time=c.segment_fade_delay_time, off_time=c.segment_off_time, fade_on=False)
        # TODO: temporarily replaced with square to get matching fade effect.
        self.DP = LightDisplay(size=c.Sizes.light, on_color=c.Colors.Segment.on, off_color=c.Colors.Segment.off, fade_delay_time=c.segment_fade_delay_time, off_time=c.segment_off_time, fade_on=False)

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
            self.checkboxes = [SwitchCheckbox() for _ in range(0, 16)]
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
            layout_hook.addWidget(self.BTNL, 1, 0)
            layout_hook.addWidget(self.BTNC, 1, 1)
            layout_hook.addWidget(self.BTNR, 1, 2)
            layout_hook.addWidget(self.BTND, 2, 1)
            layout_hook.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding), 0, 3)

        def get_input_state(self, button: StickyButton | None = None) :
            output_list = [b.isChecked() if b is not button else True for b in self.buttons_list]
            return InputState.Buttons(*output_list)