"""将GIF转换为微信公众号可用格式"""
import sys
from pathlib import Path
import subprocess

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

# 设置UTF-8输出
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from loguru import logger

# 配置日志
logger.remove()
logger.add(
    sink=lambda msg: print(msg, end=""),
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO",
    colorize=False
)

def convert_gif_to_mp4(gif_path: str, output_path: str) -> bool:
    """将GIF转换为MP4视频"""
    logger.info(f"转换: {Path(gif_path).name} -> MP4")

    cmd = [
        'ffmpeg',
        '-i', gif_path,
        '-vf', 'fps=10,scale=480:-1:flags=lanczos',
        '-c:v', 'libx264',
        '-preset', 'slow',
        '-crf', '23',
        '-pix_fmt', 'yuv420p',
        '-an',
        output_path,
        '-y'
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"转换失败: {e}")
        return False

def compress_gif(gif_path: str, output_path: str, target_size_mb: float = 1.8) -> bool:
    """压缩GIF文件到指定大小以下"""
    logger.info(f"压缩: {Path(gif_path).name} -> {target_size_mb}MB以下")

    # 使用ffmpeg压缩，降低帧率和尺寸
    cmd = [
        'ffmpeg',
        '-i', gif_path,
        '-vf', 'fps=5,scale=320:-1',
        '-f', 'gif',
        output_path,
        '-y'
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, check=True)

        # 检查文件大小
        output_size = Path(output_path).stat().st_size / (1024 * 1024)
        if output_size <= target_size_mb:
            logger.success(f"  ✓ 压缩成功: {output_size:.1f} MB")
            return True
        else:
            logger.warning(f"  ⚠ 文件仍然过大: {output_size:.1f} MB")
            return False
    except subprocess.CalledProcessError as e:
        logger.error(f"压缩失败: {e}")
        return False

def extract_static_image(video_path: str, timestamp: float, output_path: str) -> bool:
    """从视频中提取静态图片"""
    logger.info(f"提取截图: {timestamp}秒")

    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-ss', str(timestamp),
        '-vframes', '1',
        '-vf', 'scale=600:-1',
        '-q:v', '2',
        output_path,
        '-y'
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"提取失败: {e}")
        return False

def main():
    import time

    video_path = r"C:\0_life\moto\youtube 搬运\done\CV Carburetor VS Mikuni flat slide - ep34 - Roma Custom Bike_Video_Export\CV Carburetor VS Mikuni flat slide - ep34 - Roma Custom Bike.mp4"

    media_dir = Path("output/articles/Mikuni_HSR42/media")
    wechat_dir = Path("output/articles/Mikuni_HSR42/微信专用")
    wechat_dir.mkdir(exist_ok=True)

    logger.info("=" * 70)
    logger.info("微信公众号格式转换工具")
    logger.info("=" * 70)

    # 读取报告获取时间戳
    import re
    report_path = r"C:\Users\dbaa\Desktop\MotoStep\report_source\Mikuni HSR 42 真的值那 300 美金吗.txt"

    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取时间戳
    time_pattern = r'\[(\d+:\d+:\d+)\s*-\s*(\d+:\d+:\d+)\](.+)'
    matches = re.findall(time_pattern, content)

    logger.info(f"\n找到 {len(matches)} 个时间戳")
    logger.info("\n请选择转换方案：")
    logger.info("1. 转换为MP4视频（推荐，无大小限制）")
    logger.info("2. 压缩GIF到2MB以下")
    logger.info("3. 提取静态图片（最小）")
    logger.info("4. 同时生成MP4和静态图片")

    choice = input("\n请输入选项 (1-4): ").strip()

    if choice == "1":
        logger.info("\n方案1: 转换为MP4视频")
        logger.info("=" * 70)

        mp4_files = []

        for i, (start, end, desc) in enumerate(matches, 1):
            parts = start.split(':')
            timestamp = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])

            output_mp4 = str(wechat_dir / f"{i:02d}_{timestamp}s.mp4")

            # 从原始视频提取10秒片段
            logger.info(f"\n[{i}/{len(matches)}] {start} - {end}")

            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-ss', str(timestamp),
                '-t', '10',
                '-vf', 'scale=480:-1',
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '28',
                '-pix_fmt', 'yuv420p',
                '-an',
                output_mp4,
                '-y'
            ]

            try:
                subprocess.run(cmd, capture_output=True, check=True)
                file_size = Path(output_mp4).stat().st_size / 1024
                logger.success(f"  ✓ {Path(output_mp4).name} ({file_size:.0f} KB)")
                mp4_files.append(output_mp4)
            except Exception as e:
                logger.error(f"  ✗ 失败: {e}")

        logger.success(f"\n✓ 转换完成: {len(mp4_files)} 个MP4文件")
        logger.info(f"\nMP4文件保存位置: {wechat_dir}")
        logger.info("\n下一步：")
        logger.info("1. 打开微信公众号编辑器")
        logger.info("2. 点击'视频'图标")
        logger.info("3. 上传这些MP4文件")
        logger.info("4. 插入到文章对应位置")

    elif choice == "2":
        logger.info("\n方案2: 压缩GIF")
        logger.info("=" * 70)

        compressed_files = []

        for i, (start, end, desc) in enumerate(matches, 1):
            parts = start.split(':')
            timestamp = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])

            # 找到原GIF
            original_gif = media_dir / f"{i+1:02d}_{timestamp}s.gif"

            if not original_gif.exists():
                original_gif = media_dir / f"{i:02d}_{timestamp}s.gif"

            if original_gif.exists():
                output_gif = str(wechat_dir / f"{i:02d}_{timestamp}s_compressed.gif")

                logger.info(f"\n[{i}/{len(matches)}] {original_gif.name}")
                logger.info(f"  原始大小: {original_gif.stat().st_size / (1024*1024):.1f} MB")

                if compress_gif(str(original_gif), output_gif):
                    compressed_files.append(output_gif)

        logger.success(f"\n✓ 压缩完成: {len(compressed_files)} 个文件")
        logger.info(f"\n压缩文件保存位置: {wechat_dir}")

    elif choice == "3":
        logger.info("\n方案3: 提取静态图片")
        logger.info("=" * 70)

        image_files = []

        for i, (start, end, desc) in enumerate(matches, 1):
            parts = start.split(':')
            timestamp = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])

            output_img = str(wechat_dir / f"{i:02d}_{timestamp}s.jpg")

            logger.info(f"\n[{i}/{len(matches)}] {start} - {end}")

            if extract_static_image(video_path, timestamp, output_img):
                file_size = Path(output_img).stat().st_size / 1024
                logger.success(f"  ✓ {Path(output_img).name} ({file_size:.0f} KB)")
                image_files.append(output_img)

        logger.success(f"\n✓ 提取完成: {len(image_files)} 张图片")
        logger.info(f"\n图片保存位置: {wechat_dir}")

    elif choice == "4":
        logger.info("\n方案4: 生成MP4和静态图片")
        logger.info("=" * 70)

        mp4_files = []
        image_files = []

        for i, (start, end, desc) in enumerate(matches, 1):
            parts = start.split(':')
            timestamp = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])

            logger.info(f"\n[{i}/{len(matches)}] {start} - {end}")

            # 提取MP4
            output_mp4 = str(wechat_dir / f"{i:02d}_{timestamp}s.mp4")
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-ss', str(timestamp),
                '-t', '10',
                '-vf', 'scale=480:-1',
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '28',
                '-pix_fmt', 'yuv420p',
                '-an',
                output_mp4,
                '-y'
            ]

            try:
                subprocess.run(cmd, capture_output=True, check=True)
                file_size = Path(output_mp4).stat().st_size / 1024
                logger.success(f"  ✓ MP4: {file_size:.0f} KB")
                mp4_files.append(output_mp4)
            except Exception as e:
                logger.error(f"  ✗ MP4失败: {e}")

            # 提取静态图
            output_img = str(wechat_dir / f"{i:02d}_{timestamp}s.jpg")
            if extract_static_image(video_path, timestamp, output_img):
                file_size = Path(output_img).stat().st_size / 1024
                logger.success(f"  ✓ JPG: {file_size:.0f} KB")
                image_files.append(output_img)

        logger.success(f"\n✓ 生成完成:")
        logger.info(f"  - MP4视频: {len(mp4_files)} 个")
        logger.info(f"  - 静态图片: {len(image_files)} 张")
        logger.info(f"\n文件保存位置: {wechat_dir}")

if __name__ == "__main__":
    main()
