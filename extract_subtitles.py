import os
import whisper
import json
from pathlib import Path

def extract_subtitles(video_path, output_dir):
    """使用 Whisper 提取字幕"""
    print(f"处理: {video_path}")
    
    # 加载模型
    model = whisper.load_model("base")  # 可选: tiny, base, small, medium, large
    
    # 转录
    result = model.transcribe(
        video_path,
        language="zh",  # 中文
        task="transcribe",
        verbose=True
    )
    
    # 准备输出
    base_name = Path(video_path).stem
    
    # 1. 保存完整文本
    text_path = os.path.join(output_dir, f"{base_name}_full.txt")
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(result["text"])
    
    # 2. 保存 SRT 字幕
    srt_path = os.path.join(output_dir, f"{base_name}.srt")
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, segment in enumerate(result["segments"], 1):
            start = format_timestamp(segment["start"])
            end = format_timestamp(segment["end"])
            f.write(f"{i}\n")
            f.write(f"{start} --> {end}\n")
            f.write(f"{segment['text'].strip()}\n\n")
    
    # 3. 保存 JSON（完整信息）
    json_path = os.path.join(output_dir, f"{base_name}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 完成: {base_name}")
    print(f"   文本: {text_path}")
    print(f"   字幕: {srt_path}")
    print(f"   JSON: {json_path}")
    
    return result

def format_timestamp(seconds):
    """格式化时间戳为 SRT 格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def main():
    # 视频目录
    video_dir = "/Users/cory/.openclaw/workspace/xhs_analyzer/data/raw"
    output_dir = "/Users/cory/.openclaw/workspace/xhs_analyzer/data/extracted"
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 支持的格式
    video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
    
    # 获取所有视频文件
    video_files = []
    for f in os.listdir(video_dir):
        if any(f.lower().endswith(ext) for ext in video_extensions):
            video_files.append(os.path.join(video_dir, f))
    
    print(f"找到 {len(video_files)} 个视频文件")
    print("=" * 60)
    
    # 处理每个视频
    results = []
    for video_path in sorted(video_files):
        try:
            result = extract_subtitles(video_path, output_dir)
            results.append({
                "video": os.path.basename(video_path),
                "status": "success",
                "text_length": len(result["text"]),
                "segments": len(result["segments"])
            })
        except Exception as e:
            print(f"❌ 错误: {e}")
            results.append({
                "video": os.path.basename(video_path),
                "status": "error",
                "error": str(e)
            })
    
    # 保存汇总结果
    summary_path = os.path.join(output_dir, "_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("=" * 60)
    print(f"处理完成！结果保存在: {output_dir}")
    print(f"汇总报告: {summary_path}")

if __name__ == "__main__":
    main()
