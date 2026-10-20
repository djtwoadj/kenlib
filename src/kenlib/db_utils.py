from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError

import kenlib.config_utils as cu
import kenlib.devel_utils as du

ENGINE = None


def dbconnection(
    user: str, password: str, host: str, port: int, db: str, schema: str = ""
):
    connectionstring = f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}"

    if schema != "":
        connectionstring = connectionstring + f"?options=-c%20search_path%3D{schema}"

    du.log("databaseutils.dbengine", f"Connection String Is: {connectionstring}")

    return connectionstring


def dbengine():
    global ENGINE

    if ENGINE is None:

        connectionstring = cu.string_config("CONNECTION")

        du.log("databaseutils.dbengine", f"Connecting to DB: {connectionstring}")

        ENGINE = create_engine(connectionstring)

    return ENGINE


def dbengineconnect():
    return dbengine().connect()


def dbenginebegin():
    return dbengine().begin()


def pgname(name: str) -> str:
    return name.lower()


def dbexecsql(sql: str):
    du.log("databaseutils.dbexecsql", f"SQL To run\n{sql}")

    try:
        with dbengine().begin() as conn:
            conn.exec_driver_sql(text(sql))
            du.log("databaseutils.dbexecsql", f"SQL Run successfully\n{sql}")

    except ValueError as e:
        # Catches Pandas-specific errors (e.g., if_exists='fail' and table exists)
        du.logerr("databaseutils.dbexecsql", f"Pandas configuration error: {e}")

    except SQLAlchemyError as e:
        du.logerr("databaseutils.dbexecsql", f"Underlying DB Driver Error: {e}")


def dbdroptable(table: str):

    table = pgname(table)
    sql = f'DROP TABLE IF EXISTS "{table}" CASCADE'

    dbexecsql(sql)


def dbcleartable(table: str):

    table = pgname(table)
    sql = f'TRUNCATE TABLE "{table}" CASCADE'

    dbexecsql(sql)


def dbbasicsql(table: str, filter: str = "") -> str:
    table = pgname(table)
    sql = f"SELECT * from {table}"

    if filter != "":
        sql = sql + f" WHERE {filter}"

    du.log("databaseutils.dbbasicsql", f"DB Retrieve SQL: {sql}")

    return sql


def dbscalar(sql: str):

    with dbengineconnect() as conn:
        maxdate = conn.scalar(text(sql))

    return maxdate
