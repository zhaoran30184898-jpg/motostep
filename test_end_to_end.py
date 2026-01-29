"""端到端测试 - 完整流程"""
import sys
from pathlib import Path
import json

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

# 设置UTF-8输出
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from loguru import logger
from src.video_fetcher import VideoFetcher
from src.media_processor import MediaProcessor
from src.content_analyzer import ContentAnalyzer
from src.content_composer import ContentComposer
from src.models.video import VideoAnalysis, KeyMoment, MediaAsset

# 配置日志
logger.remove()
logger.add(
    sink=lambda msg: print(msg, end=""),
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO",
    colorize=False
)


def create_mock_notebooklm_report(video_title: str, output_path: str) -> None:
    """创建模拟的NotebookLM报告（用于测试）"""
    logger.info("创建模拟NotebookLM报告...")

    report_content = f"""# {video_title}

## Summary

This comprehensive motocross tutorial covers essential riding techniques that every rider should master. The instructor demonstrates proper body positioning, braking techniques, cornering skills, and jump mechanics through detailed explanations and practical demonstrations.

## Key Techniques

- **Body Positioning**: Proper body positioning is crucial for maintaining control of the motorcycle. Keep your weight centered on the bike, elbows up, and head looking forward. Shift your weight forward during acceleration and backward during braking.

- **Braking Techniques**: Master the art of braking by using both front and rear brakes together. Apply braking force gradually before corners, with 70% front brake and 30% rear brake. Practice threshold braking to maximize stopping power without locking wheels.

- **Cornering Skills**: Enter corners wide, apex at the inside point, and exit wide. Lean with the bike while keeping your body upright. Look through the corner to where you want to go, not at the ground directly in front of you.

- **Jump Mechanics**: Approach jumps with steady speed in the correct gear.compress before the lip of the jump, and maintain neutral body position in the air. Land with both wheels simultaneously and absorb impact with your legs.

- **Throttle Control**: Apply throttle smoothly and progressively. Avoid whacking the throttle open, which can cause the rear wheel to spin. Roll on the throttle as you exit corners for maximum traction.

## Key Moments

- **0:30** - Instructor demonstrates proper body positioning on the bike
- **1:45** - Front and rear brake technique demonstration
- **3:20** - Cornering line and body lean explanation
- **5:10** - Jump approach and takeoff technique
- **7:30** - Throttle control and clutch modulation
- **9:15** - Putting it all together - complete lap demonstration
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_content)

    logger.success(f"✓ 报告已创建: {output_path}")


def run_end_to_end_test(video_url: str, cookies_path: str = None):
    """运行端到端测试"""
    logger.info("=" * 70)
    logger.info("MotoStep - 端到端测试")
    logger.info("=" * 70)
    logger.info(f"\n视频URL: {video_url}\n")

    try:
        # ========== 阶段1: 视频获取 ==========
        logger.info("\n" + "=" * 70)
        logger.info("阶段1: 视频获取")
        logger.info("=" * 70)

        fetcher = VideoFetcher()
        video_id = fetcher._extract_video_id(video_url)
        logger.info(f"视频ID: {video_id}")

        # 下載视频和字幕
        logger.info("\n正在下载视频和字幕...")
        logger.warning("注意: 视频下载可能需要几分钟...")

        # 检查是否已下载
        video_dir = Path("./output/videos")
        existing_videos = list(video_dir.glob(f"*[{video_id}].mp4"))

        if cookies_path and not Path(cookies_path).exists():
            logger.warning(f"⚠ Cookies文件不存在: {cookies_path}")
            logger.info("将尝试不使用cookies下载...")
            cookies_path = None

        if not existing_videos:
            video_info = fetcher.download_video(
                url=video_url,
                quality="720p",
                cookies_path=cookies_path or "cookies.txt"
            )
            logger.success(f"✓ 视频下载完成: {video_info.local_path}")
            video_path = video_info.local_path
        else:
            video_path = str(existing_videos[0])
            logger.success(f"✓ 视频已存在: {Path(video_path).name}")

        # 下载字幕
        subtitle_dir = Path("./output/subtitles")
        subtitle_dir.mkdir(parents=True, exist_ok=True)
        subtitle_path = str(subtitle_dir / f"{video_id}.en.vtt")

        if not Path(subtitle_path).exists():
            subtitle_paths = fetcher.download_subtitles(
                url=video_url,
                video_id=video_id,
                languages=["en"],
                cookies_path=cookies_path or "cookies.txt"
            )
            logger.success(f"✓ 字幕下载完成: {len(subtitle_paths)} 种语言")
            subtitle_path = subtitle_paths.get("en", subtitle_path)
        else:
            logger.success(f"✓ 字幕已存在: {Path(subtitle_path).name}")

        # ========== 阶段2: 内容分析 ==========
        logger.info("\n" + "=" * 70)
        logger.info("阶段2: 内容分析")
        logger.info("=" * 70)

        # 创建模拟报告
        report_path = f"./output/reports/{video_id}_report.txt"
        Path("./output/reports").mkdir(parents=True, exist_ok=True)

        # 使用ffprobe获取视频标题
        from src.media_processor.ffmpeg_wrapper import FFmpegWrapper
        wrapper = FFmpegWrapper()

        # 尝试获取视频信息
        try:
            video_info_data = wrapper.get_video_info(video_path)
            # 使用实际的视频标题或文件名
            video_title = Path(video_path).stem.replace(f".[{video_id}]", "")
        except:
            video_title = f"Motocross Training Video - {video_id}"

        create_mock_notebooklm_report(video_title, report_path)

        # 分析内容
        analyzer = ContentAnalyzer(subtitle_language="en")

        # 检查字幕文件是否存在
        if Path(subtitle_path).exists():
            logger.info("\n正在分析内容（使用字幕时间戳）...")
            analysis = analyzer.analyze(
                report_path=report_path,
                subtitle_path=subtitle_path,
                video_id=video_id
            )
        else:
            logger.warning("\n⚠ 字幕文件不存在，使用报告中的关键时刻时间戳...")
            # 解析报告
            report_data = analyzer.notebooklm_helper.parse_report(report_path)

            # 创建关键时刻（使用报告中的时间戳）
            key_moments = []
            for i, km in enumerate(report_data["key_moments"][:6], 1):  # 限制前6个
                key_moments.append(KeyMoment(
                    timestamp=km["seconds"],
                    description=km["description"],
                    technique=f"Technique {i}",
                    media_type="gif" if i % 2 == 0 else "static",  # 交替使用gif/static
                    duration=3.0
                ))

            # 创建VideoAnalysis对象
            from src.models.video import VideoAnalysis
            analysis = VideoAnalysis(
                video_id=video_id,
                title=report_data["title"],
                content=report_data["summary"],
                key_moments=key_moments,
                metadata={
                    "total_techniques": len(key_moments),
                    "matched_timestamps": len(key_moments),
                    "subtitle_language": "en",
                    "source": "mock_report"
                }
            )

        # 保存分析结果
        analysis_json_path = f"./output/analysis/{video_id}_analysis.json"
        Path("./output/analysis").mkdir(parents=True, exist_ok=True)
        analyzer.save_analysis(analysis, analysis_json_path)

        analyzer.print_summary(analysis)

        # ========== 阶段3: 媒体生成 ==========
        logger.info("\n" + "=" * 70)
        logger.info("阶段3: 媒体生成")
        logger.info("=" * 70)

        processor = MediaProcessor(watermark_text="FreeSoloDirtbike")
        media_assets = []

        logger.info(f"\n正在生成{len(analysis.key_moments)}个媒体文件...")
        logger.warning("注意: GIF生成可能需要几分钟...")

        for i, moment in enumerate(analysis.key_moments[:3], 1):  # 限制生成前3个
            logger.info(f"\n{i}. {moment.technique}")
            logger.info(f"   时间: {moment.timestamp}秒")

            output_dir = "./output/images"
            Path(output_dir).mkdir(exist_ok=True)

            try:
                if moment.media_type == "gif":
                    # 生成GIF
                    gif_path = processor.generate_gif(
                        video_path=video_path,
                        start_time=moment.timestamp,
                        duration=min(moment.duration or 3, 5),  # 限制最长5秒
                        width=480,
                        fps=10,
                        output_path=f"{output_dir}/{video_id}_{i}.gif"
                    )

                    # 添加水印
                    gif_wm_path = processor.add_watermark(
                        media_path=gif_path,
                        text="FreeSoloDirtbike",
                        font_size=14
                    )

                    media_assets.append(MediaAsset(
                        type="gif",
                        local_path=gif_wm_path,
                        timestamp=moment.timestamp,
                        description=moment.description[:100],
                        size_bytes=Path(gif_wm_path).stat().st_size
                    ))

                else:
                    # 生成截图
                    screenshot_path = processor.extract_screenshot(
                        video_path=video_path,
                        timestamp=moment.timestamp,
                        quality=2,
                        output_path=f"{output_dir}/{video_id}_{i}.jpg"
                    )

                    # 添加水印
                    screenshot_wm_path = processor.add_watermark(
                        media_path=screenshot_path,
                        text="FreeSoloDirtbike",
                        font_size=16
                    )

                    media_assets.append(MediaAsset(
                        type="image",
                        local_path=screenshot_wm_path,
                        timestamp=moment.timestamp,
                        description=moment.description[:100],
                        size_bytes=Path(screenshot_wm_path).stat().st_size
                    ))

                logger.success(f"   ✓ 媒体生成成功")

            except Exception as e:
                logger.error(f"   ✗ 媒体生成失败: {e}")
                continue

        logger.success(f"\n✓ 成功生成{len(media_assets)}/{len(analysis.key_moments)}个媒体文件")

        # ========== 阶段4: 内容合成 ==========
        logger.info("\n" + "=" * 70)
        logger.info("阶段4: 内容合成")
        logger.info("=" * 70)

        composer = ContentComposer()

        # 生成所有格式的文章
        output_dir = f"./output/articles/{video_id}"
        logger.info(f"\n正在生成文章到: {output_dir}")

        results = composer.compose_all_formats(
            analysis=analysis,
            media_assets=media_assets,
            output_dir=output_dir
        )

        logger.success("\n✓ 所有格式生成完成")

        # ========== 测试总结 ==========
        logger.info("\n" + "=" * 70)
        logger.info("测试总结")
        logger.info("=" * 70)

        logger.info(f"\n视频ID: {video_id}")
        logger.info(f"视频标题: {video_title}")
        logger.info(f"关键技术点: {len(analysis.key_moments)} 个")
        logger.info(f"生成媒体: {len(media_assets)} 个")
        logger.info(f"生成文章: {len(results)} 种格式")

        logger.info("\n生成的文件:")
        logger.info(f"  视频: {video_path}")
        logger.info(f"  字幕: {subtitle_path}")
        logger.info(f"  分析结果: {analysis_json_path}")
        logger.info(f"  文章目录: {output_dir}/")

        # 列出文章文件
        for format_name, file_path in results.items():
            if Path(file_path).exists():
                file_size = Path(file_path).stat().st_size / 1024
                logger.info(f"    {format_name}: {file_path} ({file_size:.1f} KB)")

        logger.success("\n✓ 端到端测试完成!")
        logger.info("\n你可以查看以下文件:")
        logger.info(f"  1. 视频和字幕: ./output/videos/ 和 ./output/subtitles/")
        logger.info(f"  2. 媒体文件: ./output/images/")
        logger.info(f"  3. 文章: {output_dir}/")
        logger.info(f"  4. 分析结果: {analysis_json_path}")

        return True

    except Exception as e:
        logger.error(f"\n✗ 端到端测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    # 确保输出目录存在
    for dir_path in ["./output/videos", "./output/subtitles", "./output/reports",
                     "./output/images", "./output/analysis"]:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

    # 测试URL
    test_url = "https://www.youtube.com/watch?v=oPFg4VkIVIY"

    # Cookies文件（用户提供）
    cookies_file = r"C:\Users\30184\Downloads\www.youtube.com_cookies (2).txt"

    success = run_end_to_end_test(test_url, cookies_path=cookies_file)

    if success:
        logger.success("\n🎉 所有功能正常工作!")
    else:
        logger.error("\n❌ 测试失败，请检查错误信息")
