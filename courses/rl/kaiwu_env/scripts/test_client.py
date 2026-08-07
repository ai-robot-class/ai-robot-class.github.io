"""向 gamecore-server 直接发一局内置规则 AI 的 1v1 对局请求，用于验证 server 是否正常。

用法（容器内 gamecore server 已启动后）：
    python3 scripts/test_client.py
成功会打印 Success 以及一个请求 ID，并在 gamecore/simulator_output 生成 .abs 回放文件。
"""
import requests

url = "http://127.0.0.1:23432/v2/newGame"
headers = {"Content-Type": "application/json"}
data = {
    "simulator_type": "remote_repeat",
    "runtime_id": "test-runtime-id-0",
    "simulator_config": {
        "game_mode": "1v1",
        "hero_conf": [
            {"hero_id": 139},
            {"hero_id": 139},
        ],
    },
}

resp = requests.post(url=url, json=data, headers=headers, verify=False)
if resp.ok:
    print("Success", resp.json())
else:
    print("Failed", resp)
