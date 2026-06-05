from google.adk.agents import Agent

from common.model_config import make_adk_litellm_model


root_agent = Agent(
    name="sample_template",
    model=make_adk_litellm_model(),
    description="KSADK sample template.",
    instruction="You are a concise assistant.",
)

