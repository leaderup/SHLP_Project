#!/usr/bin/env python
#coding: utf8

import os
import time
import torndb
import requests
import traceback
# from chardet import detect
from log import Log
from hashlib import md5
from MySpider import user_agent
from Queue import Queue
from threading import Thread
from common_func import current_file_directory
from proxy.common import proxy_ip

# 抓取代理线程数
workA = 1
# 爬取网址线程数
workB = 100
# 启用本地导入模式
loadLocal = True
# 代理，当不用代理时会自动限速 5s
usingProxy = True
iptable = "iptotal"
passwd = "123456"
orderid = '963599851676265'
mainpage = "http://imgs.soufun.com/"
pwd = current_file_directory()
datadir = os.path.join(pwd, "data")
# 线程终止
isAlive = True
if not os.path.isdir(datadir):
    os.makedirs(datadir)
# URL日志
def myLog():
    l = Log(logname="urlServer")
    l.streamHandler()
    l.fileHandler(logLevel=40, fpath=os.path.join(pwd, "Log/urlServer.log"))
    return l.logger
uslog = myLog()
# 代理日志
def uaLog():
    l = Log(logname="proxyServer")
    l.streamHandler()
    l.fileHandler(fpath=os.path.join(pwd, "Log/proxyServer.log"))
    return l.logger
proxylog = uaLog()

# IP地址转字符
ipToStr = lambda x: sum([256**j*int(i) for j, i in enumerate(x.split('.')[::-1])])

def pingUrl(proxystring, url=mainpage):
    proxies = {
        "http": proxystring
    }
    headers = {
        'User-Agent': user_agent("pc"),
    }
    # 超时时间
    waittime = 1
    while 1:
        try:
            r = requests.get(url, headers=headers, proxies=proxies, timeout=waittime)
            loginfo = "%s %s" % (proxystring, r.status_code)
            proxylog.info(loginfo)
            return True
            """
            if r.status_code == 200:
                return True
            else:
                return False
            """
        except requests.Timeout, e:
            waittime += 1
            if waittime < 2:
                continue
            else:
                loginfo = "%s time out." % proxystring
                proxylog.info(loginfo)
                return False
        except:
            loginfo = "%s exception." % proxystring
            proxylog.error(loginfo)
            return False

def initMySQLProxy():
    # 清除无效IP及超过四个小时废IP地址
    sqlstring = "DELETE FROM iptotal WHERE `isvalid`=0 AND (UNIX_TIMESTAMP(NOW()) - UNIX_TIMESTAMP(`end`)) > 10*3600"
    conn = torndb.Connection(host="192.168.1.119", database="data_transfer", user="frem", password=passwd)
    conn.execute(sqlstring)
    conn.close()

def getipaddr():
    # 判断是否需要拉取数据
    sqlstring = "SELECT COUNT(*) AS counts FROM iptotal WHERE `isvalid`=1 AND `failed`<4"
    conn = torndb.Connection(host="192.168.1.119", database="data_transfer", user="frem", password=passwd)
    counts = conn.query(sqlstring)
    conn.close()
    if counts:
        counts = int(counts[0]['counts'])
        loginfo = "valid proxy ip address number: %s." % counts
        proxylog.info(loginfo)
        if counts > workB * 10:
            return True
    ips = proxy_ip(orderid, 900)
    if ips and isinstance(ips, list):
        for prstr in ips:
            ispass = pingUrl(prstr)
            addr, port = prstr.split(":")
            addr = ipToStr(addr)
            timestring = time.strftime("%Y-%m-%d %H:%M:%S")
            if ispass:
                items = (iptable, addr, port, 1, timestring, 1, 0, timestring)
            else:
                items = (iptable, addr, port, 0, timestring, 0, 1, timestring)
            sqlstring = "REPLACE INTO %s(`ipaddr`, `port`, `isvalid`, `start`, `succ`, `failed`, `end`) VALUES(%s, %s, %s, '%s', %s, %s, '%s')" % items
            conn = torndb.Connection(host="192.168.1.119", database="data_transfer", user="frem", password=passwd)
            conn.execute(sqlstring)
            conn.close()
        return True
    else:
        loginfo = "get none proxy ip addr."
        uslog.info(loginfo)
        return False

def updateproxy():
    global isAlive
    initMySQLProxy()

    sleeptime = 60
    while 1:
        #time.sleep(180)
        if not isAlive:
            break
        # 隔5秒更新proxy
        getipaddr()
        time.sleep(sleeptime)

    loginfo = u"catch proxy ip thread stop."
    proxylog.debug(loginfo)

class souHuUrl(Thread):
    def __init__(self, inq, outq):
        super(souHuUrl, self).__init__()
        self.inq = inq
        self.outq = outq
        self.proxies = list()
        self.trashproxies = dict()

    def updateproxies(self):
        sqlset = set()
        trashproxies = self.trashproxies
        self.trashproxies = {}
        if not usingProxy:
            # 不使用代理
            return None
        for key, value in trashproxies.iteritems():
            if value:
                sqlstring = "UPDATE %s SET `succ`=`succ`+%s, `end`=NOW() WHERE `id`=%s" % (iptable, value, key)
            else:
                sqlstring = "UPDATE %s SET `failed`=`failed`+1, `end`=NOW() WHERE `id`=%s" % (iptable, key)
            sqlset.add(sqlstring)

        conn = torndb.Connection(host="192.168.1.119", database="data_transfer", user="frem", password=passwd)
        for ipsql in sqlset:
            uslog.info(ipsql)
            conn.execute(ipsql)

        sqlstring = "SELECT id, CONCAT_WS(':', INET_NTOA(ipaddr), `port`) as proxy FROM iptotal WHERE `isvalid`=1 AND `failed`<4"
        self.proxies = conn.query(sqlstring)
        conn.close()

    def run(self):
        # time.sleep(1000)
        empty_execution = 0
        interative = 5
        loginfo = u"souHuUrl %s catch html page start." % self.getName()
        uslog.debug(loginfo)
        while 1:
            if not isAlive:
                self.updateproxies()
                break
            try:
                info = self.inq.get_nowait()
                # loginfo = "In Queue Url Size: %s.\n%s" % (self.inq.qsize(), info)
                # uslog.info(loginfo)
            except:
                # 强刷一次状态
                if len(self.trashproxies):
                    self.updateproxies()
                if empty_execution:
                    loginfo = u"souHuUrl %s wait %s(s) but cann't get url to catch." % (self.getName(), interative*empty_execution)
                    uslog.debug(loginfo)
                time.sleep(interative)
                empty_execution += 1
                if empty_execution > 24:
                    break
            else:
                # #注释
                if not usingProxy:
                    time.sleep(5)

                self._info = info
                self.work()

        # 结束
        loginfo = u"souHuUrl %s catch html page stop." % self.getName()
        uslog.info(loginfo)

    def saveUrl(self, content):
        info = self._info
        savepath = info['urlpath']
        if not savepath:
            md5obj = md5()
            md5obj.update(str(self.url))
            fname = md5obj.hexdigest()
            savepath = os.path.join(downdir, fname)
        if savepath:
            dirpath = os.path.dirname(savepath)
            if not os.path.isdir(dirpath):
                if dirpath:
                    os.makedirs(dirpath)
            with open(savepath, "w") as f:
                if isinstance(content, str):
                    f.write(content)
                else:
                    f.write(str(content))
                f.close()

    def getproxies(self, test=False, url=mainpage):
        """
        :param test: True return a proxy what can connect to mainpage
                     False return a proxy from database
        :param url:  you test main page, such as baidu.com
        :return: (ipaddress, id)
        """
        while 1:
            if not len(self.proxies):
                self.updateproxies()
                continue
            else:
                proxyinfo = self.proxies.pop()
                addr = proxyinfo["proxy"]
                mid = proxyinfo["id"]
            if not test:
                return addr, mid
            else:
                proxies = {
                    "http": addr
                }
                try:
                    r = requests.get(url, headers=self.headers, proxies=proxies, timeout=10)
                    if r.status_code == 200:
                        self.trashproxies[mid] = 1
                        return addr, mid
                except:
                    self.trashproxies[mid] = 0

    def searchLocalUrlPath(self, path_name):
        if not os.path.isfile(path_name):
            base_dir, file_name = os.path.split(path_name)
            if base_dir:
                data_dir, module_name = os.path.split(base_dir)
                i = 1
                while 1:
                    module_dir = "%s_%s" % (module_name, i)
                    base_dir = os.path.join(data_dir, module_dir)
                    if os.path.isdir(base_dir):
                        path = os.path.join(base_dir, file_name)
                        if os.path.isfile(path):
                            return path
                    else:
                        break
                    i = i + 1

        return path_name

    def obtainUrl(self):
        """
            处理请求所有URL
        """
        max_catch = 6
        info = self._info
        self.url = info['url']
        content = ""

        # 取url信息,6次机会，其中有4次为常用IP拉取
        for i in range(max_catch):
            if usingProxy:
                if i < 4:
                    addr, mid = self.getproxies()
                else:
                    addr, mid = self.getproxies(True)                
                proxies = {
                    "http": addr
                }
            else:
                proxies = {}
            # 取本地数据
            if loadLocal:
                info['urlpath'] = self.searchLocalUrlPath(info['urlpath'])
                urlpath = info['urlpath']
                if os.path.isfile(urlpath):
                    try:
                        with open(urlpath) as fp:
                            content = fp.read()
                            fp.close()
                        info['content'] = content
                        return True
                    except:
                        loginfo = "URL: %s, FILEPATH: %s.\n" % (self.url, urlpath)
                        loginfo += traceback.format_exc()
                        uslog.error(loginfo)

            # loginfo = u"%s URL: %s, catch times: %s you like" % (self.getName(), self.url, i)
            # uslog.info(loginfo)
            try:
                r = requests.get(self.url, headers=self.headers, proxies=proxies, timeout=100)
                if r.status_code == 200:
                    try:
                        content = r.content.decode('gbk').encode('utf8')
                    except:
                        content = r.content
                    self.saveUrl(content)
                    if usingProxy:
                        if mid in self.trashproxies:
                            self.trashproxies[mid] += 1
                        else:
                            self.trashproxies[mid] = 1
                    info['content'] = content
                    return True
            except:
                loginfo = u"URL: %s, catch times: %s\n" % (self.url, i)
                loginfo += traceback.format_exc()
                uslog.debug(loginfo)
                if usingProxy:
                    if mid in self.trashproxies:
                        self.trashproxies[mid] -= 1
                    else:
                        self.trashproxies[mid] = 0
        else:
            loginfo = u"URL: %s can't get page within %s times." % (self.url, max_catch)
            uslog.error(loginfo)
            info['content'] = content
        return False

    def work(self):
        headers = {
            "User-Agent": user_agent("pc")
        }
        self.headers = headers
        issucc = self.obtainUrl()
        if issucc:
            self.outq.put(self._info)
            loginfo = "url: %s is success." % self.url
            uslog.info(loginfo)
        else:
            loginfo = "url: %s is failed." % self.url
            uslog.error(loginfo)

def initQueue():
    queue = Queue()
    urls = [
        "http://newhouse.fang.com/house/s/",
        "http://newhouse.sh.fang.com/house/s/",
        "http://newhouse.gz.fang.com/house/s/",
        "http://newhouse.sz.fang.com/house/s/"
    ]

    for url in urls:
        info = {}
        info["url"] = url
        idx = urls.index(url)
        info["urlpath"] = "%s.html" % idx
        queue.put(info)

    return queue

def urlproxy(inq, outq):
    global isAlive
    threadA = []
    if usingProxy:
        for i in range(workA):
            thread = Thread(target=updateproxy)
            thread.setDaemon(True)
            threadA.append(thread)
            thread.start()

    threadB = []
    for i in range(workB):
        thread = souHuUrl(inq, outq)
        thread.setDaemon(True)
        threadB.append(thread)
        thread.start()

    for thread in threadB:
        thread.join()

    isAlive = False

    for thread in threadA:
        thread.join()

if __name__ == "__main__":
    """
    inq = initQueue()
    outq = Queue()
    urlproxy(inq, outq)
    """

    updateproxy()