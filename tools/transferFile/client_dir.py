#!/usr/bin/env python
#coding: utf8

import os
import re
import time
import socket
import requests
import traceback
from hashlib import md5
from json import loads
from uuid import uuid1

def getHostIP():
    hostname = socket.getfqdn(socket.gethostname())
    hostaddr = socket.gethostbyname(hostname)
    return hostaddr


ip = getHostIP()

baseDir = r"E:\ttest"
#baseDir = os.getcwd()
basename = "DownLoad"

def createFile(baseDir):
    for i in range(100):
        fname = str(uuid1())
        fpath = os.path.join(baseDir, fname)
        with open(fpath, 'w') as f:
            f.write(fname)
            f.close()

def download(fname, md5val, saveDir):
    # 下载文件
    downurl = r'http://%s/getFile' % ip
    data = {
        "filename": fname
    }
    r = requests.get(downurl, params=data)
    if r.status_code == 200:
        content = r.content
        
        m = md5()
        m.update(content)
        if m.hexdigest() != md5val:
            return False

        fbasename = os.path.basename(fname)
        fpath = os.path.join(saveDir, fbasename)
        try:
            with open(fpath, 'w') as f:
                f.write(content)
                f.close()
            print 'download: %s' % fname
            return True
        except:
            print traceback.format_exc()
            return False


def main():
    listfile = os.listdir(baseDir)
    bsre = re.compile("%s_(\d+)" % basename)

    posturl = r'http://%s/deleteFile' % ip
    

    # 扫描文件夹
    maxindex = 0
    for fname in listfile:
        idx = bsre.findall(fname)
        if idx:
            idx = int(idx[0])
            maxindex = max(maxindex, idx)

    if maxindex == 0:
        maxindex = 1

    filelist = []
    while 1:
        savedir = os.path.join(baseDir, "%s_%s" % (basename, maxindex))
        if os.path.isdir(savedir):
            curfiles = os.listdir(savedir)
            if len(curfiles) > 20000:
                maxindex += 1
                savedir = os.path.join(baseDir, "%s_%s" % (basename, maxindex))
                os.makedirs(savedir)
        else:
            os.makedirs(savedir)

            
        # 查有没有文件
        data = {
            'filelist': filelist
        }
        r = requests.post(posturl, data=data)
        getlist = loads(r.content)
        count = getlist['count']
        allfile = getlist['fileinfo']
        if count == 0:
            time.sleep(5)
            continue

        filelist = []
        for fname, md5val in allfile.iteritems():
            ret = download(fname, md5val, savedir)
            if ret:
                filelist.append(fname)

        
if __name__ == "__main__":
    main()

