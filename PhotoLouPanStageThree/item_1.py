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
import torndb
from hashlib import md5

passwd = "123456"
lp_photo_links = "lp_photo_links"

def dealContent(info, dataDir=None):
    """
    判断当前页面是否为指定页面
    """
    content = info['content']
    path = info['urlpath']
    if content:
        sqlstring = "UPDATE lp_photo_links SET `status`=2, `store_path`='%s' WHERE `id`=%s" % (path, info['id'])
    else:
        sqlstring = "UPDATE lp_photo_links SET `status`=4 WHERE `id`=%s" % info['id']
    conn = torndb.Connection(host="192.168.1.119", database="data_transfer", user="frem", password=passwd)
    conn.execute(sqlstring)
    conn.close()


if __name__ == "__main__":
    pass
