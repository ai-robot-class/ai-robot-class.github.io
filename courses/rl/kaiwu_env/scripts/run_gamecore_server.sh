#!/bin/bash
# 启动 gamecore-server（本包内含 Linux 版 server 二进制；模拟器本体为 Windows，经 Wine 运行）
GAMECORE_PATH=${GAMECORE_PATH:-"/rl_framework/gamecore/"}
GAMECORE_SERVER_BIND_ADDR=${GAMECORE_SERVER_BIND_ADDR:-":23432"}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$GAMECORE_PATH" || exit 1

if [ -f "gamecore-server-linux-amd64" ] && [ -z "${GAMECORE_SERVER_USE_WINE}" ]; then
    # 用 Linux 版 server 调度，模拟器通过 Wine 包装脚本运行
    ./gamecore-server-linux-amd64 server --server-address="${GAMECORE_SERVER_BIND_ADDR}" \
        --simulator-remote-bin "${SCRIPT_DIR}/sgame_simulator_remote_zmq" \
        --simulator-repeat-bin "${SCRIPT_DIR}/sgame_simulator_repeated_zmq"
else
    # 回退：整套 server 也用 Wine 跑 Windows 版
    export WINEPATH="${GAMECORE_PATH}/lib/;${GAMECORE_PATH}/bin/"
    wine gamecore-server.exe server --server-address="${GAMECORE_SERVER_BIND_ADDR}"
fi
