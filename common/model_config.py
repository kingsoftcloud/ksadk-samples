from __future__ import annotations

import os


DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_API_BASE = "https://api.openai.com/v1"


def get_model_name() -> str:
    return os.getenv("OPENAI_MODEL_NAME") or os.getenv("MODEL_NAME") or DEFAULT_MODEL


def get_openai_api_base() -> str:
    return os.getenv("OPENAI_BASE_URL") or os.getenv("OPENAI_API_BASE") or DEFAULT_API_BASE


def get_openai_api_key() -> str:
    return os.getenv("OPENAI_API_KEY", "")


def make_adk_litellm_model():
    from google.adk.models.lite_llm import LiteLlm

    return LiteLlm(
        model=f"openai/{get_model_name()}",
        api_base=get_openai_api_base(),
        api_key=get_openai_api_key(),
    )


def make_langchain_chat_model():
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=get_model_name(),
        base_url=get_openai_api_base(),
        api_key=get_openai_api_key(),
        temperature=0,
    )
