# 环境准备

默认使用 **Ubuntu 22.04** 和 Bash 终端。ROS、自瞄、导航任务按下面的 ROS2 环境准备；目标识别直接按本文的“目标识别：PyTorch 环境”准备，无需安装 ROS2。

## ROS、自瞄与导航：ROS2 环境

使用 **ROS2 Humble** 和系统 Python 3.10。运行 RViz2 需要可用的图形桌面；使用 ROS2 时退出 Conda 等独立 Python 环境，避免混用依赖。

先按 [ROS2 Humble 官方安装说明](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html)安装 ROS2 桌面版。若页面无法访问，可查看[官方文档源码](https://github.com/ros2/ros2_documentation/blob/humble/source/Installation/Ubuntu-Install-Debs.rst)。

已安装 ROS2 后，加载环境并安装作业所需的基础工具：

```bash
source /opt/ros/humble/setup.bash
sudo apt update
sudo apt install git python3-colcon-common-extensions python3-rosdep python3-opencv libopencv-dev ros-humble-cv-bridge cmake g++
```

首次使用 `rosdep` 时执行：

```bash
sudo rosdep init
rosdep update
```

若已初始化，只执行 `rosdep update`。每次打开新终端，都需执行 `source /opt/ros/humble/setup.bash`；构建作业工作空间后，还需加载其 `install/setup.bash`。具体工作空间依赖与运行步骤见各方向任务说明。

## 目标识别：PyTorch 环境

使用独立的 Python 虚拟环境，通过 [PyTorch 官方安装页面](https://pytorch.org/get-started/locally/)选择与 Python 版本、CPU 或 CUDA 环境匹配的 `torch` 和 `torchvision` 安装命令。分类任务使用 Python + PyTorch；`torchvision` 可用于加载数据和图像预处理。CPU 可完成任务，GPU 为可选加速设备。

在任务目录下创建并激活虚拟环境，再执行所选安装命令。记录实际使用的 Python、PyTorch、torchvision 版本、安装命令与运行设备；使用 GPU 时还需记录驱动和 CUDA 相关版本。不要将训练依赖安装到 ROS2 使用的系统 Python 环境中。

安装后在该环境中检查：

```bash
python -c "import torch, torchvision; print('torch:', torch.__version__); print('torchvision:', torchvision.__version__); print('CUDA available:', torch.cuda.is_available())"
```

导入成功只说明基础依赖可用；仍需按[目标识别任务](task/Recognition/README.md)完成实际训练、权重加载与评估验证。

[返回仓库入口](README.md)
