__all__ = ("colour",)

import discord
from colorama import Fore, Style

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
