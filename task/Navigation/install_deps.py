#!/usr/bin/env python3
"""
Install ROS2 and Python dependencies for this workspace.

Usage:
  python install_deps.py
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from typing import List


def run(cmd: List[str], cwd: str) -> int:
    """Run a command and return its exit code."""
    print(f"+ {subprocess.list2cmdline(cmd)}")
    return subprocess.call(cmd, cwd=cwd)


def main() -> int:
    parser = argparse.ArgumentParser(description="Install workspace dependencies.")
    parser.add_argument(
        "--skip-rosdep-update",
        action="store_true",
        help="Skip 'rosdep update' before installing dependencies.",
    )
    parser.add_argument(
        "--rosdistro",
        default=os.environ.get("ROS_DISTRO"),
        help="ROS distribution name (defaults to ROS_DISTRO env var).",
    )
    args = parser.parse_args()

    workspace_root = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(workspace_root, "src")
    if not os.path.isdir(src_dir):
        print("ERROR: 'src' directory not found. Run from the workspace root.", file=sys.stderr)
        return 1

    if shutil.which("rosdep") is None:
        print("ERROR: 'rosdep' not found in PATH.", file=sys.stderr)
        print("Install and initialize rosdep, then re-run this script.", file=sys.stderr)
        return 2

    if not args.skip_rosdep_update:
        code = run(["rosdep", "update"], cwd=workspace_root)
        if code != 0:
            return code

    rosdep_cmd = [
        "rosdep",
        "install",
        "--from-paths",
        src_dir,
        "--ignore-src",
        "-y",
    ]
    if args.rosdistro:
        rosdep_cmd += ["--rosdistro", args.rosdistro]

    code = run(rosdep_cmd, cwd=workspace_root)
    if code != 0:
        return code

    requirements = os.path.join(workspace_root, "requirements.txt")
    if os.path.isfile(requirements):
        with open(requirements, encoding="utf-8") as requirements_file:
            has_requirements = any(
                line.strip() and not line.lstrip().startswith("#")
                for line in requirements_file
            )
        if has_requirements:
            code = run([sys.executable, "-m", "pip", "install", "-r", requirements], cwd=workspace_root)
            if code != 0:
                return code

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
