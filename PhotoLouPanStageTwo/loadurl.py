#!/usr/bin/env python
#coding: utf8

"""
主url函数: urlput
"""

import sys
sys.path.append("../")
import os
import logging
import torndb
import time
from urlparse import urljoin
from urllib import urlencode
from pypinyin import lazy_pinyin
from utils import lplog

"""
    搜房网楼盘首页
    注： 
        数据库中 detail_url 字段要存在URL
"""
passwd = "123456"
lp_photo = "lp_photo_summary"

def resetUncatchStatus():
    # 重置数据状态
    sqlstring = u"UPDATE %s SET `status`=0 WHERE `status`=1" % lp_photo
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
            sqlstring = "SELECT count(*) as rownums FROM %s WHERE `status`=%s" % (lp_photo, status)
            result = conn.query(sqlstring)
            if result[0]["rownums"] == 0:
                break
            else:
                empty_execution = 0
        qsize = urlqueue.qsize()
        if qsize >= max_size:
            time.sleep(2)
            continue
        sqlstring = "SELECT * FROM %s WHERE `status`=%s LIMIT 0, %s" % (lp_photo, status, max_size)
        #sqlstring = "SELECT * FROM %s WHERE `status`=%s and `id`=22352 LIMIT 0, %s" % (lp_photo, status, max_size)
        rinit = conn.query(sqlstring)
        if len(rinit):
            empty_execution = 0
            for row in rinit:
                sqlstring = "UPDATE %s SET `status`=1 WHERE id='%s'" % (lp_photo, row["id"])
                rowcount = conn.execute_rowcount(sqlstring)
                if rowcount == 1:
                    url = row['url']
                    if row['page_type'] == 1:
                        # http://181150.fang.com/house/ajaxrequest/photolist_get.php?newcode=2811181150&type=902&nextpage=1&room=
                        udata = {
                            "newcode": row['rid'],
                            "type": row['photo_type'],
                            "nextpage": row['npage'],
                            "room": ""
                        }
                        udatastring = urlencode(udata)
                        url = "http://%s/house/ajaxrequest/photolist_get.php?%s" % (row['url'], udatastring)
                        row['url'] = url
                    elif row['page_type'] == 2:
                        if url.find('/caseFor4S'):
                            # http://home.tj.fang.com/zhuangxiu/caseFor4S________1110054175___/
                            rid = row['rid']
                            original = "_%s_" % rid
                            replace = "_%s_%s_" % (row['npage'], rid)
                            url = url.replace(original, replace)
                            row['url'] = url
                        else:
                            # http://home.tj.fang.com/zhuangxiu/caseFor4S________1110054175___/
                            urlhead, urlext = os.path.splitext(url)
                            npage = row['npage']
                            url = "%s_%s%s" % (urlhead, npage, urlext)
                            row['url'] = url
                    # c: city, l: link id, t: photo type, p: page number
                    storepath = "_".join(['c%s' % row['cid'], 'l%s' % row['lid'], 't%s' % row['photo_type'], 'p%s' % row['npage']])
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
