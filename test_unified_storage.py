#!/usr/bin/env python3
"""
测试统一数据保存逻辑
验证新的文件夹结构和命名规范
"""
import os
import sys
import json
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_storage_manager import DataStorageManager

def test_unified_storage_structure():
    """测试统一的数据存储结构"""
    print("🧪 开始测试统一数据存储逻辑...")
    
    # 创建测试数据存储管理器
    test_data_dir = "test_data"
    storage_manager = DataStorageManager(test_data_dir)
    
    # 测试数据
    test_weibo_data = [
        {
            "_id": "test_weibo_001",
            "content": "这是一条测试微博数据",
            "user_name": "测试用户1",
            "created_at": datetime.now().isoformat(),
            "platform": "weibo"
        },
        {
            "_id": "test_weibo_002", 
            "content": "这是另一条测试微博数据",
            "user_name": "测试用户2",
            "created_at": datetime.now().isoformat(),
            "platform": "weibo"
        }
    ]
    
    test_douyin_data = [
        {
            "_id": "test_douyin_001",
            "content": "这是一条测试抖音数据",
            "user_name": "测试用户3",
            "created_at": datetime.now().isoformat(),
            "platform": "douyin"
        },
        {
            "_id": "test_douyin_002",
            "content": "这是另一条测试抖音数据", 
            "user_name": "测试用户4",
            "created_at": datetime.now().isoformat(),
            "platform": "douyin"
        }
    ]
    
    # 测试微博数据保存
    print("\n📁 测试微博数据保存...")
    weibo_session_dir = storage_manager.create_session_directory("测试关键词", "weibo")
    if weibo_session_dir:
        print(f"✅ 微博会话目录创建成功: {weibo_session_dir}")
        
        # 保存原始数据
        success = storage_manager.save_raw_data(test_weibo_data, 1, "weibo_mobile", "weibo")
        if success:
            print("✅ 微博原始数据保存成功")
        
        # 保存结构化数据
        success = storage_manager.save_structured_data(test_weibo_data, platform="weibo")
        if success:
            print("✅ 微博结构化数据保存成功")
        
        # 保存会话元数据
        metadata = {
            "platform": "weibo",
            "keyword": "测试关键词",
            "test_mode": True,
            "data_count": len(test_weibo_data)
        }
        success = storage_manager.save_session_metadata(metadata)
        if success:
            print("✅ 微博会话元数据保存成功")
    else:
        print("❌ 微博会话目录创建失败")
    
    # 测试抖音数据保存
    print("\n📁 测试抖音数据保存...")
    storage_manager_douyin = DataStorageManager(test_data_dir)
    douyin_session_dir = storage_manager_douyin.create_session_directory("测试关键词", "douyin")
    if douyin_session_dir:
        print(f"✅ 抖音会话目录创建成功: {douyin_session_dir}")
        
        # 保存原始数据
        success = storage_manager_douyin.save_raw_data(test_douyin_data, 1, "douyin_data", "douyin")
        if success:
            print("✅ 抖音原始数据保存成功")
        
        # 保存结构化数据
        success = storage_manager_douyin.save_structured_data(test_douyin_data, platform="douyin")
        if success:
            print("✅ 抖音结构化数据保存成功")
        
        # 保存会话元数据
        metadata = {
            "platform": "douyin",
            "keyword": "测试关键词",
            "test_mode": True,
            "data_count": len(test_douyin_data)
        }
        success = storage_manager_douyin.save_session_metadata(metadata)
        if success:
            print("✅ 抖音会话元数据保存成功")
    else:
        print("❌ 抖音会话目录创建失败")
    
    # 验证文件夹结构
    print("\n🔍 验证文件夹结构...")
    test_data_path = Path(test_data_dir)
    if test_data_path.exists():
        print(f"📂 测试数据目录: {test_data_path}")
        
        # 列出所有一级目录（时间戳+平台名称）
        level1_dirs = [d for d in test_data_path.iterdir() if d.is_dir()]
        for level1_dir in level1_dirs:
            print(f"  📁 一级目录: {level1_dir.name}")
            
            # 列出二级目录（时间戳+平台名称+关键词）
            level2_dirs = [d for d in level1_dir.iterdir() if d.is_dir()]
            for level2_dir in level2_dirs:
                print(f"    📁 二级目录: {level2_dir.name}")
                
                # 检查子目录结构
                subdirs = ["raw_data", "structured_data", "analysis_report"]
                for subdir in subdirs:
                    subdir_path = level2_dir / subdir
                    if subdir_path.exists():
                        print(f"      ✅ {subdir}/ 目录存在")
                        
                        # 列出文件
                        files = list(subdir_path.glob("*.json"))
                        for file in files:
                            print(f"        📄 {file.name}")
                    else:
                        print(f"      ❌ {subdir}/ 目录不存在")
                
                # 检查元数据文件
                metadata_file = level2_dir / "session_metadata.json"
                if metadata_file.exists():
                    print(f"      ✅ session_metadata.json 存在")
                else:
                    print(f"      ❌ session_metadata.json 不存在")
    
    print("\n🎉 统一数据存储逻辑测试完成！")
    print("\n📋 新的文件夹结构说明:")
    print("data/")
    print("├── YYYYMMDD_weibo/                    # 一级：日期+平台名称")
    print("│   └── YYYYMMDD_HHMMSS_weibo_关键词/  # 二级：时间戳+平台名称+关键词")
    print("│       ├── raw_data/")
    print("│       │   └── weibo_raw_page_001.json")
    print("│       ├── structured_data/")
    print("│       │   └── weibo_structured_data_YYYYMMDD_HHMMSS.json")
    print("│       ├── analysis_report/")
    print("│       │   └── weibo_analysis_report_YYYYMMDD_HHMMSS.json")
    print("│       └── session_metadata.json")
    print("├── YYYYMMDD_douyin/                   # 一级：日期+平台名称")
    print("│   └── YYYYMMDD_HHMMSS_douyin_关键词/ # 二级：时间戳+平台名称+关键词")
    print("│       ├── raw_data/")
    print("│       │   └── douyin_raw_page_001.json")
    print("│       ├── structured_data/")
    print("│       │   └── douyin_structured_data_YYYYMMDD_HHMMSS.json")
    print("│       └── session_metadata.json")

def cleanup_test_data():
    """清理测试数据"""
    import shutil
    test_data_dir = "test_data"
    if os.path.exists(test_data_dir):
        try:
            shutil.rmtree(test_data_dir)
            print(f"🧹 清理测试数据目录: {test_data_dir}")
        except Exception as e:
            print(f"❌ 清理测试数据失败: {e}")

if __name__ == "__main__":
    try:
        test_unified_storage_structure()
        
        # 询问是否清理测试数据
        response = input("\n是否清理测试数据？(y/N): ").strip().lower()
        if response in ['y', 'yes']:
            cleanup_test_data()
        else:
            print("保留测试数据，可手动查看 test_data/ 目录")
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()