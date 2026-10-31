# 学习资料与路径

建议按[目标识别](task/Recognition/README.md) → [ROS](task/ROS/README.md) → [自瞄](task/Aiming/README.md) 或 [导航](task/Navigation/README.md)的路线完成任务：先完成目标识别任务，熟悉模型训练与测试；再学习 ROS2 节点和话题；最后选择自瞄或导航方向。各板块的学习资料也可按任务需要查阅。

**环境要求**：默认使用 **Ubuntu 22.04**。ROS、自瞄、导航任务使用 **ROS2 Humble**；目标识别使用独立的 **Python + PyTorch** 环境。安装与运行说明见[环境准备](ENV_SETUP.md)及对应任务说明。

## 基础资料

各方向先学习 Python 与 Linux；C++ / CMake、ROS2 按任务需要学习，目标识别任务不要求这些内容。

| 顺序 | 学习链接 |
| --- | --- |
| 1. Python | [Python 3.10 官方教程](https://docs.python.org/3.10/tutorial/) → [数据结构](https://docs.python.org/3.10/tutorial/datastructures.html) → [流程控制与函数](https://docs.python.org/3.10/tutorial/controlflow.html) |
| 2. Linux | [Ubuntu 命令行入门](https://ubuntu.com/tutorials/command-line-for-beginners) → [GNU Bash 手册](https://www.gnu.org/software/bash/manual/)；远程开发可看 [OpenSSH 手册](https://www.openssh.com/manual.html) |
| 3. C++ / CMake | [C++ 入门短视频](https://www.bilibili.com/video/BV16Me2zAE4s/) → [Learn C++ 教程](https://www.learncpp.com/) → [CMake 3.22 官方教程](https://cmake.org/cmake/help/v3.22/guide/tutorial/index.html) |
| 4. ROS2 | [动手学 ROS2 中文教程](https://fishros.com/d2lros2/#/) → [ROS2 官方教程（Humble 示例）](https://docs.ros.org/en/humble/Tutorials.html) |

## ROS2 学习

以 **ROS2** 为学习主体，官方教程使用 **Humble** 作为示例版本；本仓库任务的环境要求见[环境准备](ENV_SETUP.md)。视频可参考[机器人工匠阿杰的 ROS2 入门与实践](https://space.bilibili.com/411541289/channel/collectiondetail?sid=1728432)，更多系列见[账号主页](https://space.bilibili.com/411541289)。

该账号的 [ROS 快速入门教程](https://space.bilibili.com/411541289/channel/collectiondetail?sid=693700)为 ROS1 内容，可辅助理解节点、话题和消息；安装、构建命令及节点接口应按 ROS2 教程实践。

按“工作空间与功能包 → 发布与订阅 → 图像处理 → Launch 与话题验证”学习：

1. 按上表的 ROS2 教程学习创建工作空间与功能包，用 Python 或 C++ 完成发布者、订阅者练习，理解节点、话题和消息类型。
2. 学习 OpenCV 的图像创建、BGR / HSV 颜色空间、阈值分割和轮廓中心计算，再用 `cv_bridge` 连接 OpenCV 图像与 ROS2 图像消息。
3. 学习 Launch 文件和 `ros2 topic` 命令，完成[本仓库 ROS 作业](task/ROS/README.md)，核对图像发布频率及目标坐标随图像变化的结果。

## 自瞄方向

按“视频读写 → 图像处理 → ROS2 图像话题 → 检测与保存”学习：

1. 用 [OpenCV 视频读写教程](https://docs.opencv.org/4.x/dd/d43/tutorial_py_video_display.html)学习逐帧读取与保存；C++ 实现可查 [OpenCV C++ 教程](https://docs.opencv.org/4.x/d9/df8/tutorial_root.html)和[视频写入教程](https://docs.opencv.org/4.x/d7/d9e/tutorial_video_write.html)。
2. 用 [OpenCV Canny 边缘检测教程](https://docs.opencv.org/4.x/da/d5c/tutorial_canny_detector.html)练习图像处理，再结合上表的 ROS2 教程理解图像话题的发布与订阅。
3. 完成[本仓库自瞄任务](task/Aiming/README.md)的机器人检测及两路视频保存；追踪、弹道预测与云台控制可在完成当前任务后再学习。

## 导航方向

按“图搜索与坐标 → A* 路径规划 → ROS2 地图与路径 → 导航系统进阶”学习：

1. 先读 [Red Blob Games 的 A* 图解](https://www.redblobgames.com/pathfinding/a-star/introduction.html)，理解启发式、开放/关闭集合和路径回溯，再按[本仓库导航任务](task/Navigation/README.md)选择 Python 或 C++ 实现 A*。
2. 阅读 [`OccupancyGrid` 消息定义](https://github.com/ros2/common_interfaces/blob/humble/nav_msgs/msg/OccupancyGrid.msg)、[`Path` 消息定义](https://github.com/ros2/common_interfaces/blob/humble/nav_msgs/msg/Path.msg)和 [tf2 官方教程](https://docs.ros.org/en/humble/Tutorials/Intermediate/Tf2/Tf2-Main.html)，在 ROS2 演示中检查地图坐标系、起终点与路径。
3. 完成 A* 后阅读 [Nav2 Humble 项目说明](https://github.com/ros-navigation/navigation2/blob/humble/README.md)，了解定位、规划与控制如何组成完整导航系统；本仓库目前不要求实现完整导航栈。

## 目标识别方向

按“张量与梯度 → 神经网络 → CNN → 数据加载与训练 → 评估与预测”学习，教程中的代码选择 **PyTorch** 版本：

1. 阅读 [PyTorch 基础教程](https://docs.pytorch.org/tutorials/beginner/basics/intro.html)，依次练习 Tensor、Dataset / DataLoader、模型定义、自动微分、参数优化和模型保存与加载，理解一次训练迭代中数据与梯度的流向。
2. 阅读《动手学深度学习》的[多层感知机](https://zh.d2l.ai/chapter_multilayer-perceptrons/index.html)，重点理解激活函数、前向与反向传播、训练集与验证集、欠拟合和过拟合；尝试解释训练损失下降而验证效果变差的原因。
3. 学习[卷积神经网络](https://zh.d2l.ai/chapter_convolutional-neural-networks/index.html)，理解卷积、通道、步幅、填充、池化与分类层，并能说明自己网络各层的输入输出形状。
4. 参考 [PyTorch 图像分类训练教程](https://docs.pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html)，使用 CIFAR-10 练习数据加载、CNN 训练与测试，再完成[本仓库目标识别任务](task/Recognition/README.md)，提交自己的实现与测试结果。

[返回仓库入口](README.md)
