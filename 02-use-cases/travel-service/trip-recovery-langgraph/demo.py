from tools import render_demo_answer


DEMO_QUESTION = "分析一批行程变更事件，生成旅游服务恢复方案。"


if __name__ == "__main__":
    # 离线演示入口：不访问真实业务系统，也不需要模型 key。
    print(render_demo_answer(DEMO_QUESTION))
