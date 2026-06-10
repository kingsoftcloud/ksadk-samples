from workflow import build_agent_graph, prepare_state


# KSADK 会调用这个函数把 AgentEngine payload 转成 LangGraph 初始状态。
ksadk_prepare_state = prepare_state

# root_agent 是 agentengine.yaml 声明的入口变量。
root_agent = build_agent_graph()
