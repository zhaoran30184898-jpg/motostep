"""完整测试VideoFetcher - 实际下载视频"""
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
from src.video_fetcher import VideoFetcher

# 配置日志
logger.remove()
logger.add(
    sink=lambda msg: print(msg, end=""),
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO",
    colorize=False
)


def test_video_download():
    """测试完整的视频下载功能"""
    logger.info("=" * 70)
    logger.info("MotoStep - 视频下载完整测试")
    logger.info("=" * 70)

    # 使用一个公开的越野摩托教学视频
    test_url = "https://www.youtube.com/watch?v=0QHiZDV43aw"

    try:
        # 初始化VideoFetcher
        fetcher = VideoFetcher(output_dir="./output/videos")

        logger.info(f"\n测试视频URL:")
        logger.info(f"  {test_url}")
        logger.info(f"\n视频信息:")
        logger.info(f"  标题: Motocross Jump Technique: Where to Look")
        logger.info(f"  时长: 约11分钟")
        logger.info(f"  质量: 720p")

        logger.warning(f"\n注意:")
        logger.warning(f"  - 这是一个完整的下载测试，会下载实际视频文件")
        logger.warning(f"  - 文件大小约: 190MB")
        logger.warning(f"  - 预计时间: 5-10分钟（取决于网络速度）")
        logger.warning(f"  - 如需cookies，请将cookies.txt放在项目根目录")

        # 询问用户是否继续
        response = input("\n是否继续下载？(y/n): ").strip().lower()

        if response != 'y':
            logger.info("测试已取消")
            return False

        logger.info("\n开始下载...")
        logger.info("-" * 70)

        # 下载视频
        video_info = fetcher.download_video(
            url=test_url,
            quality="720p",
            cookies_path="./cookies.txt"
        )

        logger.info("\n" + "-" * 70)
        logger.success("视频下载成功！")
        logger.info(f"\n视频信息:")
        logger.info(f"  ID: {video_info.video_id}")
        logger.info(f"  标题: {video_info.title}")
        logger.info(f"  时长: {video_info.duration}秒 ({video_info.duration // 60}分{video_info.duration % 60}秒)")
        logger.info(f"  分辨率: {video_info.width}x{video_info.height}")
        logger.info(f"  文件路径: {video_info.local_path}")
        logger.info(f"  文件大小: {video_info.file_size_bytes / (1024*1024):.2f} MB")

        # 检查文件是否存在
        if Path(video_info.local_path).exists():
            logger.success("✓ 文件验证成功")

            # 下载字幕
            logger.info("\n开始下载字幕...")
            subtitle_paths = fetcher.download_subtitles(
                url=test_url,
                video_id=video_info.video_id,
                languages=["en", "zh-Hans", "zh-Hant"],
                cookies_path="./cookies.txt"
            )

            if subtitle_paths:
                logger.success(f"字幕下载成功: {len(subtitle_paths)}个语言")
                for lang, path in subtitle_paths.items():
                    file_size = Path(path).stat().st_size / 1024
                    logger.info(f"  - {lang}: {path} ({file_size:.1f} KB)")
            else:
                logger.warning("未找到字幕文件")

            logger.success("\n🎉 完整测试通过！")
            logger.info("\n已下载文件:")
            logger.info(f"  1. 视频文件: {video_info.local_path}")
            for lang, path in subtitle_paths.items():
                logger.info(f"  {list(subtitle_paths.keys()).index(lang) + 2}. {lang}字幕: {path}")

            return True
        else:
            logger.error("✗ 文件验证失败")
            return False

    except Exception as e:
        logger.error(f"\n✗ 测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def check_cookies():
    """检查cookies.txt文件"""
    logger.info("\n检查cookies.txt文件...")
    cookies_path = Path("./cookies.txt")

    if cookies_path.exists():
        logger.success("✓ 找到cookies.txt文件")
        file_size = cookies_path.stat().st_size
        logger.info(f"  文件大小: {file_size} bytes")

        # 读取前几行检查格式
        with open(cookies_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:3]
            logger.info(f"  文件内容预览:")
            for line in lines:
                logger.info(f"    {line.strip()}")
    else:
        logger.warning("✗ 未找到cookies.txt文件")
        logger.warning("  某些视频可能需要cookies才能下载")
        logger.warning("  您可以:")
        logger.warning("    1. 使用浏览器导出cookies.txt")
        logger.warning("    2. 或者尝试不需要认证的公开视频")


if __name__ == "__main__":
    logger.info("开始视频下载测试...\n")

    # 检查cookies
    check_cookies()

    # 测试下载
    success = test_video_download()

    if success:
        logger.success("\n" + "=" * 70)
        logger.success("所有测试完成！")
        logger.success("=" * 70)
    else:
        logger.error("\n测试未完成")
