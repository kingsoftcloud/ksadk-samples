from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha1
from typing import Any


@dataclass(frozen=True)
class TaskStep:
    """长任务中的一个可恢复阶段。"""

    step_id: str
    title: str
    tool_name: str
    receipt_key: str
    summary: str


TASK_STEPS = (
    TaskStep(
        step_id="collect_requirements",
        title="收集需求",
        tool_name="workspace.search",
        receipt_key="workspace:requirements:v1",
        summary="读取任务说明、历史反馈和验收口径，形成执行边界。",
    ),
    TaskStep(
        step_id="run_analysis",
        title="运行分析",
        tool_name="sandbox.run",
        receipt_key="sandbox:analysis:v1",
        summary="在隔离环境执行耗时分析，记录命令、输出摘要和 exit code。",
    ),
    TaskStep(
        step_id="write_report",
        title="生成交付物",
        tool_name="workspace.write",
        receipt_key="workspace:report:v1",
        summary="把分析结论写回 Workspace，并附带可复核的证据列表。",
    ),
)


def make_run_id(query: str) -> str:
    """生成可公开展示的短 run_id，避免 README 或日志里出现真实平台 ID。"""

    digest = sha1(query.encode("utf-8")).hexdigest()[:10]
    return f"demo-run-{digest}"


def build_checkpoints(run_id: str) -> list[dict[str, Any]]:
    """构造 checkpoint 列表。

    真实接入时这里应该读取 KSADK session store 或 AgentEngine 的 run state。
    """

    checkpoints: list[dict[str, Any]] = []
    for index, step in enumerate(TASK_STEPS, start=1):
        checkpoints.append(
            {
                "checkpoint_id": f"{run_id}-cp-{index}",
                "step_id": step.step_id,
                "title": step.title,
                "status": "completed" if index < len(TASK_STEPS) else "ready_to_resume",
                "summary": step.summary,
            }
        )
    return checkpoints


def simulate_tool_receipts(run_id: str, resume_attempt_id: str) -> list[dict[str, Any]]:
    """模拟 tool receipt 去重。

    长任务恢复时最容易出现的问题是重复执行外部工具。receipt_key 应该在业务侧稳定生成，
    恢复后先查 receipt，再决定是否跳过已经成功的工具调用。
    """

    receipts: list[dict[str, Any]] = []
    seen: set[str] = set()
    for step in TASK_STEPS:
        duplicate = step.receipt_key in seen
        receipts.append(
            {
                "receipt_key": step.receipt_key,
                "tool_name": step.tool_name,
                "run_id": run_id,
                "resume_attempt_id": resume_attempt_id,
                "status": "skipped_duplicate" if duplicate else "recorded",
                "summary": step.summary,
            }
        )
        seen.add(step.receipt_key)

    # 故意再放一次分析工具的 receipt，展示恢复后如何发现重复调用。
    repeated = TASK_STEPS[1]
    receipts.append(
        {
            "receipt_key": repeated.receipt_key,
            "tool_name": repeated.tool_name,
            "run_id": run_id,
            "resume_attempt_id": resume_attempt_id,
            "status": "skipped_duplicate",
            "summary": "恢复时发现分析命令已成功执行，本次跳过，避免重复扣费或重复写入。",
        }
    )
    return receipts


def duplicate_tool_count(receipts: list[dict[str, Any]]) -> int:
    """统计恢复过程中被跳过的重复工具调用。"""

    return sum(1 for receipt in receipts if receipt.get("status") == "skipped_duplicate")


def simulate_cancel_status(query: str) -> str:
    """模拟 CancelRun 状态。

    用户问题里出现取消意图时返回 cancelled，否则返回 not_requested。
    """

    lowered = query.lower()
    if "cancel" in lowered or "取消" in query or "停止" in query:
        return "cancelled"
    return "not_requested"


def render_answer(
    query: str,
    run_id: str,
    checkpoint_id: str,
    resume_attempt_id: str,
    checkpoints: list[dict[str, Any]],
    receipts: list[dict[str, Any]],
    cancel_status: str,
) -> str:
    """把长任务状态渲染为 Web UI 友好的 Markdown。"""

    checkpoint_lines = "\n".join(
        f"| `{item['checkpoint_id']}` | {item['title']} | {item['status']} | {item['summary']} |"
        for item in checkpoints
    )
    receipt_lines = "\n".join(
        f"| `{item['receipt_key']}` | `{item['tool_name']}` | {item['status']} | {item['summary']} |"
        for item in receipts
    )
    duplicate_count = duplicate_tool_count(receipts)

    return f"""# 长任务恢复演示

**用户问题**：{query}

## 任务概览

- `run_id`：`{run_id}`
- 当前恢复点：`{checkpoint_id}`
- `resume_attempt_id`：`{resume_attempt_id}`
- `cancel_status`：`{cancel_status}`
- `duplicate_tool_count`：{duplicate_count}

## checkpoint 列表

| checkpoint_id | 阶段 | 状态 | 摘要 |
| --- | --- | --- | --- |
{checkpoint_lines}

## ResumeRun

本次从 `{checkpoint_id}` 恢复。恢复逻辑先读取 checkpoint，再检查 tool receipt，最后只执行缺失阶段。真实平台接入时，`run_id`、`checkpoint_id` 和 `resume_attempt_id` 应来自 AgentEngine run/session 事件，而不是本地生成。

## tool receipt

| receipt_key | 工具 | 状态 | 说明 |
| --- | --- | --- | --- |
{receipt_lines}

## CancelRun

当前取消状态为 `{cancel_status}`。如果用户在 Web UI 或 API 中触发取消，业务侧应把长任务标记为可停止状态，并在下一次工具边界检查时退出。

## 降级说明

- 未配置 `KSADK_SESSION_BACKEND` 或数据库时，本 demo 使用本地 fixture 模拟 checkpoint。
- 未接入真实 Workspace / Sandbox 时，tool receipt 只展示去重思路，不执行外部命令。
- 生产环境建议把 checkpoint、receipt 和 cancel 状态写入同一个 session namespace，避免恢复时跨租户串读。
""".strip()
