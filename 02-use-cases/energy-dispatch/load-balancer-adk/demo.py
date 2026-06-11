from tools import render_demo_answer


DEMO_QUESTION = "根据负荷预测和设备状态，生成能源调度建议。"


if __name__ == "__main__":
    # 离线演示入口：不访问真实业务系统，也不需要模型 key。
    print(render_demo_answer(DEMO_QUESTION))
