#!/usr/bin/env python
#coding: utf8

"""
修改日期        修改人        修改内容
2015-04-18    organo.xia     基础版本
2015-05-20    organo.xia     增加字符串转化时间函数:tranformTimeString.
"""

import os
import sys
import shutil
import datetime
import inspect
import zipfile

# function: get directory of current script, if script is built
# into an executable file, get directory of the excutable file
def current_file_directory():
    path = os.path.realpath(sys.path[0])        # interpreter starter's path
    if os.path.isfile(path):                    # starter is excutable file
        path = os.path.dirname(path)
        return os.path.abspath(path)            # return excutable file's directory
    else:                                       # starter is python script
        caller_file = inspect.stack()[1][1]     # function caller's filename
        return os.path.abspath(os.path.dirname(caller_file))# return function caller's file's directory

def deleteFileByCreateDay(dirPath, defaultDays=10):
    # 清除创建文件日期在defaultDays前的所有文件，默认为10天。
    dt = datetime.datetime.today()
    dirwithfile = []
    for root, dirs, files in os.walk(dirPath):
        for fname in files:
            filePath = os.path.join(root, fname)
            print filePath
            if os.path.isfile(filePath):
                createStamp = os.path.getctime(filePath)
                createDt = datetime.datetime.fromtimestamp(createStamp)
                deltatime = dt - createDt
                # 清理10前的数据文件
                if deltatime.days >= defaultDays:
                    os.remove(filePath)
                    info = "delete file %s" % filePath
                    print info
        
        for fdir in dirs:
            dirpath = os.path.join(root, fdir)
            print dirpath
            if os.path.isdir(dirpath):
                createStamp = os.path.getctime(dirpath)
                createDt = datetime.datetime.fromtimestamp(createStamp)
                deltatime = dt - createDt
                # 清理10前的数据文件
                if deltatime.days >= defaultDays:
                    try:
                        os.removedirs(dirpath)
                        info = "delete file %s" % dirpath
                        print info
                    except:
                        dirwithfile.append(dirpath)
    
    dirwithfile.reverse()
    for dirpath in dirwithfile:
        if os.path.isdir(dirpath):
            try:
                os.removedirs(dirpath)
            except:
                # 确实存在创建新文件的文件夹
                pass

def deleteDirByCreateDay(dirPath, defaultDays=10):
    # 清除创建文件日期在defaultDays前的所有文件夹，默认为10天。
    dt = datetime.datetime.today()
    for root, dirs, files in os.walk(dirPath):
        for fdir in dirs:
            dirpath = os.path.join(root, fdir)
            createStamp = os.path.getctime(dirpath)
            createDt = datetime.datetime.fromtimestamp(createStamp)
            deltatime = dt - createDt
            # 清理10前的数据文件
            if deltatime.days >= defaultDays:
                shutil.rmtree(dirpath)
                print dirpath
        
        for fname in files:
            fpath = os.path.join(root, fname)
            if os.path.isfile(fpath):
                createStamp = os.path.getctime(fpath)
                createDt = datetime.datetime.fromtimestamp(createStamp)
                deltatime = dt - createDt
                # 清理10前的数据文件
                if deltatime.days >= defaultDays:
                    os.remove(fpath)
                    print fpath

def deleteFileByExt(dirPath, defaultExt=".gz"):
    # 删除文件后缀以defaultExt的压缩文件，默认为".gz"。
    defaultExt = defaultExt.strip()
    for root, dirs, files in os.walk(dirPath):
        for fname in files:
            filePath = os.path.join(root, fname)

            if os.path.splitext(filePath)[1].startswith(defaultExt):
                os.remove(filePath)
                info = "delete file %s" % filePath

def fileCounts(fpath):
    try:
        counts = 0
        f = open(fpath, "rb")
        while f.readline():
            counts += 1
        f.close()
        return counts
    except:
        counts = 0
        return counts

def compressDirToZip(dirpath, zipname):
    assert(os.path.isdir(dirpath))
    if not os.path.isabs(zipname):
        zipname = os.path.join(current_file_directory(), zipname)
    try:
        zipfilename = os.path.basename(zipname)
        z = zipfile.ZipFile(zipfilename, mode="w", compression=zipfile.ZIP_DEFLATED)
        for root, dirs, files in os.walk(dirpath):
            for fname in files:
                fpath = os.path.join(root, fname)
                z.write(fpath)
        z.close()
        return True
    except:
        return False

def getOneTime(timeStr):
    """
    para timeStr: 格式化时间字符串。
    获取格式化时间。
    """
    from re import findall
    strPat = "((^((1[8-9]\d{2})|([2-9]\d{3}))([-\/\._])(10|12|0?[13578])([-\/\._])(3[01]|[12][0-9]|0?[1-9])$)|(^(" \
             "(1[8-9]\d{2})|([2-9]\d{3}))([-\/\._])(11|0?[469])([-\/\._])(30|[12][0-9]|0?[1-9])$)|(^((1[8-9]\d{2})|" \
             "([2-9]\d{3}))([-\/\._])(0?2)([-\/\._])(2[0-8]|1[0-9]|0?[1-9])$)|(^([2468][048]00)([-\/\._])(0?2)" \
             "([-\/\._])(29)$)|(^([3579][26]00)([-\/\._])(0?2)([-\/\._])(29)$)|(^([1][89][0][48])([-\/\._])(0?2)" \
             "([-\/\._])(29)$)|(^([2-9][0-9][0][48])([-\/\._])(0?2)([-\/\._])(29)$)|(^([1][89][2468][048])([-\/\._])" \
             "(0?2)([-\/\._])(29)$)|(^([2-9][0-9][2468][048])([-\/\._])(0?2)([-\/\._])(29)$)|(^([1][89][13579][26])" \
             "([-\/\._])(0?2)([-\/\._])(29)$)|(^([2-9][0-9][13579][26])([-\/\._])(0?2)([-\/\._])(29)$))"
    timeinfo = findall(strPat, timeStr)
    if timeinfo:
        timeinfo = [x for x in timeinfo[0] if x]
        year = timeinfo[3]
        month = timeinfo[5]
        day = timeinfo[7]
        return (year, month, day)

def getTimeBucket(timeStr):
    from re import findall
    strPat = "((((1[8-9]\d{2})|([2-9]\d{3}))([-\/\._])(10|12|0?[13578])([-\/\._])(3[01]|[12][0-9]|0?[1-9]))|" \
             "(((1[8-9]\d{2})|([2-9]\d{3}))([-\/\._])(11|0?[469])([-\/\._])(30|[12][0-9]|0?[1-9]))|" \
             "(((1[8-9]\d{2})|([2-9]\d{3}))([-\/\._])(0?2)([-\/\._])(2[0-8]|1[0-9]|0?[1-9]))|" \
             "(([2468][048]00)([-\/\._])(0?2)([-\/\._])(29))|(([3579][26]00)([-\/\._])(0?2)([-\/\._])(29))|" \
             "(([1][89][0][48])([-\/\._])(0?2)([-\/\._])(29))|(([2-9][0-9][0][48])([-\/\._])(0?2)([-\/\._])(29))|" \
             "(([1][89][2468][048])([-\/\._])(0?2)([-\/\._])(29))|(([2-9][0-9][2468][048])([-\/\._])(0?2)" \
             "([-\/\._])(29))|(([1][89][13579][26])([-\/\._])(0?2)([-\/\._])(29))|(([2-9][0-9][13579][26])([-\/\._])" \
             "(0?2)([-\/\._])(29)))"
    timeinfo = findall(strPat, timeStr)
    if len(timeinfo) == 2:
        starttime = timeinfo[0]
        starttime = [x for x in starttime if x]
        year1 = starttime[3]
        month1 = starttime[5]
        day1 = starttime[7]
        endtime = timeinfo[1]
        endtime = [x for x in endtime if x]
        year2 = endtime[3]
        month2 = endtime[5]
        day2 = endtime[7]
        return ((year1, month1, day1), (year2, month2, day2))

def tranformTimeString(timeStr, retform="time"):
    """
    参数 timeStr: 时间日期格式。
    格式化字符串时间，时间格式如下：
        全数字格式： 150520， 20150520
        带分隔符格式： 2015/05/20， 2015-05-20， 2015/5/20， 15/5/20
    注：日期格式必须为年、月、日，这种格式。
        默认六位时间的年份是20*年。
        全数字格式的年、月、日格式只有一位时，需添加零成整数位。
    参数 format: "time"/"datetime", 返回日期格式的时间格式，默认为time.struct_time类型，否则为datetime类型。
    返回值： 时间格式对象，None为转化失败。
    """
    assert(isinstance(timeStr, str))
    if timeStr.isdigit():
        timeStr = timeStr.strip()
        if len(timeStr) == 6:
            timestring = "20%s%s%s" % (timeStr[0:2], timeStr[2:4], timeStr[4:])
        elif len(timeStr) == 8:
            timestring = "%s%s%s" % (timeStr[0:4], timeStr[4:6], timeStr[6:])
        else:
            return None
    else:
        sp = ""
        for s in timeStr:
            if not s.isdigit():
                sp = s
                break
        timeStr = timeStr.strip().split(sp)
        if len(timeStr[0]) == 2:
            timeStr[0] = "20%s" % timeStr[0]
        timestring = "".join(timeStr)

    if retform.startswith("datetime"):
        strptime = datetime.datetime.strptime
    else:
        from time import strptime
    try:
        timeobj = strptime(timestring, "%Y%m%d")
    except:
        return None
    return timeobj


if __name__ == "__main__"    :
    #compressDirToZip(r"./", r"D:\first.zip")
    # print fileCounts(r"D:/xsx.txt")
    #print getOneTime("2015-12-32")
    #print getTimeBucket("2015-12-45 2008/03/12")
    print tranformTimeString("15-05-20")
