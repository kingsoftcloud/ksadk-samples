from tools import render_demo_answer


DEMO_QUESTION = "组织一个团队把 samples 仓库补齐。"


if __name__ == "__main__":
    # 离线演示入口：不启动真实子 Agent，也不需要模型 key。
    print(render_demo_answer(DEMO_QUESTION))
