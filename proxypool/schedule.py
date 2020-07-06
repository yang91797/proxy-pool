import time
from multiprocessing import Process
import asyncio
import aiohttp
try:
    from aiohttp.errors import ProxyConnectionError,ServerDisconnectedError,ClientResponseError,ClientConnectorError
except:
    from aiohttp import ClientProxyConnectionError as ProxyConnectionError,ServerDisconnectedError,ClientResponseError,ClientConnectorError
from proxypool.db import RedisClient
from proxypool.error import ResourceDepletionError
from proxypool.getter import FreeProxyGetter
from proxypool.setting import *
from asyncio import TimeoutError
from proxypool.log import msg


class ValidityTester(object):
    """
    测试ip是否可用
    """
    test_api = TEST_API

    def __init__(self):
        self._raw_proxies = None
        self._usable_proxies = []

    def set_raw_proxies(self, proxies):
        self._raw_proxies = proxies
        self._conn = RedisClient()

    async def test_single_proxy(self, proxy):
        """
        text one proxy, if valid, put them to usable_proxies.
        """
        try:
            async with aiohttp.ClientSession() as session:
                try:
                    if isinstance(proxy, bytes):
                        proxy = proxy.decode('utf-8')
                    real_proxy = 'http://' + proxy
                    print('Testing', proxy)
                    async with session.get(self.test_api, proxy=real_proxy, timeout=get_proxy_timeout) as response:
                        if response.status == 200:
                            self._conn.put(proxy)
                            print('Valid proxy', proxy)
                except (ProxyConnectionError, TimeoutError, ValueError):
                    print('Invalid proxy', proxy)
        except (ServerDisconnectedError, ClientResponseError,ClientConnectorError) as s:
            print(s)
            msg('测试出错：%s' % s)
            pass

    def test(self):
        """
        aio test all proxies.
        """
        print('ValidityTester is working')
        try:
            loop = asyncio.get_event_loop()
            tasks = [self.test_single_proxy(proxy) for proxy in self._raw_proxies]
            loop.run_until_complete(asyncio.wait(tasks))
        except ValueError as e:
            print('Async Error')
            msg('Async Error: %s' % e)


class PoolAdder(object):
    """
    add proxy to pool
    """

    def __init__(self, threshold):
        self._threshold = threshold             # ip池最大数量
        self._conn = RedisClient()
        self._tester = ValidityTester()
        self._crawler = FreeProxyGetter()           # 爬取ip

    def is_over_threshold(self):
        """
        judge if count is overflow.
        ip池是否满了
        """
        if self._conn.queue_len >= self._threshold:
            return True
        else:
            return False

    def add_to_queue(self):
        """
        增加队列
        :return:
        """
        print('PoolAdder is working')
        proxy_count = 0
        while not self.is_over_threshold():
            for callback_label in range(self._crawler.__CrawlFuncCount__):

                callback = self._crawler.__CrawlFunc__[callback_label]
                raw_proxies = self._crawler.get_raw_proxies(callback)
                # test crawled proxies
                self._tester.set_raw_proxies(raw_proxies)
                self._tester.test()
                proxy_count += len(raw_proxies)
                if self.is_over_threshold():
                    print('IP is enough, waiting to be used')
                    msg('IP is enough, waiting to be used')
                    break
            if proxy_count == 0:
                raise ResourceDepletionError

            time.sleep(ADD_IP_CYCLE)


class Schedule(object):
    @staticmethod
    def valid_proxy(cycle=VALID_CHECK_CYCLE):
        """
        Get half of proxies which in redis
        """
        conn = RedisClient()
        tester = ValidityTester()
        while True:
            print('Refreshing ip')
            count = int(0.5 * conn.queue_len)
            if count == 0:
                print('Waiting for adding')
                time.sleep(cycle)
                continue
            raw_proxies = conn.get(count)
            tester.set_raw_proxies(raw_proxies)
            tester.test()
            time.sleep(cycle)

    @staticmethod
    def check_pool(lower_threshold=POOL_LOWER_THRESHOLD,            # ip池最低数量
                   upper_threshold=POOL_UPPER_THRESHOLD,            # ip池最大数量
                   cycle=POOL_LEN_CHECK_CYCLE):                     # ip池满后的检查时间
        """
        If the number of proxies less than lower_threshold, add proxy
        """
        conn = RedisClient()            # 链接redis
        adder = PoolAdder(upper_threshold)      # 添加ip
        while True:
            if conn.queue_len < upper_threshold:
                adder.add_to_queue()

            time.sleep(cycle)

    def run(self):
        print('Ip processing running')
        valid_process = Process(target=Schedule.valid_proxy)
        check_process = Process(target=Schedule.check_pool)
        valid_process.start()
        check_process.start()
