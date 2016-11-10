#!/usr/bin/env python
#coding:utf8

import os
import time
import re
from shutil import move

idx = 6
data_path = r"/data1/scripts/SHLouPan/data/"
module_names = [
	"HomePage",
        "HouseCounts",
        "LoupanLink",       # 城市链接 2
        "LoupanHomepage",   # 首页 3
        "XQPageLouPan",     # 详情页 4
        "PhotoLouPanStageOne",      # 相册页 - 相册类型与总数 5
        "PhotoLouPanStageTwo",      # 相册页 - 页面类型为1，Ajax请求相册页面 6
        "PhotoLouPanStageThree",      # 相册页 - 页面类型为2，页面解析 7
]
init_path = os.path.join(data_path, module_names[idx])


#init_path = r"/home/dirs"
#init_path = r"/data1/scripts/SHLouPan/data/PhotoLouPanStageTwo"
#init_path = r"/data1/scripts/SHLouPan/data/PPP"
if not os.path.isdir(init_path):
	os.makedirs(init_path)

basedir = os.path.dirname(init_path)
basename = os.path.basename(init_path)

all_dir = os.listdir(basedir)
filter_dirs = []
recpl = re.compile(r"%s_\d+" % basename)
for dirs in all_dir:
	if recpl.match(dirs):
		filter_dirs.append(dirs)
filter_dirs.sort()
index = len(filter_dirs) + 1

while 1:
	init_path_files = os.listdir(init_path)
	if len(init_path_files) > 20000:
		new_dir = os.path.join(basedir, "%s_%s" % (basename, index))
		if not os.path.isdir(new_dir):
			os.makedirs(new_dir)
			file_count = 0
			print "create new dir: %s" % new_dir
			for fname in init_path_files:
				if file_count > 20000:
					break;
				old_path = os.path.join(init_path, fname)
				new_path = os.path.join(new_dir, fname)
				move(old_path, new_path)
				file_count += 1
		else:
			index += 1
	else:
		time.sleep(5)









