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
    http://longleyizhen0512.fang.com/shop/
"""

import sys
sys.path.append("../")
import re
import torndb
import pymongo
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
        ".lpbl .lpblbox .title .gray6",
        ".lpbl .lpblbox .title .biaoti",
        ".lpbl .lpblbox .xiangqing",
        ".lpbl .lpblbox1 .xiangqing",
        "#map iframe"
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

    blank_to_one = re.compile("\s+")

    # ------------------------------------------------
    first_page_info = {
        'method': 5,
        'lid': info['id'],
        'url': info['url']
    }
    # 搜房网链接路径
    # 搜房网> 上海新房> 奉贤楼盘> 朗诗未来街区
    lp_path_tag = soup.select(".lpbl .lpblbox .title .gray6")[0]
    lp_path = clearString(lp_path_tag.text)
    lp_path = lp_path.replace(u"查看地图>>", u"")
    first_page_info['linkPath'] = lp_path
    # 小区名称
    lp_name_tag = soup.select(".lpbl .lpblbox .title .biaoti")[0]
    lp_name = clearString(lp_name_tag.text)
    first_page_info['title'] = lp_name
    # 小区别名 (无)
    # 标签 (无)
    # 首页详情信息
    first_details = []
    all_xiangqing_tag = []
    xiangqing_tags = soup.select(".lpbl .lpblbox .xiangqing")[0]
    xiangqing_tag = xiangqing_tags.findAll("dd")
    all_xiangqing_tag.extend(xiangqing_tag)
    xiangqing_tag = xiangqing_tags.findAll("dt")
    all_xiangqing_tag.extend(xiangqing_tag)
    xiangqing1_tags = soup.select(".lpbl .lpblbox1 .xiangqing")[0]
    xiangqing_tag = xiangqing1_tags.findAll("dd")
    all_xiangqing_tag.extend(xiangqing_tag)
    xiangqing_tag = xiangqing1_tags.findAll("dt")
    all_xiangqing_tag.extend(xiangqing_tag)
    for xiangqing_tag in all_xiangqing_tag:
        text = clearString(xiangqing_tag.text)
        """
        if text.find(u"："):
            key, value = text.split(u"：")
        elif text.find(u":"):
            key, value = text.split(u":")
        else:
            key = text
            value = ""
        """
        first_details.append(text)
    else:
        first_page_info['firstDetails'] = first_details

    # 地图链接地址
    iframe_map_tag = soup.select("#map iframe")[0]
    iframe_map_link = iframe_map_tag.attrs['src']
    first_page_info['iframeMap'] = iframe_map_link

    # ------------------------------------------------
    # 详情页与相册页链接
    lpxq_link = ""
    lpxc_link = ""
    lp_link_tags = soup.select(".snav_sq ul a")
    for lp_link_tag in lp_link_tags:
        text = lp_link_tag.text.strip()
        if text == u"楼盘详情":
            lpxq_link = lp_link_tag.attrs['href']
        elif text == u"楼盘相册":
            lpxc_link = lp_link_tag.attrs['href']


    # Mongo存储
    client = pymongo.MongoClient(host="192.168.1.83", port=27017)
    collection = client.loupan.get_collection("lp_homepage")
    collection.save(first_page_info)
    client.close()

    # 更新首页链接
    sqlstring = "UPDATE %s SET detail_url='%s', photo_url='%s' WHERE `id`=%s" % (lp_links, lpxq_link, lpxc_link, mid)
    conn = torndb.Connection(host="192.168.1.119", database="data_transfer", user="frem", password=passwd)
    conn.execute(sqlstring)
    conn.close()

def completeTask(info, result, dataDir=None):
    mid = info['id']
    if result:
        sqlstring = 'UPDATE %s SET `home_status`=2 WHERE `id`="%s"' % (lp_links, mid)
    else:
        sqlstring = 'UPDATE %s SET `home_status`=4 WHERE `id`="%s"' % (lp_links, mid)

    conn = torndb.Connection(host="192.168.1.119", database="data_transfer", user="frem", password=passwd)
    conn.execute(sqlstring)
    conn.close()

if __name__ == "__main__":
    from bs4 import BeautifulSoup
    f = open(r"D:\PythonProgram\SHLouPan\data\Test\longleyizhen0512.html")
    content = f.read()
    f.close()
    soup = BeautifulSoup(content, "html5lib", from_encoding="utf-8")
    info = {}
    info['url'] = u"http://longleyizhen0512.fang.com/shop/"
    info['soup'] = soup
    info['name'] = u"玉带商业广场小区网"
    info['id'] = 1 # test
    datadir = r"D:\PythonProgram\SHLouPan\data\Test"
    
    retcode, retInfo = jdugePage(info)
    print retInfo
    analysisPage(info, datadir)
