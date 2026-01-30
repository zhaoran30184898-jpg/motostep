"""视频获取模块 - VideoFetcher"""
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from loguru import logger
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.models.video import VideoInfo


class VideoFetcher:
    """视频获取器"""

    def __init__(self, output_dir: str = "./output/videos"):
        """
        初始化视频获取器

        Args:
            output_dir: 视频输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def download_video(
        self,
        url: str,
        quality: str = "720p",
        cookies_path: str = None
    ) -> VideoInfo:
        """
        下载YouTube视频

        Args:
            url: YouTube视频URL
            quality: 视频质量 (720p, 1080p)
            cookies_path: cookies文件路径

        Returns:
            VideoInfo对象
        """
        logger.info(f"开始下载视频: {url}")
        logger.info(f"质量: {quality}")

        # 使用yt-dlp Python库
        try:
            import yt_dlp
        except ImportError:
            raise Exception("yt-dlp未安装，请运行: pip install yt-dlp")

        # 根据质量选择格式 - 使用更灵活的格式选择
        if quality == "1080p":
            format_spec = "bestvideo[height<=?1080]+bestaudio/best[height<=?1080]"
        elif quality == "480p":
            format_spec = "bestvideo[height<=?480]+bestaudio/best[height<=?480]"
        else:  # 720p (默认)
            format_spec = "bestvideo[height<=?720]+bestaudio/best[height<=?720]"

        # 配置yt-dlp选项
        ydl_opts = {
            'format': format_spec,
            'merge_output_format': 'mp4',
            'outtmpl': str(self.output_dir / "%(title)s. [%(id)s].%(ext)s"),
            'quiet': False,
            'no_warnings': False,
            'ignoreerrors': True,  # 忽略不可用格式
        }

        # 添加cookies（如果提供）
        if cookies_path and Path(cookies_path).exists():
            ydl_opts['cookiefile'] = cookies_path
            logger.info(f"使用cookies: {cookies_path}")
        elif cookies_path:
            logger.warning(f"⚠ Cookies文件不存在: {cookies_path}")

        try:
            # 下载视频
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info("开始下载...")
                ydl.download([url])

            # 提取视频ID
            video_id = self._extract_video_id(url)

            # 查找下载的文件（匹配包含video_id的mp4文件）
            video_files = [f for f in self.output_dir.glob("*.mp4") if video_id in f.stem]

            if not video_files:
                all_mp4 = list(self.output_dir.glob("*.mp4"))
                logger.debug(f"找到的mp4文件: {[f.name for f in all_mp4]}")
                raise Exception(f"未找到下载的视频文件 (video_id: {video_id})")

            video_path = video_files[0]
            logger.success(f"✓ 视频下载成功: {video_path.name}")

            # 获取视频信息
            video_info = self._get_video_info(url, video_path)
            return video_info

        except Exception as e:
            logger.error(f"下载失败: {e}")
            raise Exception(f"视频下载失败: {e}")

    def download_subtitles(
        self,
        url: str,
        video_id: str,
        languages: List[str] = ["en", "zh-Hans", "zh-Hant"],
        cookies_path: str = "cookies.txt"
    ) -> Dict[str, str]:
        """
        下载字幕文件

        Args:
            url: YouTube视频URL
            video_id: 视频ID
            languages: 语言列表
            cookies_path: cookies文件路径

        Returns:
            字幕文件路径字典 {语言: 路径}
        """
        logger.info(f"开始下载字幕: {languages}")

        subtitle_paths = {}

        for lang in languages:
            cmd = [
                "yt-dlp",
                "--cookies", cookies_path,
                "--write-subs",
                "--write-auto-subs",
                "--sub-langs", lang,
                "--sub-format", "vtt",
                "--skip-download",
                "-o", str(self.output_dir / "%(title)s. [%(id)s].%(ext)s"),
                url
            ]

            try:
                logger.debug(f"下载{lang}字幕...")
                subprocess.run(cmd, capture_output=True, check=True)

                # 查找字幕文件
                subtitle_files = list(self.output_dir.glob(f"*[{video_id}].{lang}.vtt"))
                if subtitle_files:
                    subtitle_paths[lang] = str(subtitle_files[0])
                    logger.success(f"{lang}字幕下载成功")
                else:
                    logger.warning(f"未找到{lang}字幕文件")

            except subprocess.CalledProcessError as e:
                logger.warning(f"下载{lang}字幕失败: {e}")

        return subtitle_paths

    def _extract_video_id(self, url: str) -> str:
        """
        从URL提取视频ID

        Args:
            url: YouTube URL

        Returns:
            视频ID
        """
        import re
        # 匹配YouTube视频ID
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:v=)([0-9A-Za-z_-]{11})'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        raise ValueError(f"无法从URL提取视频ID: {url}")

    def _get_video_info(self, url: str, video_path: Path) -> VideoInfo:
        """
        获取视频详细信息

        Args:
            url: 视频URL
            video_path: 视频文件路径

        Returns:
            VideoInfo对象
        """
        # 使用ffprobe获取视频信息
        cmd = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,duration",
            "-of", "json",
            str(video_path)
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            import json
            video_data = json.loads(result.stdout)
            stream = video_data.get("streams", [{}])[0]

            width = stream.get("width", 1280)
            height = stream.get("height", 720)
            duration = int(float(stream.get("duration", 0)))

        except Exception as e:
            logger.warning(f"获取视频信息失败: {e}")
            width = 1280
            height = 720
            duration = 0

        # 获取文件大小
        file_size = video_path.stat().st_size

        # 提取视频ID
        video_id = self._extract_video_id(url)

        # 从文件名提取标题
        title = video_path.stem.replace(f".[{video_id}]", "")

        return VideoInfo(
            video_id=video_id,
            url=url,
            title=title,
            duration=duration,
            width=width,
            height=height,
            local_path=str(video_path),
            file_size_bytes=file_size
        )
