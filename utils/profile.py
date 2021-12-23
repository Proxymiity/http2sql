from sqlite3 import OperationalError
from mysql.connector.errors import ProgrammingError
from utils.db import Database
from pxyTools import dataIO
from utils.auth import esc
from os import listdir, getcwd
from pathlib import Path
from flask import request
FORBIDDEN_NAMES = ["table"]
profiles_path = Path(getcwd() + "/profiles")
loaded_profiles = {}


def reload():
    global loaded_profiles
    for c in loaded_profiles:
        loaded_profiles[c].close()
    loaded_profiles = {}
    for p in listdir(str(profiles_path)):
        p_path = Path(str(profiles_path) + "/" + p)
        p_cfg = dataIO.load_json(str(p_path))
        loaded_profiles[p_path.stem] = Database(name=p_cfg["friendly_name"], driver=p_cfg["driver"],
                                                parameters=p_cfg["driver_config"])


def create_table(profile, table):
    if table in FORBIDDEN_NAMES:
        return "400: Unacceptable table name.", 400
    try:
        loaded_profiles[profile].create_table(table)
    except (FileExistsError, OperationalError, ProgrammingError):
        return "409: This table already exists.", 409
    except Exception as e:
        return f"500: Could not create table. ({e})", 500
    else:
        return "200: Table created.", 200


def delete_table(profile, table):
    if table in FORBIDDEN_NAMES:
        return "400: Unacceptable table name.", 400
    try:
        loaded_profiles[profile].delete_table(table)
    except (FileNotFoundError, OperationalError, ProgrammingError):
        return "404: This table does not exist.", 404
    except Exception as e:
        return f"500: Could not delete table. ({e})", 500
    else:
        return "200: Table deleted.", 200


def get(profile, table, key):
    try:
        pool = esc(request.headers.get("Pool", "default"))
        value = loaded_profiles[profile].read(table, pool, key)
        if value is None:
            return "204: No value found in key.", 204
        return value
    except (FileNotFoundError, OperationalError, ProgrammingError):
        return "400: Error while trying to access a table that doesn't exist.", 400
    except Exception as e:
        return f"500: Could not get key. ({e})"


def put(profile, table, key):
    try:
        pool = esc(request.headers.get("Pool", "default"))
        data = request.get_data(False, True)
        loaded_profiles[profile].write(table, pool, key, data)
    except (FileNotFoundError, OperationalError, ProgrammingError):
        return "400: Error while trying to access a table that doesn't exist.", 400
    except Exception as e:
        return f"500: Could not put key. ({e})", 500
    else:
        return f"200: Value recorded.", 200


def delete(profile, table, key):
    try:
        pool = esc(request.headers.get("Pool", "default"))
        loaded_profiles[profile].delete(table, pool, key)
    except (FileNotFoundError, OperationalError, ProgrammingError):
        return "400: Error while trying to access a table that doesn't exist.", 400
    except Exception as e:
        return f"500: Could not delete key. ({e})", 500
    else:
        return f"200: Key deleted.", 200
