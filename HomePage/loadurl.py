#!/usr/bin/env python
#coding: utf8

"""
塞url函数: urlput
"""

import os
import logging

def urlput(urlqueue, datadir, log=logging.getLogger("urlput")):
    info = {}
    info['url'] = r"http://fang.com/SoufunFamily.htm"
    info['urlpath'] = os.path.join(datadir, os.path.basename(info['url']))
    urlqueue.put(info)
    loginfo = u"load url finish."
    log.info(loginfo)
