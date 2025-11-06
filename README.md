# 🎬 Video2Slides

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/downloads/)

**Convert YouTube videos to PowerPoint presentations with a single command.**

## Simple Usage

Just run this command with any YouTube URL:

```bash
uvx video2slides youtube https://www.youtube.com/watch?v=GC5ouLbJ93E
```

That's it! The tool will:
1. Download the video
2. Extract frames from slides
3. Create a PowerPoint presentation (`.pptx`)

The output file will be saved in the current directory with a name based on the video title.

### Installation (Optional)

If you want to use it without `uvx`, install it globally:

```bash
uv tool install video2slides
video2slides youtube https://www.youtube.com/watch?v=GC5ouLbJ93E
```

---

## Converting Local Video Files

To convert a local video file to slides:

```bash
uvx video2slides convert video.mp4
```

Or after installation:

```bash
video2slides convert video.mp4
```

---

## Features

- 🎬 **Smart Frame Extraction** - Extract frames at specified time intervals with intelligent deduplication
- 🧠 **Content-Aware Filtering** - Uses SSIM (Structural Similarity Index) to skip duplicate slides
- 🔲 **Corner Masking** - Ignores corner regions to filter out speaker video movements
- ⚡ **GPU Support** - Optional GPU acceleration (requires OpenCV with CUDA built from source)
- 📊 **PowerPoint Generation** - Create professional PowerPoint presentations
- 📐 **Aspect Ratio Control** - Maintain video aspect ratio or stretch to fill slides
- ⏱️ **Flexible Configuration** - Customizable frame extraction intervals and similarity thresholds
- 🚀 **High Performance** - Fast processing with optimized frame extraction
- 🖼️ **Professional Layout** - Clean, full-slide image layouts
- 📋 **Auto Cleanup** - Automatic temporary file cleanup
- 🔍 **Detailed Logging** - Optional eliot-based JSON logging

---

## Installation Options

**For users (recommended):**

```bash
# Quick start - no installation needed, just run with uvx
uvx video2slides youtube https://www.youtube.com/watch?v=iHDauMATkr0

# Or install globally for easy access
uv tool install video2slides
video2slides youtube https://www.youtube.com/watch?v=iHDauMATkr0
```

**For developers:**

```bash
# Clone the repository
git clone https://github.com/antonkulaga/video2slides.git
cd video2slides

# Install with uv
uv sync
```

---

## 📖 Detailed Usage

### Commands

Video2Slides provides two main commands:

1. **`convert`** - Convert a local video file to slides
2. **`youtube`** - Download a YouTube video and convert to slides

### Command: `convert`

Converts a local video file to PowerPoint presentation.

```
Usage: video2slides convert [OPTIONS] VIDEO

Arguments:
  VIDEO  Path to input video file [required]

Options:
  -o, --output PATH       Path to output PPTX file 
                         (default: <video_name>.pptx in current directory)
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
  --gpu/--no-gpu         Use GPU acceleration if available [default: True]
  -l, --log-file PATH    Path to eliot JSON log file (optional)
  -v, --verbose          Show detailed JSON logging to stdout
  --help                 Show this message and exit
```

### Command: `youtube`

Downloads a YouTube video and converts it to PowerPoint presentation in one go.

```
video2slides youtube [OPTIONS] URL

Arguments:
  URL    YouTube video URL [required]

Options:
  -o, --output PATH       Path to output PPTX file 
                         (default: <video_title>.pptx in current directory)
  -d, --download-dir PATH Directory to download video 
                         (default: current directory, cleaned up after conversion)
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
  --gpu/--no-gpu         Use GPU acceleration if available [default: True]
  -l, --log-file PATH    Path to eliot JSON log file (optional)
  -v, --verbose          Show detailed JSON logging to stdout
  --keep-video           Keep downloaded video file after conversion
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

#### Converting Local Videos

```bash
# Basic usage (extract 1 frame per second, filter duplicates automatically)
uv run video2slides convert video.mp4

# Extract 1 frame every 5 seconds
uv run video2slides convert video.mp4 -i 5

# Maintain aspect ratio and specify output
uv run video2slides convert video.mp4 -k -o presentation.pptx

# More strict similarity (fewer frames, only major slide changes)
uv run video2slides convert video.mp4 -s 0.98

# Less strict similarity (more frames, detect subtle changes)
uv run video2slides convert video.mp4 -s 0.90

# Disable corner filtering (compare entire frame including speaker)
uv run video2slides convert video.mp4 --no-ignore-corners

# Extract 1 frame every 2 seconds with smart deduplication
uv run video2slides convert lecture.mp4 -i 2

# Maintain aspect ratio (prevent stretching)
uv run video2slides convert presentation.mp4 -k

# Specify custom output location
uv run video2slides convert video.mp4 -o /path/to/slides.pptx

# Combine options for optimal results
uv run video2slides convert tutorial.mp4 -i 5 -k -o tutorial_slides.pptx

# Very strict - only major slide changes (best for reducing frame count)
uv run video2slides convert webinar.mp4 -s 0.98 -i 1

# Compare entire frame (no corner masking)
uv run video2slides convert screen_recording.mp4 --no-ignore-corners

# With detailed logging
uv run video2slides convert video.mp4 -i 3 -l conversion.log
```

**Note**: The `convert` command can also be used without explicitly typing `convert` if there's only one matching command pattern, but it's recommended to be explicit when using multiple commands.

#### Converting YouTube Videos

```bash
# Using uvx (recommended - no installation needed)
uvx video2slides youtube https://www.youtube.com/watch?v=iHDauMATkr0

# Extract 1 frame every 2 seconds
uvx video2slides youtube https://www.youtube.com/watch?v=iHDauMATkr0 -i 2

# Keep aspect ratio and specify output
uvx video2slides youtube https://www.youtube.com/watch?v=iHDauMATkr0 -k -o presentation.pptx

# Keep the downloaded video file after conversion
uvx video2slides youtube https://www.youtube.com/watch?v=iHDauMATkr0 --keep-video

# After global installation
video2slides youtube https://www.youtube.com/watch?v=iHDauMATkr0 -i 2 -o slides.pptx
```

**Manual Download Method** (if you prefer to download separately):

```bash
# Download a YouTube video using yt-dlp (already included with video2slides)
yt-dlp -f "best[ext=mp4]/best" -o "lecture.mp4" "https://www.youtube.com/watch?v=VIDEO_ID"

# Then convert to slides with deduplication
uv run video2slides lecture.mp4 -i 1 -s 0.95 -k
```

---

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

---

## ⚡ GPU Acceleration (Optional)

Video2Slides can use GPU acceleration for faster processing of high-resolution videos. **By default, the tool runs on CPU**, which works well for most use cases.

### GPU Support Status

**Note**: PyPI's `opencv-python` packages **do not include CUDA support**. To enable GPU acceleration, you need to either:
- Build OpenCV from source with CUDA (advanced, ~1 hour)
- Use conda-forge's pre-built OpenCV with CUDA (recommended if needed)

See [`docs/GPU_SETUP.md`](docs/GPU_SETUP.md) for detailed setup instructions.

### When GPU Helps

GPU acceleration (3-10x faster) is most beneficial for:
- 4K and higher resolution videos
- Batch processing many videos
- Very long videos (>1 hour)

For typical use cases (1080p presentations), **CPU performance is sufficient**.

### Usage

```bash
# Default - CPU processing (works out of the box)
uvx video2slides convert video.mp4

# Enable GPU (only if you've set up CUDA-enabled OpenCV)
uvx video2slides convert video.mp4 --gpu
```

---

## 🛠️ Technology Stack

- **OpenCV** - Video processing and frame extraction
- **python-pptx** - PowerPoint generation
- **scikit-image** - SSIM calculation for frame similarity
- **Typer** - Modern CLI interface
- **Eliot** - Structured logging
- **Pillow** - Image processing
- **NumPy** - Numerical computations

---

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

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** - Powers the YouTube download feature with excellent video extraction capabilities
- **[video2ppt](https://github.com/Wangxs404/video2ppt)** - The original idea was loosely inspired by this project, though `video2slides` was written from scratch with a different approach

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🐛 Support

For questions, issues, or suggestions, please open an issue on GitHub.
