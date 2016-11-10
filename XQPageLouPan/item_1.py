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
浏览：
所有items：
function judgeAll(items=undefined){
    items = [
        [
            "div.mainl div.besic_inform table tbody tr",
            "#xq_xmpt_anchor",
            "#xq_jtzk_anchor",
            "#xq_jczx_anchor",
            "#xq_lczk_anchor",
            "#xq_cwxx_anchor",
            "#xq_xgxx_anchor"
        ],
        [
            "div.maininfo div.leftinfo .yihang",
            "div.maininfo div.leftinfo .lbox",
        ]    
    ]
    function judge(items){
        ret = true;
        for(var i=0; i<items.length; i++){
            select = $(items[i]);
            if (select.length == 0){
                ret = false;
                break;
            }
        }
        return ret;
    }
    for(var i=0; i<items.length; i++){
        ret = judge(items[i])
        console.log(i+1, ret)
    }
}
"""
import sys
sys.path.append("../")
import re
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
        "div.mainl div.besic_inform table tbody tr",
        "#xq_xmpt_anchor",
        "#xq_jtzk_anchor",
        "#xq_jczx_anchor",
        "#xq_lczk_anchor",
        "#xq_cwxx_anchor",
        "#xq_xgxx_anchor"
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

    clean_square_brackets = re.compile("\[\s*\S+\s*\]")

    # ------------------------------------------------
    detail_page_info = {
        'method': 1,
        'lid': info['id'],
        'url': info['url']
    }
    # 搜房网链接路径
    # 基本信息
    basic_info = {}
    tbody = soup.select("div.mainl div.besic_inform table tbody")
    basic_info_tags = tbody[0].findAll("tr")
    for basic_info_tag in basic_info_tags:
        strong = basic_info_tag.find("strong")
        if strong:
            key = clearString(strong.text)
            text = clearString(basic_info_tag.text)
            text = clean_square_brackets.sub("", text)
            value = text.replace(key, "")
            if value.startswith(u"：") or value.startswith(u":"):
                value = value[1:]
            key = key.replace(u" ", "")
            if key.endswith(u"：") or key.endswith(u":"):
                key = key[:-1]
            key = key.endswith(u"房价") and u"房价" or key
            basic_info[key] = value.strip()
    detail_page_info["basicdetails"] = basic_info

    # 项目配套
    xq_xmpt_anchor= soup.select("#xq_xmpt_anchor")
    if xq_xmpt_anchor:
        xq_xmpt_anchor = xq_xmpt_anchor[0]
        lineheight = xq_xmpt_anchor.findNextSibling(class_="lineheight")
        text = clearString(lineheight.text)
        detail_page_info["projectSupporting"] = text    
    
    # 交通状况
    xq_jtzk_anchor = soup.select("#xq_jtzk_anchor")
    if xq_jtzk_anchor:
        xq_jtzk_anchor = xq_jtzk_anchor[0]
        lineheight = xq_jtzk_anchor.findNextSibling(class_="lineheight")
        text = clearString(lineheight.text)
        detail_page_info["trafic"] = text
    
    # 建材装修
    xq_jczx_anchor= soup.select("#xq_jczx_anchor")
    if xq_jczx_anchor:
        xq_jczx_anchor = xq_jczx_anchor[0]
        lineheight = xq_jczx_anchor.findNextSibling(class_="lineheight")
        text = clearString(lineheight.text)
        detail_page_info["buildingDecoration"] = text

    # 楼层状况
    xq_lczk_anchor= soup.select("#xq_lczk_anchor")
    if xq_lczk_anchor:
        xq_lczk_anchor = xq_lczk_anchor[0]
        lineheight = xq_lczk_anchor.findNextSibling(class_="lineheight")
        text = clearString(lineheight.text)
        detail_page_info["floor"] = text

    # 车位信息
    xq_cwxx_anchor= soup.select("#xq_cwxx_anchor")
    if xq_cwxx_anchor:
        xq_cwxx_anchor = xq_cwxx_anchor[0]
        lineheight = xq_cwxx_anchor.findNextSibling(class_="lineheight")
        text = clearString(lineheight.text)
        detail_page_info["parkingInformation"] = text

    # 相关信息
    relativeInfo = {}
    xq_xgxx_anchor= soup.select("#xq_xgxx_anchor")
    if xq_xgxx_anchor:
        xq_xgxx_anchor = xq_xgxx_anchor[0]
        lineheight = xq_xgxx_anchor.findNextSibling(class_="lineheight")
        strings = []
        for stripped in lineheight.children:
            if isinstance(stripped, element.Tag):
                string = clearString(stripped.text).strip().replace(u" ", "").replace(u"　", "").replace(u":", u"：")
            else:
                string = clearString(stripped).strip()
            strings.append(string)
        all_string = " ".join(strings)
        all_string = re.sub("\[\S+\]", "", all_string)
        items = re.findall(ur"((\S+)：\s*(\S+)?)", all_string)
        for item in items:
            key = item[1].strip()
            value = item[2].strip()
            if key not in relativeInfo:
                relativeInfo[key] = value
            else:
                relativeInfo[key] = "%s| %s" % (relativeInfo[key], value)
    detail_page_info["relativeInfo"] = relativeInfo

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
    from bs4 import BeautifulSoup
    f = open(r"D:\PythonProgram\SHLouPan\data\Test\taiyuehaoting022_detail.html")
    content = f.read()
    f.close()
    soup = BeautifulSoup(content, "html5lib", from_encoding="utf-8")
    info = {}
    info['url'] = u"http://taiyuehaoting022.fang.com/house/1110667829/housedetail.htm"
    info['soup'] = soup
    info['name'] = u"泰悦豪庭"
    info['id'] = 1 # test
    datadir = r"D:\PythonProgram\SHLouPan\data\Test"
    
    retcode, retInfo = jdugePage(info)
    print retInfo
    analysisPage(info, datadir)
