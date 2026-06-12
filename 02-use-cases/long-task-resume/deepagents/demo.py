from tools import render_demo_answer


DEMO_QUESTION = "调研国产 AI Agent Runtime 的市场格局、竞品、落地风险和下一步建议。"


if __name__ == "__main__":
    # 离线演示入口：不依赖模型 key、数据库或云账号，适合 clone 后立即查看效果。
    print(render_demo_answer(DEMO_QUESTION))
