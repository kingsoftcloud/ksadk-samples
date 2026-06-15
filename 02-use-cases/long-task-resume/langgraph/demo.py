from workflow import build_agent_graph, prepare_state


DEMO_QUESTION = "调研 GLP-1 受体激动剂在肥胖和 2 型糖尿病治疗中的临床证据、药物经济学、支付准入和真实世界安全性。"


if __name__ == "__main__":
    # 离线演示入口：不依赖模型 key、数据库或云账号，适合快速查看最终报告内容。
    state = prepare_state({"input": DEMO_QUESTION}, {})
    result = build_agent_graph().invoke(state)
    print(result["answer"])
