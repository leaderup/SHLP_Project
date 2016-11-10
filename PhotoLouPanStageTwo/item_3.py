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
    http://home.tj.fang.com/zhuangxiu/caseFor4S________1110012230___/
"""

import sys
sys.path.append("../")
import re
import torndb
import pymongo
from utils import lplog, clearString, min_page_length

passwd = "123456"
lp_photo_summary = "lp_photo_summary"
lp_photo_link = "lp_photo_links"

def jdugePage(info, dataDir=None):
    """
    判断当前页面是否为指定页面
    """
    result = True
    loginfo = u"id: %s, lp_links: %s, lp_pool: %s" % (info['id'], info['lid'], info['cid'])
    # 判断页面大小
    content = info['content']
    if len(content) < min_page_length:
        result = False
        loginfo += u" may hasn't page or length litter than %s." % min_page_length
        return (result, loginfo)

    soup = info['soup']
    items = [
       ".main .list_left .list .list_lb dl span a"
    ]
    info = []
    for item in items:
        bstag = soup.select(item)
        if len(bstag):
            continue
        else:
            result = False
            info.append(item)

    if result:
        loginfo = "%s is ok." % loginfo
    else:
        info = ", ".join(info)
        loginfo = "%s tags: [%s] not found" % (loginfo, info)

    return (result, loginfo)

def analysisPage(info, dataDir):
    """
    收集信息
    """
    mid = info['id']
    soup = info["soup"]
    
    mongodatas = []
    
    page_type = 3
    totalcpl = re.compile("\((\d+)\)")

    pic_a_tags = soup.select(".main .list_left .list .list_lb dl span a")
    for pic_a_tag in pic_a_tags:
        data = {}
        img_tag = pic_a_tag.find("img")
        img_src = img_tag.attrs['src']
        title = clearString(img_tag.attrs['alt']).strip()
        data['t8t_lid'] = info['lid']
        data['t8t_cid'] = info['cid']
        data['t8t_type'] = info['photo_type']
        data['page_type'] = page_type
        data['tag'] = title.strip().replace("'", r"\'")
        data['url'] = img_src.strip()
        mongodatas.append(data)

    # 存入MySQL
    conn = torndb.Connection(host="192.168.1.119", database="data_transfer", user="frem", password=passwd)
    for dataobj in mongodatas:
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

        # mongodb映射到mysql的id
        dataobj['t8t_id'] = t8t_id
    conn.close()

    # 存入Mongodb
    client = pymongo.MongoClient(host="192.168.1.83", port=27017)
    collection = client.loupan.get_collection("lp_photo_links")
    for dataobj in mongodatas:
        clearData = {
            't8t_id': dataobj['t8t_id']
        }
        collection.remove(clearData)
        collection.save(dataobj)
    client.close()


def completeTask(info, result, dataDir=None):
    mid = info['id']
    if result:
        sqlstring = 'UPDATE %s SET `status`=2 WHERE `id`="%s"' % (lp_photo_summary, mid)
    else:
        sqlstring = 'UPDATE %s SET `status`=4 WHERE `id`="%s"' % (lp_photo_summary, mid)

    conn = torndb.Connection(host="192.168.1.119", database="data_transfer", user="frem", password=passwd)
    conn.execute(sqlstring)
    conn.close()


if __name__ == "__main__":
    from bs4 import BeautifulSoup
    f = open(r"D:\PythonProgram\SHLouPan\data\Test\zhuangxiu.photo.html")
    content = f.read()
    f.close()
    soup = BeautifulSoup(content, "html5lib")
    info = {}
    info['url'] = u"http://home.tj.fang.com/zhuangxiu/caseFor4S155_______2_1110012230___/"
    info['content'] = content
    info['soup'] = soup
    info['name'] = u"千禧园装修"
    info['id'] = 0
    info['lid'] = 0 # test
    info['cid'] = 0
    info['photo_type'] = 902
    datadir = r"D:\PythonProgram\SHLouPan\data\Test"
    
    retcode, retInfo = jdugePage(info)
    print retInfo
    analysisPage(info, datadir)