from __future__ import annotations

from collections import defaultdict


_MEMORIES: dict[str, list[str]] = defaultdict(list)


def save_user_memory(user_id: str, content: str) -> dict[str, str]:
    normalized_user = str(user_id or "local-user")
    normalized_content = str(content or "").strip()
    if not normalized_content:
        return {"status": "ignored", "message": "空内容不会保存。"}
    _MEMORIES[normalized_user].append(normalized_content)
    return {"status": "success", "message": "记忆已保存。"}


def load_user_memory(user_id: str, query: str = "") -> dict[str, object]:
    normalized_user = str(user_id or "local-user")
    memories = list(_MEMORIES.get(normalized_user, []))
    normalized_query = str(query or "").lower().strip()
    if normalized_query:
        filtered = [item for item in memories if normalized_query in item.lower()]
        if filtered:
            memories = filtered
    return {
        "status": "success",
        "user_id": normalized_user,
        "memories": memories,
        "formatted_text": "\n".join(f"- {item}" for item in memories) or "暂无本地记忆。",
    }

