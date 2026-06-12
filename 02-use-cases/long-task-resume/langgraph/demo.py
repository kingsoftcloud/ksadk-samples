from workflow import build_agent_graph, prepare_state


DEMO_QUESTION = "调研国产 AI Agent Runtime 的市场格局、竞品、落地风险和下一步建议。"


if __name__ == "__main__":
    # 离线演示入口：不依赖模型 key、数据库或云账号，适合快速查看最终报告内容。
    state = prepare_state({"input": DEMO_QUESTION}, {})
    result = build_agent_graph().invoke(state)
    print(result["answer"])
