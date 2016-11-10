#!/usr/bin/env python
#coding: utf8
"""
针对当前页面实现两人个函数:
    一个是判断页面函数: jdugePage
    另一个是分析页面函数: analysisPage
注：
    请查阅日志 MaLoupanHomepage.log 中是否存在无效位置信息
    详情页面 和 相册页面可能为空，这个需要回补
示例：
    http://shishanghuayuandt.fang.com/photo/1110012110.htm
"""

import sys
sys.path.append("../")
import torndb
import pymongo
from json import loads

passwd = "123456"
lp_photo = "lp_photo_summary"
lp_photo_link = "lp_photo_links"

def jdugePage(info, dataDir=None):
    """
    判断当前页面是否为指定页面
    """
    result = True
    loginfo = ""

    if info['page_type'] != 1:
        result = False
        loginfo += u" page type must be 1."
        return (result, loginfo)

    content = info['content']

    if not content:
        sqlstring = "UPDATE %s SET `status`=3 WHERE `id`=%s" % (lp_photo, info['id'])
        conn = torndb.Connection(host="192.168.1.119", database="data_transfer", user="frem", password=passwd)
        conn.execute(sqlstring)
        conn.close()
        result = False
        loginfo += u" has no view page"
        return (result, loginfo)

    try:
        jdata = loads(content)
        info['jsondata'] = jdata
    except:
        sqlstring = "UPDATE %s SET `status`=4 WHERE `id`=%s" % (lp_photo, info['id'])
        conn = torndb.Connection(host="192.168.1.119", database="data_transfer", user="frem", password=passwd)
        conn.execute(sqlstring)
        conn.close()
        result = False
        loginfo += u" no json series."
        return (result, loginfo)
    else:
        if "resCode" in jdata and jdata['resCode'] == u"103":
            loginfo += u" content 没有json数据返回."
            return (result, loginfo)

    loginfo = " is ok"
    return (result, loginfo)

def analysisPage(info, dataDir=None):
    """
    收集信息
    page_type: JSON下载的URL
    """
    page_type = 1

    jdata = info['jsondata']
    # 没有数据情况
    if "resCode" in jdata and jdata['resCode'] == u"103":
        sqlstring = "UPDATE %s SET `status`=3 WHERE `id`=%s" % (lp_photo, info['id'])
        conn = torndb.Connection(host="192.168.1.119", database="data_transfer", user="frem", password=passwd)
        conn.execute(sqlstring)
        conn.close()
        return
    
    # 有数据情况
    for data in jdata:
        data['t8t_lid'] = info['lid']
        data['t8t_cid'] = info['cid']
        data['t8t_type'] = info['photo_type']
        data['page_type'] = page_type

    # 存入MySQL
    conn = torndb.Connection(host="192.168.1.119", database="data_transfer", user="frem", password=passwd)
    for dataobj in jdata:
        dataobj['tag'] = dataobj['tag'].strip().replace("'", r"\'")
        dataobj['url'] = url.strip()
        sqlstring = "select id from %s where `lid`=%s and `ptype`=%s and `url`='%s'" % \
            (lp_photo_link, info['lid'], info['photo_type'], dataobj['url'])
        rows = conn.query(sqlstring)
        if len(rows):
            sqlstring = "update %s set `name`='%s', `url`='%s' where `id`=%s" % \
                        (lp_photo_link, dataobj['tag'], dataobj['url'], rows[0]['id'])
            conn.execute_lastrowid(sqlstring)
            t8t_id = rows[0]['id']            
        else:
            sqlstring = "insert into %s(`lid`, `cid`, `ptype`, `name`, `url`, `page_type`) values(%s, %s, %s, '%s', '%s', %s)" % \
                        (lp_photo_link, info['lid'], info['cid'], info['photo_type'], dataobj['tag'], dataobj['url'], page_type)
            t8t_id = conn.execute_lastrowid(sqlstring)

        """
        sqlstring = "replace into %s(`lid`, `cid`, `ptype`, `name`, `url`, `page_type`) values(%s, %s, %s, '%s', '%s', %s)" % \
            (lp_photo_link, info['lid'], info['cid'], info['photo_type'], dataobj['tag'], dataobj['url'], page_type)
        """
        dataobj['t8t_id'] = t8t_id
    conn.close()

    # 存入Mongodb
    client = pymongo.MongoClient(host="192.168.1.83", port=27017)
    collection = client.loupan.get_collection("lp_photo_links")
    for dataobj in jdata:
        clearData = {
            't8t_id': dataobj['t8t_id']
        }
        collection.remove(clearData)
        collection.save(dataobj)
    client.close()

def completeTask(info, result, dataDir=None):
    mid = info['id']
    if result:
        sqlstring = 'UPDATE %s SET `status`=2 WHERE `id`="%s"' % (lp_photo, mid)
    else:
        sqlstring = 'UPDATE %s SET `status`=4 WHERE `id`="%s"' % (lp_photo, mid)

    conn = torndb.Connection(host="192.168.1.119", database="data_transfer", user="frem", password=passwd)
    conn.execute(sqlstring)
    conn.close()


if __name__ == "__main__":
    import requests
    url = r'http://jinlanque.fang.com/house/ajaxrequest/photolist_get.php?type=900&nextpage=1&newcode=1110664729&room='
    r = requests.get(url)
    r.encoding = 'utf-8'
    info = {}
    info['id'] = 1
    info['lid'] = 2
    info['cid'] = 19
    info['npage'] = 1
    info['photo_type'] = 900
    info['page_type'] = 1
    info['content'] = r.content
    retcode, retInfo = jdugePage(info)
    print retInfo
    datadir = r"D:\PythonProgram\SHLouPan\data\Test"
    analysisPage(info, datadir)
