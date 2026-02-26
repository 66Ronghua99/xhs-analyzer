#!/usr/bin/env python3
"""
使用 Whisper Small 模型提取视频字幕
"""

import os
import sys
import json
import time
from pathlib import Path
import whisper

def format_timestamp(seconds):
    """格式化时间戳为 SRT 格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def extract_subtitles(video_path, output_dir, model):
    """提取字幕"""
    print(f"\n{'='*60}")
    print(f"处理: {os.path.basename(video_path)}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        # 转录
        print("正在转录（使用 small 模型，可能需要几分钟）...")
        result = model.transcribe(
            video_path,
            language="zh",
            task="transcribe",
            verbose=True
        )
        
        base_name = Path(video_path).stem
        
        # 1. 保存完整文本
        text_path = os.path.join(output_dir, f"{base_name}_full.txt")
        with open(text_path, "w", encoding="utf-8") as f:
            f.write(result["text"])
        print(f"✅ 完整文本: {text_path}")
        
        # 2. 保存 SRT 字幕
        srt_path = os.path.join(output_dir, f"{base_name}.srt")
        with open(srt_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(result["segments"], 1):
                start = format_timestamp(segment["start"])
                end = format_timestamp(segment["end"])
                f.write(f"{i}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{segment['text'].strip()}\n\n")
        print(f"✅ SRT 字幕: {srt_path}")
        
        # 3. 保存 JSON
        json_path = os.path.join(output_dir, f"{base_name}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"✅ JSON 数据: {json_path}")
        
        # 统计
        elapsed = time.time() - start_time
        print(f"\n📊 统计:")
        print(f"   总时长: {result.get('duration', 0):.1f} 秒")
        print(f"   总字数: {len(result['text'])}")
        print(f"   片段数: {len(result['segments'])}")
        print(f"   处理时间: {elapsed:.1f} 秒")
        print(f"   速度比: {elapsed/result.get('duration', 1):.2f}x")
        
        return {
            "status": "success",
            "video": os.path.basename(video_path),
            "text_length": len(result["text"]),
            "segments": len(result["segments"]),
            "duration": result.get("duration", 0),
            "elapsed_time": elapsed
        }
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "video": os.path.basename(video_path),
            "error": str(e)
        }

def main():
    # 目录设置
    video_dir = "/Users/cory/.openclaw/workspace/xhs_analyzer/data/raw"
    output_dir = "/Users/cory/.openclaw/workspace/xhs_analyzer/data/extracted"
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("="*60)
    print("小红书视频字幕提取 (Whisper Small 模型)")
    print("="*60)
    
    # 加载模型（只加载一次）
    print("\n🔄 加载 Whisper Small 模型...")
    print("   (首次加载需要下载约 500MB 模型文件)")
    start_load = time.time()
    model = whisper.load_model("small")
    load_time = time.time() - start_load
    print(f"✅ 模型加载完成 ({load_time:.1f}s)\n")
    
    # 获取所有视频文件
    video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
    video_files = []
    
    for f in os.listdir(video_dir):
        if any(f.lower().endswith(ext) for ext in video_extensions):
            video_files.append(os.path.join(video_dir, f))
    
    print(f"找到 {len(video_files)} 个视频文件\n")
    
    # 处理每个视频
    results = []
    for i, video_path in enumerate(sorted(video_files), 1):
        print(f"\n[{i}/{len(video_files)}]")
        result = extract_subtitles(video_path, output_dir, model)
        results.append(result)
    
    # 保存汇总
    summary = {
        "total_videos": len(video_files),
        "successful": sum(1 for r in results if r["status"] == "success"),
        "failed": sum(1 for r in results if r["status"] == "error"),
        "results": results,
        "model": "whisper-small",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    summary_path = os.path.join(output_dir, "_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    # 最终报告
    print("\n" + "="*60)
    print("提取完成！")
    print("="*60)
    print(f"总视频数: {summary['total_videos']}")
    print(f"成功: {summary['successful']}")
    print(f"失败: {summary['failed']}")
    print(f"\n结果保存在: {output_dir}")
    print(f"汇总报告: {summary_path}")

if __name__ == "__main__":
    main()
