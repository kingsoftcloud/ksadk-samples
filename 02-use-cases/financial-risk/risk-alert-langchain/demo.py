from tools import render_demo_answer


if __name__ == "__main__":
    question = '分析一批金融风控信号，生成风险处置方案。'
    # 离线演示入口：不访问真实业务系统，也不需要模型 key。
    print(render_demo_answer(question))
