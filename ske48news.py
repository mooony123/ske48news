from bs4 import BeautifulSoup
from datetime import datetime
import pprint
import re
import aiohttp
import asyncio
import json
import os

last_news = []

def json_dump(info):
    with open('ske48news.json', 'w') as f:
        json.dump(info, f)

def json_load():
    if os.path.exists('ske48news.json'):
        with open('ske48news.json') as f:
            return json.load(f)
    else:
        return []

async def get_news_page(page: int) -> list:
    async def get(page, aiohttpsession) -> str:
        url = f'https://ske48.co.jp/news/29/?page={page}'
        async with aiohttpsession.get(url=url) as resp:
            page = await resp.text()
        return page

    async with aiohttp.ClientSession() as session:
        page = await get(page, session)

    soup = BeautifulSoup(page, 'html.parser')
    list_info = soup.find('ul', class_='list--info')
    retval = []
    for entry in list_info.find_all('li'):
        url = 'https://ske48.co.jp' + entry.find('a')['href']
        catsoup = entry.find('span', class_='cat')
        cat = catsoup['class'][1]
        cattxt = catsoup.get_text()
        date = entry.find('p', class_='date').get_text()
        title = entry.find('p', class_='tit').get_text()
        #not goods or stream
        if (cat != 'category--27') and (cat != 'category--14'):
            retval.append({'url': url, 'cat': cattxt, 'date': date, 'title': title})
    return retval

async def get_news() -> list:
    return await get_news_page(1)

async def get_new_news_items():
    curr_news = await get_news()
    new_news = [i for i in curr_news if i['url'] not in [o['url'] for o in last_news]]
    if len(new_news):
        json_dump(curr_news)
    return new_news

def news_item_to_str(item: dict) -> str:
    return f'{item["cat"]} {item["date"]}\n{item["title"]} <{item["url"]}>'

async def get_new_news_items_str():
    new_news = await get_new_news_items()
    return [news_item_to_str(item) for item in new_news]

async def init():
    if os.path.exists('ske48news.json'):
        last_news.extend(json_load())
    else:
        await get_new_news_items()

async def main():
    last_news.extend(json_load())
    new_news = await get_new_news_items()
    for item in new_news:
        print(news_item_to_str(item))
    pprint.pprint(await get_new_news_items_str())

if __name__ == '__main__':
    asyncio.run(main())

