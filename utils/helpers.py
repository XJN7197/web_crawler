"""
辅助工具函数
"""
import random
import re
import logging
from datetime import datetime, timedelta
from typing import Optional
from config.settings import USER_AGENTS

logger = logging.getLogger(__name__)

def get_random_user_agent() -> str:
    """获取随机User-Agent"""
    return random.choice(USER_AGENTS)

def parse_weibo_time(time_str: str) -> Optional[datetime]:
    """解析微博时间字符串"""
    if not time_str:
        return None
    
    try:
        # 清理时间字符串
        time_str = time_str.strip()
        
        # 处理相对时间
        if '秒前' in time_str:
            seconds = int(re.search(r'(\d+)', time_str).group(1))
            return datetime.now() - timedelta(seconds=seconds)
        
        elif '分钟前' in time_str:
            minutes = int(re.search(r'(\d+)', time_str).group(1))
            return datetime.now() - timedelta(minutes=minutes)
        
        elif '小时前' in time_str:
            hours = int(re.search(r'(\d+)', time_str).group(1))
            return datetime.now() - timedelta(hours=hours)
        
        elif '天前' in time_str:
            days = int(re.search(r'(\d+)', time_str).group(1))
            return datetime.now() - timedelta(days=days)
        
        elif '今天' in time_str:
            # 提取时间部分
            time_match = re.search(r'(\d{1,2}):(\d{2})', time_str)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2))
                today = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
                return today
        
        elif '昨天' in time_str:
            time_match = re.search(r'(\d{1,2}):(\d{2})', time_str)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2))
                yesterday = datetime.now() - timedelta(days=1)
                yesterday = yesterday.replace(hour=hour, minute=minute, second=0, microsecond=0)
                return yesterday
        
        # 处理绝对时间格式
        time_formats = [
            '%a %b %d %H:%M:%S %z %Y',  # RFC 2822格式: Mon Mar 01 01:27:11 +0800 2021
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d',
            '%m-%d %H:%M',
            '%m月%d日 %H:%M',
            '%m月%d日',
            '%Y年%m月%d日 %H:%M:%S',
            '%Y年%m月%d日 %H:%M',
            '%Y年%m月%d日'
        ]
        
        for fmt in time_formats:
            try:
                parsed_time = datetime.strptime(time_str, fmt)
                # 如果没有年份，使用当前年份
                if parsed_time.year == 1900:
                    parsed_time = parsed_time.replace(year=datetime.now().year)
                return parsed_time
            except ValueError:
                continue
        
        # 如果都无法解析，返回当前时间
        logger.warning(f"无法解析时间字符串: {time_str}")
        return datetime.now()
        
    except Exception as e:
        logger.error(f"解析时间失败: {e}")
        return datetime.now()

def format_number(num_str: str) -> int:
    """格式化数字字符串（处理万、千等单位）"""
    if not num_str:
        return 0
    
    try:
        # 移除非数字和单位字符以外的内容
        num_str = re.sub(r'[^\d万千百十kKwW.]', '', str(num_str))
        
        if not num_str:
            return 0
        
        # 处理万单位
        if '万' in num_str or 'w' in num_str.lower():
            num_part = re.sub(r'[万wW]', '', num_str)
            try:
                return int(float(num_part) * 10000)
            except ValueError:
                return 0
        
        # 处理千单位
        elif '千' in num_str or 'k' in num_str.lower():
            num_part = re.sub(r'[千kK]', '', num_str)
            try:
                return int(float(num_part) * 1000)
            except ValueError:
                return 0
        
        # 处理百单位
        elif '百' in num_str:
            num_part = re.sub(r'百', '', num_str)
            try:
                return int(float(num_part) * 100)
            except ValueError:
                return 0
        
        # 处理十单位
        elif '十' in num_str:
            num_part = re.sub(r'十', '', num_str)
            try:
                return int(float(num_part) * 10)
            except ValueError:
                return 0
        
        # 直接转换数字
        else:
            try:
                return int(float(num_str))
            except ValueError:
                return 0
                
    except Exception as e:
        logger.warning(f"格式化数字失败: {num_str}, {e}")
        return 0

def clean_text(text: str) -> str:
    """清理文本内容"""
    if not text:
        return ""
    
    try:
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        
        # 移除控制字符
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        
        return text.strip()
        
    except Exception as e:
        logger.warning(f"清理文本失败: {e}")
        return text

def is_valid_weibo_id(weibo_id: str) -> bool:
    """验证微博ID格式"""
    if not weibo_id:
        return False
    
    # 微博ID通常是字母数字组合，长度在10-20之间
    pattern = r'^[A-Za-z0-9]{10,20}$'
    return bool(re.match(pattern, weibo_id))

def extract_domain(url: str) -> Optional[str]:
    """从URL中提取域名"""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return None

def safe_int(value, default=0) -> int:
    """安全转换为整数"""
    try:
        if value is None:
            return default
        return int(float(str(value)))
    except (ValueError, TypeError):
        return default

def safe_bool(value, default=False) -> bool:
    """安全转换为布尔值"""
    try:
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return bool(value)
    except (ValueError, TypeError):
        return default

def truncate_text(text: str, max_length: int = 1000) -> str:
    """截断文本到指定长度"""
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."

def validate_url(url: str) -> bool:
    """验证URL格式"""
    if not url:
        return False
    
    try:
        from urllib.parse import urlparse
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    try:
        return filename.split('.')[-1].lower() if '.' in filename else ''
    except Exception:
        return ''

def create_safe_filename(text: str, max_length: int = 50) -> str:
    """创建安全的文件名"""
    if not text:
        return "untitled"
    
    # 移除或替换不安全字符
    safe_text = re.sub(r'[<>:"/\\|?*]', '_', text)
    safe_text = re.sub(r'\s+', '_', safe_text)
    
    # 截断长度
    if len(safe_text) > max_length:
        safe_text = safe_text[:max_length]
    
    return safe_text or "untitled"

def calculate_time_diff(start_time: datetime, end_time: datetime = None) -> str:
    """计算时间差并格式化显示"""
    if end_time is None:
        end_time = datetime.now()
    
    try:
        diff = end_time - start_time
        
        if diff.days > 0:
            return f"{diff.days}天{diff.seconds//3600}小时"
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            minutes = (diff.seconds % 3600) // 60
            return f"{hours}小时{minutes}分钟"
        elif diff.seconds >= 60:
            minutes = diff.seconds // 60
            seconds = diff.seconds % 60
            return f"{minutes}分钟{seconds}秒"
        else:
            return f"{diff.seconds}秒"
            
    except Exception as e:
        logger.warning(f"计算时间差失败: {e}")
        return "未知"

def format_file_size(size_bytes: int) -> str:
    """格式化文件大小显示"""
    try:
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f}{size_names[i]}"
        
    except Exception:
        return "未知大小"