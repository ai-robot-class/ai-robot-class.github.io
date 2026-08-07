import json
import sys
import os

# gamecore-server 生成的对局配置里 core_assets / abs_file 为绝对路径，
# 模拟器需要相对于工作目录的路径，这里做一次转换。
if __name__ == "__main__":
    conf_base = sys.argv[1]
    conf_new = sys.argv[2]
    base_path = sys.argv[3]

    with open(conf_base) as f:
        data = json.load(f)

    data["core_assets"] = os.path.relpath(data["core_assets"], base_path)
    data["abs_file"] = os.path.relpath(data["abs_file"], base_path)

    with open(conf_new, "w") as f:
        json.dump(data, f)
