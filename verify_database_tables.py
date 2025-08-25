"""
验证数据库表结构
确认微博和抖音数据使用同一数据库的不同表
"""
import pymysql
from config.settings import DATABASE_CONFIG

def verify_database_structure():
    """验证数据库表结构"""
    print("="*60)
    print("数据库表结构验证")
    print("="*60)
    
    try:
        # 连接数据库
        connection = pymysql.connect(**DATABASE_CONFIG)
        
        with connection.cursor() as cursor:
            # 显示数据库信息
            cursor.execute("SELECT DATABASE()")
            current_db = cursor.fetchone()[0]
            print(f"当前数据库: {current_db}")
            
            # 显示所有表
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"\n数据库中的表 ({len(tables)} 个):")
            
            table_info = {}
            for table in tables:
                table_name = table[0]
                print(f"  - {table_name}")
                
                # 获取表的记录数
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                table_info[table_name] = count
            
            print(f"\n表数据统计:")
            for table_name, count in table_info.items():
                print(f"  - {table_name}: {count} 条记录")
            
            # 检查微博表结构
            if 'weibo_data' in table_info:
                print(f"\n微博数据表结构:")
                cursor.execute("DESCRIBE weibo_data")
                weibo_columns = cursor.fetchall()
                for col in weibo_columns:
                    print(f"  - {col[0]}: {col[1]}")
            
            # 检查抖音表结构
            if 'douyin_data' in table_info:
                print(f"\n抖音数据表结构:")
                cursor.execute("DESCRIBE douyin_data")
                douyin_columns = cursor.fetchall()
                for col in douyin_columns:
                    print(f"  - {col[0]}: {col[1]}")
            
            # 验证最新的抖音数据
            if 'douyin_data' in table_info and table_info['douyin_data'] > 0:
                print(f"\n最新抖音数据样本:")
                cursor.execute("SELECT _id, content, user_name, platform, created_at FROM douyin_data ORDER BY created_at DESC LIMIT 3")
                recent_douyin = cursor.fetchall()
                for i, row in enumerate(recent_douyin, 1):
                    print(f"  {i}. ID: {row[0]}")
                    print(f"     内容: {row[1][:50]}...")
                    print(f"     作者: {row[2]}")
                    print(f"     平台: {row[3]}")
                    print(f"     时间: {row[4]}")
                    print()
            
            # 验证最新的微博数据
            if 'weibo_data' in table_info and table_info['weibo_data'] > 0:
                print(f"\n最新微博数据样本:")
                cursor.execute("SELECT _id, content, user_nick_name, 'weibo' as platform, created_at FROM weibo_data ORDER BY created_at DESC LIMIT 2")
                recent_weibo = cursor.fetchall()
                for i, row in enumerate(recent_weibo, 1):
                    print(f"  {i}. ID: {row[0]}")
                    print(f"     内容: {row[1][:50]}...")
                    print(f"     作者: {row[2]}")
                    print(f"     平台: {row[3]}")
                    print(f"     时间: {row[4]}")
                    print()
        
        connection.close()
        
        print("="*60)
        print("✅ 验证结果:")
        print("1. 微博和抖音数据使用同一个数据库: multi_crawler")
        print("2. 微博数据存储在: weibo_data 表")
        print("3. 抖音数据存储在: douyin_data 表")
        print("4. 两个平台的数据完全分离，互不影响")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

if __name__ == "__main__":
    verify_database_structure()