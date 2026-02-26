#!/usr/bin/env python3
"""
小红书内容深度分析器
用于解析博主的内容策略、选题方向和表达风格
"""

import json
import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, asdict
from collections import Counter


@dataclass
class ContentPattern:
    """内容模式"""
    pattern_type: str  # hook_type, structure, tone
    description: str
    examples: List[str]
    frequency: int


@dataclass
class ContentAnalysis:
    """单篇内容分析"""
    title: str
    title_length: int
    has_number: bool
    has_question: bool
    has_emotion: bool
    emoji_count: int
    paragraph_count: int
    avg_sentence_length: float
    tone: str  # professional, casual, emotional, controversial
    structure: str  # problem-solution, story, list, opinion


class XHSContentAnalyzer:
    """小红书内容策略分析器"""
    
    # 情感词库
    EMOTION_WORDS = {
        'positive': ['震惊', '绝了', '宝藏', '救命', '吹爆', '真香', '太绝了', '封神'],
        'negative': ['避雷', '踩雷', '翻车', '被骗', '套路', '坑'],
        'urgency': ['急', '快看', '刚刚', '最新', '马上', '立刻'],
        'curiosity': ['居然', '原来', '没想到', '我发现', '揭秘']
    }
    
    # 句式模式
    TITLE_PATTERNS = {
        'number_list': r'^\d+',
        'how_to': r'^(如何|怎么|怎样|教程|攻略)',
        'comparison': r'(vs|对比|区别|PK|和|还是)',
        'question': r'[？?]',
        'personal': r'(我|我的|我们)',
        'time_sensitive': r'(最新|刚刚|今天|现在|近期)',
        'emotional': r'(震惊|绝了|救命|真香|吹爆|避雷)'
    }
    
    def __init__(self):
        self.analyses: List[ContentAnalysis] = []
        self.patterns: List[ContentPattern] = []
    
    def analyze_title(self, title: str) -> Dict[str, Any]:
        """分析标题特征"""
        result = {
            'length': len(title),
            'patterns': [],
            'has_number': False,
            'has_question': False,
            'emotion_score': 0,
            'keywords': []
        }
        
        # 检测句式模式
        for pattern_name, pattern in self.TITLE_PATTERNS.items():
            if re.search(pattern, title, re.I):
                result['patterns'].append(pattern_name)
                if pattern_name == 'number_list':
                    result['has_number'] = True
                if pattern_name == 'question':
                    result['has_question'] = True
        
        # 情感词分析
        for emotion_type, words in self.EMOTION_WORDS.items():
            for word in words:
                if word in title:
                    result['emotion_score'] += 1
                    result['keywords'].append((word, emotion_type))
        
        return result
    
    def analyze_content(self, title: str, content: str) -> ContentAnalysis:
        """分析单篇内容的完整特征"""
        # 清理内容
        content_clean = re.sub(r'[#@]\w+', '', content)  # 移除标签和@提及
        
        # 分段和分句
        paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
        sentences = re.split(r'[。！？.!?]+', content_clean)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
        
        # 计算平均句长
        avg_sent_len = sum(len(s) for s in sentences) / max(len(sentences), 1)
        
        # 分析标题
        title_analysis = self.analyze_title(title)
        
        # 检测语调
        emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', content))
        
        if emoji_count > 5 or title_analysis['emotion_score'] > 2:
            tone = 'emotional'
        elif '干货' in content or '教程' in title or title_analysis['has_number']:
            tone = 'professional'
        elif '我' in content[:50] or '我的' in title:
            tone = 'personal'
        else:
            tone = 'casual'
        
        # 检测结构
        if any(w in title for w in ['如何', '怎么', '教程', '步骤']):
            structure = 'tutorial'
        elif any(w in content for w in ['首先', '然后', '最后', '第一步']):
            structure = 'step-by-step'
        elif '故事' in title or len(paragraphs) > 5:
            structure = 'story'
        elif title_analysis['has_number']:
            structure = 'list'
        else:
            structure = 'opinion'
        
        return ContentAnalysis(
            title=title,
            title_length=title_analysis['length'],
            has_number=title_analysis['has_number'],
            has_question=title_analysis['has_question'],
            has_emotion=title_analysis['emotion_score'] > 0,
            emoji_count=emoji_count,
            paragraph_count=len(paragraphs),
            avg_sentence_length=round(avg_sent_len, 1),
            tone=tone,
            structure=structure
        )
    
    def extract_patterns(self, analyses: List[ContentAnalysis]) -> List[ContentPattern]:
        """从多个内容中提取共性模式"""
        patterns = []
        
        # 分析标题长度分布
        title_lengths = [a.title_length for a in analyses]
        avg_len = sum(title_lengths) / len(title_lengths)
        
        # Hook 类型分析
        hook_types = Counter([self._classify_hook(a) for a in analyses])
        
        # 结构模式
        structures = Counter([a.structure for a in analyses])
        
        # 语调模式
        tones = Counter([a.tone for a in analyses])
        
        patterns.append(ContentPattern(
            pattern_type='title_length',
            description=f'标题平均长度: {avg_len:.0f}字，范围: {min(title_lengths)}-{max(title_lengths)}',
            examples=[a.title for a in analyses[:3]],
            frequency=len(analyses)
        ))
        
        patterns.append(ContentPattern(
            pattern_type='hook_strategy',
            description=f'Hook类型分布: {dict(hook_types)}',
            examples=[],
            frequency=len(analyses)
        ))
        
        patterns.append(ContentPattern(
            pattern_type='content_structure',
            description=f'结构偏好: {dict(structures)}',
            examples=[],
            frequency=len(analyses)
        ))
        
        patterns.append(ContentPattern(
            pattern_type='tone_preference',
            description=f'语调分布: {dict(tones)}',
            examples=[],
            frequency=len(analyses)
        ))
        
        return patterns
    
    def _classify_hook(self, analysis: ContentAnalysis) -> str:
        """分类内容的Hook类型"""
        if analysis.has_number:
            return 'list_hook'
        elif analysis.has_question:
            return 'question_hook'
        elif analysis.has_emotion:
            return 'emotion_hook'
        elif analysis.tone == 'personal':
            return 'story_hook'
        else:
            return 'fact_hook'
    
    def generate_report(self, target_name: str, analyses: List[ContentAnalysis]) -> Dict:
        """生成完整的分析报告"""
        patterns = self.extract_patterns(analyses)
        
        report = {
            'target': target_name,
            'sample_size': len(analyses),
            'overview': {
                'avg_title_length': round(sum(a.title_length for a in analyses) / len(analyses), 1),
                'most_common_structure': max(set(a.structure for a in analyses), key=lambda x: sum(1 for a in analyses if a.structure == x)),
                'dominant_tone': max(set(a.tone for a in analyses), key=lambda x: sum(1 for a in analyses if a.tone == x)),
            },
            'title_patterns': {
                'with_numbers': sum(1 for a in analyses if a.has_number),
                'with_questions': sum(1 for a in analyses if a.has_question),
                'with_emotion': sum(1 for a in analyses if a.has_emotion),
            },
            'content_patterns': [asdict(p) for p in patterns],
            'examples': [
                {
                    'title': a.title,
                    'structure': a.structure,
                    'tone': a.tone,
                    'hook_type': self._classify_hook(a)
                }
                for a in analyses[:5]
            ]
        }
        
        return report


def main():
    """测试分析器"""
    analyzer = XHSContentAnalyzer()
    
    # 测试数据（模拟实际采集的数据）
    test_analyses = [
        ContentAnalysis(
            title="震惊！我用AI 3天做出了一个产品",
            title_length=15,
            has_number=True,
            has_question=False,
            has_emotion=True,
            emoji_count=3,
            paragraph_count=5,
            avg_sentence_length=12.5,
            tone='emotional',
            structure='story'
        ),
        ContentAnalysis(
            title="Cursor vs Windsurf 到底选哪个？深度对比",
            title_length=20,
            has_number=False,
            has_question=True,
            has_emotion=False,
            emoji_count=1,
            paragraph_count=8,
            avg_sentence_length=18.2,
            tone='professional',
            structure='comparison'
        ),
    ]
    
    report = analyzer.generate_report("测试博主", test_analyses)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
