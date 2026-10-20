"""
kenlib
My Custom Library
"""

# 1. Package Metadata
__version__ = "0.1.0"
__author__ = "Ken"

# 2. Package-level Constants
DEFAULT_TIMEOUT = 30

# 3. Exposing internal code to the top level (using relative imports)
from .devel_utils import log, logerr, set_messagelevel,TimingStep
from .file_utils import fileexists, getcsvfile, getdatafile, getfile
from .config_utils import (
    get_config,
    init_config,
    set_config,
    loadconfigdict,
    string_config,
    int_config,
    numeric_config,
    bool_config,
    path_config,
    dict_config,
    list_config,
)
from .df_utils import (
    df_tonumeric,
    df_todatetime,
    printdf,
    printgeo,
    readcsv,
    writecsv,
    dfname,
    downloadfile,
    addcolorcol,
    browsedf,
    browsedf_files,
    dftogoogle,
    dfreduce,
    dfautoreduce,
    df_rowtodict,
)

from .db_utils import (
    dbconnection,
    dbengine,
    dbenginebegin,
    dbbasicsql,
    dbdroptable,
    dbcleartable,
    dbengineconnect,
    dbexecsql,
    dbscalar,
)

from .dbdf_utils import (
    dbstore_df,
    dbretrieve_df,
    dbstore_gdf,
    dbretrieve_gdf,
    dbrecord_df,
)

from .graph_utils import (
    GraphPlot
)
__all__ = []

init_config()
