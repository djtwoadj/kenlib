"""Development support, Logging"""

import datetime
import time
import sys
from pathlib import Path
from dataclasses import dataclass

import kenlib.config_utils as cu




# log messages
#
def get_messagelevelvalue(level: str) -> int:
    """Gets the integer value associated with a message log level.

    Args:
        level (str): The name of the message level.

    Returns:
        int: The integer value corresponding to the message level.
    """
    mdict = cu.get_config("MESSAGELEVELS", nolog=True)
    return mdict.get(level, 1)


def set_messagelevel(level: str) -> None:
    """Sets the message log level in the configuration.

    Args:
        level (str): The name of the message level.
    """
    cu.set_config("MESSAGELEVEL", get_messagelevelvalue(level))


def showmessage(level: str) -> bool:
    """Determines if a message of a given log level should be displayed.

    Args:
        level (str): The level of the message

    Returns:
        bool: True if the message level meets or exceeds the configured threshold, False otherwise.
    """
    return get_messagelevelvalue(level) >= cu.get_config("MESSAGELEVEL", nolog=True)


def log(process: str, mess: str, level: str = "DEBUG") -> None:
    """Creates file Path based on name, folder and extension

    No detail

    Args:

    Returns:

    Raises:

    Examples:

    """
    if showmessage(level):
        now = datetime.datetime.now()
        print(f"\n{now.strftime('%Y-%m-%d %H:%M:%S')}:{process}: {mess}")


def logerr(process: str, mess: str, level="ERROR") -> None:
    """Creates file Path based on name, folder and extension

    No detail

    Args:

    Returns:

    Raises:

    Examples:

    """
    if showmessage(level):
        print("\n***ERROR********************************\n")
        log(process, mess, level)
        print("***ERROR********************************\n")

@dataclass
class TimingStep:
    processname:str
    starttime:float=time.perf_counter()
    lasttime:float=starttime
    laststep:str="Start Up"

    def printinterval(self,stepname:str):
        steptime=time.perf_counter()
        log(f"{self.processname}:{(steptime-self.starttime):.4f}s",f"{self.laststep} -> {stepname}: {(steptime-self.lasttime):.4f}s")        
        self.lasttime=steptime
        self.lastname=stepname

