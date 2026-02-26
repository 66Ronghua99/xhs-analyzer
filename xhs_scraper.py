#!/usr/bin/env python3
"""
小红书内容采集与分析工具
用于个人IP对标研究
"""

import json
import re
import time
import random
from urllib.parse import quote, unquote
from typing import List, Dict, Any, Optional
import http.client
import ssl

class XHSScraper:
    """小红书网页版内容采集器"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cookie': 'webId=; web_session=; xsecappid=; a1=;'
        }
        self.context = ssl._create_unverified_context()
    
    def _fetch(self, url: str, host: str = "www.xiaohongshu.com") -> str:
        """获取页面内容"""
        try:
            conn = http.client.HTTPSConnection(host, context=self.context, timeout=15)
            conn.request("GET", url, headers=self.headers)
            response = conn.getresponse()
            data = response.read().decode('utf-8')
            conn.close()
            return data
        except Exception as e:
            print(f"[ERROR] Fetch failed: {e}")
            return ""
    
    def search_user_notes(self, username: str, max_notes: int = 20) -> List[Dict]:
        """
        搜索用户的笔记内容
        注意：小红书网页版有反爬限制，实际使用需要处理验证码
        """
        print(f"[INFO] 开始采集用户: {username}")
        
        # 尝试搜索用户
        search_url = f"/search_result?keyword={quote(username)}&type=user"
        result = self._fetch(search_url)
        
        # 提取笔记数据 (JSON-LD 或 SSR 数据)
        notes = []
        
        # 尝试从页面提取 note 数据
        note_pattern = r'"noteId":"([^"]+)".*?"title":"([^"]*)".*?"desc":"([^"]*)"'
        matches = re.findall(note_pattern, result, re.DOTALL)
        
        for match in matches[:max_notes]:
            note_id, title, desc = match
            notes.append({
                'note_id': note_id,
                'title': self._clean_text(title),
                'desc': self._clean_text(desc),
                'url': f'https://www.xiaohongshu.com/explore/{note_id}'
            })
        
        print(f"[INFO] 采集到 {len(notes)} 条笔记")
        return notes
    
    def _clean_text(self, text: str) -> str:
        """清理文本中的特殊字符"""
        if not text:
            return ""
        # 解码 Unicode 转义
        text = text.encode('utf-8').decode('unicode_escape', errors='ignore')
        # 去除多余空白
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def analyze_note_structure(self, notes: List[Dict]) -> Dict:
        """分析笔记的内容结构"""
        analysis = {
            'total_notes': len(notes),
            'avg_title_length': 0,
            'avg_desc_length': 0,
            'common_patterns': [],
            'title_patterns': []
        }
        
        if not notes:
            return analysis
        
        # 统计标题和描述长度
        title_lengths = [len(n['title']) for n in notes if n.get('title')]
        desc_lengths = [len(n['desc']) for n in notes if n.get('desc')]
        
        if title_lengths:
            analysis['avg_title_length'] = sum(title_lengths) / len(title_lengths)
        if desc_lengths:
            analysis['avg_desc_length'] = sum(desc_lengths) / len(desc_lengths)
        
        # 识别标题模式
        title_patterns = {
            '数字开头': r'^\d+',
            '问句': r'.*\?|.*？',
            '感叹号': r'!|！',
            '干货': r'干货|教程|攻略',
            '热点': r'最新|刚刚|突发',
            '对比': r'vs|对比|区别'
        }
        
        for pattern_name, pattern in title_patterns.items():
            count = sum(1 for n in notes if re.search(pattern, n.get('title', ''), re.I))
            if count > 0:
                analysis['title_patterns'].append({
                    'pattern': pattern_name,
                    'count': count,
                    'percentage': f"{count/len(notes)*100:.1f}%"
                })
        
        return analysis


def main():
    """示例用法"""
    scraper = XHSScraper()
    
    # 测试采集（小红书有反爬，实际使用需要处理验证）
    test_users = ["第四种黑猩猩", "老徐在创造"]
    
    for user in test_users:
        print(f"\n{'='*50}")
        print(f"正在分析用户: {user}")
        print('='*50)
        
        # 采集笔记
        notes = scraper.search_user_notes(user, max_notes=10)
        
        # 保存原始数据
        if notes:
            filename = f"xhs_data_{user}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(notes, f, ensure_ascii=False, indent=2)
            print(f"[INFO] 数据已保存到: {filename}")
            
            # 分析结构
            analysis = scraper.analyze_note_structure(notes)
            print(f"\n[ANALYSIS] 内容分析结果:")
            print(json.dumps(analysis, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
