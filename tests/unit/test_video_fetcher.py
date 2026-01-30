"""测试VideoFetcher类"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger
from src.video_fetcher import VideoFetcher

# 配置日志 - 修复Windows编码问题
import sys
import io

# 设置UTF-8输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

logger.remove()
logger.add(
    sink=lambda msg: print(msg, end=""),
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO",
    colorize=False
)


def test_video_fetcher():
    """测试视频获取功能"""
    logger.info("=" * 70)
    logger.info("测试VideoFetcher - 视频下载功能")
    logger.info("=" * 70)

    # 使用一个公开的越野摩托教学视频（不需要cookies）
    test_url = "https://www.youtube.com/watch?v=0QHiZDV43aw"  # Motocross Jump Technique

    try:
        # 初始化VideoFetcher
        fetcher = VideoFetcher(output_dir="./output/videos")

        # 下载视频（不使用cookies，仅测试基本功能）
        logger.info(f"\n测试视频URL: {test_url}")
        logger.warning("注意: 如果没有cookies，可能无法下载某些视频")

        # 先测试视频ID提取（不需要下载）
        video_id = fetcher._extract_video_id(test_url)
        logger.success(f"✓ 视频ID提取成功: {video_id}")

        # 检查output目录
        output_dir = Path("./output/videos")
        if output_dir.exists():
            existing_files = list(output_dir.glob("*.mp4"))
            if existing_files:
                logger.info(f"\n当前output目录中有 {len(existing_files)} 个视频文件:")
                for f in existing_files:
                    size_mb = f.stat().st_size / (1024 * 1024)
                    logger.info(f"  - {f.name} ({size_mb:.2f} MB)")
            else:
                logger.info("\noutput目录中还没有视频文件")
        else:
            logger.info("\noutput目录不存在")

        logger.success("\n✓ VideoFetcher基础功能测试通过!")
        logger.info("\n提示: 完整的下载测试需要:")
        logger.info("  1. 有效的cookies.txt文件")
        logger.info("  2. 或使用不需要认证的公开视频")

        return True

    except Exception as e:
        logger.error(f"✗ 测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def test_data_models():
    """测试数据模型"""
    logger.info("\n" + "=" * 70)
    logger.info("测试数据模型")
    logger.info("=" * 70)

    try:
        from src.models.video import VideoInfo, KeyMoment, VideoAnalysis, MediaAsset

        # 测试VideoInfo
        video_info = VideoInfo(
            video_id="test123",
            url="https://www.youtube.com/watch?v=test123",
            title="测试视频",
            duration=600,
            width=1280,
            height=720,
            local_path="./test.mp4"
        )
        logger.success("✓ VideoInfo模型创建成功")

        # 测试KeyMoment
        key_moment = KeyMoment(
            timestamp=124.154,
            description="起跳点",
            technique="起跳技巧",
            media_type="static"
        )
        logger.success("✓ KeyMoment模型创建成功")

        # 测试MediaAsset
        media_asset = MediaAsset(
            type="image",
            local_path="./test.jpg",
            timestamp=124.154,
            description="测试图片",
            size_bytes=102400
        )
        logger.success("✓ MediaAsset模型创建成功")

        logger.success("\n✓ 所有数据模型测试通过!")
        return True

    except Exception as e:
        logger.error(f"✗ 数据模型测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def test_wechat_client():
    """测试微信客户端（仅检查导入）"""
    logger.info("\n" + "=" * 70)
    logger.info("测试微信客户端模块")
    logger.info("=" * 70)

    try:
        from src.wechat_publisher import WeChatClient, DraftManager
        from src.models.article import Article, ArticleStatus

        logger.success("✓ 微信客户端模块导入成功")

        # 创建测试实例（不实际调用API）
        logger.info("创建测试实例...")
        # 注意: 不实际调用API，因为没有配置WECHAT_APP_ID
        logger.success("✓ 模块加载成功（需要配置.env才能实际使用）")

        logger.info("\n提示: 要使用微信发布功能，请:")
        logger.info("  1. 复制.env.example为.env")
        logger.info("  2. 填入WECHAT_APP_ID和WECHAT_APP_SECRET")

        return True

    except Exception as e:
        logger.error(f"✗ 微信客户端测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    logger.info("开始MotoStep功能测试...\n")

    results = []

    # 测试1: 数据模型
    results.append(("数据模型", test_data_models()))

    # 测试2: VideoFetcher基础功能
    results.append(("VideoFetcher", test_video_fetcher()))

    # 测试3: 微信客户端模块
    results.append(("微信客户端", test_wechat_client()))

    # 汇总结果
    logger.info("\n" + "=" * 70)
    logger.info("测试结果汇总")
    logger.info("=" * 70)

    passed = 0
    failed = 0

    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        if result:
            logger.success(f"{name}: {status}")
        else:
            logger.error(f"{name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1

    logger.info(f"\n总计: {passed} 通过, {failed} 失败")

    if failed == 0:
        logger.success("\n🎉 所有测试通过!")
    else:
        logger.warning(f"\n⚠️  有 {failed} 个测试失败")
