__all__ = (
    "colour",
    "log",
    "Embed",
    "COLOURS",
)

import os
import dotenv
import typing
import discord
import aiohttp
from colorama import Fore, Style

dotenv.load_dotenv()

LOG_LEVELS = {
    "info": "green",
    "warn": "yellow",
    "error": "red",
}



def log(text: str, level: str = "info"):
    print(
        colour(
            f"[+] {discord.utils.utcnow()} | {text}",
            colour=LOG_LEVELS.get(level, "info"),
        )
    )


async def log_webhook(embed: discord.Embed, *, content: typing.Optional[str]=None):
    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.partial(id=int(os.environ["LOG_WEBHOOK_ID"]), token=os.environ["LOG_WEBHOOK_TOKEN"], session=session)
        await webhook.send(content=content, embed=embed)
    await session.close()
        

def colour(text: str, colour: str):
    return getattr(Fore, colour.upper(), "") + text + Style.RESET_ALL


class COLOURS:
    def __getattribute__(self, name: str) -> discord.Colour:
        return getattr(discord.Colour, name.lower())()


COLOURS = COLOURS()


class Embed(discord.Embed):
    def __init__(self, color=0xA08629, fields=(), field_inline=False, **kwargs):
        super().__init__(color=color, **kwargs)
        for n, v in fields:
            self.add_field(name=n, value=v, inline=field_inline)

    @classmethod
    def SUCCESS(cls, title: str, description: str):
        embed = discord.Embed(description=description, colour=COLOURS.green)
        embed.set_author(
            name=title,
            icon_url=discord.PartialEmoji(
                name="success", id="1004762059981983754", animated=False
            ).url,
        )
        return embed

    @classmethod
    def ERROR(cls, title: str, description: str):
        embed = cls(description=description, colour=COLOURS.red)
        embed.set_author(
            name=title,
            icon_url=discord.PartialEmoji(
                name="wrong", id="1004762039618633839", animated=False
            ).url,
        )
        return embed


