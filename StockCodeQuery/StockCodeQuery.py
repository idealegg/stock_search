# -*- coding: utf-8 -*-
import urllib2
import re
import pprint
import chardet
from bs4 import BeautifulSoup


class StockCodeQuery:
    def __init__(self):
        self.url_sh = 'http://quote.eastmoney.com/stocklist.html'
        self.url_sz = 'http://quote.eastmoney.com/stocklist.html#sz'
        self.stock_map = {}

    def get_html(self, exchange_name):
        if exchange_name == 'shanghai':
            url = self.url_sh
        else:
            url = self.url_sz
        req = urllib2.Request(url)
        resp = urllib2.urlopen(req)
        content = resp.read()
        #pprint.pprint(content)
        return content

    def get_stock_code(self, content):
        soup = BeautifulSoup(content, 'lxml')
        items_list = soup.find_all(name='a', target='_blank')
        #print soup.prettify()
        for item in items_list:
            match = re.search('(.*)\((\d+)\)', item.text)
            if match and item.has_attr('href'):
                name = match.group(1)
                code = match.group(2)
                match = re.search("".join(['..', code]), item['href'])
                if match:
                    code = match.group(0)
                    self.stock_map[name] = code

    def get_stock_code2(self, content):
        start = 0
        match = re.search('<li><a target="_blank" href="http://quote.eastmoney.com/(..(\d+))\.html">(.*?)(\(\\2\))',
                      content[start:])
        while match:
            name = match.group(3).decode('gbk')
            code = match.group(1)
            self.stock_map[name] = code
            start += match.end()
            match = re.search('<li><a target="_blank" href="http://quote.eastmoney.com/(..(\d+))\.html">(.*?)(\(\\2\))',
                      content[start:])

    def update(self):
        content = self.get_html('shanghai')
        self.get_stock_code2(content)
        #content = self.get_html('shenzhen')
        #self.get_stock_code(content)

    def pprint(self):
        #pprint.pprint(self.stock_map)
        for key in self.stock_map:
            # encoding = chardet.detect(key)['encoding']
            # tmp_key =
            print "%20s\t %10s\n" % (key, self.stock_map[key])

    @classmethod
    def instance(cls):
        # print "call instance"
        if not hasattr(cls, '__instance__'):
            cls.__instance__ = StockCodeQuery()
        return cls.__instance__

if __name__ == '__main__':
    scq = StockCodeQuery()
    scq.update()
    scq.pprint()
