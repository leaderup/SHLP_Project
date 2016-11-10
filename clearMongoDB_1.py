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
client_details_distinct = pymongo.MongoClient(host="192.168.1.83", port=27017)
collection_details_distinct = client_details_distinct.loupan.get_collection("lp_details_distinct")

# Mongo存储
client_details = pymongo.MongoClient(host="192.168.1.83", port=27017)
collection_details = client_details.loupan.get_collection("lp_details")

# 清除的ID
id_sets = []
fpath = os.path.join(datadir, "cleardetails.txt")
f = open(fpath, "a+")

all_items = collection_details_distinct.find()
for item in all_items:
    is_valid = []
    _id = item['_id']
    value = item['value']
    link_id = _id['lid']
    count = int(value['count'])
    if count > 1:
        f.write("%s\n" % link_id)
        repeat_items = collection_details.find({"lid":link_id})
        for repeat in repeat_items:
            trafic = repeat['trafic']
            if trafic:
                try:
                    trafic.encode('gbk')
                    is_valid.append(repeat)
                except:
                    print "lid: %s, count: %s, has dirty data." % (link_id, count)
                    del_id = repeat['_id']
                    collection_details.remove({'_id': del_id})
        else:
            collection_details_distinct.remove(item)

        for i in range(len(is_valid)):
            if i == 0:
                continue
            else:
                repeat = is_valid[i]
                del_id = repeat['_id']
                collection_details.remove({'_id': del_id})  

client_details.close()
client_details_distinct.close()

f.close()