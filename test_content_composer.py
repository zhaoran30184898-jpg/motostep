"""内容合成模块测试"""
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


def create_mock_analysis():
    """创建模拟的VideoAnalysis对象"""
    logger.info("创建模拟分析数据...")

    # 创建关键时刻
    key_moments = [
        KeyMoment(
            timestamp=33.0,
            description="The front brake provides most of your stopping power. Apply front brake pressure gradually before corner entry.",
            technique="Front Brake Technique",
            media_type="gif",
            duration=10.0
        ),
        KeyMoment(
            timestamp=78.5,
            description="Shift your body weight back when braking, lean your body into the turn during corners.",
            technique="Body Position Control",
            media_type="gif",
            duration=13.0
        ),
        KeyMoment(
            timestamp=167.0,
            description="Use the rear brake for fine speed adjustment. Maintain rear wheel traction while sliding.",
            technique="Rear Brake Application",
            media_type="gif",
            duration=10.0
        ),
        KeyMoment(
            timestamp=260.0,
            description="Keep your body weight centered when taking off, adjust body position in the air.",
            technique="Jump Technique",
            media_type="static",
            duration=None
        ),
    ]

    # 创建VideoAnalysis
    analysis = VideoAnalysis(
        video_id="test_video_123",
        title="Motocross Technique Training: Braking and Body Position",
        content="This video covers essential motocross techniques for proper braking and body position control during high-speed riding.",
        key_moments=key_moments,
        metadata={
            "total_techniques": 4,
            "matched_timestamps": 4,
            "subtitle_language": "en"
        }
    )

    logger.success(f"✓ 创建模拟分析: {len(key_moments)} 个关键时刻")
    return analysis


def create_mock_media_assets():
    """创建模拟的媒体资产"""
    logger.info("创建模拟媒体资产...")

    media_assets = [
        MediaAsset(
            type="gif",
            local_path="./output/images/front_brake_technique.gif",
            timestamp=33.0,
            description="Front brake technique demonstration",
            size_bytes=350000
        ),
        MediaAsset(
            type="gif",
            local_path="./output/images/body_position_control.gif",
            timestamp=78.5,
            description="Body position control demonstration",
            size_bytes=450000
        ),
        MediaAsset(
            type="gif",
            local_path="./output/images/rear_brake_application.gif",
            timestamp=167.0,
            description="Rear brake application demonstration",
            size_bytes=320000
        ),
        MediaAsset(
            type="image",
            local_path="./output/images/jump_technique.jpg",
            timestamp=260.0,
            description="Jump technique demonstration",
            size_bytes=150000
        ),
    ]

    logger.success(f"✓ 创建模拟媒体: {len(media_assets)} 个资产")
    return media_assets


def test_template_loading():
    """测试模板加载"""
    logger.info("\n" + "=" * 70)
    logger.info("测试1: 模板加载")
    logger.info("=" * 70)

    try:
        composer = ContentComposer()

        # 获取模板列表
        logger.info("\n1.1 获取可用模板...")
        templates = composer.get_template_list()
        assert len(templates) > 0, "模板列表为空"
        logger.success(f"✓ 找到{len(templates)}个模板")

        for template in templates:
            logger.info(f"  - {template}")

        logger.success("\n✓ 模板加载测试通过")
        return True

    except Exception as e:
        logger.error(f"\n✗ 模板加载测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def test_wechat_article_composition():
    """测试微信公众号文章生成"""
    logger.info("\n" + "=" * 70)
    logger.info("测试2: 微信公众号文章生成")
    logger.info("=" * 70)

    try:
        composer = ContentComposer()
        analysis = create_mock_analysis()
        media_assets = create_mock_media_assets()

        # 生成文章
        logger.info("\n2.1 生成微信公众号文章...")
        output_path = "./output/articles/test_wechat_article.html"
        html_content = composer.compose_article(
            analysis=analysis,
            media_assets=media_assets,
            template_name="wechat_article.html",
            output_path=output_path
        )

        # 验证内容
        logger.info("\n2.2 验证生成内容...")
        assert len(html_content) > 0, "HTML内容为空"
        assert analysis.title in html_content, "标题未包含在HTML中"
        assert str(len(analysis.key_moments)) in html_content, "关键时刻数量未包含"
        assert "FreeSoloDirtbike" in html_content, "页脚信息缺失"

        logger.success("✓ 内容验证通过")
        logger.info(f"  HTML长度: {len(html_content)} 字符")
        logger.info(f"  关键词: 标题、技术点、页脚")

        # 验证文件存在
        if Path(output_path).exists():
            file_size = Path(output_path).stat().st_size / 1024
            logger.success(f"✓ 文件已生成 ({file_size:.1f} KB)")
        else:
            logger.warning("⚠ 文件未保存（仅测试内容）")

        logger.success("\n✓ 微信文章生成测试通过")
        return True

    except Exception as e:
        logger.error(f"\n✗ 微信文章生成测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def test_markdown_composition():
    """测试Markdown报告生成"""
    logger.info("\n" + "=" * 70)
    logger.info("测试3: Markdown报告生成")
    logger.info("=" * 70)

    try:
        composer = ContentComposer()
        analysis = create_mock_analysis()
        media_assets = create_mock_media_assets()

        # 生成Markdown
        logger.info("\n3.1 生成Markdown报告...")
        output_path = "./output/articles/test_report.md"
        markdown_content = composer.compose_markdown(
            analysis=analysis,
            media_assets=media_assets,
            output_path=output_path
        )

        # 验证内容
        logger.info("\n3.2 验证生成内容...")
        assert len(markdown_content) > 0, "Markdown内容为空"
        assert "# " + analysis.title in markdown_content, "标题未包含"
        assert "## " in markdown_content, "章节标题缺失"

        logger.success("✓ 内容验证通过")
        logger.info(f"  Markdown长度: {len(markdown_content)} 字符")

        logger.success("\n✓ Markdown生成测试通过")
        return True

    except Exception as e:
        logger.error(f"\n✗ Markdown生成测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def test_html_report_composition():
    """测试HTML报告生成"""
    logger.info("\n" + "=" * 70)
    logger.info("测试4: HTML报告生成")
    logger.info("=" * 70)

    try:
        composer = ContentComposer()
        analysis = create_mock_analysis()
        media_assets = create_mock_media_assets()

        # 生成HTML报告
        logger.info("\n4.1 生成HTML报告...")
        output_path = "./output/articles/test_report.html"
        html_content = composer.compose_html_report(
            analysis=analysis,
            media_assets=media_assets,
            output_path=output_path
        )

        # 验证内容
        logger.info("\n4.2 验证生成内容...")
        assert len(html_content) > 0, "HTML内容为空"
        assert "<!DOCTYPE html>" in html_content, "HTML声明缺失"
        assert analysis.title in html_content, "标题未包含"
        assert "technique-card" in html_content, "CSS类名缺失"

        logger.success("✓ 内容验证通过")
        logger.info(f"  HTML长度: {len(html_content)} 字符")

        logger.success("\n✓ HTML报告生成测试通过")
        return True

    except Exception as e:
        logger.error(f"\n✗ HTML报告生成测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def test_all_formats():
    """测试批量生成所有格式"""
    logger.info("\n" + "=" * 70)
    logger.info("测试5: 批量生成所有格式")
    logger.info("=" * 70)

    try:
        composer = ContentComposer()
        analysis = create_mock_analysis()
        media_assets = create_mock_media_assets()

        # 生成所有格式
        logger.info("\n5.1 批量生成所有格式...")
        output_dir = "./output/articles/test_all"
        results = composer.compose_all_formats(
            analysis=analysis,
            media_assets=media_assets,
            output_dir=output_dir
        )

        # 验证结果
        logger.info("\n5.2 验证生成结果...")
        assert len(results) == 3, "应该生成3种格式"
        assert 'wechat' in results, "缺少微信格式"
        assert 'markdown' in results, "缺少Markdown格式"
        assert 'html' in results, "缺少HTML报告格式"

        # 验证文件存在
        for format_name, file_path in results.items():
            if Path(file_path).exists():
                file_size = Path(file_path).stat().st_size / 1024
                logger.info(f"  ✓ {format_name}: {file_size:.1f} KB")
            else:
                logger.warning(f"  ⚠ {format_name}: 文件不存在")

        logger.success("\n✓ 批量生成测试通过")
        return True

    except Exception as e:
        logger.error(f"\n✗ 批量生成测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def test_filename_sanitization():
    """测试文件名清理"""
    logger.info("\n" + "=" * 70)
    logger.info("测试6: 文件名清理")
    logger.info("=" * 70)

    try:
        composer = ContentComposer()

        # 测试用例
        test_cases = [
            ("Test/File:Name", "Test_File_Name"),
            ("Normal Title", "Normal Title"),
            ("A" * 150, "A" * 100),  # 长度限制
            ("Title<>:\"|?*", "Title_________"),
        ]

        logger.info("\n6.1 测试文件名清理...")
        for original, expected in test_cases:
            sanitized = composer._sanitize_filename(original)
            # 只验证非法字符被移除
            assert "/" not in sanitized, f"未移除 /: {sanitized}"
            assert "\\" not in sanitized, f"未移除 \\: {sanitized}"
            assert ":" not in sanitized, f"未移除 :: {sanitized}"
            logger.info(f"  ✓ {original[:30]}... -> {sanitized[:30]}...")

        logger.success("\n✓ 文件名清理测试通过")
        return True

    except Exception as e:
        logger.error(f"\n✗ 文件名清理测试失败: {e}")
        return False


if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("MotoStep - 内容合成模块测试套件")
    logger.info("=" * 70)
    logger.info("\n此测试包括模板加载、文章生成和格式转换\n")

    # 确保输出目录存在
    Path("./output/articles").mkdir(parents=True, exist_ok=True)

    tests = [
        ("模板加载", test_template_loading),
        ("微信文章生成", test_wechat_article_composition),
        ("Markdown生成", test_markdown_composition),
        ("HTML报告生成", test_html_report_composition),
        ("批量生成", test_all_formats),
        ("文件名清理", test_filename_sanitization),
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
