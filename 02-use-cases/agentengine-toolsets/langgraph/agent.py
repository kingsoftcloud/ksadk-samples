from pathlib import Path
import os
import re
import sys
from typing import Annotated, Any, TypedDict

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent

from common.model_config import make_langchain_chat_model
from ksadk.skills.service_env import resolve_skill_service_url
from ksadk.toolsets import describe_agentengine_tools, get_agentengine_tools


SYSTEM_PROMPT = """你是 AgentEngine Toolsets 示例助手，用中文回答。

目标：
- 演示 LangGraph 如何绑定 KSADK 0.6.2+ 内置 toolsets。
- 演示如何发现、搜索、加载 Skill Space 下的 Skill。
- 演示业务项目如何追加自己的 tool 和 graph node。
- 在工具不可用或未配置时，返回真实错误和缺少的环境变量，不要伪造 Skill 列表或工具执行结果。

工具使用策略：
- 用户问 Space 下有哪些 skill、技能列表、Skill Space、可用工具时，必须优先使用 list_skills。
- 用户带有搜索意图时，优先使用 search_skills。
- 用户指定加载某个 Skill 时，使用 load_skill。
- 用户问当前绑定了哪些能力、运行环境或配置边界时，调用 component_status。
- 用户问 LangGraph 图结构、节点、边或自定义扩展方式时，调用 graph_status。
- 用户要生成发布风险清单或评审发布改动时，调用 release_risk_matrix。
- 用户问 Skill、Workspace、Sandbox 等低频能力时，先用 agentengine_tool_dispatcher list 或 describe 查看，再按需 call。
- 使用 agentengine_tool_dispatcher 时，include 只能填合法工具组或工具名，例如 skill、workspace、platform、sandbox、focused，不能填 file；读取或写入文件请使用 workspace 组里的工具。
- 用户只做普通咨询时可以直接回答。
"""

FOCUSED_TOOLSETS = ["focused", "agentengine_tool_dispatcher"]
AGENTENGINE_TOOL_DESCRIPTIONS = describe_agentengine_tools(include=FOCUSED_TOOLSETS)


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    route: dict[str, Any]
    custom_context: dict[str, Any]
    specialist_messages: list[BaseMessage]
    answer: str


def _tool_name(candidate: Any) -> str:
    return str(getattr(candidate, "name", None) or getattr(candidate, "__name__", "") or "")


def _group_tool_names(descriptions: list[dict[str, Any]]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {}
    for item in descriptions:
        group = str(item.get("group") or "unknown")
        grouped.setdefault(group, []).append(str(item.get("name") or ""))
    return grouped


def _env(key: str, default: str = "") -> str:
    return str(os.getenv(key) or default).strip()


def _env_enabled(key: str) -> bool:
    return bool(_env(key))


def _skill_space_ids() -> list[str]:
    raw = _env("KSADK_SKILL_SPACE_IDS") or _env("SKILL_SPACE_ID")
    return [item.strip() for item in raw.split(",") if item.strip()]


def _public_skill_space_ids() -> list[str]:
    return [item.strip() for item in _env("KSADK_PUBLIC_SKILL_SPACE_IDS").split(",") if item.strip()]


@tool
def graph_status() -> dict[str, Any]:
    """说明本示例的 LangGraph 节点、边、工具绑定和扩展点。"""

    return {
        "ok": True,
        "graph_name": "agentengine_toolsets_langgraph",
        "pattern": "route_turn -> prepare_custom_context -> run_specialist -> finalize_answer",
        "nodes": [
            {
                "name": "route_turn",
                "purpose": "根据用户输入选择 component_status、graph_status、release_risk_matrix 或通用问答路径。",
            },
            {
                "name": "prepare_custom_context",
                "purpose": "演示业务项目可以在外层 StateGraph 中注入自己的上下文。",
            },
            {
                "name": "run_specialist",
                "purpose": "运行 create_react_agent，并绑定 KSADK built-in tools 与业务自定义 tools。",
            },
            {
                "name": "finalize_answer",
                "purpose": "整理 ReAct 子图输出，返回给 AgentEngine。",
            },
        ],
        "edges": [
            "START -> route_turn",
            "route_turn -> prepare_custom_context",
            "prepare_custom_context -> run_specialist",
            "run_specialist -> finalize_answer",
            "finalize_answer -> END",
        ],
        "ksadk_toolsets": {
            "include": FOCUSED_TOOLSETS,
            "bound_tools": _group_tool_names(AGENTENGINE_TOOL_DESCRIPTIONS),
            "dispatcher": "agentengine_tool_dispatcher 可按需 list/describe/call 低频或高风险工具。",
        },
        "custom_extensions": {
            "tools": ["graph_status", "component_status", "release_risk_matrix"],
            "graph_nodes": ["route_turn", "prepare_custom_context"],
            "tool_calling": "Skill Space 查询由 ReAct 子图中的大模型根据 suggested_tools 自主调用 list_skills/search_skills/load_skill。",
        },
    }


@tool
def release_risk_matrix(release_name: str, changed_areas: list[str] | str) -> dict[str, Any]:
    """根据发布改动范围生成一个轻量风险矩阵。"""

    if isinstance(changed_areas, str):
        areas = [item.strip() for item in changed_areas.split(",") if item.strip()]
    else:
        areas = [str(item).strip() for item in changed_areas if str(item).strip()]

    risk_rules = {
        "tool": "工具 schema、权限策略和 UI 工具事件需要回归。",
        "workspace": "Workspace 文件边界、预览和写入审批需要回归。",
        "skill": "Skill 发现、加载和可选隔离执行链路需要回归。",
        "sandbox": "Sandbox 后端、超时、清理和错误回传需要回归。",
        "memory": "长期记忆的命名空间、读写权限和隐私边界需要回归。",
        "kb": "知识库 dataset、检索质量和无配置降级路径需要回归。",
    }

    risks = []
    for area in areas:
        lower = area.lower()
        matched = next((message for key, message in risk_rules.items() if key in lower), None)
        risks.append(
            {
                "area": area,
                "risk": matched or "普通业务改动，重点验证主路径、错误提示和部署配置。",
                "verification": "准备一个可复现 prompt，在本地 Web UI 和部署环境各跑一次。",
            }
        )

    high_signal = sum(
        1
        for area in areas
        if any(key in area.lower() for key in ("tool", "workspace", "skill", "sandbox", "memory", "kb"))
    )
    return {
        "ok": True,
        "release_name": release_name,
        "risk_level": "high" if high_signal >= 3 else "medium" if high_signal else "low",
        "risks": risks,
        "next_step": "把风险矩阵转成发布检查清单，并用 component_status 确认运行时绑定状态。",
    }


@tool
def component_status() -> dict[str, Any]:
    """汇总本示例绑定的 KSADK toolsets、业务自定义工具和运行边界。"""

    grouped = _group_tool_names(AGENTENGINE_TOOL_DESCRIPTIONS)
    skill_spaces = _skill_space_ids()
    public_spaces = _public_skill_space_ids()
    try:
        skill_service_url = resolve_skill_service_url(require_spaces=True)
    except Exception as exc:
        skill_service_url = ""
        skill_service_error = f"{type(exc).__name__}: {exc}"
    else:
        skill_service_error = ""

    missing_for_skill_space = []
    if not skill_spaces and not public_spaces:
        missing_for_skill_space.append("KSADK_SKILL_SPACE_IDS 或 SKILL_SPACE_ID")
    if (skill_spaces or public_spaces) and not skill_service_url:
        missing_for_skill_space.append("KSADK_SKILL_SERVICE_URL 或 KSADK_SKILL_SERVICE_ENDPOINT")
    if not (_env_enabled("KSADK_SKILL_SERVICE_ACCESS_KEY") or _env_enabled("KSYUN_ACCESS_KEY")):
        missing_for_skill_space.append("KSADK_SKILL_SERVICE_ACCESS_KEY 或 KSYUN_ACCESS_KEY")
    if not (_env_enabled("KSADK_SKILL_SERVICE_SECRET_KEY") or _env_enabled("KSYUN_SECRET_KEY")):
        missing_for_skill_space.append("KSADK_SKILL_SERVICE_SECRET_KEY 或 KSYUN_SECRET_KEY")

    return {
        "ok": True,
        "sample": {
            "name": "agentengine-toolsets-langgraph",
            "framework": "langgraph",
            "ksadk_version_target": "0.6.2+ public API",
            "binding_pattern": "get_agentengine_tools(include=['focused', 'agentengine_tool_dispatcher'])",
        },
        "bound_ksadk_tools": grouped,
        "custom_tools": ["graph_status", "component_status", "release_risk_matrix"],
        "skill_space": {
            "configured": not missing_for_skill_space,
            "space_ids_configured": len(skill_spaces),
            "public_space_ids_configured": len(public_spaces),
            "service_url_configured": bool(skill_service_url),
            "service_error": skill_service_error,
            "missing_config": missing_for_skill_space,
            "tools": ["list_skills", "search_skills", "load_skill"],
            "note": "只发现和加载 Skill 不需要 Skill Runtime；执行 Skill workflow 才需要配置 Runtime。",
        },
        "skill_runtime": {
            "backend": _env("KSADK_SKILL_RUNTIME_BACKEND") or "disabled",
            "template_configured": bool(_env("KSADK_SKILL_RUNTIME_TEMPLATE_ID") or _env("KSADK_SANDBOX_TEMPLATE_ID")),
            "agent_path_configured": bool(_env("KSADK_SKILL_RUNTIME_AGENT_PATH")),
            "meaning": "execute_skills 使用的隔离执行后端；未配置时仍可 list/search/load Skill。",
        },
        "workspace": {
            "root_configured": bool(_env("AGENTENGINE_WORKSPACE_ROOT") or _env("WORKSPACE_ROOT")),
            "meaning": "Workspace 工具只操作 AgentEngine 会话 workspace，不等同于任意宿主机目录。",
            "tools": ["workspace_status", "list_workspace_files", "read_workspace_file", "search_workspace_files"],
        },
        "sandbox": {
            "backend": _env("KSADK_SANDBOX_BACKEND") or "disabled",
            "template_configured": bool(_env("KSADK_SANDBOX_TEMPLATE_ID")),
            "meaning": "run_command/run_code 等隔离执行能力需要单独配置 sandbox backend。",
        },
        "platform": {
            "knowledge_base_configured": bool(_env("KSADK_KB_DATASET_ID")),
            "long_term_memory_configured": bool(_env("KSADK_LTM_BACKEND") or _env("KSADK_LTM_NAMESPACE")),
        },
        "boundaries": {
            "skill": "list/search/load 可直接用于 Skill 指令发现；execute_skills 需要额外配置 Skill Runtime。",
            "workspace": "Workspace 工具只操作 AgentEngine UI workspace 目录。",
            "sandbox": "run_command/run_code 只通过已配置的隔离 sandbox backend 执行。",
            "platform": "知识库和长期记忆只有在安装并配置对应能力后才会出现在 platform toolset 中。",
            "approval": "高风险工具由 KSADK Tool Gateway 返回 approval_required，不应由示例代码伪造成功。",
        },
        "how_to_expand": [
            "追加业务 tool 到 DEMO_TOOLS。",
            "在 StateGraph 中增加新的业务节点。",
            "通过 dispatcher 渐进式暴露低频工具，减少默认上下文体积。",
        ],
    }


def _build_tools() -> list[Any]:
    agentengine_tools = [
        tool_item
        for tool_item in get_agentengine_tools(include=FOCUSED_TOOLSETS)
        if _tool_name(tool_item) != "component_status"
    ]
    return [*agentengine_tools, graph_status, component_status, release_risk_matrix]


TOOLS = _build_tools()


def _last_user_text(messages: list[BaseMessage]) -> str:
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            return str(message.content or "")
    return ""


def _route_for_text(user_text: str) -> dict[str, Any]:
    lowered = user_text.lower()
    if any(word in lowered for word in ("workspace", "sandbox", "tool")) or any(
        word in user_text for word in ("工具", "工作区", "沙箱")
    ):
        return {"scenario": "ksadk_toolsets", "suggested_tools": ["agentengine_tool_dispatcher"]}
    skill_space_intent = (
        bool(re.search(r"\bskill(?:\s+space)?\b", lowered))
        or bool(re.search(r"\bspace\b", lowered))
        or any(word in user_text for word in ("技能", "技能空间"))
    )
    if skill_space_intent:
        if any(word in user_text for word in ("搜索", "查找", "找一下")) or "search" in lowered:
            return {
                "scenario": "skill_space_search",
                "suggested_tools": ["search_skills", "list_skills", "load_skill", "agentengine_tool_dispatcher"],
                "response_guidance": "让 ReAct 子图优先调用 search_skills；不要由外层 LangGraph 代替工具调用。",
            }
        return {
            "scenario": "skill_space_list",
            "suggested_tools": ["list_skills", "search_skills", "load_skill", "agentengine_tool_dispatcher"],
            "response_guidance": "让 ReAct 子图优先调用 list_skills，并基于真实工具结果总结。",
        }
    if any(word in user_text for word in ("组件", "绑定", "配置", "状态", "能力", "边界")):
        return {"scenario": "runtime_status", "suggested_tools": ["component_status"]}
    if any(word in lowered for word in ("langgraph", "graph", "节点", "边", "子图")):
        return {"scenario": "graph_structure", "suggested_tools": ["graph_status"]}
    if any(word in user_text for word in ("发布", "风险", "检查清单", "评审")):
        return {"scenario": "release_review", "suggested_tools": ["release_risk_matrix"]}
    if any(word in lowered for word in ("skill", "workspace", "sandbox", "tool")):
        return {"scenario": "ksadk_toolsets", "suggested_tools": ["agentengine_tool_dispatcher"]}
    return {"scenario": "general", "suggested_tools": []}


def ksadk_prepare_state(payload: dict, session_context: dict) -> dict:
    user_text = str(payload.get("input") or "")
    return {
        "messages": [HumanMessage(content=user_text)],
        "route": _route_for_text(user_text),
        "custom_context": {"session_context_keys": sorted(session_context.keys())},
        "specialist_messages": [],
        "answer": "",
    }


def route_turn(state: AgentState) -> dict[str, Any]:
    return {"route": _route_for_text(_last_user_text(state["messages"]))}


def prepare_custom_context(state: AgentState) -> dict[str, Any]:
    route = state.get("route") or {}
    return {
        "custom_context": {
            "sample": "agentengine-toolsets-langgraph",
            "route": route.get("scenario", "general"),
            "suggested_tools": route.get("suggested_tools", []),
            "response_guidance": route.get("response_guidance", ""),
            "skill_space_ids_configured": len(_skill_space_ids()),
            "public_skill_space_ids_configured": len(_public_skill_space_ids()),
            "custom_extension_note": "业务项目可以在 get_agentengine_tools() 之外追加 tool，也可以在 StateGraph 中增加节点。",
        }
    }


def run_specialist(state: AgentState) -> dict[str, Any]:
    model = make_langchain_chat_model()
    specialist = create_react_agent(
        model,
        TOOLS,
        prompt=SYSTEM_PROMPT,
        version="v2",
        name="agentengine_toolsets_specialist",
    )
    route = state.get("route") or {}
    custom_context = state.get("custom_context") or {}
    messages = [
        SystemMessage(
            content=(
                f"外层 LangGraph 路由: {route}. "
                f"自定义上下文: {custom_context}. "
                "优先使用 suggested_tools 中的工具；工具不可用时说明缺少哪些环境变量。"
            )
        ),
        *state["messages"],
    ]
    result = specialist.invoke({"messages": messages})
    return {"specialist_messages": result.get("messages", [])}


def finalize_answer(state: AgentState) -> dict[str, Any]:
    answer = ""
    for message in reversed(state.get("specialist_messages") or []):
        if isinstance(message, AIMessage) and message.content:
            answer = str(message.content)
            break
    if not answer:
        answer = "没有生成有效回答。请检查模型配置，或先询问“当前组件状态”。"
    return {"answer": answer, "messages": [AIMessage(content=answer)]}


workflow = StateGraph(AgentState)
workflow.add_node("route_turn", route_turn)
workflow.add_node("prepare_custom_context", prepare_custom_context)
workflow.add_node("run_specialist", run_specialist)
workflow.add_node("finalize_answer", finalize_answer)
workflow.add_edge(START, "route_turn")
workflow.add_edge("route_turn", "prepare_custom_context")
workflow.add_edge("prepare_custom_context", "run_specialist")
workflow.add_edge("run_specialist", "finalize_answer")
workflow.add_edge("finalize_answer", END)

root_agent = workflow.compile()
