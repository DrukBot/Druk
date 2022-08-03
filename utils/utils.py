import colorama

def colour(text: str, colour: str):
    return getattr(colorama.Fore, colour.upper()) + text + colorama.Style.RESET_ALL