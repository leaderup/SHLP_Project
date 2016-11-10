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
    http://weilaijiequls021.fang.com/
"""
import sys
sys.path.append("../")
import re
import torndb
from math import ceil
from urlparse import urlparse
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
        "div.main_rt300 .xc_xmdl dl dd"
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
    url = info['photo_url']
    soup = info["soup"]

    page_type = 1
    checkcpl = re.compile("(\W+)\s*(\d+)")

    # 相册类型与总数
    photolist = {}
    soufang_tags = soup.select("div.main_rt300 .xc_xmdl dl dd")
    for soufang_tag in soufang_tags:
        text = clearString(soufang_tag.text)
        allfind = checkcpl.findall(text)
        if allfind:
            ptype = ""
            ptext, ptotal = allfind[0]
            if info['encoding'] == 'windows-1252':
                ptext = ptext.encode('windows-1252').decode('gbk')
            if u"户型图" in ptext:
                ptype = 900
            elif u"交通图" in ptext:
                ptype = 901
            elif u"外景图" in ptext:
                ptype = 902
            elif u"实景图" in ptext:
                ptype = 903
            elif u"效果图" in ptext:
                ptype = 904
            elif u"样板间" in ptext:
                ptype = 905
            elif u"项目现场" in ptext:
                ptype = 906
            elif u"配套图" in ptext or u"周边" in ptext:
                ptype = 907
            
            ptotal = int(ptotal)
            if ptype:
                photolist[ptype] = ptotal

    if 1000 in photolist and photolist[1000] == 0:
        # 存在空的无照片的页面
        return None
    
    sql_lists = []
    for ptype, ptotal in photolist.iteritems():
        urldomain = urlparse(url).netloc
        rid = info['rid']
        for i in range(1, int(ceil(int(ptotal)/6.0) + 1)):
            nextpage = i
            sqlstring = "replace into lp_photo_summary(`lid`, `cid`, `url`, `rid`, `photo_type`, `total`, `npage`, `page_type`) " \
                        "values(%s, %s, '%s', %s, %s, %s, %s, %s)" % \
                        (info['id'], info['cid'], urldomain, info['rid'], ptype, ptotal, nextpage, page_type)
            sql_lists.append(sqlstring)
            
    conn = torndb.Connection(host="192.168.1.119", database="data_transfer", user="frem", password=passwd)
    for sqlstring in sql_lists:
        conn.execute(sqlstring)
    conn.close()

def completeTask(info, result, dataDir=None):
    mid = info['id']
    if result:
        sqlstring = 'UPDATE %s SET `photo_status`=2 WHERE `id`="%s"' % (lp_links, mid)
    else:
        sqlstring = 'UPDATE %s SET `photo_status`=4 WHERE `id`="%s"' % (lp_links, mid)

    conn = torndb.Connection(host="192.168.1.119", database="data_transfer", user="frem", password=passwd)
    conn.execute(sqlstring)
    conn.close()
    lplog.error(sqlstring)


if __name__ == "__main__":
    from bs4 import BeautifulSoup
    f = open(r"D:\PythonProgram\SHLouPan\data\Test\shanghaiwanhs_photo.html")
    content = f.read()
    f.close()
    soup = BeautifulSoup(content, "html5lib", from_encoding="utf-8")
    info = {}
    info['content'] = content
    info['photo_url'] = u"http://shanghaiwanhs.fang.com/photo/1110677191.htm"
    info['soup'] = soup
    info['name'] = u"恒盛尚海湾滨海"
    info['id'] = 0 # test
    info['cid'] = 0
    info['rid'] = 0
    info['encoding'] = 'utf-8'
    datadir = r"D:\PythonProgram\SHLouPan\data\Test"
    
    retcode, retInfo = jdugePage(info)
    print retInfo
    analysisPage(info, datadir)
