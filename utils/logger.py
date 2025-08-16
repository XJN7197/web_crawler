"""
日志配置模块
"""
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from config.settings import LOG_CONFIG

def setup_logger(name: str = 'weibo_crawler') -> logging.Logger:
    """设置日志记录器"""
    
    # 创建日志目录
    log_dir = os.path.dirname(LOG_CONFIG['file_path'])
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 创建logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_CONFIG['level']))
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    # 创建formatter
    formatter = logging.Formatter(LOG_CONFIG['format'])
    
    # 文件handler（带轮转）
    file_handler = RotatingFileHandler(
        LOG_CONFIG['file_path'],
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # 控制台handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # 添加handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def log_crawler_start(logger: logging.Logger, keyword: str):
    """记录爬虫开始"""
    logger.info("="*50)
    logger.info(f"开始爬取微博数据 - 关键词: {keyword}")
    logger.info(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*50)

def log_crawler_end(logger: logging.Logger, stats: dict):
    """记录爬虫结束"""
    logger.info("="*50)
    logger.info("爬取任务完成")
    logger.info(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"总爬取数量: {stats.get('total_crawled', 0)}")
    logger.info(f"成功保存: {stats.get('success_count', 0)}")
    logger.info(f"失败数量: {stats.get('error_count', 0)}")
    logger.info(f"耗时: {stats.get('duration', '未知')}")
    logger.info("="*50)

def log_page_result(logger: logging.Logger, page: int, count: int):
    """记录页面爬取结果"""
    logger.info(f"第 {page} 页爬取完成，获得 {count} 条数据")

def log_error_with_context(logger: logging.Logger, error: Exception, context: str = ""):
    """记录带上下文的错误"""
    if context:
        logger.error(f"[{context}] 发生错误: {str(error)}")
    else:
        logger.error(f"发生错误: {str(error)}")
    
    # 记录详细的异常信息到DEBUG级别
    logger.debug("详细错误信息:", exc_info=True)