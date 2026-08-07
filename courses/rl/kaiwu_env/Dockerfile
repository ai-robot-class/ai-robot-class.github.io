# 开悟《王者荣耀》1v1 · 纯 CPU 强化学习环境
#
# 该镜像在 Linux 容器里用 Wine 运行开悟的 Windows gamecore（游戏逻辑核心），
# 并安装 hok_env SDK + PyTorch(CPU) 供强化学习训练/推理使用。
# gamecore 本体与 license.dat 不打进镜像，运行时通过挂载卷提供（见 docker-compose.yml 与 README）。

FROM ubuntu:20.04

# 便携 Wine 版本（Kron4ek wow64 纯 64 位构建，免 32 位库；已实测可跑通开悟 gamecore）
ARG WINE_VERSION=11.14
ARG WINE_TARBALL=wine-${WINE_VERSION}-amd64-wow64.tar.xz

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Asia/Seoul \
    WINEDEBUG=-all \
    WINEARCH=win64 \
    WINEPREFIX=/.wine \
    GAMECORE_PATH=/rl_framework/gamecore \
    GAMECORE_SERVER_BIND_ADDR=":23432" \
    PATH=/opt/wine/bin:$PATH \
    PYTHONUNBUFFERED=1

# 1) 基础系统依赖 + Python + Wine 运行所需的常用库（headless）
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates wget curl xz-utils \
        python3 python3-pip python3-dev \
        lsof procps psmisc net-tools \
        libfreetype6 libx11-6 libxext6 libxrender1 libgl1 libglib2.0-0 \
        fontconfig && \
    ln -sf /usr/bin/python3 /usr/bin/python && \
    rm -rf /var/lib/apt/lists/*

# 2) 打入便携 Wine（wow64，无需 i386 架构；解压即用）
#    如需离线构建：把 ${WINE_TARBALL} 放到本目录并改用 COPY 代替 wget。
RUN wget -q "https://github.com/Kron4ek/Wine-Builds/releases/download/${WINE_VERSION}/${WINE_TARBALL}" -O /tmp/wine.tar.xz && \
    mkdir -p /opt && tar -xf /tmp/wine.tar.xz -C /opt && \
    mv /opt/wine-${WINE_VERSION}-amd64-wow64 /opt/wine && \
    rm -f /tmp/wine.tar.xz && \
    /opt/wine/bin/wine --version && \
    # 预初始化 wine prefix，避免首次开局时的初始化延迟
    /opt/wine/bin/wine wineboot --init && sleep 3 || true

# 3) Python 依赖：hok SDK（新版，含 py3.6~3.9 预编译扩展）+ PyTorch(CPU) + 训练/通信库
#    Ubuntu 20.04 自带 Python 3.8，正好满足 hok 要求的 Python ≤ 3.9。
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip3 install --no-cache-dir -r /tmp/requirements.txt

# 4) gamecore-server 启动脚本（来自官方 aiarena/remote-gc-server，做本地化整理）
COPY scripts/ /rl_framework/remote-gc-server/
RUN chmod +x /rl_framework/remote-gc-server/*.sh /rl_framework/remote-gc-server/sgame_simulator_* || true

# 5) 训练/测试用 Python 脚本
COPY test_1v1_random.py /rl_framework/test_1v1_random.py
COPY config.json /rl_framework/config.json
COPY entrypoint.sh /rl_framework/entrypoint.sh
RUN chmod +x /rl_framework/entrypoint.sh

WORKDIR /rl_framework
EXPOSE 23432

# 默认前台启动 gamecore server（用 Wine 跑 Windows 模拟器）
ENTRYPOINT ["/rl_framework/entrypoint.sh"]
CMD ["serve"]
