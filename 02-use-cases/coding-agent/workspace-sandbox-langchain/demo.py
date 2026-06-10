from tools import render_demo_answer


DEMO_QUESTION = "修复 Markdown 表格渲染不稳定的问题，并给出测试计划。"


if __name__ == "__main__":
    # 离线演示入口：不需要模型 key，也不会访问外部服务。
    print(render_demo_answer(DEMO_QUESTION))
