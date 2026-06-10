from __future__ import annotations

# 本地公开示例数据。真实项目可以把这里替换为知识库、Workspace 文件或业务 API。
SCENARIO_EVIDENCE = [{'id': 'scope', 'title': '变更边界', 'content': '先定位模块职责，再决定是否需要抽 helper，避免样例代码膨胀成不可维护脚本。'},
 {'id': 'tests', 'title': '测试优先', 'content': '先写失败测试证明缺口，再实现最小代码，最后跑目标测试和公开门禁。'},
 {'id': 'review', 'title': '评审重点', 'content': '关注行为回归、缺失测试、敏感信息、错误提示和 README 是否可照做。'},
 {'id': 'release',
  'title': '发布检查',
  'content': '发布前需要 public-preflight、smoke install、README 链接和 GitHub Actions 全绿。'}]

# 演示行动项模板，tools.py 会根据检索到的证据生成最终计划。
ACTION_TEMPLATES = ['生成修改计划', '列出测试用例', '给出补丁位置', '整理发布风险']
