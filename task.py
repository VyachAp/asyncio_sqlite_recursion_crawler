import asyncio
import logging
import uuid
from lxml import html as html
from sqlalchemy import inspect
from db import pages, relations

LOGGER_FORMAT = '%(filename)s %(asctime)s %(message)s'
logging.basicConfig(format=LOGGER_FORMAT, datefmt='[%H:%M:%S]')


class Crawler:
    def __init__(self, loop, session, engine, db_session, max_depth=6):
        self.max_depth = max_depth
        self.domain = 'https://en.wikipedia.org'
        self.loop = loop
        self.session = session
        self.cached_urls = []
        self.engine = engine
        self.db_session = db_session

    async def pre_cache(self):
        with self.engine.connect() as conn:
            results = conn.execute(pages.select())
            for row in results:
                row_as_dict = dict(row)
                url = row_as_dict['url']
                self.cached_urls.append(url)

    async def update_pages_table(self, urls, depth):
        with self.engine.connect() as conn:
            for each in urls:
                if each not in self.cached_urls:
                    self.cached_urls.append(each)
                    if len(self.cached_urls) % 100 == 0:
                        print(f'Crawled {len(self.cached_urls)} links')
                    conn.execute(pages.insert().values({'id': str(uuid.uuid4()), 'url': each, 'request_depth': depth}))

    async def update_relatives_table(self, parent_url, urls):
        with self.engine.connect() as conn:
            result = conn.execute(pages.select().where(pages.columns.url == parent_url))
            for row in result:
                row_as_dict = dict(row)
                parent_id = row_as_dict['id']
                for each in urls:
                    each_result = conn.execute(pages.select().where(pages.columns.url == each))
                    for each_row in each_result:
                        each_as_dict = dict(each_row)
                        each_id = each_as_dict['id']
                        conn.execute(relations.insert().values({'from_page_id': parent_id, 'link_id': each_id}))

    def get_url_list(self, resp):
        tree = html.fromstring(resp)
        subtree = tree.xpath('//div[@id="bodyContent"]')[0]
        return {self.domain + i for i in subtree.xpath("*//a/@href") if i.startswith('/wiki')}

    async def get_url_content(self, url, failed=False):
        try:
            async with self.session.get(url) as resp:
                return await resp.text()
        except Exception as e:
            if failed:
                logging.info('{}: Failed to process {} again'.format(e, url))
            logging.info('{}: Failed to process {}, retrying'.format(e, url))
            return await self.get_url_content(url, True)

    async def parse_page(self, parent_url, depth=0):
        if depth == 0:
            if parent_url not in self.cached_urls:
                with self.engine.connect() as conn:
                    conn.execute(pages.insert().values({'id': str(uuid.uuid4()), 'url': parent_url, 'request_depth': 0}))
        response = await self.get_url_content(parent_url)
        url_list = []
        if response:
            url_list = self.get_url_list(response)

        current_depth = depth + 1
        await self.update_pages_table(url_list, current_depth)
        await self.update_relatives_table(parent_url, url_list)
        logging.info('{} found {} urls'.format(parent_url, len(url_list)))
        if current_depth < self.max_depth:
            tasks = [self.parse_page(url, current_depth) for url in url_list]
            await asyncio.gather(*tasks)
