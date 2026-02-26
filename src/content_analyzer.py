#!/usr/bin/env python3
"""
内容分析器 - 分析视频字幕/文案的内容结构
"""

import re
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
from collections import Counter


@dataclass
class ContentAnalysis:
    """内容分析结果"""
    # 基础统计
    word_count: int
    char_count: int
    sentence_count: int
    avg_sentence_length: float
    
    # 内容特征
    hook_type: str
    structure: str
    topics: List[str]
    tone: str
    
    # 互动元素
    engagement_techniques: List[str]
    call_to_action: List[str]
    
    # 关键要点
    key_points: List[str]
    
    # 优化建议
    recommendations: List[str]


class ContentAnalyzer:
    """内容分析器"""
    
    # 主题关键词库
    TOPIC_KEYWORDS = {
        'AI技术': ['AI', '人工智能', '大模型', 'ChatGPT', 'Claude', 'GPT-4', 'LLM', 'AGI'],
        '编程开发': ['代码', '编程', '程序员', '开发', 'GitHub', 'Cursor', 'IDE', 'debug'],
        '产品创业': ['产品', '创业', '独立开发', '副业', '收入', '变现', 'MVP', 'PMF'],
        '工具效率': ['工具', '效率', '自动化', 'Workflow', '插件', '脚本', '快捷键'],
        '职场成长': ['职场', '成长', '学习', '进阶', '管理', '沟通', '面试'],
        '行业趋势': ['趋势', '风口', '赛道', '机会', '红利', '蓝海'],
    }
    
    # 钩子类型识别规则
    HOOK_PATTERNS = {
        '数字/列表': {
            'patterns': [r'\d+个', r'\d+种', r'\d+步', r'第[一二三四五六七八九十]', r'第\d+'],
            'psychology': '具体数字增加可信度和信息量'
        },
        '疑问/悬念': {
            'patterns': [r'吗[？?]', r'呢[？?]', r'[？?].{0,10}$', r'为什么', r'怎么', r'如何', r'是不是'],
            'psychology': '激发好奇心，让人想继续看'
        },
        '情感共鸣': {
            'patterns': [r'震惊', r'绝了', r'太[棒好牛]', r'真的', r'居然', r'没想到', r'后悔'],
            'psychology': '情绪唤起，让人产生共情'
        },
        '利益承诺': {
            'patterns': [r'学会', r'掌握', r'轻松', r'快速', r'高效', r'省钱', r'赚钱', r'变现'],
            'psychology': '明确价值，让人期待回报'
        },
        '权威背书': {
            'patterns': [r'据', r'研究发现', r'数据显示', r'专家', r'大佬', r'年薪百万'],
            'psychology': '建立信任，让人觉得可信'
        },
        '争议/反转': {
            'patterns': [r'但是', r'其实', r'真相', r'不要被', r'套路', r'坑'],
            'psychology': '打破认知，制造反转'
        }
    }
    
    # 互动技巧识别规则
    ENGAGEMENT_PATTERNS = {
        '直接行动召唤': ['点赞', '收藏', '关注', '转发', '评论', '分享', '保存'],
        '提问互动': ['你怎么看', '你觉得呢', '评论区', '留言', '告诉我', '有没有'],
        '挑战/打卡': ['试试', '挑战', '坚持', '打卡', '第X天', '一起'],
        '利益激励': ['福利', '礼物', '抽奖', '免费', '送', '领取'],
        '社群建设': ['关注', '一起', '交流', '学习', '成长', '我们'],
        '情感共鸣': ['支持', '鼓励', '加油', '陪伴', '谢谢'],
        '悬念/预告': ['下期', '下次', '接下来', '敬请期待', '预告']
    }
    
    def __init__(self):
        self.stats = {}
    
    def analyze(self, text: str) -> ContentAnalysis:
        """
        分析文本内容
        
        Args:
            text: 要分析的文本（字幕/文案）
            
        Returns:
            ContentAnalysis 分析结果
        """
        if not text or not text.strip():
            raise ValueError("文本不能为空")
        
        # 基础统计
        basic_stats = self._calculate_basic_stats(text)
        
        # 内容特征分析
        hook_type = self._identify_hook(text)
        structure = self._identify_structure(text)
        topics = self._extract_topics(text)
        tone = self._identify_tone(text)
        
        # 互动元素
        engagement = self._identify_engagement(text)
        cta = self._identify_cta(text)
        
        # 关键要点
        key_points = self._extract_key_points(text)
        
        # 优化建议
        recommendations = self._generate_recommendations(
            basic_stats, hook_type, structure, engagement, topics
        )
        
        return ContentAnalysis(
            word_count=basic_stats['word_count'],
            char_count=basic_stats['char_count'],
            sentence_count=basic_stats['sentence_count'],
            avg_sentence_length=basic_stats['avg_sentence_length'],
            hook_type=hook_type,
            structure=structure,
            topics=topics,
            tone=tone,
            engagement_techniques=engagement,
            call_to_action=cta,
            key_points=key_points,
            recommendations=recommendations
        )
    
    def _calculate_basic_stats(self, text: str) -> Dict:
        """计算基础统计信息"""
        # 清理文本
        clean_text = text.strip()
        
        # 字数（中文字符）
        char_count = len(clean_text.replace(' ', '').replace('\n', ''))
        
        # 词数（按空格和标点分割）
        words = re.findall(r'\b\w+\b|[\u4e00-\u9fff]', clean_text)
        word_count = len(words)
        
        # 句子数
        sentences = re.split(r'[。！？.!?]+', clean_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        sentence_count = len(sentences)
        
        # 平均句长
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        return {
            'word_count': word_count,
            'char_count': char_count,
            'sentence_count': sentence_count,
            'avg_sentence_length': round(avg_sentence_length, 1)
        }
    
    def _identify_hook(self, text: str) -> str:
        """识别钩子（Hook）类型"""
        first_100_chars = text[:100]
        
        for hook_name, hook_info in self.HOOK_PATTERNS.items():
            for pattern in hook_info['patterns']:
                if re.search(pattern, first_100_chars, re.IGNORECASE):
                    return hook_name
        
        return '普通叙述'
    
    def _identify_structure(self, text: str) -> str:
        """识别内容结构"""
        # 检查顺序结构
        if any(w in text for w in ['首先', '其次', '最后', '第一步', '第二步']):
            return '顺序结构'
        
        # 检查列表结构
        if re.search(r'[第]?[一二三四五六七八九十\d]+[、.]', text):
            return '列表结构'
        
        # 检查问答结构
        if text.count('？') >= 2 and '。' in text[:200]:
            return '问答结构'
        
        # 检查故事结构
        if any(w in text for w in ['故事', '经历', '那年', '当时', '后来']):
            return '故事结构'
        
        # 检查对比结构
        if any(w in text for w in ['对比', '区别', 'vs', '相比', '不如']):
            return '对比结构'
        
        return '叙述结构'
    
    def _extract_topics(self, text: str) -> List[str]:
        """提取主题关键词"""
        found_topics = []
        text_lower = text.lower()
        
        for topic, keywords in self.TOPIC_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    found_topics.append(topic)
                    break
        
        return list(set(found_topics))
    
    def _identify_tone(self, text: str) -> str:
        """识别语气/语调"""
        # 检查情感化表达
        emotion_words = ['震惊', '绝了', '太', '真的', '居然', '太棒', '超', '巨']
        emotion_count = sum(1 for w in emotion_words if w in text)
        
        # 检查专业术语密度
        professional_words = ['研究', '数据', '分析', '方法', '系统', '架构', '模型']
        prof_count = sum(1 for w in professional_words if w in text)
        
        # 检查口语化表达
        casual_words = ['咱们', '大家', '一起', '其实', '说实话', '说实话']
        casual_count = sum(1 for w in casual_words if w in text)
        
        # 判断语调
        if emotion_count >= 3:
            return '情绪化/热情'
        elif prof_count >= 4:
            return '专业/理性'
        elif casual_count >= 3:
            return '轻松/亲切'
        elif '我' in text[:100] or '我的' in text[:100]:
            return '个人化/真诚'
        else:
            return '中立/客观'
    
    def _identify_engagement(self, text: str) -> List[str]:
        """识别互动技巧"""
        found_techniques = []
        
        for technique, patterns in self.ENGAGEMENT_PATTERNS.items():
            for pattern in patterns:
                if pattern in text:
                    found_techniques.append(technique)
                    break
        
        return list(set(found_techniques))
    
    def _identify_cta(self, text: str) -> List[str]:
        """识别明确的行动召唤（CTA）"""
        cta_patterns = [
            r'记得[点关].*',
            r'[点关].*不迷路',
            r'[记得]?[加关].*[哦啊]',
            r'[求请].*[点关]',
            r'觉得.*[记得]?[点关]',
            r'别忘.*[点关]',
            r'如果.*[记得]?[点关]',
        ]
        
        found_cta = []
        for pattern in cta_patterns:
            if re.search(pattern, text):
                found_cta.append(re.search(pattern, text).group())
        
        return found_cta
    
    def _extract_key_points(self, text: str) -> List[str]:
        """提取关键要点"""
        points = []
        
        # 按句子分割
        sentences = re.split('[。！？\n]', text)
        
        for sent in sentences:
            sent = sent.strip()
            # 选择长度适中的句子
            if 15 <= len(sent) <= 80:
                # 优先选择包含关键词的句子
                if any(kw in sent for kw in ['建议', '方法', '技巧', '注意', '关键', '核心', '步骤', '首先', '最后']):
                    points.append(sent)
        
        # 去重并限制数量
        unique_points = list(dict.fromkeys(points))
        return unique_points[:5]
    
    def _generate_recommendations(self, stats: Dict, hook: str, structure: str, 
                                   engagement: List[str], topics: List[str]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        # 根据钩子类型给建议
        if hook == '普通叙述':
            recommendations.append(
                '【开头优化】建议开头使用更有吸引力的钩子，比如：\n' +
                '  - 数字型："3个方法让你..."\n' +
                '  - 疑问型："你是不是也遇到过..."\n' +
                '  - 利益型："学会这招，效率翻倍"'
            )
        
        # 根据内容结构给建议
        if structure == '叙述结构':
            recommendations.append(
                '【结构优化】可以尝试更清晰的结构：\n' +
                '  - 问题-解决：痛点 → 方案 → 效果\n' +
                '  - 步骤式：第一步 → 第二步 → 第三步\n' +
                '  - 对比式：传统方法 vs 新方法'
            )
        
        # 根据互动技巧给建议
        if len(engagement) < 2:
            recommendations.append(
                '【互动优化】建议增加更多互动引导：\n' +
                '  - 提问式："你平时是怎么做的？评论区告诉我"\n' +
                '  - 引导式："觉得有用记得点赞收藏"\n' +
                '  - 挑战式："试试这个方法，坚持7天看效果"'
            )
        
        # 根据主题给建议
        if not topics:
            recommendations.append(
                '【主题优化】内容主题可以更明确：\n' +
                '  - 确定你的垂直领域（如AI工具/编程/产品）\n' +
                '  - 在标题和内容中突出关键词\n' +
                '  - 保持内容的一致性'
            )
        
        # 根据字数给建议
        word_count = stats.get('word_count', 0)
        if word_count < 100:
            recommendations.append(
                '【内容长度】当前内容较短，建议：\n' +
                '  - 短视频文案建议 100-200 字\n' +
                '  - 增加具体案例或细节\n' +
                '  - 补充操作步骤或注意事项'
            )
        elif word_count > 500:
            recommendations.append(
                '【内容长度】当前内容较长，建议：\n' +
                '  - 考虑精简核心观点\n' +
                '  - 使用更清晰的分段\n' +
                '  - 突出关键信息'
            )
        
        return recommendations[:5]  # 最多返回5条建议


# 便捷使用函数
def quick_analyze(text: str) -> Dict:
    """快速分析文本"""
    analyzer = ContentAnalyzer()
    analysis = analyzer.analyze(text)
    return asdict(analysis)


if __name__ == "__main__":
    # 测试
    sample_text = """
    今天分享3个AI编程的绝招，学会了效率翻倍！
    
    第一，用Cursor的快捷键。很多人不知道，按住Cmd+K可以直接调用AI。
    第二，善用代码补全。不要一个一个敲，让AI帮你写完整的函数。
    第三，多用自然语言描述。越清晰的需求描述，生成的代码越准确。
    
    你平时用什么AI工具编程？评论区告诉我！
    觉得有用记得点赞收藏，关注我了解更多AI技巧。
    """
    
    print("="*60)
    print("内容分析测试")
    print("="*60)
    
    result = quick_analyze(sample_text)
    
    print(f"\n字数: {result['word_count']}")
    print(f"钩子类型: {result['hook_type']}")
    print(f"内容结构: {result['structure']}")
    print(f"主题: {', '.join(result['topics'])}")
    print(f"语气: {result['tone']}")
    print(f"\n互动技巧: {', '.join(result['engagement_techniques'])}")
    print(f"\n关键要点:")
    for i, point in enumerate(result['key_points'], 1):
        print(f"  {i}. {point}")
    print(f"\n优化建议:")
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"  {i}. {rec[:100]}...")
