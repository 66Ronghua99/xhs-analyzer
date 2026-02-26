#!/usr/bin/env python3
"""
基于公开可见内容创建模拟数据进行分析
数据来源：博主公开帖子的标题和结构特征
"""

from content_analyzer import ContentAnalysis

# ===== 第四种黑猩猩风格数据 =====
# 特征：硬核AI解读 + 深度思考 + 观点鲜明 + 长文
DISSIHONGXINGXING_DATA = [
    ContentAnalysis(
        title="Claude 4发布：这不是一次普通的模型更新",
        title_length=21,
        has_number=False,
        has_question=False,
        has_emotion=False,
        emoji_count=0,
        paragraph_count=12,
        avg_sentence_length=35.5,
        tone='professional',
        structure='opinion'
    ),
    ContentAnalysis(
        title="为什么说2024是AI应用的拐点？",
        title_length=18,
        has_number=True,
        has_question=True,
        has_emotion=False,
        emoji_count=1,
        paragraph_count=10,
        avg_sentence_length=28.3,
        tone='professional',
        structure='analysis'
    ),
    ContentAnalysis(
        title="深度解读：OpenAI的下一步棋会怎么走",
        title_length=22,
        has_number=False,
        has_question=False,
        has_emotion=False,
        emoji_count=0,
        paragraph_count=15,
        avg_sentence_length=32.8,
        tone='professional',
        structure='analysis'
    ),
    ContentAnalysis(
        title="我用AI重构了整个工作流，效率提升了10倍",
        title_length=27,
        has_number=True,
        has_question=False,
        has_emotion=False,
        emoji_count=0,
        paragraph_count=8,
        avg_sentence_length=24.5,
        tone='professional',
        structure='story'
    ),
    ContentAnalysis(
        title="聊聊AI编程工具的终局：Cursor之后是什么？",
        title_length=26,
        has_number=False,
        has_question=True,
        has_emotion=False,
        emoji_count=0,
        paragraph_count=11,
        avg_sentence_length=30.2,
        tone='casual',
        structure='opinion'
    ),
]

# ===== 老徐在创造风格数据 =====
# 特征：产品思维 + 创业记录 + 实操干货 + 个人IP
LAOXUZAICHUANGZAO_DATA = [
    ContentAnalysis(
        title="独立开发者月入10万的3个心法",
        title_length=17,
        has_number=True,
        has_question=False,
        has_emotion=False,
        emoji_count=1,
        paragraph_count=6,
        avg_sentence_length=18.5,
        tone='professional',
        structure='list'
    ),
    ContentAnalysis(
        title="为什么你的AI产品没人用？我踩过的5个坑",
        title_length=25,
        has_number=True,
        has_question=True,
        has_emotion=False,
        emoji_count=0,
        paragraph_count=8,
        avg_sentence_length=20.3,
        tone='personal',
        structure='story'
    ),
    ContentAnalysis(
        title="🔥 我的AI产品被 Product Hunt 推荐了，分享复盘",
        title_length=28,
        has_number=False,
        has_question=False,
        has_emotion=True,
        emoji_count=2,
        paragraph_count=10,
        avg_sentence_length=22.7,
        tone='emotional',
        structure='story'
    ),
    ContentAnalysis(
        title="从0到1做一个AI工具，我只花了3天",
        title_length=20,
        has_number=True,
        has_question=False,
        has_emotion=False,
        emoji_count=0,
        paragraph_count=7,
        avg_sentence_length=19.2,
        tone='casual',
        structure='story'
    ),
    ContentAnalysis(
        title="Cursor + V0 真的能让程序员失业吗？实测一周告诉你",
        title_length=31,
        has_number=False,
        has_question=True,
        has_emotion=False,
        emoji_count=0,
        paragraph_count=9,
        avg_sentence_length=24.5,
        tone='professional',
        structure='review'
    ),
    ContentAnalysis(
        title="💡 我发现了一个蓝海市场：AI+垂直场景",
        title_length=23,
        has_number=False,
        has_question=False,
        has_emotion=True,
        emoji_count=1,
        paragraph_count=8,
        avg_sentence_length=21.3,
        tone='emotional',
        structure='opinion'
    ),
]

# ===== AI新闻/思考类博主风格数据 =====
# 特征：追热点 + 快讯 + 短平快解读
AI_NEWS_BLOGGER_DATA = [
    ContentAnalysis(
        title="刚刚！Claude 4深夜发布，性能超越GPT-4",
        title_length=25,
        has_number=True,
        has_question=False,
        has_emotion=False,
        emoji_count=0,
        paragraph_count=5,
        avg_sentence_length=16.5,
        tone='professional',
        structure='news'
    ),
    ContentAnalysis(
        title="🔥 OpenAI又要搞大事了，这次是真的",
        title_length=20,
        has_number=False,
        has_question=False,
        has_emotion=True,
        emoji_count=1,
        paragraph_count=4,
        avg_sentence_length=14.2,
        tone='emotional',
        structure='news'
    ),
    ContentAnalysis(
        title="3分钟看懂今天AI圈发生了什么",
        title_length=16,
        has_number=True,
        has_question=False,
        has_emotion=False,
        emoji_count=0,
        paragraph_count=6,
        avg_sentence_length=12.8,
        tone='casual',
        structure='list'
    ),
    ContentAnalysis(
        title="ChatGPT今天的新功能，我觉得有点意思",
        title_length=22,
        has_number=False,
        has_question=False,
        has_emotion=False,
        emoji_count=0,
        paragraph_count=5,
        avg_sentence_length=18.5,
        tone='casual',
        structure='review'
    ),
    ContentAnalysis(
        title="❗️ 一个重磅消息：谷歌Gemini有大动作",
        title_length=21,
        has_number=False,
        has_question=False,
        has_emotion=True,
        emoji_count=1,
        paragraph_count=4,
        avg_sentence_length=15.3,
        tone='emotional',
        structure='news'
    ),
]


def get_all_mock_data():
    """获取所有模拟数据"""
    return {
        '第四种黑猩猩': DISSIHONGXINGXING_DATA,
        '老徐在创造': LAOXUZAICHUANGZAO_DATA,
        'AI新闻类': AI_NEWS_BLOGGER_DATA
    }


if __name__ == "__main__":
    # 测试数据
    data = get_all_mock_data()
    for name, items in data.items():
        print(f"\n{name}: {len(items)} 条样本")
        for item in items[:2]:
            print(f"  - {item.title[:30]}...")
