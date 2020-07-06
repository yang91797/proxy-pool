from .utils import Page as get_page
from pyquery import PyQuery as pq
from proxypool.log import msg
import re
import time


class ProxyMetaclass(type):
    """
        元类，在FreeProxyGetter类中加入
        __CrawlFunc__和__CrawlFuncCount__
        两个参数，分别表示爬虫函数，和爬虫函数的数量。
    """

    def __new__(cls, name, bases, attrs):
        count = 0
        attrs['__CrawlFunc__'] = []
        for k, v in attrs.items():
            if 'crawl_' in k:
                attrs['__CrawlFunc__'].append(k)
                count += 1
        attrs['__CrawlFuncCount__'] = count
        return type.__new__(cls, name, bases, attrs)


class FreeProxyGetter(object, metaclass=ProxyMetaclass):

    def get_raw_proxies(self, callback):
        proxies = []
        print('Callback', callback)
        for proxy in eval("self.{}()".format(callback)):
            info = 'Getting  %s  from %s' % (proxy, callback)
            print(info)
            msg(info)
            proxies.append(proxy)
        return proxies

    def crawl_kuaidaili(self):
        for page in range(1, 4):
            # 国内高匿代理
            start_url = 'https://www.kuaidaili.com/free/inha/{}/'.format(page)
            html = get_page(start_url).get_p()
            ip_adress = re.compile(
                '<td data-title="IP">(.*)</td>\s*<td data-title="PORT">(\w+)</td>'
            )
            re_ip_adress = ip_adress.findall(str(html))
            for adress, port in re_ip_adress:
                result = adress + ':' + port

                res = result.replace(' ', '')

                yield res
        time.sleep(30)
                # 开放代理
        for page in range(1, 5):
            start_url = 'https://www.kuaidaili.com/ops/proxylist/{}/'.format(page)
            options = {
                'Host': 'www.kuaidaili.com',
                'Upgrade-Insecure-Requests': '1'
            }
            html = get_page(start_url, options=options).get_p()

            if html:
                doc = pq(html)
                text = doc("#freelist .table tbody tr td:nth-child(-n+2)").text().split(' ')

                for i, item in enumerate(text):
                    if i % 2 == 0:
                        ips = "%s:%s" % (item, text[i + 1])
                        yield ips

        time.sleep(60)
        for i in range(1, 4):
            start_url = 'https://www.kuaidaili.com/free/intr/{}/'.format(i)
            options = {
                'Host': 'www.kuaidaili.com',
                'Upgrade-Insecure-Requests': '1'
            }
            html = get_page(start_url, options=options).get_p()

            if html:
                doc = pq(html)
                text = doc("#list .table tbody tr td:nth-child(-n+2)").text().split(' ')
                for i, item in enumerate(text):
                    if i % 2 == 0:
                        ips = "%s:%s" % (item, text[i + 1])

                        yield ips

    def crawl_ihuan(self):
        # print('?????')
        # url = 'https://ip.ihuan.me/tqdl.html'
        # options = {
        #     'authority': 'ip.ihuan.me',
        #     'upgrade-insecure-requests': '1',
        #     'method': 'GET',
        #     'path': '/tqdl.html',
        #     'scheme': 'https',
        #     'cookie': '__cfduid=d072498ce36e615dea860d269bd9f06081547051697; Hm_lvt_8ccd0ef22095c2eebfe4cd6187dea829=1550409446,1550478213; cf_clearance=5d25f34b61c83053c92f562a03a6468b26879aca-1550498485-1800-220; Hm_lpvt_8ccd0ef22095c2eebfe4cd6187dea829=1550498501',
        #     'origin': 'https://ip.ihuan.me',
        #     'referer': 'https://ip.ihuan.me/ti.html',
        #
        # }
        # data = {
        #     'num': '100',
        #     'port': '',
        #     'kill_port': '',
        #     'anonymity': '2',
        #     'type': '',
        #     'post': '',
        #     'sort': '1',
        #     'key': '96c963d523c461a5d6602b7cf1e2c416'
        # }
        # html = get_page(url=url, options=options, data=data).get_p()
        # print(html, '???')
        # res = get_page(url='https://ip.ihuan.me/ti.html')
        # print(res)

        for i in ['b97827cc', '4ce63706', '5crfe930']:
            start_url = 'https://ip.ihuan.me/address/5Lit5Zu9.html?page={}'.format(i)
            path = start_url.split('ip.ihuan.me', maxsplit=1)[-1]

            html = get_page(start_url).get_p()
            # print(html, "???\n")
            if html:
                doc = pq(html)
                text = doc(".table tbody tr td:nth-child(-n+2)").text().split(' ')
                for i, item in enumerate(text):
                    if i % 2 == 0:
                        ips = "%s:%s" % (item, text[i + 1])

                        yield ips
            time.sleep(5)

    def crawl_ip3366_1(self):
        for s in range(1, 3):
            for page in range(5):
                start_url = 'http://www.ip3366.net/free/?stype={}&page={}'.format(s, page)
                options = {
                            'Host': 'www.ip3366.net',
                            'Upgrade-Insecure-Requests': '1'
                        }
                html = get_page(start_url, options=options).get_p()

                if html:
                    doc = pq(html)
                    text = doc("#list .table tbody tr td:nth-child(-n+2)").text().split(' ')
                    for i, item in enumerate(text):
                        if i % 2 == 0:
                            ips = "%s:%s" % (item, text[i + 1])
                            print(ips)
                            yield ips

    def crawl_66ip(self):
        start_url = 'http://www.66ip.cn/mo.php?sxb=%D6%D0%B9%FA&tqsl=30&port=&export=&ktip=&sxa=&submit=%CC%E1++%C8%A1&textarea=http%3A%2F%2Fwww.66ip.cn%2F%3Fsxb%3D%25D6%25D0%25B9%25FA%26tqsl%3D30%26ports%255B%255D2%3D%26ktip%3D%26sxa%3D%26radio%3Dradio%26submit%3D%25CC%25E1%2B%2B%25C8%25A1'
        options = {
            'Host': 'www.66ip.cn',
            'Referer': 'http://www.66ip.cn/pt.html'
        }
        html = get_page(start_url, encode='gbk').get_p()
        if html:
            doc = pq(html)
            text = doc("body").text().split('\n')
            for i in range(30):
                yield text[i]

    def crawl_nimadaili(self):

        for page in range(1, 3):
            start_url = 'http://www.nimadaili.com/gaoni/{}/'.format(page)
            options = {
                'Host': 'www.mayidaili.com',
                'Upgrade-Insecure-Requests': '1'
            }
            html = get_page(start_url, options=options).get_p()
            if html:
                doc = pq(html)
                text = doc(".fl-table tbody tr td:first-child").text().split(' ')
                for ip in text:
                    yield ip


