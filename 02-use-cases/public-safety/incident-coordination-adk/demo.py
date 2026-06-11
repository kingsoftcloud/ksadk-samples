from tools import render_demo_answer


if __name__ == "__main__":
    question = '分析一批公共安全事件线索，生成联动处置方案。'
    # 离线演示入口：不访问真实业务系统，也不需要模型 key。
    print(render_demo_answer(question))
