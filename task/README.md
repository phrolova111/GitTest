# 培训考核任务

## 创建个人考核仓库

在 GitHub 创建自己的私有仓库，将本仓库克隆到本地完成任务，并把代码推送到自己的私有仓库。提交考核时，邀请指导者提供的 GitHub 账号为仓库协作者，并提交仓库链接、任务分支、提交号和结果材料。

## 任务总览

默认使用 **Ubuntu 22.04**。ROS、自瞄和导航任务使用 **ROS2 Humble**；目标识别任务使用独立的 **Python + PyTorch** 环境，无需 ROS2。开始前完成[环境准备](../ENV_SETUP.md)，并按[学习资料与路径](../LEARNING_RESOURCES.md)补足基础。各任务的实现要求、运行方式和验收项见对应说明。

**建议路线：[目标识别](Recognition/README.md) → [ROS](ROS/README.md) → [自瞄](Aiming/README.md) 或 [导航](Navigation/README.md)。**

| 任务 | 基础 | 要完成的内容 |
| --- | --- | --- |
| [目标识别](Recognition/README.md) | Python、神经网络、CNN、PyTorch | 使用 CIFAR-10 训练 PyTorch CNN 分类模型，评估准确率并保存权重 |
| [ROS](ROS/README.md) | Python 或 C++、OpenCV、ROS2 节点与话题 | 生成移动蓝色圆图像，检测并发布中心坐标，通过三个节点完成通信、统一启动与验证 |
| [自瞄](Aiming/README.md) | Python、C++、CMake、OpenCV、ROS2 | 读取与处理视频，发布和订阅图像，检测机器人，保存结果并说明验证方法 |
| [导航](Navigation/README.md) | Python 或 C++、A*、ROS2 地图与路径消息 | 选择 Python 框架或编写 C++ 节点完成 A*，运行 ROS2 演示并验证路径 |

## 提交与验收

- 提交源码、必要的构建配置及各任务要求的结果文件；大文件可提供下载链接。
- README 写明环境、依赖、运行和测试命令、实现思路、测试结果及引用的代码或模型；代码组织和提交格式见对应任务说明。
- 按任务说明复现程序，检查实际输出是否符合要求，并能解释关键实现。
