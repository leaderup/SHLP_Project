#!/usr/bin/env python
#coding: utf8

# lp_homepage

"""
去重，使用MapReduce提取重复对象:
1> Map函数
map=function (){
 emit(this.lid,{count:1})
}
2> Reduce函数
reduce=function (key,values){
 var cnt=0;   
values.forEach(function(val){ cnt+=val.count;});  
return {"count":cnt};
}
3> 生成执行函数
db.lp_homepage.mapReduce(map,reduce,{out:"mhpage2"})
"""


import os
import pymongo
import copy
from common_func import current_file_directory

pwd = current_file_directory()
datadir = os.path.join(pwd, 'data', "clearMongoDB")
if not os.path.isdir(datadir):
    os.makedirs(datadir)

# Mongo存储
client_mhpage2 = pymongo.MongoClient(host="192.168.1.83", port=27017)
collection_mhpage2 = client_mhpage2.loupan.get_collection("mhpage2")

# Mongo存储
client_homepage = pymongo.MongoClient(host="192.168.1.83", port=27017)
collection_homepage = client_homepage.loupan.get_collection("lp_homepage")

# 清除的ID
id_sets = []
fpath = os.path.join(datadir, "clearmongodb.txt")
f = open(fpath, "a+")

all_items = collection_mhpage2.find()
for item in all_items:
    is_valid = []
    _id = item['_id']
    value = item['value']
    link_id = _id['lid']
    count = int(value['count'])
    if count > 1:
        f.write("%s\n" % link_id)
        repeat_items = collection_homepage.find({"lid":link_id})
        for repeat in repeat_items:
            linkPath = repeat['linkPath']
            try:
                linkPath.encode('gbk')
                is_valid.append(repeat)
            except:
                print "lid: %s, count: %s, has dirty data." % (link_id, count)
                del_id = repeat['_id']
                collection_homepage.remove({'_id': del_id})
        else:
            collection_mhpage2.remove(item)

        for i in range(len(is_valid)):
            if i == 0:
                continue
            else:
                repeat = is_valid[i]
                del_id = repeat['_id']
                collection_homepage.remove({'_id': del_id})  

client_homepage.close()
client_mhpage2.close()

f.close()