"""完整文章生成器 - 处理所有时间戳并合成文章"""
import sys
from pathlib import Path
import re
import json

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

# 设置UTF-8输出
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from loguru import logger
from src.media_processor import MediaProcessor
from datetime import datetime

# 配置日志
logger.remove()
logger.add(
    sink=lambda msg: print(msg, end=""),
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO",
    colorize=False
)

def parse_full_report(report_path: str) -> dict:
    """完整解析报告，保留所有内容"""
    logger.info(f"解析报告: {report_path}")

    with open(report_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 提取标题
    title = lines[0].strip()

    # 解析所有技术段和时间戳
    sections = []
    current_section = []

    for line in lines[1:]:
        line = line.rstrip()
        time_match = re.match(r'\[(\d+:\d+:\d+)\s*-\s*(\d+:\d+:\d+)\](.+)', line)

        if time_match:
            # 保存上一个section
            if current_section:
                sections.append({
                    'content': '\n'.join(current_section),
                    'has_timestamp': False
                })
                current_section = []

            # 提取时间戳信息
            start_time = time_match.group(1)
            end_time = time_match.group(2)
            description = time_match.group(3).strip()

            # 转换为秒数
            parts = start_time.split(':')
            seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])

            sections.append({
                'has_timestamp': True,
                'start_time': start_time,
                'end_time': end_time,
                'seconds': seconds,
                'description': description,
                'time_range': f"{start_time} - {end_time}"
            })
        elif line.strip():
            current_section.append(line)

    # 保存最后一个section
    if current_section:
        sections.append({
            'content': '\n'.join(current_section),
            'has_timestamp': False
        })

    # 统计
    timestamp_count = sum(1 for s in sections if s['has_timestamp'])

    logger.success(f"✓ 解析完成: {len(sections)} 个段落, {timestamp_count} 个时间戳")

    return {
        'title': title,
        'sections': sections
    }

def generate_all_media(video_path: str, sections: list, output_dir: Path) -> list:
    """为所有时间戳生成媒体文件"""
    logger.info("\n" + "=" * 70)
    logger.info("生成媒体文件")
    logger.info("=" * 70)

    processor = MediaProcessor()
    media_files = {}

    for i, section in enumerate(sections, 1):
        if not section['has_timestamp']:
            continue

        timestamp = section['seconds']
        time_range = section['time_range']

        logger.info(f"\n[{i}] {time_range}")

        # 偶数生成 GIF，奇数生成截图
        if i % 2 == 0:
            # 生成 GIF
            filename = f"{i:02d}_{timestamp}s.gif"
            output_path = str(output_dir / filename)
            try:
                temp_file = processor.generate_gif(
                    video_path=video_path,
                    start_time=timestamp,
                    duration=10,  # 10秒GIF
                    output_path=str(output_dir / f"temp_{filename}")
                )

                # 添加水印
                watermarked = processor.add_watermark(
                    media_path=temp_file,
                    output_path=output_path
                )

                # 删除临时文件
                Path(temp_file).unlink(missing_ok=True)

                media_files[i] = {
                    'path': output_path,
                    'type': 'gif',
                    'filename': filename
                }
                logger.success(f"  ✓ GIF: {filename}")

            except Exception as e:
                logger.error(f"  ✗ GIF 失败: {e}")
        else:
            # 生成截图
            filename = f"{i:02d}_{timestamp}s.jpg"
            output_path = str(output_dir / filename)
            try:
                temp_file = processor.extract_screenshot(
                    video_path=video_path,
                    timestamp=timestamp,
                    output_path=str(output_dir / f"temp_{filename}")
                )

                # 添加水印
                watermarked = processor.add_watermark(
                    media_path=temp_file,
                    output_path=output_path
                )

                # 删除临时文件
                Path(temp_file).unlink(missing_ok=True)

                media_files[i] = {
                    'path': output_path,
                    'type': 'image',
                    'filename': filename
                }
                logger.success(f"  ✓ 截图: {filename}")

            except Exception as e:
                logger.error(f"  ✗ 截图失败: {e}")

    logger.success(f"\n✓ 媒体生成完成: {len(media_files)} 个文件")
    return media_files

def generate_html_article(report_data: dict, media_files: dict, output_path: str):
    """生成 HTML 格式文章"""
    logger.info("\n生成 HTML 文章...")

    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report_data['title']}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.8;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
            background: #fff;
        }}
        h1 {{
            color: #1a1a1a;
            border-bottom: 3px solid #007bff;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #2c3e50;
            margin-top: 40px;
            padding-left: 15px;
            border-left: 4px solid #007bff;
        }}
        .time-range {{
            color: #007bff;
            font-weight: bold;
            font-size: 0.9em;
            background: #f0f8ff;
            padding: 3px 8px;
            border-radius: 4px;
            margin-right: 10px;
        }}
        .media-container {{
            margin: 20px 0;
            text-align: center;
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
        }}
        .media-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .media-caption {{
            margin-top: 10px;
            font-size: 0.9em;
            color: #666;
            font-style: italic;
        }}
        p {{
            margin: 15px 0;
            text-align: justify;
        }}
        .footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #999;
            font-size: 0.9em;
            text-align: center;
        }}
    </style>
</head>
<body>
    <h1>{report_data['title']}</h1>

"""

    section_index = 0
    for section in report_data['sections']:
        section_index += 1

        if section['has_timestamp']:
            # 有时间戳的段落
            media = media_files.get(section_index)

            if media:
                file_size = Path(media['path']).stat().st_size / 1024
                # 使用 media/ 前缀
                img_src = f"media/{media['filename']}"
                if media['type'] == 'gif':
                    html_content += f"""
    <h2><span class="time-range">{section['time_range']}</span></h2>
    <div class="media-container">
        <img src="{img_src}" alt="{section['description']}">
        <div class="media-caption">{section['description']}</div>
    </div>
    <p>{section.get('content', '')}</p>
"""
                else:
                    html_content += f"""
    <h2><span class="time-range">{section['time_range']}</span></h2>
    <div class="media-container">
        <img src="{img_src}" alt="{section['description']}">
        <div class="media-caption">{section['description']}</div>
    </div>
    <p>{section.get('content', '')}</p>
"""
            else:
                html_content += f"""
    <h2><span class="time-range">{section['time_range']}</span></h2>
    <p>{section['description']}</p>
    <p>{section.get('content', '')}</p>
"""
        else:
            # 普通段落
            content = section.get('content', '')
            if content.strip():
                # 检测是否是标题
                if content.startswith('##') or content.startswith('#'):
                    # 这是一个标题
                    html_content += f"    <h2>{content.lstrip('#').strip()}</h2>\n"
                elif len(content) < 100 and '：' in content or ':' in content:
                    # 可能是小标题
                    html_content += f"    <h3>{content}</h3>\n"
                else:
                    html_content += f"    <p>{content}</p>\n"

    html_content += f"""
    <div class="footer">
        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>由 MotoStep 自动生成</p>
    </div>
</body>
</html>
"""

    # 保存文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    logger.success(f"✓ HTML 文章已保存: {output_path}")
    return output_path

def generate_markdown_article(report_data: dict, media_files: dict, output_path: str, enhanced: bool = True):
    """
    生成 Markdown 格式文章

    Args:
        report_data: 报告数据
        media_files: 媒体文件字典
        output_path: 输出路径
        enhanced: 是否使用增强格式（NeuraPress优化）
    """
    logger.info("生成 Markdown 文章...")

    if enhanced:
        # 增强格式 - 优化为 NeuraPress 兼容
        md_content = f"""# {report_data['title']}

**来源**: CV Carburetor VS Mikuni flat slide
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

"""
    else:
        # 基础格式
        md_content = f"""# {report_data['title']}

"""

    section_index = 0
    for section in report_data['sections']:
        section_index += 1

        if section['has_timestamp']:
            # 有时间戳的段落
            media = media_files.get(section_index)

            if enhanced:
                # 增强格式：使用时间范围作为元数据
                md_content += f"""## {section_index}. {section['description'][:30]}...

**时间范围**: {section['time_range']}

"""
            else:
                md_content += f"\n## {section['time_range']}\n\n"

            if media:
                file_size = Path(media['path']).stat().st_size / 1024
                # 使用 media/ 前缀
                img_src = f"media/{media['filename']}"

                if enhanced:
                    # 增强格式：更好的图片引用
                    media_label = "动图" if media['type'] == 'gif' else "图片"
                    md_content += f"""![{section['description']}]({img_src})

*{media_label}: {section['description']} ({file_size:.0f} KB)*

"""
                else:
                    md_content += f"""![{section['description']}]({img_src})

*图: {section['description']} ({file_size:.0f} KB)*

"""

            # 添加内容
            content = section.get('content', '')
            if content.strip():
                if enhanced:
                    # 增强格式：添加空行分隔
                    md_content += f"{content}\n\n"
                else:
                    md_content += f"{content}\n\n"

            if enhanced:
                # 增强格式：添加分隔线
                md_content += "---\n\n"

        else:
            # 普通段落
            content = section.get('content', '')
            if content.strip():
                if enhanced:
                    # 检测是否是标题
                    if content.startswith('##') or content.startswith('#'):
                        # 这是一个标题
                        title_text = content.lstrip('#').strip()
                        md_content += f"## {title_text}\n\n"
                    elif len(content) < 100 and ('：' in content or ':' in content):
                        # 可能是小标题或引用
                        if content.startswith('"') or content.startswith('"'):
                            # 引用文本
                            md_content += f"> {content}\n\n"
                        else:
                            md_content += f"{content}\n\n"
                    else:
                        md_content += f"{content}\n\n"
                else:
                    md_content += f"{content}\n\n"

    # 添加页脚
    if enhanced:
        md_content += f"""
---

*由 MotoStep 自动生成 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    else:
        md_content += f"""
---

*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*由 MotoStep 自动生成*
"""

    # 保存文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

    logger.success(f"✓ Markdown 文章已保存: {output_path}")
    return output_path

def generate_plain_text_article(report_data: dict, media_files: dict, output_path: str):
    """
    生成纯文本格式文章（无格式，适用于任何平台）

    Args:
        report_data: 报告数据
        media_files: 媒体文件字典
        output_path: 输出路径
    """
    logger.info("生成纯文本文章...")

    # 标题和元数据
    lines = []
    lines.append(report_data['title'])
    lines.append("")
    lines.append(f"来源: CV Carburetor VS Mikuni flat slide")
    lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")

    section_index = 0
    for section in report_data['sections']:
        section_index += 1

        if section['has_timestamp']:
            # 有时间戳的段落
            media = media_files.get(section_index)

            # 使用描述的前30个字符作为小标题
            short_desc = section['description'][:40]
            lines.append(f"{section_index}. {short_desc}")
            lines.append("")
            lines.append(f"时间范围: {section['time_range']}")
            lines.append("")

            if media:
                file_size = Path(media['path']).stat().st_size / 1024
                media_type = "动图" if media['type'] == 'gif' else "图片"
                lines.append(f"[{media_type}: {section['description']}]")
                lines.append("")

            # 添加内容
            content = section.get('content', '')
            if content.strip():
                lines.append(content)
                lines.append("")

            lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            lines.append("")

        else:
            # 普通段落
            content = section.get('content', '')
            if content.strip():
                # 检测是否是标题
                if content.startswith('##') or content.startswith('#'):
                    # 这是一个标题
                    title_text = content.lstrip('#').strip()
                    lines.append(f"【{title_text}】")
                    lines.append("")
                elif len(content) < 100 and ('：' in content or ':' in content):
                    # 可能是小标题
                    lines.append(content)
                    lines.append("")
                else:
                    lines.append(content)
                    lines.append("")

    # 添加页脚
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append("内容由 MotoStep 自动生成")
    lines.append(f"来源视频: CV Carburetor VS Mikuni flat slide")

    rendered_content = "\n".join(lines)

    # 保存文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(rendered_content)

    logger.success(f"✓ 纯文本文章已保存: {output_path}")
    return output_path

def main():
    # 文件路径
    video_path = r"C:\0_life\moto\youtube 搬运\done\CV Carburetor VS Mikuni flat slide - ep34 - Roma Custom Bike_Video_Export\CV Carburetor VS Mikuni flat slide - ep34 - Roma Custom Bike.mp4"
    report_path = r"C:\Users\dbaa\Desktop\MotoStep\report_source\Mikuni HSR 42 真的值那 300 美金吗.txt"

    # 输出目录
    output_base = Path("./output/articles/Mikuni_HSR42")
    output_base.mkdir(parents=True, exist_ok=True)

    media_dir = output_base / "media"
    media_dir.mkdir(exist_ok=True)

    logger.info("=" * 70)
    logger.info("MotoStep - 完整文章生成")
    logger.info("=" * 70)

    # ========== 阶段1: 解析报告 ==========
    logger.info("\n阶段1: 解析报告")
    logger.info("=" * 70)

    report_data = parse_full_report(report_path)

    # ========== 阶段2: 生成媒体 ==========
    logger.info("\n阶段2: 生成媒体文件")
    logger.info("=" * 70)
    logger.warning("这可能需要几分钟...")

    media_files = generate_all_media(video_path, report_data['sections'], media_dir)

    # ========== 阶段3: 生成文章 ==========
    logger.info("\n阶段3: 生成文章")
    logger.info("=" * 70)

    generated_files = {}

    # 1. 生成 HTML (Web 版本)
    logger.info("\n1. 生成 HTML 文章 (Web 版本)...")
    html_path = output_base / f"{report_data['title']}.html"
    generate_html_article(report_data, media_files, str(html_path))
    generated_files['html'] = html_path

    # 2. 生成 Markdown (NeuraPress 优化版)
    logger.info("\n2. 生成 Markdown 文章 (NeuraPress 优化版)...")
    md_path = output_base / f"{report_data['title']}.md"
    generate_markdown_article(report_data, media_files, str(md_path), enhanced=True)
    generated_files['markdown'] = md_path

    # 3. 生成纯文本 (通用版本)
    logger.info("\n3. 生成纯文本文章 (通用版本)...")
    txt_path = output_base / f"{report_data['title']}.txt"
    generate_plain_text_article(report_data, media_files, str(txt_path))
    generated_files['text'] = txt_path

    # ========== 完成 ==========
    logger.info("\n" + "=" * 70)
    logger.success("✓ 全部完成！")
    logger.info("=" * 70)

    logger.info(f"\n输出目录: {output_base}")
    logger.info(f"\n生成的文件:")
    logger.info(f"  - HTML 文章: {html_path.name}")
    logger.info(f"  - Markdown 文章 (NeuraPress 优化): {md_path.name}")
    logger.info(f"  - 纯文本文章: {txt_path.name}")
    logger.info(f"  - 媒体文件: {len(media_files)} 个 (media/ 目录)")

    logger.info("\n" + "=" * 70)
    logger.info("格式说明:")
    logger.info("=" * 70)
    logger.info("\n1. HTML 文章:")
    logger.info("   - 用途: 直接在浏览器打开或复制到微信公众号")
    logger.info("   - 特点: 包含完整样式，支持图片和GIF")

    logger.info("\n2. Markdown 文章 (NeuraPress 优化):")
    logger.info("   - 用途: 导入 NeuraPress 进行专业排版")
    logger.info("   - 特点: 结构清晰，支持标题层级和元数据")
    logger.info("   - 使用方式:")
    logger.info("     a) 安装 NeuraPress: npm install -g neurapress")
    logger.info("     b) 启动服务: neurapress dev")
    logger.info("     c) 浏览器打开: http://localhost:3000")
    logger.info("     d) 导入此 Markdown 文件")
    logger.info("     e) 应用微信主题")
    logger.info("     f) 复制到微信公众号")

    logger.info("\n3. 纯文本文章:")
    logger.info("   - 用途: 复制到任何平台（无格式要求）")
    logger.info("   - 特点: 通用性强，无 markdown 语法")
    logger.info("   - 媒体文件使用占位符，需要手动插入")

    logger.info(f"\n{'=' * 70}")

    # 显示媒体文件列表
    logger.info(f"\n媒体文件列表:")
    for idx, media in media_files.items():
        size = Path(media['path']).stat().st_size / 1024
        logger.info(f"  {idx:02d}. {media['filename']} ({size:.0f} KB)")

if __name__ == "__main__":
    main()
