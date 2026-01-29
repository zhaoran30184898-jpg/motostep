"""FFmpeg命令封装"""
import subprocess
from typing import List, Optional, Tuple
from pathlib import Path
from loguru import logger
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import settings


class FFmpegWrapper:
    """FFmpeg命令行工具封装"""

    def __init__(self):
        """初始化FFmpeg包装器"""
        self.ffmpeg_path = "ffmpeg"
        self.ffprobe_path = "ffprobe"

    def screenshot_command(
        self,
        video_path: str,
        timestamp: float,
        output_path: str,
        quality: int = 2
    ) -> List[str]:
        """
        生成截图命令

        Args:
            video_path: 视频文件路径
            timestamp: 时间戳（秒）
            output_path: 输出文件路径
            quality: JPG质量（1-31，越小越好）

        Returns:
            FFmpeg命令列表
        """
        cmd = [
            self.ffmpeg_path,
            "-ss", str(timestamp),
            "-i", video_path,
            "-vframes", "1",
            "-q:v", str(quality),
            "-y",  # 覆盖输出文件
            output_path
        ]
        return cmd

    def gif_command(
        self,
        video_path: str,
        start_time: float,
        duration: float,
        output_path: str,
        width: int = 480,
        fps: int = 10,
        use_palette: bool = True
    ) -> Tuple[List[str], Optional[List[str]]]:
        """
        生成GIF命令（支持调色板优化）

        Args:
            video_path: 视频文件路径
            start_time: 开始时间（秒）
            duration: 持续时长（秒）
            output_path: 输出文件路径
            width: 宽度（像素）
            fps: 帧率
            use_palette: 是否使用调色板优化

        Returns:
            (主命令, 调色板命令) 元组，如果不使用调色板则第二项为None
        """
        if use_palette:
            # 两步法：先生成调色板，再生成GIF
            palette_path = output_path.replace(".gif", "_palette.png")

            # 第一步：生成调色板
            palette_cmd = [
                self.ffmpeg_path,
                "-ss", str(start_time),
                "-t", str(duration),
                "-i", video_path,
                "-vf", f"fps={fps},scale={width}:-1:flags=lanczos,palettegen",
                "-y",
                palette_path
            ]

            # 第二步：使用调色板生成GIF
            gif_cmd = [
                self.ffmpeg_path,
                "-ss", str(start_time),
                "-t", str(duration),
                "-i", video_path,
                "-i", palette_path,
                "-filter_complex", f"fps={fps},scale={width}:-1:flags=lanczos[x];[x][1:v]paletteuse",
                "-y",
                output_path
            ]

            return gif_cmd, palette_cmd
        else:
            # 直接生成GIF（不使用调色板）
            gif_cmd = [
                self.ffmpeg_path,
                "-ss", str(start_time),
                "-t", str(duration),
                "-i", video_path,
                "-vf", f"fps={fps},scale={width}:-1",
                "-y",
                output_path
            ]

            return gif_cmd, None

    def watermark_command(
        self,
        input_path: str,
        output_path: str,
        text: str,
        position: str = "bottom-left",
        font_size: int = 16,
        opacity: float = 0.7
    ) -> List[str]:
        """
        生成水印命令

        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            text: 水印文字
            position: 位置（bottom-left, bottom-right等）
            font_size: 字体大小
            opacity: 不透明度（0.0-1.0）

        Returns:
            FFmpeg命令列表
        """
        # 计算位置参数
        if position == "bottom-left":
            x_pos = "10"
            y_pos = "h-th-10"
        elif position == "bottom-right":
            x_pos = "w-tw-10"
            y_pos = "h-th-10"
        elif position == "top-left":
            x_pos = "10"
            y_pos = "10"
        elif position == "top-right":
            x_pos = "w-tw-10"
            y_pos = "10"
        else:
            # 默认左下角
            x_pos = "10"
            y_pos = "h-th-10"

        # 构建drawtext滤镜
        drawtext_filter = (
            f"drawtext=text='{text}':"
            f"fontsize={font_size}:"
            f"fontcolor=white@{opacity}:"
            f"x={x_pos}:"
            f"y={y_pos}"
        )

        cmd = [
            self.ffmpeg_path,
            "-i", input_path,
            "-vf", drawtext_filter,
            "-y",
            output_path
        ]
        return cmd

    def run_command(self, cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """
        执行FFmpeg命令

        Args:
            cmd: 命令列表
            check: 是否检查返回码

        Returns:
            子进程结果
        """
        logger.debug(f"执行命令: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=check
        )

        return result

    def get_video_duration(self, video_path: str) -> float:
        """
        获取视频时长

        Args:
            video_path: 视频文件路径

        Returns:
            时长（秒）
        """
        cmd = [
            self.ffprobe_path,
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ]

        result = self.run_command(cmd, check=False)

        if result.returncode == 0:
            duration = float(result.stdout.strip())
            return duration
        else:
            raise Exception(f"获取视频时长失败: {result.stderr}")

    def get_video_info(self, video_path: str) -> dict:
        """
        获取视频详细信息

        Args:
            video_path: 视频文件路径

        Returns:
            视频信息字典
        """
        cmd = [
            self.ffprobe_path,
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,duration",
            "-of", "json",
            video_path
        ]

        result = self.run_command(cmd, check=False)

        if result.returncode == 0:
            import json
            data = json.loads(result.stdout)
            if "streams" in data and len(data["streams"]) > 0:
                return data["streams"][0]
            return {}
        else:
            raise Exception(f"获取视频信息失败: {result.stderr}")
