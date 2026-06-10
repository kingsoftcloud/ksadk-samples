from tools import render_demo_answer


DEMO_QUESTION = "验证本地 Web UI 首页无法点击发送按钮的问题。"


if __name__ == "__main__":
    # 离线演示入口：不需要模型 key，也不会访问外部服务。
    print(render_demo_answer(DEMO_QUESTION))
