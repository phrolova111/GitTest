# 导航任务

![A* 在二维栅格地图中连接起终点并绕开障碍物的示意图](../../assets/tasks/navigation-astar-v2.png)

*任务示意图，非实际运行结果。*

本任务要求在二维栅格地图上实现 A* 路径规划，根据起点和目标点找到一条避开障碍物的路径，并在 RViz2 中展示结果。

项目提供：

- `src/a_star_core/`：Python A* 算法模板，包含待完成的 `TODO(student)`。
- `src/a_star_ros2/`：二维地图、地图发布与路径规划节点，以及启动和 RViz2 配置。
- `install_deps.py`：工作空间依赖安装脚本。

需分别使用 **Python 和 C++** 完成任务。Python 需补全算法模板；C++ 需自行实现算法和 ROS2 规划节点，可复用已有地图和 RViz2 配置。两种实现按相同的路径结果验收。

使用 Ubuntu 22.04 和 ROS2 Humble，环境准备见[环境准备](../../ENV_SETUP.md)。完成算法后，可在 RViz2 中设置起点和目标点，观察路径规划结果。

## 任务要求

实现以下三个功能。Python 模板位于 `src/a_star_core/a_star_core/a_star_planner.py`，请保留函数参数和返回值；C++ 可自行组织代码。

### 1. A* 搜索：`planning()`

- 将输入的起点和目标点世界坐标转换为栅格节点。
- 使用待扩展集合和已扩展集合，每次选择 `f = g + h` 最小的节点。`g` 是起点到当前节点的累计代价，`h` 是到目标的估计代价。
- 按八邻域扩展节点：直移代价为 `1`，斜移代价为 `sqrt(2)`；排除越界、碰撞和已扩展的节点。
- 发现更短路径时更新节点代价和前驱；到达目标后记录前驱并回溯路径，无路可达时返回空路径。

Python 模板已提供坐标转换、移动模型和 `verify_node()`。待扩展集合和已扩展集合分别为 `open_set` 和 `closed_set`，使用 `calc_grid_index()` 的结果作为键。

### 2. 路径回溯：`calc_final_path()`

从目标沿前驱回溯到起点，并将栅格索引转换为世界坐标。Python 模板使用 `parent_index` 和 `closed_set`，起点的前驱为 `-1`；可调用 `calc_grid_position()` 转换坐标。函数返回等长的 `rx`、`ry` 列表，顺序为 **目标点 → 起点**，已有节点会反转后发布。C++ 可直接生成 **起点 → 目标点** 的路径。

### 3. 启发式代价：`calc_heuristic()`

接收两个栅格节点，返回估计代价 `h`。可使用欧氏距离或对角距离，代价尺度须与移动模型一致。若要保持最短路径性质，估计值不能高于实际剩余代价；八邻域下不能直接使用四邻域曼哈顿距离。

## 地图与话题

默认地图为 `room_simple`，还提供 `corridor_zigzag` 和 `grid_maze`。单独启动地图节点时，可通过 `map_id` 参数切换地图；启动文件使用固定的默认地图。

| 数据 | 话题 | 消息类型 |
| --- | --- | --- |
| 地图 | `/map` | `nav_msgs/msg/OccupancyGrid` |
| RViz2 起点 | `/initialpose` | `geometry_msgs/msg/PoseWithCovarianceStamped` |
| 另一种起点输入 | `/start` | `geometry_msgs/msg/PoseStamped` |
| 目标点 | `/goal` | `geometry_msgs/msg/PoseStamped` |
| 路径 | `/path` | `nav_msgs/msg/Path` |

起终点使用 `map` 坐标系。地图边界和未知区域按障碍处理；默认机器人半径为 `0.0`，即按点机器人演示。已有 Python 节点收到地图和起终点后调用算法，起终点变化时重新规划；起终点无效或无路可达时发布空路径。

## C++ 实现

在 `task/Navigation/src/` 下创建 `ament_cmake` 包，实现 C++ A* 算法和 ROS2 规划节点。节点需：

- 使用兼容 Transient Local 的 QoS 订阅 `/map`，并订阅 `/initialpose`、`/start` 和 `/goal`。
- 根据地图原点、分辨率、宽高和栅格数据处理坐标与障碍物；未知区域和边界按障碍处理。
- 按上述八邻域代价实现搜索和回溯。向 `/path` 发布 `nav_msgs/msg/Path`，`header.frame_id` 为 `map`，路径按起点到目标点排列。起终点变化时重新规划，无效或无路可达时发布空路径。
- 提供 `package.xml`、`CMakeLists.txt` 和运行说明，保证在 Ubuntu 22.04 + ROS2 Humble 下可构建、运行和验证。

运行 C++ 规划节点时不要同时启动 Python 规划节点，否则两个节点都会发布 `/path`。

## 提交要求

- 沿用 `task/Navigation/` 的项目结构，提交算法和 ROS2 节点源码、依赖与构建配置，以及运行所需的地图、启动和 RViz2 配置。C++ 功能包放在 `src/` 下。
- 提交 README，说明环境、构建与运行方法、算法思路、实际结果和未完成项。引用开源代码时注明来源并保留许可证声明。
- 分别提交 Python 和 C++ 的演示材料，展示地图、起终点、绕障路径和更换目标后的重新规划。路径应连接起终点，相邻节点符合八邻域移动模型；起终点相同时返回该位置，起终点无效或无路可达时发布空路径并结束搜索。较大文件可提供下载链接。
- 提供姓名或昵称、仓库链接、分支和提交号。使用 `.gitignore` 排除构建产物、日志和缓存，并确认他人能按 README 复现结果。

## 学习资料

建议先学习 A*，再了解 ROS2 消息和坐标系，最后阅读完整导航系统。后两项适合完成任务后进阶学习。

1. [Red Blob Games：A* 交互教程](https://www.redblobgames.com/pathfinding/a-star/introduction.html)：理解搜索、回溯和启发式。
2. [ROS2 Humble 官方教程](https://docs.ros.org/en/humble/Tutorials.html)（[源码](https://github.com/ros2/ros2_documentation/blob/humble/source/Tutorials.rst)）：学习工作空间、节点、话题和发布订阅。
3. [OccupancyGrid 消息定义](https://github.com/ros2/common_interfaces/blob/humble/nav_msgs/msg/OccupancyGrid.msg)：理解地图数据和坐标转换。
4. [Path 消息定义](https://github.com/ros2/common_interfaces/blob/humble/nav_msgs/msg/Path.msg)：理解路径消息。
5. [tf2 官方教程](https://docs.ros.org/en/humble/Tutorials/Intermediate/Tf2/Tf2-Main.html)（[源码](https://github.com/ros2/ros2_documentation/blob/humble/source/Tutorials/Intermediate/Tf2/Tf2-Main.rst)）：理解坐标系与变换。
6. [Nav2 Humble 项目说明](https://github.com/ros-navigation/navigation2/blob/humble/README.md)：了解导航系统的组成。
7. [PythonRobotics 路径规划算法](https://atsushisakai.github.io/PythonRobotics/modules/5_path_planning/path_planning.html)：对比其他规划算法。
8. [Nav2 规划器接口](https://github.com/ros-navigation/navigation2/blob/humble/nav2_core/include/nav2_core/global_planner.hpp)和 [NavFn 实现](https://github.com/ros-navigation/navigation2/blob/humble/nav2_navfn_planner/src/navfn_planner.cpp)：了解规划器接口和实现。
