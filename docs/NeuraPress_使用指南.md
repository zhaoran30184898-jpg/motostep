# NeuraPress 使用指南

> **NeuraPress** 是一个基于 Next.js 的 Markdown 编辑器，专为微信公众号排版设计。

**注意**: NeuraPress 目前已被官方标记为 deprecated（已弃用），但仍可使用。

## 工作流程概览

```
MotoStep 生成 Markdown → 导入 NeuraPress → 应用样式 → 复制到微信公众号
```

---

## 安装步骤

### 1. 系统要求

- **Node.js**: 18.0 或更高版本
- **npm**: 8.0 或更高版本（随 Node.js 安装）
- **操作系统**: Windows, macOS, Linux

### 2. 检查 Node.js 版本

```bash
node --version
# 应显示: v18.x.x 或更高

npm --version
# 应显示: 8.x.x 或更高
```

如果版本过低，请访问 [nodejs.org](https://nodejs.org/) 下载最新 LTS 版本。

### 3. 安装 NeuraPress

由于 NeuraPress 已被弃用，建议从 GitHub 克隆源码安装：

```bash
# 克隆仓库
git clone https://github.com/tianyaxiang/neurapress.git
cd neurapress

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 4. 启动 NeuraPress

```bash
# 在 neurapress 目录下
npm run dev
```

启动成功后，会显示：
```
✓ Ready in 3.2s
○ Local: http://localhost:3000
```

---

## 使用流程

### 步骤 1: 生成 Markdown 文件

使用 MotoStep 生成 Markdown 文件：

```bash
cd C:\Users\dbaa\Desktop\MotoStep
python full_article_generator.py
```

生成的文件位于：
```
output/articles/{文章标题}/{文章标题}.md
```

### 步骤 2: 打开 NeuraPress 编辑器

1. 浏览器访问: http://localhost:3000
2. 点击"新建文档"或"导入 Markdown"
3. 选择 MotoStep 生成的 `.md` 文件

### 步骤 3: 应用微信样式

NeuraPress 提供多种预设样式：

#### 推荐样式选项：

1. **微信默认风格**
   - 简洁清爽
   - 适合技术类文章
   - 字体大小适中

2. **杂志风格**
   - 排版精致
   - 适合长文
   - 视觉层次丰富

3. **商务风格**
   - 专业正式
   - 适合行业分析
   - 色调稳重

应用方法：
- 在右侧"样式面板"中选择预设
- 或在左侧"主题设置"中自定义

### 步骤 4: 调整排版（可选）

#### 图片调整

1. **图片大小**
   - 点击图片，选择宽度（建议 100% 或 90%）
   - 选择边框样式（无、圆角、阴影）

2. **图片说明**
   - Markdown 会自动生成 `*说明文字*`
   - NeuraPress 会将其渲染为灰色小字

#### 标题层级

- `#` 一级标题：文章标题（22px，加粗）
- `##` 二级标题：大节标题（18px，加粗，左边框）
- `###` 三级标题：小节标题（16px，加粗）

#### 引用文本

Markdown 中使用 `>` 标记的文本会显示为引用样式：

```markdown
> "即使你尝试以非常粗鲁的方式拧动油门，
> 真空系统产生的影响也会平滑掉燃油输送中的任何抖动。"
```

### 步骤 5: 预览和调整

1. 点击右上角"预览"按钮
2. 在手机模式下查看效果
3. 调整不合适的样式
4. 重复预览直到满意

### 步骤 6: 复制到微信公众号

1. 点击"复制"按钮（或 Ctrl+A → Ctrl+C）
2. 打开微信公众号编辑器: https://mp.weixin.qq.com/
3. 在编辑器中粘贴（Ctrl+V）
4. 检查格式是否正确

### 步骤 7: 上传图片

**重要**: NeuraPress 导出的 Markdown 中的图片引用是本地路径：
```markdown
![描述](media/02_51s.gif)
```

微信编辑器无法直接识别这些路径，需要手动上传：

#### 方法 A：手动上传（推荐）

1. 在微信编辑器中，点击工具栏的"图片"图标
2. 选择 `output/articles/{文章标题}/media/` 下的文件
3. 插入到对应位置

#### 方法 B：使用外链（需要白名单）

如果文章中有大量图片，可以：
1. 将图片上传到图床（如: 七牛云、阿里云OSS）
2. 在 NeuraPress 中替换图片路径为外链
3. 然后复制到微信

---

## NeuraPress vs 直接粘贴对比

| 方式 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **NeuraPress** | 专业排版、样式丰富、支持主题 | 需要额外工具、学习成本 | 追求高质量排版的文章 |
| **直接粘贴 HTML** | 快速简单、无需额外工具 | 样式控制有限、兼容性问题 | 紧急发布、简单文章 |
| **纯文本** | 通用性强、无格式问题 | 无样式、需要手动排版 | 跨平台发布 |

---

## 常见问题

### Q1: NeuraPress 启动失败

**错误信息**: `Error: Cannot find module 'xxx'`

**解决方法**:
```bash
# 删除 node_modules 和 package-lock.json
rm -rf node_modules package-lock.json

# 重新安装依赖
npm install

# 启动
npm run dev
```

### Q2: 样式在微信中显示异常

**原因**: 微信编辑器会过滤某些 CSS 样式

**解决方法**:
1. 使用 NeuraPress 的"微信兼容"模式
2. 避免使用自定义字体
3. 使用内联样式而非外部 CSS

### Q3: 图片无法显示

**原因**: 本地路径无法在微信中使用

**解决方法**:
- 方案 A: 手动上传图片到微信公众号素材库
- 方案 B: 将图片转为 Base64 嵌入（不推荐，文件会很大）
- 方案 C: 使用图床外链

### Q4: Markdown 导入后格式错乱

**原因**: MotoStep 生成的 Markdown 可能包含不兼容语法

**解决方法**:
1. 检查 Markdown 语法是否标准
2. 使用 MotoStep 的 `enhanced=True` 模式生成
3. 手动修复不兼容的语法

### Q5: NeuraPress 运行缓慢

**原因**: Node.js 应用首次加载较慢

**解决方法**:
1. 等待首次加载完成（约 10-30 秒）
2. 关闭浏览器其他标签页释放内存
3. 使用 Chrome 或 Edge 浏览器（最佳性能）

---

## 进阶技巧

### 1. 自定义样式主题

在 NeuraPress 的 `src/styles/` 目录下修改样式文件：

```css
/* 微信风格自定义 */
.wechat-title {
  font-size: 22px;
  font-weight: bold;
  color: #000;
  text-align: center;
  margin-bottom: 30px;
}

.wechat-section {
  font-size: 18px;
  font-weight: bold;
  color: #2c3e50;
  padding-left: 12px;
  border-left: 4px solid #07c160;
}
```

### 2. 批量处理多个文章

创建脚本批量转换：

```bash
#!/bin/bash
# batch_convert.sh

for md_file in output/articles/*/*.md; do
    echo "Converting: $md_file"
    # 在 NeuraPress 中手动导入此文件
    # 或使用 API（如果可用）
done
```

### 3. 与其他工具集成

#### Typora 集成

1. 在 Typora 中打开 MotoStep 生成的 Markdown
2. 使用 Typora 的导出功能（HTML、PDF）
3. 粘贴到微信公众号

#### VS Code 集成

1. 安装 "Markdown Preview Enhanced" 插件
2. 预览 Markdown 效果
3. 复制渲染后的 HTML

---

## 最佳实践

### ✅ 推荐做法

1. **生成 Markdown 时使用 `enhanced=True`**
   ```python
   generate_markdown_article(data, media, path, enhanced=True)
   ```

2. **图片命名规范**
   - 使用数字前缀: `02_51s.gif`
   - 包含时间戳便于定位

3. **保留原始媒体文件**
   - 媒体文件保存在 `media/` 目录
   - 便于后续重新生成其他格式

4. **版本控制**
   - 将 Markdown 文件纳入 Git 管理
   - 便于追踪修改历史

### ❌ 避免的做法

1. **不要直接修改 NeuraPress 输出的 HTML**
   - 应该修改 Markdown 源文件
   - 重新生成以保证一致性

2. **不要使用特殊字体**
   - 微信只支持系统默认字体
   - 特殊字体会被替换

3. **不要忽略移动端预览**
   - 大部分用户在手机上阅读
   - 务必在手机模式下预览

---

## 替代方案

如果 NeuraPress 无法使用，可以考虑：

### 方案 A: Markdown Nice (在线工具)

- 网站: https://www.mdnice.com/
- 优点: 无需安装，直接在线使用
- 缺点: 需要网络连接

### 方案 B: 微信编辑器原生功能

- 优点: 官方支持，兼容性最好
- 缺点: 样式选择有限

### 方案 B: 直接粘贴 MotoStep HTML

- 优点: 快速简单
- 缺点: 样式控制有限

---

## 总结

NeuraPress 是一个强大的 Markdown 编辑器，特别适合为微信公众号排版。通过以下步骤，你可以轻松生成专业的文章：

1. ✅ 使用 MotoStep 生成 Markdown 文件
2. ✅ 导入 NeuraPress 进行排版
3. ✅ 应用微信样式
4. ✅ 预览并调整
5. ✅ 复制到微信公众号
6. ✅ 手动上传图片

**核心价值**:
- 节省排版时间
- 提升文章质量
- 保持格式一致性

---

## 相关资源

- NeuraPress GitHub: https://github.com/tianyaxiang/neurapress
- Markdown 语法指南: https://www.markdownguide.org/
- 微信公众平台: https://mp.weixin.qq.com/
- MotoStep 文档: `USER_MANUAL.md`

---

**最后更新**: 2026-01-30
**版本**: 1.0
**作者**: MotoStep 团队
