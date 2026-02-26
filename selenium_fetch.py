#!/usr/bin/env python3
"""
使用 Selenium + Cookie 访问小红书
"""

import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Cookie 字符串
COOKIE_STR = "abRequestId=7995c002-8687-5c1d-bb07-054d8695770b; webBuild=5.11.0; xsecappid=xhs-pc-web; a1=19c9446615crmfmcv4lnzb1jxt7osts5j8c0nf3zb30000194232; webId=8deb36d1e37491ecff8fd507cde31a7c; gid=yjSj44K0KYVWyjSj44KKyYiq2SF6i6Sh41IuSuDDyVC9W8q8lM9M2I888yj4JqJ8KYfqdDY2; websectiga=8886be45f388a1ee7bf611a69f3e174cae48f1ea02c0f8ec3256031b8be9c7ee; sec_poison_id=f4aada0b-b611-4c2b-9a56-7e376adb19eb; loadts=1772071342715; unread={%22ub%22:%2269992032000000000c037f88%22%2C%22ue%22:%22699723e80000000016009f6b%22%2C%22uc%22:29}"

def parse_cookie_string(cookie_str):
    """解析 Cookie 字符串"""
    cookies = []
    for item in cookie_str.split(';'):
        item = item.strip()
        if '=' in item:
            name, value = item.split('=', 1)
            cookies.append({'name': name, 'value': value})
    return cookies

def fetch_xhs_data(keyword):
    """获取小红书数据"""
    print(f"[INFO] 开始采集关键词: {keyword}")
    
    # 配置 Chrome
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 无头模式
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = None
    results = {'keyword': keyword, 'users': [], 'notes': []}
    
    try:
        print("[INFO] 启动 Chrome...")
        driver = webdriver.Chrome(options=chrome_options)
        
        # 先访问小红书主页设置 Cookie
        print("[INFO] 设置 Cookie...")
        driver.get("https://www.xiaohongshu.com")
        time.sleep(2)
        
        # 添加 Cookie
        cookies = parse_cookie_string(COOKIE_STR)
        for cookie in cookies:
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                print(f"[WARN] 添加 Cookie 失败 {cookie['name']}: {e}")
        
        # 刷新页面使 Cookie 生效
        driver.refresh()
        time.sleep(3)
        
        # 访问搜索页面
        search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}&type=51"
        print(f"[INFO] 访问搜索页面: {search_url}")
        driver.get(search_url)
        time.sleep(5)
        
        # 获取页面源码
        page_source = driver.page_source
        print(f"[INFO] 页面源码长度: {len(page_source)} 字符")
        
        # 尝试提取 JSON 数据
        import re
        json_match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.+?});', page_source, re.DOTALL)
        if json_match:
            try:
                initial_state = json.loads(json_match.group(1))
                print(f"[INFO] 找到初始状态数据")
                
                # 提取搜索结果
                if 'search' in initial_state:
                    search_data = initial_state['search']
                    print(f"[INFO] 搜索数据类型: {type(search_data)}")
                    
                    # 尝试提取用户列表
                    if isinstance(search_data, dict):
                        if 'users' in search_data:
                            for user in search_data['users']:
                                results['users'].append({
                                    'nickname': user.get('nickname', ''),
                                    'user_id': user.get('userId', ''),
                                    'desc': user.get('desc', ''),
                                    'fans': user.get('fans', 0),
                                })
                        
                        # 尝试提取笔记列表
                        if 'notes' in search_data:
                            for note in search_data['notes']:
                                results['notes'].append({
                                    'title': note.get('title', ''),
                                    'note_id': note.get('noteId', ''),
                                    'likes': note.get('likes', 0),
                                    'author': note.get('user', {}).get('nickname', ''),
                                })
            except Exception as e:
                print(f"[ERROR] 解析 JSON 失败: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("[WARN] 未找到 window.__INITIAL_STATE__")
            
        # 保存页面源码用于调试
        with open('debug_page.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print("[INFO] 页面源码已保存到 debug_page.html")
        
    except Exception as e:
        print(f"[ERROR] 采集过程出错: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
        
        # 保存结果
        output_file = 'xhs_real_results.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n[INFO] 结果已保存到 {output_file}")
    
    return results


if __name__ == "__main__":
    print("="*60)
    print("小红书真实数据采集器 (Selenium 版)")
    print("="*60)
    
    # 采集数据
    keyword = "第四种黑猩猩"
    results = fetch_xhs_data(keyword)
    
    # 显示结果
    print("\n" + "="*60)
    print("采集结果")
    print("="*60)
    print(f"\n关键词: {results['keyword']}")
    print(f"找到用户: {len(results['users'])} 个")
    print(f"找到笔记: {len(results['notes'])} 篇")
    
    if results['users']:
        print("\n用户列表:")
        for i, user in enumerate(results['users'][:5], 1):
            print(f"{i}. {user['nickname']} (粉丝: {user['fans']})")
    
    if results['notes']:
        print("\n笔记列表:")
        for i, note in enumerate(results['notes'][:5], 1):
            print(f"{i}. {note['title'] or '无标题'} (点赞: {note['likes']})")
