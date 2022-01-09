import os
import _csv
import shutil
from pathlib import Path


def init_storage(p: Path):
    if not p.is_dir() and p.exists():
        shutil.rmtree(str(p))
        os.makedirs(str(p))
    if not p.exists():
        os.makedirs(str(p))


def sanitize(val):
    return "".join(x for x in val if x.isalnum() or x == "_")


class Driver:
    def __init__(self, relative_path):
        self.relative_path = relative_path
        self.absolute_path = Path(os.getcwd() + "/" + self.relative_path)
        print("Warning: This driver is highly dependant on IO throughput.")
        print("Warning: Performance may be decreased by the number of entries in the pool.")

    def create_table(self, name: str):
        init_storage(self.absolute_path)
        name = sanitize(name)
        t_path = Path(str(self.absolute_path) + "/" + f"{name}.csv")
        t_path.touch()

    def delete_table(self, name: str):
        name = sanitize(name)
        t_path = Path(str(self.absolute_path) + "/" + f"{name}.csv")
        t_path.unlink()

    def read(self, table: str, pool: str, name: str):
        table = sanitize(table)
        t_path = Path(str(self.absolute_path) + "/" + f"{table}.csv")
        with open(t_path, newline='') as f:
            r = _csv.reader(f, quoting=_csv.QUOTE_MINIMAL)
            for line in r:
                if line[0] == pool and line[1] == name:
                    return line[2]
            return None

    def write(self, table: str, pool: str, name: str, value: str):
        table = sanitize(table)
        t_path = Path(str(self.absolute_path) + "/" + f"{table}.csv")
        with open(t_path, 'r', newline='') as f:
            r = _csv.reader(f, quoting=_csv.QUOTE_MINIMAL)
            wl = list(r)
        with open(t_path, 'w', newline='') as f:
            w = _csv.writer(f, quoting=_csv.QUOTE_MINIMAL)
            y = 0
            for line in wl:
                if line[0] == pool and line[1] == name:
                    wl[y][2] = value
                    w.writerows(wl)
                    return
                y += 1
            wl.append([pool, name, value])
            w.writerows(wl)

    def delete(self, table: str, pool: str, name: str):
        table = sanitize(table)
        t_path = Path(str(self.absolute_path) + "/" + f"{table}.csv")
        with open(t_path, 'r', newline='') as f:
            r = _csv.reader(f, quoting=_csv.QUOTE_MINIMAL)
            wl = list(r)
        y = 0
        for line in wl:
            if line[0] == pool and line[1] == name:
                with open(t_path, 'w', newline='') as f:
                    w = _csv.writer(f, quoting=_csv.QUOTE_MINIMAL)
                    wl.pop(y)
                    w.writerows(wl)
                    return
            y += 1

    def multi(self, get: dict, put: dict, delete: dict):
        resp = {}
        if get:
            for t in get:
                t_path = Path(str(self.absolute_path) + "/" + f"{t}.csv")
                with open(t_path, 'r', newline='') as f:
                    r = _csv.reader(f, quoting=_csv.QUOTE_MINIMAL)
                    wl = list(r)
                    resp[t] = {}
                    for p in get[t]:
                        resp[t][p] = {}
                        for k in get[t][p]:
                            resp[t][p][k] = None
                            for line in wl:
                                if line[0] == p and line[1] == k:
                                    resp[t][p][k] = line[2]
                                    break
        if put:
            for t in put:
                t_path = Path(str(self.absolute_path) + "/" + f"{t}.csv")
                with open(t_path, 'r', newline='') as f:
                    r = _csv.reader(f, quoting=_csv.QUOTE_MINIMAL)
                    wl = list(r)
                with open(t_path, 'w', newline='') as f:
                    w = _csv.writer(f, quoting=_csv.QUOTE_MINIMAL)
                    for p in put[t]:
                        for k in put[t][p]:
                            y = 0
                            f = False
                            for line in wl:
                                if line[0] == p and line[1] == k:
                                    wl[y][2] = put[t][p][k]
                                    f = True
                                    break
                                y += 1
                            if not f:
                                wl.append([p, k, put[t][p][k]])
                    w.writerows(wl)
        if delete:
            for t in delete:
                t_path = Path(str(self.absolute_path) + "/" + f"{t}.csv")
                with open(t_path, 'r', newline='') as f:
                    r = _csv.reader(f, quoting=_csv.QUOTE_MINIMAL)
                    wl = list(r)
                with open(t_path, 'w', newline='') as f:
                    w = _csv.writer(f, quoting=_csv.QUOTE_MINIMAL)
                    for p in delete[t]:
                        for k in delete[t][p]:
                            y = 0
                            for line in wl:
                                if line[0] == p and line[1] == k:
                                    wl.pop(y)
                                    break
                                y += 1
                    w.writerows(wl)
        return resp

    def close(self):
        pass
