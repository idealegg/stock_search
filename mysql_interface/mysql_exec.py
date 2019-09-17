# -*- coding: utf-8 -*-
#
import os


mysql_dir=r'F:\Program Files\MySQL\MySQL Server 5.7\bin'
output_dir=r"F:\ProgramData\MySQL\MySQL Server 5.7\Uploads"
to_to_sql_path="to_do_sql"
out_result_path="out_result"

def execute_sql():
  if os.environ['PATH'].find(mysql_dir) == -1:
    os.environ['PATH'] = "".join([os.environ['PATH'], ";", mysql_dir])
  command="mysql -u gaia -pW3lcome gaia < %s > %s" % (to_to_sql_path, out_result_path)
  result=os.system(command)
  if result:
    print "Executed sql error!\n"
  else:
    print "Executed sql successfully!"
  return result

def get_stock_list(stocks_str):
  if not stocks_str:
    return []
  conditions = []
  for stock in stocks_str:
    if stock.isdigit():
      conditions.append("cast(b.code as char) like '%%%s%%'" % stock)
    else:
      if stock.startswith('^'):
        conditions.append("b.name like '%s%%'" % stock[1:])
      elif stock.endswith('$'):
        conditions.append("b.name like '%%%s_'" % stock[:-1])
      else:
        conditions.append("b.name like '%%%s%%'" % stock)
  condition_clause = " or ".join(conditions)
  command="select b.code from gaia.stock_list as b where %s\n" % condition_clause
  print "CMD:\n%s" % command
  f_sql = open(to_to_sql_path, "w")
  f_sql.write(command)
  f_sql.close()
  if not execute_sql():
    f_out=open(out_result_path, "r")
    buffer=f_out.read()
    #print "result: %s\n" % buffer
    return buffer.split("\n")[1:-1] # remove 'code' title and last LF
  return []

def format_stock(s):
  ##print s
  i = int(s)
  if i < 100000:
    return "sz%06d" % i
  if i / 100000 == 3:
    return "sz%06d" % i
  return "sh%06d" % i

def parse_stock(ss):
  ret = []
  to_select = []
  for s in ss:
    if s[0:2] == 'sz' or s[0:2] == 'sh':
      ret.append(s)
    else:
      ret.extend(map(format_stock, get_stock_list([s])))
  return ret

if __name__ == "__main__":
  print parse_stock([u'深赛'.encode('utf8'), '601058'])