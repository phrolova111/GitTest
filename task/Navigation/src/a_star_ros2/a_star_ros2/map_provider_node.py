"""
地图环境发布节点（ROS2）。

功能：
- 从内置 map_profiles 中加载二维栅格地图；
- 发布 nav_msgs/OccupancyGrid；
- 采用 Transient Local QoS，保证新订阅者也能收到地图。
"""

from __future__ import annotations

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from nav_msgs.msg import OccupancyGrid

from .map_profiles import get_map


class MapProviderNode(Node):
    """
    地图发布节点。

    参数：
    - map_id         : 内置地图 ID
    - frame_id       : 地图坐标系名称（默认 "map"）
    - publish_period : 发布周期（秒）
    """

    def __init__(self) -> None:
        super().__init__("a_star_map_provider")

        # 读取参数（可在启动时覆盖）
        self.declare_parameter("map_id", "room_simple")
        self.declare_parameter("frame_id", "map")
        self.declare_parameter("publish_period", 1.0)

        map_id = self.get_parameter("map_id").get_parameter_value().string_value
        self._frame_id = self.get_parameter("frame_id").get_parameter_value().string_value
        publish_period = self.get_parameter("publish_period").get_parameter_value().double_value

        # 加载地图配置
        self._map_profile = get_map(map_id)

        # QoS：Transient Local = “类似 latched”
        qos = QoSProfile(
            depth=1,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            reliability=ReliabilityPolicy.RELIABLE,
        )
        self._pub = self.create_publisher(OccupancyGrid, "map", qos)

        # 构建并缓存 map 消息
        self._map_msg = self._build_map_msg()

        # 定时发布（也保证新订阅者能立刻拿到）
        self._timer = self.create_timer(publish_period, self._on_timer)

        # 启动时先发一次
        self._publish_map()
        self.get_logger().info(f"Map provider started. map_id={map_id}")

    def _build_map_msg(self) -> OccupancyGrid:
        """
        将 MapProfile 转换为 OccupancyGrid 消息。
        """

        msg = OccupancyGrid()
        msg.header.frame_id = self._frame_id

        msg.info.resolution = float(self._map_profile.resolution)
        msg.info.width = int(self._map_profile.width)
        msg.info.height = int(self._map_profile.height)
        msg.info.origin.position.x = float(self._map_profile.origin_x)
        msg.info.origin.position.y = float(self._map_profile.origin_y)
        msg.info.origin.position.z = 0.0
        msg.info.origin.orientation.w = 1.0  # 无旋转

        # data 为 row-major 一维数组
        msg.data = list(self._map_profile.data)
        return msg

    def _publish_map(self) -> None:
        """
        更新时间戳并发布地图。
        """

        self._map_msg.header.stamp = self.get_clock().now().to_msg()
        self._pub.publish(self._map_msg)

    def _on_timer(self) -> None:
        """
        定时器回调：周期性发布地图。
        """

        self._publish_map()


def main() -> None:
    """
    ROS2 节点入口。
    """

    rclpy.init()
    node = MapProviderNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

