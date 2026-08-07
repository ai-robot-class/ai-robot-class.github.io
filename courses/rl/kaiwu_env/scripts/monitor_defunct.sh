#!/bin/bash
# 定期清理 Wine/模拟器留下的僵尸(defunct)进程
while true; do
    ps -e f | grep -v monitor_defunct.sh | grep defunct | grep -v grep | awk '{print $1}' | xargs -r kill -s 9
    sleep 10
done
