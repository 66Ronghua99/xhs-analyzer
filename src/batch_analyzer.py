#!/usr/bin/env python3
"""
批量内容分析器 - 批量分析多条文案并生成对比报告
"""

import json
import csv
from typing import List, Dict, Any
from collections import Counter
from dataclasses import dataclass, asdict

from .content_analyzer import ContentAnalyzer


@dataclass
class BatchAnalysisResult:
    """批量分析结果"""
    total_count: int
    successful_count: int
    failed_count: int
    analyses: List[Dict]
    summary: Dict
    patterns: Dict


class BatchAnalyzer:
    """批量内容分析器"""
    
    def __init__(self):
        self.analyzer = ContentAnalyzer()
    
    def analyze_from_json(self, json_path: str) -> Dict:
        """
        从 JSON 文件读取文案并分析
        
        Args:
            json_path: JSON 文件路径
            
        Returns:
            包含分析结果的字典
        """
        # 读取 JSON 文件
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 提取文案列表
        contents = []
        if isinstance(data, dict):
            if 'videos' in data:
                contents = data['videos']
            elif 'contents' in data:
                contents = data['contents']
            elif 'items' in data:
                contents = data['items']
            elif 'data' in data:
                contents = data['data']
            else:
                # 尝试直接作为列表处理
                contents = data if isinstance(data, list) else [data]
        elif isinstance(data, list):
            contents = data
        
        # 分析每条内容
        analyses = []
        failed = []
        
        for idx, item in enumerate(contents):
            try:
                # 提取文本内容
                if isinstance(item, str):
                    text = item
                elif isinstance(item, dict):
                    # 尝试多个可能的字段名
                    text = item.get('content') or item.get('text') or item.get('description') or item.get('body') or item.get('subtitle') or item.get('content', '')
                else:
                    text = str(item)
                
                if not text or not text.strip():
                    failed.append({'index': idx, 'error': 'Empty content'})
                    continue
                
                # 分析内容
                analysis = self.analyzer.analyze(text)
                result = asdict(analysis)
                
                # 添加原始数据信息
                if isinstance(item, dict):
                    result['metadata'] = {
                        'title': item.get('title', ''),
                        'author': item.get('author', ''),
                        'likes': item.get('likes', 0),
                        'id': item.get('id', idx)
                    }
                
                analyses.append(result)
                
            except Exception as e:
                failed.append({'index': idx, 'error': str(e)})
        
        # 生成汇总
        summary = self.generate_summary(analyses)
        patterns = self.compare_patterns(analyses)
        
        return {
            'total_count': len(contents),
            'successful_count': len(analyses),
            'failed_count': len(failed),
            'failed_items': failed,
            'analyses': analyses,
            'summary': summary,
            'patterns': patterns
        }
    
    def analyze_from_csv(self, csv_path: str, text_column: str = 'content') -> Dict:
        """
        从 CSV 文件读取文案并分析
        
        Args:
            csv_path: CSV 文件路径
            text_column: 包含文案内容的列名
            
        Returns:
            包含分析结果的字典
        """
        analyses = []
        failed = []
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for idx, row in enumerate(reader):
                try:
                    # 获取文本内容
                    text = row.get(text_column, '')
                    
                    if not text or not text.strip():
                        failed.append({'index': idx, 'error': 'Empty content'})
                        continue
                    
                    # 分析内容
                    analysis = self.analyzer.analyze(text)
                    result = asdict(analysis)
                    
                    # 添加原始数据信息（排除文本列）
                    metadata = {k: v for k, v in row.items() if k != text_column}
                    if metadata:
                        result['metadata'] = metadata
                    
                    analyses.append(result)
                    
                except Exception as e:
                    failed.append({'index': idx, 'error': str(e)})
        
        # 生成汇总
        summary = self.generate_summary(analyses)
        patterns = self.compare_patterns(analyses)
        
        return {
            'total_count': len(analyses) + len(failed),
            'successful_count': len(analyses),
            'failed_count': len(failed),
            'failed_items': failed,
            'analyses': analyses,
            'summary': summary,
            'patterns': patterns
        }
    
    def analyze_batch(self, texts: List[str], metadata: List[Dict] = None) -> Dict:
        """
        批量分析文本列表
        
        Args:
            texts: 文本列表
            metadata: 可选的元数据列表
            
        Returns:
            包含分析结果的字典
        """
        analyses = []
        failed = []
        
        for idx, text in enumerate(texts):
            try:
                if not text or not text.strip():
                    failed.append({'index': idx, 'error': 'Empty content'})
                    continue
                
                analysis = self.analyzer.analyze(text)
                result = asdict(analysis)
                
                # 添加元数据
                if metadata and idx < len(metadata):
                    result['metadata'] = metadata[idx]
                
                analyses.append(result)
                
            except Exception as e:
                failed.append({'index': idx, 'error': str(e)})
        
        # 生成汇总
        summary = self.generate_summary(analyses)
        patterns = self.compare_patterns(analyses)
        
        return {
            'total_count': len(texts),
            'successful_count': len(analyses),
            'failed_count': len(failed),
            'failed_items': failed,
            'analyses': analyses,
            'summary': summary,
            'patterns': patterns
        }
    
    def generate_summary(self, results: List[Dict]) -> Dict:
        """
        生成汇总统计
        
        Args:
            results: 分析结果列表
            
        Returns:
            汇总统计数据
        """
        if not results:
            return {
                'total_analyses': 0,
                'avg_word_count': 0,
                'avg_char_count': 0,
                'avg_sentence_count': 0,
                'hook_type_distribution': {},
                'structure_distribution': {},
                'topic_distribution': {},
                'tone_distribution': {},
                'engagement_techniques': {},
                'total_cta_count': 0,
                'top_recommendations': []
            }
        
        # 基础统计
        total = len(results)
        
        word_counts = [r.get('word_count', 0) for r in results]
        char_counts = [r.get('char_count', 0) for r in results]
        sentence_counts = [r.get('sentence_count', 0) for r in results]
        
        # 钩子类型分布
        hook_types = [r.get('hook_type', '未知') for r in results]
        hook_distribution = dict(Counter(hook_types))
        
        # 内容结构分布
        structures = [r.get('structure', '未知') for r in results]
        structure_distribution = dict(Counter(structures))
        
        # 主题分布
        all_topics = []
        for r in results:
            topics = r.get('topics', [])
            all_topics.extend(topics)
        topic_distribution = dict(Counter(all_topics))
        
        # 语气分布
        tones = [r.get('tone', '未知') for r in results]
        tone_distribution = dict(Counter(tones))
        
        # 互动技巧统计
        all_engagements = []
        for r in results:
            engagements = r.get('engagement_techniques', [])
            all_engagements.extend(engagements)
        engagement_distribution = dict(Counter(all_engagements))
        
        # CTA 统计
        total_cta = sum(len(r.get('call_to_action', [])) for r in results)
        
        # 收集建议
        all_recommendations = []
        for r in results:
            recs = r.get('recommendations', [])
            all_recommendations.extend(recs)
        
        # 统计建议出现频率
        recommendation_counter = Counter()
        for rec in all_recommendations:
            # 取建议的前50个字符作为key
            key = rec[:50] if rec else ''
            if key:
                recommendation_counter[key] += 1
        
        top_recommendations = [
            {'recommendation': rec, 'count': count}
            for rec, count in recommendation_counter.most_common(10)
        ]
        
        return {
            'total_analyses': total,
            'avg_word_count': round(sum(word_counts) / total, 1),
            'avg_char_count': round(sum(char_counts) / total, 1),
            'avg_sentence_count': round(sum(sentence_counts) / total, 1),
            'hook_type_distribution': hook_distribution,
            'structure_distribution': structure_distribution,
            'topic_distribution': topic_distribution,
            'tone_distribution': tone_distribution,
            'engagement_techniques': engagement_distribution,
            'total_cta_count': total_cta,
            'top_recommendations': top_recommendations
        }
    
    def compare_patterns(self, results: List[Dict]) -> Dict:
        """
        对比分析，识别高频模式
        
        Args:
            results: 分析结果列表
            
        Returns:
            对比分析结果
        """
        if not results:
            return {
                'top_hooks': [],
                'top_structures': [],
                'top_topics': [],
                'top_tones': [],
                'common_engagement_techniques': [],
                'patterns_insights': []
            }
        
        # 统计各维度频次
        hook_counter = Counter(r.get('hook_type', '未知') for r in results)
        structure_counter = Counter(r.get('structure', '未知') for r in results)
        
        # 主题需要合并统计
        topic_counter = Counter()
        for r in results:
            for topic in r.get('topics', []):
                topic_counter[topic] += 1
        
        tone_counter = Counter(r.get('tone', '未知') for r in results)
        
        # 互动技巧
        engagement_counter = Counter()
        for r in results:
            for eng in r.get('engagement_techniques', []):
                engagement_counter[eng] += 1
        
        # 提取高频模式
        top_hooks = [
            {'type': hook, 'count': count, 'percentage': round(count / len(results) * 100, 1)}
            for hook, count in hook_counter.most_common(5)
        ]
        
        top_structures = [
            {'type': structure, 'count': count, 'percentage': round(count / len(results) * 100, 1)}
            for structure, count in structure_counter.most_common(5)
        ]
        
        top_topics = [
            {'topic': topic, 'count': count, 'percentage': round(count / len(results) * 100, 1)}
            for topic, count in topic_counter.most_common(5)
        ]
        
        top_tones = [
            {'tone': tone, 'count': count, 'percentage': round(count / len(results) * 100, 1)}
            for tone, count in tone_counter.most_common(5)
        ]
        
        common_engagement = [
            {'technique': eng, 'count': count, 'percentage': round(count / len(results) * 100, 1)}
            for eng, count in engagement_counter.most_common(5)
        ]
        
        # 生成洞察
        insights = []
        
        # 钩子洞察
        if top_hooks:
            dominant_hook = top_hooks[0]
            if dominant_hook['percentage'] > 50:
                insights.append(
                    f"钩子偏好：{dominant_hook['type']}占比{dominant_hook['percentage']}%，建议尝试更多样化的钩子类型"
                )
            else:
                insights.append(
                    f"钩子分布较为均衡，{dominant_hook['type']}最常用({dominant_hook['percentage']}%)"
                )
        
        # 结构洞察
        if top_structures:
            dominant_structure = top_structures[0]
            if dominant_structure['percentage'] > 60:
                insights.append(
                    f"结构偏好：{dominant_structure['type']}占比{dominant_structure['percentage']}%，内容结构相对单一"
                )
        
        # 主题洞察
        if top_topics:
            if len(top_topics) == 1:
                insights.append(f"主题集中：内容专注于「{top_topics[0]['topic']}」领域")
            else:
                topics_str = '、'.join([t['topic'] for t in top_topics[:3]])
                insights.append(f"主题多元：主要涉及{topics_str}等领域")
        
        # 互动洞察
        if common_engagement:
            eng_count = len(common_engagement)
            if eng_count >= 3:
                insights.append(
                    f"互动丰富：使用了{engagement_counter.total()}种互动技巧，最常用的是「{common_engagement[0]['technique']}」"
                )
            else:
                insights.append(
                    "互动优化：建议增加更多互动引导技巧，提升观众参与度"
                )
        
        return {
            'top_hooks': top_hooks,
            'top_structures': top_structures,
            'top_topics': top_topics,
            'top_tones': top_tones,
            'common_engagement_techniques': common_engagement,
            'patterns_insights': insights
        }


# 便捷使用函数
def quick_batch_analyze(texts: List[str]) -> Dict:
    """快速批量分析文本列表"""
    analyzer = BatchAnalyzer()
    return analyzer.analyze_batch(texts)


def analyze_json_file(json_path: str) -> Dict:
    """快速分析 JSON 文件"""
    analyzer = BatchAnalyzer()
    return analyzer.analyze_from_json(json_path)


def analyze_csv_file(csv_path: str, text_column: str = 'content') -> Dict:
    """快速分析 CSV 文件"""
    analyzer = BatchAnalyzer()
    return analyzer.analyze_from_csv(csv_path, text_column)


if __name__ == "__main__":
    # 测试
    sample_texts = [
        """
        今天分享3个AI编程的绝招，学会了效率翻倍！
        
        第一，用Cursor的快捷键。很多人不知道，按住Cmd+K可以直接调用AI。
        第二，善用代码补全。不要一个一个敲，让AI帮你写完整的函数。
        第三，多用自然语言描述。越清晰的需求描述，生成的代码越准确。
        
        你平时用什么AI工具编程？评论区告诉我！
        觉得有用记得点赞收藏，关注我了解更多AI技巧。
        """,
        """
        为什么你的代码总是有bug？可能是你没用对方法！
        
        很多人写代码的时候，只关注功能实现，却忽略了代码质量。
        今天我告诉你5个让代码更健壮的技巧：
        1. 写单元测试
        2. 用类型注解
        3. 添加错误处理
        4. 代码审查
        5. 持续重构
        
        觉得有帮助的话，点个赞支持一下！
        """,
        """
        创业半年，收入从0到10万，我做对了这3件事！
        
        很多人觉得创业很难，但其实找对方法很重要。
        第一，选择合适的赛道。不要跟风，要看市场需求。
        第二，快速验证MVP。最小可行产品帮你省很多时间。
        第三，坚持用户反馈。用户的建议是最值钱的。
        
        关注我，下期分享更多创业干货！
        """
    ]
    
    print("="*60)
    print("批量分析测试")
    print("="*60)
    
    analyzer = BatchAnalyzer()
    result = analyzer.analyze_batch(sample_texts)
    
    print(f"\n分析数量: {result['successful_count']}/{result['total_count']}")
    print(f"\n【汇总统计】")
    summary = result['summary']
    print(f"平均字数: {summary['avg_word_count']}")
    print(f"平均句子数: {summary['avg_sentence_count']}")
    
    print(f"\n【钩子类型分布】")
    for hook, count in summary['hook_type_distribution'].items():
        print(f"  {hook}: {count}")
    
    print(f"\n【结构分布】")
    for structure, count in summary['structure_distribution'].items():
        print(f"  {structure}: {count}")
    
    print(f"\n【主题分布】")
    for topic, count in summary['topic_distribution'].items():
        print(f"  {topic}: {count}")
    
    print(f"\n【模式对比】")
    patterns = result['patterns']
    for insight in patterns['patterns_insights']:
        print(f"  • {insight}")
