"""
内置地图配置（二维栅格）。

说明：
- 该文件不依赖 ROS2，只负责“地图数据定义”；
- 地图用 OccupancyGrid 的 row-major 形式存储；
- 数值约定：0=空闲，100=占用。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

# OccupancyGrid 取值约定
FREE = 0
OCCUPIED = 100


@dataclass
class MapProfile:
    """
    地图配置结构体。

    - width / height : 栅格尺寸（格数）
    - resolution     : 每格大小（米）
    - origin_x/y     : 地图原点（世界坐标）
    - data           : row-major 的一维数组
    """

    map_id: str
    width: int
    height: int
    resolution: float
    origin_x: float
    origin_y: float
    data: List[int]


def _create_empty_grid(width: int, height: int, value: int = FREE) -> List[int]:
    """
    创建空白地图（所有格子初始化为 value）。
    """

    return [value] * (width * height)


def _set_cell(data: List[int], width: int, x: int, y: int, value: int) -> None:
    """
    设置单个栅格的占用状态。

    说明：
    - 使用 row-major 索引：index = y * width + x
    """

    data[y * width + x] = value


def _add_rect(
    data: List[int],
    width: int,
    height: int,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    value: int = OCCUPIED,
) -> None:
    """
    添加矩形障碍（包含边界，x0<=x<=x1, y0<=y<=y1）。
    """

    x0 = max(0, min(width - 1, x0))
    x1 = max(0, min(width - 1, x1))
    y0 = max(0, min(height - 1, y0))
    y1 = max(0, min(height - 1, y1))

    for y in range(min(y0, y1), max(y0, y1) + 1):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            _set_cell(data, width, x, y, value)


def _add_boundary_walls(data: List[int], width: int, height: int) -> None:
    """
    添加边界墙，确保地图边界不可通行。

    这样做的好处：
    - 防止路径跑出地图；
    - 便于 A* 通过障碍物推断地图边界。
    """

    # 上下边界
    _add_rect(data, width, height, 0, 0, width - 1, 0, OCCUPIED)
    _add_rect(data, width, height, 0, height - 1, width - 1, height - 1, OCCUPIED)
    # 左右边界
    _add_rect(data, width, height, 0, 0, 0, height - 1, OCCUPIED)
    _add_rect(data, width, height, width - 1, 0, width - 1, height - 1, OCCUPIED)


def _make_room_simple() -> MapProfile:
    """
    简单房间地图（参考 a_star.py 的障碍结构）。
    """

    width, height = 70, 70
    resolution = 1.0
    origin_x, origin_y = 0.0, 0.0
    data = _create_empty_grid(width, height, FREE)

    # 外围边界
    _add_boundary_walls(data, width, height)

    # 内部墙体（竖墙）
    _add_rect(data, width, height, 20, 1, 20, 40, OCCUPIED)
    _add_rect(data, width, height, 40, 30, 40, 68, OCCUPIED)

    # 横向短墙（制造绕行）
    _add_rect(data, width, height, 10, 50, 30, 50, OCCUPIED)

    return MapProfile(
        map_id="room_simple",
        width=width,
        height=height,
        resolution=resolution,
        origin_x=origin_x,
        origin_y=origin_y,
        data=data,
    )


def _make_corridor_zigzag() -> MapProfile:
    """
    Z 字走廊地图（演示窄通道与转弯）。
    """

    width, height = 80, 30
    resolution = 1.0
    origin_x, origin_y = 0.0, 0.0
    data = _create_empty_grid(width, height, FREE)

    _add_boundary_walls(data, width, height)

    # 两条横向长墙，留出错位的通道
    _add_rect(data, width, height, 1, 10, 60, 10, OCCUPIED)
    _add_rect(data, width, height, 20, 20, 78, 20, OCCUPIED)

    # 在墙上“挖洞”形成通道
    _add_rect(data, width, height, 28, 10, 32, 10, FREE)
    _add_rect(data, width, height, 48, 20, 52, 20, FREE)

    return MapProfile(
        map_id="corridor_zigzag",
        width=width,
        height=height,
        resolution=resolution,
        origin_x=origin_x,
        origin_y=origin_y,
        data=data,
    )


def _make_grid_maze() -> MapProfile:
    """
    简易栅格式迷宫（多条平行竖墙 + 缝隙）。
    """

    width, height = 50, 50
    resolution = 1.0
    origin_x, origin_y = 0.0, 0.0
    data = _create_empty_grid(width, height, FREE)

    _add_boundary_walls(data, width, height)

    # 竖向栅格墙
    for x in range(6, width - 1, 6):
        for y in range(1, height - 1):
            # 每隔一定高度留出一个“门洞”
            if y % 10 != 5:
                _set_cell(data, width, x, y, OCCUPIED)

    return MapProfile(
        map_id="grid_maze",
        width=width,
        height=height,
        resolution=resolution,
        origin_x=origin_x,
        origin_y=origin_y,
        data=data,
    )


def get_map(map_id: str) -> MapProfile:
    """
    根据 map_id 获取地图配置。

    可选 map_id：
    - room_simple
    - corridor_zigzag
    - grid_maze
    """

    maps: Dict[str, MapProfile] = {
        "room_simple": _make_room_simple(),
        "corridor_zigzag": _make_corridor_zigzag(),
        "grid_maze": _make_grid_maze(),
    }

    if map_id not in maps:
        # 若 map_id 不存在，则给出清晰错误
        valid = ", ".join(maps.keys())
        raise ValueError(f"未知 map_id: {map_id}. 可选值: {valid}")

    return maps[map_id]

