"""内容合成模块 - ContentComposer"""
import sys
from pathlib import Path
from typing import List, Optional, Dict
from loguru import logger
from datetime import datetime
import os

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from jinja2 import Environment, FileSystemLoader, select_autoescape
from src.models.video import VideoAnalysis, MediaAsset
from config import settings


class ContentComposer:
    """内容合成器 - 整合分析结果和媒体资产生成文章"""

    def __init__(self, template_dir: Optional[str] = None):
        """
        初始化内容合成器

        Args:
            template_dir: 模板目录路径（默认使用内置模板）
        """
        if template_dir is None:
            template_dir = str(Path(__file__).parent / "templates")

        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )

        logger.info(f"模板目录: {template_dir}")

    def compose_article(
        self,
        analysis: VideoAnalysis,
        media_assets: List[MediaAsset],
        template_name: str = "wechat_article.html",
        output_path: Optional[str] = None
    ) -> str:
        """
        合成文章

        Args:
            analysis: 视频分析结果
            media_assets: 媒体资产列表（按时间戳排序）
            template_name: 模板文件名
            output_path: 输出文件路径（可选）

        Returns:
            生成的HTML内容
        """
        logger.info("=" * 70)
        logger.info("内容合成 - ContentComposer")
        logger.info("=" * 70)

        # 步骤1: 匹配媒体资产到关键时刻
        logger.info("\n步骤1: 匹配媒体资产到关键时刻...")
        matched_analysis = self._match_media_to_moments(analysis, media_assets)

        # 步骤2: 加载模板
        logger.info(f"\n步骤2: 加载模板: {template_name}")
        try:
            template = self.env.get_template(template_name)
            logger.success("✓ 模板加载成功")
        except Exception as e:
            logger.error(f"✗ 模板加载失败: {e}")
            raise

        # 步骤3: 准备模板数据
        logger.info("\n步骤3: 准备模板数据...")
        template_data = {
            "analysis": matched_analysis,
            "metadata": {
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "generated_by": "MotoStep v0.5.0"
            }
        }
        logger.success("✓ 模板数据准备完成")

        # 步骤4: 渲染模板
        logger.info("\n步骤4: 渲染模板...")
        try:
            rendered_content = template.render(**template_data)
            logger.success("✓ 模板渲染成功")
            logger.info(f"  内容长度: {len(rendered_content)} 字符")
        except Exception as e:
            logger.error(f"✗ 模板渲染失败: {e}")
            raise

        # 步骤5: 保存到文件（如果指定）
        if output_path:
            logger.info(f"\n步骤5: 保存到文件: {output_path}")
            self._save_content(rendered_content, output_path, template_name)

        logger.success("\n✓ 内容合成完成")
        return rendered_content

    def _match_media_to_moments(
        self,
        analysis: VideoAnalysis,
        media_assets: List[MediaAsset]
    ) -> VideoAnalysis:
        """
        将媒体资产匹配到关键时刻

        Args:
            analysis: 视频分析结果
            media_assets: 媒体资产列表

        Returns:
            更新后的VideoAnalysis对象
        """
        logger.info(f"  分析结果: {len(analysis.key_moments)} 个关键时刻")
        logger.info(f"  媒体资产: {len(media_assets)} 个文件")

        # 创建媒体资产时间戳索引
        media_index = {asset.timestamp: asset for asset in media_assets}

        matched_count = 0
        for moment in analysis.key_moments:
            # 查找匹配的媒体资产（允许1秒误差）
            matched_asset = None
            for asset in media_assets:
                if abs(asset.timestamp - moment.timestamp) < 1.0:
                    matched_asset = asset
                    break

            if matched_asset:
                # 为关键时刻添加媒体资产
                moment.media_asset = matched_asset
                matched_count += 1
                logger.debug(f"  ✓ 匹配: {moment.technique} -> {matched_asset.local_path}")

        logger.info(f"  成功匹配: {matched_count}/{len(analysis.key_moments)}")
        return analysis

    def _save_content(
        self,
        content: str,
        output_path: str,
        template_name: str
    ) -> None:
        """
        保存内容到文件

        Args:
            content: 要保存的内容
            output_path: 输出文件路径
            template_name: 模板名称（用于确定编码）
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # 根据文件类型选择编码
        encoding = 'utf-8'

        with open(output_file, 'w', encoding=encoding) as f:
            f.write(content)

        file_size = output_file.stat().st_size / 1024
        logger.success(f"✓ 文件已保存 ({file_size:.1f} KB)")

    def compose_markdown(
        self,
        analysis: VideoAnalysis,
        media_assets: List[MediaAsset],
        output_path: Optional[str] = None
    ) -> str:
        """
        合成Markdown报告

        Args:
            analysis: 视频分析结果
            media_assets: 媒体资产列表
            output_path: 输出文件路径（可选）

        Returns:
            生成的Markdown内容
        """
        logger.info("合成Markdown报告...")

        # 匹配媒体资产
        matched_analysis = self._match_media_to_moments(analysis, media_assets)

        # 加载模板
        template = self.env.get_template("report_markdown.md")

        # 渲染
        template_data = {
            "analysis": matched_analysis,
            "metadata": {
                "created_at": datetime.now().strftime("%Y-%m-%d"),
                "generated_by": "MotoStep"
            }
        }

        rendered_content = template.render(**template_data)

        # 保存
        if output_path:
            self._save_content(rendered_content, output_path, "report_markdown.md")

        logger.success("✓ Markdown报告生成完成")
        return rendered_content

    def compose_html_report(
        self,
        analysis: VideoAnalysis,
        media_assets: List[MediaAsset],
        output_path: Optional[str] = None
    ) -> str:
        """
        合成HTML报告（用于Web展示）

        Args:
            analysis: 视频分析结果
            media_assets: 媒体资产列表
            output_path: 输出文件路径（可选）

        Returns:
            生成的HTML内容
        """
        logger.info("合成HTML报告...")

        # 匹配媒体资产
        matched_analysis = self._match_media_to_moments(analysis, media_assets)

        # 加载模板
        template = self.env.get_template("report_html.html")

        # 渲染
        template_data = {
            "analysis": matched_analysis,
            "metadata": {
                "created_at": datetime.now().strftime("%Y-%m-%d"),
                "generated_by": "MotoStep"
            }
        }

        rendered_content = template.render(**template_data)

        # 保存
        if output_path:
            self._save_content(rendered_content, output_path, "report_html.html")

        logger.success("✓ HTML报告生成完成")
        return rendered_content

    def compose_all_formats(
        self,
        analysis: VideoAnalysis,
        media_assets: List[MediaAsset],
        output_dir: str
    ) -> Dict[str, str]:
        """
        生成所有格式的文章

        Args:
            analysis: 视频分析结果
            media_assets: 媒体资产列表
            output_dir: 输出目录

        Returns:
            各格式文件的路径字典
        """
        logger.info("=" * 70)
        logger.info("生成所有格式的文章")
        logger.info("=" * 70)

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 生成文件名
        base_filename = self._sanitize_filename(analysis.title)
        video_id = analysis.video_id

        results = {}

        # 1. 微信公众号HTML
        logger.info("\n1. 生成微信公众号文章...")
        wechat_path = output_path / f"{base_filename}_wechat.html"
        results['wechat'] = self.compose_article(
            analysis,
            media_assets,
            "wechat_article.html",
            str(wechat_path)
        )

        # 2. Markdown报告
        logger.info("\n2. 生成Markdown报告...")
        markdown_path = output_path / f"{base_filename}_report.md"
        results['markdown'] = self.compose_markdown(
            analysis,
            media_assets,
            str(markdown_path)
        )

        # 3. HTML报告（Web）
        logger.info("\n3. 生成HTML报告...")
        html_path = output_path / f"{base_filename}_report.html"
        results['html'] = self.compose_html_report(
            analysis,
            media_assets,
            str(html_path)
        )

        logger.success("\n✓ 所有格式生成完成")
        logger.info(f"\n生成的文件:")
        for format_name, file_path in results.items():
            logger.info(f"  {format_name}: {file_path}")

        return results

    def _sanitize_filename(self, filename: str) -> str:
        """
        清理文件名，移除非法字符

        Args:
            filename: 原始文件名

        Returns:
            清理后的文件名
        """
        # 移除或替换非法字符
        illegal_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        sanitized = filename

        for char in illegal_chars:
            sanitized = sanitized.replace(char, '_')

        # 限制长度
        if len(sanitized) > 100:
            sanitized = sanitized[:100]

        return sanitized.strip()

    def adapt_for_wechat(
        self,
        html_content: str,
        inline_css: bool = True
    ) -> str:
        """
        适配微信公众号格式

        Args:
            html_content: 原始HTML内容
            inline_css: 是否将CSS内联（推荐）

        Returns:
            适配后的HTML内容
        """
        logger.info("适配微信公众号格式...")

        adapted = html_content

        if inline_css:
            # CSS已经内联在模板中，无需额外处理
            logger.debug("  CSS已内联")
        else:
            logger.warning("  建议使用内联CSS以获得最佳兼容性")

        # 确保所有标签都闭合
        # （Jinja2模板已经处理）

        logger.success("✓ 微信格式适配完成")
        return adapted

    def get_template_list(self) -> List[str]:
        """
        获取可用模板列表

        Returns:
            模板文件名列表
        """
        templates = []

        template_path = Path(self.template_dir)
        if template_path.exists():
            for file in template_path.glob("*.html"):
                templates.append(file.name)
            for file in template_path.glob("*.md"):
                templates.append(file.name)

        return sorted(templates)

    def compose_plain_text(
        self,
        analysis: VideoAnalysis,
        media_assets: List[MediaAsset],
        output_path: Optional[str] = None
    ) -> str:
        """
        合成纯文本报告（无格式，适用于任何平台）

        Args:
            analysis: 视频分析结果
            media_assets: 媒体资产列表
            output_path: 输出文件路径（可选）

        Returns:
            生成的纯文本内容
        """
        logger.info("合成纯文本报告...")

        # 匹配媒体资产
        matched_analysis = self._match_media_to_moments(analysis, media_assets)

        # 生成纯文本内容
        lines = []

        # 标题和元数据
        lines.append(analysis.title)
        lines.append("")
        lines.append(f"来源: {analysis.video_id}")
        lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")

        # 内容概要
        if analysis.content:
            lines.append("内容概要:")
            lines.append("")
            lines.append(analysis.content)
            lines.append("")
            lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            lines.append("")

        # 关键技术点
        if matched_analysis.key_moments:
            lines.append("关键技术详解:")
            lines.append("")

            for i, moment in enumerate(matched_analysis.key_moments, 1):
                # 技术标题
                lines.append(f"{i}. {moment.technique}")
                lines.append("")

                # 时间信息
                lines.append(f"时间点: {moment.timestamp}秒")
                if moment.duration:
                    lines.append(f"时长: {moment.duration}秒")
                lines.append("")

                # 媒体类型
                if moment.media_type == 'gif':
                    lines.append("[动图演示]")
                elif moment.media_type == 'static':
                    lines.append("[静态图片]")
                lines.append("")

                # 技术说明
                lines.append(moment.description)
                lines.append("")

                # 媒体文件信息
                if moment.media_asset:
                    media_type = "动图" if moment.media_type == 'gif' else "图片"
                    lines.append(f"[{media_type}: {moment.technique}]")
                    lines.append("")

                lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                lines.append("")

            # 统计信息
            lines.append("技术统计:")
            lines.append("")
            lines.append(f"• 技术总数: {len(matched_analysis.key_moments)} 项")
            gif_count = sum(1 for m in matched_analysis.key_moments if m.media_type == 'gif')
            img_count = sum(1 for m in matched_analysis.key_moments if m.media_type == 'static')
            lines.append(f"• 动图演示: {gif_count} 个")
            lines.append(f"• 静态图片: {img_count} 个")
            lines.append("")

        # 页脚
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")
        lines.append("内容由 MotoStep 自动生成")
        lines.append(f"来源视频: {analysis.video_id}")

        rendered_content = "\n".join(lines)

        # 保存
        if output_path:
            self._save_content(rendered_content, output_path, "plain_text.txt")

        logger.success("✓ 纯文本报告生成完成")
        return rendered_content
