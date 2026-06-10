from agent import ksadk_prepare_state, root_agent


def main() -> int:
    """最小烟测：验证恢复字段和去重字段都能出现在最终输出里。"""

    payload = {
        "input": "恢复昨天中断的报表生成任务。",
        "run_id": "demo-run-smoke",
        "checkpoint_id": "demo-run-smoke-cp-2",
        "resume_attempt_id": "demo-run-smoke-resume-2",
    }
    state = ksadk_prepare_state(payload, {})
    result = root_agent.invoke(state)
    answer = result["answer"]
    cancel_status = result.get("cancel_status")
    duplicate_tool_count = answer.count("skipped_duplicate")

    required = ("run_id", "checkpoint_id", "resume_attempt_id", "cancel_status", "duplicate_tool_count")
    missing = [field for field in required if field not in answer]
    if missing:
        raise SystemExit(f"missing fields: {', '.join(missing)}")
    if cancel_status != "not_requested":
        raise SystemExit(f"unexpected cancel_status: {cancel_status}")
    if duplicate_tool_count < 1:
        raise SystemExit("expected duplicate tool receipt")

    print(answer)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
