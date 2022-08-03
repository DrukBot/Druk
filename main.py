import asyncio
import druk

Druk = druk.Druk()

async def run():
    async with Druk:
        await Druk.start(Druk.token)

if __name__ == "__main__":
    asyncio.run(run())
