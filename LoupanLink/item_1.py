#!/usr/bin/env python
#coding: utf8
"""
针对当前页面实现两人个函数:
    一个是判断页面函数: jdugePage
    另一个是分析页面函数: analysisPage
"""

import re
import torndb
import sys
sys.path.append("../")
from utils import lplog

passwd = "123456"

def jdugePage(info, dataDir=None):
    """
    判断当前页面是否为指定页面
    http://newhouse.fang.com/house/s/b91/
    """
    loginfo = u"prov: %s, city: %s, " % (info['prov'], info['city'])
    soup = info["soup"]
    if not soup.text:
        sqlstring = 'UPDATE lp_pool SET `status`=3 WHERE `id`="%s"' % id
        conn = torndb.Connection(host="192.168.1.119", database="data_transfer", user="frem", password=passwd)
        conn.execute(sqlstring)
        conn.close()
        loginfo += u"url: %s has no view page" % info['url']
        return (False, loginfo)

    items = [
        ("div", {"class": "contentListf"}),
        ("div", {"class": "nhouse_list_content"}),
        ("div", {"class": "nhouse_list"}),
        ("div", {"class": "nl_con"}),
        ("div", {"class": "nlc_details"}),
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

def analysisPage(info, dataDir=None, gzCompile = re.compile("guanzhu\s*\(\s*'\s*(\d+)\s*'"), blank_to_one = re.compile("\s+")):
    """
    收集信息
    gzCompile: 获取资源号 关注
    blank_to_one: 连续空格合并
    """
    url = info['url']
    soup = info["soup"]

    all_list = []
    cid = info['id']

    nhouse_list_content = soup.find("div", class_="nhouse_list_content")
    nl_con = nhouse_list_content.find("div", class_="nl_con")
    nlc_details = nl_con.findAll("div", class_="nlc_details")
    for nlc_detail in nlc_details:
        # 楼盘名 + 链接
        nlcd_name = nlc_detail.find("div", class_="nlcd_name")
        nlcd_name_a = nlcd_name.find("a")
        lp_name = nlcd_name_a.text.strip().replace(u" ", u"")
        lp_link = nlcd_name_a.attrs['href']
        # 资源ID
        guanzhu = nlc_detail.find("div", class_="guanzhu")
        gzOnclick = guanzhu.attrs["onclick"]
        gz_rid = gzCompile.findall(gzOnclick)
        gz_rid = gz_rid[0]
        # 地址
        address = nlc_detail.find("div", "address")
        district = address.text.strip().replace(u"　", u"")
        district = blank_to_one.sub(" ", district)

        # 生癖字 中海寰宇天下 - 桂城桂澜路𧒽岗地铁站上盖
        if u'\U000274bd' in district:
            district = district.replace(u'\U000274bd', u'lei(\u866b\u96f7)')

        brief = (cid, lp_name, lp_link, district, gz_rid)
        all_list.append(brief)

    conn = torndb.Connection(host="192.168.1.119", database="data_transfer", user="frem", password=passwd)
    for brief in all_list:
        sqlstring = 'REPLACE INTO lp_links(`cid`, `name`, `link`, `district`, `rid`) VALUES(%s, "%s", "%s", "%s", %s)' % brief
        # lplog.info(sqlstring)
        conn.execute(sqlstring)
    conn.close()

    return True

def completeTask(info, result, dataDir=None):
    id = info['id']
    if result:
        sqlstring = 'UPDATE lp_pool SET `status`=2 WHERE `id`="%s"' % id
    else:
        sqlstring = 'UPDATE lp_pool SET `status`=4 WHERE `id`="%s"' % id

    conn = torndb.Connection(host="192.168.1.119", database="data_transfer", user="frem", password=passwd)
    conn.execute(sqlstring)
    conn.close()

if __name__ == "__main__":
    from bs4 import BeautifulSoup
    f = open(r"D:\PythonProgram\SHLouPan\data\Test\guangdong_foshan_b96.html")
    content = f.read()
    f.close()
    soup = BeautifulSoup(content, "html5lib", from_encoding="utf-8")
    info = {}
    info['url'] = u"http://newhouse.fs.fang.com/house/s/b96/"
    info['soup'] = soup
    info['id'] = "5583" # test
    datadir = r"D:\PythonProgram\SHLouPan\data\Test"
    analysisPage(info, datadir)
