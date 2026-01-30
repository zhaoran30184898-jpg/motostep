"""微信公众号媒体上传模块"""
import sys
from pathlib import Path
from typing import Optional, Dict
import requests
import subprocess
from loguru import logger

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class MediaUploader:
    """微信公众号媒体上传器"""

    def __init__(self, access_token: str):
        """
        初始化媒体上传器

        Args:
            access_token: 微信公众号访问令牌
        """
        self.access_token = access_token
        self.base_url = "https://api.weixin.qq.com/cgi-bin"

    def compress_gif_for_wechat(self, gif_path: str, output_path: str, target_size_mb: float = 1.8) -> bool:
        """
        压缩 GIF 到指定大小以下（微信限制 2MB）

        Args:
            gif_path: 原始 GIF 路径
            output_path: 输出路径
            target_size_mb: 目标大小（MB）

        Returns:
            是否成功
        """
        logger.info(f"压缩 GIF: {Path(gif_path).name}")
        logger.info(f"  目标大小: {target_size_mb} MB")

        # 检查原始文件大小
        original_size = Path(gif_path).stat().st_size / (1024 * 1024)
        logger.info(f"  原始大小: {original_size:.1f} MB")

        if original_size <= target_size_mb:
            logger.info("  文件已符合要求，无需压缩")
            # 直接复制文件
            import shutil
            shutil.copy(gif_path, output_path)
            return True

        # 使用 ffmpeg 压缩
        # 策略：降低帧率和尺寸
        cmd = [
            'ffmpeg',
            '-i', gif_path,
            '-vf', 'fps=8,scale=400:-1',  # 降低到 8fps，宽度400px
            '-f', 'gif',
            output_path,
            '-y'
        ]

        try:
            logger.info("  开始压缩...")
            result = subprocess.run(cmd, capture_output=True, check=True)

            # 检查压缩后文件大小
            compressed_size = Path(output_path).stat().st_size / (1024 * 1024)
            logger.info(f"  压缩后大小: {compressed_size:.1f} MB")

            if compressed_size <= target_size_mb:
                logger.success("  ✓ 压缩成功")
                return True
            else:
                # 如果仍然过大，进一步压缩
                logger.warning(f"  ⚠ 文件仍然过大 ({compressed_size:.1f} MB)，尝试进一步压缩...")

                cmd2 = [
                    'ffmpeg',
                    '-i', output_path,
                    '-vf', 'fps=5,scale=320:-1',  # 进一步降低
                    '-f', 'gif',
                    output_path + '_tmp.gif',
                    '-y'
                ]

                subprocess.run(cmd2, capture_output=True, check=True)

                # 替换文件
                Path(output_path + '_tmp.gif').replace(output_path)

                final_size = Path(output_path).stat().st_size / (1024 * 1024)
                logger.info(f"  最终大小: {final_size:.1f} MB")

                if final_size <= target_size_mb:
                    logger.success("  ✓ 压缩成功")
                    return True
                else:
                    logger.error(f"  ✗ 无法压缩到 {target_size_mb} MB 以下")
                    return False

        except subprocess.CalledProcessError as e:
            logger.error(f"  ✗ 压缩失败: {e}")
            return False

    def upload_image(self, image_path: str) -> Optional[str]:
        """
        上传图片到微信公众号永久素材库

        Args:
            image_path: 图片路径

        Returns:
            媒体 ID（media_id），失败返回 None
        """
        logger.info(f"上传图片: {Path(image_path).name}")

        url = f"{self.base_url}/material/add_material?access_token={self.access_token}&type=image"

        try:
            with open(image_path, 'rb') as f:
                files = {'media': f}
                response = requests.post(url, files=files, timeout=30)

            result = response.json()

            if 'media_id' in result:
                media_id = result['media_id']
                logger.success(f"  ✓ 上传成功: {media_id}")
                return media_id
            else:
                logger.error(f"  ✗ 上传失败: {result}")
                return None

        except Exception as e:
            logger.error(f"  ✗ 上传异常: {e}")
            return None

    def upload_article_thumbnail(self, image_path: str) -> Optional[str]:
        """
        上传文章封面图（缩略图）

        Args:
            image_path: 图片路径

        Returns:
            图片 URL，失败返回 None
        """
        logger.info(f"上传封面图: {Path(image_path).name}")

        url = f"{self.base_url}/media/uploadimg?access_token={self.access_token}"

        try:
            with open(image_path, 'rb') as f:
                files = {'media': f}
                response = requests.post(url, files=files, timeout=30)

            result = response.json()

            if 'url' in result:
                img_url = result['url']
                logger.success(f"  ✓ 上传成功: {img_url}")
                return img_url
            else:
                logger.error(f"  ✗ 上传失败: {result}")
                return None

        except Exception as e:
            logger.error(f"  ✗ 上传异常: {e}")
            return None

    def batch_upload_images(self, image_paths: list, compress: bool = True) -> Dict[str, Optional[str]]:
        """
        批量上传图片

        Args:
            image_paths: 图片路径列表
            compress: 是否压缩 GIF

        Returns:
            {文件路径: media_id} 字典
        """
        logger.info(f"批量上传 {len(image_paths)} 个图片文件")

        results = {}

        for i, image_path in enumerate(image_paths, 1):
            logger.info(f"\n[{i}/{len(image_paths)}] {Path(image_path).name}")

            # 检查是否为 GIF 且需要压缩
            if compress and image_path.lower().endswith('.gif'):
                # 创建临时压缩文件
                temp_path = str(Path(image_path).parent / f"compressed_{Path(image_path).name}")

                # 压缩
                if self.compress_gif_for_wechat(image_path, temp_path):
                    # 上传压缩后的文件
                    media_id = self.upload_image(temp_path)
                    results[image_path] = media_id

                    # 删除临时文件
                    Path(temp_path).unlink(missing_ok=True)
                else:
                    # 压缩失败，尝试上传原文件
                    logger.warning("  压缩失败，尝试上传原文件")
                    media_id = self.upload_image(image_path)
                    results[image_path] = media_id
            else:
                # 直接上传
                media_id = self.upload_image(image_path)
                results[image_path] = media_id

        # 统计结果
        success_count = sum(1 for m in results.values() if m is not None)
        logger.success(f"\n✓ 上传完成: {success_count}/{len(image_paths)} 成功")

        return results
