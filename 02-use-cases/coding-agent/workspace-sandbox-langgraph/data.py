from __future__ import annotations

# 模拟 Workspace 中用户上传或仓库挂载的文件。真实项目应通过 Workspace 工具读取。
WORKSPACE_FILES = [
    {
        'path': 'app/markdown_renderer.py',
        'purpose': '负责把模型输出渲染为 CommonMark 子集。',
        'finding': '表格前后缺少空行时，部分渲染器会把表格当成普通文本。',
    },
    {
        'path': 'tests/test_markdown_renderer.py',
        'purpose': '覆盖列表、表格和代码块的修复行为。',
        'finding': '已有用例覆盖列表，但缺少表格和混合列表的回归测试。',
    },
    {
        'path': 'README.md',
        'purpose': '说明 repair_markdown 的可选开启方式。',
        'finding': '需要明确默认关闭、用户按需启用，以及不会保证所有 LLM 输出严格 CommonMark。',
    },
]

# 模拟 Sandbox 中应执行的命令。真实项目应由 Sandbox 工具运行并收集 stdout/stderr/exit code。
SANDBOX_COMMANDS = [
    ('python -m pytest tests/test_markdown_renderer.py -q', '验证 Markdown 修复工具的目标回归。'),
    ('python -m pytest tests/test_sample_structure.py -q', '确认公开样例结构和 README 约束没有回退。'),
    ('make public-preflight', '发布前跑公开门禁。'),
]

# 补丁计划用来展示 Coding Agent 的可交付边界。
PATCH_PLAN = [
    '在 renderer 中只提供可选 repair_markdown 开关，默认关闭。',
    '补表格、列表、代码块混合输出的回归测试。',
    'README 写清启用方式、适用范围和业务侧兜底责任。',
]
