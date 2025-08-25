"""
抖音爬虫核心模块
"""
import requests
import json
import time
import random
import re
import logging
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode, quote

from config.settings import (
    DOUYIN_API_CONFIG, DOUYIN_URLS, DOUYIN_COOKIE_CONFIG, 
    CRAWLER_CONFIG, USER_AGENTS, PROXY_CONFIG
)
from crawler.base_spider import BaseSpider
from utils.data_processor import DataProcessor
from utils.helpers import get_random_user_agent, parse_weibo_time

logger = logging.getLogger(__name__)

class DouyinSpider(BaseSpider):
    """抖音爬虫类"""
    
    def __init__(self, storage_manager=None):
        super().__init__(storage_manager)
        self.data_processor = DataProcessor()
        
        # 设置抖音移动端请求头 - 避免复杂Cookie认证
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',  # 移除br压缩避免解析问题
            'Referer': 'https://m.douyin.com/',
            'Origin': 'https://m.douyin.com',
            'X-Requested-With': 'XMLHttpRequest',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Connection': 'keep-alive',
        })
        
        # 初始化会话配置
        self.setup_session()
    
    def get_platform_name(self) -> str:
        """获取平台名称"""
        return "Douyin"
    
    def get_platform_config(self) -> Dict[str, Any]:
        """获取平台配置"""
        return {
            'api_config': DOUYIN_API_CONFIG,
            'urls': DOUYIN_URLS,
            'cookie_config': DOUYIN_COOKIE_CONFIG,
            'proxy_config': PROXY_CONFIG
        }
    
    def _get_cookie_domain(self) -> str:
        """获取Cookie域名"""
        return ".douyin.com"
    
    def search_content(self, keyword: str, page: int = 1) -> List[Dict[str, Any]]:
        """搜索抖音内容"""
        try:
            # 构建搜索参数
            params = self._build_search_params(keyword, page)
            
            # 优先尝试移动端API接口
            mobile_url = DOUYIN_URLS.get('search_url_mobile', DOUYIN_URLS['search_url'])
            
            logger.info(f"尝试移动端API: {mobile_url}")
            
            # 发送搜索请求
            response = self.session.get(
                mobile_url,
                params=params,
                timeout=CRAWLER_CONFIG['timeout']
            )
            
            # 如果移动端失败，尝试PC端备用接口
            if not self.validate_response(response):
                logger.warning("移动端API失败，尝试PC端备用接口")
                backup_url = DOUYIN_URLS.get('search_url_backup', DOUYIN_URLS['search_url'])
                response = self.session.get(
                    backup_url,
                    params=params,
                    timeout=CRAWLER_CONFIG['timeout']
                )
            
            # 验证响应并尝试解析
            if self.validate_response(response):
                logger.info(f"API响应成功，状态码: {response.status_code}")
                
                # 解析搜索结果
                content_list = self._parse_search_response(response.text, keyword)
                
                if content_list:
                    logger.info(f"✅ 成功获取到 {len(content_list)} 条真实抖音数据")
                    # 保存原始数据
                    self.save_raw_data(content_list, page)
                    return content_list
                else:
                    logger.warning("响应成功但未解析到有效数据")
            else:
                logger.warning(f"API响应验证失败，状态码: {response.status_code}")
            
            # 如果真实API失败，返回空列表
            logger.warning("未能获取到真实抖音数据，返回空列表")
            return []
            
        except Exception as e:
            logger.error(f"搜索抖音内容失败: {e}")
            # 发生异常时返回空列表
            return []
    
    def _build_search_params(self, keyword: str, page: int = 1) -> Dict[str, Any]:
        """构建移动端搜索参数 - 简化参数避免复杂认证"""
        # 移动端基础参数（更简化）
        params = {
            # 核心搜索参数
            'keyword': keyword,
            'offset': (page - 1) * 20,
            'count': 20,
            
            # 移动端设备参数
            'device_platform': 'webapp',
            'aid': '6383',  # 移动端aid
            'channel': 'channel_pc_web',
            'search_source': 'normal_search',
            'query_correct_type': '1',
            'is_filter_search': '0',
            'sort_type': '0',  # 综合排序
            'publish_time': '0',  # 不限时间
            
            # 简化的版本信息
            'version_code': '160100',
            'version_name': '16.1.0',
            
            # 移动端特有参数
            'screen_width': '375',
            'screen_height': '812',
            'dpr': '2',
            
            # 时间戳
            'ts': int(time.time()),
            'ms_token': self._generate_ms_token(),
        }
        
        # 移动端不需要复杂签名，使用简化版本
        params['verifyFp'] = self._generate_verify_fp()
        
        return params
    
    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """生成请求签名（简化版本）"""
        # 这里是一个简化的签名生成，实际应用中需要更复杂的算法
        sorted_params = sorted(params.items())
        param_str = '&'.join([f"{k}={v}" for k, v in sorted_params])
        return hashlib.md5(param_str.encode()).hexdigest()[:16]
    
    def _generate_ms_token(self) -> str:
        """生成移动端ms_token（简化版本）"""
        # 移动端ms_token生成算法（简化版本）
        timestamp = str(int(time.time() * 1000))
        random_str = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=16))
        token_base = f"{timestamp}_{random_str}"
        return hashlib.md5(token_base.encode()).hexdigest()
    
    def _generate_verify_fp(self) -> str:
        """生成移动端verifyFp（设备指纹）"""
        # 生成设备指纹（简化版本）
        device_info = f"mobile_{int(time.time())}"
        return hashlib.md5(device_info.encode()).hexdigest()[:16]

    def _parse_search_response(self, response_text: str, keyword: str) -> List[Dict[str, Any]]:
        """解析搜索响应"""
        content_list = []
        
        try:
            # 尝试解析JSON响应
            if response_text.startswith('{'):
                json_data = json.loads(response_text)
                
                # 检查响应状态
                if json_data.get('status_code') != 0:
                    logger.warning(f"API响应错误: {json_data.get('status_msg', '未知错误')}")
                    return []
                
                # 提取视频数据
                data = json_data.get('data', [])
                for item in data:
                    if isinstance(item, dict) and 'aweme_info' in item:
                        aweme_info = item['aweme_info']
                        parsed_item = self.parse_content_item(aweme_info, keyword)
                        if parsed_item and parsed_item['_id'] not in self.crawled_ids:
                            content_list.append(parsed_item)
                            self.crawled_ids.add(parsed_item['_id'])
            
            else:
                # 如果不是JSON，尝试从HTML中提取数据
                content_list = self._parse_html_response(response_text, keyword)
            
            logger.info(f"解析到 {len(content_list)} 条抖音内容")
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            # 尝试HTML解析
            content_list = self._parse_html_response(response_text, keyword)
        except Exception as e:
            logger.error(f"解析搜索响应失败: {e}")
        
        return content_list
    
    def _parse_html_response(self, html: str, keyword: str) -> List[Dict[str, Any]]:
        """解析HTML响应（备用方案）"""
        content_list = []
        
        try:
            # 更新正则表达式匹配抖音最新数据格式
            json_pattern = r'<script id="RENDER_DATA" type="application/json">(.*?)</script>'
            match = re.search(json_pattern, html)
            
            if match:
                json_str = unquote(match.group(1))  # 处理URL编码
                json_data = json.loads(json_str)
                
                # 更新视频数据提取逻辑
                videos = self._extract_videos_from_json(json_data)
                
                for video_data in videos:
                    parsed_item = self.parse_content_item(video_data, keyword)
                    if parsed_item and parsed_item['_id'] not in self.crawled_ids:
                        content_list.append(parsed_item)
                        self.crawled_ids.add(parsed_item['_id'])
            
            logger.info(f"从HTML解析到 {len(content_list)} 条抖音内容")
            
        except Exception as e:
            logger.error(f"HTML解析失败: {e}")
        
        return content_list

    def _extract_videos_from_json(self, data: Any) -> List[Dict[str, Any]]:
        """递归提取JSON中的视频数据"""
        videos = []
        
        if isinstance(data, dict):
            # 检查是否是视频数据
            if 'aweme_id' in data and 'desc' in data:
                videos.append(data)
            else:
                # 递归搜索
                for value in data.values():
                    videos.extend(self._extract_videos_from_json(value))
        
        elif isinstance(data, list):
            for item in data:
                videos.extend(self._extract_videos_from_json(item))
        
        return videos

    def parse_content_item(self, item_data: Dict[str, Any], keyword: str) -> Optional[Dict[str, Any]]:
        """解析单个抖音视频数据"""
        try:
            # 基本信息
            aweme_id = item_data.get('aweme_id', '')
            desc = item_data.get('desc', '')
            create_time = item_data.get('create_time', 0)
            
            if not aweme_id or not desc:
                return None
            
            # 用户信息
            author = item_data.get('author', {})
            user_id = author.get('uid', '')
            user_name = author.get('nickname', '')
            user_avatar = author.get('avatar_thumb', {}).get('url_list', [''])[0]
            user_verified = author.get('verification_type', 0) > 0
            
            # 统计信息
            statistics = item_data.get('statistics', {})
            digg_count = statistics.get('digg_count', 0)  # 点赞数
            comment_count = statistics.get('comment_count', 0)  # 评论数
            share_count = statistics.get('share_count', 0)  # 分享数
            play_count = statistics.get('play_count', 0)  # 播放数
            
            # 视频信息
            video = item_data.get('video', {})
            video_url = ''
            video_cover = ''
            video_duration = 0
            
            if video:
                play_addr = video.get('play_addr', {})
                if play_addr and 'url_list' in play_addr:
                    video_url = play_addr['url_list'][0] if play_addr['url_list'] else ''
                
                cover = video.get('cover', {})
                if cover and 'url_list' in cover:
                    video_cover = cover['url_list'][0] if cover['url_list'] else ''
                
                video_duration = video.get('duration', 0) / 1000  # 转换为秒
            
            # 音乐信息
            music = item_data.get('music', {})
            music_title = music.get('title', '') if music else ''
            music_author = music.get('author', '') if music else ''
            
            # 地理位置信息
            poi_info = item_data.get('poi_info')
            location = poi_info.get('poi_name', '') if poi_info else ''
            
            # 话题标签
            text_extra = item_data.get('text_extra', [])
            hashtags = []
            for extra in text_extra:
                if extra.get('type') == 1:  # 话题类型
                    hashtags.append(extra.get('hashtag_name', ''))
            
            return {
                '_id': aweme_id,
                'aweme_id': aweme_id,
                'created_at': datetime.fromtimestamp(create_time) if create_time else datetime.now(),
                'content': desc,
                'video_url': video_url,
                'video_cover': video_cover,
                'video_duration': video_duration,
                'music_title': music_title,
                'music_author': music_author,
                'location': location,
                'hashtags': json.dumps(hashtags) if hashtags else None,
                'digg_count': digg_count,
                'comment_count': comment_count,
                'share_count': share_count,
                'play_count': play_count,
                'user_id': user_id,
                'user_name': user_name,
                'user_avatar': user_avatar,
                'user_verified': user_verified,
                'url': f"https://www.douyin.com/video/{aweme_id}",
                'keyword': keyword,
                'platform': 'douyin'
            }
            
        except Exception as e:
            logger.error(f"解析抖音视频数据失败: {e}")
            return None