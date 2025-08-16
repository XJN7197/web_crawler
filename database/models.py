"""
数据库模型定义
"""
import pymysql
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from config.settings import DATABASE_CONFIG

logger = logging.getLogger(__name__)

class DatabaseManager:
    """数据库管理类"""
    
    def __init__(self):
        self.config = DATABASE_CONFIG
        self.connection = None
        
    def connect(self):
        """建立数据库连接"""
        try:
            self.connection = pymysql.connect(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.config['database'],
                charset=self.config['charset'],
                autocommit=True
            )
            logger.info("数据库连接成功")
            return True
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            return False
    
    def disconnect(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            logger.info("数据库连接已关闭")
    
    def create_database(self):
        """创建数据库"""
        try:
            # 连接到MySQL服务器（不指定数据库）
            temp_connection = pymysql.connect(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['user'],
                password=self.config['password'],
                charset=self.config['charset']
            )
            
            with temp_connection.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                logger.info(f"数据库 {self.config['database']} 创建成功")
            
            temp_connection.close()
            return True
        except Exception as e:
            logger.error(f"创建数据库失败: {e}")
            return False
    
    def create_tables(self):
        """创建数据表"""
        if not self.connection:
            if not self.connect():
                return False
        
        # 微博数据表
        weibo_table_sql = """
        CREATE TABLE IF NOT EXISTS weibo_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            _id VARCHAR(50) UNIQUE NOT NULL COMMENT '微博ID',
            mblogid VARCHAR(50) COMMENT '文本ID',
            created_at DATETIME COMMENT '创建时间',
            geo_type VARCHAR(20) COMMENT '地理位置类型',
            geo_coordinates TEXT COMMENT '地理坐标',
            geo_detail_poiid VARCHAR(50) COMMENT 'POI地点ID',
            geo_detail_title VARCHAR(100) COMMENT '地理位置标题',
            geo_detail_type VARCHAR(20) COMMENT '地理位置详细类型',
            geo_detail_spot_type VARCHAR(20) COMMENT '地点类型',
            ip_location VARCHAR(100) COMMENT 'IP地址',
            reposts_count INT DEFAULT 0 COMMENT '转发数量',
            comments_count INT DEFAULT 0 COMMENT '评论数量',
            attitudes_count INT DEFAULT 0 COMMENT '点赞数量',
            source VARCHAR(200) COMMENT '来源',
            content TEXT COMMENT '正文内容',
            pic_urls TEXT COMMENT '图片URL列表',
            pic_num INT DEFAULT 0 COMMENT '图片数量',
            isLongText BOOLEAN DEFAULT FALSE COMMENT '是否为长文本',
            user_id VARCHAR(50) COMMENT '用户ID',
            user_avatar_hd VARCHAR(500) COMMENT '用户高清头像URL',
            user_nick_name VARCHAR(100) COMMENT '用户昵称',
            user_verified BOOLEAN DEFAULT FALSE COMMENT '是否认证',
            user_mbrank INT DEFAULT 0 COMMENT '微博会员等级',
            user_mbtype INT DEFAULT 0 COMMENT '微博会员类型',
            user_verified_type INT DEFAULT -1 COMMENT '认证类型',
            url VARCHAR(500) COMMENT '微博URL',
            keyword VARCHAR(100) COMMENT '关键词',
            crawl_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '爬取时间',
            created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
            updated_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间',
            INDEX idx_created_at (created_at),
            INDEX idx_user_id (user_id),
            INDEX idx_keyword (keyword),
            INDEX idx_crawl_time (crawl_time)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='微博数据表';
        """
        
        # 爬取日志表
        log_table_sql = """
        CREATE TABLE IF NOT EXISTS crawl_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            keyword VARCHAR(100) COMMENT '关键词',
            start_time DATETIME COMMENT '开始时间',
            end_time DATETIME COMMENT '结束时间',
            total_crawled INT DEFAULT 0 COMMENT '爬取总数',
            success_count INT DEFAULT 0 COMMENT '成功数量',
            error_count INT DEFAULT 0 COMMENT '错误数量',
            status VARCHAR(20) DEFAULT 'running' COMMENT '状态',
            error_message TEXT COMMENT '错误信息',
            created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='爬取日志表';
        """
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(weibo_table_sql)
                cursor.execute(log_table_sql)
                logger.info("数据表创建成功")
                return True
        except Exception as e:
            logger.error(f"创建数据表失败: {e}")
            return False
    
    def insert_weibo_data(self, data: Dict[str, Any]) -> bool:
        """插入微博数据"""
        if not self.connection:
            if not self.connect():
                return False
        
        sql = """
        INSERT IGNORE INTO weibo_data (
            _id, mblogid, created_at, geo_type, geo_coordinates, geo_detail_poiid,
            geo_detail_title, geo_detail_type, geo_detail_spot_type, ip_location,
            reposts_count, comments_count, attitudes_count, source, content,
            pic_urls, pic_num, isLongText, user_id, user_avatar_hd, user_nick_name,
            user_verified, user_mbrank, user_mbtype, user_verified_type, url, keyword
        ) VALUES (
            %(_id)s, %(mblogid)s, %(created_at)s, %(geo_type)s, %(geo_coordinates)s,
            %(geo_detail_poiid)s, %(geo_detail_title)s, %(geo_detail_type)s,
            %(geo_detail_spot_type)s, %(ip_location)s, %(reposts_count)s,
            %(comments_count)s, %(attitudes_count)s, %(source)s, %(content)s,
            %(pic_urls)s, %(pic_num)s, %(isLongText)s, %(user_id)s, %(user_avatar_hd)s,
            %(user_nick_name)s, %(user_verified)s, %(user_mbrank)s, %(user_mbtype)s,
            %(user_verified_type)s, %(url)s, %(keyword)s
        )
        """
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql, data)
                return True
        except Exception as e:
            logger.error(f"插入数据失败: {e}")
            return False
    
    def batch_insert_weibo_data(self, data_list: List[Dict[str, Any]]) -> int:
        """批量插入微博数据"""
        if not self.connection:
            if not self.connect():
                return 0
        
        if not data_list:
            return 0
        
        success_count = 0
        for data in data_list:
            if self.insert_weibo_data(data):
                success_count += 1
        
        logger.info(f"批量插入完成，成功: {success_count}/{len(data_list)}")
        return success_count
    
    def get_existing_ids(self) -> set:
        """获取已存在的微博ID"""
        if not self.connection:
            if not self.connect():
                return set()
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT _id FROM weibo_data")
                results = cursor.fetchall()
                return {row[0] for row in results}
        except Exception as e:
            logger.error(f"获取已存在ID失败: {e}")
            return set()
    
    def insert_crawl_log(self, log_data: Dict[str, Any]) -> bool:
        """插入爬取日志"""
        if not self.connection:
            if not self.connect():
                return False
        
        sql = """
        INSERT INTO crawl_logs (
            keyword, start_time, end_time, total_crawled, success_count,
            error_count, status, error_message
        ) VALUES (
            %(keyword)s, %(start_time)s, %(end_time)s, %(total_crawled)s,
            %(success_count)s, %(error_count)s, %(status)s, %(error_message)s
        )
        """
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql, log_data)
                return True
        except Exception as e:
            logger.error(f"插入爬取日志失败: {e}")
            return False
    
    def get_crawl_statistics(self) -> Dict[str, Any]:
        """获取爬取统计信息"""
        if not self.connection:
            if not self.connect():
                return {}
        
        try:
            with self.connection.cursor() as cursor:
                # 总数据量
                cursor.execute("SELECT COUNT(*) FROM weibo_data")
                total_count = cursor.fetchone()[0]
                
                # 今日爬取量
                cursor.execute("""
                    SELECT COUNT(*) FROM weibo_data 
                    WHERE DATE(crawl_time) = CURDATE()
                """)
                today_count = cursor.fetchone()[0]
                
                # 最新爬取时间
                cursor.execute("SELECT MAX(crawl_time) FROM weibo_data")
                latest_crawl = cursor.fetchone()[0]
                
                return {
                    'total_count': total_count,
                    'today_count': today_count,
                    'latest_crawl': latest_crawl
                }
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}