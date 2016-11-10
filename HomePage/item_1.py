#!/usr/bin/env python
#coding: utf8
"""
针对当前页面实现两人个函数:
    一个是判断页面函数: jdugePage
    另一个是分析页面函数: analysisPage
"""

import re
from os import path

def jdugePage(info, dataDir=None):
    """
    判断当前页面是否为指定页面
    """
    url = info['url']
    soup = info["soup"]
    if not soup.text:
        loginfo = u"%s has no view page." % url
        return (False, loginfo)

    items = [
        ("div", {"class": "mainContent"}),
        ("div", {"class": "letterSelt"}),
        ("div", {"class": "outCont"}),
        ("table", {}),
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
            loginfo = u"->".join(logitem)
            return (False, loginfo)
    else:
        return (True, u'ok')



def analysisPage(info, dataDir, recpl=re.compile("http://(\S+)\.fang\.com")):
    """
    收集信息
    """
    url = info['url']
    soup = info["soup"]

    all_city = {}

    outCont = soup.find(id="c02")
    if not outCont:
        outCont = soup.find("div", class_="outCont")
    trs = outCont.findAll('tr')
    for tr in trs:
        tds = tr.findAll("td")
        prov_tag = tds[1]
        # 省名
        if prov_tag.text.strip():
            prov = prov_tag.text.strip()
            all_city[prov] = []
        citylist = all_city[prov]
        city_a_tags = tds[2].findAll("a")
        for city_tag in city_a_tags:
            city_name = city_tag.text
            cityurl = city_tag.get("href")
            citylist.append((city_name, cityurl))

    # 省市URL规范文本列表
    alllist = []
    fname = path.splitext(path.basename(url))[0]
    fpath = path.join(dataDir, "%s.txt" % fname)
    with open(fpath, "w") as f:
        for prov, city_list in all_city.iteritems():
            for city in city_list:
                name, cityurl = city
                shortname = recpl.findall(cityurl)
                if len(shortname):
                    shortname = shortname[0]
                city_dict = {"prov": prov, "city": name, "shortname": shortname}
                alllist.append(city_dict)
                string = u"%s\t%s\t%s\n" % (prov, name, cityurl)
                string = string.encode('utf8')
                f.write(string)
        f.close()

    # 省市list列表
    fpath = path.join(dataDir, "%s_obj.txt" % fname)
    with open(fpath, "w") as f:
        f.write(str(alllist))
        f.close()

if __name__ == "__main__":
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(open(r"D:\PythonProgram\SHLouPan\data\HomePage\SoufunFamily.htm"), "html5lib")
    info = {}
    info['url'] = "http://fang.com/SoufunFamily.htm"
    info['soup'] = soup
    datadir = r"D:\PythonProgram\SHLouPan\data\HomePage"
    
    analysisPage(info, datadir)