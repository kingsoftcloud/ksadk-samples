from agent import ksadk_prepare_state, root_agent


DEMO_QUESTION = "帮我恢复一个中断的长任务，并说明哪些工具调用不应该重复执行。"


if __name__ == "__main__":
    # 离线演示入口：不依赖模型 key、数据库或云账号，适合 clone 后立即查看效果。
    state = ksadk_prepare_state({"input": DEMO_QUESTION}, {})
    result = root_agent.invoke(state)
    print(result["answer"])
