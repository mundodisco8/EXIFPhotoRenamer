"""Custom Logger

This module aims to help with the boilerplate code required to get a the logger module working with some stylistic
tweaks.

It provides a bunch of formatters and a quick way to add a custom file and/or console formatter

Example:
# from customLogger import EmojiFormatter, configConsoleHandler, configFileHandler, CSVFormatter
# from logging import getLogger, Formatter, INFO
# from time import sleep
# from datetime import date

# # Get a Logger object
# logger = getLogger(__name__)

# # Choose one of the two following options
# # 1. Attach a console logger with the default formatter (colour levels) to the Logger object...
# configConsoleHandler(logger)
# # 2. ... or alternatively, add an EmojiFormatter instance as the formatter, log only INFO and above
# # configConsoleHandler(logger, EmojiFormatter(), INFO)

# # Attach a file logger (without colours) to the Logger object
# today = date.today()
# filename = "my_app_{}.log".format(today.strftime("%Y_%m_%d"))
# # Again, choose one of the following
# # 1. Standard format, no colours, delta timestamps
# # configFileLogger(logger, filename, deltaFormatter())
# # 2. CSV-friendly, just delta timestamps + message
# # configFileLogger(logger, filename, CSVFormatter())
# # 3. Custom thingy: absolute timing, with date and time, time with millis after a ., and date separated from time with
# # a  comma
# absolutetimeFormat = "%(asctime)s.%(msecs)03d, %(message)s"
# configFileLogger(logger, filename, Formatter(fmt=absolutetimeFormat, datefmt="%Y-%m-%d,%H:%M:%S"))

# # Log away...
# logger.debug("MY DEBUG")
# sleep(1)
# logger.info("MY INFO")
# sleep(1)
# logger.warning("MY WARNING")
# sleep(1)
# logger.error("MY ERROR")
# sleep(1)
# logger.critical("MY CRITICAL")

Example 2: log from multiple modules. If a module has its own named logger, you would need to access it to add a handler
to it. The easiest solution (as to not get lost in a sea of dependent submodules and loggers) is to just configure the
root logger

```
from logging import getLogger
import module1 # has a logger, exposed as module_logger
import module2 # has a logger, exposed as module_logger, but also depends on a third module, module3, that has it's own
               # logger

[...]
logger = getLogger(__name__) # create a instance of a logger for this script/module, e.g. named "myScript"
# use getLogger() as the logger instance to reach the root logger
configConsoleHandler(getLogger(), EmojiFormatter(), INFO)
# now myScript, module1, module2 and module3 loggers will print with the right formatter and level

```
"""

from datetime import datetime, timezone
from enum import StrEnum
from logging import (
    CRITICAL,
    DEBUG,
    ERROR,
    INFO,
    NOTSET,
    WARNING,
    FileHandler,
    Formatter,
    Logger,
    LogRecord,
    StreamHandler,
)


class TxtColour(StrEnum):
    """Console Colours Available"""

    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    green = "\x1b[32;20m"
    yellow = "\x1b[33;20m"
    blue = "\x1b[34;20m"
    purple = "\x1b[35;20m"
    cyan = "\x1b[36;20m"
    white = "\x1b[37;20m"
    reset = "\x1b[0m"


DEFAULT_FORMAT: str = "%(delta)s |  %(levelname)8s | %(message)s"

COLOUR_FORMAT_DICT: dict[int, str] = {
    DEBUG: TxtColour.blue + DEFAULT_FORMAT + TxtColour.reset,
    INFO: TxtColour.green + DEFAULT_FORMAT + TxtColour.reset,
    WARNING: TxtColour.yellow + DEFAULT_FORMAT + TxtColour.reset,
    ERROR: TxtColour.red + DEFAULT_FORMAT + TxtColour.reset,
    CRITICAL: TxtColour.bold_red + DEFAULT_FORMAT + TxtColour.reset,
}

EMOJI_FORMAT_DICT: dict[int, str] = {
    DEBUG: "%(delta)s | 🐞 |" + TxtColour.cyan + " %(msg)s" + TxtColour.reset,
    INFO: "%(delta)s | ℹ️ |" + TxtColour.green + " %(msg)s" + TxtColour.reset,  # noqa: RUF001
    WARNING: "%(delta)s | ⚠️ |" + TxtColour.yellow + " %(msg)s" + TxtColour.reset,
    ERROR: "%(delta)s | ⛔ |" + TxtColour.red + " %(msg)s" + TxtColour.reset,
    CRITICAL: "%(delta)s | 🙊 |" + TxtColour.bold_red + " %(msg)s" + TxtColour.reset,
}


class ColourFormatter(Formatter):
    """Logging colored formatter,

    Logs messages with a bit of pop. Each debug level has a different colour. Messages have the following format

    [time delta in HH:MM:SS] | [debug level, right aligned] | message <- All in the level's colour
    """

    def __init__(self):
        """Initialises the class"""
        super().__init__()
        self.FORMATS = COLOUR_FORMAT_DICT

    def format(self, record: LogRecord):
        """Formats a record"""
        # Gets the current "relative since start time" from the record (which is in ms) and transforms it into a
        # datetime object, which is then formatted and stored in the record as an attribute named "delta" (see
        # defaultFormat)
        duration = datetime.fromtimestamp(record.relativeCreated / 1000, timezone.utc)
        record.delta = duration.strftime("%H:%M:%S")
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = Formatter(log_fmt)
        return formatter.format(record)


class EmojiFormatter(Formatter):
    """Logging colored + emoji for levels formatter,

    Logs messages with even more pop. Each debug level has a different colour and level is represented by an emoji.
    Messages have the following format

    [time delta in HH:MM:SS in white] | [debug level, as an emoji] | [message in the level's colour]
    """

    def __init__(self):
        """Initialises the class"""
        super().__init__()
        self.FORMATS = EMOJI_FORMAT_DICT

    def format(self, record: LogRecord) -> str:
        """Formats a record with the emoji format"""
        duration = datetime.fromtimestamp(record.relativeCreated / 1000, timezone.utc)
        record.delta = duration.strftime("%H:%M:%S")
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = Formatter(log_fmt)
        return formatter.format(record)


class DeltaFormatter(Formatter):
    """Logging with delta timming

    Logs events with time relative to the start of the execution of the program

    [time delta in HH:MM:SS] | [debug level, right aligned] | message
    """

    def __init__(self, formatStr: str = DEFAULT_FORMAT):
        """Initialises the class"""
        super().__init__(fmt=formatStr, datefmt="%H:%M:%S", style="%")

    def format(self, record: LogRecord) -> str:
        """Formats a record with using timedeltas as the timing source"""
        duration = datetime.fromtimestamp(record.relativeCreated / 1000, timezone.utc)
        record.delta = duration.strftime("%H:%M:%S")
        formatter = super()
        return formatter.format(record)


class CSVFormatter(Formatter):
    """Logging with delta timming

        Logs events with time relative to the start of the execution of the program

    [time delta in HH:MM:SS] | [debug level, right aligned] | message
    """

    def __init__(self):
        """Initialises the class"""
        super().__init__(fmt="%(delta)s, %(message)s", datefmt="%H:%M:%S", style="%")

    def format(self, record: LogRecord) -> str:
        """Formats a  record with a CSV-friendly format, good for log files"""
        duration = datetime.fromtimestamp(record.relativeCreated / 1000, timezone.utc)
        record.delta = duration.strftime("%H:%M:%S")
        formatter = super()
        return formatter.format(record)


def configConsoleHandler(logger: Logger, formatter: Formatter | None = None, dbgLevel: int = DEBUG) -> None:
    """Configures a logger to print to Console with a custom formatter

    Args:
        logger (Logger): the Logger object we want to attach this console logger handler
        formatter (Formatter): an instance of Formatter, to format the records
        dbgLevel (int): the minimum debug level to log
    """
    if not formatter:
        formatter = ColourFormatter()
    # Set the minimum level of the logger, but only if it's not set, or is set to something higher than the current
    # desired level
    if logger.level == NOTSET or logger.level > dbgLevel:
        logger.setLevel(dbgLevel)
    # Create stdout handler for logging to the console (logs all five levels)
    stdout_handler = StreamHandler()
    stdout_handler.setLevel(dbgLevel)
    stdout_handler.setFormatter(formatter)
    # Add Cosole handler to the logger
    logger.addHandler(stdout_handler)


def configFileHandler(logger: Logger, filename: str, formatter: Formatter | None = None, dbgLevel: int = DEBUG) -> None:
    """Configures a logger to print to Console with a custom formatter

    Args:
        logger (Logger): the Logger object we want to attach this console logger handler
        filename: the name of the file to log to
        formatter (Formatter): an instance of Formatter, to format the records
        dbgLevel (int): the minimum debug level to log
    """
    if not formatter:
        formatter = ColourFormatter()
    # Set the minimum level of the logger, but only if it's not set, or is set to something higher than the current
    # desired level
    if logger.level == NOTSET or logger.level > dbgLevel:
        logger.setLevel(dbgLevel)
    # Create stdout handler for logging to file (logs all five levels)
    # By default, the file will be opened in "append" mode
    file_handler = FileHandler(filename, encoding="UTF-8")
    file_handler.setLevel(dbgLevel)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
