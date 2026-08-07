#!/bin/bash
# 容器入口。支持三种模式：
#   serve  : 前台启动 gamecore server（默认）
#   test   : 后台启动 server + 跑随机智能体冒烟测试（test_1v1_random.py）
#   bash   : 进入交互 shell（自行手动启动）
set -e

MODE=${1:-serve}
GC="${GAMECORE_PATH:-/rl_framework/gamecore}"

# 运行前自检：gamecore 与 license 是否已挂载
preflight() {
    if [ ! -x "${GC}/gamecore-server-linux-amd64" ] && [ ! -f "${GC}/gamecore-server.exe" ]; then
        echo "[错误] 未找到 gamecore：请把开悟 gamecore 挂载到 ${GC}（见 README / docker-compose.yml）。"
        exit 1
    fi
    if [ ! -f "${GC}/core_assets/license.dat" ]; then
        echo "[警告] 未发现 ${GC}/core_assets/license.dat。"
        echo "       开悟 gamecore 需要从开悟平台申请的 license.dat 才能真正开始对局，"
        echo "       否则 server 可启动但无法完整跑完一局。"
    fi
    # gamecore 内自带 server 二进制可能无执行权限（挂载卷），补一下
    chmod +x "${GC}/gamecore-server-linux-amd64" 2>/dev/null || true
    chmod +x "${GC}/bin/"* 2>/dev/null || true
}

case "$MODE" in
    serve)
        preflight
        echo "== 启动 gamecore server（前台，Wine 运行 Windows 模拟器）=="
        export SIMULATOR_USE_WINE=1
        exec bash /rl_framework/remote-gc-server/run_gamecore_server.sh
        ;;
    test)
        preflight
        echo "== 后台启动 gamecore server 并运行随机智能体冒烟测试 =="
        export SIMULATOR_USE_WINE=1
        bash /rl_framework/remote-gc-server/start_gamecore_server.sh
        cd /rl_framework
        exec python3 test_1v1_random.py
        ;;
    bash|sh)
        exec /bin/bash
        ;;
    *)
        exec "$@"
        ;;
esac
