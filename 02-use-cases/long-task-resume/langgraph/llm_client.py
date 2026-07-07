"""LLM 调用层：模型配置检查 + 同步/流式调用。

从 agent.py 抽取的 LLM 调用层，依赖仅 os.environ/httpx/json。
"""

from __future__ import annotations

import json
import os
from typing import AsyncIterator

import httpx


def _model_configured() -> bool:
    return bool(
        os.environ.get("OPENAI_API_KEY")
        and os.environ.get("OPENAI_BASE_URL")
        and os.environ.get("OPENAI_MODEL_NAME")
    )


async def _call_chat_model(messages: list[dict[str, str]], *, temperature: float = 0.2) -> str:
    if not _model_configured():
        return ""
    base_url = os.environ["OPENAI_BASE_URL"].rstrip("/")
    api_key = os.environ["OPENAI_API_KEY"]
    model = os.environ["OPENAI_MODEL_NAME"]
    async with httpx.AsyncClient(timeout=90) as client:
        response = await client.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": model, "messages": messages, "stream": False, "temperature": temperature},
        )
        response.raise_for_status()
        data = response.json()
    choices = data.get("choices") if isinstance(data, dict) else None
    if isinstance(choices, list) and choices:
        message = choices[0].get("message") if isinstance(choices[0], dict) else None
        content = message.get("content") if isinstance(message, dict) else None
        if content:
            return str(content)
    return ""


async def _stream_chat_model(
    messages: list[dict[str, str]],
    *,
    temperature: float = 0.2,
) -> AsyncIterator[str]:
    if not _model_configured():
        raise RuntimeError(
            "模型未配置：真实 Deep Research demo 需要 OPENAI_API_KEY、OPENAI_BASE_URL、OPENAI_MODEL_NAME。"
        )
    base_url = os.environ["OPENAI_BASE_URL"].rstrip("/")
    api_key = os.environ["OPENAI_API_KEY"]
    model = os.environ["OPENAI_MODEL_NAME"]
    async with httpx.AsyncClient(timeout=90) as client:
        async with client.stream(
            "POST",
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": model, "messages": messages, "stream": True, "temperature": temperature},
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line.startswith("data:"):
                    continue
                payload = line.removeprefix("data:").strip()
                if not payload or payload == "[DONE]":
                    continue
                try:
                    data = json.loads(payload)
                except json.JSONDecodeError:
                    continue
                choices = data.get("choices") if isinstance(data, dict) else None
                if not isinstance(choices, list) or not choices:
                    continue
                choice = choices[0] if isinstance(choices[0], dict) else {}
                delta = choice.get("delta") if isinstance(choice, dict) else {}
                content = delta.get("content") if isinstance(delta, dict) else None
                if content:
                    yield str(content)


async def _call_required_llm(
    prompt: str,
    *,
    system: str = "你是严谨的 Deep Research 研究员。必须基于输入资料生成内容，不要编造来源。",
    temperature: float = 0.2,
) -> str:
    content = await _call_chat_model(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
    )
    if not content.strip():
        raise RuntimeError("LLM 没有返回可用内容")
    return content.strip()
