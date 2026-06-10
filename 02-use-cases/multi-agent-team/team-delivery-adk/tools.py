from __future__ import annotations

from data import ACCEPTANCE_CHECKS, MERGE_RULES, PARALLEL_TASKS, TEAM_ROLES
from prompts import SYSTEM_PROMPT, TITLE


def assign_team_roles(query: str) -> list[dict]:
    """分配团队角色。

    默认返回本地角色 fixture；真实项目可以替换为子 Agent 注册表或任务编排服务。
    """

    return TEAM_ROLES


def collect_parallel_progress(query: str) -> list[dict]:
    """收集并行执行轨迹。"""

    return PARALLEL_TASKS


def _render_roles(roles: list[dict]) -> str:
    return "\n".join(
        f"- **{item['name']}**：{item['responsibility']} 产物：{item['artifact']}。" for item in roles
    )


def _render_progress(tasks: list[dict]) -> str:
    lines = ["| 角色 | 任务 | 状态 |", "| --- | --- | --- |"]
    for item in tasks:
        lines.append(f"| {item['role']} | {item['task']} | {item['status']} |")
    return "\n".join(lines)


def render_demo_answer(query: str) -> str:
    """生成离线多 Agent 协作报告。"""

    roles = assign_team_roles(query)
    tasks = collect_parallel_progress(query)
    merge_lines = "\n".join(f"{index}. {rule}" for index, rule in enumerate(MERGE_RULES, 1))
    checks = "\n".join(f"- [ ] {item}" for item in ACCEPTANCE_CHECKS)
    goal_line = next((line.strip() for line in SYSTEM_PROMPT.splitlines() if line.strip().startswith("这个场景")), "")
    return f"""# {TITLE}

**用户问题**：{query}

## 结论

{goal_line} 当前 demo 使用本地团队轨迹 fixture，不伪造真实子 Agent 执行结果；接入任务队列或子 Agent 服务后可复用同一套收口结构。

## 角色分工

{_render_roles(roles)}

## 并行轨迹

{_render_progress(tasks)}

## 冲突合并

{merge_lines}

## 验收清单

{checks}

## 工程说明

- `agent.py` 暴露框架入口。
- `tools.py` 负责角色分工、进度汇总和验收清单。
- `data.py` 可替换为真实子 Agent 注册表、任务队列或协作日志。
""".strip()


def collect_evidence(query: str) -> list[dict]:
    """LangGraph 节点使用的证据收集函数。"""

    return collect_parallel_progress(query)


def plan_actions(query: str, evidence: list[dict]) -> list[dict]:
    """LangGraph 节点使用的行动规划函数。"""

    return [
        {"step": index, "owner": item["name"], "action": item["responsibility"], "why": f"产出 {item['artifact']}。"}
        for index, item in enumerate(TEAM_ROLES, 1)
    ]


def render_answer(query: str, evidence: list[dict], actions: list[dict]) -> str:
    """LangGraph 输出节点复用离线渲染。"""

    return render_demo_answer(query)
