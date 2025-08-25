# 多平台爬虫系统 - 社交媒体数据采集

一个完整的Python多平台爬虫系统，目前支持微博和抖音平台的数据采集，并将数据存储到MySQL数据库中。

## 🚀 功能特性

### 核心功能
- ✅ 多平台支持：微博、抖音数据爬取
- ✅ 多种爬取方式：支持PC端和移动端API爬取
- ✅ 智能反爬虫：User-Agent轮换、随机延迟、代理池支持
- ✅ 数据去重：基于内容ID的增量爬取机制
- ✅ 批量处理：高效的批量数据库插入
- ✅ 错误重试：自动重试机制，提高爬取成功率

### 数据处理
- ✅ 内容解析：自动提取source和pic_urls信息
- ✅ 地理位置：完整的geo字段处理
- ✅ 数据清洗：HTML标签清理、特殊字符处理
- ✅ 时间解析：支持多种时间格式
- ✅ 数据验证：完整性检查和格式标准化
- ✅ 平台适配：针对不同平台的数据结构适配

### 系统特性
- ✅ 日志记录：详细的运行日志和错误追踪
- ✅ 进度监控：实时显示爬取进度和统计信息
- ✅ 优雅退出：支持Ctrl+C安全中断
- ✅ 资源管理：自动清理数据库连接等资源

## 📋 支持平台

### 微博平台
支持微博数据采集，包含以下字段：

| 字段名 | 说明 | 状态 |
|--------|------|------|
| _id | 微博ID | ✅ |
| mblogid | 文本ID | ✅ |
| created_at | 创建时间 | ✅ |
| geo:* | 地理位置相关字段 | ✅ |
| ip_location | IP地址 | ✅ |
| reposts_count | 转发数量 | ✅ |
| comments_count | 评论数量 | ✅ |
| attitudes_count | 点赞数量 | ✅ |
| source | 来源（从正文提取） | ✅ |
| content | 正文内容 | ✅ |
| pic_urls | 图片URL（从正文提取） | ✅ |
| pic_num | 图片数量 | ✅ |
| isLongText | 是否长文本 | ✅ |
| user:* | 用户相关字段 | ✅ |
| url | 微博URL | ✅ |
| keyword | 关键词 | ✅ |
| crawl_time | 爬取时间 | ✅ |

### 抖音平台
支持抖音视频数据采集，包含以下字段：

| 字段名 | 说明 | 状态 |
|--------|------|------|
| aweme_id | 抖音视频ID | ✅ |
| desc | 视频描述 | ✅ |
| create_time | 创建时间 | ✅ |
| author | 作者信息 | ✅ |
| statistics | 统计数据（点赞、评论、分享） | ✅ |
| video_urls | 视频链接 | ✅ |
| music | 背景音乐信息 | ✅ |
| hashtags | 话题标签 | ✅ |
| location | 地理位置 | ✅ |
| keyword | 关键词 | ✅ |
| crawl_time | 爬取时间 | ✅ |

## 🛠️ 安装配置

### 1. 环境要求
- Python 3.8+
- MySQL 5.7+
- 网络连接

### 2. 安装依赖
```bash
cd multi_crawler
pip install -r requirements.txt
```

### 3. 数据库配置
编辑 `config/settings.py` 文件，修改数据库配置：

```python
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': '',      # 修改为实际用户名
    'password': '',  # 修改为实际密码
    'database': 'multi_crawler',
    'charset': 'utf8mb4'
}
```

### 4. 爬虫配置
根据需要调整爬虫参数：

```python
# 微博爬虫配置
WEIBO_CONFIG = {
    'keyword': '李雨珊',
    'max_pages': 50,              # 最大爬取页数
    'delay_range': (2, 5),        # 请求间隔（秒）
    'retry_times': 3,             # 重试次数
    'timeout': 30,                # 请求超时时间
    'batch_size': 100,            # 批量插入大小
}

# 抖音爬虫配置
DOUYIN_CONFIG = {
    'keyword': '李雨珊',
    'max_videos': 100,            # 最大爬取视频数
    'delay_range': (3, 6),        # 请求间隔（秒）
    'retry_times': 3,             # 重试次数
    'timeout': 30,                # 请求超时时间
    'batch_size': 50,             # 批量插入大小
}
```

## 🚀 使用方法

### 基本使用
```bash
# 爬取微博数据
cd multi_crawler
python main.py --platform weibo

# 爬取抖音数据
python main.py --platform douyin

# 同时爬取多平台数据
python multi_platform_crawler.py
```

### 高级使用
```python
from multi_platform_crawler import MultiPlatformCrawler

# 创建多平台爬虫实例
crawler = MultiPlatformCrawler()

# 初始化系统
if crawler.initialize():
    # 爬取微博数据
    crawler.crawl_weibo_data(
        keyword="李雨珊事件", 
        max_pages=20
    )
    
    # 爬取抖音数据
    crawler.crawl_douyin_data(
        keyword="李雨珊事件",
        max_videos=50
    )
    
    # 获取统计信息
    stats = crawler.get_statistics()
    print(stats)
    
    # 清理资源
    crawler.cleanup()
```

## 📊 项目结构

```
multi_crawler/
├── config/
│   └── settings.py          # 配置文件
├── database/
│   └── models.py           # 数据库模型
├── crawler/
│   ├── base_spider.py      # 爬虫基类
│   ├── weibo_spider.py     # 微博爬虫
│   └── douyin_spider.py    # 抖音爬虫
├── utils/
│   ├── data_processor.py   # 数据处理
│   ├── helpers.py          # 辅助函数
│   └── logger.py           # 日志配置
├── logs/                   # 日志文件目录
├── data/                   # 数据存储目录
├── main.py                 # 单平台主程序
├── multi_platform_crawler.py  # 多平台主程序
├── requirements.txt        # 依赖包
└── README.md              # 说明文档
```

## 🔧 配置说明

### 代理配置
如需使用代理，修改 `config/settings.py`：

```python
PROXY_CONFIG = {
    'enabled': True,
    'proxies': [
        'http://proxy1:port',
        'http://proxy2:port',
    ]
}
```

### User-Agent池
系统内置多个User-Agent，可在 `USER_AGENTS` 列表中添加更多：

```python
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...',
    # 添加更多User-Agent
]
```

### 平台特定配置
```python
# 微博平台配置
WEIBO_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://weibo.com/',
}

# 抖音平台配置
DOUYIN_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
    'Referer': 'https://www.douyin.com/',
}
```

## 📈 监控和日志

### 日志文件
- 位置：`logs/crawler_YYYYMMDD.log`
- 级别：INFO（控制台）、DEBUG（文件）
- 轮转：10MB自动轮转，保留5个备份

### 统计信息
系统提供详细的统计信息：
- 各平台爬取数量
- 成功保存数量
- 失败数量
- 数据库总量
- 今日爬取量
- 平台分布统计

## ⚠️ 注意事项

### 法律合规
- 请遵守各平台的robots.txt和使用条款
- 合理设置爬取间隔，避免对服务器造成压力
- 仅用于学术研究和数据分析
- 遵守相关法律法规和平台政策

### 技术建议
- 建议使用代理池避免IP被封
- 定期更新User-Agent列表
- 监控爬取成功率，及时调整策略
- 定期备份数据库数据
- 针对不同平台调整爬取策略

### 性能优化
- 调整 `batch_size` 优化数据库插入性能
- 根据网络情况调整 `delay_range`
- 使用SSD存储提高数据库性能
- 合理分配各平台爬取资源

## 🐛 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查MySQL服务是否启动
   - 验证数据库配置信息
   - 确认网络连接正常

2. **爬取无数据**
   - 检查网络连接
   - 验证关键词设置
   - 查看日志文件获取详细错误信息
   - 检查平台API是否有变化

3. **频繁请求失败**
   - 增加请求间隔时间
   - 启用代理池
   - 更新User-Agent列表
   - 检查平台反爬虫策略

4. **抖音数据爬取失败**
   - 检查抖音API接口状态
   - 验证请求头配置
   - 确认移动端模拟是否正确

### 日志分析
查看日志文件了解详细运行情况：
```bash
# 查看实时日志
tail -f logs/crawler_$(date +%Y%m%d).log

# 查看特定平台日志
grep "weibo" logs/crawler_$(date +%Y%m%d).log
grep "douyin" logs/crawler_$(date +%Y%m%d).log
```

## 📞 技术支持

如遇到问题，请：
1. 查看日志文件获取错误详情
2. 检查配置文件设置
3. 确认依赖包版本兼容性
4. 验证数据库连接和权限
5. 检查各平台API状态

## 📄 许可证

本项目仅供学习和研究使用，请遵守相关法律法规和网站使用条款。

---

**免责声明**：本工具仅用于技术学习和数据研究，使用者需自行承担使用风险，并遵守相关法律法规。请合理使用，尊重各平台的服务条款。