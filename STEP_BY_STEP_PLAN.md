# 小红书视频分析工具 - 分步开发计划

## 执行策略
- **小步快跑**：每个步骤 15-30 分钟可完成
- **结果可验证**：每个步骤有明确的验证命令和预期输出
- **并行执行**：使用 subagent 同时执行独立步骤
- **视频下载**：用户协助，放在 `data/raw/` 目录

---

## 步骤 1：项目基础验证 ✅ (已完成)

### 任务
验证项目结构已就绪

### 验证命令
```bash
cd /Users/cory/.openclaw/workspace/xhs_analyzer
ls -la
cat README.md | head -20
python3 -c "import sys; print(sys.version)"
```

### 预期输出
```
drwxr-xr-x  12 cory  staff   384 Feb 26 10:00 .
drwxr-xr-x  10 cory  staff   320 Feb 26 09:00 ..
-rw-r--r--   1 cory  staff  2419 Feb 26 10:00 README.md
-rw-r--r--   1 cory  staff   472 Feb 26 10:00 requirements.txt
drwxr-xr-x   3 cory  staff    96 Feb 26 10:00 src
Python 3.14.2
```

### 实际结果：✅ 已完成

---

## 步骤 2：批量分析器开发 ⏳ (当前)

### 任务
创建 `src/batch_analyzer.py`，支持从文件读取多条文案并批量分析

### 代码要求
```python
# 必须实现的功能：
1. 从 JSON/CSV 读取多条文案
2. 批量调用 ContentAnalyzer
3. 统计高频模式
4. 生成对比分析报告
```

### 验证命令
```bash
cd /Users/cory/.openclaw/workspace/xhs_analyzer
source venv/bin/activate

# 创建测试数据
cat > test_data.json << 'EOF'
{
  "videos": [
    {
      "title": "震惊！我用AI 3天做出了一个产品",
      "content": "今天分享我的经历...",
      "author": "博主A",
      "likes": 12000
    },
    {
      "title": "为什么说2024是AI应用的拐点？",
      "content": "深度分析...",
      "author": "博主B",
      "likes": 8500
    }
  ]
}
EOF

# 运行批量分析
python3 -c "
from src.batch_analyzer import BatchAnalyzer
analyzer = BatchAnalyzer()
results = analyzer.analyze_from_json('test_data.json')
print(f'分析了 {len(results)} 条内容')
print(f'高频钩子: {results.get("common_hooks", [])}')
"
```

### 预期输出
```
分析了 2 条内容
高频钩子: ['情感共鸣', '疑问/悬念']
内容结构分布: {'故事结构': 1, '分析结构': 1}
```

### 交付物
- `src/batch_analyzer.py` - 批量分析器
- `test_batch.py` - 单元测试

### 实际结果：⏳ 进行中

---

## 步骤 3：报告生成器开发 ⏳

### 任务
创建 `src/report_generator.py`，生成可视化分析报告

### 代码要求
```python
# 必须实现的功能：
1. 生成 Markdown 报告
2. 生成 HTML 报告（带简单图表）
3. 包含统计图表（使用 matplotlib）
4. 输出内容优化建议
```

### 验证命令
```bash
cd /Users/cory/.openclaw/workspace/xhs_analyzer
source venv/bin/activate

# 运行报告生成
python3 -c "
from src.report_generator import ReportGenerator
from src.batch_analyzer import BatchAnalyzer

# 分析数据
analyzer = BatchAnalyzer()
analysis = analyzer.analyze_from_json('test_data.json')

# 生成报告
gen = ReportGenerator()
gen.generate_markdown(analysis, 'report.md')
gen.generate_html(analysis, 'report.html')
print('报告已生成: report.md, report.html')
"

# 验证文件存在
ls -lh report.md report.html
```

### 预期输出
```
报告已生成: report.md, report.html
-rw-r--r--  1 cory  staff   12K Feb 26 11:00 report.md
-rw-r--r--  1 cory  staff   25K Feb 26 11:00 report.html
```

### 交付物
- `src/report_generator.py` - 报告生成器
- `templates/` - 报告模板目录

### 实际结果：⏳ 待开始

---

## 步骤 4：模板提取器开发 ⏳

### 任务
创建 `src/template_extractor.py`，从分析结果中提取可复用模板

### 代码要求
```python
# 必须实现的功能：
1. 识别高频内容模式
2. 提取标题公式
3. 生成开头/结尾模板
4. 输出可复用的内容框架
```

### 验证命令
```bash
cd /Users/cory/.openclaw/workspace/xhs_analyzer
source venv/bin/activate

# 运行模板提取
python3 -c "
from src.template_extractor import TemplateExtractor
from src.batch_analyzer import BatchAnalyzer

# 分析数据
analyzer = BatchAnalyzer()
analysis = analyzer.analyze_from_json('test_data.json')

# 提取模板
extractor = TemplateExtractor()
templates = extractor.extract_templates(analysis)

# 输出结果
import json
print(json.dumps(templates, indent=2, ensure_ascii=False))
"
```

### 预期输出
```json
{
  "title_templates": [
    {
      "type": "数字型",
      "formula": "{数字}个{技巧/方法}让你{结果}",
      "examples": ["3个AI技巧让你效率翻倍"]
    }
  ],
  "opening_templates": [
    {
      "type": "悬念型",
      "template": "今天分享{数字}个{主题}，学会了{结果}"
    }
  ]
}
```

### 交付物
- `src/template_extractor.py` - 模板提取器

### 实际结果：⏳ 待开始

---

## 步骤 5：CLI 界面开发 ⏳

### 任务
创建 `cli.py`，提供友好的命令行界面

### 代码要求
```python
# 必须实现的功能：
1. 主命令：xhs-analyze
2. 子命令：analyze, batch, extract, report
3. 参数解析
4. 帮助信息
```

### 验证命令
```bash
cd /Users/cory/.openclaw/workspace/xhs_analyzer
source venv/bin/activate

# 查看帮助
python3 cli.py --help

# 分析单个文件
python3 cli.py analyze --input text.txt --output result.json

# 批量分析
python3 cli.py batch --input data.json --output report.html

# 生成报告
python3 cli.py report --input analysis.json --format html
```

### 预期输出
```
$ python3 cli.py --help
usage: cli.py [-h] {analyze,batch,extract,report} ...

小红书视频内容分析工具

positional arguments:
  {analyze,batch,extract,report}
    analyze            分析单个内容
    batch              批量分析
    extract            提取模板
    report             生成报告

optional arguments:
  -h, --help           show this help message and exit
```

### 交付物
- `cli.py` - 命令行入口

### 实际结果：⏳ 待开始

---

## 视频文件目录约定

### 用户下载的视频放置位置：
```
xhs_analyzer/
└── data/
    └── raw/              # 原始视频文件
        ├── 第四种黑猩猩/
        │   ├── video_001.mp4
        │   ├── video_002.mp4
        │   └── metadata.json
        └── 老徐在创造/
            ├── video_001.mp4
            └── metadata.json
```

### metadata.json 格式：
```json
{
  "video_id": "xxx",
  "title": "视频标题",
  "author": "博主名",
  "url": "原始链接",
  "download_time": "2024-01-15T10:30:00",
  "duration": 120
}
```

---

## 执行顺序建议

### 方案A：小步快跑（推荐）
1. **Step 2.1** - 完善批量分析器（30分钟）✅
2. **Step 2.2** - 创建报告生成器（30分钟）
3. **Step 4** - 模板提取器（30分钟）
4. **Step 3** - 字幕提取（你提供视频后）
5. **Step 5** - CLI界面（可选）

### 方案B：并行开发
- Subagent 1: 负责步骤 2.1 + 2.2（分析模块）
- Subagent 2: 负责步骤 4（模板提取）
- 主会话: 负责协调和验证

---

## 立即开始

我立即创建 Step 2.1（批量分析器）和 Step 2.2（报告生成器）。这两步完成后，你就能立即使用工具分析内容了！

**需要我立即开始吗？** (回复 "开始" 或 "Start" 立即执行)