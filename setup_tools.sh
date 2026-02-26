#!/bin/bash
# 安装视频分析所需工具

echo "====================================="
echo "安装小红书视频分析工具链"
echo "====================================="

# 检查 Homebrew
if ! command -v brew &> /dev/null; then
    echo "[错误] 需要 Homebrew，请先安装: https://brew.sh"
    exit 1
fi

# 1. 安装 yt-dlp (视频下载)
echo "[1/5] 安装 yt-dlp..."
if ! command -v yt-dlp &> /dev/null; then
    brew install yt-dlp
else
    echo "    yt-dlp 已安装"
fi

# 2. 安装 ffmpeg (音视频处理)
echo "[2/5] 安装 ffmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    brew install ffmpeg
else
    echo "    ffmpeg 已安装"
fi

# 3. 安装 Whisper (字幕提取)
echo "[3/5] 安装 Whisper..."
if ! command -v whisper &> /dev/null; then
    pip3 install -U openai-whisper
else
    echo "    Whisper 已安装"
fi

# 4. 安装 Python 依赖
echo "[4/5] 安装 Python 依赖..."
pip3 install yt-dlp ffmpeg-python

# 5. 检查安装结果
echo "[5/5] 检查安装结果..."
echo ""
echo "====================================="
echo "安装检查结果:"
echo "====================================="

for tool in yt-dlp ffmpeg whisper; do
    if command -v $tool &> /dev/null; then
        version=$($tool --version 2>&1 | head -n 1)
        echo "✅ $tool: $version"
    else
        echo "❌ $tool: 未安装"
    fi
done

echo ""
echo "====================================="
echo "使用说明:"
echo "====================================="
echo "1. 下载视频:"
echo "   yt-dlp '视频URL' -o 'output.mp4'"
echo ""
echo "2. 提取音频:"
echo "   ffmpeg -i video.mp4 -vn -acodec copy audio.aac"
echo ""
echo "3. 生成字幕:"
echo "   whisper audio.aac --model base --language Chinese"
echo ""
echo "====================================="
