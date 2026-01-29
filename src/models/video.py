"""视频相关数据模型"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class VideoInfo(BaseModel):
    """视频信息模型"""
    video_id: str = Field(..., description="视频ID")
    url: str = Field(..., description="视频URL")
    title: str = Field(..., description="视频标题")
    duration: int = Field(..., description="视频时长（秒）")
    width: int = Field(default=1280, description="视频宽度")
    height: int = Field(default=720, description="视频高度")
    local_path: str = Field(..., description="本地文件路径")
    subtitle_paths: Dict[str, str] = Field(default_factory=dict, description="字幕文件路径 {语言: 路径}")
    thumbnail_url: Optional[str] = Field(None, description="缩略图URL")
    file_size_bytes: Optional[int] = Field(None, description="文件大小（字节）")


class KeyMoment(BaseModel):
    """关键时刻模型"""
    timestamp: float = Field(..., description="时间戳（秒）")
    description: str = Field(..., description="场景描述")
    technique: str = Field(..., description="技术要点")
    media_type: str = Field(..., description="媒体类型 (static/gif)")
    duration: Optional[float] = Field(None, description="GIF时长（秒）")
    media_asset: Optional['MediaAsset'] = Field(None, description="关联的媒体资产")


class VideoAnalysis(BaseModel):
    """视频分析结果模型"""
    video_id: str = Field(..., description="视频ID")
    title: str = Field(..., description="视频标题")
    instructor: Optional[str] = Field(None, description="教练/车手名称")
    summary: str = Field(default="", description="摘要")
    content: str = Field(..., description="完整报告内容")
    key_moments: List[KeyMoment] = Field(default_factory=list, description="关键时刻列表")
    metadata: Dict = Field(default_factory=dict, description="其他元数据")


class MediaAsset(BaseModel):
    """媒体资产模型"""
    type: str = Field(..., description="媒体类型 (image/gif)")
    local_path: str = Field(..., description="本地文件路径")
    url: Optional[str] = Field(None, description="URL")
    timestamp: float = Field(..., description="时间戳（秒）")
    description: str = Field(..., description="描述")
    size_bytes: int = Field(..., description="文件大小（字节）")
    width: Optional[int] = Field(None, description="宽度")
    height: Optional[int] = Field(None, description="高度")
    wechat_media_id: Optional[str] = Field(None, description="微信素材ID")
