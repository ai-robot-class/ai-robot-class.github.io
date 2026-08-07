#!/bin/bash
# 循环守护 gamecore server：崩溃自动重启，同时清理僵尸进程
LOG_DIR=${LOG_DIR:-"/aiarena/logs/"}
LOG_FILE=${LOG_DIR}/gamecore-server.log

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
nohup bash "$SCRIPT_DIR/monitor_defunct.sh" > /dev/null 2>&1 &

while true; do
    echo "[`date`] restart server"
    mkdir -p "$LOG_DIR"
    bash "$SCRIPT_DIR/run_gamecore_server.sh" >> "$LOG_FILE" 2>&1
    sleep 1
done
