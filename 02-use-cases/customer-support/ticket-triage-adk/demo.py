from tools import render_demo_answer


DEMO_QUESTION = "客户说 Web UI 启动后没有响应，帮我排查。"


if __name__ == "__main__":
    # 离线演示入口：不连接真实客服系统，也不需要模型 key。
    print(render_demo_answer(DEMO_QUESTION))
