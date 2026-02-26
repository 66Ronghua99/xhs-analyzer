# 小红书视频内容深度分析工具

## 项目结构

```
xhs_analyzer/
├── README.md                 # 项目说明
├── requirements.txt          # Python依赖
├── setup.sh                 # 安装脚本
├── config.yaml              # 配置文件
│
├── src/                     # 源代码
│   ├── __init__.py
│   ├── downloader.py        # 视频下载器
│   ├── subtitle_extractor.py # 字幕提取器
│   ├── content_analyzer.py  # 内容分析器
│   └── report_generator.py  # 报告生成器
│
├── scripts/                 # 工具脚本
│   ├── download_video.sh
│   ├── extract_audio.sh
│   └── analyze_content.py
│
├── data/                    # 数据目录
│   ├── raw/                 # 原始视频
│   ├── audio/               # 提取的音频
│   ├── subtitles/           # 字幕文件
│   └── reports/             # 分析报告
│
└── tests/                   # 测试目录
    └── test_analyzer.py
```

## 功能模块

### 1. 视频下载器 (Video Downloader)
- 支持小红书视频下载
- 使用 yt-dlp 或 you-get
- Cookie 登录支持

### 2. 字幕提取器 (Subtitle Extractor)
- Whisper 语音识别
- 支持中文和英文
- 生成 SRT/VTT 字幕文件

### 3. 内容分析器 (Content Analyzer)
- 钩子（Hook）类型识别
- 内容结构分析
- 互动技巧提取
- 情感倾向分析

### 4. 报告生成器 (Report Generator)
- 可视化数据图表
- 对比分析报告
- 内容优化建议

## 快速开始

### 安装依赖

```bash
# 1. 克隆项目
git clone <repo-url>
cd xhs_analyzer

# 2. 运行安装脚本
bash setup.sh

# 3. 安装 Python 依赖
pip install -r requirements.txt
```

### 配置 Cookie

编辑 `config.yaml`:

```yaml
xiaohongshu:
  cookie: "your_cookie_here"
  user_agent: "Mozilla/5.0 ..."
```

### 运行分析

```bash
# 分析单个视频
python -m src.analyze --url "https://xiaohongshu.com/..." --output report.html

# 批量分析
python -m src.batch_analyze --urls urls.txt --output reports/
```

## API 使用

```python
from src.downloader import VideoDownloader
from src.subtitle_extractor import SubtitleExtractor
from src.content_analyzer import ContentAnalyzer

# 下载视频
downloader = VideoDownloader()
video_path = downloader.download("https://xiaohongshu.com/...")

# 提取字幕
extractor = SubtitleExtractor()
subtitles = extractor.extract(video_path)

# 分析内容
analyzer = ContentAnalyzer()
analysis = analyzer.analyze(subtitles['full_text'])

# 生成报告
print(f"钩子类型: {analysis['hook_type']}")
print(f"内容结构: {analysis['structure']}")
print(f"互动技巧: {', '.join(analysis['engagement_techniques'])}")
```

## 开发计划

### Phase 1: 基础功能 (已完成)
- [x] 项目结构搭建
- [x] Cookie 登录支持
- [x] 基础分析框架

### Phase 2: 核心功能 (进行中)
- [ ] 视频下载器优化
- [ ] Whisper 字幕提取
- [ ] 内容分析算法

### Phase 3: 高级功能 (计划中)
- [ ] 可视化报告
- [ ] 批量分析
- [ ] 竞品对比

## 贡献指南

1. Fork 项目
2. 创建 feature 分支
3. 提交代码
4. 创建 Pull Request

## 许可证

MIT License
