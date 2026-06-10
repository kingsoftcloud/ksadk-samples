from __future__ import annotations

# 本地公开示例数据。真实项目可以把这里替换为知识库、Workspace 文件或业务 API。
# 字段参考 SWE-agent、OpenHands、ADK SWE Benchmark Agent 的工程闭环：定位、修改、测试、提交。
SCENARIO_EVIDENCE = [
    {
        'id': 'scope',
        'title': '变更边界',
        'content': '先定位模块职责，再决定是否需要抽 helper，避免样例代码膨胀成不可维护脚本。',
        'file_hint': 'workflow.py / tools.py',
        'risk': '改动跨越入口和工具层时，容易破坏 agentengine.yaml 的入口约定。',
    },
    {
        'id': 'tests',
        'title': '测试优先',
        'content': '先写失败测试证明缺口，再实现最小代码，最后跑目标测试和公开门禁。',
        'file_hint': 'tests/test_sample_structure.py',
        'risk': '只跑 demo.py 不能证明 README、敏感信息扫描和导入 smoke 都安全。',
    },
    {
        'id': 'review',
        'title': '评审重点',
        'content': '关注行为回归、缺失测试、敏感信息、错误提示和 README 是否可照做。',
        'file_hint': 'README.md / data.py',
        'risk': '公开样例如果包含内网地址、真实账号或不可复现步骤，会直接影响开源可信度。',
    },
    {
        'id': 'release',
        'title': '发布检查',
        'content': '发布前需要 public-preflight、smoke install、README 链接和 GitHub Actions 全绿。',
        'file_hint': 'Makefile / GitHub Actions',
        'risk': '本地通过但远端 CI 失败时不能宣称样例可用。',
    },
]

# 演示行动项模板，tools.py 会根据检索到的证据生成最终计划。
ACTION_TEMPLATES = ['生成修改计划', '列出测试用例', '给出补丁位置', '整理发布风险']

# Coding Agent 的演示测试矩阵。真实项目可以把它替换为 pytest、ruff、mypy、e2e 或 benchmark 结果。
TEST_MATRIX = [
    ('目标回归测试', '先验证新增行为会失败，再实现修复。'),
    ('样例 smoke', '运行 demo.py 或 agentengine run，确认用户路径可复现。'),
    ('公开门禁', '执行 make public-preflight，覆盖敏感信息和 README 质量。'),
]
