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


def sanitize(val):
    return "".join(x for x in val if x.isalnum())


class Driver:
    def __init__(self, relative_path):
        self.relative_path = relative_path
        self.absolute_path = Path(os.getcwd() + "/" + self.relative_path)

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
        d_rel = "/" + table + "/" + pool + fe
        d_data = load_file(self.relative_path + d_rel)
        if d_data is None:
            raise FileNotFoundError
        else:
            try:
                return d_data[name]
            except KeyError:
                return None

    def write(self, table: str, pool: str, name: str, value: str):
        table = sanitize(table)
        d_rel = "/" + table + "/" + pool + fe
        d_data = load_file(self.relative_path + d_rel) or {}
        d_data[name] = value
        dataIO.save_json(self.relative_path + d_rel, d_data)

    def delete(self, table: str, pool: str, name: str):
        table = sanitize(table)
        d_rel = "/" + table + "/" + pool + fe
        d_data = load_file(self.relative_path + d_rel)
        if d_data is None:
            raise FileNotFoundError
        d_data.pop(name)
        dataIO.save_json(self.relative_path + d_rel, d_data)
        if d_data == {}:
            os.remove(self.relative_path + d_rel)

    def close(self):
        pass  # Nothing to close using a file-based DB as FDs are closed after objects are written to disk
