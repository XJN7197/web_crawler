"""
数据库连接诊断脚本
用于验证数据库连接问题的根本原因
"""
import sys
import subprocess
import pymysql
from config.settings import DATABASE_CONFIG

def check_cryptography():
    """检查cryptography包是否安装"""
    try:
        import cryptography
        print(f"✓ cryptography已安装，版本: {cryptography.__version__}")
        return True
    except ImportError:
        print("✗ cryptography包未安装")
        return False

def check_pymysql_version():
    """检查PyMySQL版本"""
    print(f"PyMySQL版本: {pymysql.__version__}")

def test_mysql_connection():
    """测试MySQL连接"""
    print(f"尝试连接MySQL: {DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}")
    print(f"数据库: {DATABASE_CONFIG['database']}")
    print(f"用户: {DATABASE_CONFIG['user']}")
    
    try:
        # 尝试不指定数据库的连接
        connection = pymysql.connect(
            host=DATABASE_CONFIG['host'],
            port=DATABASE_CONFIG['port'],
            user=DATABASE_CONFIG['user'],
            password=DATABASE_CONFIG['password'],
            charset=DATABASE_CONFIG['charset']
        )
        print("✓ MySQL服务器连接成功")
        
        # 检查MySQL版本
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            print(f"MySQL版本: {version}")
            
            # 检查认证插件
            cursor.execute("SELECT user, host, plugin FROM mysql.user WHERE user = %s", (DATABASE_CONFIG['user'],))
            user_info = cursor.fetchone()
            if user_info:
                print(f"用户认证插件: {user_info[2]}")
            
        connection.close()
        return True
        
    except Exception as e:
        print(f"✗ MySQL连接失败: {e}")
        return False

def test_database_creation():
    """测试数据库创建"""
    try:
        connection = pymysql.connect(
            host=DATABASE_CONFIG['host'],
            port=DATABASE_CONFIG['port'],
            user=DATABASE_CONFIG['user'],
            password=DATABASE_CONFIG['password'],
            charset=DATABASE_CONFIG['charset']
        )
        
        with connection.cursor() as cursor:
            # 检查数据库是否存在
            cursor.execute("SHOW DATABASES LIKE %s", (DATABASE_CONFIG['database'],))
            db_exists = cursor.fetchone()
            
            if db_exists:
                print(f"✓ 数据库 '{DATABASE_CONFIG['database']}' 已存在")
            else:
                print(f"✗ 数据库 '{DATABASE_CONFIG['database']}' 不存在")
                
                # 尝试创建数据库
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_CONFIG['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                print(f"✓ 数据库 '{DATABASE_CONFIG['database']}' 创建成功")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"✗ 数据库操作失败: {e}")
        return False

def main():
    """主诊断函数"""
    print("="*60)
    print("数据库连接问题诊断")
    print("="*60)
    
    print("\n1. 检查依赖包...")
    crypto_ok = check_cryptography()
    check_pymysql_version()
    
    print("\n2. 测试MySQL连接...")
    mysql_ok = test_mysql_connection()
    
    if mysql_ok:
        print("\n3. 测试数据库操作...")
        db_ok = test_database_creation()
    
    print("\n" + "="*60)
    print("诊断结果:")
    
    if not crypto_ok:
        print("❌ 主要问题: 缺少cryptography依赖包")
        print("解决方案: pip install cryptography")
    elif not mysql_ok:
        print("❌ 主要问题: MySQL连接失败")
        print("请检查MySQL服务是否启动，用户名密码是否正确")
    else:
        print("✅ 数据库连接正常")
    
    print("="*60)

if __name__ == "__main__":
    main()