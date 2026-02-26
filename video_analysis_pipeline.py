#!/usr/bin/env python3
"""
小红书视频内容深度分析 Pipeline
包括：视频下载 → 字幕提取 → 内容分析
"""

import json
import os
import re
import subprocess
from typing import List, Dict, Optional
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs

@dataclass
class VideoContent:
    """视频内容分析结果"""
    video_id: str
    title: str
    author: str
    subtitles: str
    key_topics: List[str]
    content_structure: Dict
    hook_analysis: Dict
    engagement_techniques: List[str]


class VideoDownloader:
    """视频下载器 - 基于 yt-dlp 或类似工具"""
    
    def __init__(self, output_dir: str = "./downloads"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def check_dependencies(self) -> bool:
        """检查必要的依赖"""
        tools = ['yt-dlp', 'ffmpeg', 'whisper']
        available = {}
        
        for tool in tools:
            try:
                subprocess.run([tool, '--version'], capture_output=True, check=True)
                available[tool] = True
            except:
                available[tool] = False
        
        return available
    
    def install_dependencies_guide(self):
        """输出安装指南"""
        guide = """
# 视频分析工具链安装指南

## 1. 安装 yt-dlp (视频下载)
```bash
brew install yt-dlp
```

## 2. 安装 ffmpeg (音视频处理)
```bash
brew install ffmpeg
```

## 3. 安装 Whisper (字幕提取)
```bash
# 方式1: 使用 OpenAI 官方
pip install openai-whisper

# 方式2: 使用 faster-whisper (更快)
pip install faster-whisper
```

## 4. 测试安装
```bash
yt-dlp --version
ffmpeg -version
whisper --help
```
"""
        return guide
    
    def download_video(self, url: str, video_id: str) -> Optional[str]:
        """
        下载视频
        注意：小红书有反爬，直接下载可能失败
        """
        output_path = os.path.join(self.output_dir, f"{video_id}.mp4")
        
        try:
            # 使用 yt-dlp 下载
            cmd = [
                'yt-dlp',
                '--no-check-certificate',
                '--user-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                '-o', output_path,
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0 and os.path.exists(output_path):
                print(f"[OK] 视频已下载: {output_path}")
                return output_path
            else:
                print(f"[ERROR] 下载失败: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"[ERROR] 下载异常: {e}")
            return None


class SubtitleExtractor:
    """字幕提取器"""
    
    def __init__(self, model_size: str = "base"):
        """
        model_size: tiny, base, small, medium, large
        越大越准确但越慢
        """
        self.model_size = model_size
        self.model = None
    
    def load_model(self):
        """加载 Whisper 模型"""
        if self.model is None:
            try:
                import whisper
                print(f"[INFO] 加载 Whisper {self.model_size} 模型...")
                self.model = whisper.load_model(self.model_size)
                print("[OK] 模型加载完成")
            except Exception as e:
                print(f"[ERROR] 加载模型失败: {e}")
                raise
    
    def extract_subtitles(self, video_path: str) -> Dict:
        """
        从视频中提取字幕
        返回包含完整文本和时间戳的结果
        """
        self.load_model()
        
        print(f"[INFO] 开始提取字幕: {video_path}")
        
        try:
            # 转录音频
            result = self.model.transcribe(
                video_path,
                language='zh',  # 中文
                task='transcribe',
                verbose=True
            )
            
            # 整理结果
            subtitles = {
                'full_text': result['text'],
                'segments': [],
                'language': result.get('language', 'zh'),
                'duration': result.get('duration', 0)
            }
            
            # 处理每个片段
            for segment in result['segments']:
                subtitles['segments'].append({
                    'start': segment['start'],
                    'end': segment['end'],
                    'text': segment['text'].strip(),
                    'confidence': segment.get('avg_logprob', 0)
                })
            
            print(f"[OK] 字幕提取完成，共 {len(subtitles['segments'])} 个片段")
            print(f"[INFO] 总时长: {subtitles['duration']:.1f} 秒")
            print(f"[INFO] 总字数: {len(subtitles['full_text'])}")
            
            return subtitles
            
        except Exception as e:
            print(f"[ERROR] 提取字幕失败: {e}")
            import traceback
            traceback.print_exc()
            return {'full_text': '', 'segments': [], 'error': str(e)}


class ContentAnalyzer:
    """内容分析器"""
    
    def __init__(self):
        self.topic_keywords = {
            'AI技术': ['AI', '人工智能', '大模型', 'ChatGPT', 'Claude', 'GPT-4'],
            '编程开发': ['代码', '编程', '程序员', '开发', 'GitHub', 'Cursor'],
            '产品创业': ['产品', '创业', '独立开发', '副业', '收入', '变现'],
            '工具效率': ['工具', '效率', '自动化', 'Workflow', '插件'],
        }
    
    def analyze_content(self, text: str) -> Dict:
        """分析文本内容"""
        analysis = {
            'word_count': len(text),
            'char_count': len(text.replace(' ', '')),
            'topics': self.extract_topics(text),
            'hook_type': self.identify_hook(text),
            'structure': self.analyze_structure(text),
            'key_points': self.extract_key_points(text),
            'engagement_techniques': self.identify_engagement_techniques(text),
        }
        return analysis
    
    def extract_topics(self, text: str) -> List[str]:
        """提取主题关键词"""
        found_topics = []
        text_lower = text.lower()
        
        for topic, keywords in self.topic_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    found_topics.append(topic)
                    break
        
        return list(set(found_topics))
    
    def identify_hook(self, text: str) -> str:
        """识别钩子类型"""
        hooks = {
            '数字/列表': ['\d+个', '\d+种', '\d+步', '第一', '第二'],
            '疑问/悬念': ['吗？', '呢？', '？', '为什么', '怎么', '如何'],
            '情感共鸣': ['震惊', '绝了', '太', '真的', '居然'],
            '利益承诺': ['学会', '掌握', '学会', '赚钱', '变现'],
            '权威/数据': ['据', '研究', '数据显示', '专家'],
        }
        
        for hook_type, patterns in hooks.items():
            for pattern in patterns:
                if re.search(pattern, text[:100]):
                    return hook_type
        
        return '普通叙述'
    
    def analyze_structure(self, text: str) -> str:
        """分析内容结构"""
        if '首先' in text and '其次' in text:
            return '顺序结构'
        elif '第一' in text or '1.' in text:
            return '列表结构'
        elif '？' in text and '。' in text[:100]:
            return '问答结构'
        elif '故事' in text or '经历' in text:
            return '故事结构'
        else:
            return '叙述结构'
    
    def extract_key_points(self, text: str) -> List[str]:
        """提取关键要点"""
        points = []
        
        # 按句子分割
        sentences = re.split('[。！？\n]', text)
        
        for sent in sentences:
            sent = sent.strip()
            if len(sent) > 10 and len(sent) < 100:
                # 优先保留包含关键词的句子
                if any(kw in sent for kw in ['建议', '方法', '技巧', '注意', '关键', '核心']):
                    points.append(sent)
        
        return points[:5]  # 返回前5个要点
    
    def identify_engagement_techniques(self, text: str) -> List[str]:
        """识别互动技巧"""
        techniques = []
        
        if any(word in text for word in ['你怎么看', '你觉得呢', '评论区', '留言']):
            techniques.append('引导评论')
        
        if any(word in text for word in ['点赞', '收藏', '关注', '转发']):
            techniques.append('行动召唤')
        
        if '？' in text and text.count('？') >= 2:
            techniques.append('连续提问')
        
        if any(word in text for word in ['福利', '礼物', '抽奖', '免费']):
            techniques.append('利益激励')
        
        if '...' in text or '……' in text:
            techniques.append('悬念留白')
        
        return techniques


def main():
    """主函数"""
    print("="*60)
    print("小红书视频内容分析系统")
    print("="*60)
    
    # 示例：分析一段示例文本
    sample_text = """
    今天分享3个AI编程的绝招，学会了效率翻倍！
    
    第一，用Cursor的快捷键。很多人不知道，按住Cmd+K可以直接调用AI。
    第二，善用代码补全。不要一个一个敲，让AI帮你写完整的函数。
    第三，多用自然语言描述。越清晰的需求描述，生成的代码越准确。
    
    你平时用什么AI工具编程？评论区告诉我！
    觉得有用记得点赞收藏，关注我了解更多AI技巧。
    """
    
    print("\n示例文本分析:")
    print("-"*60)
    
    analyzer = ContentAnalyzer()
    analysis = analyzer.analyze_content(sample_text)
    
    print(f"字数: {analysis['word_count']}")
    print(f"主题: {', '.join(analysis['topics'])}")
    print(f"钩子类型: {analysis['hook_type']}")
    print(f"结构: {analysis['structure']}")
    print(f"\n关键要点:")
    for i, point in enumerate(analysis['key_points'], 1):
        print(f"  {i}. {point}")
    print(f"\n互动技巧: {', '.join(analysis['engagement_techniques'])}")
    
    print("\n" + "="*60)
    print("完整分析系统已就绪")
    print("="*60)


if __name__ == "__main__":
    main()
