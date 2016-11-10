#!/usr/bin/env python
#coding: utf8
"""
针对当前页面实现两人个函数:
    一个是判断页面函数: jdugePage
    另一个是分析页面函数: analysisPage
注：
    请查阅日志MaHouseCounts.log中是否存在无效位置信息
    部分城市抓取不全
总：
    所有模块都需要完成后进行验证，目前有效城市为26个，总城市个数"SoufunFamily_obj.txt"总行数。
    通过SQL语句:
                 SELECT DISTINCT prov, city, total FROM lp_pool -- 城市,total为当前城市所有楼盘数
                 SELECT COUNT(DISTINCT prov, city) FROM lp_pool -- 城市总数
"""

import re
import torndb
from urlparse import urljoin
from math import ceil

passwd = "123456"

def jdugePage(info, dataDir=None):
    """
    判断当前页面是否为指定页面
    """
    loginfo = u"prov: %s, city: %s, " % (info['prov'], info['city'])
    soup = info["soup"]
    if not soup.text:
        loginfo += u"url: %s has no view page" % info['url']
        return (False, loginfo)

    items = [
        ("li", {"id": "sjina_C01_30"}),
    ]

    msoup = soup
    for item in items:
        tag, attr = item
        if tag and attr:
            msoup = msoup.find(tag, attrs=attr)
        elif tag:
            msoup = msoup.find(tag)
        elif attr:
            msoup = msoup.find(attrs=attr)
        else:
            msoup = None

        if not msoup:
            logitem = []
            for item in items:
                tag, attr = item
                info = [u"%s: %s" % (k, v) for k,v in attr.iteritems()]
                info = u"%s:{%s}" % (tag, ",".join(info))
                logitem.append(info)
            loginfo += u"->".join(logitem)
            return (False, loginfo)
    else:
        return (True, u'ok')

def analysisPage(info, dataDir):
    """
    收集信息
    """
    url = info['url']
    soup = info["soup"]

    recpl1=re.compile(u"(\d+)\s*个楼盘满足您的需求")
    recpl2=re.compile(u"(\d+)\s*个楼盘有优惠")

    outCont = soup.find(id="sjina_C01_30")
    lp_total_string = outCont.text
    lp_total = recpl1.findall(lp_total_string)
    if len(lp_total) == 1:
        lp_total = lp_total[0]
    else:
        lp_total = recpl2.findall(lp_total_string)
        if len(lp_total) == 1:
            lp_total = lp_total[0]

    if not lp_total:
        lp_total = 0

    # 页面最大值
    max_page = int(ceil(int(lp_total)/20))
    conn = torndb.Connection(host="192.168.1.119", database="data_transfer", user="frem", password=passwd)
    for i in range(max_page + 1):
        url = urljoin(url, "b9%s" % i)
        sqlstring = "REPLACE INTO lp_pool(`prov`, `city`, `url`, `total`) VALUES('%s', '%s', '%s', %s)" % \
                    (info["prov"], info["city"], url, lp_total)
        conn.execute(sqlstring)
    conn.close()

    """
    # 整合信息
    startpage = 1  # 开始完成到多个小区
    alllist = []
    alllist.append(info["prov"].encode("utf8"))
    alllist.append(info["city"].encode("utf8"))
    alllist.append(url.encode("utf8"))
    alllist.append(lp_total.encode("utf8"))
    alllist.append(str(startpage))
    string = "\t".join(alllist) + "\n"
    
    # 添加到文件
    fname = "town_total.txt"
    fpath = path.join(dataDir, fname)
    with open(fpath, "a+") as f:
        f.write(string)
        f.close()
    """

if __name__ == "__main__":
    from bs4 import BeautifulSoup
    f = open(r"D:\PythonProgram\SHLouPan\data\HouseCounts\anhui_hefei.html")
    content = f.read()
    f.close()
    soup = BeautifulSoup(content, "html5lib", from_encoding="utf-8")
    info = {}
    info['url'] = u"http://newhouse.hf.fang.com/house/s/"
    info['soup'] = soup
    info['prov'] = u"安徽"
    info['city'] = u"合肥"
    datadir = r"C:\Users\organo.xia\Desktop"
    analysisPage(info, datadir)
