import sqlite3


def sanitize(val):
    return "".join(x for x in val if x.isalnum())


class Driver:
    def __init__(self, relative_path):
        self.db = sqlite3.connect(relative_path)
        self.dbc = self.db.cursor()

    def create_table(self, name: str):
        name = sanitize(name)
        self.dbc.execute(f"CREATE TABLE IF NOT EXISTS {name}(pool TEXT, name TEXT, value TEXT)")

    def delete_table(self, name: str):
        name = sanitize(name)
        self.dbc.execute(f"DROP TABLE IF EXISTS {name}")

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
