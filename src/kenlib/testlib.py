import kenlib.config_utils as cu
import kenlib.devel_utils as du
import kenlib.db_utils as db


def main():

    cu.set_config(
        "CONNECTION",
        db.dbconnection("finproc_user", "4004", "oldjone", 5432, "glts", "finproc"),
    )
    db.dbcleartable("transactions")


if __name__ == "__main__":
    main()
