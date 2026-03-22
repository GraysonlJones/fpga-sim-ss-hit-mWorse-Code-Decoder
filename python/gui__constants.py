import dataclasses as dc

from gui__states import OutputState
from PySide6.QtCore import QSize


class Colors:
    class Light:
        on = "#6f3"
        off = "#888"

    class Segment:
        on = "#ff5f6d"
        off = "#fff"
        background = "#ccc"

    class Button:
        class Light:
            pen = "#000"
            on_fill = "#aab"
            off_fill = "#eee"
            focus = "#0082e6"
        class Dark:
            pen ="#fff"
            on_fill = "#112"
            off_fill = "#333"
            focus = "#90cfff"
    
    class Switch:
        class Light:
            bg_fill = "#eee"
            pen = "#000"
            on_fill = "#cce"
            off_fill = "#aaa"
        class Dark:
            bg_fill = "#222"
            pen = "#fff"
            on_fill = "#99b"
            off_fill = "#333"


class Sizes:
    light = QSize(14, 14)
    switch = QSize(14, 28)

    base_light_size = 10
    dp_margin = 8
    dp = QSize(base_light_size, base_light_size)
    horz_light = QSize(base_light_size * 3, base_light_size)
    vert_light = QSize(base_light_size, base_light_size * 3)


class NumberStates:
    all_off = OutputState.Cathode()
    all_on = OutputState.Cathode(*[True] * 7) # 8th arg defaults to false — DP

    number_1 = OutputState.Cathode(CB=True, CC=True)
    number_2 = dc.replace(all_on, CC=False, CF=False)
    number_3 = dc.replace(all_on, CE=False, CF=False)
    number_4 = dc.replace(all_on, CA=False, CD=False, CE=False)
    number_5 = dc.replace(all_on, CB=False, CE=False)
    number_6 = dc.replace(all_on, CB=False)
    number_7 = OutputState.Cathode(CA=True, CB=True, CC=True)
    number_8 = dc.replace(all_on)
    number_9 = dc.replace(all_on, CE=False)
    number_0 = dc.replace(all_on, CG=False)

light_off_time = 100
light_fade_delay_time = 0
segment_off_time = 200
segment_fade_delay_time = 130