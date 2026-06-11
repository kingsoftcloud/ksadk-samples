from tools import render_demo_answer


DEMO_QUESTION = "分析一组产品实验数据，给出运营优化计划。"


if __name__ == "__main__":
    # 离线演示入口：不访问真实业务系统，也不需要模型 key。
    print(render_demo_answer(DEMO_QUESTION))
