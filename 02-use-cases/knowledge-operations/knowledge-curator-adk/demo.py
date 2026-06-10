from tools import render_demo_answer


DEMO_QUESTION = "整理一批用户反馈，把它转成可发布的知识库更新计划。"


if __name__ == "__main__":
    # 离线演示入口：不访问真实业务系统，也不需要模型 key。
    print(render_demo_answer(DEMO_QUESTION))
