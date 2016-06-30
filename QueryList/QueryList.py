from ConfigManager.ConfigManager import ConfigManager
from StockQuery.StockQuery import StockQuery
import chardet
import pprint
import json
import os
import sys
import time


def trim_space(str):
    start = 0
    for char in str:
        if char == ' ':
            start += 1
        else:
            break
    stop = len(str)
    for char in str[::-1]:
        if char == ' ':
            stop -= 1
        else:
            break
    return str[start:stop]


def get_time(time_format='%Y-%m-%d_%H_%M_%S', seconds=None):
    return time.strftime(time_format, time.localtime(seconds))


def my_make_dir(result_dir):
    if not os.path.isdir(result_dir):
        if os.path.exists(result_dir):
            os.remove(result_dir)
        os.mkdir(result_dir)


class QueryList:
    def __init__(self):
        self.stock_list = ConfigManager.instance().get_stock_list()
        self.stock_type = ConfigManager.instance().get_stock_type()
        self.query_all = ConfigManager.instance().get_query_all()
        self.query = StockQuery()
        self.stock_info = {}
        self.result_dir = os.path.join(os.path.dirname(sys.path[0]), 'Result')

    def do_query(self):
        if self.stock_type == 'id':
            tmp_stock_list = self.stock_list.split(',')
            for stock_id in tmp_stock_list:
                stock_id = trim_space(stock_id)
                if self.query.do_query(stock_id):
                    self.stock_info[stock_id] = self.query.stock_info
        else:
            tmp_stock_list = self.stock_list.split(',')
            for stock_name in tmp_stock_list:
                stock_name = trim_space(stock_name).decode('utf-8')
                # print chardet.detect(stock_name)
                # {'confidence': 0.938125, 'encoding': 'utf-8'}
                if self.query.do_query_by_name(stock_name):
                    self.stock_info[stock_name] = self.query.stock_info

    def pprint(self):
        pprint.pprint(self.stock_info)

    def output_excel(self, header=None):
        my_make_dir(self.result_dir)
        result_file = os.path.join(self.result_dir, ".".join(["_".join(["result", get_time()]), "csv"]))
        output = open(result_file, 'w')
        content = ""
        first = True
        for stock_name in self.stock_info:
            # tmp_stock_info = json.loads(self.stock_info[stock_name])
            tmp_stock_info = self.stock_info[stock_name]
            if first:
                if not header or self.query_all == '1':
                    header = tmp_stock_info.keys()
                content = ",".join(header)
                first = False
            line = ""
            for item in header:
                if item == 'PriceChangeRatio':
                    tmp_stock_info[item] = (tmp_stock_info['currentPrice']
                    - tmp_stock_info['closingPrice']) / tmp_stock_info['closingPrice']
                if line:
                    line = ",".join([line, unicode(tmp_stock_info[item])])
                else:
                    line = unicode(tmp_stock_info[item])
            print "content: %s\nline: %s\n" % (content, line)
            content = "\n".join([content, line])
        content = "".join([content, "\n"])
        output.writelines(content.encode('gbk'))
        output.close()

if __name__ == '__main__':
    ql = QueryList()
    ql.do_query()
    ql.pprint()
    ql.output_excel(['code', 'name', 'date', 'time', 'closingPrice', 'currentPrice', 'PriceChangeRatio'])



