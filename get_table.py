import json

fd=open('stock_list.txt')
s=fd.read()
fd.close()
j=json.loads(s)



>>> to_to_sql_path="to_do_sql"
>>> out_result_path="out_result"
>>> command="mysql -u gaia -pW3lcome gaia < %s > %s" % (to_to_sql_path, out_result_path)


>>> fd=open('tmp_stock', 'w')
>>> out=[]
>>> for stock in j[u'data'][u'diff']:
...     out.append(",".join([stock[u'f12'], stock[u'f14']]))
...
>>> len(out)


>>> fd.write("\n".join(out).encode('utf8'))
>>> fd.close()


>>> output_dir=r"F:\ProgramData\MySQL\MySQL Server 5.7\Uploads"
>>> out_file=os.path.join(output_dir, 'tmp_stock')
>>> d="load data infile '%s' into table %s fields terminated by ',' optionally e
nclosed by '\"' escaped by '\"' lines terminated by '\\n';\n" % (out_file.replac
e('\\', '\\\\'), 'gaia.stock_list')
>>> f_sql=open(to_to_sql_path, "w")
>>> f_sql.write(d)
>>> f_sql.close()
>>> result=os.system(command)