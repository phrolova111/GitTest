"""
启动示例：地图发布 + A* 规划节点 + RViz2。
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    """
    生成启动描述。
    """

    use_rviz = LaunchConfiguration("use_rviz")
    rviz_config = os.path.join(
        get_package_share_directory("a_star_ros2"), "rviz", "a_star_demo.rviz"
    )

    map_node = Node(
        package="a_star_ros2",
        executable="map_provider_node",
        name="map_provider",
        output="screen",
        parameters=[
            {"map_id": "room_simple"},
            {"frame_id": "map"},
            {"publish_period": 1.0},
        ],
    )

    planner_node = Node(
        package="a_star_ros2",
        executable="planner_node",
        name="a_star_planner",
        output="screen",
        parameters=[
            {"robot_radius": 0.0},
            {"occupied_threshold": 50},
            {"unknown_as_occupied": True},
            {"force_boundary_walls": True},
            {"anchor_map_bounds": True},
            {"use_cell_center": False},
            {"replan_on_map_update": False},
        ],
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", rviz_config],
        condition=IfCondition(use_rviz),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "use_rviz",
                default_value="true",
                description="是否启动 RViz2",
            ),
            map_node,
            planner_node,
            rviz_node,
        ]
    )

