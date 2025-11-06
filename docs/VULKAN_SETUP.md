# Building OpenCV with Vulkan Support for RTX 4090

## Prerequisites

Your RTX 4090 already has Vulkan support! Check:

```bash
# Check Vulkan is available
vulkaninfo | grep "deviceName"
# Should show: NVIDIA GeForce RTX 4090 Laptop GPU
```

If `vulkaninfo` is not found:

```bash
sudo apt-get update
sudo apt-get install -y vulkan-tools vulkan-utils
```

## Install Vulkan SDK

```bash
# Download Vulkan SDK
wget -qO - https://packages.lunarg.com/lunarg-signing-key-pub.asc | sudo apt-key add -
sudo wget -qO /etc/apt/sources.list.d/lunarg-vulkan-jammy.list \
    https://packages.lunarg.com/vulkan/lunarg-vulkan-jammy.list

# Install Vulkan development files
sudo apt-get update
sudo apt-get install -y vulkan-sdk
```

## Build OpenCV with Both CUDA and Vulkan

Why not enable BOTH? Your RTX 4090 supports both!

```bash
# 1. Install all dependencies
sudo apt-get update
sudo apt-get install -y \
    build-essential cmake git pkg-config \
    libjpeg-dev libtiff-dev libpng-dev \
    libavcodec-dev libavformat-dev libswscale-dev libv4l-dev \
    libxvidcore-dev libx264-dev \
    libatlas-base-dev gfortran \
    python3-dev python3-numpy \
    vulkan-sdk

# 2. Clone OpenCV
cd ~
git clone https://github.com/opencv/opencv.git
git clone https://github.com/opencv/opencv_contrib.git
cd opencv
git checkout 4.12.0
cd ../opencv_contrib
git checkout 4.12.0
cd ../opencv

# 3. Configure with BOTH CUDA and Vulkan
mkdir build && cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=$HOME/.local \
    -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \
    \
    -D WITH_CUDA=ON \
    -D CUDA_ARCH_BIN=8.9 \
    -D CUDA_ARCH_PTX=8.9 \
    -D WITH_CUDNN=ON \
    -D OPENCV_DNN_CUDA=ON \
    -D ENABLE_FAST_MATH=ON \
    -D CUDA_FAST_MATH=ON \
    -D WITH_CUBLAS=ON \
    \
    -D WITH_VULKAN=ON \
    -D VULKAN_INCLUDE_DIR=/usr/include \
    -D VULKAN_LIBRARY=/usr/lib/x86_64-linux-gnu/libvulkan.so \
    \
    -D WITH_TBB=ON \
    -D WITH_V4L=ON \
    -D WITH_QT=OFF \
    -D WITH_GTK=ON \
    -D WITH_OPENGL=ON \
    -D PYTHON3_EXECUTABLE=$(which python3) \
    -D BUILD_EXAMPLES=OFF \
    -D BUILD_opencv_python3=ON ..

# 4. Verify configuration shows both CUDA and Vulkan
# Look for:
#   CUDA:                        YES (ver X.X)
#   Vulkan:                      YES

# 5. Build (30-60 minutes)
make -j$(nproc)

# 6. Install
make install
echo 'export LD_LIBRARY_PATH=$HOME/.local/lib:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc

# 7. Link to your venv
cd /home/antonkulaga/sources/video2slides
source .venv/bin/activate
ln -s $HOME/.local/lib/python3.*/site-packages/cv2 .venv/lib/python3.*/site-packages/

# 8. Verify both work
python -c "
import cv2
print('OpenCV:', cv2.__version__)
print('CUDA devices:', cv2.cuda.getCudaEnabledDeviceCount())
# Vulkan check is more indirect - check build info
print('Build info:')
print(cv2.getBuildInformation())
"
```

## Vulkan vs CUDA in OpenCV Code

Note: OpenCV's Vulkan support is less mature than CUDA. Not all operations have Vulkan backends.

**CUDA** (used in video2slides):
- `cv2.cuda.cvtColor()` - ✅ Well supported
- `cv2.cuda.resize()` - ✅ Well supported
- Many more operations

**Vulkan** (OpenCV 4.x):
- Mostly used for rendering/display
- Fewer compute operations than CUDA
- Better for cross-platform compatibility

## Recommendation for Your RTX 4090

Since you have an NVIDIA GPU, I recommend:

### Quick path: **Use conda with CUDA** (5 minutes)

```bash
mamba create -n video2slides-gpu python=3.11 opencv -c conda-forge
mamba activate video2slides-gpu
cd /home/antonkulaga/sources/video2slides
uv sync
```

This gives you CUDA support immediately!

### Long path: **Build with both CUDA + Vulkan** (1 hour)

Only if you:
- Want maximum control
- Need cross-platform code (AMD/Intel GPUs later)
- Want both backends available

## Why CUDA over Vulkan for your use case?

For `video2slides` specifically:
1. ✅ **Better OpenCV support** - More operations accelerated
2. ✅ **Pre-built option** - conda-forge has it
3. ✅ **Mature** - Well-tested in OpenCV
4. ✅ **Your GPU is NVIDIA** - CUDA is native

Vulkan would be better if:
- ❌ You needed AMD/Intel GPU support
- ❌ Pre-built wheels existed (they don't)
- ❌ OpenCV had more Vulkan ops (it doesn't yet)

## Bottom Line

For your RTX 4090 with `video2slides`:
- **Use CUDA via conda** - easiest and best performance
- **Vulkan** - not worth it unless you need cross-platform support
- **Both** - only if you're building from source anyway and want options

The conda route gets you GPU acceleration in 5 minutes vs 1 hour building from source!

