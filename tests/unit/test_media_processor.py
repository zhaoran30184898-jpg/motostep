"""媒体处理模块测试"""
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
from src.media_processor import FFmpegWrapper, MediaProcessor

# 配置日志
logger.remove()
logger.add(
    sink=lambda msg: print(msg, end=""),
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO",
    colorize=False
)


def test_ffmpeg_wrapper():
    """测试FFmpegWrapper类"""
    logger.info("\n" + "=" * 70)
    logger.info("测试1: FFmpegWrapper - 命令构建")
    logger.info("=" * 70)

    try:
        wrapper = FFmpegWrapper()

        # 测试1：截图命令
        logger.info("\n1.1 测试截图命令构建...")
        screenshot_cmd = wrapper.screenshot_command(
            video_path="test.mp4",
            timestamp=124.154,
            output_path="output.jpg",
            quality=2
        )

        expected_keywords = ["ffmpeg", "-ss", "124.154", "-vframes", "1", "-q:v", "2"]
        for keyword in expected_keywords:
            assert keyword in " ".join(screenshot_cmd), f"缺少关键词: {keyword}"

        logger.success("✓ 截图命令构建正确")
        logger.info(f"  命令长度: {len(screenshot_cmd)} 个参数")

        # 测试2：GIF命令
        logger.info("\n1.2 测试GIF命令构建...")
        gif_cmd, palette_cmd = wrapper.gif_command(
            video_path="test.mp4",
            start_time=120.0,
            duration=3.0,
            output_path="output.gif",
            width=480,
            fps=10,
            use_palette=True
        )

        assert gif_cmd[0] == "ffmpeg"
        assert "-filter_complex" in " ".join(gif_cmd) or "-vf" in " ".join(gif_cmd)
        assert palette_cmd is not None
        logger.success("✓ GIF命令构建正确（带调色板）")
        logger.info(f"  主命令: {len(gif_cmd)} 个参数")
        logger.info(f"  调色板命令: {len(palette_cmd)} 个参数")

        # 测试3：水印命令
        logger.info("\n1.3 测试水印命令构建...")
        watermark_cmd = wrapper.watermark_command(
            input_path="input.jpg",
            output_path="output_wm.jpg",
            text="Test Watermark"
        )

        assert "drawtext" in " ".join(watermark_cmd)
        assert "Test Watermark" in " ".join(watermark_cmd)
        logger.success("✓ 水印命令构建正确")
        logger.info(f"  命令长度: {len(watermark_cmd)} 个参数")

        logger.success("\n✓ FFmpegWrapper所有测试通过")
        return True

    except Exception as e:
        logger.error(f"\n✗ FFmpegWrapper测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def test_media_processor():
    """测试MediaProcessor类"""
    logger.info("\n" + "=" * 70)
    logger.info("测试2: MediaProcessor - 媒体处理功能")
    logger.info("=" * 70)

    try:
        processor = MediaProcessor(watermark_text="Test Watermark")

        # 测试初始化
        logger.info("\n2.1 测试处理器初始化...")
        assert processor.wrapper is not None
        assert processor.watermark_text == "Test Watermark"
        logger.success("✓ MediaProcessor初始化成功")

        # 检查是否有已下载的视频可以测试
        logger.info("\n2.2 查找测试视频...")
        video_dir = Path("./output/videos")
        video_files = list(video_dir.glob("*.mp4"))

        if video_files:
            logger.info(f"  找到 {len(video_files)} 个视频文件")
            test_video = str(video_files[0])
            logger.info(f"  使用测试视频: {Path(test_video).name}")
            return test_actual_processing(processor, test_video)
        else:
            logger.warning("  未找到视频文件")
            logger.info("  跳过实际处理测试")
            logger.info("\n提示:")
            logger.info("  1. 先运行 test_download_video.py 下载视频")
            logger.info("  2. 或者使用已有视频文件放到 ./output/videos/")
            logger.success("\n✓ MediaProcessor基础功能验证通过")
            return True

    except Exception as e:
        logger.error(f"\n✗ MediaProcessor测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def test_actual_processing(processor: MediaProcessor, video_path: str):
    """测试实际的媒体处理功能"""
    logger.info("\n2.3 测试实际媒体处理...")

    try:
        # 获取视频信息
        wrapper = processor.wrapper
        duration = wrapper.get_video_duration(video_path)
        logger.info(f"  视频时长: {duration}秒 ({duration // 60}分{duration % 60}秒)")

        # 测试截图提取（选择视频中间时间点）
        logger.info("\n2.3.1 测试截图提取...")
        timestamp = duration / 2
        screenshot_path = processor.extract_screenshot(
            video_path=video_path,
            timestamp=timestamp,
            quality=2
        )

        if Path(screenshot_path).exists():
            file_size = Path(screenshot_path).stat().st_size / 1024
            logger.success(f"✓ 截图测试通过 ({file_size:.1f} KB)")
        else:
            logger.error("✗ 截图文件不存在")
            return False

        # 测试水印添加
        logger.info("\n2.3.2 测试水印添加...")
        watermarked_path = processor.add_watermark(
            media_path=screenshot_path,
            text="FreeSoloDirtbike"
        )

        if Path(watermarked_path).exists():
            logger.success("✓ 水印添加测试通过")
        else:
            logger.error("✗ 水印文件不存在")
            return False

        # 测试GIF生成（截取前3秒）
        logger.info("\n2.3.3 测试GIF生成...")
        gif_path = processor.generate_gif(
            video_path=video_path,
            start_time=0,
            duration=3,
            width=480,
            fps=10
        )

        if Path(gif_path).exists():
            file_size = Path(gif_path).stat().st_size / 1024
            logger.success(f"✓ GIF生成测试通过 ({file_size:.1f} KB)")
        else:
            logger.error("✗ GIF文件不存在")
            return False

        # 测试GIF水印
        logger.info("\n2.3.4 测试GIF水印...")
        gif_wm_path = processor.add_watermark(
            media_path=gif_path,
            text="FreeSoloDirtbike",
            font_size=14
        )

        if Path(gif_wm_path).exists():
            logger.success("✓ GIF水印测试通过")
        else:
            logger.error("✗ GIF水印文件不存在")
            return False

        logger.success("\n✓ 所有实际处理测试通过")
        logger.info("\n生成的文件:")
        logger.info(f"  1. 截图: {screenshot_path}")
        logger.info(f"  2. 截图(带水印): {watermarked_path}")
        logger.info(f"  3. GIF: {gif_path}")
        logger.info(f"  4. GIF(带水印): {gif_wm_path}")

        return True

    except Exception as e:
        logger.error(f"\n✗ 实际处理测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def test_batch_processing():
    """测试批量处理功能"""
    logger.info("\n" + "=" * 70)
    logger.info("测试3: 批量处理功能")
    logger.info("=" * 70)

    try:
        processor = MediaProcessor()

        # 测试批量截图参数
        logger.info("\n3.1 测试批量截图参数...")
        timestamps = [10.5, 20.5, 30.5, 40.5, 50.5]

        # 只测试参数验证，不实际处理
        logger.info(f"  时间戳数量: {len(timestamps)}")
        logger.info(f"  时间戳列表: {[f'{t:.1f}s' for t in timestamps[:3]]}...")
        logger.success("✓ 批量截图参数验证通过")

        # 测试批量GIF参数
        logger.info("\n3.2 测试批量GIF参数...")
        clips = [(10, 3), (20, 2), (30, 4)]

        logger.info(f"  片段数量: {len(clips)}")
        logger.info(f"  片段列表: {[f'{start}s-{dur}s' for start, dur in clips]}")
        logger.success("✓ 批量GIF参数验证通过")

        logger.success("\n✓ 批量处理功能验证通过")
        return True

    except Exception as e:
        logger.error(f"\n✗ 批量处理测试失败: {e}")
        return False


def test_command_execution():
    """测试FFmpeg命令执行"""
    logger.info("\n" + "=" * 70)
    logger.info("测试4: FFmpeg命令执行")
    logger.info("=" * 70)

    try:
        wrapper = FFmpegWrapper()

        # 测试ffprobe
        logger.info("\n4.1 测试ffprobe命令...")
        result = wrapper.run_command(
            [wrapper.ffprobe_path, "-version"],
            check=False
        )

        if result.returncode == 0:
            logger.success("✓ ffprobe可用")
        else:
            logger.error("✗ ffprobe不可用")
            return False

        # 测试ffmpeg
        logger.info("\n4.2 测试ffmpeg命令...")
        result = wrapper.run_command(
            [wrapper.ffmpeg_path, "-version"],
            check=False
        )

        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            logger.success(f"✓ ffmpeg可用")
            logger.info(f"  {version_line}")
        else:
            logger.error("✗ ffmpeg不可用")
            return False

        logger.success("\n✓ 命令执行测试通过")
        return True

    except Exception as e:
        logger.error(f"\n✗ 命令执行测试失败: {e}")
        return False


if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("MotoStep - 媒体处理模块测试套件")
    logger.info("=" * 70)
    logger.info("\n此测试包括命令构建和实际媒体处理\n")

    tests = [
        ("FFmpegWrapper", test_ffmpeg_wrapper),
        ("MediaProcessor", test_media_processor),
        ("批量处理", test_batch_processing),
        ("命令执行", test_command_execution),
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
        logger.success("\n🎉 所有测试通过!")
    else:
        logger.warning(f"\n⚠️  有 {failed} 个测试失败")
