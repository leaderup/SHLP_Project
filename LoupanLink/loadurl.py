#!/usr/bin/env python
#coding: utf8

"""
主url函数: urlput
主SQL：
        更新状态： UPDATE lp_pool SET `status`=0 WHERE `status`=4
"""

import sys
sys.path.append("../")
import os
import re
import time
import torndb
import logging
from uuid import uuid1
from pypinyin import lazy_pinyin

passwd = u"123456"
lp_pool = "lp_pool"
recpl = re.compile("/(b9\d+)/?$")

def init_status():
    """
    将读入状态的区域重新初始化
    """
    conn = torndb.Connection(host="192.168.1.119", database="data_transfer", user="frem", password=passwd)
    sqlstring = "UPDATE %s SET `status`=0 WHERE `status`=1" % lp_pool
    conn.execute(sqlstring)
    conn.close()

def urlput(urlqueue, datadir, log=logging.getLogger("urlput")):
    # 导入数据
    init_status()
    conn = torndb.Connection(host="192.168.1.119", database="data_transfer", user="frem", password=passwd)
    # 空查询次数
    empty_execution = 0
    # 队列长度
    max_size = 10
    # 执行数据库状态
    status = 0
    while 1:
        if empty_execution == 10:
            sqlstring = "SELECT count(*) as rownums FROM %s WHERE `status`=%s" % (lp_pool, status)
            result = conn.query(sqlstring)
            if result[0]["rownums"] == 0:
                break
            else:
                empty_execution = 0
        qsize = urlqueue.qsize()
        if qsize >= max_size:
            time.sleep(2)
            continue
        sqlstring = "SELECT * FROM %s WHERE `status`=%s LIMIT 0, %s" % (lp_pool, status, max_size)
        # sqlstring = "SELECT * FROM %s WHERE `catch_status`=%s and `id`=16568 LIMIT 0, 10" % (lp_city_list, status)
        rinit = conn.query(sqlstring)
        if len(rinit):
            empty_execution = 0
            for row in rinit:
                sqlstring = "UPDATE %s SET status=1 WHERE id='%s'" % (lp_pool, row["id"])
                rowcount = conn.execute_rowcount(sqlstring)
                if rowcount == 1:
                    base_name = recpl.findall(row['url'])
                    if base_name:
                        base_name = base_name[0]
                    else:
                        base_name = uuid1()
                    prov_name = "".join(lazy_pinyin(row['prov']))
                    city_name = "".join(lazy_pinyin(row['city']))
                    storepath = "_".join([prov_name, city_name, base_name])
                    row['urlpath'] = os.path.join(datadir, "%s.html" % storepath)
                    urlqueue.put(row)
        else:
            empty_execution += 1

    conn.close()

if __name__ == "__main__":
    datadir = r"D:\PythonProgram\SHLouPan\data\LoupanLink"
    from Queue import Queue
    queue = Queue()
    urlput(queue, datadir)
