#!/usr/bin/env python
#coding: utf8

"""
主url函数: urlput
"""

import sys
sys.path.append("../")
import os
import time
import logging
import torndb
from pypinyin import lazy_pinyin
from utils import lplog

"""
    搜房网楼盘首页
"""
passwd = "123456"
lp_link = "lp_links"

def resetUncatchStatus():
    # 重置数据状态
    sqlstring = u"UPDATE lp_links SET `home_status`=0 WHERE `home_status`=1"
    conn = torndb.Connection(host="192.168.1.119", database="data_transfer", user="frem", password=passwd)
    conn.execute(sqlstring)
    conn.close()

def urlput(urlqueue, datadir, log=logging.getLogger("urlput")):
    # 导入数据
    resetUncatchStatus()
    conn = torndb.Connection(host="192.168.1.119", database="data_transfer", user="frem", password=passwd)
    # 空查询次数
    empty_execution = 0
    # 队列长度
    max_size = 100
    # 执行数据库状态
    status = 0
    while 1:
        if empty_execution == 10:
            sqlstring = "SELECT count(*) as rownums FROM %s WHERE `home_status`=%s" % (lp_link, status)
            result = conn.query(sqlstring)
            if result[0]["rownums"] == 0:
                break
            else:
                empty_execution = 0
        qsize = urlqueue.qsize()
        if qsize >= max_size:
            time.sleep(2)
            continue
        sqlstring = "SELECT * FROM %s WHERE `home_status`=%s LIMIT 0, %s" % (lp_link, status, max_size)
        #sqlstring = "SELECT * FROM %s WHERE `home_status`=%s and `id`=27 LIMIT 0, %s" % (lp_link, status, max_size)
        rinit = conn.query(sqlstring)
        if len(rinit):
            empty_execution = 0
            for row in rinit:
                sqlstring = "UPDATE %s SET `home_status`=1 WHERE id='%s'" % (lp_link, row["id"])
                rowcount = conn.execute_rowcount(sqlstring)
                if rowcount == 1:
                    row['url'] = row['link']
                    storepath = "_".join([str(row['cid']), "loupanHP", "".join(lazy_pinyin(row['name']))])
                    row['urlpath'] = os.path.join(datadir, "%s.html" % storepath)
                    urlqueue.put(row)
        else:
            empty_execution += 1

    conn.close()

if __name__ == "__main__":
    import time
    from Queue import Queue
    from threading import Thread
    def readQueue(queue):
        i = 0
        while 1:
            i += 1
            try:
                info = queue.get_nowait()
            except:
                pass
            else:
                print "*"*20, i ,"*"*20
                for key, value in info.iteritems():
                    print "\t", key, value
            
            time.sleep(1)

    infoq = Queue()
    datadir = r"D:\PythonProgram\SHLouPan\data\LoupanHomepage"
    p = Thread(target=urlput, args=(infoq, datadir))
    p.setDaemon(True)
    c = Thread(target=readQueue, args=(infoq,))
    c.setDaemon(True)
    p.start()
    c.start()
    c.join()
    p.join()
    
    print "finish"
