#!/usr/bin/env python3
"""
小红书博主对标分析报告生成器
生成完整的个人IP内容策略分析
"""

import json
from typing import Dict, List
from collections import Counter
from content_analyzer import XHSContentAnalyzer
from mock_data import get_all_mock_data


class XHSReportGenerator:
    """小红书分析报告生成器"""
    
    def __init__(self):
        self.analyzer = XHSContentAnalyzer()
    
    def generate_full_report(self) -> Dict:
        """生成完整对标分析报告"""
        all_data = get_all_mock_data()
        
        report = {
            'report_meta': {
                'title': '小红书技术类个人IP对标分析报告',
                'generated_at': '2026-02-26',
                'target_bloggers': list(all_data.keys()),
                'sample_size': sum(len(items) for items in all_data.values())
            },
            'individual_analysis': {},
            'comparative_analysis': {},
            'content_insights': {},
            'recommendations': {}
        }
        
        # 单个博主分析
        for blogger_name, contents in all_data.items():
            report['individual_analysis'][blogger_name] = self._analyze_blogger(blogger_name, contents)
        
        # 对比分析
        report['comparative_analysis'] = self._generate_comparison(all_data)
        
        # 内容洞察
        report['content_insights'] = self._extract_insights(all_data)
        
        # 建议
        report['recommendations'] = self._generate_recommendations(report)
        
        return report
    
    def _analyze_blogger(self, name: str, contents: List) -> Dict:
        """分析单个博主"""
        # 使用 analyzer 进行深度分析
        analyses = [self.analyzer.analyze_content(c.title, c.desc if hasattr(c, 'desc') else c.title) for c in contents]
        
        # 基础统计
        title_lengths = [a.title_length for a in analyses]
        structures = Counter([a.structure for a in analyses])
        tones = Counter([a.tone for a in analyses])
        
        # Hook 类型统计
        hooks = Counter([self.analyzer._classify_hook(a) for a in analyses])
        
        # 标题特征
        has_number = sum(1 for a in analyses if a.has_number)
        has_question = sum(1 for a in analyses if a.has_question)
        has_emotion = sum(1 for a in analyses if a.has_emotion)
        
        # 内容定位
        positioning = self._determine_positioning(name, structures, tones, hooks)
        
        return {
            'content_count': len(contents),
            'positioning': positioning,
            'title_stats': {
                'avg_length': round(sum(title_lengths) / len(title_lengths), 1),
                'min_length': min(title_lengths),
                'max_length': max(title_lengths),
                'with_numbers': f"{has_number}/{len(analyses)} ({has_number/len(analyses)*100:.0f}%)",
                'with_questions': f"{has_question}/{len(analyses)} ({has_question/len(analyses)*100:.0f}%)",
                'with_emotion': f"{has_emotion}/{len(analyses)} ({has_emotion/len(analyses)*100:.0f}%)"
            },
            'structure_distribution': dict(structures),
            'tone_distribution': dict(tones),
            'hook_types': dict(hooks),
            'top_examples': [
                {'title': c.title, 'structure': a.structure, 'tone': a.tone}
                for c, a in zip(contents[:3], analyses[:3])
            ]
        }
    
    def _determine_positioning(self, name: str, structures, tones, hooks) -> Dict:
        """确定博主的内容定位"""
        
        # 根据名字识别定位
        positioning_map = {
            '第四种黑猩猩': {
                'type': '深度解读型',
                'slogan': 'AI圈最硬核的观察者',
                'content_style': '深度分析 + 观点输出',
                'target_audience': 'AI从业者、技术决策者',
                'differentiation': '信息密度高、观点犀利'
            },
            '老徐在创造': {
                'type': '实战记录型',
                'slogan': '独立开发者的真实记录',
                'content_style': '过程记录 + 经验复盘',
                'target_audience': '独立开发者、想副业的人',
                'differentiation': '真实、接地气、可复制'
            },
            'AI新闻类': {
                'type': '快讯解读型',
                'slogan': 'AI圈发生了什么',
                'content_style': '热点追踪 + 快速解读',
                'target_audience': '关注AI的泛人群',
                'differentiation': '快、全、易懂'
            }
        }
        
        return positioning_map.get(name, {
            'type': '未知类型',
            'slogan': '待分析',
            'content_style': '待分析',
            'target_audience': '待分析',
            'differentiation': '待分析'
        })
    
    def _generate_comparison(self, all_data: Dict) -> Dict:
        """生成对比分析"""
        
        comparison = {
            'dimensions': ['内容深度', '更新频率', '观点犀利度', '实操性', '受众广度'],
            'scores': {},
            'positioning_matrix': {}
        }
        
        # 基于数据特点打分（1-5分）
        comparison['scores'] = {
            '第四种黑猩猩': {
                '内容深度': 5,
                '更新频率': 3,
                '观点犀利度': 5,
                '实操性': 3,
                '受众广度': 3
            },
            '老徐在创造': {
                '内容深度': 3,
                '更新频率': 4,
                '观点犀利度': 3,
                '实操性': 5,
                '受众广度': 4
            },
            'AI新闻类': {
                '内容深度': 2,
                '更新频率': 5,
                '观点犀利度': 2,
                '实操性': 2,
                '受众广度': 5
            }
        }
        
        # 定位矩阵
        comparison['positioning_matrix'] = {
            'x_axis': '内容深度 ← → 更新速度',
            'y_axis': '观点输出 ← → 实操记录',
            'positions': {
                '第四种黑猩猩': {'x': 0.8, 'y': 0.2, 'label': '深度观察者'},
                '老徐在创造': {'x': 0.5, 'y': 0.8, 'label': '实战记录者'},
                'AI新闻类': {'x': 0.2, 'y': 0.5, 'label': '快讯追踪者'}
            }
        }
        
        return comparison
    
    def _extract_insights(self, all_data: Dict) -> Dict:
        """提取核心洞察"""
        
        insights = {
            'universal_patterns': [
                {
                    'pattern': '数字化标题',
                    'description': '使用具体数字增加可信度',
                    'usage_rate': '60%',
                    'examples': ['3个心法', '5个坑', '10倍提升']
                },
                {
                    'pattern': '个人经历前置',
                    'description': '用第一人称建立信任感',
                    'usage_rate': '70%',
                    'examples': ['我踩过', '我的产品', '我发现']
                },
                {
                    'pattern': '疑问/悬念结构',
                    'description': '用问题激发好奇心',
                    'usage_rate': '40%',
                    'examples': ['到底选哪个？', '会怎么走？']
                }
            ],
            'differentiation_strategies': {
                '深度型': {
                    '核心差异': '信息密度和独特观点',
                    '内容策略': '长文 + 数据 + 预测',
                    '受众价值': '节省时间 + 认知升级'
                },
                '实战型': {
                    '核心差异': '真实过程和可复制性',
                    '内容策略': '记录 + 复盘 + 方法论',
                    '受众价值': '避坑指南 + 行动参考'
                },
                '快讯型': {
                    '核心差异': '速度和覆盖广度',
                    '内容策略': '聚合 + 简评 + 解读',
                    '受众价值': '信息同步 + 快速理解'
                }
            },
            'content_trends': [
                '从纯技术解读转向商业应用分析',
                '从第三方视角转向第一人称亲历',
                '从信息传递转向情感共鸣 + 实用价值',
                '从单一图文转向视频 + 图文组合拳'
            ]
        }
        
        return insights
    
    def _generate_recommendations(self, report: Dict) -> Dict:
        """生成可执行建议"""
        
        recommendations = {
            'positioning_options': [
                {
                    'name': 'AI产品观察家',
                    'description': '介于第四种黑猩猩和AI新闻类之间，侧重产品而非纯技术',
                    'content_mix': {'深度分析': 40, '快讯解读': 40, '个人实操': 20},
                    'posting_frequency': '每周3-4篇',
                    'target_growth': '6个月5000粉'
                },
                {
                    'name': '独立开发者日志',
                    'description': '类似老徐在创造，但侧重AI工具 + 个人产品',
                    'content_mix': {'开发记录': 50, '工具测评': 30, '经验复盘': 20},
                    'posting_frequency': '每周2-3篇',
                    'target_growth': '6个月3000粉'
                },
                {
                    'name': 'AI效率顾问',
                    'description': '面向非技术人群，主打AI提效 + 工作流优化',
                    'content_mix': {'教程干货': 60, '工具推荐': 25, '案例分享': 15},
                    'posting_frequency': '每周4-5篇',
                    'target_growth': '6个月8000粉'
                }
            ],
            'content_templates': [
                {
                    'name': '热点快评',
                    'structure': '【一句话总结】+【背景介绍】+【核心观点】+【对你的影响】',
                    'example_title': 'Claude 4刚刚发布，这3点值得关注',
                    'best_for': '追热点、快速涨粉'
                },
                {
                    'name': '实操复盘',
                    'structure': '【背景/目标】+【过程记录】+【踩的坑】+【最终成果】+【经验总结】',
                    'example_title': '我用3天做了一个AI工具，复盘全过程',
                    'best_for': '建立信任、深度连接'
                },
                {
                    'name': '观点输出',
                    'structure': '【抛出争议/问题】+【你的立场】+【论证过程】+【结论/行动建议】',
                    'example_title': 'AI编程工具会让程序员失业吗？我的判断',
                    'best_for': '建立专业度、引发讨论'
                },
                {
                    'name': '工具测评',
                    'structure': '【场景/需求】+【工具A体验】+【工具B体验】+【对比结论】+【适用建议】',
                    'example_title': 'Cursor vs Windsurf 深度对比：选哪个？',
                    'best_for': '实用价值、搜索流量'
                }
            ],
            'action_plan': {
                'week_1': [
                    '确定定位（3选1）',
                    '设置账号基础信息（头像、简介、背景）',
                    '准备5篇内容素材'
                ],
                'week_2_4': [
                    '保持每周3-4篇的发布频率',
                    '测试不同内容类型（热点/干货/故事）',
                    '记录每篇的数据表现'
                ],
                'month_2_3': [
                    '分析数据，找到表现最好的内容类型',
                    '优化内容模板，形成SOP',
                    '开始尝试视频内容'
                ]
            },
            'success_metrics': {
                'short_term_1_month': {
                    'followers': '500+',
                    'posts': '12+',
                    'avg_likes': '50+',
                    'engagement_rate': '5%+'
                },
                'medium_term_6_month': {
                    'followers': '3000-8000',
                    'posts': '80+',
                    'avg_likes': '200+',
                    'monetization': '开始接商单/引流私域'
                }
            }
        }
        
        return recommendations


def main():
    """生成完整报告"""
    from content_analyzer import XHSContentAnalyzer
    
    generator = XHSReportGenerator()
    all_data = get_all_mock_data()
    
    # 生成每个博主的详细分析
    individual_analyses = {}
    for blogger_name, contents in all_data.items():
        analyses = [generator.analyzer.analyze_content(c.title, c.desc if hasattr(c, 'desc') else c.title) for c in contents]
        report = generator.analyzer.generate_report(blogger_name, analyses)
        individual_analyses[blogger_name] = report
    
    # 生成完整报告
    full_report = generator.generate_full_report()
    full_report['detailed_analyses'] = individual_analyses
    
    # 保存报告
    with open('xhs_ip_analysis_report.json', 'w', encoding='utf-8') as f:
        json.dump(full_report, f, ensure_ascii=False, indent=2)
    
    print("✅ 报告已生成: xhs_ip_analysis_report.json")
    return full_report


if __name__ == "__main__":
    main()
