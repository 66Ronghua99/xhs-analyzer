#!/usr/bin/env python3
"""
小红书直接数据采集器 - 使用 Selenium + Chrome Driver
绕过API限制直接获取页面内容
"""

import json
import time
import re
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class XHSNote:
    """小红书笔记数据模型"""
    title: str
    content: str
    author: str
    likes: int
    url: str
    note_id: str
    
def scrape_xhs_search(keyword: str, max_results: int = 20) -> List[XHSNote]:
    """
    搜索小红书笔记
    注意：这需要本地安装 Chrome 和 ChromeDriver
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
    except ImportError:
        print("[ERROR] 需要安装 selenium: pip3 install selenium")
        return []
    
    notes = []
    driver = None
    
    try:
        # 配置 Chrome 选项
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 无头模式
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # 尝试启动 Chrome
        try:
            driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(f"[ERROR] Chrome 启动失败: {e}")
            print("[INFO] 尝试使用 ChromeDriver...")
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
            except:
                print("[ERROR] 无法启动浏览器，请确保 Chrome 已安装")
                return []
        
        # 访问搜索页面
        search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}&type=51"
        print(f"[INFO] 访问: {search_url}")
        driver.get(search_url)
        
        # 等待页面加载
        time.sleep(5)
        
        # 尝试获取笔记数据
        # 小红书是SPA，需要等待JS渲染
        try:
            # 等待笔记卡片出现
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='note']"))
            )
        except:
            print("[WARN] 等待笔记元素超时")
        
        # 获取页面源码并解析
        page_source = driver.page_source
        
        # 尝试从页面中提取JSON数据
        json_patterns = [
            r'window\.__INITIAL_STATE__\s*=\s*({.+?});',
            r'<script[^>]*>.*?window\._SSR_HYDRATED_DATA\s*=\s*({.+?});.*?</script>',
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, page_source, re.DOTALL)
            if matches:
                try:
                    data = json.loads(matches[0])
                    print(f"[INFO] 找到JSON数据: {len(str(data))} 字符")
                    # 解析笔记数据...
                    break
                except:
                    pass
        
        # 备用：从HTML中解析可见内容
        if not notes:
            print("[INFO] 尝试从HTML解析可见内容...")
            # 提取标题
            title_patterns = [
                r'<a[^>]*title="([^"]+)"',
                r'<div[^>]*class="[^"]*title[^"]*"[^>]*>([^<]+)',
            ]
            for pattern in title_patterns:
                matches = re.findall(pattern, page_source)
                for match in matches[:max_results]:
                    if len(match) > 5:  # 过滤掉太短的内容
                        notes.append(XHSNote(
                            title=match.strip(),
                            content="",
                            author="",
                            likes=0,
                            url="",
                            note_id=""
                        ))
        
    except Exception as e:
        print(f"[ERROR] 爬取过程出错: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
    
    return notes


def main():
    """测试函数"""
    print("="*60)
    print("小红书数据采集器")
    print("="*60)
    
    # 检查依赖
    try:
        from selenium import webdriver
        print("[OK] Selenium 已安装")
    except ImportError:
        print("[ERROR] 需要安装 Selenium:")
        print("  pip3 install selenium")
        print("  pip3 install webdriver-manager")
        return
    
    # 检查 Chrome
    import subprocess
    try:
        result = subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'], 
                              capture_output=True, text=True)
        print(f"[OK] Chrome 版本: {result.stdout.strip()}")
    except:
        print("[WARN] Chrome 可能未安装或路径不对")
    
    # 搜索测试
    keyword = "第四种黑猩猩"
    print(f"\n[开始搜索] {keyword}")
    print("-"*60)
    
    notes = scrape_xhs_search(keyword, max_results=10)
    
    print("\n" + "="*60)
    print("搜索结果:")
    print("="*60)
    
    if notes:
        for i, note in enumerate(notes[:10], 1):
            print(f"\n{i}. {note.title}")
            if note.content:
                print(f"   内容: {note.content[:100]}...")
    else:
        print("[无结果] 可能需要登录或验证码")
    
    # 保存结果
    if notes:
        output_file = f"xhs_search_{keyword}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump([{
                'title': n.title,
                'content': n.content,
                'author': n.author,
                'likes': n.likes,
                'url': n.url
            } for n in notes], f, ensure_ascii=False, indent=2)
        print(f"\n[已保存] {output_file}")


if __name__ == "__main__":
    main()
