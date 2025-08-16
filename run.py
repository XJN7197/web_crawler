"""
微博爬虫系统快速启动脚本
提供简单的命令行界面
"""
import os
import sys
import argparse

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import WeiboDataCrawler
from analyze_data import main as analyze_main
from utils.logger import setup_logger

def run_crawler(keyword=None, pages=None):
    """运行爬虫"""
    print("🚀 启动微博爬虫系统...")
    
    crawler = WeiboDataCrawler()
    
    try:
        # 初始化系统
        if not crawler.initialize():
            print("❌ 系统初始化失败")
            return False
        
        # 开始爬取
        success = crawler.crawl_weibo_data(keyword=keyword, max_pages=pages)
        
        if success:
            # 显示统计信息
            stats = crawler.get_statistics()
            print("\n✅ 爬取完成！")
            print(f"📊 本次爬取: {stats['current_session']['total_crawled']} 条")
            print(f"💾 成功保存: {stats['current_session']['success_count']} 条")
            print(f"📈 数据库总量: {stats['database_stats'].get('total_count', 0)} 条")
        else:
            print("❌ 爬取过程中出现错误")
            
        return success
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断爬取")
        return False
    except Exception as e:
        print(f"❌ 运行出错: {e}")
        return False
    finally:
        crawler.cleanup()

def run_analysis():
    """运行数据分析"""
    print("📊 启动数据分析...")
    return analyze_main() == 0

def show_status():
    """显示系统状态"""
    print("📋 系统状态检查...")
    
    try:
        from database.models import DatabaseManager
        
        db_manager = DatabaseManager()
        if db_manager.connect():
            stats = db_manager.get_crawl_statistics()
            print("✅ 数据库连接正常")
            print(f"📊 数据库统计:")
            print(f"  总数据量: {stats.get('total_count', 0):,} 条")
            print(f"  今日爬取: {stats.get('today_count', 0):,} 条")
            print(f"  最新爬取: {stats.get('latest_crawl', '无')}")
            db_manager.disconnect()
            return True
        else:
            print("❌ 数据库连接失败")
            return False
            
    except Exception as e:
        print(f"❌ 状态检查失败: {e}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="微博爬虫系统 - 李雨珊事件数据采集",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python run.py crawl                    # 使用默认配置爬取
  python run.py crawl -k "关键词" -p 20   # 自定义关键词和页数
  python run.py analyze                  # 分析已爬取的数据
  python run.py status                   # 查看系统状态
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 爬取命令
    crawl_parser = subparsers.add_parser('crawl', help='开始爬取微博数据')
    crawl_parser.add_argument('-k', '--keyword', type=str, 
                             help='搜索关键词 (默认: 李雨珊事件)')
    crawl_parser.add_argument('-p', '--pages', type=int, 
                             help='最大爬取页数 (默认: 50)')
    
    # 分析命令
    subparsers.add_parser('analyze', help='分析已爬取的数据')
    
    # 状态命令
    subparsers.add_parser('status', help='查看系统状态')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    print("="*60)
    print("🐍 微博爬虫系统 - 李雨珊事件数据采集")
    print("="*60)
    
    success = False
    
    if args.command == 'crawl':
        success = run_crawler(keyword=args.keyword, pages=args.pages)
    elif args.command == 'analyze':
        success = run_analysis()
    elif args.command == 'status':
        success = show_status()
    
    print("="*60)
    
    if success:
        print("🎉 操作完成！")
        return 0
    else:
        print("❌ 操作失败！")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断程序")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 程序异常: {e}")
        sys.exit(1)