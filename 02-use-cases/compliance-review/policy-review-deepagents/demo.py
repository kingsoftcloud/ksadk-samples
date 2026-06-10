from tools import render_demo_answer


DEMO_QUESTION = "审阅一份对外发布材料，找出合规风险并给整改建议。"


if __name__ == "__main__":
    # 离线演示入口：不访问真实业务系统，也不需要模型 key。
    print(render_demo_answer(DEMO_QUESTION))
