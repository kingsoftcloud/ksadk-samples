from tools import build_resume_payload, render_demo_answer


def main() -> int:
    """最小烟测：验证恢复字段和去重字段都能出现在最终输出里。"""

    query = "恢复昨天中断的报表生成任务。"
    payload = build_resume_payload(query)
    answer = render_demo_answer(query)

    required = ("run_id", "checkpoint_id", "resume_attempt_id", "cancel_status", "duplicate_tool_count")
    missing = [field for field in required if field not in answer]
    if missing:
        raise SystemExit(f"missing fields: {', '.join(missing)}")
    if payload["cancel_status"] != "not_requested":
        raise SystemExit(f"unexpected cancel_status: {payload['cancel_status']}")
    if answer.count("skipped_duplicate") < 1:
        raise SystemExit("expected duplicate tool receipt")

    print(answer)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
