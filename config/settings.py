"""
微博爬虫系统配置文件
"""
import os
from datetime import datetime

# 数据库配置
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '12345678', 
    'database': 'weibo_crawler',
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

# 数据存储配置
STORAGE_CONFIG = {
    'save_images': True,  # 是否保存图片
    'image_dir': 'data/images',
    'backup_enabled': True,  # 是否启用数据备份
    'backup_interval': 24  # 备份间隔（小时）
}