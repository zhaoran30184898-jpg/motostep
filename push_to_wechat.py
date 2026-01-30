"""推送文章到微信公众号草稿箱"""
import sys
from pathlib import Path
import getpass
import requests
import subprocess
import re

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

# 设置UTF-8输出
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from loguru import logger

# 配置日志
logger.remove()
logger.add(
    sink=lambda msg: print(msg, end=""),
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO",
    colorize=False
)


class WeChatPublisher:
    """微信公众号文章发布器"""

    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = None
        self.base_url = "https://api.weixin.qq.com/cgi-bin"

    def get_access_token(self):
        """获取访问令牌"""
        logger.info("获取 Access Token...")

        url = f"{self.base_url}/token"
        params = {
            'grant_type': 'client_credential',
            'appid': self.app_id,
            'secret': self.app_secret
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            result = response.json()

            if 'access_token' in result:
                self.access_token = result['access_token']
                logger.success(f"✓ Access Token 获取成功")
                return self.access_token
            else:
                logger.error(f"✗ 获取失败: {result}")
                return None

        except Exception as e:
            logger.error(f"✗ 异常: {e}")
            return None

    def compress_gif(self, gif_path, output_path, target_size_mb=1.8):
        """压缩 GIF 到指定大小以下"""
        logger.info(f"  压缩: {Path(gif_path).name}")
        original_size = Path(gif_path).stat().st_size / (1024 * 1024)

        if original_size <= target_size_mb:
            logger.info(f"  已符合要求 ({original_size:.1f} MB)")
            import shutil
            shutil.copy(gif_path, output_path)
            return True

        # 使用 ffmpeg 压缩
        cmd = ['ffmpeg', '-i', gif_path, '-vf', 'fps=8,scale=400:-1',
               '-f', 'gif', output_path, '-y']

        try:
            subprocess.run(cmd, capture_output=True, check=True)
            compressed_size = Path(output_path).stat().st_size / (1024 * 1024)
            logger.info(f"  压缩后: {compressed_size:.1f} MB")
            return compressed_size <= target_size_mb
        except:
            return False

    def upload_media(self, file_path, compress_gif=False):
        """上传媒体文件"""
        filename = Path(file_path).name
        logger.info(f"  上传: {filename}")

        # 如果是 GIF 且需要压缩
        if compress_gif and file_path.lower().endswith('.gif'):
            temp_path = str(Path(file_path).parent / f"compressed_{filename}")
            if self.compress_gif(file_path, temp_path):
                upload_path = temp_path
            else:
                logger.warning("  压缩失败，上传原文件")
                upload_path = file_path
        else:
            upload_path = file_path

        url = f"{self.base_url}/material/add_material?access_token={self.access_token}&type=image"

        try:
            with open(upload_path, 'rb') as f:
                files = {'media': f}
                response = requests.post(url, files=files, timeout=60)

            result = response.json()

            if 'media_id' in result:
                media_id = result['media_id']
                logger.success(f"  ✓ 成功: {media_id}")

                # 删除临时文件
                if upload_path != file_path:
                    Path(upload_path).unlink(missing_ok=True)

                return media_id
            else:
                logger.error(f"  ✗ 失败: {result}")
                return None

        except Exception as e:
            logger.error(f"  ✗ 异常: {e}")
            return None

    def replace_media_in_html(self, html_content, media_mapping):
        """替换 HTML 中的媒体路径为 media_id"""
        # 匹配 src="media/xxx.gif"
        pattern = r'src="media/([^"]+)"'

        def replace(match):
            filename = match.group(1)
            for local_path, media_id in media_mapping.items():
                if filename in local_path and media_id:
                    return f'src="{media_id}"'
            return match.group(0)

        return re.sub(pattern, replace, html_content)

    def publish_to_draft(self, title, html_content, media_mapping=None):
        """发布到草稿箱"""
        logger.info("发布到草稿箱...")

        # 替换媒体路径
        if media_mapping:
            html_content = self.replace_media_in_html(html_content, media_mapping)

        url = f"{self.base_url}/draft/add?access_token={self.access_token}"

        # 提取纯文本摘要
        soup = re.sub(r'<[^>]+>', '', html_content)
        digest = soup[:100].strip()

        draft_data = {
            "articles": [{
                "title": title,
                "author": "MotoStep",
                "digest": digest,
                "content": html_content,
                "content_source_url": "",
                "thumb_media_id": "",
                "show_cover_pic": 0,
                "need_open_comment": 1,
                "only_fans_can_comment": 0
            }]
        }

        try:
            response = requests.post(url, json=draft_data, timeout=30)
            result = response.json()

            if 'media_id' in result:
                return result['media_id']
            else:
                logger.error(f"✗ 失败: {result}")
                return None

        except Exception as e:
            logger.error(f"✗ 异常: {e}")
            return None


def main():
    logger.info("=" * 70)
    logger.info("微信公众号文章推送工具")
    logger.info("=" * 70)

    # 输入凭证
    logger.info("\n请输入微信公众号凭证：")
    app_id = input("AppID: ").strip()
    app_secret = getpass.getpass("AppSecret: ").strip()

    if not app_id or not app_secret:
        logger.error("✗ AppID 和 AppSecret 不能为空")
        return

    # 文件路径
    html_file = r"C:\Users\dbaa\Desktop\MotoStep\output\articles\Mikuni_HSR42\进气之争：Mikuni HSR 42 真的值那 300 美金吗？.html"
    media_dir = r"C:\Users\dbaa\Desktop\MotoStep\output\articles\Mikuni_HSR42\media"

    # 读取 HTML
    logger.info("\n读取文章内容...")
    html_path = Path(html_file)

    if not html_path.exists():
        logger.error(f"✗ 文件不存在: {html_file}")
        return

    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    title = html_path.stem
    logger.info(f"  标题: {title}")

    # 确认
    logger.info("\n" + "=" * 70)
    logger.info("推送配置:")
    logger.info("=" * 70)
    logger.info(f"\n文章: {title}")
    logger.info(f"媒体目录: {Path(media_dir).name}")
    logger.info(f"媒体处理: 压缩 GIF 到 2MB 以下")
    logger.info("\n注意: 上传可能需要几分钟...")

    confirm = input("\n确认推送？(y/n): ").strip().lower()

    if confirm != 'y':
        logger.info("已取消")
        return

    # 创建发布器
    publisher = WeChatPublisher(app_id, app_secret)

    # 步骤0: 获取 Access Token
    logger.info("\n" + "=" * 70)
    logger.info("步骤0: 获取 Access Token")
    logger.info("=" * 70)

    if not publisher.get_access_token():
        logger.error("✗ 获取失败，请检查 AppID 和 AppSecret")
        return

    # 步骤1: 上传媒体文件
    logger.info("\n" + "=" * 70)
    logger.info("步骤1: 上传媒体文件")
    logger.info("=" * 70)

    media_path = Path(media_dir)
    media_files = []
    media_mapping = {}

    if media_path.exists():
        # 获取所有 GIF 和图片文件
        media_files = list(media_path.glob("*.gif")) + list(media_path.glob("*.jpg"))

        if media_files:
            logger.info(f"\n找到 {len(media_files)} 个媒体文件")

            for i, media_file in enumerate(media_files, 1):
                logger.info(f"\n[{i}/{len(media_files)}] {media_file.name}")
                media_id = publisher.upload_media(str(media_file), compress_gif=True)

                if media_id:
                    media_mapping[str(media_file)] = media_id
        else:
            logger.warning("\n未找到媒体文件")
    else:
        logger.warning(f"\n媒体目录不存在: {media_dir}")

    # 步骤2: 发布到草稿箱
    logger.info("\n" + "=" * 70)
    logger.info("步骤2: 发布到草稿箱")
    logger.info("=" * 70)

    draft_id = publisher.publish_to_draft(title, html_content, media_mapping)

    if draft_id:
        logger.success("\n" + "=" * 70)
        logger.success("✓ 推送成功！")
        logger.success("=" * 70)
        logger.info(f"\n草稿 ID: {draft_id}")
        logger.info("\n下一步：")
        logger.info("1. 登录微信公众号后台: https://mp.weixin.qq.com/")
        logger.info("2. 进入「草稿箱」")
        logger.info("3. 找到该文章并编辑")
        logger.info("4. 检查格式和媒体")
        logger.info("5. 点击「保存并群发」")
    else:
        logger.error("\n✗ 推送失败")
        logger.info("\n请检查:")
        logger.info("1. AppID 和 AppSecret 是否正确")
        logger.info("2. 网络连接是否正常")
        logger.info("3. 微信公众号 API 是否可用")


if __name__ == "__main__":
    main()
