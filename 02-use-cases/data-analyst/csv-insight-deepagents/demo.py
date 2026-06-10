from tools import render_demo_answer


DEMO_QUESTION = "分析 Agent 调试功能的激活率和留存变化。"


if __name__ == "__main__":
    # 离线演示入口：不读取真实 CSV，也不会访问外部数据源。
    print(render_demo_answer(DEMO_QUESTION))
