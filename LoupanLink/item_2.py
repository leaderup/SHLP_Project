#!/usr/bin/env python
#coding: utf8
"""
针对当前页面实现两人个函数:
    一个是判断页面函数: jdugePage
    另一个是分析页面函数: analysisPage
"""

import re
import torndb

passwd = "123456"

def jdugePage(info, dataDir=None):
    """
    判断当前页面是否为指定页面
    http://newhouse.fang.com/house/s/b9634/
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
        ("div", {"class": "sslalone"}),
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

def analysisPage(info, dataDir=None, ridCompile = re.compile("loupan_(\d+)")):
    """
    收集信息
    ridCompile: 资源号获取
    """
    url = info['url']
    soup = info["soup"]

    all_list = []
    cid = info['id']

    nhouse_list_content = soup.find("div", class_="nhouse_list_content")
    nl_con = nhouse_list_content.find("div", class_="nl_con")
    nl_con_lis = nl_con.findAll("li")
    for nl_con_li in nl_con_lis:
        # 资源ID
        sslalone = nl_con_li.find("div", class_="sslalone")
        sslalone_id = sslalone.get("id")
        rid = ridCompile.findall(sslalone_id)
        gz_rid = rid[0]

        # 楼盘名 + 链接
        h4 = nl_con_li.find("h4")
        lp_name_tag = h4.find("a")
        lp_link = lp_name_tag.attrs['href']
        lp_name = lp_name_tag.text.strip()

        # 地址
        lp_addr_div = nl_con_li.find("div", class_="add")
        lp_addr_a = lp_addr_div.find("a")
        district = lp_addr_a.text.strip()
        if district.endswith(u"(\\"):
            # "环岛路黄厝段(\"
            district = district[:-2]

        brief = (cid, lp_name, lp_link, district, gz_rid)
        all_list.append(brief)

    conn = torndb.Connection(host="192.168.1.119", database="data_transfer", user="frem", password=passwd)
    for brief in all_list:
        sqlstring = 'REPLACE INTO lp_links(`cid`, `name`, `link`, `district`, `rid`) VALUES(%s, "%s", "%s", "%s", %s)' % brief
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
    f = open(r"D:\PythonProgram\SHLouPan\data\Test\guangdong_shenzhen_b967.html")
    content = f.read()
    f.close()
    soup = BeautifulSoup(content, "html5lib", from_encoding="utf-8")
    info = {}
    info['url'] = u"http://newhouse.sz.fang.com/house/s/b967"
    info['soup'] = soup
    info['id'] = "2712" # test
    datadir = r"D:\PythonProgram\SHLouPan\data\Test"
    analysisPage(info, datadir)
