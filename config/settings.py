"""
多平台爬虫系统配置文件
"""
import os
from datetime import datetime

# 数据库配置
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '12345678', 
    'database': 'multi_crawler',
    'charset': 'utf8mb4'
}

# 爬虫配置
CRAWLER_CONFIG = {
    'keyword': '李雨珊',
    'max_pages': 50,  # 最大爬取页数
    'delay_range': (2, 5),  # 请求间隔范围（秒）
    'retry_times': 3,  # 重试次数
    'timeout': 30,  # 请求超时时间
    'batch_size': 100,  # 批量插入数据库的大小
}

# User-Agent池
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
]

# 代理配置（可选）
PROXY_CONFIG = {
    'enabled': False,
    'proxies': [
        # 'http://proxy1:port',
        # 'http://proxy2:port',
    ]
}

# 日志配置
LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file_path': f'logs/crawler_{datetime.now().strftime("%Y%m%d")}.log'
}

# 微博API配置（如果使用官方API）
WEIBO_API_CONFIG = {
    'app_key': '',  # 请填入实际的app_key
    'app_secret': '',  # 请填入实际的app_secret
    'access_token': '',  # 请填入实际的access_token
    'base_url': 'https://api.weibo.com/2/'
}

# 爬取目标URL配置
WEIBO_URLS = {
    'search_url': 'https://s.weibo.com/weibo',
    'mobile_search_url': 'https://m.weibo.cn/api/container/getIndex',
    'pc_search_url': 'https://weibo.com/ajax/side/search'
}

# Cookie配置
COOKIE_CONFIG = {
    'enabled': True,
    'weibo_cookies': {
        # PC端Cookie (根据浏览器开发者工具获取的实际Cookie字段)
        '_s_tentry': 'passport.weibo.com',  # 入口页面标识
        'ALF': '02_1757926545',  # 认证生命周期标识
        'Apache': '1542649563414.1812.1755330040952',  # Apache服务器标识
        'SCF': 'Annsd8QK6lcqTCfV-ab6qvCErtNBSYG9lr6WH4rgtAdz1yPHjPYvEL7hu9AgyUcKz6v1dvf0Hpvl8CyRBWPpvVg.',  # 安全校验字段
        'SINAGLOBAL': '1542649563414.1812.1755330040952',  # 新浪全局标识
        'SUB': '_2A25FpDfBDeRhGeFG61QZ-SbNwjqIHXVm2DUJrDV_PUJbkNAYLUr7kW9NfnvU-HMzxFa8kgg9QS7p936_AgkWZDht',  # 用户登录凭证（核心字段）
        'SUBP': '0033WrSXqPxfM725Ws9jqgMF55529P9D9W51CmIk.SluideDK0FLQNaJ5JpX5KzhUgL.FoMRehqR1Knp1Kq2dJLoIpYLxKqLB-BL12eLxKqL1-eLB-2LxKMLB-zL1-qNeK.N',  # 用户权限凭证（核心字段）
        'ULV': '1755330040952:1:1:1:1542649563414.1812.1755330040952:',  # 用户级别验证
    },
    # 移动端Cookie
    'mobile_cookies': {
        'SUB': '',
        'SUBP': '',
        'SSOLoginState': '',
        '_T_WM': '',  # 移动端特有
        'MLOGIN': '1',
        'M_WEIBOCN_PARAMS': 'luicode%3D20000174'
    }
}

# 抖音API配置 - 2025年更新版本
DOUYIN_API_CONFIG = {
    # 基础应用信息
    'app_name': 'aweme',
    'version_code': '270600',  # 更新版本代码
    'version_name': '27.6.0',  # 更新版本名称
    'aid': '1128',  # 应用ID
    'channel': 'douyin_web',  # 更新渠道
    
    # 设备信息
    'device_platform': 'webapp',  # 更新为web平台
    'device_type': 'PC',
    'device_brand': 'PC',
    'os_api': '10',
    'os_version': '10',
    'language': 'zh-CN',
    'region': 'CN',
    
    # Web特有参数
    'pc_client_type': '1',
    'cookie_enabled': 'true',
    'screen_width': '1920',
    'screen_height': '1080',
    'browser_language': 'zh-CN',
    'browser_platform': 'Win32',
    'browser_name': 'Chrome',
    'browser_version': '120.0.0.0',
    'browser_online': 'true',
    
    # 搜索相关参数
    'search_source': 'normal_search',
    'query_correct_type': '1',
    'is_filter_search': '0',
    'from_group_id': '',
    'publish_time': '0',
    'sort_type': '0',  # 0:综合排序, 1:最新发布, 2:最多点赞
    'filter_duration': '0',  # 视频时长筛选
}

# 抖音URL配置 - 2025年更新版本
DOUYIN_URLS = {
    # 主要搜索接口 - 更新为最新可用接口
    'search_url': 'https://www.douyin.com/aweme/v1/web/general/search/single/',
    'search_url_backup': 'https://www.douyin.com/aweme/v1/web/search/item/',
    'search_url_mobile': 'https://m.douyin.com/web/api/v2/search/item/',
    
    # 详情接口
    'video_detail_url': 'https://www.douyin.com/aweme/v1/web/aweme/detail/',
    'user_info_url': 'https://www.douyin.com/aweme/v1/web/user/profile/other/',
    'comment_list_url': 'https://www.douyin.com/aweme/v1/web/comment/list/',
    
    # 新增接口
    'hot_search_url': 'https://www.douyin.com/aweme/v1/web/hot/search/list/',
    'suggest_url': 'https://www.douyin.com/aweme/v1/web/search/suggest/',
}

# 抖音Cookie配置
DOUYIN_COOKIE_CONFIG = {
    'enabled': True,
    'douyin_cookies': {
        'ttwid': '',  # 抖音设备ID
        'msToken': '',  # 消息令牌
        'odin_tt': '',  # 奥丁追踪ID
        'passport_csrf_token': '',  # CSRF令牌
        'passport_csrf_token_default': '',  # 默认CSRF令牌
        'sid_guard': '',  # 会话保护
        'uid_tt': '',  # 用户追踪ID
        'uid_tt_ss': '',  # 用户追踪ID（会话）
        'sid_tt': '',  # 会话ID
        'sessionid': '',  # 会话ID
        'sessionid_ss': '',  # 会话ID（会话存储）
        'store-region': 'cn-bj',  # 存储区域
        'store-region-src': 'uid',  # 存储区域来源
    }
}

# 平台配置
PLATFORM_CONFIG = {
    'weibo': {
        'name': '微博',
        'enabled': True,
        'spider_class': 'WeiboSpider',
        'urls': 'WEIBO_URLS',
        'cookies': 'COOKIE_CONFIG',
        'api_config': 'WEIBO_API_CONFIG'
    },
    'douyin': {
        'name': '抖音',
        'enabled': True,
        'spider_class': 'DouyinSpider',
        'urls': 'DOUYIN_URLS',
        'cookies': 'DOUYIN_COOKIE_CONFIG',
        'api_config': 'DOUYIN_API_CONFIG'
    }
}

# 数据存储配置
STORAGE_CONFIG = {
    'save_images': True,  # 是否保存图片
    'save_videos': True,  # 是否保存视频（抖音特有）
    'image_dir': 'data/images',
    'video_dir': 'data/videos',  # 视频存储目录
    'backup_enabled': True,  # 是否启用数据备份
    'backup_interval': 24  # 备份间隔（小时）
}