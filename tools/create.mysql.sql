-- iptotal
CREATE TABLE `iptotal` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `ipaddr` int(11) unsigned DEFAULT NULL COMMENT 'IP地址',
  `port` int(11) DEFAULT NULL COMMENT '端口地址',
  `isvalid` tinyint(1) DEFAULT NULL COMMENT 'IP是否有效 0 无效  1 有效',
  `start` timestamp NULL DEFAULT NULL COMMENT '生效时间',
  `succ` int(11) DEFAULT NULL COMMENT '成功次数',
  `failed` int(11) DEFAULT NULL COMMENT '失败次数',
  `end` timestamp NULL DEFAULT NULL COMMENT '失效时间',
  UNIQUE KEY `id` (`id`),
  UNIQUE KEY `unique` (`ipaddr`,`port`)
) ENGINE=InnoDB AUTO_INCREMENT=49453098 DEFAULT CHARSET=utf8

-- lp_city_list
CREATE TABLE `lp_city_list` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增长ID',
  `provice` varchar(3) DEFAULT NULL COMMENT '省份',
  `city` varchar(8) DEFAULT NULL COMMENT '城市名',
  `city_SN` varchar(32) DEFAULT NULL COMMENT '城市名简写',
  `district` varchar(20) DEFAULT NULL COMMENT '区域名',
  `district_SN` varchar(60) DEFAULT NULL COMMENT '区域名简写',
  `stat_date` timestamp NULL DEFAULT NULL COMMENT '生成时间，记录生成时间',
  `task_date` timestamp NULL DEFAULT NULL COMMENT '任务执行时间',
  `catch_status` tinyint(4) DEFAULT '0' COMMENT '生成状态 0 初始化 1 读入计划 2 完成抓取 3 无数据 4 无页面 5 无法确定页面信息',
  `counts` int(11) DEFAULT '0' COMMENT '项目数量',
  `trash_page` varchar(8096) DEFAULT NULL COMMENT '两次读取页面失败，丢失页面序列号 以逗号分隔',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique` (`provice`,`city`,`district`)
) ENGINE=InnoDB AUTO_INCREMENT=24139 DEFAULT CHARSET=utf8

-- lp_city_list_main
CREATE TABLE `lp_city_list_main` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增长ID',
  `provice` varchar(3) DEFAULT NULL COMMENT '省份',
  `city` varchar(8) DEFAULT NULL COMMENT '城市名',
  `city_SN` varchar(32) DEFAULT NULL COMMENT '城市名简写',
  `district` varchar(20) DEFAULT NULL COMMENT '区域名',
  `district_SN` varchar(60) DEFAULT NULL COMMENT '区域名简写',
  `stat_date` timestamp NULL DEFAULT NULL COMMENT '生成时间，记录生成时间',
  `task_date` timestamp NULL DEFAULT NULL COMMENT '任务执行时间',
  `catch_status` tinyint(4) DEFAULT '0' COMMENT '生成状态 0 初始化 1 读入计划 2 完成抓取 3 无数据 4 无页面 5 无法确定页面信息',
  `counts` int(11) DEFAULT '0' COMMENT '项目数量',
  `trash_page` varchar(8096) DEFAULT NULL COMMENT '两次读取页面失败，丢失页面序列号 以逗号分隔',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique` (`provice`,`city`,`district`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8

-- lp_items
CREATE TABLE `lp_items` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增长ID',
  `cid` int(11) DEFAULT NULL COMMENT '城市唯一标识',
  `name` varchar(50) DEFAULT NULL COMMENT '小区项目名',
  `link` varchar(1024) DEFAULT NULL COMMENT '小区项目链接',
  `rid` varchar(20) DEFAULT '0' COMMENT '项目资源ID值',
  `catch_hp_status` tinyint(4) DEFAULT '0' COMMENT '楼盘主页信息状态 0 未初始化 1 初始化 2 完成抓取 3 无页面 4 无效页',
  `catch_status` tinyint(4) DEFAULT '0' COMMENT '详情页面状态 0 未初始化 1 初始化 2 完成抓取 3 无页面 4 无效页面 5 头部未获取到 6 主体未获取 7 主体部分未获取',
  `lpxq_link` varchar(1024) DEFAULT NULL COMMENT '详情页url',
  `catch_pic_status` tinyint(4) DEFAULT '0' COMMENT '楼盘像册状态 0 未初始化 1 初始化 2 完成抓取 3 无页面 4 无效页',
  `lpxc_link` varchar(1024) DEFAULT NULL COMMENT '像册面url',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=253794 DEFAULT CHARSET=utf8

-- lp_items_main
CREATE TABLE `lp_items_main` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增长ID',
  `cid` int(11) DEFAULT NULL COMMENT '城市唯一标识',
  `name` varchar(50) DEFAULT NULL COMMENT '小区项目名',
  `link` varchar(1024) DEFAULT NULL COMMENT '小区项目链接',
  `rid` varchar(20) DEFAULT '0' COMMENT '项目资源ID值',
  `catch_hp_status` tinyint(4) DEFAULT '0' COMMENT '楼盘主页信息状态 0 未初始化 1 初始化 2 完成抓取 3 无页面 4 无效页',
  `catch_status` tinyint(4) DEFAULT '0' COMMENT '详情页面状态 0 未初始化 1 初始化 2 完成抓取 3 无页面 4 无效页面 5 头部未获取到 6 主体未获取 7 主体部分未获取',
  `lpxq_link` varchar(1024) DEFAULT NULL COMMENT '详情页url',
  `catch_pic_status` tinyint(4) DEFAULT '0' COMMENT '楼盘像册状态 0 未初始化 1 初始化 2 完成抓取 3 无页面 4 无效页',
  `lpxc_link` varchar(1024) DEFAULT NULL COMMENT '像册面url',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8

-- lp_links
CREATE TABLE `lp_links` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT '自增ID小区唯一序列',
  `cid` int(11) NOT NULL COMMENT '楼盘省市链接ID',
  `name` varchar(100) DEFAULT NULL COMMENT '小区名',
  `link` varchar(1024) DEFAULT NULL COMMENT '楼盘链接地址',
  `district` varchar(100) DEFAULT NULL COMMENT '楼盘名称',
  `rid` bigint(12) unsigned DEFAULT NULL COMMENT '楼盘资源ID名',
  `home_status` tinyint(4) DEFAULT '0' COMMENT '楼盘首页状态 0 初始状态 1 初始化 2 正常页面 3 无页面 4 无数据 5 页面异常',
  `detail_url` varchar(1024) DEFAULT NULL COMMENT '楼盘详情链接',
  `detail_status` tinyint(4) DEFAULT '0' COMMENT '楼盘详情页请求状态 0 初始状态 1 初始化 2 无页面 3 无数据',
  `photo_url` varchar(1024) DEFAULT NULL COMMENT '楼盘相册链接',
  `photo_status` tinyint(4) DEFAULT '0' COMMENT '楼盘相册页信息',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique` (`cid`,`name`)
) ENGINE=InnoDB AUTO_INCREMENT=196626 DEFAULT CHARSET=utf8

-- lp_photo_links
CREATE TABLE `lp_photo_links` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '图片唯一ID值',
  `lid` int(11) DEFAULT NULL COMMENT '链接ID',
  `cid` int(11) DEFAULT NULL COMMENT '城市ID',
  `ptype` smallint(6) DEFAULT NULL COMMENT '图片类型',
  `name` varchar(128) DEFAULT NULL COMMENT '图片名称',
  `url` varchar(1024) DEFAULT NULL COMMENT '图片URL',
  `status` tinyint(4) DEFAULT '0' COMMENT '状态',
  `store_path` varchar(256) DEFAULT NULL COMMENT '存储路径',
  `page_type` tinyint(4) DEFAULT NULL COMMENT '页面类型',
  `samelink` int(11) DEFAULT NULL COMMENT '页面重复URL的ID',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4577859 DEFAULT CHARSET=utf8

-- lp_photo_summary
CREATE TABLE `lp_photo_summary` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '序列ID',
  `lid` int(11) DEFAULT NULL COMMENT 'lp_links''s id',
  `cid` int(11) DEFAULT NULL COMMENT 'lp_pool''s id',
  `url` varchar(256) DEFAULT NULL COMMENT '当前URL，page_type=1 新页面 page_type=2 旧页面',
  `rid` bigint(20) DEFAULT NULL COMMENT '资源ID',
  `photo_type` smallint(6) DEFAULT NULL COMMENT '相册类型',
  `total` int(11) DEFAULT NULL COMMENT '当前类型相册总数',
  `npage` smallint(6) DEFAULT NULL COMMENT '页码',
  `page_type` smallint(6) DEFAULT NULL COMMENT '相册网页页面类型',
  `status` tinyint(4) DEFAULT '0' COMMENT '抓取状态',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1251735 DEFAULT CHARSET=utf8

-- lp_photo_summary_distinct
CREATE TABLE `lp_photo_summary_distinct` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '序列ID',
  `lid` int(11) DEFAULT NULL COMMENT 'lp_links''s id',
  `cid` int(11) DEFAULT NULL COMMENT 'lp_pool''s id',
  `url` varchar(256) DEFAULT NULL COMMENT '当前URL，page_type=1 新页面 page_type=2 旧页面',
  `rid` bigint(20) DEFAULT NULL COMMENT '资源ID',
  `photo_type` smallint(6) DEFAULT NULL COMMENT '相册类型',
  `total` int(11) DEFAULT NULL COMMENT '当前类型相册总数',
  `npage` smallint(6) DEFAULT NULL COMMENT '页码',
  `page_type` smallint(6) DEFAULT NULL COMMENT '相册网页页面类型',
  `status` tinyint(4) DEFAULT '0' COMMENT '抓取状态',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique` (`lid`,`photo_type`,`npage`)
) ENGINE=InnoDB AUTO_INCREMENT=2217439 DEFAULT CHARSET=utf8

-- lp_pool
CREATE TABLE `lp_pool` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增长ID',
  `prov` varchar(6) DEFAULT NULL COMMENT '省名',
  `city` varchar(4) DEFAULT NULL COMMENT '市名',
  `url` varchar(64) DEFAULT NULL COMMENT '楼盘汇总页面URL',
  `status` tinyint(4) DEFAULT '0' COMMENT '当着页面抓取状态 0 默认 1 初始化 2 完成 3 无页面 4 无数据',
  `total` int(11) DEFAULT NULL COMMENT '当前城市总楼盘数',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique` (`prov`,`city`,`url`)
) ENGINE=InnoDB AUTO_INCREMENT=7068 DEFAULT CHARSET=utf8

-- lp_tmp_links
CREATE TABLE `lp_tmp_links` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT '自增ID小区唯一序列',
  `cid` int(11) NOT NULL COMMENT '楼盘省市链接ID',
  `name` varchar(100) DEFAULT NULL COMMENT '小区名',
  `link` varchar(1204) DEFAULT NULL COMMENT '楼盘链接地址',
  `district` varchar(100) DEFAULT NULL COMMENT '楼盘名称',
  `rid` bigint(12) unsigned DEFAULT NULL COMMENT '楼盘资源ID名',
  `home_status` tinyint(4) DEFAULT '0' COMMENT '楼盘首页状态 0 初始状态 1 初始化 2 无页面 3 无数据',
  `detail_status` tinyint(4) DEFAULT '0' COMMENT '楼盘详情页请求状态 0 初始状态 1 初始化 2 无页面 3 无数据',
  `phone_status` tinyint(4) DEFAULT NULL COMMENT '楼盘相册页信息',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique` (`cid`,`name`)
) ENGINE=InnoDB AUTO_INCREMENT=297032 DEFAULT CHARSET=utf8

-- pyscr_result
CREATE TABLE `pyscr_result` (
  `id` int(10) NOT NULL AUTO_INCREMENT COMMENT '自增ID值',
  `srvname` varchar(200) NOT NULL COMMENT '服务名',
  `start_time` datetime NOT NULL COMMENT '脚本执行开始时间',
  `is_succ` tinyint(1) NOT NULL COMMENT '脚本执行是否成功, 1: 成功 0 失败',
  `using_time` float DEFAULT NULL COMMENT '脚本执行使用时间',
  `tips` text COMMENT '日志内容',
  UNIQUE KEY `id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2632 DEFAULT CHARSET=utf8

-- sh_loupan
CREATE TABLE `sh_loupan` (
  `id` int(11) NOT NULL COMMENT '小区唯一ID值',
  `prov` varchar(6) NOT NULL COMMENT '所有省会',
  `city` varchar(4) NOT NULL COMMENT '所在城市',
  `name` varchar(100) NOT NULL COMMENT '小区名称',
  `district` varchar(64) DEFAULT NULL COMMENT '所在街道地址',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8
