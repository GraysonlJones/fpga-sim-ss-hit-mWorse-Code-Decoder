import dataclasses as dc

from PySide6.QtCore import QSize

from states import OutputState


class Colors:
    class Light:
        on = "#6f3"
        off = "#111"

    class Segment:
        on = "#f00"
        radio_on = "#f77"  # approx color of segment middle due to shading
        off = "#f8fdfd"


class Sizes:
    # Until switches are reskinned, must be this size for checkbox alignment
    light = QSize(14, 14)
    horz_light = QSize(42, 14)
    vert_light = QSize(14, 42)


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
