#!/usr/bin/env bash
# 在容器内（浏览器桌面的终端里）执行一次，安装本周项目依赖。
set -e

echo "[1/2] 安装 Python 依赖（aiohttp + pybullet）..."
pip3 install --break-system-packages aiohttp pybullet || \
  pip3 install aiohttp pybullet

echo "[2/2] 确认 turtlesim 已安装（ROS2 desktop 镜像自带）..."
if ! ros2 pkg executables turtlesim >/dev/null 2>&1; then
  echo "  turtlesim 未找到，尝试安装..."
  sudo apt-get update && sudo apt-get install -y ros-humble-turtlesim
fi

echo ""
echo "依赖准备完成。接下来："
echo "  方向 A（机器狗）:"
echo "    cd ~/week14_starters/pybullet_dog && python3 server.py"
echo "    浏览器桌面里会弹出 PyBullet 迷宫窗口；手机访问 http://<宿主机Tailscale_IP>:8765"
echo ""
echo "  方向 B（小乌龟）: 开两个终端"
echo "    终端1: source /opt/ros/humble/setup.bash && ros2 run turtlesim turtlesim_node"
echo "    终端2: source /opt/ros/humble/setup.bash && cd ~/week14_starters/turtlesim_remote && python3 turtlesim_web_bridge.py"
echo "    手机访问 http://<宿主机Tailscale_IP>:8080"
