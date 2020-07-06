import requests
import asyncio
import aiohttp
from requests.exceptions import ConnectionError
from fake_useragent import UserAgent,FakeUserAgentError
from proxypool.log import msg
import random
import time

class Page:

    def __init__(self, url, encode='utf-8', options={}, data=None):
        self.url = url
        self.options = options
        self.encode = encode
        self.data = data
        try:
            # self.proxy = get_proxy()
            self.proxy = {'http': 'http://170.84.112.224:8080', 'https': 'https://170.84.112.224:8080'}

        except Exception:
            self.proxy = None

    def get_p(self):
        # print('代理ip', proxy)
        count = 0
        try:
            ua = UserAgent()
        except FakeUserAgentError:
            pass
        base_headers = {
            'User-Agent':  ua.random,
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8'
        }
        headers = dict(base_headers, **self.options)
        print('Getting', self.url)
        try:
            r = requests.get(
                self.url,
                headers=headers,
                data=self.data,
                proxies=self.proxy
                )
            print(self.proxy, '**********')
            info = 'Getting result:%s  ： %s' % (self.url, r.status_code)
            print(info)
            msg(info)

            r.encoding = self.encode
            if r.status_code == 200:
                return r.text
            if r.status_code == 403:
                print(r.text)
                if count <= 1:
                    self.proxy = get_proxy()
                    self.get_p()
                    count += 1
        except ConnectionError:
            print('Crawling Failed', self.url)
            if count <= 1:
                self.proxy = get_proxy()
                self.get_p()
                count += 1

            return None


def get_proxy():
    r = requests.get('http://localhost:5000/get')
    proxy = {
        'http': 'http://%s' % r.text,
        'https': 'https://%s' % r.text
        }
    return proxy


class Downloader(object):
    """
    一个异步下载器，可以对代理源异步抓取，但是容易被BAN。
    """

    def __init__(self, urls):
        self.urls = urls
        self._htmls = []

    async def download_single_page(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                self._htmls.append(await resp.text())

    def download(self):
        loop = asyncio.get_event_loop()
        tasks = [self.download_single_page(url) for url in self.urls]
        loop.run_until_complete(asyncio.wait(tasks))

    @property
    def htmls(self):
        self.download()
        return self._htmls
