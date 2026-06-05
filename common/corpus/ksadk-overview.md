# KSADK 概览

KSADK 是面向 Agent 开发、调试、部署和运行时集成的开发套件。它提供本地运行、托管 Web UI、部署、Responses 兼容接口、知识库上下文、长期记忆和工作区文件等能力。

开发者通常先在本地通过 `uv run agentengine run -i .` 验证 Agent，再使用 `uv run agentengine web .` 打开调试界面，最后通过 `uv run agentengine deploy .` 部署到 AgentEngine。
