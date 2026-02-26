#!/usr/bin/env python3
"""
报告生成器 - 生成内容分析可视化报告
"""

import os
import json
from typing import Dict, List, Any
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
import wordcloud

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['PingFang SC', 'SimHei', 'Hiragino Sans GB', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


class ReportGenerator:
    """分析报告生成器"""
    
    def __init__(self):
        self.colors = {
            'primary': '#FF6B6B',
            'secondary': '#4ECDC4',
            'accent': '#45B7D1',
            'warning': '#F7B731',
            'success': '#26DE81',
            'purple': '#A55EEA',
            'pink': '#FD79A8',
            'blue': '#0984E3',
        }
    
    def _normalize_content(self, content) -> Dict:
        """将 ContentAnalysis 对象或字典转换为标准字典格式"""
        if hasattr(content, '__dict__'):
            # ContentAnalysis 对象
            return {
                'word_count': content.word_count,
                'char_count': content.char_count,
                'sentence_count': content.sentence_count,
                'avg_sentence_length': content.avg_sentence_length,
                'hook_type': content.hook_type,
                'structure': content.structure,
                'topics': content.topics,
                'tone': content.tone,
                'engagement_techniques': content.engagement_techniques,
                'call_to_action': content.call_to_action,
                'key_points': content.key_points,
                'recommendations': content.recommendations
            }
        return content  # 已经是字典
    
    def generate_summary(self, analysis: Dict) -> str:
        """
        生成内容摘要
        
        Args:
            analysis: 分析结果字典
            
        Returns:
            摘要文本
        """
        content = analysis.get('content_analysis', analysis)
        
        # 转换为字典格式（兼容 ContentAnalysis 对象）
        content = self._normalize_content(content)
        
        # 提取关键指标
        word_count = content.get('word_count', 0)
        char_count = content.get('char_count', 0)
        hook_type = content.get('hook_type', '未知')
        structure = content.get('structure', '未知')
        topics = content.get('topics', [])
        tone = content.get('tone', '未知')
        engagement = content.get('engagement_techniques', [])
        
        summary = f"""
📊 内容分析摘要
{'='*40}

📝 基础数据:
   • 字数: {word_count} 字
   • 字符数: {char_count}
   • 句数: {content.get('sentence_count', 0)} 句
   • 平均句长: {content.get('avg_sentence_length', 0)} 词

🎯 内容特征:
   • 钩子类型: {hook_type}
   • 内容结构: {structure}
   • 主题领域: {', '.join(topics) if topics else '未识别'}
   • 语气风格: {tone}

💬 互动分析:
   • 互动技巧: {', '.join(engagement) if engagement else '未检测到'}
   • CTA数量: {len(content.get('call_to_action', []))} 个

📈 关键要点:
"""
        key_points = content.get('key_points', [])
        for i, point in enumerate(key_points[:3], 1):
            summary += f"   {i}. {point[:60]}{'...' if len(point) > 60 else ''}\n"
        
        return summary
    
    def generate_markdown(self, analysis: Dict, output_path: str) -> None:
        """
        生成 Markdown 格式报告
        
        Args:
            analysis: 分析结果
            output_path: 输出文件路径
        """
        content = analysis.get('content_analysis', analysis)
        
        # 转换为字典格式（兼容 ContentAnalysis 对象）
        content = self._normalize_content(content)
        
        # 构建 Markdown 内容
        md = f"""# 📊 小红书内容分析报告

---

## 1. 数据概览

| 指标 | 数值 |
|------|------|
| 字数 | {content.get('word_count', 0)} 字 |
| 字符数 | {content.get('char_count', 0)} |
| 句子数 | {content.get('sentence_count', 0)} 句 |
| 平均句长 | {content.get('avg_sentence_length', 0)} 词 |

---

## 2. 内容特征分析

### 2.1 钩子类型
> **{content.get('hook_type', '未知')}** 

### 2.2 内容结构
> **{content.get('structure', '未知')}**

### 2.3 主题领域
{', '.join(content.get('topics', [])) if content.get('topics') else '未识别'}

### 2.4 语气风格
> **{content.get('tone', '未知')}**

---

## 3. 互动元素分析

### 3.1 互动技巧
"""
        
        engagement = content.get('engagement_techniques', [])
        if engagement:
            for tech in engagement:
                md += f"- {tech}\n"
        else:
            md += "- 未检测到明显的互动技巧\n"
        
        md += """
### 3.2 行动召唤 (CTA)
"""
        ctas = content.get('call_to_action', [])
        if ctas:
            for cta in ctas:
                md += f"- {cta}\n"
        else:
            md += "- 未检测到明确的行动召唤\n"
        
        md += """
---

## 4. 关键要点

"""
        key_points = content.get('key_points', [])
        for i, point in enumerate(key_points, 1):
            md += f"{i}. {point}\n\n"
        
        if not key_points:
            md += "_未能提取到关键要点_\n"
        
        md += """
---

## 5. 优化建议

"""
        recommendations = content.get('recommendations', [])
        for i, rec in enumerate(recommendations, 1):
            # 处理多行建议
            rec_clean = rec.replace('\n', '\n   ')
            md += f"### {i}. {rec_clean}\n\n"
        
        if not recommendations:
            md += "_暂无优化建议_\n"
        
        # 添加图表引用
        md += """
---

## 6. 图表分析

> 📈 详细可视化图表请查看 HTML 报告

---

*报告生成时间: 由 xhs_analyzer 自动生成*
"""
        
        # 写入文件
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md)
        
        print(f"✅ Markdown 报告已生成: {output_path}")
    
    def generate_html(self, analysis: Dict, output_path: str) -> None:
        """
        生成 HTML 格式报告（带内嵌图表）
        
        Args:
            analysis: 分析结果
            output_path: 输出文件路径
        """
        content = analysis.get('content_analysis', analysis)
        
        # 转换为字典格式（兼容 ContentAnalysis 对象）
        content = self._normalize_content(content)
        
        # 先生成图表
        charts_dir = str(Path(output_path).parent / 'charts')
        Path(charts_dir).mkdir(parents=True, exist_ok=True)
        
        self.generate_charts({'content_analysis': content}, charts_dir)
        
        # 构建图表路径
        charts = {
            'hook_pie': 'charts/hook_type_pie.png',
            'structure_bar': 'charts/structure_bar.png',
            'wordcloud': 'charts/topic_wordcloud.png',
            'engagement': 'charts/engagement_stats.png'
        }
        
        # content 已经在前面规范化过了
        
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>小红书内容分析报告</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
            background: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
            color: white;
            padding: 40px;
            border-radius: 16px;
            text-align: center;
            margin-bottom: 30px;
        }}
        .header h1 {{
            font-size: 2em;
            margin-bottom: 10px;
        }}
        .header p {{
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .card {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        }}
        .card h2 {{
            color: #FF6B6B;
            font-size: 1.4em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #ffe5e5;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
        }}
        .stat-item {{
            background: #f8f9fa;
            padding: 16px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #FF6B6B;
        }}
        .stat-label {{
            color: #666;
            font-size: 0.9em;
        }}
        .tag {{
            display: inline-block;
            background: linear-gradient(135deg, #4ECDC4 0%, #44a8a0 100%);
            color: white;
            padding: 6px 16px;
            border-radius: 20px;
            margin: 4px;
            font-size: 0.9em;
        }}
        .chart-container {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin: 20px 0;
        }}
        .chart-box {{
            background: #f8f9fa;
            padding: 16px;
            border-radius: 8px;
            text-align: center;
        }}
        .chart-box img {{
            max-width: 100%;
            border-radius: 8px;
        }}
        .chart-box h4 {{
            margin-bottom: 12px;
            color: #333;
        }}
        .recommendation {{
            background: #fff9e6;
            border-left: 4px solid #F7B731;
            padding: 16px;
            margin: 12px 0;
            border-radius: 0 8px 8px 0;
        }}
        .recommendation h4 {{
            color: #d68910;
            margin-bottom: 8px;
        }}
        .key-point {{
            background: #e8f5e9;
            border-left: 4px solid #26DE81;
            padding: 12px 16px;
            margin: 8px 0;
            border-radius: 0 8px 8px 0;
        }}
        .footer {{
            text-align: center;
            padding: 30px;
            color: #999;
            font-size: 0.9em;
        }}
        @media (max-width: 768px) {{
            .chart-container {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 小红书内容分析报告</h1>
            <p>AI 驱动的内容分析 | 洞察爆款规律</p>
        </div>
        
        <div class="card">
            <h2>📈 数据概览</h2>
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-value">{content.get('word_count', 0)}</div>
                    <div class="stat-label">总字数</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{content.get('char_count', 0)}</div>
                    <div class="stat-label">字符数</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{content.get('sentence_count', 0)}</div>
                    <div class="stat-label">句子数</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{content.get('avg_sentence_length', 0)}</div>
                    <div class="stat-label">平均句长</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>🎯 内容特征</h2>
            <p><strong>钩子类型:</strong> <span class="tag">{content.get('hook_type', '未知')}</span></p>
            <p><strong>内容结构:</strong> <span class="tag">{content.get('structure', '未知')}</span></p>
            <p><strong>语气风格:</strong> <span class="tag">{content.get('tone', '未知')}</span></p>
            <p><strong>主题领域:</strong></p>
            <div style="margin-top: 10px;">
                {''.join(f'<span class="tag">{t}</span>' for t in content.get('topics', [])) or '<span class="tag">未识别</span>'}
            </div>
        </div>
        
        <div class="card">
            <h2>💬 互动元素</h2>
            <p><strong>互动技巧:</strong></p>
            <div style="margin-top: 10px;">
                {''.join(f'<span class="tag">{e}</span>' for e in content.get('engagement_techniques', [])) or '<span class="tag">未检测到</span>'}
            </div>
            <p style="margin-top: 16px;"><strong>行动召唤 (CTA):</strong></p>
            <ul style="margin-top: 8px; padding-left: 20px;">
                {''.join(f'<li>{c}</li>' for c in content.get('call_to_action', [])) or '<li>未检测到明确的 CTA</li>'}
            </ul>
        </div>
        
        <div class="card">
            <h2>📝 关键要点</h2>
            {''.join(f'<div class="key-point">{p}</div>' for p in content.get('key_points', [])) or '<p>未能提取到关键要点</p>'}
        </div>
        
        <div class="card">
            <h2>📊 图表分析</h2>
            <div class="chart-container">
                <div class="chart-box">
                    <h4>🎣 钩子类型分布</h4>
                    <img src="{charts['hook_pie']}" alt="钩子类型分布">
                </div>
                <div class="chart-box">
                    <h4>📐 内容结构分布</h4>
                    <img src="{charts['structure_bar']}" alt="内容结构分布">
                </div>
                <div class="chart-box">
                    <h4>☁️ 主题词云</h4>
                    <img src="{charts['wordcloud']}" alt="主题词云">
                </div>
                <div class="chart-box">
                    <h4>💡 互动技巧统计</h4>
                    <img src="{charts['engagement']}" alt="互动技巧统计">
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>💡 优化建议</h2>
            {''.join(f'<div class="recommendation"><h4>建议 {i}</h4><p>{r.replace(chr(10), "<br>")}</p></div>' for i, r in enumerate(content.get('recommendations', []), 1)) or '<p>暂无优化建议</p>'}
        </div>
        
        <div class="footer">
            <p>🤖 由 xhs_analyzer 自动生成</p>
        </div>
    </div>
</body>
</html>
"""
        
        # 写入文件
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ HTML 报告已生成: {output_path}")
    
    def generate_charts(self, analysis: Dict, output_dir: str) -> None:
        """
        生成统计图表
        
        Args:
            analysis: 分析结果
            output_dir: 输出目录
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        content = analysis.get('content_analysis', analysis)
        
        # 转换为字典格式（兼容 ContentAnalysis 对象）
        content = self._normalize_content(content)
        
        # 1. 钩子类型分布饼图
        self._generate_hook_pie(content, output_dir)
        
        # 2. 内容结构柱状图
        self._generate_structure_bar(content, output_dir)
        
        # 3. 主题词云图
        self._generate_wordcloud(content, output_dir)
        
        # 4. 互动技巧统计图
        self._generate_engagement_stats(content, output_dir)
        
        print(f"✅ 图表已生成: {output_dir}/")
    
    def _generate_hook_pie(self, content: Dict, output_dir: str) -> None:
        """生成钩子类型分布饼图"""
        hook_type = content.get('hook_type', '未知')
        
        # 创建模拟数据用于展示
        hook_data = {
            hook_type: 1,
            '其他类型': 2
        }
        
        # 颜色列表
        colors = [self.colors['primary'], self.colors['secondary'], 
                  self.colors['accent'], self.colors['warning'], 
                  self.colors['success'], self.colors['purple']]
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        wedges, texts, autotexts = ax.pie(
            hook_data.values(),
            labels=hook_data.keys(),
            autopct='%1.1f%%',
            colors=colors[:len(hook_data)],
            explode=[0.05] * len(hook_data),
            shadow=True,
            startangle=90
        )
        
        # 设置样式
        for text in texts:
            text.set_fontsize(11)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title('Hook Type Distribution', fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/hook_type_pie.png', dpi=150, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.close()
    
    def _generate_structure_bar(self, content: Dict, output_dir: str) -> None:
        """生成内容结构柱状图"""
        structure = content.get('structure', '未知')
        
        # 创建模拟数据用于展示
        structure_data = {
            structure: 1,
            '叙述结构': 1,
            '列表结构': 1,
            '问答结构': 1
        }
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        bars = ax.bar(
            list(structure_data.keys()),
            list(structure_data.values()),
            color=[self.colors['primary'], self.colors['secondary'],
                   self.colors['accent'], self.colors['warning']][:len(structure_data)],
            edgecolor='white',
            linewidth=1.5
        )
        
        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontweight='bold')
        
        ax.set_ylabel('数量', fontsize=12)
        ax.set_title('Content Structure Distribution', fontsize=14, fontweight='bold', pad=20)
        ax.set_ylim(0, max(structure_data.values()) * 1.3)
        
        # 美化
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(axis='x', rotation=15)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/structure_bar.png', dpi=150, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.close()
    
    def _generate_wordcloud(self, content: Dict, output_dir: str) -> None:
        """生成主题词云图"""
        topics = content.get('topics', [])
        
        # 使用主题词作为词云基础
        if topics:
            topic_text = ' '.join(topics * 3)  # 增加权重
        else:
            topic_text = '内容分析 AI 效率 技巧 方法'
        
        # 生成词云
        wc = wordcloud.WordCloud(
            width=800,
            height=400,
            background_color='white',
            max_words=50,
            colormap='RdYlBu_r',
            font_path=None,  # 使用系统字体
            prefer_horizontal=0.7,
            min_font_size=10
        )
        
        wc.generate(topic_text)
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        ax.set_title('Topic Wordcloud', fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/topic_wordcloud.png', dpi=150, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.close()
    
    def _generate_engagement_stats(self, content: Dict, output_dir: str) -> None:
        """生成互动技巧统计图"""
        engagement = content.get('engagement_techniques', [])
        
        # 统计各类型数量
        engagement_counts = Counter(engagement)
        
        # 如果没有数据，提供默认展示
        if not engagement_counts:
            engagement_counts = {'未检测到': 1}
        
        # 创建水平柱状图
        fig, ax = plt.subplots(figsize=(10, 6))
        
        y_pos = range(len(engagement_counts))
        colors = [self.colors['primary'], self.colors['secondary'],
                  self.colors['accent'], self.colors['warning'],
                  self.colors['success'], self.colors['purple']][:len(engagement_counts)]
        
        bars = ax.barh(
            y_pos,
            list(engagement_counts.values()),
            color=colors,
            edgecolor='white',
            linewidth=1.5
        )
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(list(engagement_counts.keys()))
        ax.invert_yaxis()
        
        # 添加数值标签
        for i, (bar, count) in enumerate(zip(bars, engagement_counts.values())):
            ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                   str(count), va='center', fontweight='bold')
        
        ax.set_xlabel('出现次数', fontsize=12)
        ax.set_title('Engagement Techniques Stats', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlim(0, max(engagement_counts.values()) * 1.3)
        
        # 美化
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/engagement_stats.png', dpi=150, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.close()


# 便捷使用函数
def generate_report(analysis: Dict, output_path: str, format: str = 'both') -> None:
    """
    便捷报告生成函数
    
    Args:
        analysis: 分析结果
        output_path: 输出路径
        format: 输出格式 ('markdown', 'html', 'both')
    """
    generator = ReportGenerator()
    
    if format in ('markdown', 'both'):
        md_path = output_path.replace('.html', '.md') if format == 'both' else output_path
        generator.generate_markdown(analysis, md_path)
    
    if format in ('html', 'both'):
        html_path = output_path.replace('.md', '.html') if format == 'both' else output_path
        generator.generate_html(analysis, html_path)


if __name__ == "__main__":
    # 测试代码
    from content_analyzer import ContentAnalyzer
    
    test_text = """
    今天分享3个AI编程的绝招，学会了效率翻倍！
    
    第一，用Cursor的快捷键。很多人不知道，按住Cmd+K可以直接调用AI。
    第二，善用代码补全。不要一个一个敲，让AI帮你写完整的函数。
    第三，多用自然语言描述。越清晰的需求描述，生成的代码越准确。
    
    你平时用什么AI工具编程？评论区告诉我！
    觉得有用记得点赞收藏，关注我了解更多AI技巧。
    """
    
    print("="*60)
    print("报告生成器测试")
    print("="*60)
    
    # 分析内容
    analyzer = ContentAnalyzer()
    result = analyzer.analyze(test_text)
    
    # 转换为字典
    analysis_dict = {
        'content_analysis': {
            'word_count': result.word_count,
            'char_count': result.char_count,
            'sentence_count': result.sentence_count,
            'avg_sentence_length': result.avg_sentence_length,
            'hook_type': result.hook_type,
            'structure': result.structure,
            'topics': result.topics,
            'tone': result.tone,
            'engagement_techniques': result.engagement_techniques,
            'call_to_action': result.call_to_action,
            'key_points': result.key_points,
            'recommendations': result.recommendations
        }
    }
    
    # 生成报告
    gen = ReportGenerator()
    
    print("\n生成摘要...")
    summary = gen.generate_summary(analysis_dict)
    print(summary)
    
    print("\n生成 Markdown 报告...")
    gen.generate_markdown(analysis_dict, '/tmp/test_report.md')
    
    print("\n生成 HTML 报告...")
    gen.generate_html(analysis_dict, '/tmp/test_report.html')
    
    print("\n生成图表...")
    gen.generate_charts(analysis_dict, '/tmp/charts')
    
    print("\n✅ 测试完成!")
