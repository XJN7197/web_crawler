# 微博爬虫系统 - "李雨珊事件"数据采集

一个完整的Python微博爬虫系统，专门用于爬取"李雨珊事件"相关的微博传播数据，并将数据存储到MySQL数据库中。

## 🚀 功能特性

### 核心功能
- ✅ 多种爬取方式：支持PC端和移动端API爬取
- ✅ 智能反爬虫：User-Agent轮换、随机延迟、代理池支持
- ✅ 数据去重：基于微博ID的增量爬取机制
- ✅ 批量处理：高效的批量数据库插入
- ✅ 错误重试：自动重试机制，提高爬取成功率

### 数据处理
- ✅ 内容解析：自动提取source和pic_urls信息
- ✅ 地理位置：完整的geo字段处理
- ✅ 数据清洗：HTML标签清理、特殊字符处理
- ✅ 时间解析：支持多种微博时间格式
- ✅ 数据验证：完整性检查和格式标准化

### 系统特性
- ✅ 日志记录：详细的运行日志和错误追踪
- ✅ 进度监控：实时显示爬取进度和统计信息
- ✅ 优雅退出：支持Ctrl+C安全中断
- ✅ 资源管理：自动清理数据库连接等资源

## 📋 数据字段

根据提供的数据字段说明表，系统支持以下字段：

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

## 🛠️ 安装配置

### 1. 环境要求
- Python 3.8+
- MySQL 5.7+
- 网络连接

### 2. 安装依赖
```bash
cd weibo_crawler
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
    'database': 'weibo_crawler',
    'charset': 'utf8mb4'
}
```

### 4. 爬虫配置
根据需要调整爬虫参数：

```python
CRAWLER_CONFIG = {
    'keyword': '李雨珊',
    'max_pages': 50,              # 最大爬取页数
    'delay_range': (2, 5),        # 请求间隔（秒）
    'retry_times': 3,             # 重试次数
    'timeout': 30,                # 请求超时时间
    'batch_size': 100,            # 批量插入大小
}
```

## 🚀 使用方法

### 基本使用
```bash
cd weibo_crawler
python main.py
```

### 高级使用
```python
from main import WeiboDataCrawler

# 创建爬虫实例
crawler = WeiboDataCrawler()

# 初始化系统
if crawler.initialize():
    # 开始爬取（自定义参数）
    crawler.crawl_weibo_data(
        keyword="李雨珊事件", 
        max_pages=20
    )
    
    # 获取统计信息
    stats = crawler.get_statistics()
    print(stats)
    
    # 清理资源
    crawler.cleanup()
```

## 📊 项目结构

```
weibo_crawler/
├── config/
│   └── settings.py          # 配置文件
├── database/
│   └── models.py           # 数据库模型
├── crawler/
│   └── weibo_spider.py     # 爬虫核心
├── utils/
│   ├── data_processor.py   # 数据处理
│   ├── helpers.py          # 辅助函数
│   └── logger.py           # 日志配置
├── logs/                   # 日志文件目录
├── data/                   # 数据存储目录
├── main.py                 # 主程序
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

## 📈 监控和日志

### 日志文件
- 位置：`logs/crawler_YYYYMMDD.log`
- 级别：INFO（控制台）、DEBUG（文件）
- 轮转：10MB自动轮转，保留5个备份

### 统计信息
系统提供详细的统计信息：
- 本次爬取数量
- 成功保存数量
- 失败数量
- 数据库总量
- 今日爬取量

## ⚠️ 注意事项

### 法律合规
- 请遵守微博的robots.txt和使用条款
- 合理设置爬取间隔，避免对服务器造成压力
- 仅用于学术研究和数据分析

### 技术建议
- 建议使用代理池避免IP被封
- 定期更新User-Agent列表
- 监控爬取成功率，及时调整策略
- 定期备份数据库数据

### 性能优化
- 调整 `batch_size` 优化数据库插入性能
- 根据网络情况调整 `delay_range`
- 使用SSD存储提高数据库性能

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

3. **频繁请求失败**
   - 增加请求间隔时间
   - 启用代理池
   - 更新User-Agent列表

### 日志分析
查看日志文件了解详细运行情况：
```bash
tail -f logs/crawler_$(date +%Y%m%d).log
```

## 📞 技术支持

如遇到问题，请：
1. 查看日志文件获取错误详情
2. 检查配置文件设置
3. 确认依赖包版本兼容性
4. 验证数据库连接和权限

## 📄 许可证

本项目仅供学习和研究使用，请遵守相关法律法规和网站使用条款。

---

**免责声明**：本工具仅用于技术学习和数据研究，使用者需自行承担使用风险，并遵守相关法律法规。