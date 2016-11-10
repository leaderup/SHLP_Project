# -*- coding:utf-8 -*-
__author__ = 'fremcode@gmail.com'

import requests
import AgentHeader
import ConfigParser
import encrypt
import os
import MySQLdb
import MyLog

project_path = '/data1/scripts/ClickSystem/'
log = MyLog.MyLog(path=project_path + 'log' + os.sep, name='click', type='sys', level='DEBUG')


def click_request(url, proxy, device):
    """
    单次点击请求(url统计需要302跳转,所以第一次请求返回200应该是错误请求,跳转之后请求返回的200才是正确能统计到的请求)
    :param url: 请求的url
    :param proxy: 请求时使用的代理
    :param device: 请求时的设备类型'android', 'ios', 'browser'
    :return: bool
    """
    agent = AgentHeader.user_agent(device)
    headers = {
        'User-Agent': agent,
        'Connection': 'keep-alive',
        'Accept-Language': 'zh-CN',
        'Accept-Encoding': 'zh-CN,zh;q=0.8,en;q=0.6',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    }
    proxy = {
        'http': proxy
    }
    try:
        req = requests.get(url=url, proxies=proxy, headers=headers, verify=False, allow_redirects=False)
        if req.status_code == 200:
            return True
        elif req.status_code == 302:
            url = req.headers['location']
            req = requests.get(url=url, proxies=proxy, headers=headers, verify=False, allow_redirects=False)
            if req.status_code == 200:
                return True
            elif req.status_code == 302:
                return False
            elif req.status_code == 404:
                return False
            else:
                return False
        else:
            return False
    except Exception, ex:
        print ex
        log.error('click request status:fail ' + str(ex))
        return False


def proxy_ip(order_id, num):
    host_url = 'http://dev.kuaidaili.com/api/getproxy/?orderid='+str(order_id)+'&num='+str(num)+'&browser=1&protocol=1&method=1&an_ha=1&sp2=1&sort=0&sep=2'
    try:
        req = requests.get(host_url)
        if req.status_code == 200:
            ip_all = req.text
            ip_list = ip_all.split('\n')
            return ip_list
        else:
            #log_string = 'Get proxy status:fail'
            #log.error(log_string)
            return False
    except Exception, ex:
        #log_string = 'Get proxy status:fail' + str(ex)
        #log.error(log_string)
        return False


def config(unit, name, is_decrypt):
    config_path = project_path + 'config.ini'
    config_obj = ConfigParser.ConfigParser()
    config_obj.readfp(open(config_path, 'rb'))
    result_string = config_obj.get(unit, name)

    encrypt_obj = encrypt.StringEncrypt()

    if is_decrypt == 1:
        result = encrypt_obj.decrypt(result_string, 'private.pem')
        return result
    elif is_decrypt == 0:
        return result_string
    else:
        return False


class MysqlConn:
    def __init__(self):
        host = config('db', 'host', 1)
        port = int(config('db', 'port', 1))
        user = config('db', 'user', 1)
        pass_word = config('db', 'pass_word', 1)
        self.db_name = config('db', 'db_name', 1)
        charset = config('db', 'charset', 1)

        conn = MySQLdb.connect(host=host, port=port, user=user, passwd=pass_word, db=self.db_name, charset=charset)
        cursor = conn.cursor()
        self.conn = conn
        self.cursor = cursor

    def __del__(self):
        self.cursor.close()
        self.conn.close()

    def task_add(self, value_tuple):
        sql_insert = 'insert into ' + self.db_name + '.pm_click_task(url,rate_type,rate_value,device,click_total,task_note,' \
                    't0,t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12,t13,t14,t15,t16,t17,t18,t19,t20,t21,t22,t23) ' \
                    'values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        try:
            self.cursor.execute(sql_insert, value_tuple)
            log.info('task add ' + value_tuple[0] + 'status:ok')
            self.conn.commit()
            return True
        except Exception, ex:
            log.error('task add ' + value_tuple[0] + 'status:fail ' + str(ex))
            return False

    def task_info(self, task_status=0):
        sql_select = "select id,pid,url,device,click_total,click,task_note from " + self.db_name + ".pm_click_task where task_status='" + str(task_status) + "'"
        try:
            self.cursor.execute(sql_select)
            result = self.cursor.fetchall()
            return result
        except Exception, ex:
            log.error('task info get status:fail ' + str(ex))
            return False

    def task_kill_list(self):
        sql_select = "select pid from " + self.db_name + ".pm_task_kill"
        try:
            self.cursor.execute(sql_select)
            result = self.cursor.fetchall()
            return result
        except Exception, ex:
            log.error('task info get kill list status:fail ' + str(ex))
            return False

    def task_kill(self, pid):
        sql_select = "select pid from " + self.db_name + ".pm_click_task where task_status='1'"
        self.cursor.execute(sql_select)
        result_t = self.cursor.fetchall()
        result_list = list()
        for result in result_t:
            result_list.append(str(result[0]))

        if pid not in result_list:
            return False
        else:
            sql_insert = 'insert into ' + self.db_name + '.pm_task_kill(pid) values(%s)'
            try:
                self.cursor.execute(sql_insert, pid)
                self.conn.commit()
            except Exception, ex:
                log.error(sql_insert + ' status:fail ' + str(ex))
                return False

            sql_update = "update " + self.db_name + ".pm_click_task set task_status=3 where pid='" + pid + "'"
            try:
                self.cursor.execute(sql_update)
                self.conn.commit()
            except Exception, ex:
                log.error(sql_update + ' status:fail ' + str(ex))
                return False
            return True

    def task_start(self, pid):
        sql_select = "select pid from " + self.db_name + ".pm_click_task where task_status='1'"
        self.cursor.execute(sql_select)
        result_t = self.cursor.fetchall()
        result_list = list()
        for result in result_t:
            result_list.append(str(result[0]))

        if pid in result_list:
            return False
        else:
            sql_update = "update " + self.db_name + ".pm_click_task set task_status=0,click=0  where pid='" + pid + "'"
            try:
                self.cursor.execute(sql_update)
                self.conn.commit()
            except Exception, ex:
                log.error(sql_update + ' status:fail ' + str(ex))
                return False
            return True

    def task_kill_table_del(self, pid):
        sql_delete = "delete from " + self.db_name + ".pm_task_kill WHERE pid='" + str(pid) + "'"
        try:
            self.cursor.execute(sql_delete)
            self.conn.commit()
        except Exception, ex:
            log.error(sql_delete + ' status:fail ' + str(ex))
            return False
        return True

    def task_list(self):
        result = dict()
        sql_select = 'select id,url,rate_value,device,click_total,t0,t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12,t13,t14,t15,' \
                     't16,t17,t18,t19,t20,t21,t22,t23 from ' + self.db_name + '.pm_click_task where task_status=0'
        try:
            self.cursor.execute(sql_select)
            res = self.cursor.fetchall()
            for i in res:
                result[i[0]] = {
                    'url': i[1],
                    'rate_value': i[2],
                    'device': i[3],
                    'click_total': i[4],
                    't0': i[5],
                    't1': i[6],
                    't2': i[7],
                    't3': i[8],
                    't4': i[9],
                    't5': i[10],
                    't6': i[11],
                    't7': i[12],
                    't8': i[13],
                    't9': i[14],
                    't10': i[15],
                    't11': i[16],
                    't12': i[17],
                    't13': i[18],
                    't14': i[19],
                    't15': i[20],
                    't16': i[21],
                    't17': i[22],
                    't18': i[23],
                    't19': i[24],
                    't20': i[25],
                    't21': i[26],
                    't22': i[27],
                    't23': i[28]
                }
            return result
        except Exception, ex:
            log.error('select task list status:fail ' + str(ex))
            return False

    def task_begin(self, task_id, pid):
        sql_update = "update " + self.db_name + ".pm_click_task set pid=" + str(task_id) + ",task_status=1 where id=" + str(task_id)
        try:
            self.cursor.execute(sql_update)
            self.conn.commit()
            return True
        except Exception, ex:
            log.error('update ' + str(task_id) + ' task begin info status:fail ' + str(ex))
            return False

    def task_done(self, task_id):
        sql_update = "update " + self.db_name + ".pm_click_task set pid=0,task_status=2 where id=" + str(task_id)
        try:
            self.cursor.execute(sql_update)
            self.conn.commit()
            return True
        except Exception, ex:
            log.error('update ' + str(task_id) + ' task done info status:fail ' + str(ex))
            return False

    def task_except(self, task_id):
        sql_update = "update " + self.db_name + ".pm_click_task set pid=0,task_status=3 where id=" + str(task_id)
        try:
            self.cursor.execute(sql_update)
            self.conn.commit()
            return True
        except Exception, ex:
            log.error('update ' + str(task_id) + ' task except info status:fail ' + str(ex))
            return False

    def task_click_add(self, url):
        sql_update = "update " + self.db_name + ".pm_click_task set click=click+1 where url='" + url + "'"
        try:
            self.cursor.execute(sql_update)
            self.conn.commit()
        except Exception, ex:
            log.error('update ' + str(url) + ' click+1 status:fail ' + str(ex))
            return False

    def task_click_done(self, url):
        sql_select = "select click from " + self.db_name + ".pm_click_task where url='" + url + "'"
        try:
            self.cursor.execute(sql_select)
            result = self.cursor.fetchall()
            return result[0][0]
        except Exception, ex:
            log.error(sql_select + ' status:fail-' + str(ex))

if __name__ == '__main__':
    #click_request('http://um0.cn/253aqE', '', 'ios')
    ip = proxy_ip('963599851676265', 9)
    print ip
