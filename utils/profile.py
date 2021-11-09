from utils.db import Database
from utils.dataIO import dataIO
from utils.auth import esc
from os import listdir, getcwd
from pathlib import Path
from flask import request
profiles_path = Path(getcwd() + "/profiles")
loaded_profiles = {}


def reload():
    global loaded_profiles
    loaded_profiles = {}
    for p in listdir(str(profiles_path)):
        p_path = Path(str(profiles_path) + "/" + p)
        p_cfg = dataIO.load_json(str(p_path))
        loaded_profiles[p_path.stem] = Database(p_cfg["driver"], p_cfg["driver_config"])


def create_table(profile, table):
    loaded_profiles[profile].create_table(table)


def delete_table(profile, table):
    loaded_profiles[profile].delete_table(table)


def get(profile, table, key):
    pool = esc(request.headers.get("Pool", "default"))
    return loaded_profiles[profile].read(table, pool, key)


def put(profile, table, key):
    pool = esc(request.headers.get("Pool", "default"))
    data = request.get_data(False, True)
    loaded_profiles[profile].write(table, pool, key, data)


def delete(profile, table, key):
    pool = esc(request.headers.get("Pool", "default"))
    loaded_profiles[profile].delete(table, pool, key)
