"""
多平台爬虫系统安装和配置脚本
"""
import os
import sys
import subprocess
import json
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    print(f"✅ Python版本检查通过: {sys.version}")
    return True

def install_dependencies():
    """安装依赖包"""
    print("📦 正在安装依赖包...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依赖包安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖包安装失败: {e}")
        return False

def create_directories():
    """创建必要的目录"""
    directories = ['logs', 'data']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ 创建目录: {directory}")

def setup_database_config():
    """设置数据库配置"""
    print("\n🔧 数据库配置设置")
    print("请输入MySQL数据库配置信息:")
    
    config = {}
    config['host'] = input("数据库主机 (默认: localhost): ").strip() or 'localhost'
    config['port'] = int(input("数据库端口 (默认: 3306): ").strip() or '3306')
    config['user'] = input("数据库用户名: ").strip()
    config['password'] = input("数据库密码: ").strip()
    config['database'] = input("数据库名称 (默认: multi_crawler): ").strip() or 'multi_crawler'
    
    # 测试数据库连接
    try:
        import pymysql
        connection = pymysql.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # 创建数据库（如果不存在）
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        
        connection.close()
        print("✅ 数据库连接测试成功")
        
        # 更新配置文件
        update_config_file(config)
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

def update_config_file(db_config):
    """更新配置文件"""
    config_file = 'config/settings.py'
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换数据库配置
        new_config = f"""DATABASE_CONFIG = {{
    'host': '{db_config['host']}',
    'port': {db_config['port']},
    'user': '{db_config['user']}',
    'password': '{db_config['password']}',
    'database': '{db_config['database']}',
    'charset': 'utf8mb4'
}}"""
        
        # 找到并替换DATABASE_CONFIG部分
        import re
        pattern = r'DATABASE_CONFIG\s*=\s*\{[^}]*\}'
        content = re.sub(pattern, new_config, content, flags=re.DOTALL)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ 配置文件更新完成")
        return True
        
    except Exception as e:
        print(f"❌ 配置文件更新失败: {e}")
        return False

def initialize_database():
    """初始化数据库表"""
    print("🗄️ 正在初始化数据库表...")
    
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from database.models import DatabaseManager
        
        db_manager = DatabaseManager()
        if db_manager.connect():
            if db_manager.create_tables():
                print("✅ 数据库表创建成功")
                db_manager.disconnect()
                return True
            else:
                print("❌ 数据库表创建失败")
                return False
        else:
            print("❌ 数据库连接失败")
            return False
            
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False

def show_usage_instructions():
    """显示使用说明"""
    print("\n" + "="*60)
    print("🎉 多平台爬虫系统安装完成！")
    print("="*60)
    print("\n📖 使用方法:")
    print("1. 基本爬取:")
    print("   python run.py crawl")
    print("\n2. 自定义爬取:")
    print("   python run.py crawl -k '关键词' -p 20")
    print("\n3. 数据分析:")
    print("   python run.py analyze")
    print("\n4. 查看状态:")
    print("   python run.py status")
    print("\n5. 直接运行主程序:")
    print("   python main.py")
    print("\n📚 更多信息请查看 README.md")
    print("="*60)

def main():
    """主安装流程"""
    print("🚀 多平台爬虫系统安装程序")
    print("="*50)
    
    # 检查Python版本
    if not check_python_version():
        return 1
    
    # 创建目录
    create_directories()
    
    # 安装依赖
    if not install_dependencies():
        return 1
    
    # 数据库配置
    if not setup_database_config():
        print("⚠️ 数据库配置失败，请手动修改 config/settings.py")
        return 1
    
    # 初始化数据库
    if not initialize_database():
        print("⚠️ 数据库初始化失败，请检查配置后手动运行")
        return 1
    
    # 显示使用说明
    show_usage_instructions()
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ 安装被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 安装过程出错: {e}")
        sys.exit(1)