from importlib import import_module


class Database:
    def __init__(self, name: str, driver: str, parameters=None):
        self.name = name
        self.driver_module = import_module(f"drivers.{driver}")
        self.driver = self.driver_module.Driver(**parameters)
        print(f"[db][{self.name}] Initialized Database ({driver})")

    def create_table(self, name: str):
        print(f"[db][{self.name}] POST /{name}")
        self.driver.create_table(name)

    def delete_table(self, name: str):
        print(f"[db][{self.name}] DELETE /{name}")
        self.driver.delete_table(name)

    def read(self, table: str, pool: str, key: str) -> str:
        print(f"[db][{self.name}] GET /{table}/{key}:{pool}")
        return self.driver.read(table, pool, key)

    def write(self, table: str, pool: str, key: str, value: str):
        print(f"[db][{self.name}] PUT /{table}/{key}:{pool}")
        self.driver.write(table, pool, key, value)

    def delete(self, table: str, pool: str, key: str):
        print(f"[db][{self.name}] DELETE /{table}/{key}:{pool}")
        self.driver.delete(table, pool, key)

    def multi(self, get: dict, put: dict, delete: dict):
        print(f"[db][{self.name}] MULTI")
        return self.driver.multi(get, put, delete)

    def close(self):
        print(f"[db][{self.name}] Closed Database")
        self.driver.close()
