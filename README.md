# MotoStep - 越野摩托教学视频转图文自动化系统

## 项目简介

MotoStep是一个全自动化的内容流水线系统，能够将YouTube上的越野摩托教学视频转化为符合微信公众号规范的技术教学文章，并自动推送到草稿箱。

## 核心功能

- ✅ **视频自动下载**：支持YouTube视频下载（720p/1080p）
- ✅ **AI内容分析**：集成NotebookLM进行深度视频内容分析
- ✅ **关键场景提取**：自动识别并提取关键时间戳
- ✅ **媒体资产生成**：高质量JPG截图 + GIF动图
- ✅ **批量水印添加**：自动为所有媒体添加版权水印
- ✅ **微信发布集成**：一键发布到微信公众号草稿箱

## 技术栈

- **Python**：3.10+
- **视频下载**：yt-dlp 2025.12.08
- **媒体处理**：FFmpeg 8.0.1
- **AI分析**：NotebookLM（手动操作）
- **模板引擎**：Jinja2 3.1.x
- **微信API**：httpx 0.27.x
- **Web框架**：Flask 3.0.x
- **数据验证**：Pydantic 2.10.x

## 安装

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/motostep.git
cd motostep
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 安装FFmpeg

**Windows**:
```bash
# 使用chocolatey
choco install ffmpeg

# 或从官网下载: https://ffmpeg.org/download.html
```

**Mac**:
```bash
brew install ffmpeg
```

**Linux**:
```bash
sudo apt-get install ffmpeg
```

### 4. 配置环境变量

```bash
cp .env.example .env
# 编辑.env文件，填入你的配置
```

**必需配置**：
```bash
# 微信公众号配置
WECHAT_APP_ID=your_app_id
WECHAT_APP_SECRET=your_app_secret

# YouTube cookies（用于访问受限制视频）
VIDEO_COOKIES_PATH=./cookies.txt
```

## 使用方法

### 命令行方式

```bash
# 处理单个视频（不发布）
python main.py "https://www.youtube.com/watch?v=xxx" --report ./output/report.txt

# 处理并发布到微信
python main.py "URL" --report ./output/report.txt --publish

# 批量处理
python main.py --batch urls.txt --reports-dir ./output/reports
```

### Web界面方式

```bash
# 启动Web服务
python app.py

# 访问 http://localhost:5000
```

## 项目结构

```
motostep/
├── src/
│   ├── video_fetcher/         # 视频获取模块
│   ├── content_analyzer/      # 内容分析模块
│   ├── media_processor/       # 媒体处理模块
│   ├── content_composer/      # 内容合成模块
│   ├── wechat_publisher/      # 微信发布模块
│   ├── pipeline/              # 工作流编排
│   └── models/                # 数据模型
├── templates/                 # Web界面模板
├── static/                    # 静态资源
├── output/                    # 输出目录
├── tests/                     # 测试文件
├── config.py                  # 配置管理
├── main.py                    # 命令行入口
└── app.py                     # Flask Web入口
```

## 开发进度

- [x] **阶段1：项目初始化** - 已完成
  - [x] 项目目录结构
  - [x] 配置文件
  - [x] 复用wechat-PA关键文件

- [x] **阶段2：视频获取模块** - 已完成
  - [x] VideoFetcher类
  - [x] 视频下载功能
  - [x] 字幕下载功能

- [ ] **阶段3：媒体处理模块** - 开发中
  - [ ] FFmpegWrapper类
  - [ ] MediaProcessor类
  - [ ] 截图提取
  - [ ] GIF生成
  - [ ] 水印添加

- [ ] **阶段4：内容分析模块**
  - [ ] ContentAnalyzer类
  - [ ] NotebookLM报告解析
  - [ ] 时间戳提取

- [ ] **阶段5：内容合成模块**
  - [ ] ContentComposer类
  - [ ] Jinja2模板
  - [ ] HTML生成

- [ ] **阶段6：工作流编排**
  - [ ] PipelineOrchestrator类
  - [ ] 状态管理

- [ ] **阶段7：Web界面**
  - [ ] Flask应用
  - [ ] 前端页面

- [ ] **阶段8：测试与优化**
  - [ ] 单元测试
  - [ ] 集成测试

## 复用代码

本项目复用了以下两个开源项目的代码：

1. **ytreport-dirtbike**
   - FFmpeg命令（截图、GIF、水印）
   - HTML报告模板
   - 工作流程参考

2. **wechat-PA**
   - WeChatClient（微信API客户端）
   - DraftManager（草稿管理器）
   - Article数据模型

## 贡献指南

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## 联系方式

- 项目地址：https://github.com/zhaoran30184898-jpg/motostep
- 问题反馈：https://github.com/zhaoran30184898-jpg/motostep/issues

---

**开发状态**：v0.1.0-alpha
**最后更新**：2026-01-29
