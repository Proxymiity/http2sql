from sqlite3 import OperationalError
from mysql.connector.errors import ProgrammingError
from psycopg2.errors import UndefinedTable, DuplicateTable
from utils.db import Database
from pxyTools import dataIO
from utils.auth import esc, send_json, get_config
from os import listdir, getcwd
from pathlib import Path
from flask import request
from json import loads
from json.decoder import JSONDecodeError
from uwsgidecorators import postfork
FORBIDDEN_NAMES = ["table"]
profiles_path = Path(getcwd() + "/profiles")
loaded_profiles = {}


def sanitize(val):
    return "".join(x for x in val if x.isalnum() or x == "_")


@postfork
def _uwsgi_post_fork():
    if get_config()["use_uwsgi_forking"] is True:
        reload()


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
    if table.lower() in FORBIDDEN_NAMES:
        return "400: Unacceptable table name.", 400
    try:
        loaded_profiles[profile].create_table(table)
    except (FileExistsError, OperationalError, ProgrammingError, DuplicateTable):
        return "409: This table already exists.", 409
    except Exception as e:
        return f"500: Could not create table. ({e})", 500
    else:
        return "200: Table created.", 200


def delete_table(profile, table):
    if table.lower() in FORBIDDEN_NAMES:
        return "400: Unacceptable table name.", 400
    try:
        loaded_profiles[profile].delete_table(table)
    except (FileNotFoundError, OperationalError, ProgrammingError, UndefinedTable):
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
    except (FileNotFoundError, OperationalError, ProgrammingError, UndefinedTable):
        return "400: Error while trying to access a table that doesn't exist.", 400
    except Exception as e:
        return f"500: Could not get key. ({e})"


def put(profile, table, key):
    try:
        pool = esc(request.headers.get("Pool", "default"))
        data = request.get_data(False, True)
        loaded_profiles[profile].write(table, pool, key, data)
    except (FileNotFoundError, OperationalError, ProgrammingError, UndefinedTable):
        return "400: Error while trying to access a table that doesn't exist.", 400
    except Exception as e:
        return f"500: Could not put key. ({e})", 500
    else:
        return f"200: Value recorded.", 200


def delete(profile, table, key):
    try:
        pool = esc(request.headers.get("Pool", "default"))
        loaded_profiles[profile].delete(table, pool, key)
    except (FileNotFoundError, OperationalError, ProgrammingError, UndefinedTable):
        return "400: Error while trying to access a table that doesn't exist.", 400
    except Exception as e:
        return f"500: Could not delete key. ({e})", 500
    else:
        return f"200: Key deleted.", 200


def multi(profile):
    data = request.get_data(False, True)
    try:
        json_data = loads(data)
        if not isinstance(json_data, dict):
            return f"400: Malformed JSON. (Expected a dictionary)"
    except JSONDecodeError as e:
        return f"400: Malformed JSON. ({e})", 400
    try:
        json_get = json_data.get("get", {})
        json_get = {sanitize(x): json_get[x] for x in json_get}
        json_put = json_data.get("put", {})
        json_put = {sanitize(x): json_put[x] for x in json_put}
        json_del = json_data.get("delete", {})
        json_del = {sanitize(x): json_del[x] for x in json_del}
        _multi_null_check(json_put)
        resp = loaded_profiles[profile].multi(json_get, json_put, json_del)
        if resp:
            return send_json(resp, 200)
        return send_json({}, 204)
    except Exception as e:
        return f"400: Could not process request. This is likely an error on your side. " \
               f"Please check your JSON and the database you are reading/writing to. ({e})", 400


def _multi_null_check(j):
    if j:
        for t in j:
            for p in j[t]:
                for k in j[t][p]:
                    if j[t][p][k] is None:
                        raise Exception("Trying to write null values.")
