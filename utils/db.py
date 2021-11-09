from importlib import import_module


class Database:
    def __init__(self, driver: str, parameters=None):
        self.driver_module = import_module(f"drivers.{driver}")
        self.driver = self.driver_module.Driver(**parameters)
        print(f"Initialized Database ({driver}, {parameters})")

    def create_table(self, name: str):
        self.driver.create_table(name)

    def delete_table(self, name: str):
        self.driver.delete_table(name)

    def read(self, table: str, pool: str, name: str) -> str:
        return self.driver.read(table, pool, name)

    def write(self, table: str, pool: str, name: str, value: str):
        try:
            self.driver.write(table, pool, name, value)
        except FileNotFoundError:
            pass

    def delete(self, table: str, pool: str, name: str):
        self.driver.delete(table, pool, name)
