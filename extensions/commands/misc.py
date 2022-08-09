import os
import dotenv
import aiohttp
import discord
from wikipediaapi import Wikipedia, ExtractFormat


from discord.ext import commands
from discord.app_commands import Choice
from discord import app_commands

from utils.utils import Embed

dotenv.load_dotenv()


class Miscellaneous(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    misc = app_commands.Group(name="misc", description="Get information about thing.")

    @misc.command(name="weather", description="Get the weather in a city.")
    @app_commands.describe(city="The city you want to get the weather from.")
    async def weather(self, ctx: discord.Interaction, city: str):

        base_url = "http://api.openweathermap.org/data/2.5/weather?"

        complete_url = (
            base_url + "appid=" + (os.environ["WEATHER_API_KEY"]) + "&q=" + city
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(complete_url) as resp:
                data = await resp.json()
            try:
                main = data["main"]
                wind = data["wind"]
                weather = data["weather"]
                city_name = data["name"]
                temperature_in_celcius = int(main["temp"] - 273)
                feelslike_in_celcius = int(main["feels_like"] - 273)
                max_tempr = int(main["temp_max"] - 273)
                min_tempr = int(main["temp_min"] - 273)
                wind = data["wind"]
                speed_wind = wind["speed"]
                weather_description = str(weather[0]["description"]).title()
            except KeyError:
                return await ctx.response.send_message(
                    embed=Embed.ERROR(
                        "No Data Found!", "The city you entered is not found."
                    )
                )

        embed = Embed(
            title=f"Weather of {city_name.capitalize()}",
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(name="Temperature", value=f"{temperature_in_celcius} °C")
        embed.add_field(name="Feels Like", value=f"{feelslike_in_celcius} °C")
        embed.add_field(name="Maximum Temperature", value=f"{max_tempr} °C")
        embed.add_field(name="Minimum Temperature", value=f"{min_tempr} °C")
        embed.add_field(name="Description", value=weather_description)
        embed.add_field(name="Wind Velocity", value=f"{speed_wind} km/h")

        await ctx.response.send_message(embed=embed)

    @misc.command(name="truth-or-dare", description="Get a truth or dare.")
    @app_commands.describe(
        category="The category of the truth or dare.",
        type="The type of the truth or dare.",
    )
    @app_commands.choices(
        category=[
            Choice(name="Friendly", value="pg13"),
            Choice(name="Dirty", value="r"),
        ],
        type=[Choice(name="Truth", value="truth"), Choice(name="Dare", value="dare")],
    )
    async def t_or_d(
        self, ctx: discord.Interaction, category: Choice[str], type: Choice[str]
    ):
        data = {"category": category.value, "type": type.value}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"https://api.truthordarebot.xyz/v1/{category.value}?rating={type.value}",
            ) as resp:
                if resp.status > 200:
                    return await ctx.response.send_message(
                        embed=Embed.ERROR("API Error", "The API returned an error.")
                    )

        response = await resp.json()

        embed = Embed(
            title=f"{type.capitalize()} Question", description=response["question"]
        )
        await ctx.response.send_message(embed=embed)


    @misc.command(name="wiki", description="Search wikipedia!")
    @app_commands.describe(search="The item you want to search for")
    async def wiki(self, ctx: discord.Interaction, search: str):
        wiki_wiki = Wikipedia('en',
        extract_format=ExtractFormat.WIKI
        )

        page = wiki_wiki.page(search)

        if not page.exists():
            await ctx.response.send_message(embed=Embed.ERROR(
                "Whoops!", f"There is not a page for {search} on Wikipedia!"
            ))
            return
        
        embed = Embed(
            title=page.title,
            description=page.text[0:4096]
        )
        
        embed.add_field(
            name="URL for further reading",
            value=page.fullurl
        )

        await ctx.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Miscellaneous(bot))
