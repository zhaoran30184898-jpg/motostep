"""内容分析模块 - ContentAnalyzer"""
import sys
from pathlib import Path
from typing import List, Dict, Optional
from loguru import logger
import json

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.content_analyzer.notebooklm_helper import NotebookLMHelper
from src.content_analyzer.timestamp_extractor import TimestampExtractor
from src.models.video import VideoAnalysis, KeyMoment


class ContentAnalyzer:
    """内容分析器 - 整合NotebookLM报告和字幕时间戳"""

    def __init__(self, subtitle_language: str = "en"):
        """
        初始化内容分析器

        Args:
            subtitle_language: 字幕语言 (en, zh-Hans, zh-Hant)
        """
        self.notebooklm_helper = NotebookLMHelper()
        self.timestamp_extractor = TimestampExtractor()
        self.subtitle_language = subtitle_language

    def analyze(
        self,
        report_path: str,
        subtitle_path: str,
        video_id: str
    ) -> VideoAnalysis:
        """
        分析NotebookLM报告并提取关键时间戳

        Args:
            report_path: NotebookLM报告路径（.txt）
            subtitle_path: 字幕文件路径（.vtt）
            video_id: 视频ID

        Returns:
            VideoAnalysis对象
        """
        logger.info("=" * 70)
        logger.info("内容分析 - ContentAnalyzer")
        logger.info("=" * 70)

        # 步骤1: 验证报告文件
        logger.info("\n步骤1: 验证报告文件...")
        if not self.notebooklm_helper.validate_report(report_path):
            raise ValueError(f"无效的报告文件: {report_path}")
        logger.success("✓ 报告文件有效")

        # 步骤2: 解析NotebookLM报告
        logger.info("\n步骤2: 解析NotebookLM报告...")
        report_data = self.notebooklm_helper.parse_report(report_path)

        # 步骤3: 提取时间戳
        logger.info("\n步骤3: 提取技术时间戳...")
        techniques_with_timestamps = self.timestamp_extractor.extract_all_techniques(
            techniques=report_data["techniques"],
            subtitle_path=subtitle_path,
            key_moments=report_data["key_moments"]
        )

        # 步骤4: 构建KeyMoment对象列表
        logger.info("\n步骤4: 构建关键时刻列表...")
        key_moments = []
        for tech in techniques_with_timestamps:
            if tech["mid_seconds"] is not None:
                # 根据时间范围决定媒体类型
                duration = tech["end_seconds"] - tech["start_seconds"]
                media_type = "gif" if duration > 3 else "static"

                key_moment = KeyMoment(
                    timestamp=tech["mid_seconds"],
                    description=tech["description"],
                    technique=tech["technique_name"],
                    media_type=media_type,
                    duration=duration if media_type == "gif" else None
                )
                key_moments.append(key_moment)

        logger.success(f"✓ 构建了{len(key_moments)}个关键时刻")

        # 步骤5: 创建VideoAnalysis对象
        logger.info("\n步骤5: 创建分析结果...")
        analysis = VideoAnalysis(
            video_id=video_id,
            title=report_data["title"],
            content=report_data["summary"],
            key_moments=key_moments,
            metadata={
                "total_techniques": len(techniques_with_timestamps),
                "matched_timestamps": len(key_moments),
                "subtitle_language": self.subtitle_language,
                "techniques": techniques_with_timestamps,
                "report_path": report_path,
                "subtitle_path": subtitle_path
            }
        )

        logger.success("\n✓ 内容分析完成")
        logger.info(f"  视频标题: {analysis.title}")
        logger.info(f"  技术总数: {len(techniques_with_timestamps)}")
        logger.info(f"  已匹配时间戳: {len(key_moments)}")

        return analysis

    def save_analysis(self, analysis: VideoAnalysis, output_path: str) -> None:
        """
        保存分析结果到JSON文件

        Args:
            analysis: VideoAnalysis对象
            output_path: 输出文件路径
        """
        logger.info(f"保存分析结果到: {output_path}")

        # 转换为JSON可序列化的格式
        analysis_dict = {
            "video_id": analysis.video_id,
            "title": analysis.title,
            "content": analysis.content,
            "key_moments": [
                {
                    "timestamp": km.timestamp,
                    "description": km.description,
                    "technique": km.technique,
                    "media_type": km.media_type,
                    "duration": km.duration
                }
                for km in analysis.key_moments
            ],
            "metadata": analysis.metadata
        }

        # 写入文件
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_dict, f, ensure_ascii=False, indent=2)

        logger.success(f"✓ 分析结果已保存")

    def load_analysis(self, input_path: str) -> VideoAnalysis:
        """
        从JSON文件加载分析结果

        Args:
            input_path: 输入文件路径

        Returns:
            VideoAnalysis对象
        """
        logger.info(f"加载分析结果: {input_path}")

        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 重建KeyMoment对象
        key_moments = [
            KeyMoment(**km_data)
            for km_data in data["key_moments"]
        ]

        # 创建VideoAnalysis对象
        analysis = VideoAnalysis(
            video_id=data["video_id"],
            title=data["title"],
            content=data["content"],
            key_moments=key_moments,
            metadata=data.get("metadata", {})
        )

        logger.success(f"✓ 分析结果已加载")
        logger.info(f"  视频ID: {analysis.video_id}")
        logger.info(f"  关键时刻: {len(analysis.key_moments)}")

        return analysis

    def get_timestamps_for_media_generation(
        self,
        analysis: VideoAnalysis
    ) -> List[Dict]:
        """
        获取用于媒体生成的时间戳列表

        Args:
            analysis: VideoAnalysis对象

        Returns:
            媒体生成参数列表，每个包含：
            - timestamp: 时间戳
            - media_type: 媒体类型 (static/gif)
            - duration: GIF时长（仅GIF）
            - description: 描述
            - technique: 技术名称
        """
        media_params = []

        for moment in analysis.key_moments:
            param = {
                "timestamp": moment.timestamp,
                "media_type": moment.media_type,
                "description": moment.description,
                "technique": moment.technique
            }

            if moment.media_type == "gif" and moment.duration:
                param["duration"] = moment.duration

            media_params.append(param)

        return media_params

    def print_summary(self, analysis: VideoAnalysis) -> None:
        """
        打印分析结果摘要

        Args:
            analysis: VideoAnalysis对象
        """
        logger.info("\n" + "=" * 70)
        logger.info("分析结果摘要")
        logger.info("=" * 70)

        logger.info(f"\n视频ID: {analysis.video_id}")
        logger.info(f"标题: {analysis.title}")
        logger.info(f"关键时刻数量: {len(analysis.key_moments)}")

        logger.info("\n关键时刻列表:")
        for i, moment in enumerate(analysis.key_moments, 1):
            media_icon = "🎬" if moment.media_type == "gif" else "📷"
            duration_str = f" ({moment.duration:.1f}s)" if moment.duration else ""

            logger.info(
                f"{i}. {media_icon} {moment.technique} - "
                f"{moment.timestamp:.2f}秒{duration_str}"
            )
            logger.info(f"   {moment.description[:80]}...")

        logger.info("\n" + "=" * 70)
