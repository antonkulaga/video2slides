"""Unit tests for Video2Slides converter."""

import os
import tempfile
from pathlib import Path

import cv2
import numpy as np
import pytest

from video2slides.converter import Video2Slides


@pytest.fixture
def temp_dir() -> str:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp:
        yield tmp


@pytest.fixture
def sample_video(temp_dir: str) -> str:
    """Create a simple test video file."""
    video_path = os.path.join(temp_dir, "test_video.mp4")
    
    # Create a simple video with 10 frames
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(video_path, fourcc, 2.0, (640, 480))
    
    for i in range(10):
        # Create a frame with a solid color
        frame = (i * 25, i * 25, i * 25)
        img = cv2.imencode('.jpg', cv2.cvtColor(
            cv2.resize(
                cv2.imread(
                    cv2.samples.findFile('samples/data/lena.jpg')
                ) if os.path.exists(cv2.samples.findFile('samples/data/lena.jpg'))
                else cv2.Mat.zeros((480, 640, 3), cv2.CV_8UC3),
                (640, 480)
            ),
            cv2.COLOR_BGR2RGB
        ))[1].tobytes()
        out.write(cv2.imdecode(cv2.frombuffer(img, dtype=cv2.uint8), cv2.IMREAD_COLOR))
    
    out.release()
    return video_path


@pytest.fixture
def sample_video_with_duplicates(temp_dir: str) -> str:
    """Create a test video with duplicate frames (simulating static slides)."""
    video_path = os.path.join(temp_dir, "test_video_duplicates.mp4")
    
    # Create video: 5 unique slides, each shown for 10 frames
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(video_path, fourcc, 10.0, (640, 480))
    
    for slide_num in range(5):
        # Create a unique slide with text
        for _ in range(10):
            frame = np.ones((480, 640, 3), dtype=np.uint8) * (slide_num * 50)
            cv2.putText(
                frame, 
                f"Slide {slide_num + 1}", 
                (200, 240), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                2, 
                (255, 255, 255), 
                3
            )
            out.write(frame)
    
    out.release()
    return video_path


def test_video2slides_init(sample_video: str) -> None:
    """Test Video2Slides initialization."""
    converter = Video2Slides(video_path=sample_video, fps_interval=1)
    
    assert converter.video_path == sample_video
    assert converter.fps_interval == 1
    assert converter.keep_aspect_ratio is False
    assert converter.similarity_threshold == 0.95
    assert converter.ignore_corners is True
    assert os.path.exists(converter.output_path)


def test_video2slides_custom_similarity(sample_video: str) -> None:
    """Test Video2Slides with custom similarity threshold."""
    converter = Video2Slides(
        video_path=sample_video, 
        similarity_threshold=0.98,
        ignore_corners=False
    )
    
    assert converter.similarity_threshold == 0.98
    assert converter.ignore_corners is False


def test_video2slides_file_not_found() -> None:
    """Test that FileNotFoundError is raised for missing video."""
    with pytest.raises(FileNotFoundError):
        Video2Slides(video_path="nonexistent_video.mp4")


def test_video2slides_output_path_default(sample_video: str) -> None:
    """Test that default output path is generated correctly."""
    converter = Video2Slides(video_path=sample_video)
    
    expected_output = f"{Path(sample_video).stem}_slides.pptx"
    assert Path(converter.output_path).name == expected_output


def test_frame_similarity_detection(sample_video_with_duplicates: str, temp_dir: str) -> None:
    """Test that duplicate frames are correctly filtered out."""
    output_path = os.path.join(temp_dir, "output.pptx")
    converter = Video2Slides(
        video_path=sample_video_with_duplicates,
        output_path=output_path,
        fps_interval=1,
        similarity_threshold=0.95
    )
    
    converter.extract_frames()
    
    # Should extract ~5 unique frames (one per slide), not 50
    assert len(converter.frames) < 10, f"Expected < 10 frames, got {len(converter.frames)}"
    assert len(converter.frames) >= 5, f"Expected >= 5 frames, got {len(converter.frames)}"


def test_corner_masking(temp_dir: str) -> None:
    """Test that corner masking correctly ignores corner regions."""
    # Create two frames: identical except for corner
    frame1 = np.ones((480, 640, 3), dtype=np.uint8) * 128
    frame2 = frame1.copy()
    
    # Add different content in corner (simulating speaker movement)
    frame2[400:480, 560:640] = 255
    
    converter = Video2Slides(
        video_path="dummy.mp4",  # Won't be used
        ignore_corners=True
    )
    
    # With corner masking, frames should be considered similar
    similarity = converter._compute_frame_similarity(frame1, frame2)
    assert similarity > 0.90, f"Expected high similarity with corner masking, got {similarity}"
    
    # Without corner masking, frames should be different
    converter.ignore_corners = False
    similarity_no_mask = converter._compute_frame_similarity(frame1, frame2)
    assert similarity_no_mask < similarity, "Expected lower similarity without corner masking"
