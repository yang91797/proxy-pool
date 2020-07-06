from proxypool.utils import Page as get_page
from pyquery import PyQuery as pq
import re
import time
import requests


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
    print('llll')
    def get_raw_proxies(self, callback):
        proxies = []
        print('Callback', callback)
        for proxy in eval("self.{}()".format(callback)):
            print('Getting', proxy, 'from', callback)
            proxies.append(proxy)
        return proxies

    def crawl_ip181(self):
        start_url = 'http://www.ip181.com/'
        html = get_page(start_url)
        ip_adress = re.compile('<tr.*?>\s*<td>(.*?)</td>\s*<td>(.*?)</td>')
        # \s* 匹配空格，起到换行作用
        re_ip_adress = ip_adress.findall(str(html))
        for adress, port in re_ip_adress:
            result = adress + ':' + port
            yield result.replace(' ', '')

    def crawl_kuaidaili(self):
        for page in range(1, 4):
            # 国内高匿代理
            start_url = 'https://www.kuaidaili.com/free/inha/{}/'.format(page)
            html = get_page(start_url)
            ip_adress = re.compile(
                '<td data-title="IP">(.*)</td>\s*<td data-title="PORT">(\w+)</td>'
            )
            re_ip_adress = ip_adress.findall(str(html))
            for adress, port in re_ip_adress:
                result = adress + ':' + port

                res = result.replace(' ', '')

                yield res

    def crawl_xicidaili(self):
        for page in range(1, 4):
            start_url = 'http://www.xicidaili.com/wt/{}'.format(page)
            html = get_page(start_url)
            ip_adress = re.compile(
                '<td class="country"><img src="http://fs.xicidaili.com/images/flag/cn.png" alt="Cn" /></td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>'
            )
            # \s* 匹配空格，起到换行作用
            re_ip_adress = ip_adress.findall(str(html))
            for adress, port in re_ip_adress:
                result = adress + ':' + port
                yield result.replace(' ', '')

    def crawl_daili66(self, page_count=4):
        start_url = 'http://www.66ip.cn/{}.html'
        urls = [start_url.format(page) for page in range(1, page_count + 1)]
        for url in urls:
            print('Crawling', url)
            html = get_page(url)
            if html:
                doc = pq(html)
                trs = doc('.containerbox table tr:gt(0)').items()
                for tr in trs:
                    ip = tr.find('td:nth-child(1)').text()
                    port = tr.find('td:nth-child(2)').text()
                    yield ':'.join([ip, port])

    def crawl_data5u(self):
        for i in ['gngn', 'gnpt']:
            start_url = 'http://www.data5u.com/free/{}/index.shtml'.format(i)
            html = get_page(start_url)
            ip_adress = re.compile(
                ' <ul class="l2">\s*<span><li>(.*?)</li></span>\s*<span style="width: 100px;"><li class=".*">(.*?)</li></span>'
            )
            # \s * 匹配空格，起到换行作用
            re_ip_adress = ip_adress.findall(str(html))
            for adress, port in re_ip_adress:
                result = adress + ':' + port
                yield result.replace(' ', '')

    def crawl_kxdaili(self):
        for i in range(1, 4):
            start_url = 'http://www.kxdaili.com/ipList/{}.html#ip'.format(i)
            html = get_page(start_url)
            ip_adress = re.compile('<tr.*?>\s*<td>(.*?)</td>\s*<td>(.*?)</td>')
            # \s* 匹配空格，起到换行作用
            re_ip_adress = ip_adress.findall(str(html))
            for adress, port in re_ip_adress:
                result = adress + ':' + port
                yield result.replace(' ', '')

    def crawl_premproxy(self):
        for i in ['China-01', 'China-02', 'China-03', 'China-04', 'Taiwan-01']:
            start_url = 'https://premproxy.com/proxy-by-country/{}.htm'.format(
                i)
            html = get_page(start_url)
            if html:
                ip_adress = re.compile('<td data-label="IP:port ">(.*?)</td>')
                re_ip_adress = ip_adress.findall(str(html))
                for adress_port in re_ip_adress:
                    yield adress_port.replace(' ', '')

    def crawl_xroxy(self):
        for i in ['CN', 'TW']:
            start_url = 'http://www.xroxy.com/proxylist.php?country={}'.format(
                i)
            html = get_page(start_url)
            if html:
                ip_adress1 = re.compile(
                    "title='View this Proxy details'>\s*(.*).*")
                re_ip_adress1 = ip_adress1.findall(str(html))
                ip_adress2 = re.compile(
                    "title='Select proxies with port number .*'>(.*)</a>")
                re_ip_adress2 = ip_adress2.findall(html)
                for adress, port in zip(re_ip_adress1, re_ip_adress2):
                    adress_port = adress + ':' + port
                    yield adress_port.replace(' ', '')

    def crawl_ihuan(self):
        print('llll')
        # start_url = 'https://ip.ihuan.me/address/5Lit5Zu9.html'
        for i in ['b97827cc', '4ce63706', '5crfe930']:
            start_url = 'https://ip.ihuan.me/address/5Lit5Zu9.html?page={}'.format(i)
            path = start_url.split('ip.ihuan.me', maxsplit=1)[-1]
            print(path)
            # html = get_page(start_url, options={'upgrade-insecure-requests': '1'})
            # # print(html, "???\n")
            # if html:
            #     doc = pq(html)
            #     text = doc(".table tbody tr td:nth-child(-n+2)").text().split(' ')
            #     for i, item in enumerate(text):
            #         if i % 2 == 0:
            #             ips = "%s:%s" % (item, text[i + 1])
            #             print(ips)

            time.sleep(5)
        # yield "114.119.116.92:61066"


# FreeProxyGetter().crawl_ihuan()

# st = '58.243.56.148 8060 116.209.57.108 9999 116.209.54.139 9999 159.226.140.15 3128 218.205.30.61 53281 221.2.174.6 8060 120.79.180.39 3128 139.159.231.74 8088 116.209.52.12 9999 61.164.39.69 53281 222.135.92.105 8060 140.143.142.14 1080 121.61.2.116 9999 183.230.175.93 8060 124.206.234.126 3128 116.209.54.179 9999 221.235.235.224 9999 114.95.166.108 8060'
# print(st.split(' '))
# st = st.split(' ')
# for i, item in enumerate(st):
#     if i % 2 == 0:
#         ips = "%s:%s" % (item, st[i+1])
#         print(ips)

# def get_page(url, options={}):
#     print(options)
#     print(**options)
#     base_headers = {
#         'Accept-Encoding': 'gzip, deflate, sdch',
#         'Accept-Language': 'zh-CN,zh;q=0.8'
#     }
#     headers = dict(base_headers, **options)
#     print('Getting', headers)
#
#
# get_page('ooo', options={'21321': '000', 'sis': 'iwiwjid'})

def foo():
    proxy = {'https': 'https://60.246.205.255:53281'}

    for i in ['b97827cc', '4ce63706', '5crfe930']:
        start_url = 'https://ip.ihuan.me/address/5Lit5Zu9.html?page={}'.format(i)
        path = start_url.split('ip.ihuan.me', maxsplit=1)[-1]
        print(path)
        options = {
            'authority': 'ip.ihuan.me',
            'upgrade-insecure-requests': '1',
            'method': 'GET',
            'path': path,
            'scheme': 'https',
            'referer': 'https://ip.ihuan.me/address/5Lit5Zu9.html?page=b97827cc',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
            'cookie': '__cfduid=d072498ce36e615dea860d269bd9f06081547051697; Hm_lvt_8ccd0ef22095c2eebfe4cd6187dea829=1550409446,1550478213; cf_clearance=5d25f34b61c83053c92f562a03a6468b26879aca-1550498485-1800-220; Hm_lpvt_8ccd0ef22095c2eebfe4cd6187dea829=1550498501'
        }
        # html = get_page(start_url, options={})
        # print(html, "???\n")
        html = requests.get(
            url=start_url,
            headers=options,
            proxies=proxy
        )
        print(html.text)
        if html:
            doc = pq(html)
            text = doc(".table tbody tr td:nth-child(-n+2)").text().split(' ')
            for i, item in enumerate(text):
                if i % 2 == 0:
                    ips = "%s:%s" % (item, text[i + 1])
                    print(ips, '??????')


# foo()

# proxy = {'http': 'http://58.254.220.116:53579', 'https': 'https://58.254.220.116:53579'}
# options = {
#     'referer': 'https://ip.ihuan.me/address/5Lit5Zu9.html?page=b97827cc',
#     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
#     'cookie': '__cfduid=d072498ce36e615dea860d269bd9f06081547051697; Hm_lvt_8ccd0ef22095c2eebfe4cd6187dea829=1550409446,1550478213; cf_clearance=5d25f34b61c83053c92f562a03a6468b26879aca-1550498485-1800-220; Hm_lpvt_8ccd0ef22095c2eebfe4cd6187dea829=1550498501'
# }
# r = requests.get(
#     url='https://www.baidu.com/s?ie=utf8&oe=utf8&tn=98010089_dg&ch=11&wd=ip',
#     headers=options,
#     proxies=proxy
# )
# print(r.text)

import threading
import time

def run():

    time.sleep(2)
    print('当前线程的名字是： ', threading.current_thread().name)
    time.sleep(2)


if __name__ == '__main__':

    start_time = time.time()

    print('这是主线程：', threading.current_thread().name)
    thread_list = []
    for i in range(5):
        t = threading.Thread(target=run)
        thread_list.append(t)
        t.start()
    # for t in thread_list:
    #     t.setDaemon(True)
    #     t.start()

    for t in thread_list:
        t.join()

    print('主线程结束了！' , threading.current_thread().name)
    print('一共用时：', time.time()-start_time)