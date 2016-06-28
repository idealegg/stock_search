# -*- coding: utf-8 -*-
import urllib2
import chardet
import json
import pprint
from ConfigManager.ConfigManager import ConfigManager
from StockCodeQuery.StockCodeQuery import StockCodeQuery


class StockQuery:
    def __init__(self):
        self.url = ''
        self.req = None
        self.resp = None
        self.content = ''
        self.stock_info = {}
        self.api_key = ConfigManager.instance().get_api_key()

    def do_query(self, stock_id):
        self.url = 'http://apis.baidu.com/apistore/stockservice/stock?stockid=%s&list=0' % stock_id
        self.req = urllib2.Request(self.url)
        self.req.add_header("apikey", self.api_key)
        self.resp = urllib2.urlopen(self.req)
        self.content = self.resp.read()
        if self.content:
            print chardet.detect(self.content)
            print self.content+"\n"
            self.stock_info = json.loads(self.content)['retData']['stockinfo']
            return True
        return False

    def do_query_by_name(self, name):
        StockCodeQuery.instance().update()
        if name in StockCodeQuery.instance().stock_map:
            return self.do_query(StockCodeQuery.instance().stock_map[name])
        return False

    def pprint(self):
        pprint.pprint(self.stock_info)

if __name__ == '__main__':
    sq = StockQuery()
    #sq.do_query('sz000006')
    sq.do_query_by_name(u'中国中冶')
    sq.pprint()
