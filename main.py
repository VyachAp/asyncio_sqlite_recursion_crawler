import argparse
import asyncio
import logging
from datetime import datetime

import aiohttp

from db import on_start_db
from task import Crawler

LOGGER_FORMAT = '%(filename)s %(asctime)s %(message)s'
logging.basicConfig(format=LOGGER_FORMAT, datefmt='[%H:%M:%S]')

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('--depth', type=int, default=4, help='Recursion depth')
arg_parser.add_argument('--url', type=str, help='Wiki-article URL', required=True)


async def main(loop, base_url, engine, db_session, max_depth):
    async with aiohttp.ClientSession(loop=loop) as session:
        now = datetime.now()
        parser = Crawler(loop, session, engine, db_session, max_depth)
        await parser.pre_cache()
        await parser.parse_page(base_url)
        logging.info(
            'Parsing with depth {} took {:.2f} seconds'.format(max_depth, (datetime.now() - now).total_seconds()))


if __name__ == "__main__":
    args = arg_parser.parse_args()
    engine, db_session = on_start_db()
    base_url = args.url
    max_depth = args.depth
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop, base_url, engine, db_session, max_depth))
    loop.close()
