# -*- coding: utf-8 -*-

import requests
import pprint
import time
import ConfigParser
import win32api
import win32con
import re
import chardet
import threading
import mysql_interface.mysql_exec
import TestTaskbarIcon.TestTaskbarIcon


class MointorStock:
  def __init__(self, conf_path):
    self.TRIGGER_BUY_1_MONITOR = 'monitor_buy_1'
    self.JUST_PRINT = 'just_print'
    self.config_parser = ConfigParser.ConfigParser()
    self.conf_path = conf_path
    self.work_time = (('0930', '1130'), ('1300', '1457')
                      , ('0000', '2359')
                      )
    self.conf = {'interval': 10,
                 'retry_interval': 60,
                 'report_interval': 60,
                 'line_length': 240,
                 self.TRIGGER_BUY_1_MONITOR: {
                                    'min_trade_vol': 5000.0,
                                    'min_trade_rate': 0.1,
                                    'min_buy_1_vol': 10000.0,
                                    'stock' : []
                  },
                 self.JUST_PRINT : {
                                    'stock' : [],
                                    'hold'  : [],

                 }
                 }
    self.base_url = 'http://qt.gtimg.cn/q=%s'
    #self.stock_list = []
    self.trigger = {self.TRIGGER_BUY_1_MONITOR: self.monitor_buy_1,
                    self.JUST_PRINT : self.get_new_msg}
    self.trigger_list = []
    self.last_msg = {}
    self.cur_msg = {}
    self.warning_list = []
    self.warning_msg = ''
    self.cur_trigger = None
    self.print_out_list = [(1,  2, 3,  4, 5, 32, 33, 34, 38, 43, 6, 9, 10),
                           (13, 7, 13, 8, 8, 8,  8,  8, 10, 8, 19, 8, 19)]
    self.printed_header = False
    self.first = True
    self.msg_prop = TestTaskbarIcon.TestTaskbarIcon.TestTaskbarIcon()
    self.Field_content = {0: '未知',
                 1: '名字',
                 2: '代码',
                 3: '当前价格',
                 4: '昨收',
                 5: '今开',
                 6: '成交量（手）',
                 7: '外盘',
                 8: '内盘',
                 9: '买一',
                 10: '买一量（手）',
                 11: '买二',
                 12: '买二量（手）',
                 13: '买三',
                 14: '买三量（手）',
                 15: '买四',
                 16: '买四量（手）',
                 17: '买五',
                 18: '买五量（手）',
                 19: '卖一',
                 20: '卖一量',
                 19: '卖二',
                 20: '卖二量',
                 19: '卖三',
                 20: '卖三量',
                 19: '卖四',
                 20: '卖四量',
                 19: '卖五',
                 20: '卖五量',
                 29: '最近逐笔成交',
                 30: '时间',
                 31: '涨跌',
                 32: '涨跌%',
                 33: '最高',
                 34: '最低',
                 35: '价格/成交量（手）/成交额',
                 36: '成交量（手）',
                 37: '成交额（万）',
                 38: '换手率',
                 39: '市盈率',
                 40: '',
                 41: '最高',
                 42: '最低',
                 43: '振幅',
                 44: '流通市值',
                 45: '总市值',
                 46: '市净率',
                 47: '涨停价',
                 48: '跌停价'
                 }

  def read_conf(self):
    if not self.conf_path:
      self.conf_path = 'parameters.ini'
    self.config_parser.read(self.conf_path)
    self.conf.update(dict(self.config_parser.items('GLOBAL')))
    self.trigger_list = re.split(re.compile('[,\s]+'), self.conf['trigger'])
    #self.stock_list = re.split(re.compile('[,\s]+'), self.conf['stock'])
    if self.config_parser.has_section(self.TRIGGER_BUY_1_MONITOR):
      self.conf[self.TRIGGER_BUY_1_MONITOR] = dict(self.config_parser.items(self.TRIGGER_BUY_1_MONITOR))
      self.conf[self.TRIGGER_BUY_1_MONITOR]['stock'] = mysql_interface.mysql_exec.parse_stock(
                                        re.split(re.compile('[,\s]+'), self.conf[self.TRIGGER_BUY_1_MONITOR]['stock']))
    if self.config_parser.has_section(self.JUST_PRINT):
      self.conf[self.JUST_PRINT] = dict(self.config_parser.items(self.JUST_PRINT))
      self.conf[self.JUST_PRINT]['stock'] = mysql_interface.mysql_exec.parse_stock(
                                        re.split(re.compile('[,\s]+'), self.conf[self.JUST_PRINT]['stock']))
      if self.conf[self.JUST_PRINT].has_key('hold'):
        tmp = re.split(re.compile('[,\s]+'), self.conf[self.JUST_PRINT]['hold'])
        self.conf[self.JUST_PRINT]['hold'] = {}
        for t in tmp:
          t1 = t.split(":")
          if len(t1) > 3:
            s = mysql_interface.mysql_exec.parse_stock([t1[0]])[0]
            self.conf[self.JUST_PRINT]['hold'][s] = {}
            self.conf[self.JUST_PRINT]['hold'][s]['cost'] = float(t1[1])
            self.conf[self.JUST_PRINT]['hold'][s]['vol'] = int(t1[2])
            self.conf[self.JUST_PRINT]['hold'][s]['today'] = t1[3] == 'Y'
            self.conf[self.JUST_PRINT]['stock'].extend([s])

  def warning(self):
    print self.warning_msg.decode('gbk')
    self.warning_list.append("%s: %s: %s" % (time.ctime(), self.cur_trigger, self.warning_msg))
    t1 = threading.Thread(target=win32api.MessageBox, args=(0, self.warning_msg,
                "%s %s" % (self.cur_trigger, time.ctime()),
                win32con.MB_OK | win32con.MB_ICONWARNING))
    t1.start()
    self.msg_prop.showMsg(self.cur_trigger, self.warning_msg)
    #win32api.MessageBox(0, self.warning_msg,
    #                       "%s %s" %(self.cur_trigger, time.ctime()),
    #                       win32con.MB_OK | win32con.MB_ICONWARNING)

  def get_new_msg(self, stock):
    while True:
      try:
        req = requests.get(self.base_url % stock)
      except Exception, e:
        print "Exception in get_new_msg:"
        print e.message
        time.sleep(float(self.conf['retry_interval']))
        continue
      break
    #print req
    #print req.encoding
    #print req.content
    if self.cur_msg.has_key(stock):
      self.last_msg[stock] = self.cur_msg[stock]
    self.cur_msg[stock] = []
    self.cur_msg[stock] = req.content.split('~')
    encoding = req.encoding
    #print stock
    #print self.cur_msg[stock]
    #print self.cur_msg[stock][1]
    self.cur_msg[stock][1] = self.cur_msg[stock][1].decode(encoding).encode('utf8')
    req.close()
    #pprint.pprint(self.cur_msg[stock])
    self.print_stock_info(stock)
    #return self.cur_msg[stock][1]

  def print_stock_info2(self, stock):
    s = ''
    if self.cur_msg.has_key(stock):
      for field in self.print_out_list[0]:
        s = ', '.join([s, "%s: %s" % (self.Field_content[field], self.cur_msg[stock][field])])
        if len(s) > int(self.conf['line_length']):
          print s
          s = ''
      print s

  def print_stock_info(self, stock):
    l1 = ''
    l2 = ''
    if self.cur_msg.has_key(stock):
      i = 0
      #if self.first:
      #  self.print_out_list[1] = [0] * len(self.print_out_list[0])
      for field in self.print_out_list[0]:
        #if self.first:
        #  self.print_out_list[1][i] = max(self.print_out_list[1][i],
        #      max(len(self.Field_content[field].strip()), len(self.cur_msg[stock][field].strip())) + 1)
        #print '[%-18s][%d]' % (self.Field_content[field].strip(), len(self.Field_content[field].strip()))
        #print '[%-18s][%d]' % (self.cur_msg[stock][field].strip(), len(self.cur_msg[stock][field].strip()))
        l1 = " ".join([l1, "%-*s" % (self.print_out_list[1][i] + len(self.Field_content[field].strip())/3,
                                     self.Field_content[field].strip())])
        l2 = " ".join([l2, "%-*s" % (self.print_out_list[1][i] if (field != 1) else
                                       self.print_out_list[1][i] + len(self.cur_msg[stock][field].strip())/3,
                                     self.cur_msg[stock][field].strip())])
        i += 1
      l1 = '' if self.printed_header else "".join(["\n%s | Trigger [%s]:\n" % (time.ctime(), "just_print"), l1, '开盘涨跌', '\n'])
      self.printed_header = True
      self.first = False
      print "%s%s%-.2f" % (l1, l2, float(self.cur_msg[stock][5])/float(self.cur_msg[stock][4]) *100 - 100)

  def monitor_buy_1(self, stock):
    self.get_new_msg(stock)
    #self.TRIGGER_BUY_1_MONITOR = 'monitor_buy_1'
    if self.last_msg.has_key(stock):
      if self.last_msg[stock][9] != self.cur_msg[stock][9]:
        self.cur_trigger = self.TRIGGER_BUY_1_MONITOR
        self.warning_msg = "%s buy_1 price decreased from %s to %s!" % (
                     self.cur_msg[stock][1].decode('utf8').encode('gbk'),
                     self.last_msg[stock][9], self.cur_msg[stock][9])
        self.warning()
        return
      #self.print_stock_info(stock)
      last = float(self.last_msg[stock][10])   # buy_1 trade volume
      cur = float(self.cur_msg[stock][10])
      #pprint.pprint(self.conf)
      if last - cur > float(self.conf[self.TRIGGER_BUY_1_MONITOR]['min_trade_vol']) \
        or (last - cur)/last > float(self.conf[self.TRIGGER_BUY_1_MONITOR]['min_trade_rate']) \
        or cur < float(self.conf[self.TRIGGER_BUY_1_MONITOR]['min_buy_1_vol']):
        self.cur_trigger = self.TRIGGER_BUY_1_MONITOR
        self.warning_msg = "%s buy_1 trade vol decreased from %s to %s!" % (
          self.cur_msg[stock][1].decode('utf8').encode('gbk'), last, cur)
        self.warning()

  def print_cost(self):
    if self.conf[self.JUST_PRINT].has_key('hold'):
      all_cost = 0.0
      day_cost = 0.0
      for stock in self.conf[self.JUST_PRINT]['hold'].keys():
        all_cost += (float(self.cur_msg[stock][9]) - self.conf[self.JUST_PRINT]['hold'][stock]['cost']
                     ) * self.conf[self.JUST_PRINT]['hold'][stock]['vol']
        day_cost += (float(self.cur_msg[stock][9]) - (float(self.cur_msg[stock][4])
             if not self.conf[self.JUST_PRINT]['hold'][stock]['today'] else self.conf[self.JUST_PRINT]['hold'][stock]['cost']
                    )) * self.conf[self.JUST_PRINT]['hold'][stock]['vol']
      print "All cost: %.02f, Day cost: %.02f\n" % (all_cost, day_cost)


  def is_in_working_time(self, t=None):
    t1 = time.localtime(t)
    d = time.strftime("%y%m%d", t1)
    #print "\n--- check time: %s" % time.strftime("%y-%m-%d %H:%M:%S", t1)
    for seg in self.work_time:
      start_time = time.strptime(''.join([d,seg[0]]), '%y%m%d%H%M')
      end_time = time.strptime(''.join([d,seg[1]]), '%y%m%d%H%M')
      t = time.mktime(t1)
      if t >= time.mktime(start_time) and t <= time.mktime(end_time):
        return True
    return False

if __name__ == "__main__":
  ms = MointorStock('p.ini')
  ms.read_conf()
  count = 0
  while True:
    if ms.is_in_working_time():
      for t in ms.trigger_list:
        for stock in ms.conf[t]['stock']:
          #print "\n%s | Trigger [%s]: [%s]" % (time.ctime(), t, stock)
          ms.trigger[t](stock)
    else:
      print "current is not working time!"
    ms.print_cost()
    time.sleep(float(ms.conf['interval']))
    count += 1
    ms.printed_header = False
    if float(ms.conf['interval']) * count > float(ms.conf['report_interval']):
      pprint.pprint(ms.warning_list)
      count = 0
