#!/usr/bin/env python
#coding: utf8

"""
发送文件
"""
import os
import json
import socket
from hashlib import md5
from uuid import uuid1
from flask import Flask, request, send_from_directory

def getHostIP():
    hostname = socket.getfqdn(socket.gethostname())
    hostaddr = socket.gethostbyname(hostname)
    return hostaddr

app = Flask(__name__)
ip = getHostIP()
isTest = False

baseDir = r"E:\Test"
#baseDir = os.getcwd()
#baseDir = r"/home/test"

@app.route('/', methods=['GET', 'POST'])
def test():
    if request.method == "POST":
        return "post ok!"
    else:
        return 'test ok!'

def createFile(baseDir):
    for i in range(100):
        fname = str(uuid1())
        fpath = os.path.join(baseDir, fname)
        with open(fpath, 'w') as f:
            f.write(fname)
            f.close()

@app.route('/listFile')
def listFile():
    listfile = os.listdir(baseDir)
    
    info = {
        "numbers": len(listfile),
        "names": listfile
    }
    return json.dumps(info)

@app.route('/getFile')
def getFile():
    fname = request.args.get('filename')
    if fname:
        if os.path.isabs(fname):
            if fname.startswith(baseDir):
                fname = fname.replace(baseDir, '')
                if not fname.startswith('/'):
                    fname = './%s' % fname
        return send_from_directory(baseDir, fname)
    else:
        return ''

def fileMd5(fpath):
    m = md5()
    with open(fpath) as f:
        m.update(f.read())
        f.close()
    return m.hexdigest()

@app.route('/deleteFile', methods=['GET', 'POST'])
def deleteFile():
    count = 0
    max_to_down = 200
    if request.method == "POST":
        filelists = request.form.getlist('filelist')
        for fpath in filelists:
            #fpath = os.path.join(baseDir, fname)
            if os.path.isfile(fpath):
                os.remove(fpath)

        # 生成文件
        if isTest:
            createFile(baseDir)

        # listfile = os.listdir(baseDir)
        filedict = {}
        for root, dirs, fnames in os.walk(baseDir):
            if not max_to_down:
                break
            for fname in fnames:
                filePath = os.path.join(root, fname)
                # Md5文件校验
                md5val = fileMd5(filePath)
                filedict[filePath] = md5val
                count += 1

                max_to_down -= 1
                if not max_to_down:
                    break

        """
        for fname in listfile:
            md5val = fileMd5(os.path.join(baseDir, fname))
            filedict[fname] = md5val
            count += 1

            max_to_down -= 1
            if not max_to_down:
                break
        """

        info = {
            "count": count,
            "fileinfo": filedict
        }
        return json.dumps(info)
    else:
        return 'post'

if __name__ == "__main__":
    app.run(host=ip, port=80)
