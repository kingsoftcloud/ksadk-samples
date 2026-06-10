from tools import render_demo_answer


DEMO_QUESTION = '生成一份 Agent Runtime Platform 选型报告。'


if __name__ == "__main__":
    # 离线演示入口：不调用模型，直接展示 DeepAgents 样例的报告输出形态。
    print(render_demo_answer(DEMO_QUESTION))
