"""
A* 路径规划节点（ROS2）。

功能：
- 订阅地图、起点、终点；
- 将 ROS2 消息转换为 A* 可用数据；
- 调用 a_star_core.AStarPlanner 输出路径；
- 发布 nav_msgs/Path。
"""

from __future__ import annotations

from typing import List, Optional, Tuple

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy

from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from nav_msgs.msg import OccupancyGrid, Path

from a_star_core import AStarPlanner


class AStarPlannerNode(Node):
    """
    A* 规划 ROS2 节点。

    重要参数：
    - robot_radius        : 机器人半径（影响障碍膨胀）
    - occupied_threshold  : >= 该阈值视为障碍
    - unknown_as_occupied : 地图未知区域是否当作障碍
    - force_boundary_walls: 是否强制将地图边界视为障碍
    - anchor_map_bounds   : 是否添加“边界锚点”保证 A* 地图边界正确
    - use_cell_center     : 发布路径时是否使用“栅格中心”
    - replan_on_map_update: 地图更新时是否重新规划（默认 False）
    """

    def __init__(self) -> None:
        super().__init__("a_star_planner_node")

        # 参数声明
        self.declare_parameter("robot_radius", 0.0)
        self.declare_parameter("occupied_threshold", 50)
        self.declare_parameter("unknown_as_occupied", True)
        self.declare_parameter("force_boundary_walls", True)
        self.declare_parameter("anchor_map_bounds", True)
        self.declare_parameter("use_cell_center", False)
        self.declare_parameter("replan_on_map_update", False)

        # 读取参数
        self._robot_radius = self.get_parameter("robot_radius").get_parameter_value().double_value
        self._occupied_threshold = int(
            self.get_parameter("occupied_threshold").get_parameter_value().integer_value
        )
        self._unknown_as_occupied = (
            self.get_parameter("unknown_as_occupied").get_parameter_value().bool_value
        )
        self._force_boundary_walls = (
            self.get_parameter("force_boundary_walls").get_parameter_value().bool_value
        )
        self._anchor_map_bounds = (
            self.get_parameter("anchor_map_bounds").get_parameter_value().bool_value
        )
        self._use_cell_center = self.get_parameter("use_cell_center").get_parameter_value().bool_value
        self._replan_on_map_update = (
            self.get_parameter("replan_on_map_update").get_parameter_value().bool_value
        )

        # 订阅地图：使用 Transient Local 以拿到 latched 地图
        map_qos = QoSProfile(
            depth=1,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            reliability=ReliabilityPolicy.RELIABLE,
        )
        self._map_sub = self.create_subscription(OccupancyGrid, "map", self._on_map, map_qos)

        # 起点 / 终点订阅
        self._start_sub = self.create_subscription(PoseStamped, "start", self._on_start, 10)
        self._initialpose_sub = self.create_subscription(
            PoseWithCovarianceStamped, "initialpose", self._on_initialpose, 10
        )
        self._goal_sub = self.create_subscription(PoseStamped, "goal", self._on_goal, 10)

        # 路径发布
        self._path_pub = self.create_publisher(Path, "path", 10)

        # 内部状态
        self._map_msg: Optional[OccupancyGrid] = None
        self._start_msg: Optional[PoseStamped] = None
        self._goal_msg: Optional[PoseStamped] = None

        # 是否需要重新规划
        self._need_plan = False

        self.get_logger().info("A* planner node started.")

    # ------------------------ ROS2 回调部分 ------------------------ #
    def _on_map(self, msg: OccupancyGrid) -> None:
        """
        地图回调。
        """

        # 首次收到地图时触发规划
        first_time = self._map_msg is None
        self._map_msg = msg

        if first_time or self._replan_on_map_update:
            self._need_plan = True
            self._try_plan()

    def _on_start(self, msg: PoseStamped) -> None:
        """
        起点回调。
        """
        self._set_start(msg)

    def _on_initialpose(self, msg: PoseWithCovarianceStamped) -> None:
        """
        RViz 2D Pose Estimate 回调（PoseWithCovarianceStamped）。
        """
        pose_msg = PoseStamped()
        pose_msg.header = msg.header
        pose_msg.pose = msg.pose.pose
        self._set_start(pose_msg)

    def _set_start(self, msg: PoseStamped) -> None:
        """
        统一设置起点并触发规划。
        """
        self._start_msg = msg
        self._need_plan = True
        self._try_plan()

    def _on_goal(self, msg: PoseStamped) -> None:
        """
        终点回调。
        """

        self._goal_msg = msg
        self._need_plan = True
        self._try_plan()

    # ------------------------ 核心规划逻辑 ------------------------ #
    def _try_plan(self) -> None:
        """
        若条件满足则执行规划。
        """

        if not self._need_plan:
            return
        if self._map_msg is None or self._start_msg is None or self._goal_msg is None:
            return

        self._need_plan = False  # 避免重复触发

        # 提取起终点
        sx = float(self._start_msg.pose.position.x)
        sy = float(self._start_msg.pose.position.y)
        gx = float(self._goal_msg.pose.position.x)
        gy = float(self._goal_msg.pose.position.y)

        # 检查起终点是否在地图内
        if not self._pose_in_map(sx, sy) or not self._pose_in_map(gx, gy):
            self.get_logger().warn("起点或终点超出地图范围，无法规划。")
            self._publish_empty_path()
            return

        # 检查起终点是否落在障碍上
        if self._pose_is_occupied(sx, sy):
            self.get_logger().warn("起点在障碍物上，无法规划。")
            self._publish_empty_path()
            return
        if self._pose_is_occupied(gx, gy):
            self.get_logger().warn("终点在障碍物上，无法规划。")
            self._publish_empty_path()
            return

        # 由 OccupancyGrid 转换障碍物点列表
        ox, oy = self._occupancy_to_obstacles(self._map_msg)

        # 调用 A* 核心
        resolution = float(self._map_msg.info.resolution)
        planner = AStarPlanner(ox, oy, resolution, self._robot_radius)
        rx, ry = planner.planning(sx, sy, gx, gy)

        # 判断是否真正找到路径
        if not self._path_is_valid(rx, ry, sx, sy, gx, gy, resolution):
            self.get_logger().warn("未找到有效路径。")
            self._publish_empty_path()
            return

        # A* 返回的是“终点 -> 起点”，需要反转
        rx = list(reversed(rx))
        ry = list(reversed(ry))

        # 发布路径
        path_msg = self._build_path_msg(rx, ry)
        self._path_pub.publish(path_msg)
        self.get_logger().info(f"规划成功，路径长度：{len(path_msg.poses)}")

    # ------------------------ 工具函数 ------------------------ #
    def _pose_in_map(self, x: float, y: float) -> bool:
        """
        判断一个世界坐标是否在地图边界内。
        """

        info = self._map_msg.info
        origin_x = info.origin.position.x
        origin_y = info.origin.position.y
        max_x = origin_x + info.width * info.resolution
        max_y = origin_y + info.height * info.resolution
        return origin_x <= x < max_x and origin_y <= y < max_y

    def _pose_is_occupied(self, x: float, y: float) -> bool:
        """
        判断一个世界坐标是否落在障碍物上。

        说明：
        - 使用 round 将世界坐标映射到栅格索引；
        - 未知区域可配置为“占用”或“空闲”。
        """

        info = self._map_msg.info
        origin_x = info.origin.position.x
        origin_y = info.origin.position.y
        res = info.resolution

        ix = int(round((x - origin_x) / res))
        iy = int(round((y - origin_y) / res))

        if ix < 0 or iy < 0 or ix >= info.width or iy >= info.height:
            return True

        value = self._map_msg.data[iy * info.width + ix]
        if value < 0:
            return self._unknown_as_occupied
        return value >= self._occupied_threshold

    def _occupancy_to_obstacles(self, msg: OccupancyGrid) -> Tuple[List[float], List[float]]:
        """
        将 OccupancyGrid 转换为障碍物点列表（ox, oy）。

        关键点：
        - 使用栅格左下角坐标（与 A* 内部的 calc_grid_position 对齐）；
        - 可选强制边界墙，防止路径越界；
        - 可选边界锚点，确保 A* 通过障碍推断到正确边界。
        """

        info = msg.info
        res = info.resolution
        origin_x = info.origin.position.x
        origin_y = info.origin.position.y

        ox: List[float] = []
        oy: List[float] = []

        # 遍历全部栅格，提取障碍点
        for y in range(info.height):
            base = y * info.width
            for x in range(info.width):
                value = msg.data[base + x]
                if value < 0 and self._unknown_as_occupied:
                    is_occ = True
                else:
                    is_occ = value >= self._occupied_threshold
                if is_occ:
                    # 使用“格子左下角坐标”
                    ox.append(origin_x + x * res)
                    oy.append(origin_y + y * res)

        # 强制边界墙：确保地图外围不可通行
        if self._force_boundary_walls:
            for x in range(info.width):
                ox.append(origin_x + x * res)
                oy.append(origin_y)
                ox.append(origin_x + x * res)
                oy.append(origin_y + (info.height - 1) * res)
            for y in range(info.height):
                ox.append(origin_x)
                oy.append(origin_y + y * res)
                ox.append(origin_x + (info.width - 1) * res)
                oy.append(origin_y + y * res)

        # 边界锚点：用于让 A* 正确推断地图边界
        if self._anchor_map_bounds:
            ox.extend(
                [
                    origin_x,
                    origin_x + info.width * res,
                    origin_x,
                    origin_x + info.width * res,
                ]
            )
            oy.extend(
                [
                    origin_y,
                    origin_y,
                    origin_y + info.height * res,
                    origin_y + info.height * res,
                ]
            )

        return ox, oy

    def _path_is_valid(
        self,
        rx: List[float],
        ry: List[float],
        sx: float,
        sy: float,
        gx: float,
        gy: float,
        resolution: float,
    ) -> bool:
        """
        简单校验路径是否有效。

        思路：
        - A* 默认返回 “终点 -> 起点”；
        - 首尾是否接近目标点，用分辨率做容差；
        - 若长度为 1，则必须是 start == goal 才算成功。
        """

        if len(rx) == 0 or len(ry) == 0:
            return False

        tol = resolution * 0.5

        # rx[0], ry[0] 应接近 goal
        goal_ok = abs(rx[0] - gx) <= tol and abs(ry[0] - gy) <= tol
        # rx[-1], ry[-1] 应接近 start
        start_ok = abs(rx[-1] - sx) <= tol and abs(ry[-1] - sy) <= tol

        return goal_ok and start_ok

    def _build_path_msg(self, rx: List[float], ry: List[float]) -> Path:
        """
        将路径点转换为 nav_msgs/Path。
        """

        msg = Path()
        msg.header.frame_id = self._map_msg.header.frame_id or "map"
        msg.header.stamp = self.get_clock().now().to_msg()

        # 可选将点移动到栅格中心
        res = float(self._map_msg.info.resolution)
        center_offset = 0.5 * res if self._use_cell_center else 0.0

        for x, y in zip(rx, ry):
            pose = PoseStamped()
            pose.header = msg.header
            pose.pose.position.x = x + center_offset
            pose.pose.position.y = y + center_offset
            pose.pose.position.z = 0.0
            pose.pose.orientation.w = 1.0  # 朝向不做规划
            msg.poses.append(pose)

        return msg

    def _publish_empty_path(self) -> None:
        """
        发布空路径（表示规划失败）。
        """

        msg = Path()
        msg.header.frame_id = self._map_msg.header.frame_id if self._map_msg else "map"
        msg.header.stamp = self.get_clock().now().to_msg()
        self._path_pub.publish(msg)


def main() -> None:
    """
    ROS2 节点入口。
    """

    rclpy.init()
    node = AStarPlannerNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

