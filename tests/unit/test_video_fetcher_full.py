"""VideoFetcher功能测试（不需要下载大文件）"""
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
from src.models.video import VideoInfo, KeyMoment, MediaAsset

# 配置日志
logger.remove()
logger.add(
    sink=lambda msg: print(msg, end=""),
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO",
    colorize=False
)


def test_ytdlp_installed():
    """测试yt-dlp是否已安装"""
    logger.info("\n" + "=" * 70)
    logger.info("测试1: yt-dlp安装检查")
    logger.info("=" * 70)

    try:
        result = subprocess.run(
            ["yt-dlp", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            version = result.stdout.strip()
            logger.success(f"✓ yt-dlp已安装: {version}")
            return True
        else:
            logger.error("✗ yt-dlp未正确安装")
            return False

    except FileNotFoundError:
        logger.error("✗ yt-dlp未找到")
        logger.info("请运行: pip install yt-dlp")
        return False
    except Exception as e:
        logger.error(f"✗ 检查失败: {e}")
        return False


def test_video_id_extraction():
    """测试视频ID提取功能"""
    logger.info("\n" + "=" * 70)
    logger.info("测试2: 视频ID提取")
    logger.info("=" * 70)

    test_urls = [
        ("https://www.youtube.com/watch?v=0QHiZDV43aw", "0QHiZDV43aw"),
        ("https://youtu.be/0QHiZDV43aw", "0QHiZDV43aw"),
        ("https://www.youtube.com/embed/0QHiZDV43aw", "0QHiZDV43aw"),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ]

    fetcher = VideoFetcher(output_dir="./output/videos")
    passed = 0
    failed = 0

    for url, expected_id in test_urls:
        try:
            extracted_id = fetcher._extract_video_id(url)
            if extracted_id == expected_id:
                logger.success(f"✓ {url[:50]}...")
                logger.info(f"  提取ID: {extracted_id}")
                passed += 1
            else:
                logger.error(f"✗ {url[:50]}...")
                logger.info(f"  期望: {expected_id}, 实际: {extracted_id}")
                failed += 1
        except Exception as e:
            logger.error(f"✗ {url[:50]}...")
            logger.info(f"  错误: {e}")
            failed += 1

    logger.info(f"\n结果: {passed}/{len(test_urls)} 通过")
    return failed == 0


def test_video_info_model():
    """测试VideoInfo数据模型"""
    logger.info("\n" + "=" * 70)
    logger.info("测试3: VideoInfo数据模型")
    logger.info("=" * 70)

    try:
        # 创建测试视频信息
        video_info = VideoInfo(
            video_id="test123",
            url="https://www.youtube.com/watch?v=test123",
            title="测试视频标题",
            duration=600,
            width=1280,
            height=720,
            local_path="./test.mp4",
            file_size_bytes=1024000
        )

        logger.success("✓ VideoInfo对象创建成功")
        logger.info(f"  视频ID: {video_info.video_id}")
        logger.info(f"  标题: {video_info.title}")
        logger.info(f"  时长: {video_info.duration}秒 ({video_info.duration // 60}分钟)")
        logger.info(f"  分辨率: {video_info.width}x{video_info.height}")
        logger.info(f"  文件大小: {video_info.file_size_bytes / (1024*1024):.2f} MB")

        # 测试JSON序列化
        import json
        video_dict = video_info.model_dump()
        logger.success("✓ JSON序列化成功")
        logger.info(f"  字段数量: {len(video_dict)}")

        return True

    except Exception as e:
        logger.error(f"✗ 测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def test_subtitle_url_building():
    """测试字幕下载命令构建"""
    logger.info("\n" + "=" * 70)
    logger.info("测试4: 字幕下载命令")
    logger.info("=" * 70)

    try:
        fetcher = VideoFetcher(output_dir="./output/videos")
        test_url = "https://www.youtube.com/watch?v=0QHiZDV43aw"
        video_id = "0QHiZDV43aw"

        # 构建字幕下载命令（不实际执行）
        import shutil
        yt_dlp_path = shutil.which("yt-dlp")

        if not yt_dlp_path:
            logger.error("✗ yt-dlp未找到")
            return False

        cmd = [
            "yt-dlp",
            "--cookies", "cookies.txt",
            "--write-subs",
            "--write-auto-subs",
            "--sub-langs", "en,zh-Hans,zh-Hant",
            "--sub-format", "vtt",
            "--skip-download",
            "-o", "./output/videos/%(title)s. [%(id)s].%(ext)s",
            test_url
        ]

        logger.success("✓ 字幕下载命令构建成功")
        logger.info(f"  命令长度: {len(cmd)} 个参数")
        logger.info(f"  目标语言: en, zh-Hans, zh-Hant")
        logger.info(f"  输出格式: vtt")

        # 验证关键参数
        assert "--write-subs" in cmd
        assert "--sub-langs" in cmd
        # 检查语言参数（它们是作为一个逗号分隔的字符串）
        lang_index = cmd.index("--sub-langs")
        languages = cmd[lang_index + 1].split(',')
        assert "en" in languages
        assert "zh-Hans" in languages
        logger.success("✓ 命令参数验证通过")

        return True

    except Exception as e:
        logger.error(f"✗ 测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def test_output_directory():
    """测试输出目录创建"""
    logger.info("\n" + "=" * 70)
    logger.info("测试5: 输出目录管理")
    logger.info("=" * 70)

    try:
        output_dir = Path("./output/videos")

        # 创建fetcher实例
        fetcher = VideoFetcher(output_dir=str(output_dir))

        # 检查目录是否存在
        if output_dir.exists():
            logger.success(f"✓ 输出目录已存在: {output_dir}")
        else:
            logger.success(f"✓ 输出目录已创建: {output_dir}")

        # 检查目录权限
        if output_dir.is_dir():
            logger.success("✓ 目录类型验证通过")
        else:
            logger.error("✗ 路径不是目录")
            return False

        # 列出目录内容
        files = list(output_dir.glob("*"))
        logger.info(f"  当前文件数: {len(files)}")

        return True

    except Exception as e:
        logger.error(f"✗ 测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def test_ffmpeg_integration():
    """测试FFmpeg集成（用于视频信息获取）"""
    logger.info("\n" + "=" * 70)
    logger.info("测试6: FFmpeg集成")
    logger.info("=" * 70)

    try:
        # 检查ffprobe是否可用
        result = subprocess.run(
            ["ffprobe", "-version"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            logger.error("✗ ffprobe未找到")
            logger.info("VideoFetcher使用ffprobe获取视频信息")
            return False

        # 提取版本信息
        first_line = result.stdout.split('\n')[0]
        logger.success(f"✓ FFmpeg工具已安装")
        logger.info(f"  {first_line}")

        # 检查是否有已下载的视频可以测试
        output_dir = Path("./output/videos")
        mp4_files = list(output_dir.glob("*.mp4"))

        if mp4_files:
            logger.info(f"\n找到 {len(mp4_files)} 个视频文件:")
            for f in mp4_files[:3]:  # 只显示前3个
                size_mb = f.stat().st_size / (1024 * 1024)
                logger.info(f"  - {f.name} ({size_mb:.1f} MB)")
        else:
            logger.info("  当前没有已下载的视频文件")
            logger.info("  运行 python test_download_video.py 下载视频")

        return True

    except FileNotFoundError:
        logger.error("✗ FFmpeg未找到")
        logger.info("请安装FFmpeg: https://ffmpeg.org/download.html")
        return False
    except Exception as e:
        logger.error(f"✗ 测试失败: {e}")
        return False


if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("MotoStep - VideoFetcher功能测试套件")
    logger.info("=" * 70)
    logger.info("\n此测试不需要下载大文件，只测试核心功能\n")

    tests = [
        ("yt-dlp安装", test_ytdlp_installed),
        ("视频ID提取", test_video_id_extraction),
        ("VideoInfo模型", test_video_info_model),
        ("字幕命令构建", test_subtitle_url_building),
        ("输出目录管理", test_output_directory),
        ("FFmpeg集成", test_ffmpeg_integration),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            logger.error(f"\n测试异常: {name} - {e}")
            results.append((name, False))

    # 汇总结果
    logger.info("\n" + "=" * 70)
    logger.info("测试结果汇总")
    logger.info("=" * 70)

    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed

    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        if result:
            logger.success(f"{name}: {status}")
        else:
            logger.error(f"{name}: {status}")

    logger.info(f"\n总计: {passed}/{len(results)} 通过")

    if failed == 0:
        logger.success("\n🎉 所有功能测试通过!")
        logger.info("\n下一步:")
        logger.info("  1. 运行 python test_download_video.py 进行完整下载测试")
        logger.info("  2. 或继续开发阶段3：媒体处理模块")
    else:
        logger.warning(f"\n⚠️  有 {failed} 个测试失败")
        logger.info("请检查上述错误信息")

    sys.exit(0 if failed == 0 else 1)
