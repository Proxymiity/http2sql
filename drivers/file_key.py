import os
import shutil
from pathlib import Path
from pxyTools import dataIO
fe = ".json"


def init_storage(p: Path):
    if not p.is_dir() and p.exists():
        shutil.rmtree(str(p))
        os.makedirs(str(p))
    if not p.exists():
        os.makedirs(str(p))


def load_file(p: str):
    try:
        return dataIO.load_json(p)
    except FileNotFoundError:
        return None


def table_exists(to, t: str):
    if not Path(str(to.absolute_path) + "/" + t).exists():
        raise FileNotFoundError


def sanitize(val):
    return "".join(x for x in val if x.isalnum() or x == "_")


class Driver:
    def __init__(self, relative_path):
        self.relative_path = relative_path
        self.absolute_path = Path(os.getcwd() + "/" + self.relative_path)
        print("Warning: This driver is highly dependant on IO throughput.")

    def create_table(self, name: str):
        init_storage(self.absolute_path)
        name = sanitize(name)
        t_path = Path(str(self.absolute_path) + "/" + name)
        os.makedirs(t_path)

    def delete_table(self, name: str):
        name = sanitize(name)
        t_path = Path(str(self.absolute_path) + "/" + name)
        shutil.rmtree(str(t_path))

    def read(self, table: str, pool: str, name: str):
        table = sanitize(table)
        table_exists(self, table)
        d_rel = "/" + table + "/" + name + fe
        d_data = load_file(self.relative_path + d_rel)
        if d_data is None:
            return None
        else:
            try:
                return d_data[pool]
            except KeyError:
                return None

    def write(self, table: str, pool: str, name: str, value: str):
        table = sanitize(table)
        table_exists(self, table)
        d_rel = "/" + table + "/" + name + fe
        d_data = load_file(self.relative_path + d_rel) or {}
        d_data[pool] = value
        dataIO.save_json(self.relative_path + d_rel, d_data)

    def delete(self, table: str, pool: str, name: str):
        table = sanitize(table)
        table_exists(self, table)
        d_rel = "/" + table + "/" + name + fe
        d_data = load_file(self.relative_path + d_rel)
        if d_data is None:
            return
        d_data.pop(pool)
        dataIO.save_json(self.relative_path + d_rel, d_data)
        if d_data == {}:
            os.remove(self.relative_path + d_rel)

    def multi(self, get: dict, put: dict, delete: dict):
        resp = {}
        if get:
            for t in get:
                resp[t] = {}
                for p in get[t]:
                    resp[t][p] = {}
                    for k in get[t][p]:
                        resp[t][p][k] = self.read(t, p, k)
        if put:
            for t in put:
                for p in put[t]:
                    for k in put[t][p]:
                        self.write(t, p, k, put[t][p][k])
        if delete:
            for t in delete:
                for p in delete[t]:
                    for k in delete[t][p]:
                        self.delete(t, p, k)
        return resp

    def close(self):
        pass  # Nothing to close using a file-based DB as FDs are closed after objects are written to disk
