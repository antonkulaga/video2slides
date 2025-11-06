# GPU Acceleration Setup Guide

## The Problem

**Bad news first**: PyPI's `opencv-python` and `opencv-contrib-python` packages **DO NOT include CUDA support**. This is a known limitation - OpenCV wheels on PyPI are pre-compiled without CUDA to keep the packages small and portable.

Your system:
- ✅ NVIDIA GeForce RTX 4090
- ✅ CUDA 12.6  
- ✅ Driver 560.35.03

But `video2slides` shows: `💻 GPU acceleration: Disabled (CPU only)`

## Solution Options (Ranked by Ease)

### Option 1: Use Conda/Mamba (EASIEST & RECOMMENDED) ⭐

Conda-forge provides pre-built OpenCV with CUDA support:

```bash
# Install mamba (faster conda)
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-$(uname)-$(uname -m).sh"
bash Mambaforge-$(uname)-$(uname -m).sh

# Create environment with OpenCV + CUDA
mamba create -n video2slides-gpu python=3.11 opencv -c conda-forge
mamba activate video2slides-gpu

# Install video2slides in this environment
cd /home/antonkulaga/sources/video2slides
uv sync

# Verify GPU is detected
python -c "import cv2; print('CUDA devices:', cv2.cuda.getCudaEnabledDeviceCount())"
```

### Option 2: Use System OpenCV (If Already Installed with CUDA)

If you already have OpenCV built with CUDA on your system:

```bash
# Check if system OpenCV has CUDA
python3 -c "import cv2; print('CUDA:', cv2.cuda.getCudaEnabledDeviceCount())"

# If it shows > 0, use system site-packages
cd /home/antonkulaga/sources/video2slides
UV_SYSTEM_PYTHON=1 uv sync

# Or create venv with system site-packages
uv venv --system-site-packages
source .venv/bin/activate
uv sync
```

### Option 3: Build OpenCV from Source with CUDA (MOST CONTROL)

This gives you a custom OpenCV build optimized for your RTX 4090:

```bash
# 1. Install build dependencies
sudo apt-get update
sudo apt-get install -y \
    build-essential cmake git pkg-config \
    libjpeg-dev libtiff-dev libpng-dev \
    libavcodec-dev libavformat-dev libswscale-dev libv4l-dev \
    libxvidcore-dev libx264-dev \
    libatlas-base-dev gfortran \
    python3-dev python3-numpy

# 2. Clone OpenCV repositories
cd ~
git clone https://github.com/opencv/opencv.git
git clone https://github.com/opencv/opencv_contrib.git
cd opencv
git checkout 4.12.0  # Match your current version
cd ../opencv_contrib
git checkout 4.12.0
cd ../opencv

# 3. Configure build for RTX 4090 (Ada Lovelace, compute capability 8.9)
mkdir build && cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=$HOME/.local \
    -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \
    -D WITH_CUDA=ON \
    -D CUDA_ARCH_BIN=8.9 \
    -D CUDA_ARCH_PTX=8.9 \
    -D WITH_CUDNN=ON \
    -D OPENCV_DNN_CUDA=ON \
    -D ENABLE_FAST_MATH=ON \
    -D CUDA_FAST_MATH=ON \
    -D WITH_CUBLAS=ON \
    -D WITH_TBB=ON \
    -D WITH_V4L=ON \
    -D WITH_QT=OFF \
    -D WITH_GTK=ON \
    -D WITH_OPENGL=ON \
    -D PYTHON3_EXECUTABLE=$(which python3) \
    -D PYTHON3_INCLUDE_DIR=$(python3 -c "from sysconfig import get_paths; print(get_paths()['include'])") \
    -D PYTHON3_PACKAGES_PATH=$(python3 -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())") \
    -D BUILD_EXAMPLES=OFF \
    -D INSTALL_PYTHON_EXAMPLES=OFF \
    -D INSTALL_C_EXAMPLES=OFF \
    -D BUILD_opencv_python3=ON ..

# 4. Build (takes 30-60 minutes, uses all CPU cores)
make -j$(nproc)

# 5. Install to user directory
make install

# 6. Update library path
echo 'export LD_LIBRARY_PATH=$HOME/.local/lib:$LD_LIBRARY_PATH' >> ~/.bashrc
echo 'export PKG_CONFIG_PATH=$HOME/.local/lib/pkgconfig:$PKG_CONFIG_PATH' >> ~/.bashrc
source ~/.bashrc

# 7. Link to your Python environment
cd /home/antonkulaga/sources/video2slides
source .venv/bin/activate
ln -s $HOME/.local/lib/python3.*/site-packages/cv2 .venv/lib/python3.*/site-packages/

# 8. Verify
python -c "import cv2; print('OpenCV:', cv2.__version__); print('CUDA devices:', cv2.cuda.getCudaEnabledDeviceCount())"
```

### Option 4: Docker with CUDA-enabled OpenCV

Create a `Dockerfile.gpu` in your project:

```dockerfile
FROM nvidia/cuda:12.6.0-runtime-ubuntu24.04

# Install Python and system dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    libopencv-dev \
    && rm -rf /var/lib/apt/lists/*

# Install OpenCV with CUDA from conda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    /opt/conda/bin/conda install -y -c conda-forge opencv && \
    /opt/conda/bin/conda clean -a

ENV PATH="/opt/conda/bin:$PATH"

# Copy and install video2slides
COPY . /app
WORKDIR /app
RUN pip install -e .

CMD ["video2slides"]
```

Build and run:

```bash
docker build -t video2slides-gpu -f Dockerfile.gpu .
docker run --gpus all -v $(pwd):/data video2slides-gpu convert /data/video.mp4
```

## Verification

After any installation method, verify GPU support:

```bash
cd /home/antonkulaga/sources/video2slides
uv run python -c "
import cv2
print('OpenCV version:', cv2.__version__)
print('CUDA module available:', hasattr(cv2, 'cuda'))
if hasattr(cv2, 'cuda'):
    device_count = cv2.cuda.getCudaEnabledDeviceCount()
    print('CUDA devices detected:', device_count)
    if device_count > 0:
        print('✅ GPU acceleration: ENABLED')
        print('GPU 0:', cv2.cuda.printCudaDeviceInfo(0))
    else:
        print('❌ GPU acceleration: DISABLED (OpenCV has CUDA module but found 0 devices)')
else:
    print('❌ GPU acceleration: DISABLED (OpenCV built without CUDA support)')
"
```

## Expected Performance with RTX 4090

Once GPU acceleration is working:
- **3-10x faster** frame extraction
- **5-15x faster** for 4K videos
- GPU memory usage: ~500MB - 2GB depending on video resolution
- Best for: High-resolution videos (1080p, 4K, 8K)
- Minimal benefit for: Low-res videos (480p, 720p) - CPU is often fast enough

## Usage After Setup

```bash
# Default - GPU auto-detected and used
uv run video2slides convert video.mp4

# Force CPU (useful for testing/debugging)
uv run video2slides convert video.mp4 --no-gpu

# Check GPU status in output
uv run video2slides convert video.mp4 --verbose
```

## Why This Is Hard

1. **CUDA Toolkit Size**: CUDA adds ~5GB to package size
2. **Platform Specific**: Different CUDA versions for different GPUs  
3. **Build Complexity**: OpenCV + CUDA requires ~30-60 min to compile
4. **Licensing**: Distribution restrictions on pre-built binaries

This is why **conda-forge** is the recommended solution - they handle all the complexity!

## Quick Recommendation for Your RTX 4090

**Use conda/mamba** (Option 1). It's the easiest path to get CUDA-enabled OpenCV:

```bash
mamba create -n video2slides-gpu python=3.11 opencv -c conda-forge
mamba activate video2slides-gpu
cd /home/antonkulaga/sources/video2slides
uv sync
# Verify: should now show "⚡ GPU acceleration: Enabled (CUDA)"
uv run video2slides convert test_data/*.mp4
```
