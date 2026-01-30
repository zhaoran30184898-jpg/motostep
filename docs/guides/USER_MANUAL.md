# MotoStep 产品使用手册

**版本**: v0.1.0-alpha
**更新日期**: 2026-01-30
**产品官网**: https://github.com/zhaoran30184898-jpg/motostep

---

## 目录

1. [产品介绍](#1-产品介绍)
2. [系统要求](#2-系统要求)
3. [安装部署](#3-安装部署)
4. [配置说明](#4-配置说明)
5. [快速开始](#5-快速开始)
6. [使用指南](#6-使用指南)
7. [工作流程详解](#7-工作流程详解)
8. [高级功能](#8-高级功能)
9. [API参考](#9-api参考)
10. [常见问题](#10-常见问题)
11. [故障排除](#11-故障排除)
12. [附录](#12-附录)

---

## 1. 产品介绍

### 1.1 什么是 MotoStep？

MotoStep 是一个全自动化的内容生产流水线系统，专门用于将 YouTube 越野摩托教学视频转化为符合微信公众号规范的技术教学文章，并支持自动推送到草稿箱。

### 1.2 核心功能

| 功能模块 | 说明 | 状态 |
|---------|------|------|
| **视频自动下载** | 支持 YouTube 视频下载（720p/1080p），自动处理字幕 | ✅ 已完成 |
| **AI内容分析** | 集成 NotebookLM 进行深度视频内容分析 | ✅ 已完成 |
| **关键场景提取** | 自动识别并提取关键技术时间戳 | ✅ 已完成 |
| **媒体资产生成** | 高质量 JPG 截图 + GIF 动图自动生成 | ✅ 已完成 |
| **批量水印添加** | 自动为所有媒体添加版权水印 | ✅ 已完成 |
| **微信发布集成** | 一键发布到微信公众号草稿箱 | 🚧 开发中 |

### 1.3 应用场景

- **教学博主**: 快速将视频教程转化为图文教程
- **自媒体运营**: 批量处理视频内容，提高内容生产效率
- **技术文档**: 创建带演示动图的技术文档
- **知识管理**: 将视频内容整理为可搜索的文字资料

### 1.4 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                    MotoStep 系统架构                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   视频源     │───▶│  视频下载    │───▶│  字幕提取    │  │
│  │  (YouTube)  │    │  (yt-dlp)   │    │  (srt/vtt)  │  │
│  └─────────────┘    └─────────────┘    └─────────────┘  │
│                                               │          │
│                                               ▼          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │  微信发布    │◀───│  内容合成    │◀───│  AI内容分析  │  │
│  │ (草稿箱)     │    │  (Jinja2)   │    │ (NotebookLM)│  │
│  └─────────────┘    └─────────────┘    └─────────────┘  │
│                            ▲                             │
│                            │                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │  最终输出    │    │  媒体处理    │    │  原始视频    │  │
│  │ (HTML/MD)   │    │  (FFmpeg)   │    │   (.mp4)    │  │
│  └─────────────┘    └─────────────┘    └─────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 2. 系统要求

### 2.1 硬件要求

| 组件 | 最低配置 | 推荐配置 |
|------|---------|---------|
| CPU | 双核 2.0GHz | 四核 3.0GHz+ |
| 内存 | 4 GB | 8 GB+ |
| 硬盘 | 10 GB 可用空间 | 50 GB+ SSD |
| 网络 | 稳定的互联网连接 | 高速宽带 |

### 2.2 软件要求

| 软件 | 版本要求 | 必需/可选 |
|------|---------|----------|
| Python | 3.10+ | **必需** |
| FFmpeg | 4.0+ | **必需** |
| Git | 任意版本 | 推荐 |

### 2.3 操作系统

- ✅ Windows 10/11
- ✅ macOS 10.15+
- ✅ Linux (Ubuntu 20.04+, Debian 11+, CentOS 8+)

---

## 3. 安装部署

### 3.1 方式一：从 GitHub 克隆

```bash
# 1. 克隆项目
git clone https://github.com/zhaoran30184898-jpg/motostep.git
cd motostep

# 2. 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt
```

### 3.2 安装 FFmpeg

**Windows:**
```bash
# 使用 Chocolatey
choco install ffmpeg

# 或从官网下载
# https://ffmpeg.org/download.html
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

**验证安装:**
```bash
ffmpeg -version
```

### 3.3 配置环境变量

```bash
# 1. 复制环境变量模板
cp .env.example .env

# 2. 编辑 .env 文件
# Windows: notepad .env
# macOS/Linux: nano .env
```

### 3.4 目录结构说明

```
motostep/
├── .env                      # 环境配置文件（需创建）
├── .env.example              # 环境变量模板
├── config.py                 # 配置管理模块
├── requirements.txt          # Python依赖
├── src/                      # 源代码目录
│   ├── video_fetcher/        # 视频获取模块
│   ├── content_analyzer/     # 内容分析模块
│   ├── media_processor/      # 媒体处理模块
│   ├── content_composer/     # 内容合成模块
│   ├── wechat_publisher/     # 微信发布模块
│   └── models/               # 数据模型
├── output/                   # 输出目录（自动创建）
│   ├── videos/               # 下载的视频
│   ├── subtitles/            # 提取的字幕
│   ├── reports/              # AI分析报告
│   ├── images/               # 生成的媒体文件
│   ├── analysis/             # 分析结果JSON
│   └── articles/             # 生成的文章
├── temp/                     # 临时文件
└── logs/                     # 日志文件
```

---

## 4. 配置说明

### 4.1 环境变量配置 (.env)

```bash
# ===== 微信公众号配置 =====
WECHAT_APP_ID=your_app_id_here
WECHAT_APP_SECRET=your_app_secret_here

# ===== 视频下载配置 =====
VIDEO_QUALITY=720p                    # 视频质量: 720p/1080p
VIDEO_COOKIES_PATH=./cookies.txt      # YouTube cookies文件路径

# ===== 媒体生成配置 =====
SCREENSHOT_QUALITY=2                  # 截图质量 (1-5, 越大质量越高)
GIF_WIDTH=480                         # GIF宽度 (像素)
GIF_FPS=10                            # GIF帧率
GIF_USE_PALETTE=true                  # 使用调色板优化GIF大小
WATERMARK_TEXT=FreeSoloDirtbike       # 水印文字

# ===== 内容生成配置 =====
ARTICLE_MIN_LENGTH=5000               # 文章最小字数
ARTICLE_MAX_LENGTH=10000              # 文章最大字数
TARGET_LANGUAGE=zh-CN                 # 目标语言

# ===== 存储配置 =====
OUTPUT_DIR=./output                   # 输出目录
TEMP_DIR=./temp                       # 临时目录
LOG_DIR=./logs                        # 日志目录

# ===== Web服务配置 =====
FLASK_HOST=127.0.0.1                  # Web服务地址
FLASK_PORT=5000                       # Web服务端口
FLASK_DEBUG=true                      # 调试模式

# ===== 应用配置 =====
APP_ENV=development                   # 环境: development/production
APP_LOG_LEVEL=INFO                    # 日志级别
APP_TIMEZONE=Asia/Shanghai            # 时区

# ===== 重试配置 =====
HTTP_MAX_RETRIES=3                    # HTTP重试次数
HTTP_RETRY_DELAY=1                    # 重试延迟(秒)
```

### 4.2 获取微信公众号配置

1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 进入"开发" → "基本配置"
3. 获取 AppID 和 AppSecret
4. 将其填入 `.env` 文件

### 4.3 YouTube Cookies（可选）

某些 YouTube 视频可能需要登录才能访问，此时需要提供 cookies：

```bash
# 使用浏览器扩展导出 cookies
# 推荐: "Get cookies.txt LOCALLY" 扩展

# 1. 安装浏览器扩展
# 2. 访问 YouTube 并登录
# 3. 点击扩展图标，导出 cookies.txt
# 4. 保存到项目根目录
```

---

## 5. 快速开始

### 5.1 五分钟快速体验

```bash
# 1. 确保已安装所有依赖
pip install -r requirements.txt

# 2. 运行端到端测试
python test_end_to_end.py

# 测试会自动：
# - 下载示例视频
# - 生成媒体文件
# - 创建文章（3种格式）
```

### 5.2 处理第一个视频

```python
# 创建你的第一个处理脚本
from pathlib import Path
from src.video_fetcher import VideoFetcher
from src.content_analyzer import ContentAnalyzer
from src.media_processor import MediaProcessor
from src.content_composer import ContentComposer

# 1. 下载视频
fetcher = VideoFetcher()
video_info = fetcher.download_video(
    url="https://www.youtube.com/watch?v=YOUR_VIDEO_ID"
)

# 2. 分析内容（需要先准备 NotebookLM 报告）
analyzer = ContentAnalyzer()
analysis = analyzer.analyze_from_report(
    report_path="./output/reports/YOUR_VIDEO_ID_report.txt",
    subtitle_path="./output/subtitles/YOUR_VIDEO_ID.zh-CN.srt"
)

# 3. 生成媒体文件
processor = MediaProcessor()
assets = processor.generate_assets(
    video_path=video_info['video_path'],
    analysis=analysis
)

# 4. 合成文章
composer = ContentComposer()
article = composer.compose(
    analysis=analysis,
    assets=assets,
    output_dir="./output/articles"
)
```

### 5.3 使用测试脚本

项目提供了多个测试脚本供快速体验：

| 测试脚本 | 功能 | 运行命令 |
|---------|------|---------|
| `test_video_fetcher.py` | 测试视频下载 | `python test_video_fetcher.py` |
| `test_media_processor.py` | 测试媒体生成 | `python test_media_processor.py` |
| `test_content_analyzer.py` | 测试内容分析 | `python test_content_analyzer.py` |
| `test_content_composer.py` | 测试文章生成 | `python test_content_composer.py` |
| `test_end_to_end.py` | 完整流程测试 | `python test_end_to_end.py` |

---

## 6. 使用指南

### 6.1 准备 NotebookLM 报告

MotoStep 使用 NotebookLM 进行 AI 内容分析，需要手动准备分析报告：

#### 步骤 1: 上传视频到 NotebookLM

1. 访问 [https://notebooklm.google.com/](https://notebooklm.google.com/)
2. 创建新的 Notebook
3. 添加 YouTube 视频链接作为源

#### 步骤 2: 生成分析报告

在 NotebookLM 中请求生成以下内容：

```
请分析这个视频，并提供：
1. 视频摘要
2. 关键技术点列表（每个技术点需要中英文名称）
3. 关键时刻时间戳列表（格式：分:秒 - 描述）
4. 每个技术点的详细说明
```

#### 步骤 3: 导出报告

1. 复制 NotebookLM 生成的报告
2. 保存为文本文件：`./output/reports/{VIDEO_ID}_report.txt`

**报告格式示例：**

```markdown
# Pro Motocross Techniques with Luke Fauser

## Summary
This comprehensive motocross tutorial covers essential riding techniques...

## Key Techniques

- **Body Positioning**: Proper body positioning is crucial...
- **Braking Techniques**: Master the art of braking...
- **Cornering Skills**: Enter corners wide, apex at the inside point...

## Key Moments

- **0:30** - Instructor demonstrates proper body positioning on the bike
- **1:45** - Front and rear brake technique demonstration
- **3:20** - Cornering line and body lean explanation
```

### 6.2 命令行使用

```bash
# 下载单个视频
python -c "
from src.video_fetcher import VideoFetcher
fetcher = VideoFetcher()
fetcher.download_video('https://www.youtube.com/watch?v=xxx')
"

# 生成媒体文件
python -c "
from src.media_processor import MediaProcessor
from src.content_analyzer import ContentAnalyzer

analyzer = ContentAnalyzer()
analysis = analyzer.analyze_from_report('./output/reports/xxx_report.txt')

processor = MediaProcessor()
processor.generate_assets('./output/videos/xxx.mp4', analysis)
"

# 生成文章
python -c "
from src.content_composer import ContentComposer
composer = ContentComposer()
composer.compose_from_files(
    analysis_path='./output/analysis/xxx_analysis.json',
    images_dir='./output/images',
    output_dir='./output/articles/xxx'
)
"
```

### 6.3 Python API 使用

#### 完整流程示例

```python
from pathlib import Path
from src.video_fetcher import VideoFetcher
from src.content_analyzer import ContentAnalyzer
from src.media_processor import MediaProcessor
from src.content_composer import ContentComposer
from loguru import logger

# 配置日志
logger.add("./logs/motostep_{time}.log", rotation="1 day")

def process_video(video_url: str, report_path: str):
    """完整的视频处理流程"""

    # 1. 下载视频
    logger.info(f"开始处理视频: {video_url}")
    fetcher = VideoFetcher()
    video_info = fetcher.download_video(video_url)
    video_id = video_info['video_id']

    # 2. 分析内容
    logger.info("分析视频内容...")
    analyzer = ContentAnalyzer()

    # 查找字幕文件
    subtitle_path = Path(f"./output/subtitles/{video_id}.zh-CN.srt")

    analysis = analyzer.analyze_from_report(
        report_path=report_path,
        subtitle_path=str(subtitle_path) if subtitle_path.exists() else None
    )

    # 保存分析结果
    analysis_path = f"./output/analysis/{video_id}_analysis.json"
    analyzer.save_analysis(analysis, analysis_path)

    # 3. 生成媒体文件
    logger.info("生成媒体文件...")
    processor = MediaProcessor()
    assets = processor.generate_assets(
        video_path=video_info['video_path'],
        analysis=analysis
    )

    # 4. 合成文章
    logger.info("合成文章...")
    composer = ContentComposer()
    article = composer.compose(
        analysis=analysis,
        assets=assets,
        output_dir=f"./output/articles/{video_id}"
    )

    logger.success(f"处理完成！文章保存在: ./output/articles/{video_id}")
    return article

# 使用
if __name__ == "__main__":
    article = process_video(
        video_url="https://www.youtube.com/watch?v=oPFg4VkIVIY",
        report_path="./output/reports/oPFg4VkIVIY_report.txt"
    )
```

### 6.4 批量处理

```python
from pathlib import Path
import json

def batch_process(url_file: str, report_dir: str):
    """批量处理多个视频"""

    # 读取URL列表
    with open(url_file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]

    # 处理每个视频
    for url in urls:
        try:
            # 提取视频ID
            video_id = url.split('v=')[-1].split('&')[0]

            # 查找对应的报告文件
            report_path = Path(report_dir) / f"{video_id}_report.txt"

            if not report_path.exists():
                logger.warning(f"报告不存在，跳过: {video_id}")
                continue

            # 处理视频
            process_video(url, str(report_path))

        except Exception as e:
            logger.error(f"处理失败: {url}, 错误: {e}")
            continue

# 使用
batch_process(
    url_file="./video_urls.txt",
    report_dir="./output/reports"
)
```

---

## 7. 工作流程详解

### 7.1 完整工作流程图

```
┌──────────────────────────────────────────────────────────────────┐
│                        MotoStep 工作流程                           │
└──────────────────────────────────────────────────────────────────┘

   用户输入
   ┌──────────────┐
   │ YouTube URL  │
   └──────┬───────┘
          │
          ▼
   ┌───────────────┐
   │  阶段1: 视频获取  │
   ├───────────────┤
   │ • 下载视频      │
   │ • 提取字幕      │
   │ • 获取元数据    │
   └───────┬───────┘
           │
           ▼
   ┌───────────────┐
   │  阶段2: AI分析  │  ◀── 需要手动准备 NotebookLM 报告
   ├───────────────┤
   │ • 解析报告      │
   │ • 提取技术点    │
   │ • 识别时间戳    │
   └───────┬───────┘
           │
           ▼
   ┌───────────────┐
   │ 阶段3: 媒体处理 │
   ├───────────────┤
   │ • 提取关键帧    │
   │ • 生成GIF      │
   │ • 添加水印      │
   └───────┬───────┘
           │
           ▼
   ┌───────────────┐
   │ 阶段4: 内容合成 │
   ├───────────────┤
   │ • 生成HTML      │
   │ • 生成Markdown  │
   │ • 嵌入媒体      │
   └───────┬───────┘
           │
           ▼
   ┌───────────────┐
   │ 阶段5: 微信发布 │  🚧 开发中
   ├───────────────┤
   │ • 上传媒体      │
   │ • 创建草稿      │
   │ • 推送到公众号  │
   └───────┬───────┘
           │
           ▼
      最终输出
   ┌────────────────┐
   │ • 微信HTML      │
   │ • Markdown文档  │
   │ • HTML报告      │
   └────────────────┘
```

### 7.2 各阶段详细说明

#### 阶段1: 视频获取

**功能**: 从 YouTube 下载视频和字幕

**输入**:
- YouTube URL
- Cookies 文件（可选）

**输出**:
- 视频文件 (MP4)
- 字幕文件 (SRT/VTT)
- 视频元数据

**耗时**: 1-5 分钟（取决于视频大小和网络速度）

**实现**:
```python
from src.video_fetcher import VideoFetcher

fetcher = VideoFetcher()
video_info = fetcher.download_video(
    url="https://www.youtube.com/watch?v=xxx",
    quality="720p",
    cookies_path="./cookies.txt"
)
```

#### 阶段2: 内容分析

**功能**: 解析 AI 报告，提取关键技术点和时间戳

**输入**:
- NotebookLM 报告文本
- 字幕文件（可选）

**输出**:
- 分析结果 JSON
- 技术点列表
- 关键时刻时间戳

**耗时**: < 1 秒

**实现**:
```python
from src.content_analyzer import ContentAnalyzer

analyzer = ContentAnalyzer()
analysis = analyzer.analyze_from_report(
    report_path="./output/reports/xxx_report.txt",
    subtitle_path="./output/subtitles/xxx.srt"  # 可选
)

# 保存分析结果
analyzer.save_analysis(analysis, "./output/analysis/xxx_analysis.json")
```

#### 阶段3: 媒体处理

**功能**: 根据分析结果生成媒体资产

**输入**:
- 视频文件路径
- 分析结果（包含关键时刻）

**输出**:
- 高质量截图 (JPG)
- GIF 动图
- 所有文件均带水印

**耗时**: 30-60 秒（取决于媒体数量）

**实现**:
```python
from src.media_processor import MediaProcessor

processor = MediaProcessor()
assets = processor.generate_assets(
    video_path="./output/videos/xxx.mp4",
    analysis=analysis,
    output_dir="./output/images"
)
```

**配置选项**:
- `screenshot_quality`: 截图质量 (1-5)
- `gif_width`: GIF 宽度（像素）
- `gif_fps`: GIF 帧率
- `watermark_text`: 水印文字

#### 阶段4: 内容合成

**功能**: 将分析结果和媒体合成为最终文章

**输入**:
- 分析结果 JSON
- 媒体文件目录

**输出**:
- 微信公众号 HTML
- Markdown 文档
- HTML 报告

**耗时**: < 1 秒

**实现**:
```python
from src.content_composer import ContentComposer

composer = ContentComposer()
article = composer.compose(
    analysis=analysis,
    assets=assets,
    output_dir="./output/articles/xxx"
)
```

#### 阶段5: 微信发布（开发中）

**功能**: 将文章发布到微信公众号草稿箱

**输入**:
- 文章 HTML
- 微信 AppID 和 AppSecret

**输出**:
- 微信草稿
- 发布成功确认

**实现**（计划）:
```python
from src.wechat_publisher import WeChatPublisher, DraftManager

publisher = WeChatPublisher()
draft_manager = DraftManager(publisher)

result = draft_manager.create_draft(
    title="文章标题",
    content=article['wechat_html'],
    cover_path=article['cover_image']
)
```

---

## 8. 高级功能

### 8.1 自定义媒体生成

```python
from src.media_processor import MediaProcessor
from src.models.video import KeyMoment

# 创建自定义关键时刻
custom_moments = [
    KeyMoment(
        timestamp=30,
        title="自定义场景1",
        description="这个场景的详细说明",
        media_type="image"  # 或 "gif"
    ),
    KeyMoment(
        timestamp=120,
        title="自定义场景2",
        description="另一个场景",
        media_type="gif",
        duration=5  # GIF时长（秒）
    )
]

# 使用自定义时间戳生成媒体
processor = MediaProcessor()
assets = processor.generate_assets(
    video_path="./output/videos/xxx.mp4",
    key_moments=custom_moments,
    output_dir="./output/images"
)
```

### 8.2 自定义文章模板

```python
from src.content_composer import ContentComposer
from pathlib import Path

# 创建自定义模板
custom_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
    <style>
        /* 自定义样式 */
        body { font-family: 'Microsoft YaHei', sans-serif; }
        .tech-point { background: #f0f0f0; padding: 10px; }
    </style>
</head>
<body>
    <h1>{{ title }}</h1>
    <div class="summary">{{ summary }}</div>

    {% for tech in techniques %}
    <div class="tech-point">
        <h2>{{ tech.title }}</h2>
        <p>{{ tech.description }}</p>
        {% if tech.media %}
        <img src="{{ tech.media.path }}" alt="{{ tech.media.title }}">
        {% endif %}
    </div>
    {% endfor %}
</body>
</html>
"""

# 保存自定义模板
template_path = Path("./templates/custom_article.html")
template_path.parent.mkdir(exist_ok=True)
template_path.write_text(custom_template, encoding='utf-8')

# 使用自定义模板
composer = ContentComposer()
article = composer.compose(
    analysis=analysis,
    assets=assets,
    template_path=str(template_path),
    output_dir="./output/articles/custom"
)
```

### 8.3 性能优化

#### 并行媒体生成

```python
from concurrent.futures import ThreadPoolExecutor
from src.media_processor import MediaProcessor

def generate_media_asset(moment):
    """生成单个媒体资产"""
    processor = MediaProcessor()
    return processor.generate_single_asset(
        video_path=video_path,
        moment=moment
    )

# 并行生成多个媒体
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(generate_media_asset, moment)
               for moment in analysis.key_moments]
    assets = [f.result() for f in futures]
```

#### 增量处理

```python
from pathlib import Path
import hashlib

def get_file_hash(filepath):
    """计算文件哈希值"""
    return hashlib.md5(Path(filepath).read_bytes()).hexdigest()

def incremental_process(video_path, report_path):
    """增量处理：只处理有变化的文件"""

    # 检查是否已处理
    video_hash = get_file_hash(video_path)
    cache_file = Path(f"./temp/{video_hash}.json")

    if cache_file.exists():
        logger.info("使用缓存结果")
        return json.loads(cache_file.read_text())

    # 执行处理
    result = process_video(video_path, report_path)

    # 保存缓存
    cache_file.parent.mkdir(exist_ok=True)
    cache_file.write_text(json.dumps(result))

    return result
```

### 8.4 错误处理和重试

```python
import time
from functools import wraps

def retry(max_attempts=3, delay=1):
    """重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    logger.warning(f"尝试 {attempt + 1} 失败: {e}")
                    time.sleep(delay)
        return wrapper
    return decorator

# 使用
@retry(max_attempts=3, delay=2)
def download_video_with_retry(url):
    fetcher = VideoFetcher()
    return fetcher.download_video(url)
```

### 8.5 NeuraPress 集成（专业排版）

> **NeuraPress** 是一个基于 Next.js 的 Markdown 编辑器，专为微信公众号排版设计。通过集成 NeuraPress，你可以为文章添加专业的样式和排版。

#### 8.5.1 安装 NeuraPress

```bash
# 克隆 NeuraPress 仓库
git clone https://github.com/tianyaxiang/neurapress.git
cd neurapress

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

启动成功后，访问 http://localhost:3000

#### 8.5.2 使用 MotoStep 生成 NeuraPress 优化的 Markdown

```python
# 方法1: 使用 full_article_generator.py（推荐）
python full_article_generator.py

# 自动生成三个文件:
# - {标题}.html      - Web 版本
# - {标题}.md        - NeuraPress 优化的 Markdown
# - {标题}.txt       - 纯文本版本
```

NeuraPress 优化的 Markdown 包含:
- ✅ 清晰的标题层级结构
- ✅ 元数据（来源、生成时间）
- ✅ 水平分隔线（`---`）
- ✅ 图片说明和文件大小
- ✅ 时间范围标记

#### 8.5.3 工作流程

```
MotoStep 生成 → 导入 NeuraPress → 应用样式 → 复制到微信公众号
     ↓                ↓                ↓              ↓
  .md 文件      本地编辑器       专业排版        发布文章
```

**详细步骤**:

1. **生成 Markdown**（MotoStep）
   ```bash
   python full_article_generator.py
   ```

2. **导入 NeuraPress**
   - 打开 http://localhost:3000
   - 点击"新建文档"
   - 选择生成的 `.md` 文件

3. **应用微信样式**
   - 在右侧"样式面板"选择预设
   - 推荐样式: "微信默认风格" 或 "杂志风格"

4. **预览和调整**
   - 点击"预览"查看效果
   - 在"手机模式"下检查移动端显示

5. **复制到微信**
   - 点击"复制"按钮（或 Ctrl+A → Ctrl+C）
   - 粘贴到微信公众号编辑器
   - 手动上传图片（微信限制）

#### 8.5.4 三种输出格式对比

| 格式 | 文件扩展名 | 优点 | 缺点 | 适用场景 |
|------|-----------|------|------|----------|
| **HTML** | `.html` | 样式完整，即开即用 | 样式控制有限 | 快速发布、浏览器查看 |
| **Markdown (NeuraPress)** | `.md` | 结构清晰，专业排版 | 需要额外工具 | 追求高质量排版 |
| **纯文本** | `.txt` | 通用性强，无格式 | 无样式，需手动排版 | 跨平台发布 |

#### 8.5.5 使用示例

**生成所有格式**:
```python
# full_article_generator.py 会自动生成三种格式
python full_article_generator.py

# 输出:
# output/articles/Mikuni_HSR42/
# ├── 进气之争：Mikuni HSR 42 真的值那 300 美金吗？.html
# ├── 进气之争：Mikuni HSR 42 真的值那 300 美金吗？.md
# ├── 进气之争：Mikuni HSR 42 真的值那 300 美金吗？.txt
# └── media/
#     ├── 02_51s.gif
#     ├── 04_72s.gif
#     └── ...
```

**在 NeuraPress 中使用**:
```markdown
# MotoStep 生成的 Markdown 示例

# 进气之争：Mikuni HSR 42 真的值那 300 美金吗？

**来源**: CV Carburetor VS Mikuni flat slide
**生成时间**: 2026-01-30 11:32:35

---

## 1. CV 化油器：会替你"思考"的真空系统

**时间范围**: 00:00:51 - 00:01:12

![CV化油器工作原理](media/02_51s.gif)

*动图: CV（Constant Velocity）代表"等速"...*

这种设计最核心的意义在于它的"平滑效应"...

---

## 2. "平滑效应"：机械式的牵引力控制

**时间范围**: 00:01:12 - 00:01:38

...
```

#### 8.5.6 常见问题

**Q: NeuraPress 已被标记为 deprecated，还能使用吗？**

A: 可以。虽然官方停止维护，但核心功能仍然可用。如果需要更活跃的项目，可以考虑:
- [Markdown Nice](https://www.mdnice.com/) - 在线工具
- 直接使用 MotoStep 生成的 HTML

**Q: 为什么需要手动上传图片？**

A: 微信公众号只接受上传到其素材库的图片，不支持本地路径或外链（除非有白名单）。生成的 Markdown 中的图片路径如 `media/02_51s.gif` 需要手动上传。

**Q: 如何处理微信的 2MB 文件大小限制？**

A: MotoStep 生成的 GIF 通常为 6-7 MB，超过微信限制。解决方案:
```bash
# 使用 convert_for_wechat.py 转换
python convert_for_wechat.py

# 选择:
# 1. 转换为 MP4 视频（推荐，无大小限制）
# 2. 压缩 GIF 到 2MB 以下
# 3. 使用静态图片
```

#### 8.5.7 相关文档

- **NeuraPress 详细使用指南**: `docs/NeuraPress_使用指南.md`
- **NeuraPress GitHub**: https://github.com/tianyaxiang/neurapress
- **Markdown 语法参考**: https://www.markdownguide.org/

---

## 9. API参考

### 9.1 VideoFetcher (视频获取模块)

```python
from src.video_fetcher import VideoFetcher

fetcher = VideoFetcher(
    output_dir="./output/videos",    # 视频输出目录
    quality="720p",                  # 视频质量
    cookies_path=None                # Cookies文件路径
)

# 下载视频
video_info = fetcher.download_video(
    url: str,                        # YouTube URL
    quality: str = "720p",           # 视频质量
    cookies_path: str = None         # Cookies文件
) -> dict

# 返回格式:
{
    "video_id": "oPFg4VkIVIY",
    "title": "视频标题",
    "video_path": "/path/to/video.mp4",
    "subtitle_path": "/path/to/subtitle.srt",
    "duration": 600,  # 秒
    "thumbnail": "https://..."
}
```

### 9.2 ContentAnalyzer (内容分析模块)

```python
from src.content_analyzer import ContentAnalyzer

analyzer = ContentAnalyzer()

# 从报告分析
analysis = analyzer.analyze_from_report(
    report_path: str,                # NotebookLM报告路径
    subtitle_path: str = None        # 字幕文件路径（可选）
) -> VideoAnalysis

# 从字幕分析
analysis = analyzer.analyze_from_subtitle(
    subtitle_path: str,              # 字幕文件路径
    video_title: str                 # 视频标题
) -> VideoAnalysis

# 保存分析结果
analyzer.save_analysis(
    analysis: VideoAnalysis,
    output_path: str
)

# VideoAnalysis 结构:
{
    "video_id": "xxx",
    "title": "视频标题",
    "summary": "视频摘要",
    "techniques": [                  # 技术点列表
        {
            "name": "技术名称",
            "name_en": "English Name",
            "description": "详细说明"
        }
    ],
    "key_moments": [                 # 关键时刻列表
        {
            "timestamp": 30,         # 时间戳（秒）
            "title": "场景标题",
            "description": "场景描述",
            "media_type": "image"    # "image" 或 "gif"
        }
    ]
}
```

### 9.3 MediaProcessor (媒体处理模块)

```python
from src.media_processor import MediaProcessor

processor = MediaProcessor(
    output_dir="./output/images",
    screenshot_quality=2,            # 1-5
    gif_width=480,
    gif_fps=10,
    watermark_text="FreeSoloDirtbike"
)

# 生成所有媒体资产
assets = processor.generate_assets(
    video_path: str,                 # 视频文件路径
    analysis: VideoAnalysis,         # 分析结果
    output_dir: str = "./output/images"
) -> List[MediaAsset]

# 生成单个资产
asset = processor.generate_single_asset(
    video_path: str,
    moment: KeyMoment,
    output_dir: str
) -> MediaAsset

# MediaAsset 结构:
{
    "path": "/path/to/asset.jpg",
    "type": "image",                 # "image" 或 "gif"
    "timestamp": 30,
    "title": "场景标题",
    "size": 102400                   # 字节
}
```

### 9.4 ContentComposer (内容合成模块)

```python
from src.content_composer import ContentComposer

composer = ContentComposer()

# 从对象合成
article = composer.compose(
    analysis: VideoAnalysis,
    assets: List[MediaAsset],
    output_dir: str,
    template_path: str = None        # 自定义模板（可选）
) -> dict

# 从文件合成
article = composer.compose_from_files(
    analysis_path: str,
    images_dir: str,
    output_dir: str
) -> dict

# 返回格式:
{
    "wechat_html": "/path/to/wechat.html",
    "markdown": "/path/to/report.md",
    "html_report": "/path/to/report.html",
    "title": "文章标题",
    "summary": "文章摘要",
    "stats": {
        "technique_count": 6,
        "media_count": 3
    }
}
```

### 9.5 WeChatClient (微信发布模块，开发中)

```python
from src.wechat_publisher import WeChatClient

client = WeChatClient(
    app_id="your_app_id",
    app_secret="your_app_secret"
)

# 获取访问令牌
token = client.get_access_token()

# 上传媒体
media_id = client.upload_media(
    file_path: str,
    media_type: str  # "image" 或 "video"
)

# 创建草稿
draft_id = client.create_draft(
    title: str,
    content: str,
    cover_media_id: str
)
```

---

## 10. 常见问题

### 10.1 安装和配置

**Q1: 安装依赖时报错 "Microsoft Visual C++ 14.0 is required"？**

A: Windows 用户需要安装 Visual Studio Build Tools：
1. 下载 [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/)
2. 安装"使用 C++ 的桌面开发"组件
3. 重新运行 `pip install -r requirements.txt`

**Q2: FFmpeg 安装后无法识别？**

A: 确保 FFmpeg 已添加到系统 PATH：
```bash
# 检查 FFmpeg 版本
ffmpeg -version

# 如果提示找不到命令，需要添加到 PATH
# Windows: 将 FFmpeg bin 目录添加到系统环境变量
# macOS/Linux: 添加到 ~/.bash_profile 或 ~/.zshrc
export PATH="/path/to/ffmpeg/bin:$PATH"
```

**Q3: 如何获取微信公众号的 AppID 和 AppSecret？**

A:
1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 进入"开发" → "基本配置"
3. 如果没有 AppSecret，点击"重置"生成
4. 将值复制到 `.env` 文件

### 10.2 视频下载

**Q4: 视频下载失败，提示 "Video unavailable"？**

A: 可能的原因和解决方案：
1. 视频需要登录：提供 cookies.txt 文件
2. 视频地区限制：使用 VPN
3. 视频已删除：检查视频是否仍然可用

**Q5: 下载速度太慢？**

A: 优化建议：
1. 使用更快的网络连接
2. 降低视频质量（720p → 480p）
3. 使用代理或 CDN 加速

**Q6: 如何下载需要登录的 YouTube 视频？**

A:
1. 安装浏览器扩展 "Get cookies.txt LOCALLY"
2. 登录 YouTube
3. 导出 cookies.txt
4. 在配置中设置 `VIDEO_COOKIES_PATH=./cookies.txt`

### 10.3 内容分析

**Q7: NotebookLM 报告的格式有什么要求？**

A: 报告必须包含以下部分：
- `Summary` 或 `摘要`：视频概要
- `Key Techniques` 或 `关键技术`：技术点列表
- `Key Moments` 或 `关键时刻`：时间戳列表，格式为 `分:秒 - 描述`

**Q8: 视频没有字幕怎么办？**

A: MotoStep 支持无字幕模式：
1. 仅使用 NotebookLM 报告中的时间戳
2. 自动跳过字幕分析步骤
3. 确保报告中的时间戳准确即可

**Q9: 分析结果不准确怎么办？**

A: 优化方法：
1. 改进 NotebookLM 提示词，要求更详细的分析
2. 提供英文字幕，提高时间戳准确性
3. 手动编辑报告，修正错误的时间戳

### 10.4 媒体生成

**Q10: GIF 文件太大？**

A: 减小 GIF 尺寸的方法：
```python
# 在 .env 文件中调整
GIF_WIDTH=320          # 减小宽度（默认480）
GIF_FPS=8              # 降低帧率（默认10）
GIF_USE_PALETTE=true   # 使用调色板优化
```

**Q11: 截图质量不够高？**

A: 提高截图质量：
```python
# 在 .env 文件中调整
SCREENSHOT_QUALITY=5   # 1-5，越高质量越高（默认2）
```

**Q12: 如何修改水印文字和位置？**

A: 当前版本水印文字可在 `.env` 中修改：
```bash
WATERMARK_TEXT=YourText
```

自定义位置需要修改源代码 `src/media_processor/processor.py`

### 10.5 内容生成

**Q13: 生成的文章格式不符合要求？**

A: 可以使用自定义模板：
```python
# 创建自定义模板
# 参见 8.2 节"自定义文章模板"

# 使用模板
composer.compose(..., template_path="your_template.html")
```

**Q14: 如何调整文章长度？**

A: 在 `.env` 文件中设置：
```bash
ARTICLE_MIN_LENGTH=5000   # 最小字数
ARTICLE_MAX_LENGTH=10000  # 最大字数
```

或在 NotebookLM 报告中控制内容详细程度。

### 10.6 微信发布

**Q15: 微信发布失败，提示 "access_token invalid"？**

A: 检查：
1. AppID 和 AppSecret 是否正确
2. 是否已获取正确的 access_token
3. IP 地址是否在微信白名单中

**Q16: 上传图片到微信失败？**

A: 微信图片限制：
- 格式：JPG/PNG
- 大小：≤ 2MB
- 尺寸：建议 900×500 像素

---

## 11. 故障排除

### 11.1 日志查看

MotoStep 使用 `loguru` 记录日志：

```python
from loguru import logger

# 配置日志
logger.add(
    "./logs/motostep_{time}.log",    # 日志文件
    rotation="1 day",                 # 每天轮换
    retention="7 days",               # 保留7天
    level="INFO"                      # 日志级别
)
```

查看日志：
```bash
# 查看最新日志
tail -f ./logs/motostep_2026-01-30.log

# 搜索错误
grep "ERROR" ./logs/motostep_*.log
```

### 11.2 常见错误代码

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| `VideoUnavailable` | 视频不可用 | 检查视频URL，确认视频可访问 |
| `SubtitleNotFound` | 字幕不存在 | 使用无字幕模式，或提供其他语言的字幕 |
| `AnalysisFailed` | 分析失败 | 检查 NotebookLM 报告格式 |
| `FFmpegError` | FFmpeg 错误 | 确认 FFmpeg 已正确安装 |
| `WeChatAuthFailed` | 微信认证失败 | 检查 AppID 和 AppSecret |
| `NetworkError` | 网络错误 | 检查网络连接，尝试使用代理 |

### 11.3 调试模式

启用调试模式：

```python
# 在 .env 文件中设置
APP_ENV=development
APP_LOG_LEVEL=DEBUG
FLASK_DEBUG=true
```

或直接在代码中：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 11.4 性能分析

```python
import time
from functools import wraps

def timing(func):
    """计时装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.info(f"{func.__name__} 耗时: {end - start:.2f}秒")
        return result
    return wrapper

# 使用
@timing
def process_video(url):
    # ...
    pass
```

### 11.5 测试各模块

```bash
# 测试视频下载
python test_video_fetcher.py

# 测试媒体处理
python test_media_processor.py

# 测试内容分析
python test_content_analyzer.py

# 测试文章生成
python test_content_composer.py

# 完整流程测试
python test_end_to_end.py
```

---

## 12. 附录

### 12.1 项目结构详解

```
motostep/
├── .env                          # 环境配置（需创建）
├── .env.example                  # 环境变量模板
├── .gitignore                    # Git忽略文件
├── config.py                     # Pydantic配置管理
├── requirements.txt              # Python依赖列表
│
├── src/                          # 源代码目录
│   ├── __init__.py
│   │
│   ├── video_fetcher/            # 视频获取模块
│   │   ├── __init__.py
│   │   └── fetcher.py            # VideoFetcher类
│   │
│   ├── content_analyzer/         # 内容分析模块
│   │   ├── __init__.py
│   │   ├── analyzer.py           # ContentAnalyzer类
│   │   ├── notebooklm_helper.py  # NotebookLM辅助
│   │   └── timestamp_extractor.py # 时间戳提取
│   │
│   ├── media_processor/          # 媒体处理模块
│   │   ├── __init__.py
│   │   ├── processor.py          # MediaProcessor类
│   │   └── ffmpeg_wrapper.py     # FFmpeg包装器
│   │
│   ├── content_composer/         # 内容合成模块
│   │   ├── __init__.py
│   │   └── composer.py           # ContentComposer类
│   │
│   ├── wechat_publisher/         # 微信发布模块
│   │   ├── __init__.py
│   │   ├── client.py             # WeChatClient类
│   │   └── draft_manager.py      # DraftManager类
│   │
│   └── models/                   # 数据模型
│       ├── __init__.py
│       ├── video.py              # VideoAnalysis, KeyMoment等
│       └── article.py            # Article相关模型
│
├── output/                       # 输出目录（自动创建）
│   ├── videos/                   # 下载的视频
│   ├── subtitles/                # 提取的字幕
│   ├── reports/                  # AI分析报告
│   ├── images/                   # 生成的媒体文件
│   ├── analysis/                 # 分析结果JSON
│   └── articles/                 # 生成的文章
│
├── temp/                         # 临时文件
├── logs/                         # 日志文件
│
├── tests/                        # 单元测试（未实现）
│
├── test_*.py                     # 集成测试脚本
│   ├── test_video_fetcher.py
│   ├── test_media_processor.py
│   ├── test_content_analyzer.py
│   ├── test_content_composer.py
│   └── test_end_to_end.py
│
└── docs/                         # 文档（未创建）
```

### 12.2 依赖项说明

| 依赖包 | 版本 | 用途 |
|--------|------|------|
| yt-dlp | 2025.12.08 | YouTube 视频下载 |
| httpx | 0.27.0 | HTTP 客户端 |
| jinja2 | 3.1.6 | 模板引擎 |
| pydantic | 2.10.4 | 数据验证 |
| pydantic-settings | 2.7.1 | 配置管理 |
| loguru | 0.7.3 | 日志记录 |

### 12.3 环境变量完整列表

参见 [4.1 环境变量配置](#41-环境变量配置-env)

### 12.4 NotebookLM 报告示例

完整示例参见 [6.1 准备 NotebookLM 报告](#61-准备-notebooklm-报告)

### 12.5 贡献指南

欢迎贡献代码！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 12.6 开发路线图

| 阶段 | 功能 | 状态 | 预计完成 |
|------|------|------|---------|
| 1 | 项目初始化 | ✅ 完成 | 2026-01-27 |
| 2 | 视频获取模块 | ✅ 完成 | 2026-01-28 |
| 3 | 媒体处理模块 | ✅ 完成 | 2026-01-29 |
| 4 | 内容分析模块 | ✅ 完成 | 2026-01-29 |
| 5 | 内容合成模块 | ✅ 完成 | 2026-01-29 |
| 6 | 微信发布模块 | 🚧 开发中 | 2026-02-05 |
| 7 | Web 界面 | ⏳ 计划中 | 2026-02-15 |
| 8 | 批量处理优化 | ⏳ 计划中 | 2026-02-20 |

### 12.7 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

### 12.8 联系方式

- 项目地址：https://github.com/zhaoran30184898-jpg/motostep
- 问题反馈：https://github.com/zhaoran30184898-jpg/motostep/issues
- 邮箱：（待补充）

### 12.9 致谢

本项目复用了以下开源项目的代码：

1. **ytreport-dirtbike**
   - FFmpeg 命令（截图、GIF、水印）
   - HTML 报告模板
   - 工作流程参考

2. **wechat-PA**
   - WeChatClient（微信 API 客户端）
   - DraftManager（草稿管理器）
   - Article 数据模型

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v0.1.0-alpha | 2026-01-30 | 初始版本，核心功能完成 |

---

**文档结束**

如有问题或建议，请提交 Issue 或 Pull Request！
