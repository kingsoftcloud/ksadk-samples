from tools import render_demo_answer


DEMO_QUESTION = "分析支付服务 5xx 激增和延迟升高的告警。"


if __name__ == "__main__":
    # 离线演示入口：不访问真实外部系统，也不需要模型 key。
    print(render_demo_answer(DEMO_QUESTION))
