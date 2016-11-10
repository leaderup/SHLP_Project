#!/usr/bin/env python
#coding: utf8

"""
主url函数: urlput
"""

import sys
sys.path.append("../")
import os
import re
import time
import logging
import torndb

"""
    搜房网楼盘首页
    注： 
        数据库中 detail_url 字段要存在URL
"""
passwd = "123456"
tablename = "lp_photo_links"

def resizeJpg(x, y):
    if x >= 800 or y >= 600:
        return (x, y)

    i = 2
    while i:
        x1 = x * i
        y1 = y * i
        if x1 >= 800 and y1 >= 600:
            return (x1, y1)
        else:
            i += 1

        if i >= 800:
            return (x, y)

def resetUncatchStatus():
    # 重置数据状态
    sqlstring = u"UPDATE %s SET `status`=0 WHERE `status`=1" % tablename
    conn = torndb.Connection(host="192.168.1.119", database="data_transfer", user="frem", password=passwd)
    conn.execute(sqlstring)
    conn.close()

def urlput(urlqueue, datadir, log=logging.getLogger("urlput")):
    # 导入数据
    #resetUncatchStatus()
    conn = torndb.Connection(host="192.168.1.119", database="data_transfer", user="frem", password=passwd)
    # 空查询次数
    empty_execution = 0
    # 队列长度
    max_size = 100
    # 执行数据库状态
    status = 0
    # 取url中图片尺寸大小
    recpl = re.compile('(\d+)x(\d+)')
    while 1:
        if empty_execution == 10:
            sqlstring = "SELECT count(*) as rownums FROM %s WHERE `status`=%s" % (tablename, status)
            result = conn.query(sqlstring)
            if result[0]["rownums"] == 0:
                break
            else:
                empty_execution = 0
        qsize = urlqueue.qsize()
        if qsize >= max_size:
            time.sleep(2)
            continue
        sqlstring = "SELECT * FROM %s WHERE `status`=%s LIMIT 0, %s" % (tablename, status, max_size)
        # sqlstring = "SELECT * FROM %s WHERE `status`=%s and `id`=66 LIMIT 0, %s" % (tablename, status, max_size)
        rinit = conn.query(sqlstring)
        if len(rinit):
            empty_execution = 0
            for row in rinit:
                sqlstring = "UPDATE %s SET `status`=1 WHERE id='%s'" % (tablename, row["id"])
                rowcount = conn.execute_rowcount(sqlstring)
                if rowcount == 1:
                    # 处理重复URL的表
                    samelink = row['samelink']
                    if int(samelink) > 0:
                        sqlstring = "UPDATE %s SET `status`=2 WHERE id='%s'" % (tablename, row["id"])
                        conn.execute(sqlstring)
                        continue
                    # 处理图片文件名
                    urlhead, ext = os.path.splitext(row['url'])
                    if not ext:
                        ext = '.jpg'
                    # 处理图片尺寸
                    url = row['url']
                    urlexcision = url.split('/')
                    lastsplit = urlexcision[-1]
                    retxy = recpl.findall(lastsplit)
                    if retxy:
                        x, y = retxy[0]
                        x1, y1 = resizeJpg(int(x), int(y))
                        newlastsplit = lastsplit.replace(x, str(x1)).replace(y, str(y1))
                        urlexcision[-1] = newlastsplit
                        url = '/'.join(urlexcision)
                        row['url'] = url
                        sqlstring = "UPDATE %s SET `url`='%s' WHERE id='%s'" % (tablename, url, row["id"])
                        conn.execute(sqlstring)
                    storepath = "_".join([str(row['lid']), str(row['ptype']), str(row['id'])])
                    row['urlpath'] = os.path.join(datadir, "%s%s" % (storepath, ext))
                    row['webtype'] = 'download'
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
