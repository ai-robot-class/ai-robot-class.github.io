#!/bin/bash
# 后台启动 gamecore server，并等待端口就绪
LOG_DIR=${LOG_DIR:-"/aiarena/logs/"}
mkdir -p "$LOG_DIR"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
nohup bash "$SCRIPT_DIR/run_and_monitor_gamecore_server.sh" >/dev/null 2>&1 &

echo "等待 gamecore server 监听 ${GAMECORE_SERVER_BIND_ADDR:-:23432} ..."
while true; do
    lsof -i "${GAMECORE_SERVER_BIND_ADDR:-:23432}" && break
    sleep 1
done
echo "gamecore server 已就绪。日志：${LOG_DIR}/gamecore-server.log"
