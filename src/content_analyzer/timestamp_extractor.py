"""时间戳提取器 - 使用Grep搜索字幕文件"""
import subprocess
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from loguru import logger


class TimestampExtractor:
    """使用Grep从VTT字幕文件中提取时间戳"""

    def __init__(self, grep_path: str = "grep"):
        """
        初始化提取器

        Args:
            grep_path: grep命令路径，Windows下需要安装Git Bash或使用findstr
        """
        self.grep_path = grep_path

    def search_keywords(
        self,
        subtitle_path: str,
        keywords: List[str]
    ) -> List[Dict]:
        """
        在字幕文件中搜索关键词并提取时间戳

        Args:
            subtitle_path: 字幕文件路径（.vtt格式）
            keywords: 关键词列表

        Returns:
            匹配结果列表，每个结果包含：
            - keyword: 匹配的关键词
            - timestamp: VTT时间戳 (如 "00:02:02.719 --> 00:02:05.590")
            - text: 字幕文本
            - start_seconds: 开始时间（秒）
            - end_seconds: 结束时间（秒）
            - mid_seconds: 中间时间（秒）
        """
        logger.info(f"在字幕中搜索{len(keywords)}个关键词...")

        if not Path(subtitle_path).exists():
            raise FileNotFoundError(f"字幕文件不存在: {subtitle_path}")

        all_matches = []

        for keyword in keywords:
            try:
                matches = self._grep_keyword(subtitle_path, keyword)
                all_matches.extend(matches)
            except Exception as e:
                logger.warning(f"搜索关键词 '{keyword}' 失败: {e}")
                continue

        # 按时间排序
        all_matches.sort(key=lambda x: x["start_seconds"])

        # 去重（同一时间段的多个关键词合并）
        unique_matches = self._deduplicate_matches(all_matches)

        logger.success(f"✓ 找到{len(unique_matches)}个匹配")
        return unique_matches

    def _grep_keyword(self, subtitle_path: str, keyword: str) -> List[Dict]:
        """
        使用grep搜索单个关键词

        Args:
            subtitle_path: 字幕文件路径
            keyword: 关键词

        Returns:
            匹配结果列表
        """
        matches = []

        # Windows兼容性：使用findstr或grep
        try:
            # 尝试使用grep（Git Bash）
            result = subprocess.run(
                [self.grep_path, "-i", "-n", keyword, subtitle_path],
                capture_output=True,
                text=True,
                check=False,
                encoding='utf-8',
                errors='ignore'
            )

            if result.returncode != 0:
                # grep失败，尝试Python实现
                return self._fallback_search(subtitle_path, keyword)

            # 解析grep输出
            grep_output = result.stdout
            matches = self._parse_grep_output(subtitle_path, grep_output, keyword)

        except FileNotFoundError:
            # grep不可用，使用Python实现
            logger.debug(f"grep不可用，使用Python搜索: {keyword}")
            matches = self._fallback_search(subtitle_path, keyword)

        return matches

    def _parse_grep_output(
        self,
        subtitle_path: str,
        grep_output: str,
        keyword: str
    ) -> List[Dict]:
        """
        解析grep输出，提取完整的时间戳和文本

        Args:
            subtitle_path: 字幕文件路径
            grep_output: grep的stdout输出
            keyword: 搜索的关键词

        Returns:
            匹配结果列表
        """
        matches = []

        # 读取完整的字幕文件
        subtitle_content = Path(subtitle_path).read_text(encoding='utf-8')
        lines = subtitle_content.split('\n')

        # grep输出格式: "行号:匹配的文本"
        for line in grep_output.split('\n'):
            if not line.strip():
                continue

            try:
                # 提取行号
                line_num = int(line.split(':')[0])

                # 向上查找时间戳（VTT格式：时间戳在文本行之前）
                timestamp_info = self._find_timestamp_for_line(lines, line_num)

                if timestamp_info:
                    # 提取匹配的文本
                    matched_text = ':'.join(line.split(':')[1:]).strip()

                    matches.append({
                        "keyword": keyword,
                        "timestamp": timestamp_info["timestamp"],
                        "text": matched_text,
                        "start_seconds": timestamp_info["start_seconds"],
                        "end_seconds": timestamp_info["end_seconds"],
                        "mid_seconds": timestamp_info["mid_seconds"]
                    })

            except (ValueError, IndexError) as e:
                logger.debug(f"解析grep输出失败: {line}, 错误: {e}")
                continue

        return matches

    def _find_timestamp_for_line(
        self,
        lines: List[str],
        line_num: int
    ) -> Optional[Dict]:
        """
        查找指定行对应的时间戳

        Args:
            lines: 字幕文件所有行
            line_num: 文本行号

        Returns:
            时间戳信息字典
        """
        # VTT格式：时间戳在文本之前
        # 向上搜索最近的时间戳行
        for i in range(line_num - 1, max(0, line_num - 5), -1):
            line = lines[i].strip()

            # VTT时间戳格式: "00:02:02.719 --> 00:02:05.590"
            timestamp_pattern = r'(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})'

            match = re.search(timestamp_pattern, line)
            if match:
                start_time = match.group(1)
                end_time = match.group(2)

                start_seconds = self._vtt_time_to_seconds(start_time)
                end_seconds = self._vtt_time_to_seconds(end_time)
                mid_seconds = (start_seconds + end_seconds) / 2

                return {
                    "timestamp": f"{start_time} --> {end_time}",
                    "start_seconds": start_seconds,
                    "end_seconds": end_seconds,
                    "mid_seconds": mid_seconds
                }

        return None

    def _fallback_search(self, subtitle_path: str, keyword: str) -> List[Dict]:
        """
        备用搜索方法：纯Python实现（当grep不可用时）

        Args:
            subtitle_path: 字幕文件路径
            keyword: 关键词

        Returns:
            匹配结果列表
        """
        matches = []

        subtitle_content = Path(subtitle_path).read_text(encoding='utf-8')
        lines = subtitle_content.split('\n')

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # 检查是否是时间戳行
            timestamp_pattern = r'(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})'
            timestamp_match = re.search(timestamp_pattern, line)

            if timestamp_match:
                # 获取后续的文本行
                text_lines = []
                j = i + 1
                while j < len(lines) and lines[j].strip() and not re.match(timestamp_pattern, lines[j]):
                    text_lines.append(lines[j].strip())
                    j += 1

                text = ' '.join(text_lines)

                # 检查关键词是否在文本中（不区分大小写）
                if keyword.lower() in text.lower():
                    start_time = timestamp_match.group(1)
                    end_time = timestamp_match.group(2)

                    start_seconds = self._vtt_time_to_seconds(start_time)
                    end_seconds = self._vtt_time_to_seconds(end_time)
                    mid_seconds = (start_seconds + end_seconds) / 2

                    matches.append({
                        "keyword": keyword,
                        "timestamp": f"{start_time} --> {end_time}",
                        "text": text,
                        "start_seconds": start_seconds,
                        "end_seconds": end_seconds,
                        "mid_seconds": mid_seconds
                    })

                i = j
            else:
                i += 1

        return matches

    def _deduplicate_matches(self, matches: List[Dict]) -> List[Dict]:
        """
        去重：合并时间上重叠的匹配

        Args:
            matches: 原始匹配列表

        Returns:
            去重后的匹配列表
        """
        if not matches:
            return []

        # 按开始时间排序
        sorted_matches = sorted(matches, key=lambda x: x["start_seconds"])

        unique = []
        current = sorted_matches[0]

        for next_match in sorted_matches[1:]:
            # 检查时间重叠（间隔小于3秒视为重复）
            if next_match["start_seconds"] - current["end_seconds"] < 3:
                # 合并：保留时间范围更大的
                if next_match["end_seconds"] > current["end_seconds"]:
                    current["end_seconds"] = next_match["end_seconds"]
                    current["mid_seconds"] = (current["start_seconds"] + current["end_seconds"]) / 2
                    current["timestamp"] = (
                        f"{self._seconds_to_vtt_time(current['start_seconds'])} --> "
                        f"{self._seconds_to_vtt_time(current['end_seconds'])}"
                    )
                    # 合并关键词
                    if next_match["keyword"] not in current.get("keywords", []):
                        current.setdefault("keywords", []).append(current["keyword"])
                        current["keywords"].append(next_match["keyword"])
            else:
                unique.append(current)
                current = next_match

        unique.append(current)
        return unique

    def _vtt_time_to_seconds(self, vtt_time: str) -> float:
        """
        将VTT时间戳转换为秒

        Args:
            vtt_time: VTT时间戳格式 "00:02:02.719"

        Returns:
            秒数
        """
        # 分割时:分:秒.毫秒
        time_part, ms_part = vtt_time.split('.')
        h, m, s = time_part.split(':')

        total_seconds = int(h) * 3600 + int(m) * 60 + int(s) + float(f"0.{ms_part}")
        return total_seconds

    def _seconds_to_vtt_time(self, seconds: float) -> str:
        """
        将秒转换为VTT时间戳格式

        Args:
            seconds: 秒数

        Returns:
            VTT时间戳 "00:02:02.719"
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60

        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"

    def extract_timestamps_for_technique(
        self,
        technique: Dict,
        subtitle_path: str
    ) -> List[Dict]:
        """
        为特定技术提取所有相关时间戳

        Args:
            technique: 技术信息字典（包含keywords字段）
            subtitle_path: 字幕文件路径

        Returns:
            时间戳列表
        """
        keywords = technique.get("keywords", [])

        if not keywords:
            logger.warning(f"技术 '{technique.get('name')}' 没有关键词")
            return []

        logger.info(f"为技术 '{technique.get('name')}' 提取时间戳...")
        logger.debug(f"  关键词: {keywords}")

        matches = self.search_keywords(subtitle_path, keywords)

        # 为每个匹配添加技术信息
        for match in matches:
            match["technique_name"] = technique.get("name")
            match["technique_desc"] = technique.get("description")

        return matches

    def find_best_timestamp(
        self,
        technique: Dict,
        subtitle_path: str,
        preferred_time: Optional[float] = None
    ) -> Optional[Dict]:
        """
        为技术找到最佳时间戳

        策略：
        1. 如果有preferred_time，选择最接近的时间戳
        2. 否则选择关键词匹配最多的时间戳
        3. 如果都没有，选择第一个时间戳

        Args:
            technique: 技术信息字典
            subtitle_path: 字幕文件路径
            preferred_time: 偏好的时间点（秒）

        Returns:
            最佳时间戳信息
        """
        matches = self.extract_timestamps_for_technique(technique, subtitle_path)

        if not matches:
            return None

        if preferred_time is not None:
            # 选择最接近preferred_time的
            best_match = min(
                matches,
                key=lambda m: abs(m["mid_seconds"] - preferred_time)
            )
            logger.info(f"  选择最接近{preferred_time}秒的时间戳: {best_match['mid_seconds']:.2f}秒")
        else:
            # 选择第一个（通常是最相关的）
            best_match = matches[0]
            logger.info(f"  选择第一个时间戳: {best_match['mid_seconds']:.2f}秒")

        return best_match

    def extract_all_techniques(
        self,
        techniques: List[Dict],
        subtitle_path: str,
        key_moments: Optional[List[Dict]] = None
    ) -> List[Dict]:
        """
        批量提取所有技术的时间戳

        Args:
            techniques: 技术列表
            subtitle_path: 字幕文件路径
            key_moments: 关键时刻列表（可选，用于辅助定位）

        Returns:
            技术时间戳列表，每个包含：
            - technique_name: 技术名称
            - description: 技术描述
            - timestamp: 时间戳
            - start_seconds: 开始时间
            - end_seconds: 结束时间
            - mid_seconds: 中间时间
        """
        logger.info(f"批量提取{len(techniques)}个技术的时间戳...")

        results = []

        for i, technique in enumerate(techniques, 1):
            logger.info(f"\n{i}. {technique.get('name')}")

            # 如果有关键时刻，尝试使用关键时刻作为首选时间
            preferred_time = None
            if key_moments and i <= len(key_moments):
                preferred_time = key_moments[i - 1].get("seconds")

            # 提取时间戳
            timestamp_info = self.find_best_timestamp(
                technique,
                subtitle_path,
                preferred_time
            )

            if timestamp_info:
                results.append({
                    "technique_name": technique.get("name"),
                    "description": technique.get("description"),
                    "timestamp": timestamp_info["timestamp"],
                    "start_seconds": timestamp_info["start_seconds"],
                    "end_seconds": timestamp_info["end_seconds"],
                    "mid_seconds": timestamp_info["mid_seconds"],
                    "keywords_matched": timestamp_info.get("keywords", [timestamp_info["keyword"]])
                })
                logger.success(f"  ✓ 找到时间戳: {timestamp_info['mid_seconds']:.2f}秒")
            else:
                logger.warning(f"  ✗ 未找到时间戳")
                # 仍然添加到结果，但没有时间戳
                results.append({
                    "technique_name": technique.get("name"),
                    "description": technique.get("description"),
                    "timestamp": None,
                    "start_seconds": None,
                    "end_seconds": None,
                    "mid_seconds": None,
                    "keywords_matched": []
                })

        logger.success(f"\n✓ 成功为{sum(1 for r in results if r['timestamp'])}/{len(results)}个技术找到时间戳")

        return results
