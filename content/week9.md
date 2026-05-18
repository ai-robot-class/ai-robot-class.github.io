# 第9周：机器人与机器视觉数学基础（网课）

**课时**: 3小时（线上录播课程）

> 💡 **说明**: 本周为网课，着重讲解机器人学和机器视觉的数学基础知识，为后续实战课程打下理论基础。

---

## 📋 本周课程大纲

| 模块 | 时长 | 主题 | 内容 |
|------|------|------|------|
| 模块1 | 50分钟 | 线性代数基础 | 向量、矩阵、坐标变换 |
| 模块2 | 50分钟 | 机器人运动学数学 | 正逆运动学、雅可比矩阵 |
| 模块3 | 50分钟 | 计算机视觉数学 | 图像表示、卷积、特征提取 |
| 作业 | 30分钟 | 习题练习 | 数学推导与编程验证 |

---

## 模块1：线性代数基础（50分钟）

### 1.1 为什么机器人需要数学？

```
机器人的本质是数学模型：

物理世界              数学世界              控制指令
  ↓                    ↓                    ↓
┌────────┐          ┌────────┐          ┌────────┐
│ 机械臂 │  建模→   │ 数学方程│  求解→   │ 电机角度│
│ 位置   │          │ 矩阵运算│          │ 速度   │
└────────┘          └────────┘          └────────┘
```

**核心数学工具**：
- **线性代数**：描述位置、姿态、变换
- **微积分**：描述速度、加速度、优化
- **概率统计**：处理传感器噪声、不确定性

---

### 1.2 向量与坐标系

#### 1.2.1 向量表示

```
三维空间中的点可以用向量表示：

       z
       ↑
       |    • P(x, y, z)
       |   /
       |  /
       | /
       |/________→ y
      /
     /
    ↓
   x

向量表示：p = [x]
              [y]
              [z]

Python实现：
```

```python
import numpy as np

# 定义三维空间中的点
p = np.array([1.0, 2.0, 3.0])
print(f"点P: {p}")

# 向量的长度（模）
length = np.linalg.norm(p)
print(f"向量长度: {length:.2f}")  # √(1²+2²+3²) = √14 ≈ 3.74

# 单位向量（方向）
unit_vector = p / length
print(f"单位向量: {unit_vector}")
```

#### 1.2.2 向量运算

| 运算 | 数学表示 | 物理意义 | Python |
|------|---------|---------|--------|
| 加法 | a + b | 位移叠加 | `a + b` |
| 减法 | a - b | 相对位置 | `a - b` |
| 点积 | a·b | 投影、夹角 | `np.dot(a, b)` |
| 叉积 | a×b | 法向量、力矩 | `np.cross(a, b)` |

```python
# 向量运算示例
a = np.array([1, 0, 0])  # x轴方向
b = np.array([0, 1, 0])  # y轴方向

# 点积：a·b = |a||b|cosθ
dot_product = np.dot(a, b)
print(f"点积: {dot_product}")  # 0 (垂直)

# 叉积：a×b，结果垂直于a和b
cross_product = np.cross(a, b)
print(f"叉积: {cross_product}")  # [0, 0, 1] (z轴方向)
```

---

### 1.3 矩阵与坐标变换

#### 1.3.1 旋转矩阵

```
二维旋转：

      y                y'
      ↑               ↗
      |              /
      |  θ          /
      |___→ x      /____→ x'
    
绕z轴旋转θ角：

R(θ) = [cos(θ)  -sin(θ)]
       [sin(θ)   cos(θ)]
```

```python
import numpy as np
import matplotlib.pyplot as plt

def rotation_matrix_2d(theta):
    """2D旋转矩阵"""
    return np.array([
        [np.cos(theta), -np.sin(theta)],
        [np.sin(theta),  np.cos(theta)]
    ])

# 旋转一个点
p = np.array([1, 0])  # x轴上的点
theta = np.pi / 4     # 旋转45度

R = rotation_matrix_2d(theta)
p_rotated = R @ p     # 矩阵乘法

print(f"原点: {p}")
print(f"旋转后: {p_rotated}")  # [0.707, 0.707]

# 可视化
plt.figure(figsize=(6, 6))
plt.arrow(0, 0, p[0], p[1], color='blue', width=0.02, label='原始')
plt.arrow(0, 0, p_rotated[0], p_rotated[1], color='red', width=0.02, label='旋转45°')
plt.xlim(-0.5, 1.5)
plt.ylim(-0.5, 1.5)
plt.grid(True)
plt.legend()
plt.axis('equal')
plt.title('2D旋转变换')
plt.show()
```

#### 1.3.2 齐次变换矩阵

> 同时表示旋转和平移

```
齐次变换矩阵（4×4）：

T = [R  t]    R: 3×3旋转矩阵
    [0  1]    t: 3×1平移向量

应用：p' = T * p
```

```python
def homogeneous_transform(rotation, translation):
    """
    构建齐次变换矩阵
    rotation: 3x3旋转矩阵
    translation: 3x1平移向量
    """
    T = np.eye(4)
    T[:3, :3] = rotation
    T[:3, 3] = translation
    return T

# 示例：旋转90度并平移(1,2,3)
R = np.array([
    [0, -1, 0],
    [1,  0, 0],
    [0,  0, 1]
])
t = np.array([1, 2, 3])

T = homogeneous_transform(R, t)
print("齐次变换矩阵:")
print(T)

# 应用变换
p = np.array([1, 0, 0, 1])  # 齐次坐标
p_transformed = T @ p
print(f"变换后: {p_transformed[:3]}")  # [1, 3, 3]
```

---

## 模块2：机器人运动学数学（50分钟）

### 2.1 正运动学（Forward Kinematics）

> **问题**：已知关节角度，求末端位置

```
机械臂示例：

    末端
     •
    /
   /  θ2
  /___
  |
  | θ1
  |___
  底座

正运动学：[θ1, θ2] → [x, y]
```

#### 2.1.1 DH参数法

**Denavit-Hartenberg参数**：描述连杆关系的标准方法

| 参数 | 含义 |
|------|------|
| a | 连杆长度 |
| α | 连杆扭转角 |
| d | 连杆偏距 |
| θ | 关节角 |

```python
def forward_kinematics_2dof(theta1, theta2, L1, L2):
    """
    2自由度机械臂正运动学
    theta1, theta2: 关节角度（弧度）
    L1, L2: 连杆长度
    """
    x = L1 * np.cos(theta1) + L2 * np.cos(theta1 + theta2)
    y = L1 * np.sin(theta1) + L2 * np.sin(theta1 + theta2)
    return x, y

# 示例
L1, L2 = 1.0, 1.0  # 两个连杆长度都是1
theta1 = np.pi / 4   # 45度
theta2 = np.pi / 4   # 45度

x, y = forward_kinematics_2dof(theta1, theta2, L1, L2)
print(f"末端位置: ({x:.2f}, {y:.2f})")
```

---

### 2.2 逆运动学（Inverse Kinematics）

> **问题**：已知末端位置，求关节角度（更难！）

```
逆运动学：[x, y] → [θ1, θ2]

特点：
• 可能有多个解（手肘向上/向下）
• 可能无解（超出工作空间）
• 可能有无穷多解（冗余机械臂）
```

#### 2.2.1 解析解法（简单机械臂）

```python
def inverse_kinematics_2dof(x, y, L1, L2):
    """
    2自由度机械臂逆运动学（解析解）
    """
    # 余弦定理求θ2
    D = (x**2 + y**2 - L1**2 - L2**2) / (2 * L1 * L2)
    
    # 检查是否有解
    if abs(D) > 1:
        raise ValueError("目标点超出工作空间")
    
    # 手肘向上的解
    theta2 = np.arccos(D)
    theta1 = np.arctan2(y, x) - np.arctan2(L2*np.sin(theta2), L1+L2*np.cos(theta2))
    
    return theta1, theta2

# 测试：先正运动学，再逆运动学
theta1_target = np.pi / 3
theta2_target = np.pi / 6

x, y = forward_kinematics_2dof(theta1_target, theta2_target, L1, L2)
print(f"正运动学: θ1={theta1_target:.2f}, θ2={theta2_target:.2f} → ({x:.2f}, {y:.2f})")

theta1_solved, theta2_solved = inverse_kinematics_2dof(x, y, L1, L2)
print(f"逆运动学: ({x:.2f}, {y:.2f}) → θ1={theta1_solved:.2f}, θ2={theta2_solved:.2f}")
print(f"误差: Δθ1={abs(theta1_target-theta1_solved):.4f}, Δθ2={abs(theta2_target-theta2_solved):.4f}")
```

#### 2.2.2 数值解法（复杂机械臂）

```python
from scipy.optimize import fsolve

def ik_numerical(target_pos, L1, L2, initial_guess=[0, 0]):
    """
    数值法求解逆运动学
    """
    def equations(theta):
        x, y = forward_kinematics_2dof(theta[0], theta[1], L1, L2)
        return [x - target_pos[0], y - target_pos[1]]
    
    solution = fsolve(equations, initial_guess)
    return solution

# 测试
target = [1.0, 1.0]
theta_solution = ik_numerical(target, L1, L2)
print(f"数值解: θ1={theta_solution[0]:.2f}, θ2={theta_solution[1]:.2f}")

# 验证
x_check, y_check = forward_kinematics_2dof(theta_solution[0], theta_solution[1], L1, L2)
print(f"验证: 目标({target[0]:.2f}, {target[1]:.2f}), 实际({x_check:.2f}, {y_check:.2f})")
```

---

### 2.3 雅可比矩阵（Jacobian Matrix）

> 描述关节速度与末端速度的关系

```
雅可比矩阵：

v = J(θ) * θ̇

v: 末端速度（笛卡尔空间）
θ̇: 关节速度（关节空间）
J: 雅可比矩阵
```

```python
def jacobian_2dof(theta1, theta2, L1, L2):
    """
    2自由度机械臂雅可比矩阵
    """
    J = np.array([
        [-L1*np.sin(theta1) - L2*np.sin(theta1+theta2), -L2*np.sin(theta1+theta2)],
        [ L1*np.cos(theta1) + L2*np.cos(theta1+theta2),  L2*np.cos(theta1+theta2)]
    ])
    return J

# 示例：给定关节速度，求末端速度
theta1, theta2 = np.pi/4, np.pi/4
joint_velocity = np.array([0.1, 0.1])  # 关节速度 (rad/s)

J = jacobian_2dof(theta1, theta2, L1, L2)
end_velocity = J @ joint_velocity

print(f"雅可比矩阵:\n{J}")
print(f"关节速度: {joint_velocity}")
print(f"末端速度: {end_velocity}")
```

**雅可比矩阵的应用**：
1. **速度映射**：关节速度 → 末端速度
2. **力映射**：末端力 → 关节力矩
3. **奇异性检测**：det(J)=0 时机械臂失去自由度
4. **速度级逆运动学**：v_target = J(θ) * Δθ → Δθ = J^(-1) * v_target

---

## 模块3：计算机视觉数学（50分钟）

### 3.1 图像的数学表示

#### 3.1.1 数字图像

```
图像 = 矩阵

灰度图像（单通道）：
I(x, y) ∈ [0, 255]

   x →
y  ┌──────────┐
↓  │ 255  200 │  明亮
   │ 100   50 │  较暗
   └──────────┘

彩色图像（三通道）：
R(x, y), G(x, y), B(x, y)
```

```python
import cv2
import numpy as np
import matplotlib.pyplot as plt

# 创建一个简单的灰度图像
img = np.array([
    [255, 200, 150],
    [200, 150, 100],
    [150, 100,  50]
], dtype=np.uint8)

print(f"图像形状: {img.shape}")
print(f"图像矩阵:\n{img}")
print(f"像素(0,0)的值: {img[0, 0]}")

# 显示图像
plt.imshow(img, cmap='gray')
plt.colorbar()
plt.title('数字图像矩阵')
plt.show()
```

---

### 3.2 卷积运算（Convolution）

> 卷积是计算机视觉和深度学习的核心运算

#### 3.2.1 什么是卷积？

```
卷积 = 滑动窗口 × 加权求和

原图像 I:           卷积核 K:
┌────────┐         ┌────┐
│1 2 3 4 │         │1  0│
│5 6 7 8 │    *    │0 -1│
│9 0 1 2 │         └────┘
└────────┘

过程：
1. 将卷积核放在图像左上角
2. 对应元素相乘并求和
3. 移动卷积核到下一位置
4. 重复直到遍历整个图像
```

```python
def convolve2d_manual(image, kernel):
    """
    手动实现2D卷积（教学用）
    """
    img_h, img_w = image.shape
    ker_h, ker_w = kernel.shape
    
    # 输出图像大小
    out_h = img_h - ker_h + 1
    out_w = img_w - ker_w + 1
    output = np.zeros((out_h, out_w))
    
    # 滑动窗口
    for i in range(out_h):
        for j in range(out_w):
            # 提取窗口
            window = image[i:i+ker_h, j:j+ker_w]
            # 卷积运算
            output[i, j] = np.sum(window * kernel)
    
    return output

# 示例图像
image = np.array([
    [1, 2, 3, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12]
], dtype=float)

# 边缘检测卷积核
kernel = np.array([
    [ 1,  0],
    [ 0, -1]
])

result = convolve2d_manual(image, kernel)
print("原图像:")
print(image)
print("\n卷积核:")
print(kernel)
print("\n卷积结果:")
print(result)
```

#### 3.2.2 常见卷积核及其作用

```python
# 1. 边缘检测（Sobel算子）
sobel_x = np.array([
    [-1, 0, 1],
    [-2, 0, 2],
    [-1, 0, 1]
])

sobel_y = np.array([
    [-1, -2, -1],
    [ 0,  0,  0],
    [ 1,  2,  1]
])

# 2. 模糊（均值滤波）
blur_kernel = np.ones((3, 3)) / 9

# 3. 锐化
sharpen = np.array([
    [ 0, -1,  0],
    [-1,  5, -1],
    [ 0, -1,  0]
])

# 使用OpenCV应用卷积
img = cv2.imread('test.jpg', cv2.IMREAD_GRAYSCALE)

edges_x = cv2.filter2D(img, -1, sobel_x)
edges_y = cv2.filter2D(img, -1, sobel_y)
blurred = cv2.filter2D(img, -1, blur_kernel)
sharpened = cv2.filter2D(img, -1, sharpen)

# 可视化
fig, axes = plt.subplots(2, 3, figsize=(12, 8))
axes[0, 0].imshow(img, cmap='gray')
axes[0, 0].set_title('原图')
axes[0, 1].imshow(edges_x, cmap='gray')
axes[0, 1].set_title('X方向边缘')
axes[0, 2].imshow(edges_y, cmap='gray')
axes[0, 2].set_title('Y方向边缘')
axes[1, 0].imshow(blurred, cmap='gray')
axes[1, 0].set_title('模糊')
axes[1, 1].imshow(sharpened, cmap='gray')
axes[1, 1].set_title('锐化')
plt.tight_layout()
plt.show()
```

---

### 3.3 特征提取数学

#### 3.3.1 梯度与边缘

```
图像梯度：

∇I = [∂I/∂x]
     [∂I/∂y]

梯度幅值：|∇I| = √((∂I/∂x)² + (∂I/∂y)²)
梯度方向：θ = arctan(∂I/∂y / ∂I/∂x)
```

```python
def compute_gradient(image):
    """计算图像梯度"""
    # 使用Sobel算子
    grad_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
    
    # 梯度幅值
    magnitude = np.sqrt(grad_x**2 + grad_y**2)
    
    # 梯度方向
    direction = np.arctan2(grad_y, grad_x)
    
    return magnitude, direction, grad_x, grad_y

# 测试
img = cv2.imread('test.jpg', cv2.IMREAD_GRAYSCALE)
mag, dire, gx, gy = compute_gradient(img)

fig, axes = plt.subplots(2, 2, figsize=(10, 10))
axes[0, 0].imshow(gx, cmap='gray')
axes[0, 0].set_title('X梯度')
axes[0, 1].imshow(gy, cmap='gray')
axes[0, 1].set_title('Y梯度')
axes[1, 0].imshow(mag, cmap='gray')
axes[1, 0].set_title('梯度幅值（边缘强度）')
axes[1, 1].imshow(dire, cmap='hsv')
axes[1, 1].set_title('梯度方向')
plt.tight_layout()
plt.show()
```

#### 3.3.2 Harris角点检测

> 角点 = 两个方向梯度都很大的点

```
Harris矩阵：

M = [Σ(Ix²)    Σ(IxIy)]
    [Σ(IxIy)   Σ(Iy²) ]

角点响应：
R = det(M) - k * trace(M)²

R > threshold → 角点
```

```python
def harris_corner_detection(image, k=0.04, threshold=0.01):
    """Harris角点检测"""
    # 计算梯度
    Ix = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
    Iy = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
    
    # Harris矩阵的元素
    Ixx = Ix * Ix
    Iyy = Iy * Iy
    Ixy = Ix * Iy
    
    # 高斯窗口平滑
    Ixx = cv2.GaussianBlur(Ixx, (5, 5), 1)
    Iyy = cv2.GaussianBlur(Iyy, (5, 5), 1)
    Ixy = cv2.GaussianBlur(Ixy, (5, 5), 1)
    
    # 计算角点响应
    det = Ixx * Iyy - Ixy * Ixy
    trace = Ixx + Iyy
    R = det - k * trace * trace
    
    # 阈值化
    corners = R > threshold * R.max()
    
    return R, corners

# 测试
img = cv2.imread('test.jpg', cv2.IMREAD_GRAYSCALE)
R, corners = harris_corner_detection(img)

# 可视化
img_color = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
img_color[corners] = [0, 0, 255]  # 红色标记角点

plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.imshow(img, cmap='gray')
plt.title('原图')
plt.subplot(1, 2, 2)
plt.imshow(cv2.cvtColor(img_color, cv2.COLOR_BGR2RGB))
plt.title('角点检测结果')
plt.show()
```

---

### 3.4 相机成像模型

#### 3.4.1 针孔相机模型

```
三维世界点 → 二维图像点

         世界坐标系 (Xw, Yw, Zw)
              ↓
         相机坐标系 (Xc, Yc, Zc)
              ↓
         图像平面 (u, v)

投影方程：
u = fx * (Xc/Zc) + cx
v = fy * (Yc/Zc) + cy

其中：
(fx, fy): 焦距
(cx, cy): 主点
```

```python
def project_3d_to_2d(point_3d, camera_matrix):
    """
    3D点投影到2D图像
    point_3d: [X, Y, Z]
    camera_matrix: 3x3相机内参矩阵
    """
    X, Y, Z = point_3d
    fx, fy = camera_matrix[0, 0], camera_matrix[1, 1]
    cx, cy = camera_matrix[0, 2], camera_matrix[1, 2]
    
    # 投影
    u = fx * (X / Z) + cx
    v = fy * (Y / Z) + cy
    
    return np.array([u, v])

# 相机内参矩阵
K = np.array([
    [800,   0, 320],  # fx, 0, cx
    [  0, 800, 240],  # 0, fy, cy
    [  0,   0,   1]
])

# 三维点
point_3d = np.array([1.0, 0.5, 2.0])  # 距离相机2米

# 投影
point_2d = project_3d_to_2d(point_3d, K)
print(f"3D点: {point_3d}")
print(f"投影到图像: ({point_2d[0]:.1f}, {point_2d[1]:.1f})")
```

---

## 本周作业

### ✅ 必做题

#### 1. 线性代数练习

```python
# TODO: 完成以下练习
# 1. 实现3D旋转矩阵（绕x/y/z轴）
# 2. 验证旋转矩阵性质：R * R^T = I
# 3. 组合两个旋转变换
```

#### 2. 运动学练习

```python
# TODO: 3自由度机械臂
# 1. 实现正运动学函数
# 2. 实现逆运动学函数
# 3. 绘制工作空间
```

#### 3. 卷积练习

```python
# TODO: 图像处理
# 1. 手动实现3x3卷积
# 2. 应用不同卷积核观察效果
# 3. 比较手动实现与OpenCV的结果
```

### 🌟 选做题（加分）

1. **推导雅可比矩阵**：手推3自由度机械臂的雅可比矩阵
2. **相机标定**：使用棋盘格标定相机内参
3. **特征匹配**：实现SIFT/ORB特征点匹配

---

## 📚 参考资料

### 教材

1. **《机器人学导论》** - John J. Craig
2. **《计算机视觉：算法与应用》** - Richard Szeliski
3. **《深度学习》** - Ian Goodfellow

### 在线资源

- [3Blue1Brown 线性代数系列](https://www.3blue1brown.com/topics/linear-algebra) - 直观数学动画
- [机器人学公开课](https://www.youtube.com/user/StanfordCS223A) - Stanford CS223A
- [OpenCV教程](https://docs.opencv.org/4.x/d9/df8/tutorial_root.html)

### Python库

```bash
# 科学计算
pip install numpy scipy matplotlib

# 计算机视觉
pip install opencv-python opencv-contrib-python

# 机器人工具
pip install roboticstoolbox-python
```

---

## 📊 知识点总结

```
第9周知识图谱：

┌─────────────────────────────────────────────────────────────┐
│                   数学基础                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  线性代数              运动学数学          视觉数学         │
│  ├── 向量             ├── 正运动学        ├── 图像矩阵     │
│  ├── 矩阵             ├── 逆运动学        ├── 卷积运算     │
│  ├── 旋转矩阵         ├── 雅可比矩阵      ├── 特征提取     │
│  └── 齐次变换         └── 奇异性分析      └── 相机模型     │
│                                                             │
│  应用场景：                                                 │
│  • 机械臂轨迹规划                                           │
│  • 机器人定位导航                                           │
│  • 视觉目标检测                                             │
│  • 图像识别分类                                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 下周预告

> **第10周：物体检测与识别（已完成）**
> **第11周：目标追踪（已完成）**
> **第12周：视觉与语音入门 + 期末项目启动**
> - OpenCV实战
> - 语音识别/合成入门
> - 项目分组与选题

---

*第9周网课结束！数学基础打好，后面实战更轻松！*
