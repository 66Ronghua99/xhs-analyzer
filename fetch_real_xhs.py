#!/usr/bin/env python3
"""
使用真实Cookie获取小红书数据
"""

import json
import time
import re
import http.client
import urllib.parse
from typing import List, Dict, Optional

# 用户提供的 Cookie
COOKIE = "abRequestId=7995c002-8687-5c1d-bb07-054d8695770b; webBuild=5.11.0; xsecappid=xhs-pc-web; a1=19c9446615crmfmcv4lnzb1jxt7osts5j8c0nf3zb30000194232; webId=8deb36d1e37491ecff8fd507cde31a7c; gid=yjSj44K0KYVWyjSj44KKyYiq2SF6i6Sh41IuSuDDyVC9W8q8lM9M2I888yj4JqJ8KYfqdDY2; websectiga=8886be45f388a1ee7bf611a69f3e174cae48f1ea02c0f8ec3256031b8be9c7ee; sec_poison_id=f4aada0b-b611-4c2b-9a56-7e376adb19eb; loadts=1772071342715; unread={%22ub%22:%2269992032000000000c037f88%22%2C%22ue%22:%22699723e80000000016009f6b%22%2C%22uc%22:29}"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Cookie': COOKIE,
    'Referer': 'https://www.xiaohongshu.com/'
}


def search_users(keyword: str) -> List[Dict]:
    """搜索用户"""
    print(f"[INFO] 搜索用户: {keyword}")
    
    # 尝试访问搜索页面
    search_url = f"/search_result?keyword={urllib.parse.quote(keyword)}&type=user"
    
    try:
        conn = http.client.HTTPSConnection("www.xiaohongshu.com", timeout=15)
        conn.request("GET", search_url, headers=HEADERS)
        response = conn.getresponse()
        data = response.read().decode('utf-8')
        conn.close()
        
        # 尝试提取 JSON 数据
        # 小红书通常在 window.__INITIAL_STATE__ 中存储数据
        json_match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.+?});', data, re.DOTALL)
        if json_match:
            try:
                initial_state = json.loads(json_match.group(1))
                print(f"[INFO] 找到初始数据，大小: {len(str(initial_state))} 字符")
                # 提取用户数据...
                return extract_users_from_state(initial_state)
            except Exception as e:
                print(f"[ERROR] 解析 JSON 失败: {e}")
        
        # 备用：从 HTML 中提取可见文本
        print(f"[INFO] 未找到 JSON 数据，返回 HTML 长度: {len(data)} 字符")
        return []
        
    except Exception as e:
        print(f"[ERROR] 请求失败: {e}")
        return []


def extract_users_from_state(state: Dict) -> List[Dict]:
    """从初始状态中提取用户数据"""
    users = []
    
    # 尝试不同的路径结构
    # 小红书的结构可能会变化
    try:
        # 搜索用户的结果通常在 search 或 user 字段
        if 'search' in state:
            search_data = state['search']
            if 'users' in search_data:
                for user in search_data['users']:
                    users.append({
                        'nickname': user.get('nickname', ''),
                        'user_id': user.get('userId', ''),
                        'avatar': user.get('avatar', ''),
                        'desc': user.get('desc', ''),
                        'follows': user.get('follows', 0),
                        'fans': user.get('fans', 0),
                    })
    except Exception as e:
        print(f"[ERROR] 提取用户数据失败: {e}")
    
    return users


def get_user_notes(user_id: str, max_notes: int = 20) -> List[Dict]:
    """获取用户的笔记"""
    print(f"[INFO] 获取用户 {user_id} 的笔记")
    
    # 尝试访问用户主页
    user_url = f"/user/profile/{user_id}"
    
    try:
        conn = http.client.HTTPSConnection("www.xiaohongshu.com", timeout=15)
        conn.request("GET", user_url, headers=HEADERS)
        response = conn.getresponse()
        data = response.read().decode('utf-8')
        conn.close()
        
        # 尝试提取笔记数据
        json_match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.+?});', data, re.DOTALL)
        if json_match:
            try:
                initial_state = json.loads(json_match.group(1))
                print(f"[INFO] 找到用户数据")
                return extract_notes_from_state(initial_state)
            except Exception as e:
                print(f"[ERROR] 解析失败: {e}")
        
        return []
        
    except Exception as e:
        print(f"[ERROR] 请求失败: {e}")
        return []


def extract_notes_from_state(state: Dict) -> List[Dict]:
    """从状态中提取笔记数据"""
    notes = []
    
    try:
        # 笔记数据可能在不同的路径
        if 'user' in state and 'notes' in state['user']:
            for note in state['user']['notes']:
                notes.append({
                    'note_id': note.get('noteId', ''),
                    'title': note.get('title', ''),
                    'desc': note.get('desc', ''),
                    'likes': note.get('likes', 0),
                    'covers': note.get('covers', []),
                })
    except Exception as e:
        print(f"[ERROR] 提取笔记失败: {e}")
    
    return notes


def main():
    """主函数"""
    print("="*60)
    print("小红书真实数据采集器")
    print("="*60)
    
    # 测试搜索
    keyword = "第四种黑猩猩"
    print(f"\n[搜索] {keyword}")
    
    users = search_users(keyword)
    
    if users:
        print(f"\n找到 {len(users)} 个用户:")
        for i, user in enumerate(users[:5], 1):
            print(f"{i}. {user['nickname']} (ID: {user['user_id']})")
            print(f"   粉丝: {user.get('fans', 0)}, 简介: {user.get('desc', '无')[:50]}")
    else:
        print("\n[警告] 未找到用户数据，可能需要登录或验证码")
    
    # 如果找到用户，尝试获取笔记
    if users:
        target_user = users[0]
        print(f"\n[获取笔记] 用户: {target_user['nickname']}")
        
        notes = get_user_notes(target_user['user_id'], max_notes=10)
        
        if notes:
            print(f"\n找到 {len(notes)} 篇笔记:")
            for i, note in enumerate(notes[:10], 1):
                print(f"\n{i}. {note['title'] or '无标题'}")
                print(f"   点赞: {note.get('likes', 0)}")
                content = note.get('desc', '')
                if content:
                    print(f"   内容: {content[:100]}...")
        else:
            print("\n[警告] 未找到笔记数据")
    
    # 保存结果
    result = {
        'keyword': keyword,
        'users': users,
        'timestamp': time.time()
    }
    
    output_file = 'xhs_real_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n[保存] 结果已保存到 {output_file}")


if __name__ == "__main__":
    main()
