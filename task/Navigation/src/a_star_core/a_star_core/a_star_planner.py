"""
A* 栅格规划算法（纯 Python 版）

设计目标：
1. 尽量复用原始 a_star.py 的算法结构；
2. 不依赖 ROS2，便于在不同上层节点中复用；
3. 代码注释清晰，适合学习与调试。
"""

from __future__ import annotations

import math
from typing import Dict, List, Tuple


class AStarPlanner:
    """
    A* 栅格规划器（二维）。

    注意：
    - 该实现会**根据障碍物坐标自动推断地图边界**。
      因此上层在构造 `ox, oy` 时，应确保边界处也有点
      （或手动添加“边界锚点”），避免地图边界被缩小。
    """

    class Node:
        """
        栅格节点结构，用于 A* 搜索。

        说明：
        - x, y       : 栅格索引（整数）
        - cost       : 从起点到当前节点的累计代价 g(n)
        - parent_idx : 父节点索引，用于回溯路径
        """

        def __init__(self, x: int, y: int, cost: float, parent_idx: int) -> None:
            self.x = x                              # 栅格索引 x
            self.y = y                              # 栅格索引 y
            self.cost = cost                        # 从起点到当前节点的累计代价 g(n)
            self.parent_index = parent_idx          # 父节点索引，用于回溯路径

        def __str__(self) -> str:
            """
            返回节点的字符串表示
            """
            return f"{self.x},{self.y},{self.cost},{self.parent_index}"

    def __init__(self, ox: List[float], oy: List[float], resolution: float, rr: float) -> None:
        """
        初始化 A* 规划器。

        参数：
        - ox, oy     : 障碍物坐标列表（世界坐标系）
        - resolution: 栅格分辨率（米/格）
        - rr        : 机器人半径（用于障碍膨胀）
        """

        self.resolution = resolution                # 栅格分辨率（米/格）
        self.rr = rr                                # 机器人半径（用于障碍膨胀）  
        self.min_x, self.min_y = 0, 0               # 地图边界（由障碍物推断）最小 x 和 y 坐标
        self.max_x, self.max_y = 0, 0               # 最大 x 和 y 坐标
        self.x_width, self.y_width = 0, 0           # 栅格宽高（以“格子数量”为单位）
        self.obstacle_map: List[List[bool]] = []    # 障碍物栅格地图：True 表示有障碍，False 表示可通行
        self.motion = self.get_motion_model()       # 8 邻域移动模型
        self.calc_obstacle_map(ox, oy)              # 根据障碍物生成地图

    def planning(self, sx: float, sy: float, gx: float, gy: float) -> Tuple[List[float], List[float]]:
        """
        执行 A* 路径规划。

        输入：
        - sx, sy : 起点坐标（世界坐标）
        - gx, gy : 终点坐标（世界坐标）

        输出：
        - rx, ry : 规划路径坐标列表

        注意：本实现返回的路径**默认是从终点回溯到起点**。
        上层若需要起点到终点的顺序，请在外部反转列表。
        """

        # 将起终点转换为栅格索引
        start_node = self.Node(
            self.calc_xy_index(sx, self.min_x), # 将起点坐标转换为栅格索引，x坐标
            self.calc_xy_index(sy, self.min_y), # 将起点坐标转换为栅格索引，y坐标
            0.0,                                # 起点到当前节点的累计代价 g(n)
            -1,                                 # 父节点索引，用于回溯路径，-1表示没有父节点
        )
        goal_node = self.Node(
            self.calc_xy_index(gx, self.min_x), # 将终点坐标转换为栅格索引，x坐标
            self.calc_xy_index(gy, self.min_y), # 将终点坐标转换为栅格索引，y坐标
            0.0,                                # 终点到当前节点的累计代价 g(n)
            -1,                                 # 父节点索引，用于回溯路径，-1表示没有父节点
        )

        # open_set：待扩展节点，closed_set：已扩展节点
        open_set: Dict[int, AStarPlanner.Node] = {}                 # 待扩展节点集合，键为栅格索引，值为节点对象
        closed_set: Dict[int, AStarPlanner.Node] = {}               # 已扩展节点集合，键为栅格索引，值为节点对象，初始为空字典（初始化）  
        open_set[self.calc_grid_index(start_node)] = start_node     # 将起点加入 open_set，[]内为键，start_node为值（Node对象）

        # TODO(student): 实现 A* 主循环
        # 建议步骤（伪代码）:
        #   while open_set not empty:
        #       1) 选择 f = g + h 最小的节点作为 current
        #       2) 若 current 为目标节点：记录 parent/cost 后退出循环
        #       3) 将 current 从 open_set 移到 closed_set
        #       4) 扩展 8 邻域（self.motion）
        #           - 生成邻居节点 Node
        #           - 越界/碰撞 -> 跳过 (self.verify_node)
        #           - 若在 closed_set -> 跳过
        #           - 若不在 open_set 或更短路径 -> 更新
        #
        # 提示:
        # - f = g + h，其中 h 可调用 self.calc_heuristic(goal_node, node)
        # - open_set/closed_set 的 key 为 self.calc_grid_index(node)
        # - 搜索失败时可以返回空路径（[], []），或按原实现返回回溯路径
        #
        # 完成后，记得回溯路径并返回:
        #   rx, ry = self.calc_final_path(goal_node, closed_set)
        #   return rx, ry
        raise NotImplementedError(
            "A* 主循环未实现：请完成 planning() 中的 TODO 后再运行。"
        )

    def calc_final_path(self, goal_node: Node, closed_set: Dict[int, Node]) -> Tuple[List[float], List[float]]:
        """
        回溯生成路径。

        从终点开始，沿 parent_index 逐步回溯到起点。
        """

        # TODO(student): 回溯路径
        # 提示:
        # - 从 goal_node 开始，沿 parent_index 回溯到 -1
        # - 使用 self.calc_grid_position(...) 将栅格索引转回世界坐标
        # - closed_set 的 key 是节点索引（calc_grid_index）
        raise NotImplementedError(
            "路径回溯未实现：请完成 calc_final_path() 中的 TODO 后再运行。"
        )

    @staticmethod
    def calc_heuristic(n1: Node, n2: Node) -> float:
        """
        启发式函数 h(n)。

        这里使用欧氏距离，可根据需要替换为：
        - 曼哈顿距离
        - 对角距离
        """

        # TODO(student): 实现启发式函数 h(n)
        # 建议之一（欧氏距离）:
        #   w = 1.0
        #   return w * math.hypot(n1.x - n2.x, n1.y - n2.y)
        #
        # 也可尝试：
        # - 曼哈顿距离: abs(dx) + abs(dy)
        # - 对角距离（Diagonal/Octile）
        raise NotImplementedError(
            "启发式函数未实现：请完成 calc_heuristic() 中的 TODO 后再运行。"
        )

    def calc_grid_position(self, index: int, min_position: float) -> float:
        """
        将栅格索引转换为世界坐标。

        注意：
        - 该实现使用“栅格左下角”坐标，而非中心坐标。
        - 若需要中心坐标，可在外部加 0.5 * resolution。
        """

        return index * self.resolution + min_position

    def calc_xy_index(self, position: float, min_pos: float) -> int:
        """
        将世界坐标转换为栅格索引。
        """

        return round((position - min_pos) / self.resolution)

    def calc_grid_index(self, node: Node) -> int:
        """
        计算节点的唯一索引。

        说明：
        - 该索引只用于在 open/closed set 中做字典键；
        - 与 obstacle_map 的索引无直接关系。
        """

        return (node.y - self.min_y) * self.x_width + (node.x - self.min_x)

    def verify_node(self, node: Node) -> bool:
        """
        检查节点是否可用（边界 + 碰撞）。
        """

        px = self.calc_grid_position(node.x, self.min_x)
        py = self.calc_grid_position(node.y, self.min_y)

        # 边界检查
        if px < self.min_x or py < self.min_y or px >= self.max_x or py >= self.max_y:
            return False

        # 碰撞检查
        if self.obstacle_map[node.x][node.y]:
            return False

        return True

    def calc_obstacle_map(self, ox: List[float], oy: List[float]) -> None:
        """
        根据障碍物坐标生成栅格地图。

        关键点：
        - 地图边界由障碍物的最小/最大坐标推断；
        - 若障碍物不包含边界点，地图范围会被“缩小”。
        """

        self.min_x = round(min(ox))
        self.min_y = round(min(oy))
        self.max_x = round(max(ox))
        self.max_y = round(max(oy))

        self.x_width = round((self.max_x - self.min_x) / self.resolution)
        self.y_width = round((self.max_y - self.min_y) / self.resolution)

        # 初始化障碍栅格
        self.obstacle_map = [[False for _ in range(self.y_width)] for _ in range(self.x_width)]

        # 对每个栅格点，判断是否与障碍物距离 <= rr
        for ix in range(self.x_width):
            x = self.calc_grid_position(ix, self.min_x)
            for iy in range(self.y_width):
                y = self.calc_grid_position(iy, self.min_y)
                for iox, ioy in zip(ox, oy):
                    d = math.hypot(iox - x, ioy - y)
                    if d <= self.rr:
                        self.obstacle_map[ix][iy] = True
                        break

    @staticmethod
    def get_motion_model() -> List[List[float]]:
        """
        8 邻域动作模型（dx, dy, cost）。
        """

        return [
            [1, 0, 1],
            [0, 1, 1],
            [-1, 0, 1],
            [0, -1, 1],
            [-1, -1, math.sqrt(2)],
            [-1, 1, math.sqrt(2)],
            [1, -1, math.sqrt(2)],
            [1, 1, math.sqrt(2)],
        ]

