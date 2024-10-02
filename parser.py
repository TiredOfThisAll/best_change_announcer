import requests
import aiohttp
from bs4 import BeautifulSoup
import re
import asyncio

user_from_curr = "privat24-uah"
user_to_curr = "psbank"


def sync_extract_html_content(url):
    return requests.get(url).text


async def extract_html_content(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.text()
            else:
                raise Exception(f"Error fetching {url}: {response.status}")


async def parse_currencies_from_html(url):
    html_content = await extract_html_content(url)

    soup = BeautifulSoup(html_content, 'html.parser')

    script_tag = soup.find('script', text=lambda x: 'var session_params' in str(x))

    script_content = script_tag.string

    extracted_data = {}

    for match in re.findall(r'(cu_list = new Array\()(.*?)\)', script_content):
        key, value = match
        if "'" in value:
            value = value[1:-1].split("', '")
        else:
            value = value.split(", ")
        extracted_data[key.split(" ")[0]] = value
    
    print(extracted_data['cu_list'])

    return extracted_data['cu_list']


async def craft_link(url, from_curr, to_curr):
    return url + from_curr + "-to-" + to_curr + ".html"


async def parse_best_rate(url):
    html_content = await extract_html_content(url)

    soup = BeautifulSoup(html_content, 'html.parser')

    table = soup.find('table', id="content_table")
    if not table:
        return None

    header = []
    thead = table.find('thead')
    tds = thead.findChildren("td")
    give_index, get_index = [tds.index(td) for td in tds if 'Give' in td.text or 'Get' in td.text]

    tbody = table.find('tbody')
    trs = tbody.findChildren("tr")
    first_row = trs[0]
    tds = first_row.findChildren("td")
    give_col = tds[give_index]
    get_col = tds[get_index]

    pattern = "(\d+(\.\d*)?|\.\d +)"
    give_rate = float(re.search(pattern, give_col.text)[0])
    get_rate = float(re.search(pattern, get_col.text)[0])
    rate, ascending = [get_rate, True] if get_rate > give_rate else [give_rate, False]

    print(rate, ascending)
    
    return rate, ascending
