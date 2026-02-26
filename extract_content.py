#!/usr/bin/env python3
"""
小红书视频内容提取脚本
使用 faster-whisper 进行语音识别
"""

import os
import json
import subprocess
from pathlib import Path
from faster_whisper import WhisperModel

# 配置
PROJECT_DIR = Path("/Users/cory/.openclaw/workspace/xhs_analyzer")
RAW_DIR = PROJECT_DIR / "data" / "raw"
EXTRACT_DIR = PROJECT_DIR / "data" / "extracted"
AUDIO_DIR = EXTRACT_DIR / "audio"
OUTPUT_DIR = EXTRACT_DIR

# 确保目录存在
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# 获取所有视频文件
video_files = list(RAW_DIR.glob("*.mp4"))
print(f"找到 {len(video_files)} 个视频文件:")
for v in video_files:
    size_mb = v.stat().st_size / 1024 / 1024
    print(f"  - {v.name} ({size_mb:.1f} MB)")

# 使用 faster-whisper (使用 tiny 模型，更快)
print("\n加载 Whisper 模型 (tiny)...")
model = WhisperModel("tiny", device="cpu", compute_type="int8")

def extract_audio(video_path: Path, audio_path: Path):
    """使用 ffmpeg 提取音频"""
    if audio_path.exists():
        print(f"  音频已存在，跳过提取: {audio_path.name}")
        return True
    
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vn", "-acodec", "pcm_s16le",
        "-ar", "16000", "-ac", "1",
        str(audio_path)
    ]
    print(f"  提取音频: {audio_path.name}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  错误: {result.stderr}")
        return False
    return True

def transcribe_audio(audio_path: Path, output_json: Path):
    """转录音频"""
    print(f"  转录音频: {audio_path.name}")
    
    segments, info = model.transcribe(
        str(audio_path),
        language="zh",
        beam_size=5,
        vad_filter=True
    )
    
    results = []
    full_text = []
    
    print(f"  检测到语言: {info.language} (概率: {info.language_probability:.2f})")
    
    for segment in segments:
        text = segment.text.strip()
        results.append({
            "start": segment.start,
            "end": segment.end,
            "text": text
        })
        full_text.append(text)
    
    # 保存 JSON 格式（带时间戳）
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump({
            "language": info.language,
            "language_probability": info.language_probability,
            "segments": results,
            "full_text": "".join(full_text)
        }, f, ensure_ascii=False, indent=2)
    
    # 保存纯文本
    txt_path = output_json.with_suffix(".txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("".join(full_text))
    
    # 保存 SRT 字幕
    srt_path = output_json.with_suffix(".srt")
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(results, 1):
            start = format_srt_time(seg["start"])
            end = format_srt_time(seg["end"])
            f.write(f"{i}\n{start} --> {end}\n{seg['text']}\n\n")
    
    return len(results)

def format_srt_time(seconds: float) -> str:
    """格式化 SRT 时间"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

# 处理每个视频
print("\n开始处理...")
for video in video_files:
    print(f"\n处理: {video.name}")
    
    # 音频文件路径
    audio_name = video.stem + ".wav"
    audio_path = AUDIO_DIR / audio_name
    
    # 输出文件路径
    output_json = OUTPUT_DIR / f"{video.stem}_transcript.json"
    
    # 1. 提取音频
    if not extract_audio(video, audio_path):
        continue
    
    # 2. 转录
    try:
        num_segments = transcribe_audio(audio_path, output_json)
        print(f"  完成! 共 {num_segments} 个片段")
    except Exception as e:
        print(f"  转录错误: {e}")

print("\n✅ 全部完成!")
print(f"结果保存在: {EXTRACT_DIR}")
