"""Integration test for downloading YouTube videos and converting them to slides."""

import os
import shutil
from pathlib import Path

import pytest
import yt_dlp
from eliot import start_action

from video2slides.converter import Video2Slides

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent
TEST_DATA_DIR = PROJECT_ROOT / "test_data"


@pytest.fixture
def test_data_dir() -> Path:
    """
    Create a persistent test data directory.
    
    Files are NOT deleted by default so you can examine the results.
    To clean up, manually delete the test_data/ directory or set CLEANUP=1 environment variable.
    """
    TEST_DATA_DIR.mkdir(exist_ok=True)
    yield TEST_DATA_DIR
    
    # Only cleanup if explicitly requested via environment variable
    if os.environ.get("CLEANUP") == "1":
        if TEST_DATA_DIR.exists():
            shutil.rmtree(TEST_DATA_DIR)


def download_youtube_video(video_url: str, output_dir: Path) -> str:
    """
    Download a YouTube video using yt-dlp.
    
    If the video file already exists, skip downloading.

    Args:
        video_url: YouTube video URL
        output_dir: Directory to save the downloaded video

    Returns:
        Path to the downloaded video file
    """
    with start_action(action_type="download_youtube_video", video_url=video_url):
        ydl_opts = {
            "format": "best[ext=mp4]/best",
            "outtmpl": str(output_dir / "%(title)s.%(ext)s"),
            "quiet": False,
            "no_warnings": False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            filename = ydl.prepare_filename(info)
            
            # Check if file already exists
            if os.path.exists(filename):
                print(f"\nVideo already exists, skipping download: {filename}")
                return filename
            
            # Download if not exists
            print(f"\nDownloading video to: {filename}")
            ydl.extract_info(video_url, download=True)

        return filename


def test_youtube_video_to_slides(test_data_dir: Path) -> None:
    """
    Integration test: Download a YouTube video and convert it to slides.

    This test downloads a real video from YouTube and generates a PowerPoint
    presentation from it. Files are saved to test_data/ directory and NOT deleted
    by default so you can examine them.
    
    To enable cleanup, run with: CLEANUP=1 pytest tests/test_integration_youtube.py
    """
    with start_action(action_type="test_youtube_video_to_slides"):
        # YouTube video URL
        video_url = "https://www.youtube.com/watch?v=iHDauMATkr0"

        # Download the video (or use existing)
        video_path = download_youtube_video(video_url, test_data_dir)

        assert os.path.exists(video_path), f"Video file not found: {video_path}"
        assert os.path.getsize(video_path) > 0, "Video file is empty"

        # Convert video to slides
        output_ppt = test_data_dir / "test_slides.pptx"

        converter = Video2Slides(
            video_path=video_path,
            output_path=str(output_ppt),
            fps_interval=2,  # Extract one frame every 2 seconds
            keep_aspect_ratio=True,
        )

        converter.convert()

        # Verify the PowerPoint file was created
        assert output_ppt.exists(), f"PowerPoint file not found: {output_ppt}"
        assert output_ppt.stat().st_size > 0, "PowerPoint file is empty"

        # Print info about the created files
        video_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        ppt_size_mb = output_ppt.stat().st_size / (1024 * 1024)

        print(f"\n{'='*60}")
        print(f"Test completed successfully!")
        print(f"{'='*60}")
        print(f"Video: {os.path.basename(video_path)}")
        print(f"Video size: {video_size_mb:.2f} MB")
        print(f"PowerPoint: {output_ppt.name}")
        print(f"PowerPoint size: {ppt_size_mb:.2f} MB")
        print(f"\nFiles saved to: {test_data_dir.absolute()}")
        print(f"\nTo clean up test files, run: rm -rf {test_data_dir.absolute()}")
        print(f"Or run with: CLEANUP=1 pytest tests/test_integration_youtube.py")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    # Allow running the test directly for manual testing
    import sys

    TEST_DATA_DIR.mkdir(exist_ok=True)
    try:
        test_youtube_video_to_slides(TEST_DATA_DIR)
        print("\nTest passed!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        sys.exit(1)

