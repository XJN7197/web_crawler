"""
数据存储管理器模块
按时间戳组织数据存储，每次爬取创建独立的文件夹
"""
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

from utils.data_analyzer import WeiboDataAnalyzer, DecimalEncoder

logger = logging.getLogger(__name__)

class DataStorageManager:
    """数据存储管理器类"""
    
    def __init__(self, base_data_dir: str = "data"):
        self.base_data_dir = Path(base_data_dir)
        self.current_session_dir = None
        self.session_timestamp = None
        
        # 确保基础数据目录存在
        self.base_data_dir.mkdir(exist_ok=True)
    
    def create_session_directory(self, keyword: str = None) -> str:
        """创建新的爬取会话目录"""
        try:
            # 生成时间戳
            self.session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 创建会话目录名称
            if keyword:
                # 清理关键词中的特殊字符，用于文件夹名称
                clean_keyword = self._clean_filename(keyword)
                session_name = f"{self.session_timestamp}_{clean_keyword}"
            else:
                session_name = self.session_timestamp
            
            # 创建会话目录
            self.current_session_dir = self.base_data_dir / session_name
            self.current_session_dir.mkdir(exist_ok=True)
            
            # 创建子目录
            (self.current_session_dir / "raw_data").mkdir(exist_ok=True)
            (self.current_session_dir / "structured_data").mkdir(exist_ok=True)
            (self.current_session_dir / "analysis_report").mkdir(exist_ok=True)
            
            logger.info(f"创建爬取会话目录: {self.current_session_dir}")
            
            return str(self.current_session_dir)
            
        except Exception as e:
            logger.error(f"创建会话目录失败: {e}")
            return None
    
    def save_raw_data(self, data: List[Dict[str, Any]], page: int = None, data_type: str = "weibo") -> bool:
        """保存原始数据"""
        try:
            if not self.current_session_dir:
                logger.error("未创建会话目录，无法保存原始数据")
                return False
            
            # 生成文件名
            if page is not None:
                filename = f"{data_type}_raw_page_{page:03d}.json"
            else:
                timestamp = datetime.now().strftime("%H%M%S")
                filename = f"{data_type}_raw_{timestamp}.json"
            
            # 保存文件
            file_path = self.current_session_dir / "raw_data" / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, cls=DecimalEncoder)
            
            logger.info(f"保存原始数据: {file_path} ({len(data)} 条记录)")
            return True
            
        except Exception as e:
            logger.error(f"保存原始数据失败: {e}")
            return False
    
    def save_structured_data(self, data: List[Dict[str, Any]], filename: str = None) -> bool:
        """保存结构化数据"""
        try:
            if not self.current_session_dir:
                logger.error("未创建会话目录，无法保存结构化数据")
                return False
            
            # 生成文件名
            if not filename:
                filename = f"structured_data_{self.session_timestamp}.json"
            
            # 保存文件
            file_path = self.current_session_dir / "structured_data" / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, cls=DecimalEncoder)
            
            logger.info(f"保存结构化数据: {file_path} ({len(data)} 条记录)")
            return True
            
        except Exception as e:
            logger.error(f"保存结构化数据失败: {e}")
            return False
    
    def save_analysis_report(self, report: Dict[str, Any], db_manager=None, keyword: str = None) -> bool:
        """保存分析报告"""
        try:
            if not self.current_session_dir:
                logger.error("未创建会话目录，无法保存分析报告")
                return False
            
            # 如果没有提供报告，则生成报告
            if not report and db_manager:
                analyzer = WeiboDataAnalyzer(db_manager)
                report = analyzer.generate_summary_report(keyword or "默认关键词")
            
            if not report:
                logger.warning("没有分析报告数据可保存")
                return False
            
            # 生成文件名
            filename = f"analysis_report_{self.session_timestamp}.json"
            
            # 保存文件
            file_path = self.current_session_dir / "analysis_report" / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, cls=DecimalEncoder)
            
            logger.info(f"保存分析报告: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存分析报告失败: {e}")
            return False
    
    def save_session_metadata(self, metadata: Dict[str, Any]) -> bool:
        """保存会话元数据"""
        try:
            if not self.current_session_dir:
                logger.error("未创建会话目录，无法保存元数据")
                return False
            
            # 添加会话信息
            metadata.update({
                'session_id': self.session_timestamp,
                'session_dir': str(self.current_session_dir),
                'created_at': datetime.now().isoformat(),
                'data_structure': {
                    'raw_data': '原始爬取数据，按页面分文件存储',
                    'structured_data': '处理后的结构化数据',
                    'analysis_report': '数据分析报告'
                }
            })
            
            # 保存元数据文件
            file_path = self.current_session_dir / "session_metadata.json"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2, cls=DecimalEncoder)
            
            logger.info(f"保存会话元数据: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存会话元数据失败: {e}")
            return False
    
    def get_session_summary(self) -> Dict[str, Any]:
        """获取当前会话摘要"""
        if not self.current_session_dir or not self.current_session_dir.exists():
            return {}
        
        try:
            summary = {
                'session_id': self.session_timestamp,
                'session_dir': str(self.current_session_dir),
                'created_at': datetime.now().isoformat(),
                'files': {
                    'raw_data': [],
                    'structured_data': [],
                    'analysis_report': []
                }
            }
            
            # 统计各类文件
            for subdir in ['raw_data', 'structured_data', 'analysis_report']:
                subdir_path = self.current_session_dir / subdir
                if subdir_path.exists():
                    files = list(subdir_path.glob('*.json'))
                    summary['files'][subdir] = [f.name for f in files]
            
            return summary
            
        except Exception as e:
            logger.error(f"获取会话摘要失败: {e}")
            return {}
    
    def list_all_sessions(self) -> List[Dict[str, Any]]:
        """列出所有爬取会话"""
        sessions = []
        
        try:
            if not self.base_data_dir.exists():
                return sessions
            
            # 查找所有会话目录
            for item in self.base_data_dir.iterdir():
                if item.is_dir() and self._is_session_directory(item):
                    session_info = self._get_session_info(item)
                    if session_info:
                        sessions.append(session_info)
            
            # 按时间排序
            sessions.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            return sessions
            
        except Exception as e:
            logger.error(f"列出会话失败: {e}")
            return sessions
    
    def _clean_filename(self, filename: str) -> str:
        """清理文件名中的特殊字符"""
        # 移除或替换不适合文件名的字符
        import re
        cleaned = re.sub(r'[<>:"/\\|?*]', '_', filename)
        cleaned = re.sub(r'\s+', '_', cleaned)
        return cleaned[:50]  # 限制长度
    
    def _is_session_directory(self, path: Path) -> bool:
        """判断是否为会话目录"""
        # 检查目录名是否符合时间戳格式
        import re
        pattern = r'^\d{8}_\d{6}'
        return bool(re.match(pattern, path.name))
    
    def _get_session_info(self, session_dir: Path) -> Optional[Dict[str, Any]]:
        """获取会话信息"""
        try:
            # 尝试读取元数据文件
            metadata_file = session_dir / "session_metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # 如果没有元数据文件，生成基本信息
            return {
                'session_id': session_dir.name,
                'session_dir': str(session_dir),
                'created_at': datetime.fromtimestamp(session_dir.stat().st_ctime).isoformat(),
                'timestamp': session_dir.name.split('_')[0] + '_' + session_dir.name.split('_')[1] if '_' in session_dir.name else session_dir.name
            }
            
        except Exception as e:
            logger.warning(f"获取会话信息失败 {session_dir}: {e}")
            return None
    
    def cleanup_old_sessions(self, keep_days: int = 30) -> int:
        """清理旧的会话数据"""
        cleaned_count = 0
        
        try:
            cutoff_date = datetime.now() - timedelta(days=keep_days)
            
            for session_dir in self.base_data_dir.iterdir():
                if session_dir.is_dir() and self._is_session_directory(session_dir):
                    # 从目录名提取时间戳
                    try:
                        timestamp_str = session_dir.name.split('_')[0] + session_dir.name.split('_')[1]
                        session_date = datetime.strptime(timestamp_str, "%Y%m%d%H%M%S")
                        
                        if session_date < cutoff_date:
                            import shutil
                            shutil.rmtree(session_dir)
                            logger.info(f"清理旧会话: {session_dir}")
                            cleaned_count += 1
                            
                    except (ValueError, IndexError) as e:
                        logger.warning(f"解析会话时间戳失败 {session_dir}: {e}")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"清理旧会话失败: {e}")
            return cleaned_count