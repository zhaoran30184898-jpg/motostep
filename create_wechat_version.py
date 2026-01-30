"""创建适合微信公众号的HTML版本"""
import sys
from pathlib import Path
import re
import shutil

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

# 设置UTF-8输出
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from loguru import logger

# 配置日志
logger.remove()
logger.add(
    sink=lambda msg: print(msg, end=""),
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO",
    colorize=False
)

def create_wechat_html():
    """创建微信公众号专用HTML"""

    # 读取原始报告
    report_path = r"C:\Users\dbaa\Desktop\MotoStep\report_source\Mikuni HSR 42 真的值那 300 美金吗.txt"
    media_dir = Path("output/articles/Mikuni_HSR42/media")

    with open(report_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    title = lines[0].strip()

    # 解析内容
    sections = []
    current_section = []

    for line in lines[1:]:
        line = line.rstrip()
        time_match = re.match(r'\[(\d+:\d+:\d+)\s*-\s*(\d+:\d+:\d+)\](.+)', line)

        if time_match:
            if current_section:
                sections.append({
                    'content': '\n'.join(current_section),
                    'has_timestamp': False
                })
                current_section = []

            start_time = time_match.group(1)
            end_time = time_match.group(2)
            description = time_match.group(3).strip()

            section_num = len([s for s in sections if s.get('has_timestamp')]) + len([s for s in sections if not s.get('has_timestamp')]) + 1

            sections.append({
                'has_timestamp': True,
                'start_time': start_time,
                'end_time': end_time,
                'description': description,
                'time_range': f"{start_time} - {end_time}",
                'section_num': section_num,
                'media_file': f"media/{section_num:02d}_{int(start_time.split(':')[0])*360 + int(start_time.split(':')[1])*60 + int(start_time.split(':')[2])}s.gif"
            })
        elif line.strip():
            current_section.append(line)

    if current_section:
        sections.append({
            'content': '\n'.join(current_section),
            'has_timestamp': False
        })

    # 生成微信专用HTML
    wechat_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system-font, "Helvetica Neue", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            line-height: 1.8;
            max-width: 677px;
            margin: 0 auto;
            padding: 20px 16px;
            color: #3f3f3f;
            background: #fff;
        }}
        .title {{
            font-size: 22px;
            font-weight: bold;
            color: #000;
            text-align: center;
            margin-bottom: 30px;
            line-height: 1.4;
        }}
        .section-title {{
            font-size: 18px;
            font-weight: bold;
            color: #000;
            margin-top: 30px;
            margin-bottom: 15px;
            padding-left: 12px;
            border-left: 4px solid #07c160;
        }}
        .time-badge {{
            display: inline-block;
            background: #f0f0f0;
            color: #576b95;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 14px;
            margin-bottom: 10px;
            font-weight: 500;
        }}
        .media-placeholder {{
            margin: 20px 0;
            text-align: center;
            background: #f8f8f8;
            padding: 20px;
            border-radius: 8px;
            border: 2px dashed #ccc;
        }}
        .media-placeholder img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 0 auto;
        }}
        .media-caption {{
            margin-top: 12px;
            font-size: 14px;
            color: #888;
            text-align: center;
            line-height: 1.6;
        }}
        p {{
            font-size: 16px;
            margin: 15px 0;
            text-align: justify;
            text-indent: 2em;
        }}
        .intro {{
            background: #f7f7f7;
            padding: 15px;
            border-radius: 6px;
            margin: 20px 0;
            text-indent: 0;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e7e7e7;
            text-align: center;
            font-size: 14px;
            color: #888;
        }}
    </style>
</head>
<body>
    <div class="title">{title}</div>

"""

    section_index = 0
    for section in sections:
        section_index += 1

        if section['has_timestamp']:
            # 有时间戳的段落
            media_file = section['media_file']
            media_path = media_dir / Path(media_file).name

            # 检查文件是否存在
            has_media = media_path.exists()

            wechat_html += f"""
    <div class="time-badge">{section['time_range']}</div>
"""

            if has_media:
                file_size = media_path.stat().st_size / 1024
                wechat_html += f"""
    <div class="media-placeholder">
        <img src="{media_file}" alt="{section['description']}">
        <div class="media-caption">{section['description']}</div>
    </div>
"""
            else:
                wechat_html += f"""
    <div class="media-placeholder">
        <div style="color: #999;">📺 图片位置</div>
        <div class="media-caption">{section['description']}</div>
    </div>
"""

            content = section.get('content', '')
            if content.strip():
                wechat_html += f"    <p>{content}</p>\n"

        else:
            # 普通段落
            content = section.get('content', '')
            if content.strip():
                if section_index == 1:
                    # 第一段作为引言
                    wechat_html += f'    <div class="intro">{content}</div>\n\n'
                elif content.startswith('##') or content.startswith('#'):
                    # 标题
                    title_text = content.lstrip('#').strip()
                    wechat_html += f'    <div class="section-title">{title_text}</div>\n\n'
                elif len(content) < 100 and ('：' in content or ':' in content):
                    # 可能是小标题
                    wechat_html += f'    <div class="section-title">{content}</div>\n\n'
                else:
                    wechat_html += f'    <p>{content}</p>\n\n'

    wechat_html += """
    <div class="footer">
        <p>点击"在看"分享给更多摩友</p>
    </div>
</body>
</html>
"""

    # 保存微信版本
    output_path = Path("output/articles/Mikuni_HSR42/微信公众号版本.html")
    output_path.write_text(wechat_html, encoding='utf-8')

    logger.success(f"✓ 微信版本已生成: {output_path}")

    # 同时生成纯文本说明
    instructions = f"""
# 微信公众号发布指南

## 文件位置
HTML文件: output/articles/Mikuni_HSR42/微信公众号版本.html
图片文件夹: output/articles/Mikuni_HSR42/media/

## 方法一：使用第三方编辑器（推荐）

### 步骤：
1. 下载并安装微信公众号编辑器：
   - **135编辑器**: https://www.135editor.com/
   - **秀米**: https://xiumi.us/
   - **i排版**: https://ipaiban.com/

2. 打开编辑器，导入HTML文件或直接复制内容

3. 上传图片到编辑器

4. 一键同步到微信公众号

## 方法二：手动复制粘贴

### 步骤：

1. **准备阶段**
   - 打开浏览器访问：https://mp.weixin.qq.com/
   - 登录并进入"图文编辑"

2. **上传图片（重要！）**
   - 点击编辑器工具栏的"图片"图标
   - 将以下图片依次上传：
   """

    # 添加图片列表
    for i, section in enumerate(sections):
        if section.get('has_timestamp'):
            media_file = section['media_file']
            media_path = media_dir / Path(media_file).name
            if media_path.exists():
                file_size = media_path.stat().st_size / 1024 / 1024
                instructions += f"\n   - 图片{i+1}: {media_file} ({file_size:.1f} MB) - {section['description'][:30]}...\n"

    instructions += f"""
   - 上传后，微信会为每个图片生成一个ID（如：img.png）

3. **复制文字内容**
   - 用浏览器打开: {output_path.absolute()}
   - 选择所有文字（Ctrl+A）
   - 复制（Ctrl+C）

4. **粘贴到微信编辑器**
   - 在微信编辑器中粘贴（Ctrl+V）
   - 文字和基础格式会保留

5. **插入图片**
   - 将光标移动到对应位置
   - 点击"图片"图标
   - 选择已上传的图片
   - 调整图片大小（建议宽度100%）

## 方法三：使用浏览器开发者工具（高级）

### 步骤：

1. **在浏览器中打开HTML文件**
   - 双击打开: {output_path.absolute()}

2. **打开开发者工具**
   - 按 F12
   - 点击"Elements"（元素）标签

3. **复制body内容**
   - 找到 `<body>` 标签
   - 右键点击 → Copy → Copy outerHTML

4. **粘贴到微信编辑器**
   - 使用微信编辑器的"源码模式"（如果有）
   - 或者直接粘贴

## 注意事项：

1. **图片上传限制**
   - 微信公众号图片大小限制：≤ 2MB
   - 你的GIF文件都超过2MB，需要：
     * 方案A: 压缩GIF文件
     * 方案B: 转换为MP4视频（微信支持）
     * 方案C: 使用外链（需要微信白名单）

2. **样式兼容性**
   - 微信编辑器会过滤某些CSS样式
   - 建议使用微信支持的样式

3. **预览**
   - 发布前务必使用"预览"功能
   - 在手机上检查效果

## 推荐方案：

由于你的GIF文件都超过2MB（微信限制），建议：

### 方案A：压缩GIF
   - 使用在线工具：https://ezgif.com/optimize
   - 或使用软件：FileOptimizer

### 方案B：转换为视频（推荐）
   - GIF转MP4后可上传到微信视频号
   - 然后在文章中插入视频

需要我帮你：
1. 压缩GIF到2MB以下？
2. 转换GIF为MP4视频？
3. 创建微信上传专用的图片包？

请告诉我你的选择！
"""

    instructions_path = Path("output/articles/Mikuni_HSR42/微信发布指南.md")
    instructions_path.write_text(instructions, encoding='utf-8')

    logger.success(f"✓ 发布指南已生成: {instructions_path}")

    print("\n" + "=" * 70)
    print("微信公众号发布指南")
    print("=" * 70)
    print("\n⚠️  重要提示：")
    print("\n你的GIF文件都超过了微信的2MB限制！")
    print("文件大小：6-7 MB/个，微信限制：≤2 MB")
    print("\n推荐解决方案：")
    print("\n1. 【推荐】转换为MP4视频 - 微信支持视频，没有大小限制")
    print("2. 压缩GIF文件 - 降低质量和尺寸到2MB以下")
    print("3. 使用静态图片 - 将GIF改为JPG截图")
    print("\n详细的发布指南已保存到：")
    print(f"  {instructions_path.absolute()}")
    print("\n需要我帮你转换文件格式吗？")

if __name__ == "__main__":
    create_wechat_html()
