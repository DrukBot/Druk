from __future__ import annotations

_all_ = ("DB",)

import typing
import aiosqlite
import datetime

SQLTYPES = {
    int: "BIGINT",
    str: "TEXT",
    bool: "BOOLEAN",
    bytes: "BLOB",
    datetime.datetime: "DATETIME",
}


class Column:
    def __init__(self, name: str, sql_type: typing.Any):
        self.name = name
        if sql_type in SQLTYPES:
            self.type = SQLTYPES[sql_type]
        else:
            self.type = sql_type


class Table:
    def __init__(
        self, name: str, columns: typing.List[Column], primary_key: str = None
    ):
        self.name = name
        self.columns = columns
        primary_key = primary_key

    def create(self):
        return f'CREATE TABLE IF NOT EXISTS {self.name} ({", ".join(f"{c.name} {c.type}" for c in self.columns)})'


class Database:
    """A database manager to make database usage easy."""

    def __init__(
        self,
        url: str,
        name: str,
        tables: typing.List[Table],
    ):
        self.url = url
        self.conn = None
        self.tables = tables

    async def connect(self) -> Database:
        """Connect to the database."""
        self.conn = await aiosqlite.connect(self.url)
        for table in self.tables:
            await self.create_table(table)
        return self

    async def close(self):
        """Closes the database connection."""
        await self.conn.close()

    async def commit(self):
        """Commit the current transaction."""
        await self.conn.commit()

    async def execute(
        self, sql: str, parameters: typing.Iterable = (), all: bool = False
    ) -> typing.Optional[typing.List[aiosqlite.Row]]:
        """Execute a SQL query."""
        async with self.conn.cursor() as cursor:
            await cursor.execute(sql, parameters)
            if all:
                return await cursor.fetchall()
            return await cursor.fetchone()

    async def create_table(self, table: Table):
        """Create a table in the database."""
        await self.execute(table.create())
        await self.conn.commit()

    async def select(self, table: str, where: str, all: bool = False):
        """Select a row from the database."""
        return await self.execute(f"SELECT * FROM {table} WHERE {where};", all=all)

    async def insert(self, table: str, values: typing.Iterable):
        """Insert a row into the database."""
        await self.execute(
            f"INSERT INTO {table} VALUES ({', '.join(['?'] * len(values))});", values
        )
        await self.conn.commit()

    async def update(
        self, table: str, values: typing.Dict[str, typing.Any], where: str
    ):
        """Update a row in the database."""
        await self.execute(
            f"UPDATE {table} SET {', '.join(v+'=?' for v in values)} WHERE {where};",
            values.values(),
        )
        await self.conn.commit()

    async def upsert(self, table: str, values: typing.Iterable, where: str):
        """Upsert a row in the database."""
        await self.execute(
            f"INSERT OR REPLACE INTO {table} VALUES ({', '.join(['?'] * len(values))});",
            values,
        )
        await self.conn.commit()

    async def delete(self, table: str, where: str):
        """Delete a row in the database."""
        await self.execute(f"DELETE FROM {table} WHERE {where};")
        await self.conn.commit()