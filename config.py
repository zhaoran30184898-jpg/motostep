"""MotoStep配置管理模块"""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """MotoStep应用配置类"""

    # ===== 微信公众号配置 =====
    wechat_app_id: str = Field(default="", env="WECHAT_APP_ID")
    wechat_app_secret: str = Field(default="", env="WECHAT_APP_SECRET")

    # ===== 视频下载配置 =====
    video_quality: str = Field(default="720p", env="VIDEO_QUALITY")
    video_cookies_path: str = Field(default="./cookies.txt", env="VIDEO_COOKIES_PATH")

    # ===== 媒体生成配置 =====
    screenshot_quality: int = Field(default=2, env="SCREENSHOT_QUALITY")
    gif_width: int = Field(default=480, env="GIF_WIDTH")
    gif_fps: int = Field(default=10, env="GIF_FPS")
    gif_use_palette: bool = Field(default=True, env="GIF_USE_PALETTE")
    watermark_text: str = Field(default="FreeSoloDirtbike", env="WATERMARK_TEXT")

    # ===== 内容生成配置 =====
    article_min_length: int = Field(default=5000, env="ARTICLE_MIN_LENGTH")
    article_max_length: int = Field(default=10000, env="ARTICLE_MAX_LENGTH")
    target_language: str = Field(default="zh-CN", env="TARGET_LANGUAGE")

    # ===== 存储配置 =====
    output_dir: str = Field(default="./output", env="OUTPUT_DIR")
    temp_dir: str = Field(default="./temp", env="TEMP_DIR")
    log_dir: str = Field(default="./logs", env="LOG_DIR")

    # ===== Web服务配置 =====
    flask_host: str = Field(default="127.0.0.1", env="FLASK_HOST")
    flask_port: int = Field(default=5000, env="FLASK_PORT")
    flask_debug: bool = Field(default=True, env="FLASK_DEBUG")

    # ===== 应用配置 =====
    app_env: str = Field(default="development", env="APP_ENV")
    app_log_level: str = Field(default="INFO", env="APP_LOG_LEVEL")
    app_timezone: str = Field(default="Asia/Shanghai", env="APP_TIMEZONE")

    # ===== 重试配置 =====
    http_max_retries: int = Field(default=3, env="HTTP_MAX_RETRIES")
    http_retry_delay: int = Field(default=1, env="HTTP_RETRY_DELAY")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# 全局配置实例
settings = Settings()
