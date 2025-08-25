#!/usr/bin/env python3
"""
测试移动端抖音API - 验证是否能避免Cookie问题获取真实数据
"""

import requests
import json
import time
import hashlib
import random
from typing import Dict, Any

class MobileDouyinTester:
    """移动端抖音API测试器"""
    
    def __init__(self):
        self.session = requests.Session()
        
        # 移动端请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://m.douyin.com/',
            'Origin': 'https://m.douyin.com',
            'X-Requested-With': 'XMLHttpRequest',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        })
    
    def _generate_ms_token(self) -> str:
        """生成移动端ms_token"""
        timestamp = str(int(time.time() * 1000))
        random_str = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=16))
        token_base = f"{timestamp}_{random_str}"
        return hashlib.md5(token_base.encode()).hexdigest()
    
    def _generate_verify_fp(self) -> str:
        """生成设备指纹"""
        device_info = f"mobile_{int(time.time())}"
        return hashlib.md5(device_info.encode()).hexdigest()[:16]
    
    def build_mobile_params(self, keyword: str) -> Dict[str, Any]:
        """构建移动端搜索参数"""
        return {
            'keyword': keyword,
            'offset': 0,
            'count': 10,
            'device_platform': 'webapp',
            'aid': '6383',
            'channel': 'channel_pc_web',
            'search_source': 'normal_search',
            'query_correct_type': '1',
            'is_filter_search': '0',
            'sort_type': '0',
            'publish_time': '0',
            'version_code': '160100',
            'version_name': '16.1.0',
            'screen_width': '375',
            'screen_height': '812',
            'dpr': '2',
            'ts': int(time.time()),
            'ms_token': self._generate_ms_token(),
            'verifyFp': self._generate_verify_fp(),
        }
    
    def test_mobile_apis(self, keyword: str = "测试"):
        """测试多个移动端API接口"""
        
        # 测试的API接口列表
        test_urls = [
            'https://m.douyin.com/web/api/v2/search/item/',
            'https://www.douyin.com/aweme/v1/web/general/search/single/',
            'https://www.douyin.com/aweme/v1/web/search/item/',
        ]
        
        params = self.build_mobile_params(keyword)
        
        print("=" * 60)
        print(f"测试移动端抖音API - 关键词: {keyword}")
        print("=" * 60)
        
        for i, url in enumerate(test_urls, 1):
            print(f"\n{i}. 测试接口: {url}")
            print("-" * 50)
            
            try:
                response = self.session.get(url, params=params, timeout=10)
                
                print(f"状态码: {response.status_code}")
                print(f"响应头: {dict(response.headers)}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"JSON响应成功: {len(str(data))} 字符")
                        
                        # 检查是否包含视频数据
                        if 'data' in data and isinstance(data['data'], list) and len(data['data']) > 0:
                            print(f"✅ 成功获取到 {len(data['data'])} 条数据")
                            
                            # 显示第一条数据的基本信息
                            first_item = data['data'][0]
                            if 'aweme_info' in first_item:
                                aweme = first_item['aweme_info']
                                print(f"   视频ID: {aweme.get('aweme_id', 'N/A')}")
                                print(f"   描述: {aweme.get('desc', 'N/A')[:50]}...")
                                print(f"   作者: {aweme.get('author', {}).get('nickname', 'N/A')}")
                            
                            return True, url, data
                        else:
                            print("❌ 响应格式正确但无数据")
                            
                    except json.JSONDecodeError:
                        print(f"❌ JSON解析失败")
                        print(f"响应内容前500字符: {response.text[:500]}")
                else:
                    print(f"❌ HTTP错误: {response.status_code}")
                    print(f"响应内容: {response.text[:200]}")
                    
            except Exception as e:
                print(f"❌ 请求异常: {e}")
        
        print("\n" + "=" * 60)
        print("所有接口测试完成，未获取到真实数据")
        print("=" * 60)
        return False, None, None

def main():
    """主测试函数"""
    tester = MobileDouyinTester()
    
    # 测试不同关键词
    test_keywords = ["美食", "旅行", "科技"]
    
    for keyword in test_keywords:
        success, url, data = tester.test_mobile_apis(keyword)
        if success:
            print(f"\n🎉 成功！使用关键词 '{keyword}' 在接口 {url} 获取到真实数据")
            break
        time.sleep(2)  # 避免请求过快
    else:
        print("\n❌ 所有测试均失败，可能需要其他解决方案")

if __name__ == "__main__":
    main()