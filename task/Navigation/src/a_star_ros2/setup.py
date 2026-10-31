from setuptools import setup

package_name = "a_star_ros2"

setup(
    name=package_name,
    version="0.0.1",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", ["launch/a_star_demo.launch.py"]),
        (f"share/{package_name}/rviz", ["rviz/a_star_demo.rviz"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="anon",
    maintainer_email="anon@todo.com",
    description="ROS2 节点：地图发布 + A* 路径规划。",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "map_provider_node = a_star_ros2.map_provider_node:main",
            "planner_node = a_star_ros2.planner_node:main",
        ],
    },
)

