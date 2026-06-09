# 第 14 周项目 · Docker 环境（让项目在你自己电脑上一键跑起来）

本周项目可以**完全在 Docker 里完成**，用的就是第 10/11 周配置过的那套
ROS2 桌面镜像 `ghcr.io/tiryoh/ros2-desktop-vnc:humble`。
它自带一个**浏览器里的 Linux 桌面**（noVNC），所以 turtlesim 和 PyBullet
的图形窗口都能看到，不需要在 Windows 上单独装 ROS2。

## 为什么用这套 Docker

- 一次配置，全班一致：避免「我电脑能跑、你电脑报错」。
- 浏览器即桌面：`http://localhost:6080` 就能看到仿真画面。
- 端口已打通：`8765`（机器狗）/`8080`（小乌龟）网页控制器自动映射到宿主机。

## 启动步骤

```bash
# 1. 进入 docker 目录，启动容器
cd week14_starters/docker
docker compose up -d

# 2. 浏览器打开桌面（密码通常是 ubuntu，见镜像说明）
#    http://localhost:6080

# 3. 在桌面里打开一个终端，安装依赖（只需一次）
cd ~/week14_starters/docker && bash setup.sh
```

## 方向 A：PyBullet 机器狗

桌面终端里：

```bash
cd ~/week14_starters/pybullet_dog
python3 server.py
```

桌面里会弹出 PyBullet 迷宫窗口（也可以在手机网页上看俯视图）。

## 方向 B：turtlesim 小乌龟

需要两个终端：

```bash
# 终端 1
source /opt/ros/humble/setup.bash
ros2 run turtlesim turtlesim_node

# 终端 2
source /opt/ros/humble/setup.bash
cd ~/week14_starters/turtlesim_remote
python3 turtlesim_web_bridge.py
```

## 手机怎么连进来（Tailscale）

容器把 `8765 / 8080` 端口**映射到了宿主机**，所以手机只要能访问
**宿主机的 Tailscale 地址**即可，不必在容器里装 Tailscale：

1. 在宿主机（Windows/WSL）上按第 14.3 节装好并登录 Tailscale；
2. `tailscale ip -4` 查到宿主机的 `100.x.y.z`；
3. 手机登录同一 Tailscale 账号后，浏览器打开：
   - 方向 A：`http://100.x.y.z:8765`
   - 方向 B：`http://100.x.y.z:8080`

## 关闭 / 重启

```bash
docker compose down      # 停止并删除容器
docker compose up -d     # 重新启动
```

> 代码挂载在容器里（`~/week14_starters`），你在宿主机用编辑器改代码，
> 容器里重新运行程序即可生效，不用重建镜像。
