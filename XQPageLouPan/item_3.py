#!/usr/bin/env python
#coding: utf8
"""
针对当前页面实现两人个函数:
    一个是判断页面函数: jdugePage
    另一个是分析页面函数: analysisPage
注：
    请查阅日志 MaXQPageLouPan.log 中是否存在无效信息
示例：
    http://icshejidasha.fang.com/xiangqing/
"""

import sys
sys.path.append("../")
import torndb
import pymongo
from bs4 import element
from utils import lplog, clearString, min_page_length

passwd = "123456"
lp_links = "lp_links"

def jdugePage(info, dataDir=None):
    """
    判断当前页面是否为指定页面
    """
    result = True
    loginfo = u"name: %s" % info['name']
    # 判断页面大小
    content = info['content']
    if len(content) < min_page_length:
        result = False
        loginfo += u" may hasn't page or length litter than %s." % min_page_length
        return (result, loginfo)

    soup = info['soup']
    items = [
        "div.wrap .lpbl .lpblbox1 dl"
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

    # ------------------------------------------------
    detail_page_info = {
        'method': 2,
        'lid': info['id'],
        'url': info['url']
    }
    # 搜房网链接路径
    basic_info_tags = {}
    lpblbox1s = soup.select("div.wrap .lpbl .lpblbox1")
    for lpblbox1 in lpblbox1s:
        lpblbox_children = []
        for lpblbox_tag in lpblbox1.children:
            if isinstance(lpblbox_tag, element.Tag):
                lpblbox_children.append(lpblbox_tag)
        title_tag = lpblbox_children[0].find(class_="name")
        title = clearString(title_tag.text)
        basic_tag = lpblbox_children[1]
        if title == u"基本信息":
            basic_info_tags[title] = basic_tag
        elif title == u"配套设施":
            basic_info_tags[title] = basic_tag
        elif title == u"交通状况":
            basic_info_tags[title] = basic_tag
        elif title == u"周边信息":
            basic_info_tags[title] = basic_tag
    
    # 基本信息
    basic_info = {}
    if u"基本信息" in basic_info_tags:
        basic_tag = basic_info_tags[u"基本信息"]
        dds = basic_tag.findAll("dd")
        for dd in dds:
            dd_text = clearString(dd.text)
            if u"：" in dd_text:
                key, value = dd_text.split(u"：", 1)
            elif u":" in dd_text:
                key, value = dd_text.split(u":", 1)
            else:
                continue
            
            key = key.strip()
            value = value.strip()
            basic_info[key] = value
        detail_page_info["basicdetails"] = basic_info
    
    # 配套设施（无）
    
    # 周边信息 peripheralInformation
    if u"周边信息" in basic_info_tags:
        peripheral_information = {}
        peripheral_info_tag = basic_info_tags[u"周边信息"]
        peripheral_information = clearString(peripheral_info_tag.text)
        detail_page_info['peripheralInformation'] = peripheral_information
    
    
    # 交通状况
    if u"交通状况" in basic_info_tags:
        trafic_tag = basic_info_tags[u"交通状况"]
        text = clearString(trafic_tag.text)
        detail_page_info["trafic"] = text

    # Mongo存储
    client = pymongo.MongoClient(host="192.168.1.83", port=27017)
    collection = client.loupan.get_collection("lp_details")
    clearData = {"lid": info['id']}
    collection.remove(clearData)
    collection.save(detail_page_info)
    client.close()


def completeTask(info, result, dataDir=None):
    mid = info['id']
    if result:
        sqlstring = 'UPDATE %s SET `detail_status`=2 WHERE `id`="%s"' % (lp_links, mid)
    else:
        sqlstring = 'UPDATE %s SET `detail_status`=4 WHERE `id`="%s"' % (lp_links, mid)

    conn = torndb.Connection(host="192.168.1.119", database="data_transfer", user="frem", password=passwd)
    conn.execute(sqlstring)
    conn.close()
    lplog.error(sqlstring)


if __name__ == "__main__":
    from bs4 import BeautifulSoup, UnicodeDammit
    f = open(r"D:\PythonProgram\SHLouPan\data\Test\icshejidasha_detail.html")
    content = f.read()
    f.close()
    soup = BeautifulSoup(content, "html5lib", from_encoding="utf-8")
    info = {}
    info['content'] = content
    info['url'] = u"http://icshejidasha.fang.com/xiangqing/#jtzk"
    info['soup'] = soup
    info['name'] = u"IC设计大厦小区网"
    info['id'] = 1 # test
    datadir = r"D:\PythonProgram\SHLouPan\data\Test"
    
    retcode, retInfo = jdugePage(info)
    print retInfo
    analysisPage(info, datadir)
