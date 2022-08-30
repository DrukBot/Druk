from __future__ import annotations

_all_ = (
    "Database",
    "Table",
    "Column",
)

import typing
import os
import asyncio
import asyncpg
import datetime

SQLTYPES = {
    int: "BIGINT",
    str: "LONGTEXT",
    bool: "BOOLEAN",
    bytes: "LONGBLOB",
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
        self.primary_key = primary_key

    def create(self):
        return f"""
        CREATE TABLE IF NOT EXISTS {self.name} ({", ".join(f"{c.name} {c.type}{' PRIMARY KEY' if c.name==self.primary_key else ''}" for c in self.columns)})
        """


DBURL = os.environ["DBURL"]
DBPWD = os.environ["DBPWD"]
DBUSER = os.environ["DBUSER"]

class Database:
    """A database manager to make database usage easy."""

    def __init__(
        self,
        name: str,
        tables: typing.List[Table],
    ):
        self.name = name
        self.conn = None
        self.tables = tables
        self.connected = asyncio.Event()

    async def wait_until_connected(self):
        if not self.connected.is_set:
            await self.connected.wait()

    async def connect(self) -> Database:
        """Connect to the database."""
        self.conn = await asyncpg.connect(
            f'postgres://{DBUSER}:{DBPWD}@{DBURL}/{"druk"+self.name}')
        for table in self.tables:
            await self.create_table(table)
        self.connected.set()
        return self

    async def close(self):
        """Closes the database connection."""
        await self.conn.close()
        self.connected.clear()

    async def refresh(self) -> Database:
        await self.wait_until_connected()
        await self.close()
        await self.connect()

    async def execute(
        self, *args, **kwargs
    ):
        """Execute a SQL query."""
        await self.wait_until_connected()
        return await self.conn.execute(*args, **kwargs)

    async def create_table(self, table: Table):
        """Create a table in the database."""
        return await self.execute(table.create())

    async def fetch(self, table: str, where: str = None, *, all: bool = False, order_by: str = None) -> asyncpg.Record:
        """Select a row from the database."""
        q=f"SELECT * FROM {table}"
        q+=f"\n WHERE {where}" if where else ''
        q+=f"\n ORDER BY {order_by}" if order_by else ''
        if all:
            return await self.conn.fetch(q)
        return await self.conn.fetchrow(q)

    async def insert(self, table: str, values: typing.List[typing.Any]):
        """Insert a row into the database."""
        return await self.execute(
            f"INSERT INTO {table} VALUES ({', '.join(f'${i+1}' for i in  range(len(values)))})",
            *values
        )

    async def update(
        self, table: str, values: typing.Dict[str, typing.Any], where: str
    ):
        """Update a row in the database."""
        k = tuple(values.keys())
        q=f"""
        UPDATE {table}
        SET {', '.join(f'{k[v]} = ${v+1}' for v in range(len(values)))} WHERE {where}
        """
        return await self.execute(
            q,
            *values.values()
        )

    async def upsert(self, table: str, values: typing.Iterable, where: str):
        """Upsert a row in the database."""
        r = tuple(values)
        return await self.execute(
            f"""
            INSERT INTO {table} VALUES ({', '.join(f'${i+1}' for i in  range(len(values)))})
            ON CONFLICT ({where}) DO UPDATE SET {', '.join(f'{r[v]}=${v+1}' for v in range(len(values)))} WHERE {where};
            """, *values
        )

    async def delete(self, table: str, where: str):
        """Delete a row in the database."""
        return await self.execute(f"DELETE FROM {table} WHERE {where}")
