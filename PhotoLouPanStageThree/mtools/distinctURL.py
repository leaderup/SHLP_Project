#!/usr/bin/env python
#coding: utf8

import torndb
"""
通过临时表创建无重复URL拉取序列
临时表创建命令：

"""

passwd = '123456'
table = 'lp_photo_links'
table_t = 'lp_photo_links_t'
table_t_t = 'lp_photo_links_t_t'
table_1 = 'lp_photo_links_1'

conn = torndb.Connection(host="192.168.1.119", database="data_transfer", user="frem", password=passwd)
sql_str = "select * from %s" % table_1
rows = conn.query(sql_str)

db_dict = {}
f = open("d:/xsx.txt")
db_index = f.read()
f.close()
db_dict = eval(db_index)

f = open("d:/%s_2.txt" % table, 'w')
i = 0
for row in rows:
    i = i + 1
    mid = row['id']
    url = row['url']
    tmp_id = db_dict[url]
    if tmp_id == mid:
        row['samelink'] = 0
    else:
        row['samelink'] = tmp_id
    sql_str = u"insert into %s(`id`, `lid`, `cid`, `ptype`, `name`, `url`, `status`, `store_path`, `page_type`, `samelink`) " \
              " value('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (table_t_t, row['id'], row['lid'], row['cid']
              , row['ptype'], row['name'], row['url'], row['status'], row['store_path'], row['page_type'], row['samelink'])
    #print sql_str
    sql_str = sql_str + u'\n'
    f.write(sql_str.encode('utf8'))
    print i
    #conn.execute(sql_str)

f.close()
conn.close()




