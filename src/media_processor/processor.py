"""媒体处理模块 - MediaProcessor"""
import os
from pathlib import Path
from typing import List, Optional
from loguru import logger
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import settings
from src.media_processor.ffmpeg_wrapper import FFmpegWrapper
from src.models.video import MediaAsset


class MediaProcessor:
    """媒体处理器 - 处理截图、GIF和水印"""

    def __init__(self, watermark_text: Optional[str] = None):
        """
        初始化媒体处理器

        Args:
            watermark_text: 水印文字，默认从配置读取
        """
        self.wrapper = FFmpegWrapper()
        self.watermark_text = watermark_text or settings.watermark_text

    def extract_screenshot(
        self,
        video_path: str,
        timestamp: float,
        output_path: Optional[str] = None,
        quality: int = 2
    ) -> str:
        """
        提取高质量截图

        Args:
            video_path: 视频文件路径
            timestamp: 时间戳（秒）
            output_path: 输出文件路径（可选）
            quality: JPG质量（1-31，越小越好）

        Returns:
            截图文件路径
        """
        if output_path is None:
            video_dir = Path(video_path).parent
            output_path = str(video_dir / f"screenshot_{timestamp:.3f}.jpg")

        logger.info(f"提取截图: {timestamp:.3f}秒 -> {output_path}")

        # 生成命令
        cmd = self.wrapper.screenshot_command(
            video_path=video_path,
            timestamp=timestamp,
            output_path=output_path,
            quality=quality
        )

        # 执行命令
        result = self.wrapper.run_command(cmd)

        # 验证输出文件
        if Path(output_path).exists():
            file_size = Path(output_path).stat().st_size / 1024
            logger.success(f"✓ 截图生成成功 ({file_size:.1f} KB)")
            return output_path
        else:
            raise Exception(f"截图生成失败: {output_path}")

    def generate_gif(
        self,
        video_path: str,
        start_time: float,
        duration: float,
        output_path: Optional[str] = None,
        width: int = 480,
        fps: int = 10,
        use_palette: bool = True
    ) -> str:
        """
        生成GIF动图

        Args:
            video_path: 视频文件路径
            start_time: 开始时间（秒）
            duration: 持续时长（秒）
            output_path: 输出文件路径（可选）
            width: 宽度（像素）
            fps: 帧率
            use_palette: 是否使用调色板优化

        Returns:
            GIF文件路径
        """
        if output_path is None:
            video_dir = Path(video_path).parent
            output_path = str(video_dir / f"gif_{start_time:.0f}_{duration:.0f}s.gif")

        logger.info(f"生成GIF: {start_time:.0f}秒, {duration:.0f}秒, {width}px")

        # 生成命令
        gif_cmd, palette_cmd = self.wrapper.gif_command(
            video_path=video_path,
            start_time=start_time,
            duration=duration,
            output_path=output_path,
            width=width,
            fps=fps,
            use_palette=use_palette
        )

        # 如果使用调色板，先生成调色板
        if use_palette and palette_cmd:
            logger.debug("生成调色板...")
            palette_result = self.wrapper.run_command(palette_cmd, check=False)
            if palette_result.returncode != 0:
                logger.warning(f"调色板生成失败: {palette_result.stderr}")

        # 执行GIF生成命令
        result = self.wrapper.run_command(gif_cmd)

        # 清理调色板文件（如果存在）
        if use_palette:
            palette_path = output_path.replace(".gif", "_palette.png")
            Path(palette_path).unlink(missing_ok=True)

        # 验证输出文件
        if Path(output_path).exists():
            file_size = Path(output_path).stat().st_size / 1024
            logger.success(f"✓ GIF生成成功 ({file_size:.1f} KB)")
            return output_path
        else:
            raise Exception(f"GIF生成失败: {output_path}")

    def add_watermark(
        self,
        media_path: str,
        output_path: Optional[str] = None,
        text: Optional[str] = None,
        position: str = "bottom-left",
        font_size: int = 16,
        opacity: float = 0.7
    ) -> str:
        """
        添加水印

        Args:
            media_path: 媒体文件路径（图片或GIF）
            output_path: 输出文件路径（可选）
            text: 水印文字（可选）
            position: 位置（bottom-left, bottom-right等）
            font_size: 字体大小
            opacity: 不透明度（0.0-1.0）

        Returns:
            输出文件路径
        """
        if text is None:
            text = self.watermark_text

        if output_path is None:
            # 自动生成输出文件名
            path = Path(media_path)
            stem = path.stem
            suffix = path.suffix
            output_path = str(path.parent / f"{stem}_wm{suffix}")

        logger.info(f"添加水印: {media_path} -> {output_path}")

        # 生成命令
        cmd = self.wrapper.watermark_command(
            input_path=media_path,
            output_path=output_path,
            text=text,
            position=position,
            font_size=font_size,
            opacity=opacity
        )

        # 执行命令
        result = self.wrapper.run_command(cmd)

        # 验证输出文件
        if Path(output_path).exists():
            logger.success(f"✓ 水印添加成功")
            return output_path
        else:
            raise Exception(f"水印添加失败: {output_path}")

    def batch_process_screenshots(
        self,
        video_path: str,
        timestamps: List[float],
        output_dir: Optional[str] = None,
        quality: int = 2
    ) -> List[str]:
        """
        批量提取截图

        Args:
            video_path: 视频文件路径
            timestamps: 时间戳列表
            output_dir: 输出目录（可选）
            quality: JPG质量

        Returns:
            截图文件路径列表
        """
        if output_dir is None:
            output_dir = str(Path(video_path).parent)

        output_paths = []

        logger.info(f"批量提取{len(timestamps)}张截图...")

        for i, timestamp in enumerate(timestamps, 1):
            try:
                output_path = os.path.join(
                    output_dir,
                    f"{i:02d}_screenshot_{timestamp:.3f}.jpg"
                )

                result_path = self.extract_screenshot(
                    video_path=video_path,
                    timestamp=timestamp,
                    output_path=output_path,
                    quality=quality
                )

                output_paths.append(result_path)

            except Exception as e:
                logger.error(f"✗ 截图{i}失败: {e}")
                continue

        logger.success(f"批量截图完成: {len(output_paths)}/{len(timestamps)} 成功")
        return output_paths

    def batch_process_gifs(
        self,
        video_path: str,
        clips: List[tuple],
        output_dir: Optional[str] = None,
        width: int = 480,
        fps: int = 10,
        use_palette: bool = True
    ) -> List[str]:
        """
        批量生成GIF

        Args:
            video_path: 视频文件路径
            clips: (start_time, duration) 元组列表
            output_dir: 输出目录（可选）
            width: 宽度
            fps: 帧率
            use_palette: 是否使用调色板

        Returns:
            GIF文件路径列表
        """
        if output_dir is None:
            output_dir = str(Path(video_path).parent)

        output_paths = []

        logger.info(f"批量生成{len(clips)}个GIF...")

        for i, (start_time, duration) in enumerate(clips, 1):
            try:
                output_path = os.path.join(
                    output_dir,
                    f"gif_{i:02d}_{start_time:.0f}s_{duration:.0f}s.gif"
                )

                result_path = self.generate_gif(
                    video_path=video_path,
                    start_time=start_time,
                    duration=duration,
                    output_path=output_path,
                    width=width,
                    fps=fps,
                    use_palette=use_palette
                )

                output_paths.append(result_path)

            except Exception as e:
                logger.error(f"✗ GIF{i}失败: {e}")
                continue

        logger.success(f"批量GIF生成完成: {len(output_paths)}/{len(clips)} 成功")
        return output_paths

    def batch_add_watermarks(
        self,
        media_paths: List[str],
        output_dir: Optional[str] = None,
        text: Optional[str] = None
    ) -> List[str]:
        """
        批量添加水印

        Args:
            media_paths: 媒体文件路径列表
            output_dir: 输出目录（可选）
            text: 水印文字（可选）

        Returns:
            输出文件路径列表
        """
        if output_dir is None:
            output_dir = str(Path(media_paths[0]).parent)

        output_paths = []

        logger.info(f"批量添加水印到{len(media_paths)}个文件...")

        for media_path in media_paths:
            try:
                filename = Path(media_path).stem
                suffix = Path(media_path).suffix

                # 生成输出路径
                if "_wm" not in filename:
                    output_filename = f"{filename}_wm{suffix}"
                else:
                    output_filename = f"{filename}{suffix}"

                output_path = os.path.join(output_dir, output_filename)

                result_path = self.add_watermark(
                    media_path=media_path,
                    output_path=output_path,
                    text=text
                )

                output_paths.append(result_path)

            except Exception as e:
                logger.error(f"✗ 水印添加失败: {media_path} - {e}")
                continue

        logger.success(f"批量水印添加完成: {len(output_paths)}/{len(media_paths)} 成功")
        return output_paths
