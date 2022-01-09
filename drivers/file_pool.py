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
        d_rel = "/" + table + "/" + pool + fe
        d_data = load_file(self.relative_path + d_rel)
        if d_data is None:
            return None
        else:
            try:
                return d_data[name]
            except KeyError:
                return None

    def write(self, table: str, pool: str, name: str, value: str):
        table = sanitize(table)
        table_exists(self, table)
        d_rel = "/" + table + "/" + pool + fe
        d_data = load_file(self.relative_path + d_rel) or {}
        d_data[name] = value
        dataIO.save_json(self.relative_path + d_rel, d_data)

    def delete(self, table: str, pool: str, name: str):
        table = sanitize(table)
        table_exists(self, table)
        d_rel = "/" + table + "/" + pool + fe
        d_data = load_file(self.relative_path + d_rel)
        if d_data is None:
            return
        d_data.pop(name)
        dataIO.save_json(self.relative_path + d_rel, d_data)
        if d_data == {}:
            os.remove(self.relative_path + d_rel)

    def multi(self, get: dict, put: dict, delete: dict):
        resp = {}
        if get:
            for t in get:
                table_exists(self, t)
                resp[t] = {}
                for p in get[t]:
                    d_rel = "/" + t + "/" + p + fe
                    d_data = load_file(self.relative_path + d_rel)
                    resp[t][p] = {}
                    for k in get[t][p]:
                        if d_data is None:
                            resp[t][p][k] = None
                        else:
                            try:
                                resp[t][p][k] = d_data[k]
                            except KeyError:
                                resp[t][p][k] = None
        if put:
            for t in put:
                table_exists(self, t)
                for p in put[t]:
                    d_rel = "/" + t + "/" + p + fe
                    d_data = load_file(self.relative_path + d_rel) or {}
                    for k in put[t][p]:
                        d_data[k] = put[t][p][k]
                    dataIO.save_json(self.relative_path + d_rel, d_data)
        if delete:
            for t in delete:
                table_exists(self, t)
                for p in delete[t]:
                    d_rel = "/" + t + "/" + p + fe
                    d_data = load_file(self.relative_path + d_rel) or {}
                    for k in delete[t][p]:
                        if d_data is not None:
                            d_data.pop(k)
                    dataIO.save_json(self.relative_path + d_rel, d_data)
                    if d_data == {}:
                        os.remove(self.relative_path + d_rel)
        return resp

    def close(self):
        pass  # Nothing to close using a file-based DB as FDs are closed after objects are written to disk
