"""
简单的抖音URL测试
快速验证哪个URL可用
"""
import requests
import json

def quick_test():
    """快速测试抖音URL"""
    urls_to_test = [
        'https://www.douyin.com/aweme/v1/web/search/item/',
        'https://www.douyin.com/aweme/v1/web/general/search/single/',
        'https://www.iesdouyin.com/web/api/v2/search/item/',
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://www.douyin.com/',
    }
    
    params = {
        'keyword': '美食',
        'count': 10,
        'offset': 0
    }
    
    for i, url in enumerate(urls_to_test, 1):
        print(f"\n{i}. 测试: {url}")
        try:
            response = requests.get(url, params=params, headers=headers, timeout=5)
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ JSON解析成功")
                    print(f"   响应字段: {list(data.keys()) if isinstance(data, dict) else 'Not dict'}")
                    
                    # 检查是否有数据
                    if isinstance(data, dict) and 'data' in data:
                        data_content = data['data']
                        if isinstance(data_content, list) and len(data_content) > 0:
                            print(f"   ✅ 找到 {len(data_content)} 条数据")
                            return url, True
                        elif isinstance(data_content, dict):
                            print(f"   ✅ 找到数据对象")
                            return url, True
                        else:
                            print(f"   ⚠️ 数据为空")
                    else:
                        print(f"   ⚠️ 无'data'字段")
                        
                except json.JSONDecodeError:
                    print(f"   ❌ 非JSON响应")
                    print(f"   响应内容: {response.text[:100]}...")
            else:
                print(f"   ❌ 状态码: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 请求失败: {e}")
    
    return None, False

if __name__ == "__main__":
    print("快速测试抖音API...")
    url, success = quick_test()
    
    if success:
        print(f"\n🎉 找到可用的URL: {url}")
    else:
        print(f"\n❌ 所有URL都无法获取数据")
        print("可能的原因:")
        print("1. 需要有效的Cookie")
        print("2. 需要特殊的签名参数")
        print("3. IP被限制")
        print("4. API需要登录状态")