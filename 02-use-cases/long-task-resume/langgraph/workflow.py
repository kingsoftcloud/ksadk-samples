from __future__ import annotations

from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from tools import (
    build_checkpoints,
    make_run_id,
    render_answer,
    simulate_cancel_status,
    simulate_tool_receipts,
)


class ResumeState(TypedDict, total=False):
    """长任务恢复状态，字段名尽量贴近用户在 Web UI 里看到的运行信息。"""

    query: str
    run_id: str
    active_checkpoint_ref: str
    resume_attempt_id: str
    checkpoints: list[dict[str, Any]]
    tool_receipts: list[dict[str, Any]]
    cancel_status: str
    answer: str
    session_context: dict[str, Any]


def prepare_state(payload: dict, session_context: dict) -> ResumeState:
    """把 AgentEngine payload 转成 LangGraph 初始状态。"""

    query = str(payload.get("input") or "").strip() or "演示一个可恢复的长任务。"
    run_id = str(payload.get("run_id") or make_run_id(query))
    return {
        "query": query,
        "run_id": run_id,
        "active_checkpoint_ref": str(payload.get("checkpoint_id") or ""),
        "resume_attempt_id": str(payload.get("resume_attempt_id") or f"{run_id}-resume-1"),
        "checkpoints": [],
        "tool_receipts": [],
        "cancel_status": "not_requested",
        "answer": "",
        "session_context": dict(session_context or {}),
    }


def build_agent_graph():
    """构建长任务恢复 LangGraph。

    节点刻意拆成 checkpoint、resume、cancel、finalize 四段，方便用户照着替换为真实存储。
    """

    def load_checkpoints(state: ResumeState) -> dict[str, Any]:
        checkpoints = build_checkpoints(state["run_id"])
        active_checkpoint_ref = state.get("active_checkpoint_ref") or checkpoints[-1]["checkpoint_id"]
        return {"checkpoints": checkpoints, "active_checkpoint_ref": active_checkpoint_ref}

    def resume_from_checkpoint(state: ResumeState) -> dict[str, Any]:
        receipts = simulate_tool_receipts(state["run_id"], state["resume_attempt_id"])
        return {"tool_receipts": receipts}

    def check_cancel_status(state: ResumeState) -> dict[str, str]:
        return {"cancel_status": simulate_cancel_status(state.get("query", ""))}

    def finalize_answer(state: ResumeState) -> dict[str, str]:
        return {
            "answer": render_answer(
                query=state.get("query", ""),
                run_id=state.get("run_id", ""),
                checkpoint_id=state.get("active_checkpoint_ref", ""),
                resume_attempt_id=state.get("resume_attempt_id", ""),
                checkpoints=state.get("checkpoints", []),
                receipts=state.get("tool_receipts", []),
                cancel_status=state.get("cancel_status", "not_requested"),
            )
        }

    graph = StateGraph(ResumeState)
    graph.add_node("load_checkpoints", load_checkpoints)
    graph.add_node("resume_from_checkpoint", resume_from_checkpoint)
    graph.add_node("check_cancel_status", check_cancel_status)
    graph.add_node("finalize_answer", finalize_answer)
    graph.set_entry_point("load_checkpoints")
    graph.add_edge("load_checkpoints", "resume_from_checkpoint")
    graph.add_edge("resume_from_checkpoint", "check_cancel_status")
    graph.add_edge("check_cancel_status", "finalize_answer")
    graph.add_edge("finalize_answer", END)
    return graph.compile(name="long-task-resume")
