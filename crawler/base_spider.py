"""
爬虫基础抽象类
提供通用的爬虫功能和接口定义
"""
import requests
import time
import random
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode

from utils.data_storage_manager import DataStorageManager
from utils.helpers import get_random_user_agent

logger = logging.getLogger(__name__)

class BaseSpider(ABC):
    """爬虫基础抽象类"""
    
    def __init__(self, storage_manager: DataStorageManager = None):
        self.session = requests.Session()
        self.storage_manager = storage_manager
        self.crawled_ids = set()
        
        # 设置基础请求头
        self.session.headers.update({
            'User-Agent': get_random_user_agent(),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """获取平台名称"""
        pass
    
    @abstractmethod
    def get_platform_config(self) -> Dict[str, Any]:
        """获取平台配置"""
        pass
    
    @abstractmethod
    def search_content(self, keyword: str, page: int = 1) -> List[Dict[str, Any]]:
        """搜索内容 - 子类必须实现"""
        pass
    
    @abstractmethod
    def parse_content_item(self, item_data: Dict[str, Any], keyword: str) -> Optional[Dict[str, Any]]:
        """解析单个内容项 - 子类必须实现"""
        pass
    
    def setup_session(self):
        """设置会话配置 - 子类可重写"""
        config = self.get_platform_config()
        
        # 设置代理
        if config.get('proxy_config', {}).get('enabled'):
            proxies = config['proxy_config'].get('proxies', [])
            if proxies:
                proxy = random.choice(proxies)
                self.session.proxies = {'http': proxy, 'https': proxy}
        
        # 设置Cookie
        cookie_config = config.get('cookie_config', {})
        if cookie_config.get('enabled'):
            cookies = cookie_config.get('cookies', {})
            for name, value in cookies.items():
                if value:  # 只设置非空Cookie
                    domain = self._get_cookie_domain()
                    self.session.cookies.set(name, value, domain=domain)
    
    def _get_cookie_domain(self) -> str:
        """获取Cookie域名 - 子类可重写"""
        return f".{self.get_platform_name().lower()}.com"
    
    def crawl_with_retry(self, keyword: str, page: int = 1, max_retries: int = 3) -> List[Dict[str, Any]]:
        """带重试机制的爬取"""
        for attempt in range(max_retries):
            try:
                results = self.search_content(keyword, page)
                if results:
                    return results
                
                logger.warning(f"第 {attempt + 1} 次尝试未获取到数据")
                
            except Exception as e:
                logger.warning(f"第 {attempt + 1} 次尝试失败: {e}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(2, 5))
                    # 更换User-Agent
                    self.session.headers['User-Agent'] = get_random_user_agent()
        
        logger.error(f"爬取失败，已重试 {max_retries} 次")
        return []
    
    def random_delay(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """随机延迟"""
        delay = random.uniform(min_delay, max_delay)
        logger.debug(f"等待 {delay:.2f} 秒")
        time.sleep(delay)
    
    def validate_response(self, response: requests.Response) -> bool:
        """验证响应是否有效"""
        if response.status_code != 200:
            logger.warning(f"响应状态码异常: {response.status_code}")
            return False
        
        # 检查是否被重定向到登录页面
        if 'login' in response.url.lower() or '登录' in response.text:
            logger.warning("检测到被重定向到登录页面")
            return False
        
        # 检查是否包含反爬虫提示
        if '验证码' in response.text or 'captcha' in response.text.lower():
            logger.warning("检测到验证码或反爬虫机制")
            return False
        
        return True
    
    def save_raw_data(self, data: List[Dict[str, Any]], page: int = None):
        """保存原始数据 - 传递平台信息"""
        if self.storage_manager and data:
            platform_name = self.get_platform_name().lower()
            self.storage_manager.save_raw_data(data, page, f"{platform_name}_data", platform_name)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取爬取统计信息"""
        return {
            'platform': self.get_platform_name(),
            'crawled_count': len(self.crawled_ids),
            'session_cookies': len(self.session.cookies),
            'session_headers': dict(self.session.headers)
        }