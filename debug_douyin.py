"""
抖音爬虫问题诊断脚本
用于验证抖音API访问问题的根本原因
"""
import requests
import json
from config.settings import DOUYIN_URLS, DOUYIN_API_CONFIG

def test_douyin_url_access():
    """测试抖音URL访问"""
    print("="*60)
    print("抖音URL访问测试")
    print("="*60)
    
    search_url = DOUYIN_URLS['search_url']
    print(f"测试URL: {search_url}")
    
    # 测试基本访问
    try:
        response = requests.get(search_url, timeout=10)
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 404:
            print("❌ URL返回404，可能已失效")
        elif response.status_code == 403:
            print("❌ 访问被禁止，可能需要认证")
        elif response.status_code == 200:
            print("✅ URL可访问")
            print(f"响应内容长度: {len(response.text)}")
        else:
            print(f"⚠️ 异常状态码: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def test_douyin_search_with_params():
    """测试带参数的抖音搜索"""
    print("\n" + "="*60)
    print("抖音搜索参数测试")
    print("="*60)
    
    search_url = DOUYIN_URLS['search_url']
    
    # 构建基本搜索参数
    params = {
        'device_platform': DOUYIN_API_CONFIG['device_platform'],
        'aid': DOUYIN_API_CONFIG['aid'],
        'channel': DOUYIN_API_CONFIG['channel'],
        'keyword': '李雨珊',
        'search_source': 'normal_search',
        'offset': 0,
        'count': 20,
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': 'https://www.douyin.com/',
        'Origin': 'https://www.douyin.com',
    }
    
    try:
        response = requests.get(search_url, params=params, headers=headers, timeout=10)
        print(f"请求URL: {response.url}")
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 搜索请求成功")
            try:
                data = response.json()
                print(f"响应数据类型: {type(data)}")
                if isinstance(data, dict):
                    print(f"响应字段: {list(data.keys())}")
                    print(f"status_code: {data.get('status_code')}")
                    print(f"status_msg: {data.get('status_msg')}")
                    
                    # 显示更多详细信息
                    if 'data' in data:
                        print(f"data字段类型: {type(data['data'])}")
                        if isinstance(data['data'], list):
                            print(f"data列表长度: {len(data['data'])}")
                        else:
                            print(f"data字段内容: {data['data']}")
                    
                    # 保存响应数据到文件以便分析
                    with open('douyin_response_debug.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    print("响应数据已保存到 douyin_response_debug.json")
            except Exception as e:
                print(f"JSON解析失败: {e}")
                print(f"响应内容前500字符: {response.text[:500]}")
        else:
            print(f"❌ 搜索请求失败: {response.status_code}")
            print(f"响应内容: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ 搜索请求异常: {e}")

def test_alternative_douyin_urls():
    """测试替代的抖音URL"""
    print("\n" + "="*60)
    print("替代抖音URL测试")
    print("="*60)
    
    alternative_urls = [
        'https://www.douyin.com/search/',
        'https://www.douyin.com/aweme/v1/web/general/search/single/',
        'https://www.douyin.com/aweme/v1/web/search/item/',
        'https://www.iesdouyin.com/web/api/v2/search/item/',
    ]
    
    for url in alternative_urls:
        print(f"\n测试URL: {url}")
        try:
            response = requests.get(url, timeout=5)
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                print("✅ 可访问")
            elif response.status_code == 404:
                print("❌ 404 - URL不存在")
            elif response.status_code == 403:
                print("⚠️ 403 - 访问被禁止")
            else:
                print(f"⚠️ 状态码: {response.status_code}")
        except Exception as e:
            print(f"❌ 请求失败: {e}")

def main():
    """主诊断函数"""
    print("开始抖音爬虫问题诊断...")
    
    # 测试基本URL访问
    test_douyin_url_access()
    
    # 测试带参数的搜索
    test_douyin_search_with_params()
    
    # 测试替代URL
    test_alternative_douyin_urls()
    
    print("\n" + "="*60)
    print("诊断建议:")
    print("1. 如果所有URL都返回404，说明抖音API已更新")
    print("2. 如果返回403，说明需要有效的Cookie和认证")
    print("3. 如果返回200但无数据，说明需要正确的签名算法")
    print("4. 建议使用抖音网页版搜索接口作为替代方案")
    print("="*60)

if __name__ == "__main__":
    main()