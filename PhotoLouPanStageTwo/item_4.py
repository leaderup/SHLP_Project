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
    判断是否为空页
    """
    result = False
    loginfo = u"id: %s, lp_links: %s, lp_pool: %s" % (info['id'], info['lid'], info['cid'])
    # 判断页面大小
    content = info['content']
    if len(content) < min_page_length:
        result = False
        loginfo += u" may hasn't page or length litter than %s." % min_page_length
        return (result, loginfo)

    soup = info['soup']
    yeshu = soup.select(".wrap .pho_main_right .fanye strong")
    if yeshu:
        yeshu = yeshu[0].text.strip()
        if yeshu.isalnum():
            if int(yeshu) == 0:
                result = True
                loginfo += " is ok."
                return (result, loginfo)
    
    loginfo += ", [.wrap .pho_main_right .fanye strong] not found."
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
    from bs4 import BeautifulSoup, UnicodeDammit
    f = open(r"D:\PythonProgram\SHLouPan\data\Test\mingrenbieshu_photo.html")
    content = f.read()
    f.close()
    codeobj = UnicodeDammit(content)
    encoding = codeobj.original_encoding
    soup = BeautifulSoup(content, "html5lib", from_encoding=encoding)
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