# 🎬 Video2Slides

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/downloads/)

**Automatically convert video files to PowerPoint presentations with customizable frame extraction.**

## ✨ Features

- 🎬 **Smart Frame Extraction** - Extract frames at specified time intervals with intelligent deduplication
- 🧠 **Content-Aware Filtering** - Uses SSIM (Structural Similarity Index) to skip duplicate slides
- 🔲 **Corner Masking** - Ignores corner regions to filter out speaker video movements
- 📊 **PowerPoint Generation** - Create professional PowerPoint presentations
- 📐 **Aspect Ratio Control** - Maintain video aspect ratio or stretch to fill slides
- ⏱️ **Flexible Configuration** - Customizable frame extraction intervals and similarity thresholds
- 🚀 **High Performance** - Fast processing with optimized frame extraction
- 🖼️ **Professional Layout** - Clean, full-slide image layouts
- 📋 **Auto Cleanup** - Automatic temporary file cleanup
- 🔍 **Detailed Logging** - Optional eliot-based JSON logging

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/antonkulaga/video2slides.git
cd video2slides

# Install with uv
uv sync
```

### Basic Usage

```bash
# Basic usage (extract 1 frame per second, filter duplicates automatically)
uv run video2slides video.mp4

# Extract 1 frame every 5 seconds
uv run video2slides video.mp4 -i 5

# Maintain aspect ratio and specify output
uv run video2slides video.mp4 -k -o presentation.pptx

# More strict similarity (fewer frames, only major slide changes)
uv run video2slides video.mp4 -s 0.98

# Less strict similarity (more frames, detect subtle changes)
uv run video2slides video.mp4 -s 0.90

# Disable corner filtering (compare entire frame including speaker)
uv run video2slides video.mp4 --no-ignore-corners
```

### Downloading YouTube Videos

If you want to convert YouTube videos to slides, first download them using `yt-dlp`:

```bash
# Install yt-dlp (if not already installed)
uv pip install yt-dlp

# Download a YouTube video
yt-dlp -f "best[ext=mp4]/best" -o "lecture.mp4" "https://www.youtube.com/watch?v=VIDEO_ID"

# Then convert to slides with deduplication
uv run video2slides lecture.mp4 -i 1 -s 0.95 -k
```

Or using Python:

```python
import yt_dlp

# Download video
ydl_opts = {
    "format": "best[ext=mp4]/best",
    "outtmpl": "lecture.%(ext)s",
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download(["https://www.youtube.com/watch?v=VIDEO_ID"])
```

## 📖 Usage

### Command Line Options

```
Usage: video2slides [OPTIONS] VIDEO

Arguments:
  VIDEO  Path to input video file [required]

Options:
  -o, --output PATH       Path to output PPTX file 
                         (default: <video_name>_slides.pptx in current directory)
  -i, --interval INTEGER  Frame extraction interval in seconds [default: 1]
  -k, --keep-aspect      Maintain video aspect ratio in slides 
                         (otherwise stretch to fill) [default: False]
  -s, --similarity FLOAT  Similarity threshold (0-1) for detecting slide changes
                         (higher = more strict, fewer frames) [default: 0.95]
  --ignore-corners/--no-ignore-corners
                         Ignore corner regions when comparing frames 
                         (useful for speaker video) [default: True]
  --corner-size FLOAT    Size of corners to ignore as percentage (0-1)
                         when ignore-corners is enabled [default: 0.15]
  -l, --log-file PATH    Path to eliot JSON log file (optional)
  -v, --verbose          Show detailed JSON logging to stdout
  --help                 Show this message and exit
```

### Similarity Threshold Guide

The `--similarity` option controls how strict the duplicate detection is:

- **0.98-1.0**: Very strict - Only extracts frames when slides change significantly (recommended for presentations with clear slide transitions)
- **0.95** (default): Balanced - Good for most presentations with speaker video
- **0.90-0.94**: Lenient - Captures more subtle changes
- **< 0.90**: Very lenient - May capture minor variations

### Corner Masking

By default, the tool ignores the corners of each frame (typically 15% from each edge) when comparing similarity. This is useful because:

- **Speaker videos** are often in corners (bottom-right is common)
- **Movement in corners** doesn't indicate slide changes
- **Main slide content** is typically in the center

Disable corner masking with `--no-ignore-corners` if:
- Your video doesn't have a speaker overlay
- Important content appears in corners
- You want to detect any visual changes

### Examples

```bash
# Extract 1 frame every 2 seconds with smart deduplication
uv run video2slides lecture.mp4 -i 2

# Maintain aspect ratio (prevent stretching)
uv run video2slides presentation.mp4 -k

# Specify custom output location
uv run video2slides video.mp4 -o /path/to/slides.pptx

# Combine options for optimal results
uv run video2slides tutorial.mp4 -i 5 -k -o tutorial_slides.pptx

# Very strict - only major slide changes (best for reducing frame count)
uv run video2slides webinar.mp4 -s 0.98 -i 1

# Compare entire frame (no corner masking)
uv run video2slides screen_recording.mp4 --no-ignore-corners

# With detailed logging
uv run video2slides video.mp4 -i 3 -l conversion.log
```

## 📊 Performance

### Frame Reduction with Smart Deduplication

The new similarity-based filtering dramatically reduces the number of extracted frames while keeping all unique slides:

**Example: 30-slide presentation video**
- **Without deduplication**: ~1000+ frames (with speaker movement)
- **With deduplication (default)**: ~30-50 frames (one per slide + transitions)
- **Reduction**: 95%+ fewer frames

### Processing Times

Typical processing times for a 37-minute (76MB) MP4 video:

| Interval | Mode | Processing Time | File Size | Slide Count |
|----------|------|----------------|-----------|-------------|
| -i 10    | With dedup | ~8 seconds  | ~2 MB   | ~30 slides |
| -i 5     | With dedup | ~15 seconds | ~3 MB   | ~40 slides |
| -i 10    | No dedup   | ~7 seconds  | ~9 MB   | ~222 slides|
| -i 5     | No dedup   | ~14 seconds | ~17 MB  | ~444 slides|

**Note**: Processing time increases slightly with deduplication enabled due to SSIM calculations, but the resulting file size is dramatically smaller.

**Recommended:** Use default settings (`-i 1 -s 0.95`) for presentations with speaker video.

## 🛠️ Technology Stack

- **OpenCV** - Video processing and frame extraction
- **python-pptx** - PowerPoint generation
- **scikit-image** - SSIM calculation for frame similarity
- **Typer** - Modern CLI interface
- **Eliot** - Structured logging
- **Pillow** - Image processing
- **NumPy** - Numerical computations

## 🧑‍💻 Development

### Setup Development Environment

```bash
# Install with dev dependencies
uv sync

# Run tests
uv run pytest tests/ -v

# Run linter
uv run ruff check video2slides/

# Run type checker
uv run mypy video2slides/
```

### Project Structure

```
video2slides/
├── video2slides/          # Main package
│   ├── __init__.py       # Package initialization
│   ├── converter.py      # Core conversion logic
│   └── main.py          # CLI interface
├── tests/               # Test suite
├── pyproject.toml      # Project configuration
└── README.md          # This file
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🐛 Support

For questions, issues, or suggestions, please open an issue on GitHub.

