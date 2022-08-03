__all__ = (
    'colour',
)

import discord
from colorama import Fore, Style

LOG_LEVELS = {
    "info": Fore.GREEN,
    "warn": Fore.YELLOW,
    "error": Fore.RED,
}

def log(text: str, level: str = "info"):
    print(f'{LOG_LEVELS.get(level, Fore.GREEN)} [+] {discord.utils.utcnow()} | {text} {Style.RESET_ALL}')

def colour(text: str, colour: str):
    return getattr(Fore, colour.upper()) + text + Style.RESET_ALL