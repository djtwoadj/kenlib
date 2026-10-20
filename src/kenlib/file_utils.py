"""Module containing functions to create filenames and check files existstance"""

import sys
from pathlib import Path
import hashlib
import base64
import datetime

import kenlib.config_utils as cu
import kenlib.devel_utils as du


# file name from directory, file and ext
def getfile(dir: str, filename: str, ext: str) -> Path:
    """Creates file Path based on name, folder and extension

    No detail

    Args:
        dir: folder name as string
        filename: file name body as string
        ext: File extension string with or without initial dot

    Returns:
        The full file as a Path object

    Raises:
        No errors raised

    Examples:
        getfile (r"/home/ken")
    """

    if ext[0] != ".":
        ext = "." + ext

    return (Path(dir) / filename).with_suffix(ext)


def getdatafile(filename: str, ext: str) -> Path:
    """Creates file Path based on name, folder and extension

    No detail

    Args:

    Returns:

    Raises:

    Examples:

    """

    return getfile(cu.get_config("DATADIR"), filename, ext)


def getcsvfile(filename: str) -> Path:
    """Creates file Path based on name, folder and extension

    No detail

    Args:

    Returns:

    Raises:

    Examples:

    """

    return getdatafile(filename, ".csv")


def getparquetfile(filename: str) -> Path:
    """Creates file Path based on name, folder and extension

    No detail

    Args:

    Returns:

    Raises:

    Examples:

    """

    return getdatafile(filename, ".parquet")


def getdatafolder() -> Path:
    return cu.path_config("DATADIR")


def fileexists(file: Path, noterr: bool = False) -> bool:
    """Checks if a file exists and deals with the issue if it doesn't

    No detail

    Args:
        file: A Path object defining the file
        noterr: Optional boolean flag, if True just returs if file exists, if false checks folder and quits. Default False

    Returns:
        Boolean saying if file exists or not
    Raises:

    Examples:

    """
    if file.is_file():
        du.log("predictutils.fileexists", f"The file exists: {file}")
        return True
    elif not noterr:
        du.logerr("predictutils.fileexists", f"The file does not exists: {file}")

        folder = file.parent
        if folder.is_dir():
            du.log("predictutils.fileexists", f"The folder exists: {folder}")
        else:
            du.logerr(
                "predictutils.fileexists", f"The folder does not exists: {folder}"
            )

        sys.exit()

    else:
        return False


def hashname(filename):
    raw_hash = hashlib.sha256(filename.encode("utf-8")).digest()

    b64_name = base64.urlsafe_b64encode(raw_hash).decode("utf-8").rstrip("=")

    return b64_name[:12]


def cachefile(filename: str, ext: str) -> Path:
    datadir = getdatafolder()
    cachedir = datadir / "dbcache"

    return getfile(str(cachedir), hashname(filename), ext)


def usecachefile(
    cachefile: Path, recentdate: datetime.datetime = datetime.datetime.now()
) -> bool:
    if cachefile.exists():
        if lastmodified(cachefile) <= recentdate:
            return True

    return False


def lastmodified(file: Path) -> datetime.datetime:
    mod_timestamp = file.stat().st_mtime
    return datetime.datetime.fromtimestamp(mod_timestamp)
