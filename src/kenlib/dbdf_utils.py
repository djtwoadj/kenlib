from sqlalchemy import create_engine, inspect, select, DateTime, TIMESTAMP
from sqlalchemy.sql import Select
from sqlalchemy.exc import SQLAlchemyError

import pandas as pd
import geopandas as gpd

import kenlib.config_utils as cu
import kenlib.devel_utils as du
import kenlib.db_utils as db
import kenlib.file_utils as fu
import kenlib.df_utils as dfu


def dbstore_df(df, table: str, mode: str = "A", index: bool = False):
    # A = append, T is create temp table T_ for test, "N" is new table, "F" if not new

    match mode:
        case "T":
            table = "T_" + table
            exist = "replace"
        case "A":
            exist = "append"
        case "F":
            exist = "fail"
        case "R":
            exist = "replace"
        case _:
            exist = "replace"

    table = db.pgname(table)
    df.columns = df.columns.str.lower()

    du.log(
        "databaseutils.dbstore_df", f"Upload datafile to  {table} if_exists is {exist}"
    )

    with db.dbengineconnect() as conn:
        try:
            df.to_sql(name=table, con=conn, if_exists=exist, index=index)
            conn.commit()
            du.log("databaseutils.dbstore_df", f"DB to_SQL succesful for table {table}")

        except ValueError as e:
            # Catches Pandas-specific errors (e.g., if_exists='fail' and table exists)
            du.logerr("databaseutils.dbstore_df", f"Pandas configuration error: {e}")

        except SQLAlchemyError as e:
            du.logerr("databaseutils.dbstore_df", f"Underlying DB Driver Error: {e}")


def dbstore_gdf(gdf, table: str, mode: str = "A", index=False):
    # A = append, T is create temp table T_ for test, "N" is new table, "F" if not new

    match mode:
        case "C":
            db.dbcleartable(table)
            exist = "replace"
        case "T":
            table = "T_" + table
            exist = "replace"
        case "A":
            exist = "append"
        case "F":
            exist = "fail"
        case _:
            exist = "replace"

    table = db.pgname(table)
    gdf.columns = gdf.columns.str.lower()

    du.log(
        "databaseutils.dbstore_gdf", f"Upload datafile to  {table} if_exists is {exist}"
    )

    try:
        gdf.to_postgis(name=table, con=db.dbengine(), if_exists=exist, index=index)
        du.log("databaseutils.dbstore_gdf", f"DB to_SQL succesful for table {table}")

    except ValueError as e:
        # Catches Pandas-specific errors (e.g., if_exists='fail' and table exists)
        du.logerr("databaseutils.dbstore_gdf", f"Pandas configuration error: {e}")

    except SQLAlchemyError as e:
        du.logerr("databaseutils.dbstore_gdf", f"Underlying DB Driver Error: {e}")


def dbretrieve_gdf(region, table: str = "", filter: str = ""):

    sql = db.dbbasicsql(region, table, filter)

    try:
        gdf = gpd.read_postgis(sql, con=db.dbengine(), geom_col="geometry")

        du.log("databaseutils.dbretrieve_gdf", f"SQL succesful for {sql}")
        gdf.attrs["name"] = f"{region}"

        return gdf

    except ValueError as e:
        # Catches Pandas-specific errors (e.g., if_exists='fail' and table exists)
        du.logerr("databaseutils.dbretrieve_gdf", f"Pandas configuration error: {e}")

    except SQLAlchemyError as e:
        du.logerr("databaseutils.dbretrieve_gdf", f"Underlying DB Driver Error: {e}")


def dbretrieve_df(table: str = "", filter: str = ""):

    sql = db.dbbasicsql(table, filter)

    cachefile = fu.cachefile(sql, ".parquet")

    if fu.usecachefile(cachefile):
        df = dfu.dfread(cachefile)
        du.log("databaseutils.dbretrieve_df", f"Read data from cachefile for {sql}")
        return df

    try:
        du.log("databaseutils.dbretrieve_df", f"No cachefile for {sql}, query database")

        df = pd.read_sql(sql, con=db.dbengine())
        du.log("databaseutils.dbretrieve_df", f"SQL succesful for {sql}")

        dfu.dfwrite(df, cachefile)
        du.log("databaseutils.dbretrieve_df", f"Wrote data from cachefile for {sql}")

        return df

    except ValueError as e:
        # Catches Pandas-specific errors (e.g., if_exists='fail' and table exists)
        du.logerr("databaseutils.dbretrieve_df", f"Pandas configuration error: {e}")

    except SQLAlchemyError as e:
        du.logerr("databaseutils.dbretrieve_df", f"Underlying DB Driver Error: {e}")


def dbrecord_df(statement: Select) -> pd.DataFrame:
    """
    Executes a SQLAlchemy 2.0 select statement and loads the results into a Pandas
    DataFrame, automatically detecting and casting datetime and integer columns.
    """

    datetime_cols = []

    try:
        # Extract the model/entity being queried (e.g., AppleHealthRecord)
        for entity in statement.column_descriptions:
            model = entity.get("entity")
            if model:
                # Loop through columns and check their database type
                for mapper_property in inspect(model).mapper.column_attrs:
                    column = mapper_property.columns[0]
                    if isinstance(column.type, (DateTime, TIMESTAMP)):
                        datetime_cols.append(column.key)
    except Exception:
        # Fallback if it's a complex primitive construct rather than a standard ORM entity
        pass

    with db.dbengineconnect() as connection:
        df = pd.read_sql_query(sql=statement, con=connection)

    if df.empty:
        return df

    for col in datetime_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    for col in df.select_dtypes(include=["float64"]).columns:
        # Check if all non-null values in this column are whole numbers
        if df[col].dropna().round().eq(df[col].dropna()).all():
            df[col] = df[col].astype("Int64")

    return df
