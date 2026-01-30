"""Pytest配置和共享fixtures"""
import sys
from pathlib import Path
import pytest
import shutil

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session")
def project_root():
    """项目根目录"""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def output_dir(project_root):
    """输出目录"""
    output = project_root / "output" / "tests"
    output.mkdir(parents=True, exist_ok=True)
    return output


@pytest.fixture(scope="session")
def test_data_dir(project_root):
    """测试数据目录"""
    return project_root / "tests" / "fixtures"


@pytest.fixture(scope="function")
def clean_output_dir(output_dir):
    """每个测试后清理输出目录"""
    yield
    # 清理测试生成的文件
    if output_dir.exists():
        for file in output_dir.glob("*"):
            if file.is_file():
                file.unlink()


class TestVideoInfo:
    """测试用视频信息"""
    video_id = "test_video_123"
    title = "Test Motocross Video"
    duration = 600  # 10分钟


@pytest.fixture
def sample_video_info():
    """示例视频信息"""
    return TestVideoInfo()


class TestPaths:
    """测试用路径"""
    def __init__(self):
        self.sample_video = Path("tests/fixtures/sample_video.mp4")
        self.sample_report = Path("tests/fixtures/sample_report.txt")
        self.sample_subtitle = Path("tests/fixtures/sample_subtitle.vtt")


@pytest.fixture
def test_paths(test_data_dir):
    """测试用路径"""
    return TestPaths()
