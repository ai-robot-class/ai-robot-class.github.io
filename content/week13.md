# 第13周：四足机器人入门 + 期末项目实施

**课时**: 3小时（一次课）

---

## 📋 本周课程大纲

| 模块 | 时间 | 主题 | 内容 |
|------|------|------|------|
| 模块1 | 60分钟 | 四足机器人基础 | 概述+PyBullet仿真+步态 |
| 模块2 | 20分钟 | **工业级仿真演示** | MATRiX 现场演示（教师演示） |
| 茶歇 | 10分钟 | 休息 | - |
| 模块3 | 90分钟 | 项目开发辅导 | 答疑+调试+开发 |

---

## 第一模块：四足机器人基础（80分钟）

### ⏱️ 时间分配

| 环节 | 时间 | 内容 |
|------|------|------|
| 讲解 | 25分钟 | 四足机器人概述+步态 |
| 演示+实践 | 35分钟 | PyBullet仿真实战（学生跟做）|
| 工业级演示 | 20分钟 | **MATRiX 现场演示**（教师演示，学生观看）|

---

## 13.1 四足机器人概述

### 13.1.1 为什么研究四足机器人？

```
四足 vs 轮式 vs 双足：

┌─────────────────────────────────────────────────────────────┐
│  类型        优势               劣势           代表产品      │
├─────────────────────────────────────────────────────────────┤
│  轮式    速度快、能耗低      地形适应差    扫地机器人       │
│  双足    类人、灵活          控制困难      Atlas, Optimus  │
│  四足    稳定、越障强        速度中等      Spot, Unitree   │
└─────────────────────────────────────────────────────────────┘
```

**四足机器人的应用场景**：
- 🏭 工业巡检（电厂、化工厂）
- 🚨 搜救探测（地震、火灾）
- 🎖️ 军事侦察
- 📦 物流运输
- 🎬 影视拍摄

---

### 13.1.2 四足机器人结构

```
基本结构：

         ┌─── 机身(Body) ───┐
         │                 │
    ┌────┴────┐       ┌────┴────┐
    │ 前左腿  │       │ 前右腿  │
    │ LF      │       │ RF      │
    └─────────┘       └─────────┘
    
    ┌─────────┐       ┌─────────┐
    │ 后左腿  │       │ 后右腿  │
    │ LH      │       │ RH      │
    └─────────┘       └─────────┘

每条腿3个关节：
• Hip（髋关节）：左右摆动
• Thigh（大腿关节）：前后摆动  
• Calf（小腿关节）：前后摆动

总自由度：4腿 × 3关节 = 12 DoF
```

**真实四足机器人示例**：

| 品牌 | 型号 | 价格范围 | 特点 |
|------|------|----------|------|
| Boston Dynamics | Spot | $75,000+ | 工业级、高性能 |
| Unitree | Go1 | $2,700+ | 开源、教育研究 |
| Unitree | B2 | $15,000+ | 高载重 |
| XGO | XGO-Mini | $500+ | 桌面级、入门 |

---

### 13.1.3 步态（Gait）基础

> 步态 = 腿部抬起落下的顺序和时序

#### 常见步态类型

```
1. 静态步态（慢速、稳定）

   Walk步态（四足轮流抬起）：
   
   时刻1: LF抬起  (3腿着地)
   时刻2: RH抬起  (3腿着地)
   时刻3: RF抬起  (3腿着地)
   时刻4: LH抬起  (3腿着地)
   
   特点：始终3腿以上着地，稳定但慢


2. 动态步态（快速、需要平衡）

   Trot步态（对角线腿同时抬起）：
   
   阶段1: LF+RH抬起  (对角腿)
   阶段2: RF+LH抬起  (另一对角)
   
   特点：只有2腿着地，需要动态平衡，速度快
   

步态周期可视化：

     LF  ████░░░░████░░░░  ■着地 □腾空
     RF  ░░░░████░░░░████
     LH  ░░░░████░░░░████
     RH  ████░░░░████░░░░
         └─ 一个周期 ─┘
```

---

## 13.2 PyBullet仿真入门

> PyBullet是轻量级物理仿真引擎，适合学习

### 13.2.1 安装与基本使用

```bash
# 安装PyBullet
pip install pybullet numpy

# 验证
python3 -c "import pybullet as p; print('PyBullet已安装')"
```

### 13.2.2 基础仿真示例

```python
import pybullet as p
import pybullet_data
import time

# 连接物理引擎（GUI模式）
physicsClient = p.connect(p.GUI)

# 设置搜索路径（用于加载默认模型）
p.setAdditionalSearchPath(pybullet_data.getDataPath())

# 设置重力
p.setGravity(0, 0, -9.8)

# 加载地面
planeId = p.loadURDF("plane.urdf")

# 加载一个立方体
startPos = [0, 0, 1]
startOrientation = p.getQuaternionFromEuler([0, 0, 0])
boxId = p.loadURDF("cube.urdf", startPos, startOrientation)

# 仿真循环
for i in range(1000):
    p.stepSimulation()
    time.sleep(1./240.)  # 240Hz仿真频率

# 断开连接
p.disconnect()
```

### 13.2.3 加载四足机器人模型

```python
import pybullet as p
import pybullet_data
import time
import numpy as np

# 连接
p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.8)

# 加载地面
planeId = p.loadURDF("plane.urdf")

# 加载四足机器人（使用示例模型）
# 注意：这里使用的是PyBullet自带的Laikago模型
robotId = p.loadURDF("laikago/laikago_toes.urdf", [0, 0, 0.5])

# 获取机器人信息
numJoints = p.getNumJoints(robotId)
print(f"关节数量: {numJoints}")

# 打印关节信息
for i in range(numJoints):
    info = p.getJointInfo(robotId, i)
    print(f"关节{i}: {info[1].decode('utf-8')}, 类型: {info[2]}")

# 简单仿真
for _ in range(2000):
    p.stepSimulation()
    time.sleep(1./240.)

p.disconnect()
```

---

## 13.3 简单步态控制

### 13.3.1 正弦波步态生成

> 最简单的步态：用正弦函数控制关节

```python
import pybullet as p
import pybullet_data
import time
import numpy as np

# 初始化
p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.8)
p.loadURDF("plane.urdf")

# 加载机器人
robotId = p.loadURDF("laikago/laikago_toes.urdf", [0, 0, 0.5])

# 定义关节ID（根据模型不同可能需要调整）
# 假设每条腿3个关节：hip, thigh, calf
leg_joints = {
    'LF': [0, 1, 2],    # 前左腿
    'RF': [3, 4, 5],    # 前右腿
    'LH': [6, 7, 8],    # 后左腿
    'RH': [9, 10, 11]   # 后右腿
}

def simple_gait(t, leg_name, frequency=1.0):
    """
    生成简单的正弦波步态
    t: 时间
    leg_name: 'LF', 'RF', 'LH', 'RH'
    """
    # 不同腿的相位差（实现Trot步态）
    phase_offset = {
        'LF': 0,
        'RH': 0,        # 与LF同相位（对角线）
        'RF': np.pi,    # 相位差180度
        'LH': np.pi     # 与RF同相位（对角线）
    }
    
    phase = phase_offset[leg_name]
    
    # 关节角度（简化版）
    hip_angle = 0  # 髋关节保持中立
    thigh_angle = 0.3 * np.sin(2 * np.pi * frequency * t + phase)
    calf_angle = -0.6 * np.sin(2 * np.pi * frequency * t + phase)
    
    return [hip_angle, thigh_angle, calf_angle]

# 仿真循环
t = 0
dt = 1./240.

for _ in range(5000):
    # 为每条腿生成目标角度
    for leg_name, joint_ids in leg_joints.items():
        target_angles = simple_gait(t, leg_name, frequency=0.5)
        
        # 设置关节目标位置（位置控制）
        for joint_id, target_angle in zip(joint_ids, target_angles):
            p.setJointMotorControl2(
                robotId,
                joint_id,
                p.POSITION_CONTROL,
                targetPosition=target_angle,
                force=20  # 最大力矩
            )
    
    p.stepSimulation()
    time.sleep(dt)
    t += dt

p.disconnect()
```

### 13.3.2 Trot步态实现

```python
import pybullet as p
import pybullet_data
import time
import numpy as np

class QuadrupedController:
    """简单的四足控制器"""
    
    def __init__(self, robot_id):
        self.robot_id = robot_id
        
        # 关节ID（需要根据实际模型调整）
        self.leg_joints = {
            'LF': [0, 1, 2],
            'RF': [3, 4, 5],
            'LH': [6, 7, 8],
            'RH': [9, 10, 11]
        }
        
        # 步态参数
        self.stance_height = 0.3  # 站立高度
        self.step_height = 0.05   # 抬腿高度
        self.step_length = 0.1    # 步长
        
    def trot_gait(self, t, leg_name, frequency=1.0):
        """
        Trot步态生成
        """
        # 相位（对角腿同相）
        if leg_name in ['LF', 'RH']:
            phase = 0
        else:  # RF, LH
            phase = np.pi
        
        # 步态周期位置
        cycle_phase = (2 * np.pi * frequency * t + phase) % (2 * np.pi)
        
        # 摆动相 vs 支撑相
        if cycle_phase < np.pi:  # 摆动相（腿抬起）
            progress = cycle_phase / np.pi
            x = self.step_length * (progress - 0.5)
            z = self.step_height * np.sin(np.pi * progress)
        else:  # 支撑相（腿着地）
            progress = (cycle_phase - np.pi) / np.pi
            x = self.step_length * (0.5 - progress)
            z = 0
        
        # 逆运动学（简化版）
        y = 0  # 横向位置
        hip = 0
        
        # 大腿和小腿角度（简化计算）
        l_thigh = 0.2  # 大腿长度
        l_calf = 0.2   # 小腿长度
        target_height = self.stance_height + z
        
        # 简化逆运动学
        thigh = np.arctan2(x, target_height)
        calf = -2 * thigh
        
        return [hip, thigh, calf]
    
    def step(self, t, frequency=1.0):
        """执行一步控制"""
        for leg_name, joint_ids in self.leg_joints.items():
            target_angles = self.trot_gait(t, leg_name, frequency)
            
            for joint_id, angle in zip(joint_ids, target_angles):
                p.setJointMotorControl2(
                    self.robot_id,
                    joint_id,
                    p.POSITION_CONTROL,
                    targetPosition=angle,
                    force=20
                )

# 主程序
def main():
    # 初始化
    p.connect(p.GUI)
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.setGravity(0, 0, -9.8)
    p.loadURDF("plane.urdf")
    
    # 加载机器人
    robotId = p.loadURDF("laikago/laikago_toes.urdf", [0, 0, 0.5])
    
    # 创建控制器
    controller = QuadrupedController(robotId)
    
    # 仿真
    t = 0
    dt = 1./240.
    
    print("开始仿真，按Ctrl+C停止...")
    
    try:
        while True:
            controller.step(t, frequency=0.5)
            p.stepSimulation()
            time.sleep(dt)
            t += dt
            
    except KeyboardInterrupt:
        print("仿真结束")
    
    p.disconnect()

if __name__ == '__main__':
    main()
```

---

## 13.4 进阶话题（了解即可）

### 13.4.1 控制方法对比

| 方法 | 原理 | 优点 | 缺点 | 代表 |
|------|------|------|------|------|
| **模型预测控制(MPC)** | 基于动力学模型优化 | 精确、可解释 | 需要准确模型 | MIT Cheetah |
| **强化学习(RL)** | 神经网络端到端学习 | 自适应、鲁棒 | 训练时间长 | ANYmal |
| **轨迹优化** | 离线优化轨迹 | 高效、可预测 | 难以适应变化 | 研究用 |
| **CPG(中央模式发生器)** | 生物启发振荡器 | 简单、实时 | 适应性差 | 早期机器人 |

### 13.4.2 从仿真到实物（Sim-to-Real）

```
Sim2Real的挑战：

仿真环境                 实物环境
┌──────────┐            ┌──────────┐
│ 完美模型 │            │ 模型误差 │
│ 无噪声   │    ≠      │ 传感噪声 │
│ 精确控制 │            │ 延迟抖动 │
└──────────┘            └──────────┘

解决方法：
1. Domain Randomization（领域随机化）
   → 仿真中随机化参数（质量、摩擦力等）
   
2. 系统辨识（System Identification）
   → 测量实物参数，更新仿真模型
   
3. 教师-学生网络
   → 仿真中训练教师，实物上部署学生
```

### 13.4.3 前沿研究方向

1. **可微仿真**：使用可微分物理引擎，梯度优化控制策略
2. **视觉导航**：结合视觉感知的自主导航
3. **操作任务**：带机械臂的四足机器人
4. **人形机器人**：四足技术向双足迁移

---

## 13.5 工业级仿真平台 — MATRiX（课堂演示 / 选修）

> 让大家看看产业界、研究院在用的高保真仿真平台是什么样的

### 13.5.1 MATRiX 是什么

[MATRiX](https://github.com/ZSIBOT/MATRIX) 是中山智能机器人研究院（ZSIBOT）开源的四足机器人仿真平台：

```
MATRiX = MuJoCo（物理）+ Unreal Engine 5（渲染）+ CARLA（场景）

┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   物理仿真层    →    MuJoCo（高精度、关节动力学）          │
│        ↓                                                    │
│   通信中间件    →    ROS2 Humble（话题、服务）              │
│        ↓                                                    │
│   视觉渲染层    →    Unreal Engine 5（光线追踪、超写实）   │
│        ↓                                                    │
│   场景库        →    CARLA（自动驾驶场景、城市/野外）      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 13.5.2 与 PyBullet 的对比

| 维度 | PyBullet（本课作业） | MATRiX（演示） |
|------|----------------------|----------------|
| **物理引擎** | Bullet（简单） | MuJoCo（精确） |
| **渲染质量** | 简单 OpenGL | UE5 光追、超写实 |
| **场景库** | 几何 URDF | CARLA 城市/野外 |
| **传感器仿真** | 基础相机 | 相机/LiDAR/IMU 全栈 |
| **硬件需求** | ❌ 无独显也行 | ✅ NVIDIA RTX 4060+ |
| **适用场景** | 教学、原型 | 产业级开发、Sim2Real |

### 13.5.3 硬件要求（必读）

> ⚠️ **完整 MATRiX 必须有独立 NVIDIA 显卡才能运行**

| 项目 | 最低要求 | 推荐 |
|------|----------|------|
| 操作系统 | Ubuntu 22.04 | Ubuntu 22.04 |
| GPU | NVIDIA RTX 4060 | RTX 4070 及以上 |
| 显存 | 8 GB | 12 GB+ |
| 驱动 | NVIDIA Driver ≥ 535 | 最新版 |
| ROS | ROS2 Humble | ROS2 Humble |
| 编译器 | GCC C++11+ | GCC 11+ |

> 📝 **没有独显的同学**：本课不强制要求安装 MATRiX。课堂上看演示即可，作业用 PyBullet 完成。

### 13.5.4 Docker 快速部署（仅供有显卡同学）

```bash
# 1. 安装 NVIDIA Container Toolkit（让 Docker 能用 GPU）
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/libnvidia-container/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list \
  | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt update && sudo apt install -y nvidia-container-toolkit
sudo systemctl restart docker

# 2. 拉取 MATRiX 代码并构建（需要联网下载 ~10GB 资源包）
git clone https://github.com/ZSIBOT/MATRIX.git
cd MATRIX
bash scripts/install_deps.sh

# 3. 下载发布资源（基础包 + 运行时 + 地图）
bash scripts/release_manager/install_chunks.sh 0.1.2

# 4. 验证环境
bash scripts/check_env.sh runtime

# 5. 启动仿真
./bin/sim_launcher
```

> 💡 **网络问题**：如果 ROS apt 源不可达，使用 `ROSAPTREPOURL=<镜像>` 环境变量。
> 如果 aria2/wget 报 TLS 错误，加 `SKIPARIA2=1` 跳过加速。

### 13.5.5 课堂演示流程（建议 8-10 分钟）

> 👨‍🏫 **教师指南**：在带独显的笔记本上提前安装好 MATRiX，课堂现场演示

#### 演示脚本

```
[0:00 - 0:30] 介绍 MATRiX 的定位
  "我们前面学的 PyBullet 是教学版仿真，
   现在给大家看一下产业界、研究院用的工业级仿真平台 —— MATRiX"

[0:30 - 2:00] 启动 sim_launcher，展示界面
  - 演示机器人选择（Unitree Go1 / Go2 / 自定义）
  - 演示地图选择（城市 / 工地 / 野外 / 室内）
  - 强调：这是 UE5 实时渲染，光线追踪

[2:00 - 4:00] 启动一个城市场景
  - 让四足机器人在城市街道上漫游
  - 展示相机视角切换（俯瞰 / 第三人称 / 第一人称）
  - 强调：相机/LiDAR 数据可以通过 ROS2 topic 接入

[4:00 - 6:00] 用手柄/键盘控制机器人
  - 让学生看到响应感
  - 强调：物理基于 MuJoCo，运动学约束真实

[6:00 - 8:00] 展示 ROS2 接入
  - 开另一个终端：rqt 看 topic 列表
  - 启动一个 SLAM 或导航节点
  - 强调："和我们前几周学的 ROS2 完全兼容"

[8:00 - 10:00] 总结 & Q&A
  - 为什么用 UE5？→ 视觉模型可以训练成更接近真实
  - Sim2Real 怎么做？→ Domain Randomization 在这里设置
  - 学生可以做什么？→ 留作业：思考如何用 PyBullet 仿真训练，
                       再迁移到 MATRiX 这种高保真仿真验证
```

#### 演示前检查清单

- [ ] 笔记本电源接好（UE5 + GPU 很耗电）
- [ ] 提前 `bash scripts/release_manager/install_chunks.sh 0.1.2` 完成
- [ ] 提前下载 2-3 个常用地图（避免现场下载）
- [ ] 测试投影分辨率（UE5 高分辨率渲染流畅度）
- [ ] 准备一个手柄（演示效果更好）
- [ ] 录屏软件（备份录像，作为下次离线播放）

### 13.5.6 选修拓展任务

**适合电脑有独显的同学（可作为期末项目加分）**：

1. **场景搭建**：用 MATRiX 自定义场景（按 [Custom Scene Guide](https://github.com/ZSIBOT/MATRIX/tree/main/docs)）
2. **数据采集**：在 MATRiX 中跑机器人，采集相机/LiDAR 数据用于训练
3. **Sim2Real 对比**：同一控制策略在 PyBullet 和 MATRiX 中跑，对比效果
4. **多机器人协同**：参考 [Multi-Robot Tutorial](https://github.com/ZSIBOT/MATRIX/tree/main/docs)

**没有独显的同学也能做的扩展**：

1. **MuJoCo 学习**（CPU 即可）：`pip install mujoco`，跑 MuJoCo 自带 4 足模型
2. **看 MATRiX 源码**：阅读 `src/` 目录理解工业级仿真器的架构
3. **写技术对比报告**：PyBullet / MuJoCo / Gazebo / MATRiX 的差异分析

### 13.5.7 进一步学习

- 📚 [MATRiX 官方文档](https://github.com/ZSIBOT/MATRIX/tree/main/docs)
- 💬 MATRiX 微信社区（README 中扫码）
- 🎬 课堂演示录像（教师上传到课程仓库的 `demos/` 目录）
- 🔬 [MuJoCo 官网](https://mujoco.org/) - MATRiX 的物理核心
- 🎮 [Unreal Engine 学习路径](https://www.unrealengine.com/zh-CN/onlinelearning-courses)

---

## 13.6 课后深造 — 深蓝学院课程推荐

> 🎓 本课只是机器人/AI 的入门。想真正进入这个领域，强烈推荐去 **[深蓝学院（ShenLan XueYuan）](https://www.shenlanxueyuan.com/)** 系统学习。

### 13.6.1 关于深蓝学院

[深蓝学院](https://www.shenlanxueyuan.com/) 是国内最大、最专业的机器人 / 无人驾驶 / 计算机视觉在线教育平台之一：

- 👨‍🏫 **讲师阵容**：高校教授（清华、北大、浙大、上交、港中文等）+ 工业界专家（百度 Apollo、华为、小马智行、文远知行、Momenta 等）
- 📚 **课程深度**：从基础理论到工业级项目，配套有论文阅读、代码实战、答辩等
- 🎓 **学习方式**：直播 + 录播，配有专属答疑群、助教
- 🏆 **优势**：每个课程都有对应的工业实战项目，学完直接可以做项目/写论文/进大厂

### 13.6.2 与本课程对应的推荐课程

按你在本课程的兴趣方向推荐：

#### 🤖 机器人方向（对应 Week 4-5, 13）

| 课程 | 推荐理由 | 难度 |
|------|---------|------|
| **ROS 入门到精通** | 把 Week 2-8 学的 ROS2 系统化 | ⭐⭐ |
| **机器人运动规划** | 深入 Week 5 学的运动学 | ⭐⭐⭐⭐ |
| **机械臂控制理论与实战** | 工业机器人核心课程 | ⭐⭐⭐⭐ |
| **四足/双足机器人控制** | 进阶 Week 13 内容 | ⭐⭐⭐⭐⭐ |
| **强化学习与机器人控制** | 现代腿足机器人主流方法 | ⭐⭐⭐⭐⭐ |

#### 👁️ 计算机视觉方向（对应 Week 9-12）

| 课程 | 推荐理由 | 难度 |
|------|---------|------|
| **三维视觉与SLAM基础** | 系统讲 SLAM 理论 | ⭐⭐⭐ |
| **视觉 SLAM 进阶** | 高翔老师明星课程 | ⭐⭐⭐⭐ |
| **激光 SLAM 理论与实践** | 激光雷达 SLAM 必学 | ⭐⭐⭐⭐ |
| **多传感器融合定位** | 自动驾驶/机器人定位核心 | ⭐⭐⭐⭐ |
| **YOLO 系列与实时检测** | 进阶 Week 10 内容 | ⭐⭐⭐ |
| **目标跟踪与多目标跟踪** | 进阶 Week 11 内容 | ⭐⭐⭐⭐ |
| **深度学习与计算机视觉** | CV 必学基础 | ⭐⭐⭐ |

#### 🚗 自动驾驶方向（对应 Week 6 KITTI）

| 课程 | 推荐理由 | 难度 |
|------|---------|------|
| **自动驾驶感知与定位** | 从传感器到地图全栈 | ⭐⭐⭐⭐ |
| **决策规划与控制** | Apollo 工程师必学 | ⭐⭐⭐⭐ |
| **端到端自动驾驶**（热门 🔥）| 大模型时代新方向 | ⭐⭐⭐⭐⭐ |
| **BEV 感知与 Transformer** | 当前主流量产方案 | ⭐⭐⭐⭐⭐ |

#### 🧠 AI / 大模型方向（前沿）

| 课程 | 推荐理由 | 难度 |
|------|---------|------|
| **大语言模型（LLM）原理与实战** | 入行大模型 | ⭐⭐⭐⭐ |
| **具身智能（Embodied AI）**（热门 🔥）| 机器人 + 大模型，最前沿 | ⭐⭐⭐⭐⭐ |
| **多模态大模型** | GPT-4V / Sora 背后技术 | ⭐⭐⭐⭐⭐ |
| **VLA（视觉-语言-动作）** | 机器人新范式 | ⭐⭐⭐⭐⭐ |

### 13.6.3 学习路径建议

根据你的期末项目方向，推荐三条学习路径：

#### 🛤️ 路径 A：移动机器人方向

```
本课程 → ROS 入门精通 → 视觉 SLAM 基础 → 视觉 SLAM 进阶
       → 机器人运动规划 → 强化学习与机器人控制

适合：想做服务机器人、四足机器人、巡检机器人
就业：宇树、云深处、追觅、智元等
```

#### 🛤️ 路径 B：自动驾驶方向

```
本课程 → 自动驾驶感知与定位 → BEV 感知与 Transformer
       → 决策规划与控制 → 端到端自动驾驶

适合：想做无人车感知/规控
就业：小马智行、文远知行、Momenta、华为车 BU、特斯拉等
```

#### 🛤️ 路径 C：具身智能方向（最热门）

```
本课程 → 深度学习与CV → 大语言模型原理与实战
       → 具身智能（Embodied AI）→ VLA 模型实战

适合：想做人形机器人、家庭机器人
就业：宇树人形、银河通用、星动纪元、智元、 Figure AI、Physical Intelligence
```

### 13.6.4 学习方法建议

> 💡 老师过来人的经验

1. **不要一上来就报 5 门课**
   先选 1 门自己最感兴趣的深耕，比如做完 SLAM 课程的所有作业，远比看 5 门课的录播有用

2. **跟着课程动手写代码**
   不要看视频，看完就忘。一定要在自己机器上跑通每个 demo

3. **结合论文阅读**
   深蓝学院每门课会推荐相关论文，把核心论文当作课程教材读

4. **加群提问 + 找人组队**
   学习社区是最大资产，跟同学一起做项目、互相 review 代码

5. **定期输出**
   写技术博客（CSDN/知乎/掘金/Notion），把学到的东西讲明白才是真学会了

### 13.6.5 其他优秀学习资源

除了深蓝学院，这些也值得参考：

| 平台 | 特点 | 适合 |
|------|------|------|
| 📺 [B站](https://www.bilibili.com/) | 大量优质免费机器人/AI 教程 | 入门补充 |
| 🎓 [Coursera](https://www.coursera.org/) | 国外名校（CMU、宾大、ETH）机器人课 | 系统学英语课程 |
| 🤖 [MIT OpenCourseWare](https://ocw.mit.edu/) | MIT 公开课，机器人/AI 经典 | 理论扎实 |
| 📚 [Hugging Face](https://huggingface.co/learn) | LLM/具身智能社区与教程 | 大模型方向 |
| 🛠️ [古月居](https://www.guyuehome.com/) | 中文 ROS 社区 | ROS 实战 |
| 🌐 [GitHub Awesome 系列](https://github.com/topics/awesome) | 收录大量精选资源 | 自学路径图 |

### 13.6.6 关于继续读研 / 就业

如果学完深蓝学院的 2-3 门课程，你已经具备：

- ✅ 能独立完成一个机器人/AI 小项目
- ✅ 能读懂 SLAM/感知/规划的经典论文
- ✅ 简历上可以写出有内容的项目经历
- ✅ 面试时能聊清楚技术细节

**这就足够**：
- 🎓 申请国内外机器人/CV 方向硕博
- 💼 进入互联网/机器人/自动驾驶大厂
- 🚀 参加机器人竞赛（RoboMaster、RoboCup、CCFRC 等）
- 🏆 申请 GSoC、字节夏令营等

---

## 第二次课：期末项目开发辅导（3小时）

### ⏱️ 时间分配

| 环节 | 时间 | 内容 |
|------|------|------|
| 项目进度检查 | 30分钟 | 各组汇报进度 |
| 技术答疑 | 60分钟 | 解决技术问题 |
| 茶歇 | 10分钟 | 休息 |
| 自由开发时间 | 100分钟 | 现场开发与调试 |

---

## 13.7 项目开发指导

### 13.7.1 项目开发检查清单

#### 阶段1：基础搭建（应在第12周完成）

- [ ] GitHub仓库创建
- [ ] 开发环境配置（ROS2/OpenCV/YOLO等）
- [ ] 基本框架代码
- [ ] README.md初稿

#### 阶段2：核心功能实现（第13周重点）

- [ ] 核心算法实现
- [ ] ROS2节点编写
- [ ] 基本功能测试
- [ ] 代码注释补充

#### 阶段3：测试与完善（第13周末）

- [ ] 功能完整性测试
- [ ] 边界情况测试
- [ ] 性能优化
- [ ] Bug修复

#### 阶段4：文档与演示（第14周或答辩前）

- [ ] README.md完善
- [ ] 录制演示视频（2-5分钟）
- [ ] 准备答辩PPT（可选）
- [ ] 代码整理提交

---

### 13.7.2 常见问题解答（FAQ）

#### Q1: 如何在没有真实机器人的情况下测试？

**A**: 使用仿真环境
```bash
# 选项1: Gazebo仿真
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py

# 选项2: PyBullet仿真
python3 quadruped_sim.py

# 选项3: 使用录制的视频/数据
ros2 bag play recorded_data.bag
```

#### Q2: OpenCV找不到摄像头怎么办？

**A**: 使用视频文件或图片
```python
# 方法1: 使用视频文件
cap = cv2.VideoCapture('test_video.mp4')

# 方法2: 使用图片序列
img = cv2.imread('test_image.jpg')

# 方法3: 检查摄像头索引
for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"摄像头{i}可用")
        break
```

#### Q3: ROS2节点通信失败？

**A**: 调试步骤
```bash
# 1. 检查节点是否运行
ros2 node list

# 2. 检查话题是否发布
ros2 topic list
ros2 topic echo /your_topic

# 3. 检查消息类型
ros2 interface show sensor_msgs/msg/Image

# 4. 查看节点信息
ros2 node info /your_node
```

#### Q4: YOLO检测太慢？

**A**: 性能优化方法
```python
# 方法1: 使用更小的模型
model = YOLO('yolov8n.pt')  # n < s < m < l

# 方法2: 降低图像分辨率
img = cv2.resize(img, (640, 480))

# 方法3: 跳帧处理
frame_count = 0
if frame_count % 3 == 0:  # 每3帧处理一次
    results = model(frame)
frame_count += 1

# 方法4: 使用GPU（如果有）
model = YOLO('yolov8n.pt')
model.to('cuda')
```

#### Q5: GitHub提交遇到问题？

**A**: 常用Git命令
```bash
# 克隆仓库
git clone https://github.com/username/repo.git

# 查看状态
git status

# 添加文件
git add .

# 提交
git commit -m "实现颜色检测功能"

# 推送
git push

# 如果遇到冲突
git pull
# 解决冲突后再push
```

---

### 13.7.3 项目展示准备

#### 演示视频录制要点

1. **时长**: 2-5分钟
2. **内容结构**:
   ```
   - 开场（10秒）：项目名称、团队成员
   - 功能演示（1-2分钟）：展示核心功能
   - 技术介绍（1分钟）：使用的技术栈
   - 结果展示（30秒）：效果截图/数据
   - 总结（20秒）：总结与展望
   ```

3. **录制工具**:
   - Windows: Xbox Game Bar (Win+G)
   - Mac: QuickTime Player
   - Linux: SimpleScreenRecorder
   - 全平台: OBS Studio

4. **注意事项**:
   - 声音清晰（可后期配音）
   - 画面流畅（建议30fps）
   - 突出重点功能
   - 展示实际效果

#### README.md模板

```markdown
# 项目名称

**团队成员**: XXX, YYY, ZZZ

## 项目简介

简要描述项目目标和功能（2-3句话）

## 功能特性

- [x] 功能1：xxx
- [x] 功能2：xxx
- [ ] 功能3（扩展）：xxx

## 技术栈

- ROS2 Humble
- OpenCV 4.x
- YOLO v8
- Python 3.10

## 快速开始

### 安装依赖

\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 运行

\`\`\`bash
# 启动ROS2节点
ros2 run your_package your_node

# 或使用launch文件
ros2 launch your_package main.launch.py
\`\`\`

## 项目结构

\`\`\`
project/
├── src/              # 源代码
│   ├── detector.py   # 检测模块
│   └── controller.py # 控制模块
├── launch/           # ROS2启动文件
├── config/           # 配置文件
├── docs/             # 文档
│   └── demo.mp4      # 演示视频
└── README.md
\`\`\`

## 演示视频

[点击观看演示视频](docs/demo.mp4)

或

![演示GIF](docs/demo.gif)

## 运行效果

![效果图1](docs/result1.png)
![效果图2](docs/result2.png)

## 遇到的问题与解决方案

### 问题1: xxx
**解决方案**: xxx

### 问题2: xxx
**解决方案**: xxx

## 未来改进

- [ ] 改进1
- [ ] 改进2

## 参考资料

1. [参考链接1](https://...)
2. [参考链接2](https://...)

## 致谢

感谢老师的指导和同学的帮助！
```

---

### 13.7.4 项目评分细则

| 评分项 | 权重 | 优秀(90-100) | 良好(75-89) | 及格(60-74) | 不及格(<60) |
|--------|------|-------------|-------------|-------------|-------------|
| **功能完整度** | 40% | 核心功能+扩展功能 | 核心功能完整 | 核心功能部分实现 | 功能不完整 |
| **技术难度** | 30% | 复杂算法+创新 | 使用多种技术 | 基本技术应用 | 技术过于简单 |
| **代码质量** | 15% | 结构清晰+注释完整 | 可读性好 | 可运行 | 代码混乱 |
| **文档报告** | 15% | 文档详细+视频优秀 | 文档完整 | 基本说明 | 文档缺失 |

**加分项**：
- 🌟 开源贡献（+5分）
- 🌟 创新性强（+5分）
- 🌟 实际部署（+10分）
- 🌟 技术难度高（+5分）

---

## 本周作业

### ✅ 必做

| 序号 | 任务 | 截止 | 完成 |
|------|------|------|------|
| 1 | 完成PyBullet仿真实验 | 本周三 | ☐ |
| 2 | 项目核心功能实现 | 本周五 | ☐ |
| 3 | 项目功能测试 | 本周六 | ☐ |
| 4 | 录制演示视频 | 本周日 | ☐ |
| 5 | 提交最终代码 | 下周一 | ☐ |

### 📦 提交清单

**最终提交内容**：
```
提交到GitHub仓库：
✓ 完整源代码
✓ README.md
✓ requirements.txt
✓ 演示视频
✓ 效果截图/数据

提交到课程平台：
✓ GitHub仓库链接
✓ 演示视频链接
✓ 项目报告PDF（可选）
```

---

## 参考资料

### 四足机器人

1. **教材**:
   - 《腿足机器人导论》 - MIT Press
   - 《动态行走机器人》 - Springer

2. **开源项目**:
   - [Unitree SDK](https://github.com/unitreerobotics/unitree_legged_sdk)
   - [Stanford Pupper](https://github.com/stanfordroboticsclub/StanfordQuadruped)
   - [OpenQuadruped](https://github.com/adham-elarabawy/open-quadruped)

3. **论文**:
   - "Learning Quadrupedal Locomotion over Challenging Terrain" (MIT, 2020)
   - "RMA: Rapid Motor Adaptation for Legged Robots" (Berkeley, 2021)

### PyBullet

- [官方文档](https://pybullet.org/wordpress/)
- [快速入门指南](https://docs.google.com/document/d/10sXEhzFRSnvFcl3XxNGhnD4N2SedqwdAvK3dsihxVUA/)
- [示例代码](https://github.com/bulletphysics/bullet3/tree/master/examples/pybullet)

---

## 课程总结

```
课程知识体系回顾：

┌─────────────────────────────────────────────────────────────┐
│                   AI机器人课程                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Week 1-3: 基础环境                                         │
│  ├── WSL + Ubuntu + ROS2                                   │
│  ├── Git + GitHub + VSCode                                 │
│  └── 命令行操作                                            │
│                                                             │
│  Week 4-8: 机器人基础                                       │
│  ├── Python编程                                            │
│  ├── 机器人运动学                                          │
│  ├── 传感器与数据处理                                      │
│  ├── Docker容器                                            │
│  └── Markdown文档                                          │
│                                                             │
│  Week 9: 数学基础（网课）                                   │
│  ├── 线性代数：矩阵、变换                                   │
│  ├── 运动学：正逆运动学、雅可比                             │
│  └── 视觉数学：卷积、特征提取                               │
│                                                             │
│  Week 10-11: AI视觉                                        │
│  ├── YOLO目标检测                                          │
│  └── Sort目标追踪                                          │
│                                                             │
│  Week 12-13: 综合应用                                       │
│  ├── OpenCV视觉处理                                        │
│  ├── 语音识别/合成                                         │
│  ├── 四足机器人入门                                        │
│  └── 期末项目实战                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 寄语

> 🎓 恭喜你完成了AI机器人课程的学习！
> 
> 从零开始，你已经掌握了：
> - Linux命令行与ROS2基础
> - 计算机视觉与深度学习
> - 机器人控制的数学原理
> - 实际项目开发能力
> 
> 这只是开始，机器人和AI的世界还有更多精彩等待探索！
> 
> **下一步建议**：
> 1. 深入学习某个感兴趣的方向（视觉/控制/规划）
> 2. 参加机器人竞赛（RoboCup、ICRA等）
> 3. 阅读前沿论文，关注ICRA、IROS、RSS会议
> 4. 为开源项目贡献代码
> 5. 考虑研究生深造或相关领域工作
> 
> **保持联系**：
> - 课程GitHub: [ai-robot-class](https://github.com/ai-robot-class/)
> - 课程网站: [course.a-real.me](https://course.a-real.me)
> 
> 祝未来一切顺利，期待你在AI机器人领域的精彩表现！🚀

---

*第13周结束！课程完成！*

*期末项目加油，我们答辩见！*
