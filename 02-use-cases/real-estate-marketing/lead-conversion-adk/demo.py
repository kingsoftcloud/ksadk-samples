from tools import render_demo_answer


if __name__ == "__main__":
    question = '分析一批楼盘营销线索，生成转化协同方案。'
    # 离线演示入口：不访问真实业务系统，也不需要模型 key。
    print(render_demo_answer(question))
