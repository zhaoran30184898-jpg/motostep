"""NotebookLM报告解析助手"""
import re
from pathlib import Path
from typing import List, Dict, Optional
from loguru import logger


class NotebookLMHelper:
    """NotebookLM报告解析辅助类"""

    def __init__(self):
        """初始化助手"""
        pass

    def parse_report(self, report_path: str) -> Dict:
        """
        解析NotebookLM生成的文本报告

        Args:
            report_path: 报告文件路径（.txt格式）

        Returns:
            解析后的报告数据字典，包含：
            - title: 视频标题
            - summary: 内容摘要
            - techniques: 技术列表
            - key_moments: 关键时刻
        """
        logger.info(f"解析NotebookLM报告: {report_path}")

        report_file = Path(report_path)
        if not report_file.exists():
            raise FileNotFoundError(f"报告文件不存在: {report_path}")

        # 读取报告内容
        content = report_file.read_text(encoding='utf-8')

        # 解析报告
        result = {
            "title": self._extract_title(content),
            "summary": self._extract_summary(content),
            "techniques": self._extract_techniques(content),
            "key_moments": self._extract_key_moments(content)
        }

        logger.success(f"✓ 报告解析成功")
        logger.info(f"  标题: {result['title']}")
        logger.info(f"  技术数量: {len(result['techniques'])}")
        logger.info(f"  关键时刻: {len(result['key_moments'])}")

        return result

    def _extract_title(self, content: str) -> str:
        """提取视频标题"""
        # 尝试多种标题格式
        patterns = [
            r'^#\s+(.+)$',  # Markdown # 标题
            r'^Title:\s*(.+)$',  # Title: 行
            r'^视频标题[：:]\s*(.+)$',  # 中文标题行
            r'^(.+)\s*-\s*YouTube',  # YouTube格式
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                return match.group(1).strip()

        # 如果没找到，使用第一行
        first_line = content.split('\n')[0].strip()
        return first_line if first_line else "未命名视频"

    def _extract_summary(self, content: str) -> str:
        """提取内容摘要"""
        # 查找摘要部分
        patterns = [
            r'##\s*摘要\s*\n+(.+?)(?=\n##|\n\n|\Z)',  # Markdown摘要
            r'Summary[：:]\s*\n+(.+?)(?=\n\n|\Z)',  # 英文Summary
            r'摘要[：:]\s*\n+(.+?)(?=\n\n|\Z)',  # 中文摘要
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                summary = match.group(1).strip()
                # 清理多余的空行
                summary = re.sub(r'\n{3,}', '\n\n', summary)
                return summary

        # 如果没找到专门的摘要部分，返回前500字符
        lines = content.split('\n')
        summary_lines = []
        for line in lines[:10]:
            if line.strip() and not line.startswith('#'):
                summary_lines.append(line)
            if len('\n'.join(summary_lines)) > 300:
                break

        return '\n'.join(summary_lines).strip() or "无摘要"

    def _extract_techniques(self, content: str) -> List[Dict]:
        """
        提取技术列表

        Returns:
            技术列表，每个技术包含：
            - name: 技术名称
            - description: 技术描述
            - keywords: 搜索关键词列表
        """
        techniques = []

        # 尝试识别技术列表的多种格式
        # 格式1: - **技术名称**: 描述内容
        list_pattern = r'(?:^|\n)[-*]\s+\*\*(.+?)\*\*[：:]\s*(.+?)(?=(?:\n[-*]|\n\n|\Z))'
        matches = re.finditer(list_pattern, content, re.MULTILINE | re.DOTALL)

        for match in matches:
            name = match.group(1).strip()
            description = match.group(2).strip()

            # 清理描述（移除多余的换行）
            description = re.sub(r'\n+', ' ', description)

            # 生成搜索关键词（从技术名称中提取）
            keywords = self._generate_keywords(name, description)

            techniques.append({
                "name": name,
                "description": description,
                "keywords": keywords
            })

        # 格式2: 编号列表
        if not techniques:
            numbered_pattern = r'\n\d+\.\s+\*\*(.+?)\*\*[：:]\s*(.+?)(?=(?:\n\d+\.|\n\n|\Z))'
            matches = re.finditer(numbered_pattern, content, re.MULTILINE | re.DOTALL)

            for match in matches:
                name = match.group(1).strip()
                description = match.group(2).strip()
                description = re.sub(r'\n+', ' ', description)
                keywords = self._generate_keywords(name, description)

                techniques.append({
                    "name": name,
                    "description": description,
                    "keywords": keywords
                })

        # 格式3: 关键词提取（如果没有明确的列表格式）
        if not techniques:
            logger.warning("未找到明确的技术列表，使用关键词提取")
            techniques = self._fallback_technique_extraction(content)

        return techniques

    def _clean_list_text(self, text: str) -> str:
        """清理列表文本，移除列表标记"""
        lines = text.split('\n')
        cleaned = []
        for line in lines:
            # 移除列表标记 (-, *, 1., 2., etc)
            cleaned_line = re.sub(r'^[-*\d+.]+\s+', '', line.strip())
            if cleaned_line:
                cleaned.append(cleaned_line)

        return ' '.join(cleaned).strip()

    def _generate_keywords(self, name: str, description: str) -> List[str]:
        """
        从技术名称和描述生成搜索关键词

        优先级：
        1. 技术名称中的核心词汇
        2. 描述中的关键词
        3. 相关技术术语
        """
        keywords = []

        # 从名称中提取关键词
        # 移除常见的连接词和标点
        name_words = re.findall(r'\b[A-Za-z]{3,}\b', name)
        keywords.extend([w.lower() for w in name_words if len(w) >= 3])

        # 从描述中提取关键词（名词和动词）
        desc_words = re.findall(r'\b[A-Za-z]{4,}\b', description)
        # 添加出现频率高的词
        from collections import Counter
        word_freq = Counter(desc_words)
        for word, count in word_freq.most_common(5):
            if word.lower() not in keywords and count >= 2:
                keywords.append(word.lower())

        # 添加常见技术术语（如果有相关词出现）
        tech_terms = {
            'brake': ['braking', 'brake', 'front brake', 'rear brake'],
            'corner': ['cornering', 'corner', 'turn', 'apex'],
            'jump': ['jump', 'jumping', 'takeoff', 'landing'],
            'body': ['body position', 'weight', 'balance', 'posture'],
            'throttle': ['throttle', 'acceleration', 'gas', 'power'],
        }

        for term, related in tech_terms.items():
            if any(term in text.lower() for text in [name, description]):
                for r in related:
                    if r not in keywords and r in name.lower() + ' ' + description.lower():
                        keywords.append(r)

        # 去重并限制数量
        keywords = list(set(keywords))
        return keywords[:10]  # 最多10个关键词

    def _fallback_technique_extraction(self, content: str) -> List[Dict]:
        """
        备用技术提取方法：当没有明确列表时使用

        基于常见的摩托车技术术语
        """
        # 常见技术术语模式
        tech_patterns = [
            r'(body position|weight transfer|braking|cornering|jumping|acceleration|clutch|throttle)',
            r'(front suspension|rear suspension|compression|rebound)',
            r'(line selection|apex|entry|exit|track standing)',
        ]

        all_matches = []
        for pattern in tech_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                all_matches.append(match.group(1))

        # 去重
        unique_techs = list(set(all_matches))

        techniques = []
        for tech in unique_techs:
            techniques.append({
                "name": tech.title(),
                "description": f"关于{tech}的技术讲解",
                "keywords": [tech.lower()]
            })

        return techniques

    def _extract_key_moments(self, content: str) -> List[Dict]:
        """
        提取关键时刻

        Returns:
            关键时刻列表，每个时刻包含：
            - time: 时间描述（如"2:04"）
            - description: 时刻描述
        """
        key_moments = []

        # 查找时间戳模式 (如 "2:04", "0:15:30")
        time_patterns = [
            r'[-*]\s*\*\*(\d{1,2}:\d{2})\*\*\s*[-–—]\s*(.+)',  # "- **2:04** - description"
            r'(\d{1,2}:\d{2})\s*[-–—]\s*(.+)',  # "2:04 - description"
            r'at\s+(\d{1,2}:\d{2})[：:]\s*(.+)',  # "at 2:04: description"
            r'(\d{1,2}:\d{2})秒[：:]\s*(.+)',  # "2:04秒: description"
        ]

        for pattern in time_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                time_str = match.group(1)
                description = match.group(2).strip()

                # 转换为秒
                seconds = self._time_to_seconds(time_str)

                key_moments.append({
                    "time": time_str,
                    "seconds": seconds,
                    "description": description
                })

        # 按时间排序
        key_moments.sort(key=lambda x: x["seconds"])

        return key_moments

    def _time_to_seconds(self, time_str: str) -> float:
        """
        将时间字符串转换为秒

        支持格式：
        - "2:04" -> 124秒
        - "1:05:30" -> 3930秒
        """
        parts = time_str.split(':')

        if len(parts) == 2:
            # MM:SS
            minutes, seconds = parts
            return int(minutes) * 60 + float(seconds)
        elif len(parts) == 3:
            # HH:MM:SS
            hours, minutes, seconds = parts
            return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
        else:
            logger.warning(f"无法解析时间格式: {time_str}")
            return 0.0

    def validate_report(self, report_path: str) -> bool:
        """
        验证报告文件是否有效

        Args:
            report_path: 报告文件路径

        Returns:
            是否为有效的NotebookLM报告
        """
        try:
            report_file = Path(report_path)

            # 检查文件存在
            if not report_file.exists():
                logger.error(f"报告文件不存在: {report_path}")
                return False

            # 检查文件格式
            if report_file.suffix.lower() not in ['.txt', '.md']:
                logger.error(f"报告格式不支持: {report_file.suffix}")
                return False

            # 检查文件大小
            if report_file.stat().st_size < 100:
                logger.error("报告文件太小，可能不是有效报告")
                return False

            # 检查内容
            content = report_file.read_text(encoding='utf-8')
            if len(content.strip()) < 50:
                logger.error("报告内容太少")
                return False

            return True

        except Exception as e:
            logger.error(f"报告验证失败: {e}")
            return False
