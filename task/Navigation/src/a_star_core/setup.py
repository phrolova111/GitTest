from setuptools import setup

package_name = "a_star_core"

setup(
    name=package_name,
    version="0.0.1",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="anon",
    maintainer_email="anon@todo.com",
    description="纯 Python 版 A* 栅格规划核心算法（不依赖 ROS2）。",
    license="MIT",
    tests_require=["pytest"],
)

