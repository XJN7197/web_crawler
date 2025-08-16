"""
数据处理工具模块
"""
import re
import json
import logging
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class DataProcessor:
    """数据处理类"""
    
    def __init__(self):
        # 来源匹配模式
        self.source_patterns = [
            r'来自\s*([^<>\n]+)',
            r'via\s+([^<>\n]+)',
            r'source:\s*([^<>\n]+)',
            r'发布于\s*([^<>\n]+)'
        ]
        
        # 图片URL匹配模式
        self.pic_url_patterns = [
            r'https?://[^\s<>"]+\.(?:jpg|jpeg|png|gif|webp|bmp)',
            r'https?://wx\d+\.sinaimg\.cn/[^\s<>"]+',
            r'https?://tva\d+\.sinaimg\.cn/[^\s<>"]+',
            r'https?://ww\d+\.sinaimg\.cn/[^\s<>"]+'
        ]
    
    def extract_source_and_pics(self, content: str) -> Tuple[Optional[str], List[str]]:
        """从微博正文中提取来源和图片URL"""
        source = self._extract_source(content)
        pic_urls = self._extract_pic_urls(content)
        
        return source, pic_urls
    
    def _extract_source(self, content: str) -> Optional[str]:
        """提取来源信息"""
        try:
            for pattern in self.source_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    source = match.group(1).strip()
                    # 清理HTML标签
                    source = re.sub(r'<[^>]+>', '', source)
                    return source
            
            # 如果没有明确的来源标识，尝试提取可能的客户端信息
            client_match = re.search(r'(iPhone|Android|iPad|微博网页版|微博桌面版)', content)
            if client_match:
                return client_match.group(1)
            
            return None
            
        except Exception as e:
            logger.warning(f"提取来源失败: {e}")
            return None
    
    def _extract_pic_urls(self, content: str) -> List[str]:
        """提取图片URL"""
        pic_urls = []
        
        try:
            for pattern in self.pic_url_patterns:
                matches = re.findall(pattern, content)
                pic_urls.extend(matches)
            
            # 去重并验证URL
            unique_urls = []
            for url in pic_urls:
                if url not in unique_urls and self._is_valid_image_url(url):
                    unique_urls.append(url)
            
            return unique_urls
            
        except Exception as e:
            logger.warning(f"提取图片URL失败: {e}")
            return []
    
    def _is_valid_image_url(self, url: str) -> bool:
        """验证图片URL是否有效"""
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # 检查文件扩展名
            path = parsed.path.lower()
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
            
            return any(path.endswith(ext) for ext in valid_extensions)
            
        except Exception:
            return False
    
    def clean_content(self, content: str) -> str:
        """清理微博内容"""
        if not content:
            return ""
        
        try:
            # 移除HTML标签
            content = re.sub(r'<[^>]+>', '', content)
            
            # 移除多余的空白字符
            content = re.sub(r'\s+', ' ', content)
            
            # 移除特殊字符
            content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', content)
            
            return content.strip()
            
        except Exception as e:
            logger.warning(f"清理内容失败: {e}")
            return content
    
    def extract_hashtags(self, content: str) -> List[str]:
        """提取话题标签"""
        try:
            hashtags = re.findall(r'#([^#]+)#', content)
            return [tag.strip() for tag in hashtags if tag.strip()]
        except Exception as e:
            logger.warning(f"提取话题标签失败: {e}")
            return []
    
    def extract_mentions(self, content: str) -> List[str]:
        """提取@用户"""
        try:
            mentions = re.findall(r'@([^\s@]+)', content)
            return [mention.strip() for mention in mentions if mention.strip()]
        except Exception as e:
            logger.warning(f"提取@用户失败: {e}")
            return []
    
    def extract_urls(self, content: str) -> List[str]:
        """提取URL链接"""
        try:
            url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
            urls = re.findall(url_pattern, content)
            return [url.strip() for url in urls if url.strip()]
        except Exception as e:
            logger.warning(f"提取URL失败: {e}")
            return []
    
    def process_geo_data(self, geo_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理地理位置数据"""
        processed = {
            'geo_type': None,
            'geo_coordinates': None,
            'geo_detail_poiid': None,
            'geo_detail_title': None,
            'geo_detail_type': None,
            'geo_detail_spot_type': None
        }
        
        try:
            if not geo_data:
                return processed
            
            processed['geo_type'] = geo_data.get('type')
            
            coordinates = geo_data.get('coordinates')
            if coordinates:
                processed['geo_coordinates'] = json.dumps(coordinates)
            
            detail = geo_data.get('detail', {})
            if detail:
                processed['geo_detail_poiid'] = detail.get('poiid')
                processed['geo_detail_title'] = detail.get('title')
                processed['geo_detail_type'] = detail.get('type')
                processed['geo_detail_spot_type'] = detail.get('spot_type')
            
            return processed
            
        except Exception as e:
            logger.warning(f"处理地理位置数据失败: {e}")
            return processed
    
    def validate_weibo_data(self, data: Dict[str, Any]) -> bool:
        """验证微博数据完整性"""
        required_fields = ['_id', 'content', 'keyword']
        
        try:
            for field in required_fields:
                if field not in data or not data[field]:
                    logger.warning(f"缺少必要字段: {field}")
                    return False
            
            # 验证数据类型
            if not isinstance(data.get('reposts_count', 0), int):
                data['reposts_count'] = 0
            
            if not isinstance(data.get('comments_count', 0), int):
                data['comments_count'] = 0
            
            if not isinstance(data.get('attitudes_count', 0), int):
                data['attitudes_count'] = 0
            
            if not isinstance(data.get('pic_num', 0), int):
                data['pic_num'] = 0
            
            # 验证时间格式
            if data.get('created_at') and not isinstance(data['created_at'], datetime):
                logger.warning("创建时间格式不正确")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"验证数据失败: {e}")
            return False
    
    def normalize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """标准化数据格式"""
        try:
            # 清理内容
            if data.get('content'):
                data['content'] = self.clean_content(data['content'])
            
            # 标准化用户名
            if data.get('user_nick_name'):
                data['user_nick_name'] = data['user_nick_name'].strip()
            
            # 标准化来源
            if data.get('source'):
                data['source'] = data['source'].strip()
            
            # 确保数值字段为整数
            numeric_fields = ['reposts_count', 'comments_count', 'attitudes_count', 'pic_num']
            for field in numeric_fields:
                if field in data:
                    try:
                        data[field] = int(data[field]) if data[field] is not None else 0
                    except (ValueError, TypeError):
                        data[field] = 0
            
            # 确保布尔字段
            boolean_fields = ['isLongText', 'user_verified']
            for field in boolean_fields:
                if field in data:
                    data[field] = bool(data[field]) if data[field] is not None else False
            
            return data
            
        except Exception as e:
            logger.error(f"标准化数据失败: {e}")
            return data
    
    def deduplicate_data(self, data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """数据去重"""
        seen_ids = set()
        unique_data = []
        
        for data in data_list:
            weibo_id = data.get('_id')
            if weibo_id and weibo_id not in seen_ids:
                seen_ids.add(weibo_id)
                unique_data.append(data)
        
        logger.info(f"去重前: {len(data_list)} 条，去重后: {len(unique_data)} 条")
        return unique_data