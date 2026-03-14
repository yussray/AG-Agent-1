# ============================================================
# research_workflow.py — Antigravity Multi-Agent System
# Pre-built workflows: Research, Web Search, Slides, Q&A
# ============================================================

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import paths  # noqa: E402

from workflow_engine import WorkflowEngine, WorkflowStep, engine
from workflow_engine import step_ollama_generate, step_anythingllm_query, step_save_to_file


def build_research_workflow(topic: str) -> list:
    """Workflow: Research a topic using RAG, then generate a summary report."""

    def set_topic(context: dict, topic: str) -> str:
        context["input"] = f"What do you know about: {topic}?"
        context["topic"] = topic
        return topic

    def build_summary_prompt(context: dict) -> str:
        rag_result = context.get("query_knowledge_base", "No data retrieved.")
        topic = context.get("topic", "unknown")
        prompt = (
            f"You are a research assistant. Based on the following retrieved knowledge, "
            f"write a clear, structured research summary about: {topic}\n\n"
            f"Retrieved Knowledge:\n{rag_result}\n\n"
            f"Write a professional summary with sections: Overview, Key Points, Conclusion."
        )
        context["summary_prompt"] = prompt
        return prompt

    def generate_summary(context: dict) -> str:
        return step_ollama_generate(context, prompt_key="summary_prompt")

    def save_report(context: dict) -> str:
        import re
        topic = context.get("topic", "report")
        slug = re.sub(r'[^\w]', '_', topic.lower())[:30]
        return step_save_to_file(context, "generate_summary", f"research_{slug}.txt")

    return [
        WorkflowStep("Set Topic", set_topic, params={"topic": topic}),
        WorkflowStep("Query Knowledge Base", step_anythingllm_query, params={"query_key": "input"}, retries=2),
        WorkflowStep("Build Summary Prompt", build_summary_prompt),
        WorkflowStep("Generate Summary", generate_summary, retries=2),
        WorkflowStep("Save Report", save_report),
    ]


def build_web_search_workflow(query: str, url: str = None) -> list:
    """Workflow: Search internet and summarise with Ollama."""

    def scrape_web(context: dict) -> str:
        context["query"] = query
        context["url"] = url or ""
        from tavily_search import search_and_scrape as tavily_search_and_scrape
        result = tavily_search_and_scrape(query=query, n=3, url=url)
        context["scraped_content"] = result
        return result

    def summarise_results(context: dict) -> str:
        scraped = context.get("scraped_content", "No content retrieved.")
        prompt = (
            f"Based on the following web content, provide a clear and concise summary "
            f"addressing the user's query: '{query}'\n\n"
            f"Web Content:\n{scraped[:6000]}\n\n"
            f"Write a well-structured summary with key findings."
        )
        context["summarise_prompt"] = prompt
        return step_ollama_generate(context, prompt_key="summarise_prompt")

    return [
        WorkflowStep("Scrape Web", scrape_web, retries=2),
        WorkflowStep("Summarise Results", summarise_results, retries=2),
    ]


def build_slides_workflow(topic: str) -> list:
    """Workflow: Designer Skill → structured outline → PPTX generation."""

    def set_topic(context: dict, topic: str) -> str:
        context["topic"] = topic
        return topic

    def run_designer(context: dict) -> str:
        from designer_skill import designer
        topic = context.get("topic", "")
        context["input"] = topic
        rag_context = context.get("query_knowledge_base", "")
        outline = designer.design_presentation(topic, context=rag_context)
        context["slide_prompt"] = outline
        return outline

    def save_slides(context: dict) -> str:
        import re
        topic = context.get("topic", "slides")
        slug = re.sub(r'[^\w]', '_', topic.lower())[:30]
        return step_save_to_file(context, "run_designer", f"slides_{slug}.txt")

    return [
        WorkflowStep("Set Topic", set_topic, params={"topic": topic}),
        WorkflowStep("Designer Skill", run_designer, retries=2),
        WorkflowStep("Save Slides Outline", save_slides),
    ]


def build_qa_workflow(question: str) -> list:
    """Workflow: Answer a question using RAG + Ollama refinement."""

    def set_question(context: dict, question: str) -> str:
        context["input"] = question
        context["question"] = question
        return question

    def refine_answer(context: dict) -> str:
        rag = context.get("query_knowledge_base", "No relevant documents found.")
        question = context.get("question", "")
        prompt = (
            f"Using the following retrieved knowledge, provide a precise and professional answer.\n\n"
            f"Question: {question}\n\n"
            f"Retrieved Knowledge:\n{rag}\n\n"
            f"Answer clearly and concisely."
        )
        context["refine_prompt"] = prompt
        return step_ollama_generate(context, prompt_key="refine_prompt")

    return [
        WorkflowStep("Set Question", set_question, params={"question": question}),
        WorkflowStep("Query Knowledge Base", step_anythingllm_query, params={"query_key": "input"}, retries=2),
        WorkflowStep("Refine Answer", refine_answer, retries=2),
    ]


def register_all(eng: WorkflowEngine = engine):
    """Register all built-in workflows with the engine."""
    eng._registry["research_report"] = []
    eng._registry["generate_slides"] = []
    eng._registry["qa_with_rag"] = []
    eng._registry["web_search"] = []
    return eng


register_all()
