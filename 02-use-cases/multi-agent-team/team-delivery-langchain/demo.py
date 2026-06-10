from tools import render_demo_answer


DEMO_QUESTION = "组织一个团队把 samples 仓库补齐。"


if __name__ == "__main__":
    # 离线演示入口：不需要模型 key，也不会访问外部服务。
    print(render_demo_answer(DEMO_QUESTION))
