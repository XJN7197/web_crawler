"""
测试抖音新URL数据获取功能
验证哪个URL能够成功获取搜索数据
"""
import requests
import json
import time
from config.settings import DOUYIN_API_CONFIG

def test_url_with_search(url, test_name):
    """测试指定URL的搜索功能"""
    print(f"\n{'='*50}")
    print(f"测试 {test_name}")
    print(f"URL: {url}")
    print(f"{'='*50}")
    
    # 构建搜索参数
    params = {
        'keyword': '美食',
        'offset': 0,
        'count': 20,
    }
    
    # 设置请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.douyin.com/',
        'Origin': 'https://www.douyin.com',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"请求URL: {response.url}")
        
        if response.status_code == 200:
            print("✅ 请求成功")
            
            # 尝试解析JSON
            try:
                data = response.json()
                print(f"响应数据类型: {type(data)}")
                
                if isinstance(data, dict):
                    print(f"响应字段: {list(data.keys())}")
                    
                    # 检查是否有数据
                    if 'data' in data:
                        print(f"数据字段类型: {type(data['data'])}")
                        if isinstance(data['data'], list):
                            print(f"数据条数: {len(data['data'])}")
                            if len(data['data']) > 0:
                                print("✅ 成功获取到搜索数据")
                                # 显示第一条数据的结构
                                first_item = data['data'][0]
                                if isinstance(first_item, dict):
                                    print(f"数据项字段: {list(first_item.keys())}")
                                return True
                            else:
                                print("⚠️ 数据列表为空")
                        elif isinstance(data['data'], dict):
                            print(f"数据对象字段: {list(data['data'].keys())}")
                            return True
                    else:
                        print("⚠️ 响应中没有'data'字段")
                        # 显示实际的响应结构
                        print(f"实际响应内容: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}...")
                
            except json.JSONDecodeError:
                print("❌ 响应不是有效的JSON格式")
                print(f"响应内容前500字符: {response.text[:500]}")
                
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text[:300]}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    return False

def test_douyin_web_search():
    """测试抖音网页版搜索"""
    print(f"\n{'='*50}")
    print("测试抖音网页版搜索")
    print(f"{'='*50}")
    
    url = 'https://www.douyin.com/search/'
    params = {
        'keyword': '美食',
        'type': 'general'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': 'https://www.douyin.com/',
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"请求URL: {response.url}")
        
        if response.status_code == 200:
            print("✅ 网页请求成功")
            print(f"响应内容长度: {len(response.text)}")
            
            # 检查是否包含搜索结果
            if '美食' in response.text:
                print("✅ 网页包含搜索关键词")
            
            # 检查是否有视频数据
            if 'video' in response.text.lower() or 'aweme' in response.text.lower():
                print("✅ 网页可能包含视频数据")
                return True
            else:
                print("⚠️ 网页可能不包含视频数据")
        else:
            print(f"❌ 网页请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 网页请求异常: {e}")
    
    return False

def main():
    """主测试函数"""
    print("开始测试抖音新URL数据获取功能...")
    
    # 测试的URL列表
    test_urls = [
        ('https://www.douyin.com/aweme/v1/web/search/item/', 'API搜索接口1'),
        ('https://www.douyin.com/aweme/v1/web/general/search/single/', 'API搜索接口2'),
        ('https://www.iesdouyin.com/web/api/v2/search/item/', 'API搜索接口3'),
    ]
    
    successful_urls = []
    
    # 测试API接口
    for url, name in test_urls:
        if test_url_with_search(url, name):
            successful_urls.append((url, name))
        time.sleep(1)  # 避免请求过快
    
    # 测试网页版搜索
    if test_douyin_web_search():
        successful_urls.append(('https://www.douyin.com/search/', '网页版搜索'))
    
    # 总结结果
    print(f"\n{'='*60}")
    print("测试结果总结")
    print(f"{'='*60}")
    
    if successful_urls:
        print("✅ 以下URL可以获取数据:")
        for url, name in successful_urls:
            print(f"  - {name}: {url}")
        
        print(f"\n推荐使用: {successful_urls[0][1]} ({successful_urls[0][0]})")
    else:
        print("❌ 所有测试的URL都无法获取到有效数据")
        print("建议:")
        print("1. 检查网络连接")
        print("2. 尝试添加有效的Cookie")
        print("3. 考虑使用Selenium等浏览器自动化工具")
    
    print(f"{'='*60}")

if __name__ == "__main__":
    main()