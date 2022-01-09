import psycopg2


def sanitize(val):
    return "".join(x for x in val if x.isalnum() or x == "_")


class Driver:
    def __init__(self, host, user, password, database, port=5432):
        self.db = psycopg2.connect(host=host, port=port,
                                   user=user, password=password, dbname=database)
        self.dbc = self.db.cursor()
        self._db_args = (host, user, password, database, port)

    def check(self):
        if self.db.closed != 0:
            self.db = psycopg2.connect(host=self._db_args[0], port=self._db_args[4], autocommit=True,
                                       user=self._db_args[1], password=self._db_args[2], dbname=self._db_args[3])
            self.dbc = self.db.cursor()

    def create_table(self, name: str):
        self.check()
        name = sanitize(name)
        self.dbc.execute(f"CREATE TABLE {name}(pool TEXT, name TEXT, value TEXT)")

    def delete_table(self, name: str):
        self.check()
        name = sanitize(name)
        self.dbc.execute(f"DROP TABLE {name}")

    def read(self, table: str, pool: str, name: str):
        self.check()
        table = sanitize(table)
        try:
            self.dbc.execute(f"SELECT value FROM {table} WHERE pool = %s AND name = %s", (pool, name))
            value = self.dbc.fetchall()[0][0]
        except IndexError:
            value = None
        return value

    def write(self, table: str, pool: str, name: str, value: str):
        self.check()
        table = sanitize(table)
        if self.read(table, pool, name) is None:
            self.dbc.execute(f"INSERT INTO {table}(pool, name, value) VALUES (%s, %s, %s)", (pool, name, value))
        else:
            self.dbc.execute(f"UPDATE {table} SET value = %s WHERE pool = %s AND name = %s", (value, pool, name))
        self.db.commit()

    def delete(self, table: str, pool: str, name: str):
        self.check()
        table = sanitize(table)
        self.dbc.execute(f"DELETE FROM {table} WHERE pool = %s AND name = %s", (pool, name))
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
                                             f"VALUES (%s, %s, %s)", (p, k, pm[t][p][k][1]))
                        else:
                            self.dbc.execute(f"UPDATE {t} SET value = %s "
                                             f"WHERE pool = %s AND name = %s", (pm[t][p][k][1], p, k))
        if delete:
            for t in delete:
                for p in delete[t]:
                    for k in delete[t][p]:
                        self.dbc.execute(f"DELETE FROM {t} WHERE pool=%s AND name=%s", (p, k))
        if put or delete:
            self.db.commit()
        return resp

    def close(self):
        self.dbc.close()
        self.db.close()
