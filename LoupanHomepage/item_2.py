#!/usr/bin/env python
#coding: utf8
"""
针对当前页面实现两人个函数:
    一个是判断页面函数: jdugePage
    另一个是分析页面函数: analysisPage
注：
    请查阅日志MaHouseCounts.log中是否存在无效位置信息
示例：
    http://changxinxinyuan.fang.com/
"""

import sys
sys.path.append("../")
import re
import torndb
import pymongo
from utils import lplog, min_page_length

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
        "div.wrap div.bread p.floatl",
        "div.logoBox_sq div.ceninfo_sq h1 a",
        "div.plptinfo_txt.floatr div.plptinfo_list ul li",
        "div.con_left div.box iframe",
        "div#orginalNaviBox ul li a"
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
    encoding = info['encoding']
    
    if encoding == 'windows-1252':
        is_windows = True
    else:
        is_windows = False

    blank_to_one = re.compile("\s+")

    # ------------------------------------------------
    first_page_info = {
        'method': 2,
        'lid': info['id'],
        'url': info['url']
    }
    # 搜房网链接路径
    # 搜房网> 上海新房> 奉贤楼盘> 朗诗未来街区
    lp_path_tag = soup.select("div.wrap div.bread p.floatl")[0]
    if is_windows:
        lp_path = lp_path_tag.text.replace(u'\u2002', "").strip().encode('windows-1252').decode('gbk')
    else:
        lp_path = lp_path_tag.text.replace(u'\u2002', "").strip()
    lp_path = blank_to_one.sub(" ", lp_path).replace(u"\xa0", "").split(">")
    lp_path = [x.strip() for x in lp_path]
    lp_path = ">".join(lp_path[1:])
    first_page_info['linkPath'] = lp_path
    # 小区名称
    lp_name_tag = soup.select("div.logoBox_sq div.ceninfo_sq h1 a")[0]
    lp_name = lp_name_tag.text.replace(u'\u2002', "").strip()
    if is_windows:
        lp_name = lp_name.encode('windows-1252').decode('gbk')
    first_page_info['title'] = lp_name
    # 小区别名 (无)
    # 标签 (无)
    # 首页详情信息
    first_details = []
    first_detail_tags = soup.select("div.plptinfo_txt.floatr div.plptinfo_list ul li")
    for first_detail_tag in first_detail_tags:
        if is_windows:
            first_detail = first_detail_tag.text.replace(u'\u2002', "").encode('windows-1252').decode('gbk')            
        first_detail = blank_to_one.sub(" ", first_detail)
        first_detail = first_detail.replace(u"\xa0", "")
        first_details.append(first_detail)
    else:
        first_page_info['firstDetails'] = first_details
    # 地图链接地址
    iframe_map_tag = soup.select("div.con_left div.box iframe")[1]
    iframe_map_link = iframe_map_tag.attrs['src']
    first_page_info['iframeMap'] = iframe_map_link

    # ------------------------------------------------
    # 详情页与相册页链接
    lpxq_link = ''
    lpxc_link = ''
    lp_link_tags = soup.select("div#orginalNaviBox ul li a")
    for lp_link in lp_link_tags:
        if encoding == 'windows-1252':
            title = lp_link.text.strip().replace(u'\u2002', "").encode('windows-1252').decode('gbk')
        else:
            title = lp_link.text
        if title == u"小区详情":
            lpxq_link = lp_link.attrs['href']
        elif title == u"小区相册":
            lpxc_link = lp_link.attrs['href']

    # Mongo存储
    client = pymongo.MongoClient(host="192.168.1.83", port=27017)
    collection = client.loupan.get_collection("lp_homepage")
    collection.save(first_page_info)
    client.close()

    # 更新首页链接
    sqlstring = "UPDATE lp_links SET detail_url='%s', photo_url='%s' WHERE `id`=%s" % (lpxq_link, lpxc_link, mid)
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
    f = open(r"D:\PythonProgram\SHLouPan\data\Test\lishexsj.html")
    content = f.read()
    f.close()
    soup = BeautifulSoup(content, "html5lib", from_encoding="utf-8")
    info = {}
    info['url'] = u"http://lishexsj.fang.com/"
    info['soup'] = soup
    info['name'] = u"新世界丽舍小区网"
    info['id'] = 1 # test
    datadir = r"D:\PythonProgram\SHLouPan\data\Test"
    
    retcode, retInfo = jdugePage(info)
    print retInfo
    analysisPage(info, datadir)
