################################################################################
# PhotoRenamingSripts.py
###
# This module will contain all the auxiliary functions used on the Photo
# Renaming Scripts
###
################################################################################

from typing import List
from enum import Enum

###
# Coloured console text. Simplicity Studio / Eclipse allows printing with colour,
###

# so spotting errors or warnings is easier (it requires installing the ANSI Console
# plugin). I haven't found a way of doing it in Atmel Studio / VS
# Group of Different functions for different styles

# By adding the str class, BEFORE THE Enum class, we define an Enum with string values!
# If you want to access the members without having to add 'lvl.' before, you can add them
# to the global namespace with
#
# globals().update(lvl.__members__)
#
# But the linter will report them as undefined variables

class lvl(str, Enum):
    """Debug log levels

    The different logging levels and the colours associated to the output
    """
    ERROR = "\x1b[0;31;22m"  # RED + normal mode
    OK = "\x1b[0;32;22m"  # GREEN
    WARNING = "\x1b[0;33;22m"  # YELLOW
    # YELLOW, but I can use in temporary debugs and then delete
    DEBUG = "\x1b[0;33;22m"
    INFO = "\x1b[0;36;22m"  # CYAN
    NORMAL = "\x1b[0;37;22m"  # NORMAL white text
    RESET = "\x1b[0m"       # Reset


def debugPrint(level: lvl, msg: str):
    """Prints coloured text

    Args:
        level: a member of the class lvl, that indicates the level of the messsage
        msg: a string to be printed with the selected colour
    """
    print(level + msg + lvl.RESET)