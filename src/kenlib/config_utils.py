"""Manage the apps configurations, Need to initialise
using init_config()"""

from typing import Any
from pathlib import Path
import sys
import kenlib.devel_utils as du


class Config:
    def __init__(self) -> None:
        self.configs: dict[str, object] = {}

    def set(
        self, key: str, value: object, new: bool = False, update: bool = False
    ) -> None:
        if key in self.configs:
            if new:
                du.logerr(
                    "config.utils,add",
                    f"Dictionary Value already exists for  {key}\nDictionary Values :{self.configs}",
                )
                sys.exit()
            else:
                self.configs[key] = value
        else:
            if update:
                du.logerr(
                    "config.utils,set",
                    f"No value to update for  dictionary value for {key}\nDictionary Values :{self.configs}",
                )
                sys.exit()
            else:
                self.configs[key] = value

    def get(
        self, key: str, default: object = None, crash: bool = False, nolog: bool = False
    ) -> object:
        if key in self.configs:
            if not nolog:
                du.log(
                    "config.utils,get",
                    f"Returning dictionary value for {key} as :{self.configs[key]}\nDictionary Values :{self.configs}",
                    "ALL",
                )
            return self.configs[key]
        else:
            if crash:
                if not nolog:
                    du.logerr(
                        "config.utils,get",
                        f"Cannot get dictionary value for {key}\nDictionary Values :{self.configs}",
                    )

                print("**EXIT BECAUSE OF LOG ERROR**")
                sys.exit()
            else:
                return default

    def loaddict(self, dict: dict[str, object]):
        du.log(
            "config.utils,loaddict",
            f"Adding to config a Dictionary of Values :{dict}",
            "ALL",
        )
        self.configs.update(dict)


CONFIG = Config()


def init_config():
    global CONFIG

    # basic values

    CONFIG.set(
        "MESSAGELEVELS", {"ALL": 0, "DEBUG": 1, "INFO": 2, "WARNING": 3, "ERROR": 4}
    )
    du.set_messagelevel("DEBUG")


def set_config(key: str, value: object, new: bool = False, update: bool = False):
    """Creates or updates a config setting

    Allows checking if new value or updating existing value

    Args:
        key: String name of configuratop property
        value: any value for property stored
        new: If True stops  if property already exists. Default False
        new: If True stops  if property doesn't exist. Default False
    Returns:
        Returns None
    Raises:
        No Raise Errors
    Examples:
        set_config("HOMEDIR",r"/ken/datafiles")
    """
    CONFIG.set(key, value, new, update)


def get_config(
    key: str,
    default: object = None,
    crash: bool = False,
    nolog: bool = False,
    update: bool = False,
    noempty: bool = False,
) -> object:

    return CONFIG.get(key, default, crash, nolog)


def string_config(
    key: str, default: str = "", crash: bool = False, nolog: bool = False
) -> str:
    """Gets a string config setting

    Allows checking if value doesn't exst and returning new value

    Args:
        key: String name of configuratop property
        default: Value returned if property not set
        crash: If True stops  if property doesn't exist. Default False
    Returns:
        Returns string Value of property
    Raises:
        No Raise Errors
    Examples:
        myhomdir=get_config("HOMEDIR",default=r"/ken/datafiles")
    """

    value: object = CONFIG.get(key, default, crash, nolog)
    if isinstance(value, str):
        return value
    else:
        if not nolog:
            du.logerr(
                "config_utils.string_config",
                f"Return value for {key} is not a string :{value}",
            )
        if crash:
            sys.exit()
        else:
            return default


def int_config(
    key: str, default: int = 0, crash: bool = False, nolog: bool = False
) -> int:
    """Gets an integer config setting

    Allows checking if value doesn't exst and returning new value

    Args:
        key: String name of configuratop property
        default: Value returned if property not set
        crash: If True stops  if property doesn't exist. Default False
    Returns:
        Returns int Value of property
    Raises:
        No Raise Errors
    Examples:
        myhomdir=get_config("HOMEDIR",default=r"/ken/datafiles")
    """

    value: object = CONFIG.get(key, default, crash, nolog)
    if isinstance(value, int):
        return value
    else:
        if not nolog:
            du.logerr(
                "config_utils.int_config",
                f"Return value for {key} is not an int :{value}",
            )
        if crash:
            sys.exit()
        else:
            return default


def numeric_config(
    key: str, default: float = 0.0, crash: bool = False, nolog: bool = False
) -> float:
    """Gets a float config setting

    Allows checking if value doesn't exst and returning new value

    Args:
        key: String name of configuratop property
        default: Value returned if property not set
        crash: If True stops  if property doesn't exist. Default False
    Returns:
        Returns int Value of property
    Raises:
        No Raise Errors
    Examples:
        myhomdir=get_config("HOMEDIR",default=r"/ken/datafiles")
    """

    value: object = CONFIG.get(key, default, crash, nolog)
    if isinstance(value, float):
        return value
    else:
        if not nolog:
            du.logerr(
                "config_utils.numeric_config",
                f"Return value for {key} is not a numeric :{value}",
            )
        if crash:
            sys.exit()
        else:
            return default


def bool_config(
    key: str, default: bool = False, crash: bool = False, nolog: bool = False
) -> bool:
    """Gets a boolean config setting

    Allows checking if value doesn't exst and returning new value

    Args:
        key: String name of configuratop property
        default: Value returned if property not set
        crash: If True stops  if property doesn't exist. Default False
    Returns:
        Returns int Value of property
    Raises:
        No Raise Errors
    Examples:
        myhomdir=get_config("HOMEDIR",default=r"/ken/datafiles")
    """

    value: object = CONFIG.get(key, default, crash, nolog)
    if isinstance(value, bool):
        return value
    else:
        if not nolog:
            du.logerr(
                "config_utils.numeric_config",
                f"Return value for {key} is not a boolean :{value}",
            )
        if crash:
            sys.exit()
        else:
            return default


def path_config(key: str) -> Path:
    """Gets a boolean config setting

    Allows checking if value doesn't exst and returning new value

    Args:
        key: String name of configuratop property
        crash: If True stops  if property doesn't exist. Default False
    Returns:
        Returns int Value of property
    Raises:
        No Raise Errors
    Examples:
        myhomdir=get_config("HOMEDIR",default=r"/ken/datafiles")
    """

    value: str = string_config(key, "", crash=True, nolog=False)

    return Path(value)


def dict_config(
    key: str, default: dict = {}, crash: bool = False, nolog: bool = False
) -> dict:

    value = get_config(key, "", crash=True, nolog=False)

    if isinstance(value, dict):
        return value
    else:
        if not nolog:
            du.logerr(
                "config_utils.numeric_config",
                f"Return value for {key} is not a dictionary :{value}",
            )
        if crash:
            sys.exit()
        else:
            return default


def list_config(
    key: str, default: list = [], crash: bool = False, nolog: bool = False
) -> list:

    value = get_config(key, "", crash=True, nolog=False)

    if isinstance(value, list):
        return value
    else:
        if not nolog:
            du.logerr(
                "config_utils.numeric_config",
                f"Return value for {key} is not a dictionary :{value}",
            )
        if crash:
            sys.exit()
        else:
            return default


def loadconfigdict(dict: dict[str, object]):
    """Adds a dictionary of settings in bulk to config settings

    Args:
        dict: A dictionary of configuration settings
    Returns:
        Returns None
    Raises:
        No Raise Errors
    Examples:
        loaddict({"HOMEDIR":r"/ken/datafiles","LIMIT":4})
    """
    CONFIG.loaddict(dict)
