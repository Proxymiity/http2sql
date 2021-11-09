import mysql.connector


def sanitize(val):
    return "".join(x for x in val if x.isalnum())


class Driver:
    def __init__(self, host, user, password, database):
        self.db = mysql.connector.connect(host=host, autocommit=True,
                                          user=user, password=password, database=database)
        self.dbc = self.db.cursor()

    def check(self):
        if not self.db.is_connected():
            self.db.reconnect()

    def create_table(self, name: str):
        self.check()
        name = sanitize(name)
        print(f"CREATE TABLE IF NOT EXISTS {name}(pool TEXT, name TEXT, value TEXT)")
        self.dbc.execute(f"CREATE TABLE IF NOT EXISTS {name}(pool TEXT, name TEXT, value TEXT)")

    def delete_table(self, name: str):
        self.check()
        name = sanitize(name)
        self.dbc.execute("SET foreign_key_checks = 0")
        self.dbc.execute(f"DROP TABLE IF EXISTS {name}")
        self.dbc.execute("SET foreign_key_checks = 1")

    def read(self, table: str, pool: str, name: str):
        self.check()
        table = sanitize(table)
        try:
            self.dbc.execute(f"SELECT value FROM {table} WHERE pool=%s AND name=%s", (pool, name))
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
            self.dbc.execute(f"UPDATE {table} SET value=%s WHERE pool=%s AND name=%s", (value, pool, name))

    def delete(self, table: str, pool: str, name: str):
        self.check()
        table = sanitize(table)
        self.dbc.execute(f"DELETE FROM {table} WHERE pool=%s AND name=%s", (pool, name))
