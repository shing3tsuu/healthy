
import asyncio
import logging
from logging import basicConfig

from config_reader import load_config


async def main():

    logging,basicConfig(level=logging.INFO)
    print(load_config('.env').tg_bot.token)


if __name__ == '__main__':
    asyncio.run(main())