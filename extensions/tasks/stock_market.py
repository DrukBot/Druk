from time import sleep
import discord

from discord.ext import commands, tasks
from utils.utils import Embed
import aiohttp
import os
import dotenv

from utils.db import Database, Table, Column

dotenv.load_dotenv()

class StockMarket(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.db = Database("economy", tables=[stable])


    @tasks.loop(minutes=15)
    async def update_stocks(self):
        allstocks = await self.db.fetch('stock_info', all=True)
        for stock in allstocks:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url=f"https://finnhub.io/api/v1/quote?symbol={stock['stock_id']}&token={os.environ['STOCK_KEY']}"
                ) as resp:

                    if resp.status != 200:
                        self.bot.log_webhook(embed=Embed.ERROR("Whoops", f"Something went wrong with the API, it returned status {resp.status}"))

                    response = await resp.json()

            await self.db.update("stock_info", {'price': round(response['c'])+1}, f"stock_id = {stock['stock_id']}")
            sleep(.5)


stable = Table(
    "stock_info",
    [
        Column("stock_id", "TEXT"),
        Column("name", "TEXT"),
        Column("price", int),
        Column("max_owned", int),
        Column("remaining", int)
    ],
    primary_key="stock_id"
)

async def setup(bot):
    await bot.add_cog(StockMarket(bot))