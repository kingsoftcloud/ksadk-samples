from tools import render_demo_answer


DEMO_QUESTION = "审阅一份合作合同，提取关键条款和谈判建议。"


if __name__ == "__main__":
    # 离线演示入口：不访问真实业务系统，也不需要模型 key。
    print(render_demo_answer(DEMO_QUESTION))
