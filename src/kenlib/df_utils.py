import webbrowser

import gspread
import pandas as pd
import geopandas as gpd
from gspread_dataframe import set_with_dataframe
from pathlib import Path

import kenlib.config_utils as cu
import kenlib.devel_utils as du
import kenlib.file_utils as fu


def dfautoreduce(df: pd.DataFrame, field="value", sortfield="data_date"):
    recs = len(df.index)

    if recs > 100:
        reduce = int(recs / 100)
        return dfreduce(df, field, sortfield, reduce, reduce)

    return df


def dfreduce(df: pd.DataFrame, field: str = "value", sortfield="data_date", window: int = 1, sample: int = 1):

    df=df.sort_values(by=sortfield)

    if window != 1:
        df[field] = df[field].rolling(window=sample).mean()

    if sample != 1:
        df = df.iloc[::sample]

    return df


def df_tonumeric(df: pd.DataFrame, fields: list[str]) -> pd.DataFrame:
    for fld in fields:
        if fld != "":
            df[fld] = pd.to_numeric(df[fld], errors="coerce")
            # df = df.dropna(subset=[df])

    return df

def df_todatetime(df: pd.DataFrame, fields: list[str]) -> pd.DataFrame:
    for fld in fields:
        if fld != "":
            df[fld] = pd.to_datetime(df[fld], errors="coerce")
            # df = df.dropna(subset=[df])

    return df


def printdf(df: pd.DataFrame, title: str):
    """
    Log and print the contents of a pandas DataFrame with a specified title.

    Parameters
    ----------
    df : pandas.DataFrame or Any
        The DataFrame (or generic object) to be logged and printed.
    title : str
        The title or description associated with the DataFrame for logging and printing context.
    """
    du.log("printdf", f"\n\nPrinting dataframe: {title}")

    # print(f"DataFrame name is: {dfname(df)}")

    printdfany(df, title)


def printgeo(gdf: pd.DataFrame, title: str):
    du.log("printdf", f"\n\nPrinting geodataframe: {title}")

    # print(f"GeoDataFrame name is: {dfname(gdf)}")

    printdfany(gdf, title)


def printdfany(df, title):

    du.log("gltsutils.printdfany", f"{title} Type:{type(df)}")

    if isinstance(df, pd.DataFrame):
        recs = len(df.index)
        cols = len(df.columns)

        if recs == 0:
            print("****Empty Dataframe****")
        else:
            colline = ",".join(
                [
                    f"{col}({dtype}):[{val}]"
                    for (col, dtype), val in zip(df.dtypes.items(), df.iloc[0])
                ]
            )

            print(f"Dataframe,Total Records:{recs} Total Columns:{cols}")
            print(f"All Columns: {colline}")
            cols = min(14, cols)
            rows = min(10, recs)
            print(df.iloc[:rows, :cols])

    elif isinstance(df, pd.Series):
        print(f"Series info:\n{df.info()}\n{df.head(10)}")

    else:
        print("****Unknown Data Type****")


def dfname(df: pd.DataFrame, default: str = "NoName") -> str:

    # Check if 'name' key exists in attrs
    if "name" in df.attrs:
        return df.attrs["name"]
    else:
        return default


def writecsv(data: pd.DataFrame, filename: str = ""):
    if filename != "":
        file = fu.getcsvfile(filename)
        data.to_csv(file, index=False)


def writeparquet(data: pd.DataFrame, filename: str = ""):
    if filename != "":
        file = fu.getparquetfile(filename)
        data.to_parquet(file, index=False)


def readcsv(filename: str, skiprows=0, header=True) -> pd.DataFrame:
    file = fu.getcsvfile(filename)
    if fu.fileexists(file):
        if header:
            data = pd.read_csv(file, skiprows=skiprows)
        else:
            data = pd.read_csv(file, skiprows=skiprows, header=None)
        return data

    return pd.DataFrame()


def readparquet(filename: str) -> pd.DataFrame:
    file = fu.getparquetfile(filename)
    if fu.fileexists(file):
        data = pd.read_parquet(file)
        return data

    return None


def downloadfile(filename: str, url: str, force: bool = False):
    file = fu.getcsvfile(filename)

    if force or not fu.fileexists(file, noterr=True):
        du.log("predictutils.downloadfile", f"Downloading directly from url {url}")
        data = pd.read_csv(url)
        du.log("predictutils.downloadfile", f"Saving copy to  {file}")
        data.to_csv(file, index=False)
        return data
    else:
        du.log("predictutils.downloadfile", f"Reading csv from file {file}")
        return pd.read_csv(file)


def addcolorcol(data: gpd.GeoDataFrame, col: str):

    min_val, max_val = data[col].min(), data[col].max()
    data["norm_val"] = (data[col] - min_val) / (max_val - min_val)

    data["fill_color"] = data["norm_val"].apply(get_color)

    return data


def get_color(norm: float):
    r = int(norm * 255)
    g = 0
    b = int((1 - norm) * 255)
    return [r, g, b, 140]  # RGBA


def browsedf(
    data=None,
    caption="",
    filename: str = "",
    ftype: str = "c",
    htmlname: str = "dataset_view",
):

    css_styles = """
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 30px;
            background-color: #f9f9fb;
            color: #333;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin-top: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            background-color: #ffffff;
            border-radius: 8px;
            overflow: hidden;
        }
        th, td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #eef2f5;
        }
        th {
            background-color: #4f46e5; /* Modern Indigo */
            color: white;
            font-weight: 600;
            font-size: 12px;
            letter-spacing: 0.5px;
        }
        tr:hover {
            background-color: #f1f5f9; /* Subtle row highlight on hover */
        }
        tr:nth-child(even) {
            background-color: #f8fafc; /* Zebra striping */
        }
    </style>
    """

    if data is None:
        if ftype == "c":
            data = readcsv(filename)
        elif ftype == "p":
            data = readparquet(filename)

    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)

    # 3. Define the HTML file name
    html_file = fu.getdatafile(htmlname, ".html")

    if caption != "":
        title = caption
    elif filename != "":
        title = f"File: {filename}"
    else:
        title = "No Name"

    table_html = data.to_html(index=False)

    full_html_content = f"{css_styles}\n<h2>{title}</h2>{table_html}"

    html_file.write_text(full_html_content, encoding="utf-8")

    du.log(
        "df_utils.browsedf",
        f"Successfully generated '{html_file.as_uri()}' now open in the browser",
    )
    # 5. Automatically open the HTML file in your default web browser
    # webbrowser.open(html_file.as_uri())

    pd.reset_option("display")


def browsedf_files():
    folder = fu.getdatafolder()

    files = [f for f in folder.iterdir() if f.is_file()]

    files = sorted(files)
    # Print the file names
    opt = 0
    for file in files:
        opt += 1
        print(f"{opt}: {file.name}")

    user_number = int(input("Enter the file number: "))
    while user_number > 0:
        filename = str(files[user_number - 1])

        # printdf(readcsv(filename),filename)

        browsedf(filename=filename)

        user_number = int(input("Enter the file number: "))


def dftogoogle(data=None, filename="", workbookname="", sheetname=""):

    if data is None:
        data = readcsv(filename)

    if workbookname == "":
        workbookname = cu.string_config("GOOGLESHEET")

    gc = gspread.service_account(filename="credentials.json")
    du.log("df_utils.dftogoogle", f"trying to get workbook {workbookname}")
    sh = gc.open(workbookname)

    try:
        # Try to get the existing worksheet
        du.log("df_utils.dftogoogle", f"trying to get worksheet {sheetname}")
        wsh = sh.worksheet(sheetname)
    except gspread.exceptions.WorksheetNotFound:
        du.log(
            "df_utils.dftogoogle", f"Could not get worksheet {sheetname}, will create"
        )
        wsh = sh.add_worksheet(title=sheetname, rows=100, cols=20)
        du.log("df_utils.dftogoogle", f"Added worksheet {sheetname}")

    wsh.clear()

    set_with_dataframe(
        wsh,
        data,
        row=1,
        col=1,
        include_index=False,
        include_column_header=True,
        resize=True,
    )

    du.log("df_utils.dftogoogle", "DataFrame successfully uploaded!")


def dfread(file: Path) -> pd.DataFrame:
    match file.suffix:
        case ".csv":
            return pd.read_csv(file)
        case ".parquet":
            return pd.read_parquet(file)
        case ".pickle":
            return pd.read_pickle(file)

    return pd.DataFrame()


def dfwrite(df: pd.DataFrame, file: Path):
    match file.suffix:
        case ".csv":
            df.to_csv(file, index=False)
        case ".parquet":
            df.to_parquet(file, index=False)
        case ".pickle":
            df.to_pickle(file)

def df_rowtodict (df:pd.DataFrame, field:str, value:str):
    return  df.loc[df[field] == value].to_dict(orient='records')[0]
