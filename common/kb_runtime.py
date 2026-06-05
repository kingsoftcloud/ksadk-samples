from __future__ import annotations

import os
from typing import Any, Mapping

from common.local_kb import search_local_knowledge_text


DEFAULT_KB_ENDPOINT = "aicp.api.ksyun.com"
DEFAULT_KB_REGION = "cn-beijing-6"


def _env_get(environ: Mapping[str, str], key: str, default: str = "") -> str:
    return str(environ.get(key, default) or "").strip()


def resolve_kb_connection(environ: Mapping[str, str] | None = None) -> dict[str, str]:
    env = environ or os.environ
    endpoint = _env_get(env, "KSADK_KB_ENDPOINT", DEFAULT_KB_ENDPOINT)
    scheme = _env_get(env, "KSADK_KB_SCHEME")
    if not scheme:
        scheme = "https"
    return {
        "endpoint": endpoint,
        "scheme": scheme,
        "region": _env_get(env, "KSADK_KB_REGION") or _env_get(env, "KSYUN_REGION", DEFAULT_KB_REGION),
    }


def collect_kb_runtime_status(environ: Mapping[str, str] | None = None) -> dict[str, Any]:
    env = environ or os.environ
    connection = resolve_kb_connection(env)
    dataset_id = _env_get(env, "KSADK_KB_DATASET_ID")
    access_key = _env_get(env, "KSADK_KB_ACCESS_KEY") or _env_get(env, "KSYUN_ACCESS_KEY")
    secret_key = _env_get(env, "KSADK_KB_SECRET_KEY") or _env_get(env, "KSYUN_SECRET_KEY")
    local_mode = not bool(dataset_id)

    status = "LOCAL_MODE" if local_mode else "READY"
    issues: list[str] = []
    next_step = "当前未配置 KSADK_KB_DATASET_ID，示例会使用仓库内置本地知识库。"

    if dataset_id and (not access_key or not secret_key):
        status = "AUTH_MISSING"
        if not access_key:
            issues.append("missing_access_key")
        if not secret_key:
            issues.append("missing_secret_key")
        next_step = "请配置 KSYUN_ACCESS_KEY/KSYUN_SECRET_KEY，或配置 KSADK_KB_ACCESS_KEY/KSADK_KB_SECRET_KEY。"
    elif dataset_id:
        next_step = "云知识库配置已就绪，示例会优先调用 KSADK 知识库工具。"

    return {
        "status": status,
        "issues": issues,
        "effective_config": {
            "mode": "local" if local_mode else "cloud",
            "dataset_id": dataset_id,
            "endpoint": connection["endpoint"],
            "scheme": connection["scheme"],
            "region": connection["region"],
            "has_access_key": bool(access_key),
            "has_secret_key": bool(secret_key),
        },
        "next_step": next_step,
    }


def search_knowledge(query: str, top_k: int = 3) -> dict[str, str]:
    if _env_get(os.environ, "KSADK_KB_DATASET_ID"):
        try:
            from ksadk.knowledge_base.tool import search_knowledge as search_cloud_knowledge

            return {"mode": "cloud", "result": search_cloud_knowledge(query, top_k=top_k)}
        except Exception as exc:
            return {"mode": "cloud", "result": f"云知识库检索失败: {exc}"}
    return {"mode": "local", "result": search_local_knowledge_text(query, top_k=top_k)}
