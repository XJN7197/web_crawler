"""
微博爬虫主程序
"""
import os
import sys
import time
import signal
from datetime import datetime
from typing import Dict, Any

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import CRAWLER_CONFIG
from database.models import DatabaseManager
from crawler.weibo_spider import WeiboSpider
from utils.data_storage_manager import DataStorageManager
from utils.data_analyzer import WeiboDataAnalyzer
from utils.logger import setup_logger, log_crawler_start, log_crawler_end, log_page_result
from utils.helpers import calculate_time_diff

class WeiboDataCrawler:
    """微博数据爬虫主类"""
    
    def __init__(self):
        self.logger = setup_logger()
        self.db_manager = DatabaseManager()
        self.storage_manager = DataStorageManager()
        self.spider = WeiboSpider(self.storage_manager)
        self.is_running = True
        
        # 统计信息
        self.stats = {
            'total_crawled': 0,
            'success_count': 0,
            'error_count': 0,
            'start_time': None,
            'end_time': None
        }
        
        # 注册信号处理器
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理器，用于优雅退出"""
        self.logger.info("接收到退出信号，正在安全退出...")
        self.is_running = False
    
    def initialize(self) -> bool:
        """初始化系统"""
        self.logger.info("正在初始化微博爬虫系统...")
        
        try:
            # 创建数据库
            if not self.db_manager.create_database():
                self.logger.error("创建数据库失败")
                return False
            
            # 连接数据库
            if not self.db_manager.connect():
                self.logger.error("连接数据库失败")
                return False
            
            # 创建数据表
            if not self.db_manager.create_tables():
                self.logger.error("创建数据表失败")
                return False
            
            self.logger.info("系统初始化完成")
            return True
            
        except Exception as e:
            self.logger.error(f"初始化失败: {e}")
            return False
    
    def crawl_weibo_data(self, keyword: str = None, max_pages: int = None) -> bool:
        """爬取微博数据"""
        if not keyword:
            keyword = CRAWLER_CONFIG['keyword']
        
        if not max_pages:
            max_pages = CRAWLER_CONFIG['max_pages']
        
        self.stats['start_time'] = datetime.now()
        log_crawler_start(self.logger, keyword)
        
        # 创建数据存储会话目录
        session_dir = self.storage_manager.create_session_directory(keyword)
        if session_dir:
            self.logger.info(f"创建数据存储会话目录: {session_dir}")
        
        try:
            # 获取已存在的微博ID，用于去重
            existing_ids = self.db_manager.get_existing_ids()
            self.logger.info(f"数据库中已有 {len(existing_ids)} 条记录")
            
            # 记录爬取开始日志
            log_data = {
                'keyword': keyword,
                'start_time': self.stats['start_time'],
                'end_time': None,
                'total_crawled': 0,
                'success_count': 0,
                'error_count': 0,
                'status': 'running',
                'error_message': None
            }
            
            batch_data = []  # 批量插入缓存
            all_crawled_data = []  # 存储所有爬取的数据用于文件保存
            
            for page in range(1, max_pages + 1):
                if not self.is_running:
                    self.logger.info("收到停止信号，退出爬取")
                    break
                
                self.logger.info(f"正在爬取第 {page} 页...")
                
                try:
                    # 爬取当前页数据
                    weibo_list = self.spider.crawl_with_retry(keyword, page)
                    
                    if not weibo_list:
                        self.logger.warning(f"第 {page} 页没有获取到数据")
                        continue
                    
                    # 过滤已存在的数据
                    new_weibo_list = []
                    for weibo in weibo_list:
                        if weibo['_id'] not in existing_ids:
                            new_weibo_list.append(weibo)
                            existing_ids.add(weibo['_id'])
                    
                    if new_weibo_list:
                        batch_data.extend(new_weibo_list)
                        all_crawled_data.extend(new_weibo_list)  # 保存所有数据用于文件存储
                        self.stats['total_crawled'] += len(new_weibo_list)
                        
                        log_page_result(self.logger, page, len(new_weibo_list))
                        
                        # 批量插入数据库
                        if len(batch_data) >= CRAWLER_CONFIG['batch_size']:
                            success_count = self.db_manager.batch_insert_weibo_data(batch_data)
                            self.stats['success_count'] += success_count
                            self.stats['error_count'] += len(batch_data) - success_count
                            batch_data = []  # 清空缓存
                    else:
                        self.logger.info(f"第 {page} 页数据已存在，跳过")
                    
                    # 随机延迟
                    self.spider.random_delay()
                    
                except Exception as e:
                    self.logger.error(f"爬取第 {page} 页失败: {e}")
                    self.stats['error_count'] += 1
                    continue
            
            # 处理剩余的批量数据
            if batch_data:
                success_count = self.db_manager.batch_insert_weibo_data(batch_data)
                self.stats['success_count'] += success_count
                self.stats['error_count'] += len(batch_data) - success_count
            
            # 更新统计信息
            self.stats['end_time'] = datetime.now()
            self.stats['duration'] = calculate_time_diff(
                self.stats['start_time'], 
                self.stats['end_time']
            )
            
            # 记录爬取结束日志
            log_data.update({
                'end_time': self.stats['end_time'],
                'total_crawled': self.stats['total_crawled'],
                'success_count': self.stats['success_count'],
                'error_count': self.stats['error_count'],
                'status': 'completed' if self.is_running else 'interrupted',
                'error_message': None
            })
            
            self.db_manager.insert_crawl_log(log_data)
            log_crawler_end(self.logger, self.stats)
            
            # 保存结构化数据到文件
            if all_crawled_data:
                self.storage_manager.save_structured_data(all_crawled_data)
                self.logger.info(f"保存结构化数据: {len(all_crawled_data)} 条记录")
            
            # 生成并保存分析报告
            try:
                analyzer = WeiboDataAnalyzer(self.db_manager)
                report = analyzer.generate_summary_report(keyword)
                if report:
                    self.storage_manager.save_analysis_report(report)
                    self.logger.info("保存分析报告完成")
            except Exception as e:
                self.logger.warning(f"生成分析报告失败: {e}")
            
            # 保存会话元数据
            session_metadata = {
                'keyword': keyword,
                'max_pages': max_pages,
                'total_crawled': self.stats['total_crawled'],
                'success_count': self.stats['success_count'],
                'error_count': self.stats['error_count'],
                'start_time': self.stats['start_time'].isoformat(),
                'end_time': self.stats['end_time'].isoformat(),
                'duration': self.stats['duration']
            }
            self.storage_manager.save_session_metadata(session_metadata)
            
            return True
            
        except Exception as e:
            self.logger.error(f"爬取过程发生错误: {e}")
            
            # 记录错误日志
            if 'log_data' in locals():
                log_data.update({
                    'end_time': datetime.now(),
                    'total_crawled': self.stats['total_crawled'],
                    'success_count': self.stats['success_count'],
                    'error_count': self.stats['error_count'],
                    'status': 'error',
                    'error_message': str(e)
                })
                self.db_manager.insert_crawl_log(log_data)
            
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取爬取统计信息"""
        db_stats = self.db_manager.get_crawl_statistics()
        
        return {
            'current_session': self.stats,
            'database_stats': db_stats
        }
    
    def cleanup(self):
        """清理资源"""
        try:
            self.db_manager.disconnect()
            self.logger.info("资源清理完成")
        except Exception as e:
            self.logger.error(f"清理资源失败: {e}")

def main():
    """主函数"""
    crawler = WeiboDataCrawler()
    
    try:
        # 初始化系统
        if not crawler.initialize():
            print("系统初始化失败，程序退出")
            return 1
        
        # 开始爬取数据
        success = crawler.crawl_weibo_data()
        
        # 显示统计信息
        stats = crawler.get_statistics()
        print("\n" + "="*50)
        print("爬取统计信息:")
        print(f"本次爬取: {stats['current_session']['total_crawled']} 条")
        print(f"成功保存: {stats['current_session']['success_count']} 条")
        print(f"失败数量: {stats['current_session']['error_count']} 条")
        print(f"数据库总量: {stats['database_stats'].get('total_count', 0)} 条")
        print(f"今日爬取: {stats['database_stats'].get('today_count', 0)} 条")
        print("="*50)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n用户中断程序")
        return 1
    except Exception as e:
        print(f"程序运行出错: {e}")
        return 1
    finally:
        crawler.cleanup()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)