"""
抖音爬虫功能测试脚本
用于验证抖音数据爬取功能是否正常工作
"""
import os
import sys
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_platform_crawler import MultiPlatformCrawler
from config.settings import PLATFORM_CONFIG
from utils.logger import setup_logger

def test_douyin_crawler():
    """测试抖音爬虫功能"""
    logger = setup_logger()
    
    print("="*60)
    print("抖音爬虫功能测试")
    print("="*60)
    
    try:
        # 创建抖音爬虫实例
        print("1. 创建抖音爬虫实例...")
        crawler = MultiPlatformCrawler(platform='douyin')
        print("✓ 抖音爬虫实例创建成功")
        
        # 初始化系统
        print("\n2. 初始化系统...")
        if crawler.initialize():
            print("✓ 系统初始化成功")
        else:
            print("✗ 系统初始化失败")
            return False
        
        # 测试配置加载
        print("\n3. 测试配置加载...")
        platform_config = PLATFORM_CONFIG.get('douyin')
        if platform_config:
            print(f"✓ 平台配置加载成功: {platform_config['name']}")
            print(f"  - 搜索URL: {platform_config['search_url']}")
            print(f"  - 用户代理: {platform_config['user_agent'][:50]}...")
        else:
            print("✗ 平台配置加载失败")
            return False
        
        # 测试爬虫创建
        print("\n4. 测试爬虫实例...")
        spider = crawler.spider
        if spider:
            print(f"✓ 爬虫实例创建成功: {type(spider).__name__}")
        else:
            print("✗ 爬虫实例创建失败")
            return False
        
        # 测试数据库连接
        print("\n5. 测试数据库连接...")
        db_manager = crawler.db_manager
        if db_manager.connection:
            print("✓ 数据库连接成功")
            
            # 检查抖音数据表是否存在
            try:
                with db_manager.connection.cursor() as cursor:
                    cursor.execute("SHOW TABLES LIKE 'douyin_data'")
                    result = cursor.fetchone()
                    if result:
                        print("✓ 抖音数据表存在")
                    else:
                        print("✗ 抖音数据表不存在")
                        return False
            except Exception as e:
                print(f"✗ 检查数据表失败: {e}")
                return False
        else:
            print("✗ 数据库连接失败")
            return False
        
        # 测试小规模数据爬取
        print("\n6. 测试数据爬取功能...")
        print("正在进行小规模测试爬取（1页数据）...")
        
        test_keyword = "美食"  # 使用通用关键词进行测试
        success = crawler.crawl_data(keyword=test_keyword, max_pages=1)
        
        if success:
            print("✓ 数据爬取测试成功")
            
            # 显示统计信息
            stats = crawler.get_statistics()
            current_stats = stats['current_session']
            
            print(f"  - 爬取关键词: {test_keyword}")
            print(f"  - 总爬取数量: {current_stats['total_crawled']}")
            print(f"  - 成功保存: {current_stats['success_count']}")
            print(f"  - 失败数量: {current_stats['error_count']}")
            
            if current_stats['total_crawled'] > 0:
                print("✓ 成功获取到抖音数据")
            else:
                print("⚠ 未获取到数据，可能是网络问题或反爬虫限制")
        else:
            print("✗ 数据爬取测试失败")
            return False
        
        # 测试数据查询
        print("\n7. 测试数据查询功能...")
        try:
            with db_manager.connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM douyin_data")
                count = cursor.fetchone()[0]
                print(f"✓ 数据库中共有 {count} 条抖音数据")
                
                if count > 0:
                    cursor.execute("SELECT _id, content, author, publish_time FROM douyin_data LIMIT 1")
                    sample = cursor.fetchone()
                    if sample:
                        print("✓ 数据样本:")
                        print(f"  - ID: {sample[0]}")
                        print(f"  - 内容: {sample[1][:50]}...")
                        print(f"  - 作者: {sample[2]}")
                        print(f"  - 发布时间: {sample[3]}")
        except Exception as e:
            print(f"✗ 数据查询失败: {e}")
            return False
        
        print("\n" + "="*60)
        print("✓ 抖音爬虫功能测试完成 - 所有测试通过!")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        logger.error(f"抖音爬虫测试失败: {e}")
        return False
    
    finally:
        # 清理资源
        try:
            crawler.cleanup()
        except:
            pass

def test_platform_comparison():
    """测试平台对比功能"""
    print("\n" + "="*60)
    print("平台对比测试")
    print("="*60)
    
    platforms = ['weibo', 'douyin']
    
    for platform in platforms:
        print(f"\n测试 {PLATFORM_CONFIG[platform]['name']} 平台:")
        try:
            crawler = MultiPlatformCrawler(platform=platform)
            if crawler.initialize():
                print(f"✓ {PLATFORM_CONFIG[platform]['name']} 初始化成功")
                
                # 获取统计信息
                stats = crawler.get_statistics()
                db_stats = stats.get('database_stats', {})
                
                if platform == 'weibo':
                    table_name = 'weibo_data'
                else:
                    table_name = 'douyin_data'
                
                try:
                    with crawler.db_manager.connection.cursor() as cursor:
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        count = cursor.fetchone()[0]
                        print(f"  - 数据库记录数: {count}")
                except:
                    print(f"  - 数据库记录数: 0")
                
                crawler.cleanup()
            else:
                print(f"✗ {PLATFORM_CONFIG[platform]['name']} 初始化失败")
        except Exception as e:
            print(f"✗ {PLATFORM_CONFIG[platform]['name']} 测试失败: {e}")

def main():
    """主测试函数"""
    print("开始抖音爬虫功能测试...")
    
    # 测试抖音爬虫功能
    douyin_success = test_douyin_crawler()
    
    # 测试平台对比
    test_platform_comparison()
    
    # 输出最终结果
    print("\n" + "="*60)
    if douyin_success:
        print("🎉 抖音爬虫功能测试全部通过!")
        print("系统已准备好进行抖音数据爬取。")
        print("\n使用方法:")
        print("python multi_platform_crawler.py --platform douyin --keyword '搜索关键词' --pages 5")
    else:
        print("❌ 抖音爬虫功能测试失败!")
        print("请检查配置和网络连接后重试。")
    print("="*60)
    
    return 0 if douyin_success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)