'''
Declares state classes. Dependency of constants but of course not a constant
so I put this at the very top. TODO: Probably not the best way to lay it out.
'''

import dataclasses as dc
from dataclasses import dataclass


# Just for plus button state display
def bool_to_char(inp: bool):
    return "x" if inp == True else "."

class InputState:
    @dataclass
    class Buttons:
        BTNU: bool = False
        BTND: bool = False
        BTNL: bool = False
        BTNR: bool = False
        BTNC: bool = False

        def pretty(self):
            top = f" {bool_to_char(self.BTNU)} "
            middle = f"{bool_to_char(self.BTNL)}{bool_to_char(self.BTNC)}{bool_to_char(self.BTNR)}"
            bottom = f" {bool_to_char(self.BTND)} "
            return f"{top}\n{middle}\n{bottom}" 

    @dataclass
    class Switches:
        SW0: bool = False
        SW1: bool = False
        SW2: bool = False
        SW3: bool = False
        SW4: bool = False
        SW5: bool = False
        SW6: bool = False
        SW7: bool = False
        SW8: bool = False
        SW9: bool = False
        SW10: bool = False
        SW11: bool = False
        SW12: bool = False
        SW13: bool = False
        SW14: bool = False
        SW15: bool = False

class OutputState:
    @dataclass
    class Anode:
        AN0: bool = False
        AN1: bool = False
        AN2: bool = False
        AN3: bool = False

    @dataclass
    class Cathode:
        CA: bool = False
        CB: bool = False
        CC: bool = False
        CD: bool = False
        CE: bool = False
        CF: bool = False
        CG: bool = False
        DP: bool = False

    @dataclass
    class Lights:
        LD0: bool = False
        LD1: bool = False
        LD2: bool = False
        LD3: bool = False
        LD4: bool = False
        LD5: bool = False
        LD6: bool = False
        LD7: bool = False
        LD8: bool = False
        LD9: bool = False
        LD10: bool = False
        LD11: bool = False
        LD12: bool = False
        LD13: bool = False
        LD14: bool = False
        LD15: bool = False

@dataclass
class WholeInputState:
    buttons: InputState.Buttons
    switches: InputState.Switches

@dataclass
class WholeOutputState:
    lights: OutputState.Lights
    anode: OutputState.Anode
    cathode: OutputState.Cathode