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
    mid = info['id']
    soup = info["soup"]
    result = False
    loginfo = u", [.main .list_left .list] not found"

    list_tag = soup.select(".main .list_left .list")
    if list_tag:
        list_tag = clearString(list_tag[0].text)
        list_tag = list_tag.strip()
        
        if info['encoding'] == 'windows-1252':
            list_tag = list_tag.encode('windows-1252').decode('gbk')          
        
        if u"您搜索的内容不存在或因涉及敏感词汇而不能正常显示，请重新搜索其它关键词" in list_tag:
            result = True
            loginfo = u"内容不存在或因涉及敏感词汇而不能正常显示."         

    return (result, loginfo)

def analysisPage(info, dataDir):
    """
    收集信息
    """
    pass

def completeTask(info, result, dataDir=None):
    mid = info['id']
    if result:
        sqlstring = 'UPDATE %s SET `status`=3 WHERE `id`="%s"' % (lp_photo_summary, mid)
    else:
        sqlstring = 'UPDATE %s SET `status`=4 WHERE `id`="%s"' % (lp_photo_summary, mid)

    conn = torndb.Connection(host="192.168.1.119", database="data_transfer", user="frem", password=passwd)
    conn.execute(sqlstring)
    conn.close()


if __name__ == "__main__":
    from bs4 import BeautifulSoup
    f = open(r"D:\PythonProgram\SHLouPan\data\Test\casesearchResult_photo.html")
    content = f.read()
    f.close()
    soup = BeautifulSoup(content, "html5lib")
    info = {}
    info['content'] = content
    info['url'] = u"http://lishexsj.fang.com/photo/list_902_3210047636.htm"
    info['soup'] = soup
    info['name'] = u"大通花园"
    info['encoding'] = "utf8"
    info['id'] = 0
    info['lid'] = 0 # test
    info['cid'] = 0
    info['photo_type'] = 902
    datadir = r"D:\PythonProgram\SHLouPan\data\Test"
    
    retcode, retInfo = jdugePage(info)
    print retInfo
    analysisPage(info, datadir)