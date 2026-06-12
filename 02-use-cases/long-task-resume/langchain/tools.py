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
    status: str
    summary: str
    progress: str


TASK_STEPS = (
    TaskStep(
        step_id="plan_research",
        title="规划研究问题",
        tool_name="llm.plan",
        receipt_key="deepresearch:plan:v1",
        status="completed",
        summary="把用户问题拆成研究目标、关键子问题、检索关键词和输出结构。",
        progress="研究计划已经固化，恢复后不需要重新澄清需求。",
    ),
    TaskStep(
        step_id="search_web",
        title="检索公开网页",
        tool_name="web.search",
        receipt_key="deepresearch:web_search:v1",
        status="completed",
        summary="用通用 web_search 检索公开互联网，得到候选来源和摘要。",
        progress="候选来源已经记录，恢复后不会重复发起同一批搜索请求。",
    ),
    TaskStep(
        step_id="fetch_sources",
        title="抓取来源正文",
        tool_name="web.fetch",
        receipt_key="deepresearch:web_fetch:v1",
        status="completed",
        summary="抓取候选来源正文，清洗标题、链接、正文片段和发布时间。",
        progress="来源正文已经落入工作集，恢复后从证据筛选继续。",
    ),
    TaskStep(
        step_id="screen_evidence",
        title="筛选证据并去重",
        tool_name="evidence.screen",
        receipt_key="deepresearch:evidence_screen:v1",
        status="ready_to_resume",
        summary="按相关性、可信度和重复度筛选证据，保留可引用材料。",
        progress="可引用证据清单已经确定，恢复后直接进入交叉分析。",
    ),
    TaskStep(
        step_id="analyze_findings",
        title="交叉分析发现",
        tool_name="llm.analyze",
        receipt_key="deepresearch:analysis:v1",
        status="pending",
        summary="调用 LLM 对证据做主题归纳、冲突识别、趋势判断和缺口分析。",
        progress="首次执行默认在这里模拟一次外部工具失败，恢复后从 checkpoint 继续。",
    ),
    TaskStep(
        step_id="critic_review",
        title="批判性质检",
        tool_name="llm.critic",
        receipt_key="deepresearch:critic:v1",
        status="pending",
        summary="独立 reviewer 检查引用覆盖、推理跳跃、反例和置信度。",
        progress="质检通过后进入最终报告写入。",
    ),
    TaskStep(
        step_id="write_report",
        title="生成研究报告",
        tool_name="workspace.write",
        receipt_key="deepresearch:report:v1",
        status="pending",
        summary="写入摘要、证据表、主要发现、风险提示、参考链接和可复用模板。",
        progress="最终报告 deepresearch-report.md 写入工作区。",
    ),
)


def make_run_id(query: str) -> str:
    """生成可公开展示的短 run_id，避免 README 或日志里出现真实平台 ID。"""

    digest = sha1(query.encode("utf-8")).hexdigest()[:10]
    return f"demo-run-{digest}"


def build_checkpoints(run_id: str) -> list[dict[str, Any]]:
    """构造 checkpoint 索引列表。

    真实接入时 checkpoint 本体由 LangGraph checkpointer 保存；这里的列表只模拟
    session event 中的 run_checkpoint 索引和业务摘要。
    """

    checkpoints: list[dict[str, Any]] = []
    for index, step in enumerate(TASK_STEPS, start=1):
        checkpoints.append(
            {
                "checkpoint_id": f"{run_id}-cp-{index}",
                "step_id": step.step_id,
                "title": step.title,
                "status": step.status,
                "summary": step.summary,
                "progress": step.progress,
            }
        )
    return checkpoints


def simulate_tool_receipts(run_id: str, resume_attempt_id: str) -> list[dict[str, Any]]:
    """模拟 tool receipt 去重。

    长任务恢复时最容易出现的问题是重复执行外部搜索、网页抓取、LLM 分析或写报告。
    receipt_key 应该在业务侧稳定生成，恢复后先查 receipt，再决定是否跳过已经成功的工具调用。
    """

    receipts: list[dict[str, Any]] = []
    for step in TASK_STEPS[:4]:
        receipts.append(
            {
                "receipt_key": step.receipt_key,
                "tool_name": step.tool_name,
                "run_id": run_id,
                "resume_attempt_id": resume_attempt_id,
                "status": "skipped_duplicate",
                "summary": f"恢复时发现「{step.title}」已经完成，本次跳过，避免重复执行。",
            }
        )

    for step in TASK_STEPS[4:]:
        receipts.append(
            {
                "receipt_key": step.receipt_key,
                "tool_name": step.tool_name,
                "run_id": run_id,
                "resume_attempt_id": resume_attempt_id,
                "status": "recorded",
                "summary": step.progress,
            }
        )
    return receipts


def duplicate_tool_count(receipts: list[dict[str, Any]]) -> int:
    """统计恢复过程中被跳过的重复工具调用。"""

    return sum(1 for receipt in receipts if receipt.get("status") == "skipped_duplicate")


def simulate_cancel_status(query: str) -> str:
    """模拟 CancelRun 状态。"""

    lowered = query.lower()
    if "cancel" in lowered or "取消" in query or "停止" in query:
        return "cancelled"
    return "not_requested"


def build_resume_payload(query: str) -> dict[str, Any]:
    """构造一次本地恢复演示所需的全部状态。"""

    normalized_query = query.strip() or "调研一个技术产品的市场格局、竞品和落地风险。"
    run_id = make_run_id(normalized_query)
    checkpoints = build_checkpoints(run_id)
    checkpoint_id = checkpoints[3]["checkpoint_id"]
    resume_attempt_id = f"{run_id}-resume-1"
    receipts = simulate_tool_receipts(run_id, resume_attempt_id)
    cancel_status = simulate_cancel_status(normalized_query)
    return {
        "query": normalized_query,
        "run_id": run_id,
        "checkpoint_id": checkpoint_id,
        "resume_attempt_id": resume_attempt_id,
        "checkpoints": checkpoints,
        "receipts": receipts,
        "cancel_status": cancel_status,
    }


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
    skipped_steps = "、".join(item["title"] for item in checkpoints[:4])
    continued_steps = "、".join(item["title"] for item in checkpoints[4:])

    return f"""# 通用 DeepResearch 长任务恢复演示

**用户问题**：{query}

## 任务概览

- `run_id`：`{run_id}`
- 当前恢复点：`{checkpoint_id}`
- `resume_attempt_id`：`{resume_attempt_id}`
- `cancel_status`：`{cancel_status}`
- `duplicate_tool_count`：{duplicate_count}
- 交付物：`deepresearch-report.md`

## checkpoint 列表

| checkpoint_id | 阶段 | 状态 | 摘要 |
| --- | --- | --- | --- |
{checkpoint_lines}

## ResumeRun

本次从 `{checkpoint_id}` 恢复。恢复逻辑先读取 LangGraph checkpoint，再检查 tool receipt：

- 跳过已完成阶段：{skipped_steps}。
- 继续执行阶段：{continued_steps}。
- 恢复后不会重复 web_search / web_fetch，也不会重复 LLM 分析或覆盖已生成证据表。

## tool receipt

| receipt_key | 工具 | 状态 | 说明 |
| --- | --- | --- | --- |
{receipt_lines}

## CancelRun

当前取消状态为 `{cancel_status}`。如果用户在 Web UI 或 API 中触发取消，业务侧只记录取消意图；长任务在工具边界退出，并保留最近 checkpoint，下一次 ResumeRun 从交叉分析或后续阶段继续。

## 降级说明

- 未配置 `KSADK_SESSION_BACKEND` 或数据库时，本 demo 使用本地 fixture 模拟 checkpoint 索引。
- 未配置真实 web_search / web_fetch / LLM 时，工具会降级为可运行的示例输出。
- 生产环境建议把 checkpoint、receipt 和 cancel 状态写入同一个 session namespace，避免恢复时跨租户串读。
- 这个样例是通用 DeepResearch 模板；替换研究计划、工具实现和报告模板即可改成自己的业务 Agent。
""".strip()


def render_demo_answer(query: str) -> str:
    """生成离线长任务恢复报告。"""

    payload = build_resume_payload(query)
    return render_answer(
        query=payload["query"],
        run_id=payload["run_id"],
        checkpoint_id=payload["checkpoint_id"],
        resume_attempt_id=payload["resume_attempt_id"],
        checkpoints=payload["checkpoints"],
        receipts=payload["receipts"],
        cancel_status=payload["cancel_status"],
    )
