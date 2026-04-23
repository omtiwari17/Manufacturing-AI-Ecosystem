from crewai import Agent, LLM
import os

DEFAULT_MODEL = "groq/llama-3.3-70b-versatile"

def _make_llm(api_key: str, model: str = DEFAULT_MODEL):
    return LLM(
        model=model,
        api_key=api_key,
    )

def build_researcher(api_key: str, model: str = DEFAULT_MODEL):
    llm = _make_llm(api_key, model)
    return Agent(
        role="Supplier Researcher",
        goal="Find potential suppliers matching the sourcing query and return JSON only.",
        backstory="You are good at structured web research and evidence capture.",
        llm=llm,
        verbose=False,
    )

def build_writer(api_key: str, model: str = DEFAULT_MODEL):
    llm = _make_llm(api_key, model)
    return Agent(
        role="Supplier Report Writer",
        goal="Convert research dataset into ranked suppliers + markdown report.",
        backstory="You write structured, clear supplier comparisons.",
        llm=llm,
        verbose=False,
    )