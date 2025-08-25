"""
微博爬虫核心模块
"""
import requests
import json
import time
import random
import re
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode, quote
from bs4 import BeautifulSoup

from config.settings import CRAWLER_CONFIG, USER_AGENTS, PROXY_CONFIG, WEIBO_URLS, COOKIE_CONFIG
from utils.data_processor import DataProcessor
from utils.data_storage_manager import DataStorageManager
from utils.helpers import get_random_user_agent, parse_weibo_time

logger = logging.getLogger(__name__)

class WeiboSpider:
    """微博爬虫类"""
    
    def __init__(self, storage_manager: DataStorageManager = None):
        self.session = requests.Session()
        self.data_processor = DataProcessor()
        self.storage_manager = storage_manager
        self.crawled_ids = set()
        
        # 设置请求头
        self.session.headers.update({
            'User-Agent': get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # 设置代理（如果启用）
        if PROXY_CONFIG['enabled'] and PROXY_CONFIG['proxies']:
            proxy = random.choice(PROXY_CONFIG['proxies'])
            self.session.proxies = {'http': proxy, 'https': proxy}
        
        # 配置Cookie
        if COOKIE_CONFIG['enabled']:
            # 设置PC端Cookie
            for name, value in COOKIE_CONFIG['weibo_cookies'].items():
                if value:  # 只设置非空Cookie
                    self.session.cookies.set(name, value, domain='.weibo.com')
            
            # 添加Cookie验证日志
            cookie_count = len([v for v in COOKIE_CONFIG['weibo_cookies'].values() if v])
            logger.info(f"[Cookie] 已配置 {cookie_count} 个Cookie")
            
            if cookie_count == 0:
                logger.warning("[Cookie] 未配置有效Cookie，可能影响爬取效果")
    
    def search_weibo(self, keyword: str, page: int = 1) -> List[Dict[str, Any]]:
        """搜索微博数据"""
        try:
            # 构建搜索URL
            params = {
                'q': keyword,
                'typeall': '1',
                'suball': '1',
                'timescope': '',
                'category': '4',
                'intpicture': '',
                'f': '1',
                'realip': '1',
                'topsug': '1',
                'sug': '1',
                'atten': '1',
                'Refer': 'g',
                'page': page
            }
            
            search_url = f"{WEIBO_URLS['search_url']}?{urlencode(params)}"
            
            # 发送请求
            response = self.session.get(
                search_url,
                timeout=CRAWLER_CONFIG['timeout'],
                headers={'User-Agent': get_random_user_agent()}
            )
            
            if response.status_code == 200:
                # 添加调试日志：记录响应信息
                logger.info(f"[调试] 搜索请求成功，状态码: {response.status_code}")
                logger.info(f"[调试] 响应头: {dict(response.headers)}")
                logger.info(f"[调试] 响应内容长度: {len(response.text)} 字符")
                logger.info(f"[调试] 响应内容前500字符: {response.text[:500]}")
                
                # 检查是否被重定向到登录页面
                if 'login' in response.url.lower() or '登录' in response.text:
                    logger.warning("[调试] 检测到被重定向到登录页面")
                
                # 检查是否包含反爬虫提示
                if '验证码' in response.text or 'captcha' in response.text.lower():
                    logger.warning("[调试] 检测到验证码或反爬虫机制")
                
                # 解析搜索结果
                weibo_list = self._parse_search_results(response.text, keyword)
                
                # 保存原始数据
                if self.storage_manager and weibo_list:
                    self.storage_manager.save_raw_data(weibo_list, page, "weibo_web", "weibo")
                
                return weibo_list
            else:
                logger.warning(f"搜索请求失败，状态码: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"搜索微博失败: {e}")
            return []
    
    def search_weibo_mobile(self, keyword: str, page: int = 1) -> List[Dict[str, Any]]:
        """使用移动端API搜索微博"""
        try:
            # 移动端搜索参数
            params = {
                'containerid': f'100103type=1&q={quote(keyword)}',
                'page_type': 'searchall',
                'page': page
            }
            
            mobile_url = f"{WEIBO_URLS['mobile_search_url']}?{urlencode(params)}"
            
            # 设置移动端请求头
            mobile_headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
                'Accept': 'application/json, text/plain, */*',
                'Referer': 'https://m.weibo.cn/',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            response = self.session.get(
                mobile_url,
                headers=mobile_headers,
                timeout=CRAWLER_CONFIG['timeout']
            )
            
            if response.status_code == 200:
                # 添加调试日志：记录移动端响应信息
                logger.info(f"[调试] 移动端搜索请求成功，状态码: {response.status_code}")
                logger.info(f"[调试] 移动端响应头: {dict(response.headers)}")
                
                try:
                    json_data = response.json()
                    logger.info(f"[调试] JSON响应结构: {list(json_data.keys()) if isinstance(json_data, dict) else type(json_data)}")
                    
                    if isinstance(json_data, dict) and 'data' in json_data:
                        data = json_data['data']
                        logger.info(f"[调试] data字段结构: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                        
                        if isinstance(data, dict) and 'cards' in data:
                            cards = data['cards']
                            logger.info(f"[调试] 找到 {len(cards)} 个cards")
                            for i, card in enumerate(cards[:3]):  # 只记录前3个card的信息
                                logger.info(f"[调试] Card {i}: type={card.get('card_type')}, keys={list(card.keys())}")
                    
                    # 解析移动端结果
                    weibo_list = self._parse_mobile_results(json_data, keyword)
                    
                    # 保存原始数据
                    if self.storage_manager and weibo_list:
                        self.storage_manager.save_raw_data(weibo_list, page, "weibo_mobile", "weibo")
                    
                    return weibo_list
                except json.JSONDecodeError as e:
                    logger.error(f"[调试] JSON解析失败: {e}")
                    logger.info(f"[调试] 原始响应内容: {response.text[:500]}")
                    return []
            else:
                logger.warning(f"移动端搜索失败，状态码: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"移动端搜索失败: {e}")
            return []
    
    def _parse_search_results(self, html: str, keyword: str) -> List[Dict[str, Any]]:
        """解析搜索结果页面"""
        weibo_list = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # 添加调试日志：检查页面结构
            logger.info(f"[调试] 开始解析HTML，长度: {len(html)} 字符")
            
            # 检查页面标题
            title = soup.find('title')
            if title:
                logger.info(f"[调试] 页面标题: {title.get_text()}")
            
            # 查找微博卡片
            cards = soup.find_all('div', class_='card-wrap')
            logger.info(f"[调试] 找到 {len(cards)} 个card-wrap元素")
            
            # 如果没有找到card-wrap，尝试其他可能的选择器
            if not cards:
                logger.info("[调试] 未找到card-wrap，尝试其他选择器...")
                
                # 尝试其他可能的微博容器选择器
                alternative_selectors = [
                    'div[class*="card"]',
                    'div[class*="weibo"]',
                    'div[class*="feed"]',
                    'div[class*="content"]',
                    '.m-con-box',
                    '.WB_feed',
                    '.WB_cardwrap'
                ]
                
                for selector in alternative_selectors:
                    elements = soup.select(selector)
                    if elements:
                        logger.info(f"[调试] 使用选择器 '{selector}' 找到 {len(elements)} 个元素")
                        break
                else:
                    logger.warning("[调试] 所有选择器都未找到匹配元素")
                    
                    # 记录页面的主要结构
                    body = soup.find('body')
                    if body:
                        main_divs = body.find_all('div', limit=10)
                        logger.info(f"[调试] 页面主要div元素的class属性:")
                        for i, div in enumerate(main_divs):
                            class_attr = div.get('class', [])
                            logger.info(f"[调试] Div {i}: class={class_attr}")
            
            for card in cards:
                try:
                    weibo_data = self._extract_weibo_from_card(card, keyword)
                    if weibo_data and weibo_data['_id'] not in self.crawled_ids:
                        weibo_list.append(weibo_data)
                        self.crawled_ids.add(weibo_data['_id'])
                except Exception as e:
                    logger.warning(f"解析微博卡片失败: {e}")
                    continue
            
            logger.info(f"解析到 {len(weibo_list)} 条微博数据")
            
        except Exception as e:
            logger.error(f"解析搜索结果失败: {e}")
        
        return weibo_list
    
    def _parse_mobile_results(self, json_data: dict, keyword: str) -> List[Dict[str, Any]]:
        """解析移动端API返回的JSON数据"""
        weibo_list = []
        
        try:
            if 'data' in json_data and 'cards' in json_data['data']:
                cards = json_data['data']['cards']
                
                for card in cards:
                    # 支持多种微博卡片类型：9 和 11
                    card_type = card.get('card_type')
                    if card_type in [9, 11]:  # 微博卡片类型
                        try:
                            logger.debug(f"[调试] 处理卡片类型: {card_type}")
                            weibo_data = self._extract_weibo_from_mobile_card(card, keyword)
                            if weibo_data and weibo_data['_id'] not in self.crawled_ids:
                                weibo_list.append(weibo_data)
                                self.crawled_ids.add(weibo_data['_id'])
                                logger.debug(f"[调试] 成功提取微博数据，ID: {weibo_data['_id']}")
                        except Exception as e:
                            logger.warning(f"解析移动端微博卡片失败 (card_type={card_type}): {e}")
                            continue
                    else:
                        logger.debug(f"[调试] 跳过卡片类型: {card_type}")
            
            logger.info(f"移动端解析到 {len(weibo_list)} 条微博数据")
            
        except Exception as e:
            logger.error(f"解析移动端结果失败: {e}")
        
        return weibo_list
    
    def _extract_weibo_from_card(self, card, keyword: str) -> Optional[Dict[str, Any]]:
        """从网页卡片中提取微博数据"""
        try:
            # 提取基本信息
            content_elem = card.find('p', class_='txt')
            if not content_elem:
                return None
            
            content = content_elem.get_text(strip=True)
            
            # 提取微博ID
            mid_elem = card.find('a', href=re.compile(r'/\d+/[A-Za-z0-9]+'))
            if not mid_elem:
                return None
            
            href = mid_elem.get('href', '')
            mid_match = re.search(r'/(\d+)/([A-Za-z0-9]+)', href)
            if not mid_match:
                return None
            
            user_id = mid_match.group(1)
            mblog_id = mid_match.group(2)
            
            # 提取用户信息
            user_elem = card.find('a', class_='name')
            user_name = user_elem.get_text(strip=True) if user_elem else ''
            
            # 提取时间
            time_elem = card.find('a', class_='time')
            created_at = parse_weibo_time(time_elem.get_text(strip=True)) if time_elem else datetime.now()
            
            # 提取互动数据
            action_elem = card.find('div', class_='card-act')
            reposts_count = 0
            comments_count = 0
            attitudes_count = 0
            
            if action_elem:
                action_links = action_elem.find_all('a')
                for link in action_links:
                    text = link.get_text(strip=True)
                    if '转发' in text:
                        reposts_count = self._extract_count(text)
                    elif '评论' in text:
                        comments_count = self._extract_count(text)
                    elif '赞' in text:
                        attitudes_count = self._extract_count(text)
            
            # 提取来源和图片
            source, pic_urls = self.data_processor.extract_source_and_pics(content)
            
            return {
                '_id': mblog_id,
                'mblogid': mblog_id,
                'created_at': created_at,
                'geo_type': None,
                'geo_coordinates': None,
                'geo_detail_poiid': None,
                'geo_detail_title': None,
                'geo_detail_type': None,
                'geo_detail_spot_type': None,
                'ip_location': None,
                'reposts_count': reposts_count,
                'comments_count': comments_count,
                'attitudes_count': attitudes_count,
                'source': source,
                'content': content,
                'pic_urls': json.dumps(pic_urls) if pic_urls else None,
                'pic_num': len(pic_urls) if pic_urls else 0,
                'isLongText': len(content) > 140,
                'user_id': user_id,
                'user_avatar_hd': None,
                'user_nick_name': user_name,
                'user_verified': False,
                'user_mbrank': 0,
                'user_mbtype': 0,
                'user_verified_type': -1,
                'url': f"https://weibo.com/{user_id}/{mblog_id}",
                'keyword': keyword
            }
            
        except Exception as e:
            logger.error(f"提取微博数据失败: {e}")
            return None
    
    def _extract_weibo_from_mobile_card(self, card: dict, keyword: str) -> Optional[Dict[str, Any]]:
        """从移动端API卡片中提取微博数据"""
        try:
            # 处理新的数据结构：微博数据可能在card_group中
            mblog = None
            
            # 首先检查顶级是否有mblog字段（兼容旧结构）
            if 'mblog' in card:
                mblog = card['mblog']
            # 如果没有，检查card_group中的子卡片
            elif 'card_group' in card:
                card_group = card.get('card_group', [])
                for sub_card in card_group:
                    if isinstance(sub_card, dict) and 'mblog' in sub_card:
                        mblog = sub_card['mblog']
                        break
            
            if not mblog:
                logger.debug(f"[调试] 卡片中未找到mblog数据，card_type={card.get('card_type')}")
                return None
            
            logger.debug(f"[调试] 成功找到mblog数据，mid={mblog.get('mid')}")
            
            # 基本信息
            mid = mblog.get('mid', '')
            content = mblog.get('text', '')
            created_at = parse_weibo_time(mblog.get('created_at', ''))
            
            # 用户信息
            user = mblog.get('user', {})
            user_id = str(user.get('id', ''))
            user_name = user.get('screen_name', '')
            user_avatar = user.get('avatar_hd', '')
            user_verified = user.get('verified', False)
            user_verified_type = user.get('verified_type', -1)
            
            # 互动数据
            reposts_count = mblog.get('reposts_count', 0)
            comments_count = mblog.get('comments_count', 0)
            attitudes_count = mblog.get('attitudes_count', 0)
            
            # 地理位置信息
            geo = mblog.get('geo')
            geo_type = None
            geo_coordinates = None
            geo_detail = {}
            
            if geo:
                geo_type = geo.get('type')
                geo_coordinates = json.dumps(geo.get('coordinates', []))
                geo_detail = geo.get('detail', {})
            
            # IP位置
            ip_location = mblog.get('region_name', '')
            
            # 来源
            source = mblog.get('source', '')
            
            # 图片信息
            pic_urls = []
            pic_infos = mblog.get('pic_infos', {})
            if pic_infos:
                pic_urls = [info.get('large', {}).get('url', '') for info in pic_infos.values()]
            
            return {
                '_id': mid,
                'mblogid': mid,
                'created_at': created_at,
                'geo_type': geo_type,
                'geo_coordinates': geo_coordinates,
                'geo_detail_poiid': geo_detail.get('poiid'),
                'geo_detail_title': geo_detail.get('title'),
                'geo_detail_type': geo_detail.get('type'),
                'geo_detail_spot_type': geo_detail.get('spot_type'),
                'ip_location': ip_location,
                'reposts_count': reposts_count,
                'comments_count': comments_count,
                'attitudes_count': attitudes_count,
                'source': source,
                'content': content,
                'pic_urls': json.dumps(pic_urls) if pic_urls else None,
                'pic_num': len(pic_urls),
                'isLongText': mblog.get('isLongText', False),
                'user_id': user_id,
                'user_avatar_hd': user_avatar,
                'user_nick_name': user_name,
                'user_verified': user_verified,
                'user_mbrank': user.get('mbrank', 0),
                'user_mbtype': user.get('mbtype', 0),
                'user_verified_type': user_verified_type,
                'url': f"https://weibo.com/{user_id}/{mid}",
                'keyword': keyword
            }
            
        except Exception as e:
            logger.error(f"提取移动端微博数据失败: {e}")
            return None
    
    def _extract_count(self, text: str) -> int:
        """从文本中提取数字"""
        try:
            # 提取数字
            numbers = re.findall(r'\d+', text)
            if numbers:
                return int(numbers[0])
            return 0
        except:
            return 0
    
    def crawl_with_retry(self, keyword: str, page: int = 1, use_mobile: bool = True) -> List[Dict[str, Any]]:
        """带重试机制的爬取"""
        for attempt in range(CRAWLER_CONFIG['retry_times']):
            try:
                if use_mobile:
                    results = self.search_weibo_mobile(keyword, page)
                else:
                    results = self.search_weibo(keyword, page)
                
                if results:
                    return results
                
                # 如果没有结果，尝试另一种方式
                if use_mobile:
                    results = self.search_weibo(keyword, page)
                else:
                    results = self.search_weibo_mobile(keyword, page)
                
                return results
                
            except Exception as e:
                logger.warning(f"第 {attempt + 1} 次尝试失败: {e}")
                if attempt < CRAWLER_CONFIG['retry_times'] - 1:
                    time.sleep(random.uniform(2, 5))
                    # 更换User-Agent
                    self.session.headers['User-Agent'] = get_random_user_agent()
        
        logger.error(f"爬取失败，已重试 {CRAWLER_CONFIG['retry_times']} 次")
        return []
    
    def random_delay(self):
        """随机延迟"""
        delay = random.uniform(*CRAWLER_CONFIG['delay_range'])
        logger.debug(f"等待 {delay:.2f} 秒")
        time.sleep(delay)