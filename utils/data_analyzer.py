"""
数据分析和报告生成模块
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import Counter
from decimal import Decimal
import re

logger = logging.getLogger(__name__)

class DecimalEncoder(json.JSONEncoder):
    """自定义JSON编码器，处理Decimal和datetime类型"""
    
    def default(self, obj):
        if isinstance(obj, Decimal):
            # 将Decimal转换为float，保持数值精度
            return float(obj)
        elif isinstance(obj, datetime):
            # 将datetime转换为ISO格式字符串
            return obj.isoformat()
        return super(DecimalEncoder, self).default(obj)

class WeiboDataAnalyzer:
    """微博数据分析器"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def generate_summary_report(self, keyword: str = "李雨珊事件") -> Dict[str, Any]:
        """生成数据摘要报告"""
        try:
            if not self.db_manager.connection:
                if not self.db_manager.connect():
                    return {}
            
            report = {
                'keyword': keyword,
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'basic_stats': self._get_basic_statistics(keyword),
                'time_distribution': self._get_time_distribution(keyword),
                'user_analysis': self._get_user_analysis(keyword),
                'content_analysis': self._get_content_analysis(keyword),
                'engagement_analysis': self._get_engagement_analysis(keyword),
                'geographic_analysis': self._get_geographic_analysis(keyword)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"生成摘要报告失败: {e}")
            return {}
    
    def _get_basic_statistics(self, keyword: str) -> Dict[str, Any]:
        """获取基础统计信息"""
        try:
            with self.db_manager.connection.cursor() as cursor:
                # 总数据量
                cursor.execute("""
                    SELECT COUNT(*) as total_count,
                           MIN(created_at) as earliest_post,
                           MAX(created_at) as latest_post,
                           AVG(reposts_count) as avg_reposts,
                           AVG(comments_count) as avg_comments,
                           AVG(attitudes_count) as avg_likes
                    FROM weibo_data 
                    WHERE keyword = %s
                """, (keyword,))
                
                result = cursor.fetchone()
                
                if result:
                    return {
                        'total_posts': result[0],
                        'earliest_post': result[1].strftime('%Y-%m-%d %H:%M:%S') if result[1] else None,
                        'latest_post': result[2].strftime('%Y-%m-%d %H:%M:%S') if result[2] else None,
                        'avg_reposts': round(result[3] or 0, 2),
                        'avg_comments': round(result[4] or 0, 2),
                        'avg_likes': round(result[5] or 0, 2)
                    }
                
                return {}
                
        except Exception as e:
            logger.error(f"获取基础统计失败: {e}")
            return {}
    
    def _get_time_distribution(self, keyword: str) -> Dict[str, Any]:
        """获取时间分布分析"""
        try:
            with self.db_manager.connection.cursor() as cursor:
                # 按日期分布
                cursor.execute("""
                    SELECT DATE(created_at) as post_date, 
                           COUNT(*) as post_count
                    FROM weibo_data 
                    WHERE keyword = %s AND created_at IS NOT NULL
                    GROUP BY DATE(created_at)
                    ORDER BY post_date
                """, (keyword,))
                
                daily_data = cursor.fetchall()
                
                # 按小时分布
                cursor.execute("""
                    SELECT HOUR(created_at) as post_hour, 
                           COUNT(*) as post_count
                    FROM weibo_data 
                    WHERE keyword = %s AND created_at IS NOT NULL
                    GROUP BY HOUR(created_at)
                    ORDER BY post_hour
                """, (keyword,))
                
                hourly_data = cursor.fetchall()
                
                return {
                    'daily_distribution': [
                        {
                            'date': row[0].strftime('%Y-%m-%d'),
                            'count': row[1]
                        } for row in daily_data
                    ],
                    'hourly_distribution': [
                        {
                            'hour': row[0],
                            'count': row[1]
                        } for row in hourly_data
                    ]
                }
                
        except Exception as e:
            logger.error(f"获取时间分布失败: {e}")
            return {}
    
    def _get_user_analysis(self, keyword: str) -> Dict[str, Any]:
        """获取用户分析"""
        try:
            with self.db_manager.connection.cursor() as cursor:
                # 活跃用户TOP10
                cursor.execute("""
                    SELECT user_nick_name, 
                           COUNT(*) as post_count,
                           SUM(reposts_count) as total_reposts,
                           SUM(comments_count) as total_comments,
                           SUM(attitudes_count) as total_likes
                    FROM weibo_data 
                    WHERE keyword = %s AND user_nick_name IS NOT NULL
                    GROUP BY user_nick_name
                    ORDER BY post_count DESC
                    LIMIT 10
                """, (keyword,))
                
                top_users = cursor.fetchall()
                
                # 认证用户统计
                cursor.execute("""
                    SELECT user_verified, COUNT(*) as count
                    FROM weibo_data 
                    WHERE keyword = %s
                    GROUP BY user_verified
                """, (keyword,))
                
                verified_stats = cursor.fetchall()
                
                return {
                    'top_active_users': [
                        {
                            'username': row[0],
                            'post_count': row[1],
                            'total_reposts': row[2] or 0,
                            'total_comments': row[3] or 0,
                            'total_likes': row[4] or 0
                        } for row in top_users
                    ],
                    'verified_distribution': {
                        'verified': next((row[1] for row in verified_stats if row[0]), 0),
                        'unverified': next((row[1] for row in verified_stats if not row[0]), 0)
                    }
                }
                
        except Exception as e:
            logger.error(f"获取用户分析失败: {e}")
            return {}
    
    def _get_content_analysis(self, keyword: str) -> Dict[str, Any]:
        """获取内容分析"""
        try:
            with self.db_manager.connection.cursor() as cursor:
                # 获取所有内容进行分析
                cursor.execute("""
                    SELECT content, pic_num, isLongText, source
                    FROM weibo_data 
                    WHERE keyword = %s AND content IS NOT NULL
                """, (keyword,))
                
                contents = cursor.fetchall()
                
                # 分析内容特征
                total_posts = len(contents)
                long_text_count = sum(1 for row in contents if row[2])
                has_image_count = sum(1 for row in contents if row[1] and row[1] > 0)
                
                # 来源统计
                sources = [row[3] for row in contents if row[3]]
                source_counter = Counter(sources)
                
                # 提取话题标签
                all_hashtags = []
                for row in contents:
                    if row[0]:
                        hashtags = re.findall(r'#([^#]+)#', row[0])
                        all_hashtags.extend(hashtags)
                
                hashtag_counter = Counter(all_hashtags)
                
                return {
                    'total_analyzed': total_posts,
                    'long_text_ratio': round(long_text_count / total_posts * 100, 2) if total_posts > 0 else 0,
                    'image_ratio': round(has_image_count / total_posts * 100, 2) if total_posts > 0 else 0,
                    'top_sources': [
                        {'source': source, 'count': count}
                        for source, count in source_counter.most_common(10)
                    ],
                    'top_hashtags': [
                        {'hashtag': hashtag, 'count': count}
                        for hashtag, count in hashtag_counter.most_common(10)
                    ]
                }
                
        except Exception as e:
            logger.error(f"获取内容分析失败: {e}")
            return {}
    
    def _get_engagement_analysis(self, keyword: str) -> Dict[str, Any]:
        """获取互动分析"""
        try:
            with self.db_manager.connection.cursor() as cursor:
                # 互动数据统计
                cursor.execute("""
                    SELECT 
                        SUM(reposts_count) as total_reposts,
                        SUM(comments_count) as total_comments,
                        SUM(attitudes_count) as total_likes,
                        MAX(reposts_count) as max_reposts,
                        MAX(comments_count) as max_comments,
                        MAX(attitudes_count) as max_likes
                    FROM weibo_data 
                    WHERE keyword = %s
                """, (keyword,))
                
                result = cursor.fetchone()
                
                # 高互动微博TOP10
                cursor.execute("""
                    SELECT content, user_nick_name, reposts_count, comments_count, attitudes_count,
                           (reposts_count + comments_count + attitudes_count) as total_engagement
                    FROM weibo_data 
                    WHERE keyword = %s
                    ORDER BY total_engagement DESC
                    LIMIT 10
                """, (keyword,))
                
                top_engagement = cursor.fetchall()
                
                if result:
                    return {
                        'total_engagement': {
                            'reposts': result[0] or 0,
                            'comments': result[1] or 0,
                            'likes': result[2] or 0
                        },
                        'max_engagement': {
                            'reposts': result[3] or 0,
                            'comments': result[4] or 0,
                            'likes': result[5] or 0
                        },
                        'top_engagement_posts': [
                            {
                                'content': row[0][:100] + '...' if row[0] and len(row[0]) > 100 else row[0],
                                'user': row[1],
                                'reposts': row[2] or 0,
                                'comments': row[3] or 0,
                                'likes': row[4] or 0,
                                'total': row[5] or 0
                            } for row in top_engagement
                        ]
                    }
                
                return {}
                
        except Exception as e:
            logger.error(f"获取互动分析失败: {e}")
            return {}
    
    def _get_geographic_analysis(self, keyword: str) -> Dict[str, Any]:
        """获取地理分析"""
        try:
            with self.db_manager.connection.cursor() as cursor:
                # IP位置统计
                cursor.execute("""
                    SELECT ip_location, COUNT(*) as count
                    FROM weibo_data 
                    WHERE keyword = %s AND ip_location IS NOT NULL AND ip_location != ''
                    GROUP BY ip_location
                    ORDER BY count DESC
                    LIMIT 20
                """, (keyword,))
                
                ip_locations = cursor.fetchall()
                
                # 地理位置统计
                cursor.execute("""
                    SELECT geo_detail_title, COUNT(*) as count
                    FROM weibo_data 
                    WHERE keyword = %s AND geo_detail_title IS NOT NULL AND geo_detail_title != ''
                    GROUP BY geo_detail_title
                    ORDER BY count DESC
                    LIMIT 20
                """, (keyword,))
                
                geo_locations = cursor.fetchall()
                
                return {
                    'ip_distribution': [
                        {'location': row[0], 'count': row[1]}
                        for row in ip_locations
                    ],
                    'geo_distribution': [
                        {'location': row[0], 'count': row[1]}
                        for row in geo_locations
                    ]
                }
                
        except Exception as e:
            logger.error(f"获取地理分析失败: {e}")
            return {}
    
    def export_report_to_json(self, report: Dict[str, Any], filename: str = None) -> str:
        """导出报告为JSON文件"""
        try:
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"data/weibo_analysis_report_{timestamp}.json"
            
            # 确保目录存在
            import os
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, cls=DecimalEncoder)
            
            logger.info(f"报告已导出到: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"导出报告失败: {e}")
            logger.error(f"错误类型: {type(e).__name__}")
            logger.error(f"错误详情: {str(e)}")
            return ""
    
    
    def print_summary(self, report: Dict[str, Any]):
        """打印报告摘要"""
        try:
            print("\n" + "="*60)
            print(f"微博数据分析报告 - {report.get('keyword', '未知关键词')}")
            print(f"生成时间: {report.get('generated_at', '未知')}")
            print("="*60)
            
            # 基础统计
            basic = report.get('basic_stats', {})
            if basic:
                print(f"\n📊 基础统计:")
                print(f"  总微博数: {basic.get('total_posts', 0):,}")
                print(f"  时间范围: {basic.get('earliest_post', '未知')} ~ {basic.get('latest_post', '未知')}")
                print(f"  平均转发: {basic.get('avg_reposts', 0)}")
                print(f"  平均评论: {basic.get('avg_comments', 0)}")
                print(f"  平均点赞: {basic.get('avg_likes', 0)}")
            
            # 用户分析
            user_analysis = report.get('user_analysis', {})
            if user_analysis:
                print(f"\n👥 用户分析:")
                verified = user_analysis.get('verified_distribution', {})
                print(f"  认证用户: {verified.get('verified', 0)}")
                print(f"  普通用户: {verified.get('unverified', 0)}")
                
                top_users = user_analysis.get('top_active_users', [])[:5]
                if top_users:
                    print(f"  活跃用户TOP5:")
                    for i, user in enumerate(top_users, 1):
                        print(f"    {i}. {user.get('username', '未知')} ({user.get('post_count', 0)}条)")
            
            # 内容分析
            content = report.get('content_analysis', {})
            if content:
                print(f"\n📝 内容分析:")
                print(f"  长文本比例: {content.get('long_text_ratio', 0)}%")
                print(f"  含图片比例: {content.get('image_ratio', 0)}%")
                
                top_hashtags = content.get('top_hashtags', [])[:5]
                if top_hashtags:
                    print(f"  热门话题TOP5:")
                    for i, tag in enumerate(top_hashtags, 1):
                        print(f"    {i}. #{tag.get('hashtag', '未知')}# ({tag.get('count', 0)}次)")
            
            # 互动分析
            engagement = report.get('engagement_analysis', {})
            if engagement:
                total_eng = engagement.get('total_engagement', {})
                print(f"\n💬 互动统计:")
                print(f"  总转发数: {total_eng.get('reposts', 0):,}")
                print(f"  总评论数: {total_eng.get('comments', 0):,}")
                print(f"  总点赞数: {total_eng.get('likes', 0):,}")
            
            print("="*60)
            
        except Exception as e:
            logger.error(f"打印摘要失败: {e}")