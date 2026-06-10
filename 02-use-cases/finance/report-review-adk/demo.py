from tools import render_demo_answer


DEMO_QUESTION = "审阅本季度收入、毛利率和现金流风险。"


if __name__ == "__main__":
    # 离线演示入口：不访问真实财务系统，也不需要模型 key。
    print(render_demo_answer(DEMO_QUESTION))
