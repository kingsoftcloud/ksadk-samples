from tools import render_demo_answer


DEMO_QUESTION = '修复 Markdown 表格渲染不稳定的问题，并给出测试计划。'


if __name__ == "__main__":
    # 离线演示入口：不调用模型、不执行命令，只展示 Workspace/Sandbox 规划。
    print(render_demo_answer(DEMO_QUESTION))
