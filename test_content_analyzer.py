"""内容分析模块测试"""
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
from src.content_analyzer import ContentAnalyzer, NotebookLMHelper, TimestampExtractor

# 配置日志
logger.remove()
logger.add(
    sink=lambda msg: print(msg, end=""),
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO",
    colorize=False
)


def create_mock_report(report_path: str):
    """创建模拟的NotebookLM报告"""
    logger.info("创建模拟报告文件...")

    report_content = """# Motocross Technique Training: Braking and Body Position

## Summary

This video covers essential motocross techniques for proper braking and body position control during high-speed riding. Through track demonstrations and slow-motion footage, it shows the correct coordination between front brake and rear brake, as well as how to maintain body balance in corners.

## Key Techniques

- **Front Brake Technique**: The front brake provides most of your stopping power. Apply front brake pressure gradually before corner entry, avoid locking the front wheel which causes sliding, and shift your body weight backward.

- **Body Position Control**: Shift your body weight back when braking, lean your body into the turn during corners. Keep your head up and eyes looking toward the corner exit, grip the tank with your knees for stability.

- **Rear Brake Application**: Use the rear brake for fine speed adjustment. Maintain rear wheel traction while sliding, coordinate with front brake for smooth deceleration.

- **Jump Technique**: Keep your body weight centered when taking off, adjust body position in the air to control landing. Bend your knees to absorb the impact upon landing.

## Key Moments

- **0:30** - Demonstrates proper front brake usage
- **1:15** - Shows corner body position adjustment
- **2:45** - Front and rear brake coordination demonstration
- **4:20** - Jump takeoff technique
- **5:10** - Landing body position control
"""

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)

    logger.success(f"✓ 模拟报告已创建: {report_path}")


def create_mock_subtitle(subtitle_path: str):
    """创建模拟的VTT字幕文件"""
    logger.info("创建模拟字幕文件...")

    subtitle_content = """WEBVTT

00:00:00.000 --> 00:00:05.000
欢迎来到今天的越野摩托车技术教学

00:00:05.000 --> 00:00:10.000
我们将学习如何正确使用刹车

00:00:28.000 --> 00:00:35.000
首先让我们看看front brake的使用

00:00:30.000 --> 00:00:38.000
The front brake provides most of your stopping power

00:01:12.000 --> 00:01:20.000
Now let's talk about body position

00:01:15.000 --> 00:01:22.000
When cornering, you need to lean your body into the turn

00:01:18.000 --> 00:01:25.000
Keeping your weight centered is crucial for balance

00:02:42.000 --> 00:02:48.000
Let's see how to combine front and rear brakes

00:02:45.000 --> 00:02:52.000
The key is smooth application of both brakes

00:04:15.000 --> 00:04:22.000
Now watch this jump technique

00:04:18.000 --> 00:04:25.000
When taking off, keep your body centered

00:05:05.000 --> 00:05:12.000
The landing is just as important as the takeoff

00:05:08.000 --> 00:05:15.000
Bend your knees to absorb the impact
"""

    with open(subtitle_path, 'w', encoding='utf-8') as f:
        f.write(subtitle_content)

    logger.success(f"✓ 模拟字幕已创建: {subtitle_path}")


def test_notebooklm_helper():
    """测试NotebookLMHelper类"""
    logger.info("\n" + "=" * 70)
    logger.info("测试1: NotebookLMHelper - 报告解析")
    logger.info("=" * 70)

    try:
        helper = NotebookLMHelper()

        # 创建模拟报告
        report_path = "./output/test_report.txt"
        create_mock_report(report_path)

        # 测试验证
        logger.info("\n1.1 测试报告验证...")
        is_valid = helper.validate_report(report_path)
        assert is_valid, "报告验证失败"
        logger.success("✓ 报告验证通过")

        # 测试解析
        logger.info("\n1.2 测试报告解析...")
        result = helper.parse_report(report_path)

        assert result["title"], "标题为空"
        assert result["summary"], "摘要为空"
        assert len(result["techniques"]) > 0, "技术列表为空"
        assert len(result["key_moments"]) > 0, "关键时刻为空"

        logger.success("✓ 报告解析成功")
        logger.info(f"  标题: {result['title']}")
        logger.info(f"  技术数量: {len(result['techniques'])}")
        logger.info(f"  关键时刻: {len(result['key_moments'])}")

        # 测试技术提取
        logger.info("\n1.3 检查技术提取结果...")
        for i, tech in enumerate(result["techniques"][:3], 1):
            logger.info(f"  {i}. {tech['name']}")
            logger.info(f"     关键词: {', '.join(tech['keywords'][:5])}")

        logger.success("\n✓ NotebookLMHelper所有测试通过")
        return True

    except Exception as e:
        logger.error(f"\n✗ NotebookLMHelper测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def test_timestamp_extractor():
    """测试TimestampExtractor类"""
    logger.info("\n" + "=" * 70)
    logger.info("测试2: TimestampExtractor - 时间戳提取")
    logger.info("=" * 70)

    try:
        extractor = TimestampExtractor()

        # 创建模拟字幕
        subtitle_path = "./output/test_subtitle.vtt"
        create_mock_subtitle(subtitle_path)

        # 测试关键词搜索
        logger.info("\n2.1 测试关键词搜索...")
        keywords = ["front brake", "body position", "jump", "landing"]
        matches = extractor.search_keywords(subtitle_path, keywords)

        assert len(matches) > 0, "未找到匹配"
        logger.success(f"✓ 找到{len(matches)}个匹配")

        # 检查匹配结果
        logger.info("\n2.2 检查匹配结果...")
        for i, match in enumerate(matches[:3], 1):
            logger.info(f"  {i}. 关键词: {match['keyword']}")
            logger.info(f"     时间: {match['timestamp']}")
            logger.info(f"     中间时间: {match['mid_seconds']:.2f}秒")
            logger.info(f"     文本: {match['text'][:60]}...")

        # 测试时间戳计算
        logger.info("\n2.3 测试时间戳转换...")
        test_cases = [
            ("00:00:30.000", 30.0),
            ("00:01:15.500", 75.5),
            ("00:02:45.000", 165.0),
        ]

        for vtt_time, expected_seconds in test_cases:
            actual_seconds = extractor._vtt_time_to_seconds(vtt_time)
            assert abs(actual_seconds - expected_seconds) < 0.01, f"时间转换错误: {vtt_time}"
            logger.info(f"  ✓ {vtt_time} = {actual_seconds}秒")

        logger.success("✓ 时间戳转换正确")

        logger.success("\n✓ TimestampExtractor所有测试通过")
        return True

    except Exception as e:
        logger.error(f"\n✗ TimestampExtractor测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def test_content_analyzer():
    """测试ContentAnalyzer类"""
    logger.info("\n" + "=" * 70)
    logger.info("测试3: ContentAnalyzer - 完整分析流程")
    logger.info("=" * 70)

    try:
        analyzer = ContentAnalyzer()

        # 创建测试文件
        report_path = "./output/test_report.txt"
        subtitle_path = "./output/test_subtitle.vtt"
        video_id = "test_video_123"

        create_mock_report(report_path)
        create_mock_subtitle(subtitle_path)

        # 执行分析
        logger.info("\n3.1 执行完整分析...")
        analysis = analyzer.analyze(
            report_path=report_path,
            subtitle_path=subtitle_path,
            video_id=video_id
        )

        # 验证结果
        logger.info("\n3.2 验证分析结果...")
        assert analysis.video_id == video_id, "视频ID不匹配"
        assert analysis.title, "标题为空"
        assert len(analysis.key_moments) > 0, "关键时刻为空"

        logger.success("✓ 分析结果验证通过")
        logger.info(f"  视频标题: {analysis.title}")
        logger.info(f"  关键时刻数量: {len(analysis.key_moments)}")

        # 测试保存和加载
        logger.info("\n3.3 测试保存和加载...")
        output_path = "./output/test_analysis.json"
        analyzer.save_analysis(analysis, output_path)

        loaded_analysis = analyzer.load_analysis(output_path)
        assert loaded_analysis.video_id == analysis.video_id, "加载的视频ID不匹配"
        assert len(loaded_analysis.key_moments) == len(analysis.key_moments), "加载的时刻数量不匹配"

        logger.success("✓ 保存和加载测试通过")

        # 打印摘要
        logger.info("\n3.4 打印分析摘要...")
        analyzer.print_summary(analysis)

        logger.success("\n✓ ContentAnalyzer所有测试通过")
        return True

    except Exception as e:
        logger.error(f"\n✗ ContentAnalyzer测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def test_media_generation_params():
    """测试媒体生成参数提取"""
    logger.info("\n" + "=" * 70)
    logger.info("测试4: 媒体生成参数提取")
    logger.info("=" * 70)

    try:
        analyzer = ContentAnalyzer()

        # 创建并分析测试文件
        report_path = "./output/test_report.txt"
        subtitle_path = "./output/test_subtitle.vtt"
        video_id = "test_video_123"

        create_mock_report(report_path)
        create_mock_subtitle(subtitle_path)

        analysis = analyzer.analyze(report_path, subtitle_path, video_id)

        # 获取媒体生成参数
        logger.info("\n4.1 提取媒体生成参数...")
        media_params = analyzer.get_timestamps_for_media_generation(analysis)

        assert len(media_params) > 0, "媒体参数为空"
        logger.success(f"✓ 提取了{len(media_params)}个媒体参数")

        # 检查参数类型
        logger.info("\n4.2 检查参数类型...")
        static_count = sum(1 for p in media_params if p["media_type"] == "static")
        gif_count = sum(1 for p in media_params if p["media_type"] == "gif")

        logger.info(f"  静态图片: {static_count}")
        logger.info(f"  GIF动图: {gif_count}")

        # 显示示例参数
        logger.info("\n4.3 示例媒体参数:")
        for i, param in enumerate(media_params[:3], 1):
            media_icon = "🎬" if param["media_type"] == "gif" else "📷"
            logger.info(f"  {i}. {media_icon} {param['technique']}")
            logger.info(f"     时间: {param['timestamp']:.2f}秒")
            logger.info(f"     类型: {param['media_type']}")
            if param["media_type"] == "gif":
                logger.info(f"     时长: {param.get('duration', 0):.1f}秒")

        logger.success("\n✓ 媒体生成参数测试通过")
        return True

    except Exception as e:
        logger.error(f"\n✗ 媒体生成参数测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def test_real_world_scenario():
    """测试真实场景（如果有实际文件）"""
    logger.info("\n" + "=" * 70)
    logger.info("测试5: 真实场景测试（可选）")
    logger.info("=" * 70)

    # 检查是否有真实的报告和字幕文件
    report_dir = Path("./output/reports")
    subtitle_dir = Path("./output/subtitles")

    if not report_dir.exists() or not subtitle_dir.exists():
        logger.warning("未找到真实的报告/字幕文件，跳过真实场景测试")
        logger.info("提示: 将NotebookLM报告和字幕文件放到对应目录以进行测试")
        return True

    # 查找文件
    report_files = list(report_dir.glob("*.txt"))
    subtitle_files = list(subtitle_dir.glob("*.vtt"))

    if not report_files or not subtitle_files:
        logger.warning("未找到测试文件，跳过真实场景测试")
        return True

    logger.info(f"找到 {len(report_files)} 个报告文件")
    logger.info(f"找到 {len(subtitle_files)} 个字幕文件")

    # 使用第一个文件进行测试
    report_path = str(report_files[0])
    subtitle_path = str(subtitle_files[0])

    try:
        analyzer = ContentAnalyzer()
        video_id = Path(subtitle_path).stem

        logger.info(f"\n使用文件:")
        logger.info(f"  报告: {Path(report_path).name}")
        logger.info(f"  字幕: {Path(subtitle_path).name}")

        analysis = analyzer.analyze(report_path, subtitle_path, video_id)
        analyzer.print_summary(analysis)

        logger.success("\n✓ 真实场景测试通过")
        return True

    except Exception as e:
        logger.error(f"\n✗ 真实场景测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("MotoStep - 内容分析模块测试套件")
    logger.info("=" * 70)
    logger.info("\n此测试包括报告解析、时间戳提取和完整分析流程\n")

    # 确保输出目录存在
    Path("./output").mkdir(exist_ok=True)

    tests = [
        ("NotebookLMHelper", test_notebooklm_helper),
        ("TimestampExtractor", test_timestamp_extractor),
        ("ContentAnalyzer", test_content_analyzer),
        ("媒体生成参数", test_media_generation_params),
        ("真实场景", test_real_world_scenario),
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
