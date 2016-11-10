#!/usr/bin/env python
#coding: utf8

import re
import os
import torndb
import time
from PIL import Image

passwd = '123456'
table = 'lp_photo_links_t_t'
data_dir = r'D:\PythonProgram\SHLouPan\PhotoLouPanStageThree\mtools\picture'

path = os.path.join(os.getcwd(), 'picture')
idcpl = re.compile('\d+_\d+_(\d+)')
resizable_url = re.compile('\d+x\d+')

conn = torndb.Connection(host="192.168.1.119", database="data_transfer", user="frem", password=passwd)

def clear(fpath):
    isdelete = False
    retry = False

    fname = os.path.basename(fpath)
    db_id = idcpl.findall(fname)[0]
    sql_str = "select * from %s where `id`='%s'" % (table, db_id)
    row = conn.query(sql_str)
    if not row:
        return None
    else:
        row = row[0]

    url = row['url']
    url_basename = os.path.basename(url)
    samelink = row['samelink']
    if int(samelink) > 0:
        isdelete = True

    try:
        with open(fpath, 'rb') as fp:
            img = Image.open(fp)
            fp.close()
            x, y = img.size
    except:
        isdelete = True
        retry = True
        x, y = (0, 0)

    if x > 600 or y > 500:
        # 如果图片够大，则不需要更新
        pass
    else:
        if resizable_url.search(url_basename):
            retry = True
            isdelete = True

    if retry:
        sql_str = "update %s set `status`=0 where `id`='%s'" % (table, db_id)
        #print sql_str
        conn.execute(sql_str)

    if isdelete:
        os.remove(fpath)

f = open('recode.txt', 'a+')
j = 0
for dirpath, dirnames, filenames in os.walk(data_dir):
    i = 0
    j = j + 1
    print "scan the %d's dir: %s" % (j, dirpath)
    for filename in filenames:
        i = i + 1
        fpath = os.path.join(dirpath, filename)
        try:
            clear(fpath)
        except:
            f.write("%s\n" % fpath)
        if i % 1000 == 0:
            print "%s - %s" % (time.ctime(), i)

f.close()
conn.close()

