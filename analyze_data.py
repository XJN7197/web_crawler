"""
数据分析独立脚本
用于分析已爬取的微博数据并生成报告
"""
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.models import DatabaseManager
from utils.data_analyzer import WeiboDataAnalyzer
from utils.logger import setup_logger

def main():
    """主函数"""
    logger = setup_logger('data_analyzer')
    
    try:
        print("正在初始化数据分析器...")
        
        # 初始化数据库连接
        db_manager = DatabaseManager()
        if not db_manager.connect():
            print("❌ 数据库连接失败，请检查配置")
            return 1
        
        # 创建分析器
        analyzer = WeiboDataAnalyzer(db_manager)
        
        print("正在生成数据分析报告...")
        
        # 生成报告
        report = analyzer.generate_summary_report("李雨珊事件")
        
        if not report:
            print("❌ 生成报告失败，可能没有相关数据")
            return 1
        
        # 打印摘要
        analyzer.print_summary(report)
        
        # 导出详细报告
        filename = analyzer.export_report_to_json(report)
        if filename:
            print(f"\n✅ 详细报告已导出到: {filename}")
        
        # 关闭数据库连接
        db_manager.disconnect()
        
        print("\n🎉 数据分析完成！")
        return 0
        
    except Exception as e:
        logger.error(f"数据分析过程出错: {e}")
        print(f"❌ 分析失败: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)