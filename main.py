import dotenv
dotenv.load_dotenv()

import druk, asyncio

Druk = druk.Druk()


async def run():
    async with Druk:
        await Druk.start(Druk.token)


if __name__ == "__main__":
    asyncio.run(run())
