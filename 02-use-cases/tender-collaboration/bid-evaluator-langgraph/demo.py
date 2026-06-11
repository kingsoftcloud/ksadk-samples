# 离线演示入口：不需要模型 key，用 fixture 快速验证输出结构。
from tools import render_demo_answer


if __name__ == "__main__":
    print(render_demo_answer('分析一组招投标协同材料，生成评分协同复盘方案。'))
