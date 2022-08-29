__all__ = (
    "colour",
    "log",
    "Embed",
    "COLOURS",
)

from operator import iconcat
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


def colour(text: str, colour: str):
    return getattr(Fore, colour.upper(), "") + text + Style.RESET_ALL


class COLOURS:
    def __getattribute__(self, name: str) -> discord.Colour:
        return getattr(discord.Colour, name.lower())()


class emoji:
    SuccessURL = discord.PartialEmoji(
        name="success", animated=False, id=1004762059981983754
    ).url
    ErrorURL = discord.PartialEmoji(
        name="wrong", animated=False, id=1004762039618633839
    )


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
                name="Success", id="1004762059981983754", animated=False
            ).url,
        )
        return embed

    @classmethod
    def ERROR(cls, title: str, description: str):
        embed = cls(description=description, colour=COLOURS.red)
        embed.set_author(
            name=title,
            icon_url=discord.PartialEmoji(
                name="Wrong", id="1004762039618633839", animated=False
            ).url,
        )
        return embed

    @classmethod
    def WARN(cls, title: str, description: str):
        embed = cls(description=description, colour=COLOURS.yellow)
        embed.set_author(
            name=title,
            icon_url=discord.PartialEmoji(
                name="Warn", animated=False, id=1013862574632210443
            ).url,
        )
        return embed

    @classmethod
    def INFO(cls, title: str, description: str):
        embed = cls(description=description, colour=COLOURS.blue)
        embed.set_author(
            name=title,
            icon_url=discord.PartialEmoji(
                name="Info", animated=False, id=1013862488892248164
            ).url,
        )
        return embed
