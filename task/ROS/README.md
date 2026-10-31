# ROS 作业：模拟目标检测与节点通信

![ROS2 蓝色圆检测与三个节点通信示意图](../../assets/tasks/ros-node-flow-v2.png)

*任务流程示意图，非实际运行结果。*

使用 **Ubuntu 22.04 + ROS2 Humble**，选择 **Python 或 C++**，创建名为 `rm_vision_sim` 的功能包，包含以下三个节点。

## 1. 节点功能

### `camera_node`：图像发布者

- 使用 OpenCV 创建 640×480 像素的黑色背景图像，无需真实摄像头。
- 绘制半径为 20 像素的蓝色实心圆，使其在图像范围内随机缓慢移动。
- 以 10 Hz 向 `/image_raw` 发布图像，消息类型为 `sensor_msgs/msg/Image`。

### `detector_node`：目标检测器

- 订阅 `/image_raw`，接收 `sensor_msgs/msg/Image` 图像。
- 使用 OpenCV 将 BGR 图像转换为 HSV，通过颜色阈值分割找出蓝色区域，并计算其轮廓的几何中心。
- 向 `/target_position` 发布 `geometry_msgs/msg/PointStamped` 消息，将中心的像素坐标填入 `point.x`、`point.y`，并填写 `header` 中的时间戳。

### `logger_node`：日志记录器

- 订阅 `/target_position`，接收 `geometry_msgs/msg/PointStamped` 消息。
- 每收到一条消息，在终端打印目标坐标，例如：`Target detected at: [x=320.5, y=240.1]`。

## 2. 启动与测试

- 编写 `tracking_sim.launch.py`，一次启动上述三个节点。
- 提供 `test.sh` 或带 `test` 目标的 `Makefile`，完成 `colcon build`、加载环境和 `ros2 launch rm_vision_sim tracking_sim.launch.py`。运行时应能看到日志节点持续打印坐标。
- 在 README 中写明环境配置、构建和运行方法，以及手动验证步骤。系统启动后，应能在加载了 ROS2 和工作空间环境的新终端中执行以下命令，查看目标位置：

```bash
ros2 topic echo /target_position
```

## 作业效果

运行后，应能观察到以下结果：

- **图像内容**：查看 `/image_raw` 图像时，能看到 640×480 的黑色画面中有一个蓝色实心圆，蓝圆在画面内缓慢移动。
- **坐标输出**：终端持续打印检测到的圆心坐标，明确标出 `x`、`y`，单位为像素。坐标以图像左上角为原点，向右 x 增大，向下 y 增大。
- **图像与坐标对应**：蓝圆向右移动时，输出的 x 随之增大；向下移动时，y 随之增大。例如圆心在画面中央附近时，检测坐标应接近 `(320, 240)`。日志中的坐标应来自实际检测结果，并随蓝圆位置变化。
- **话题通信**：在另一个已加载环境的终端执行 `ros2 topic echo /target_position`，能持续收到坐标消息，其中 `point.x`、`point.y` 与日志打印的同一条消息对应。

展示测试结果时，可以把蓝圆画面和坐标日志放在同一张截图或一段录屏中，让查看者直接看懂“目标在哪里、程序检测到了什么位置”。

## 思考

如果图像中出现剧烈的光照变化，简单的颜色阈值分割可能会变得不稳定。完成作业后，可以进一步思考原因以及如何提升检测的鲁棒性。

## 代码与目录规范

- 以 `task/ROS/` 为工作空间，功能包放在其 `src/rm_vision_sim/` 下，包含节点源码、包声明、构建配置和 Launch 文件。
- 三个节点分工清楚，关键步骤有必要注释，话题和消息遵循任务要求。
- 依赖和文件路径配置清楚，确保能按 README 构建和启动；引用开源代码时注明来源并保留必要的许可证声明。

## 提交要求

- 提交功能包源码、构建配置、Launch 文件、`test.sh` 或带 `test` 目标的 `Makefile`，以及任务 README。
- README 写明环境、依赖、构建和测试命令及执行目录，展示图像与坐标对应的实际结果，说明未完成项。
- 用 `.gitignore` 排除构建产物、日志、虚拟环境和缓存。Git 提交说明具体改动，提交前按 README 检查能否复现。
- 提交时提供姓名或昵称、仓库链接、分支、提交号和结果材料位置，验收以该版本为准。

环境配置见[环境准备](../../ENV_SETUP.md)，相关教程见[学习资料与路径](../../LEARNING_RESOURCES.md)。

[返回培训考核首页](../../README.md)
