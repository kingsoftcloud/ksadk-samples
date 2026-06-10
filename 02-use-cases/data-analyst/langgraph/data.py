from __future__ import annotations

# 本地公开示例数据。真实项目可以把这里替换为知识库、Workspace 文件或业务 API。
SCENARIO_EVIDENCE = [{'id': 'activation', 'title': '激活率', 'content': '30 秒跑通 demo、Web UI 首屏体验和 README 路径清晰度影响新用户激活。'},
 {'id': 'retention', 'title': '留存', 'content': '可复现脚本、错误提示和场景连续性会影响用户第二次打开仓库。'},
 {'id': 'conversion', 'title': '转化', 'content': '真实截图、GIF、对比矩阵和可部署样例会提高 Star 与贡献转化。'},
 {'id': 'quality', 'title': '质量', 'content': '门禁覆盖 README、敏感信息、样例导入、运行 smoke 和 CI 状态。'}]

# 演示行动项模板，tools.py 会根据检索到的证据生成最终计划。
ACTION_TEMPLATES = ['定义指标口径', '抽取样例数据', '生成洞察排序', '提出实验建议']
