import sqlite3


def sanitize(val):
    return "".join(x for x in val if x.isalnum() or x == "_")


class Driver:
    def __init__(self, relative_path):
        self.db = sqlite3.connect(relative_path, check_same_thread=False)
        self.dbc = self.db.cursor()

    def create_table(self, name: str):
        name = sanitize(name)
        self.dbc.execute(f"CREATE TABLE {name}(pool TEXT, name TEXT, value TEXT)")

    def delete_table(self, name: str):
        name = sanitize(name)
        self.dbc.execute(f"DROP TABLE {name}")

    def read(self, table: str, pool: str, name: str):
        table = sanitize(table)
        try:
            self.dbc.execute(f"SELECT value FROM {table} WHERE pool=(?) AND name=(?)", (pool, name))
            value = self.dbc.fetchall()[0][0]
        except IndexError:
            value = None
        return value

    def write(self, table: str, pool: str, name: str, value: str):
        table = sanitize(table)
        if self.read(table, pool, name) is None:
            self.dbc.execute(f"INSERT INTO {table}(pool, name, value) VALUES (?, ?, ?)", (pool, name, value))
        else:
            self.dbc.execute(f"UPDATE {table} SET value=(?) WHERE pool=(?) AND name=(?)", (value, pool, name))
        self.db.commit()

    def delete(self, table: str, pool: str, name: str):
        table = sanitize(table)
        self.dbc.execute(f"DELETE FROM {table} WHERE pool=(?) AND name=(?)", (pool, name))
        self.db.commit()

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
            pm = {}
            for t in put:
                pm[t] = {}
                for p in put[t]:
                    pm[t][p] = {}
                    for k in put[t][p]:
                        insert = True if self.read(t, p, k) is None else False
                        pm[t][p][k] = (insert, put[t][p][k])
            for t in put:
                for p in put[t]:
                    for k in put[t][p]:
                        if pm[t][p][k][0]:
                            self.dbc.execute(f"INSERT INTO {t}(pool, name, value) "
                                             f"VALUES (?, ?, ?)", (p, k, pm[t][p][k][1]))
                        else:
                            self.dbc.execute(f"UPDATE {t} SET value=(?) "
                                             f"WHERE pool=(?) AND name=(?)", (pm[t][p][k][1], p, k))
        if delete:
            for t in delete:
                for p in delete[t]:
                    for k in delete[t][p]:
                        self.dbc.execute(f"DELETE FROM {t} WHERE pool=(?) AND name=(?)", (p, k))
        if put or delete:
            self.db.commit()
        return resp

    def close(self):
        self.dbc.close()
        self.db.close()
