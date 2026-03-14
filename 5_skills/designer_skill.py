# ============================================================
# designer_skill.py — Antigravity Multi-Agent System
# Designer Skill: Universal Output Polisher
# Structures and polishes content before it reaches the tool layer
# ============================================================

import os
import json
from ollama_connector import ollama
from config import REASONING_MODEL

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "layout_templates")


def _load_template(name: str) -> dict:
    """Load a JSON layout template by name."""
    path = os.path.join(TEMPLATES_DIR, f"{name}.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


PRESENTATION_LAYOUT = _load_template("presentation_layout")
REPORT_LAYOUT = _load_template("report_layout")
SPREADSHEET_LAYOUT = _load_template("spreadsheet_layout")


class DesignerSkill:
    """
    Converts raw user intent and content into structured, polished
    document outlines before they are passed to the tool layer.
    """

    def __init__(self, model: str = REASONING_MODEL):
        self.model = model

    def design_presentation(self, topic: str, context: str = "") -> str:
        structure = PRESENTATION_LAYOUT["slide_structure"]
        rules = PRESENTATION_LAYOUT["design_rules"]
        anti = PRESENTATION_LAYOUT["anti_patterns"]

        slide_types = "\n".join([
            f"  Slide {s['slide']}: {s['type'].upper()} — {s['purpose']}"
            for s in structure
        ])

        prompt = (
            f"You are a professional presentation designer.\n\n"
            f"Create a structured PowerPoint slide outline about: **{topic}**\n\n"
            f"Use this exact slide structure:\n{slide_types}\n\n"
            f"Design rules:\n"
            f"- Maximum {rules['max_bullets_per_slide']} bullets per slide\n"
            f"- Maximum {rules['max_words_per_bullet']} words per bullet\n"
            f"- Title maximum {rules['title_max_words']} words\n"
            f"- Style: {rules['style']}\n\n"
            f"Avoid these anti-patterns: {', '.join(anti)}\n\n"
            + (f"Background knowledge to incorporate:\n{context}\n\n" if context else "")
            + "Format output as:\n"
            f"SLIDE 1: [Title]\n"
            f"  - bullet\n"
            f"  - bullet\n\n"
            f"SLIDE 2: [Title]\n"
            f"  - bullet\n"
            f"Continue for all {len(structure)} slides. Output only the slide outline."
        )

        return ollama.generate(model=self.model, prompt=prompt)

    def design_report(self, topic: str, context: str = "") -> str:
        structure = REPORT_LAYOUT["document_structure"]
        rules = REPORT_LAYOUT["design_rules"]
        anti = REPORT_LAYOUT["anti_patterns"]

        sections = "\n".join([
            f"  {s['section']}. {s['heading']}: {s['purpose']}"
            for s in structure
        ])

        prompt = (
            f"You are a professional technical writer.\n\n"
            f"Write a complete structured report about: **{topic}**\n\n"
            f"Use this exact document structure:\n{sections}\n\n"
            f"Rules:\n"
            f"- Executive Summary: maximum {rules['executive_summary_max_words']} words\n"
            f"- Paragraphs: maximum {rules['max_paragraph_sentences']} sentences each\n"
            f"- Use ## for section headings\n"
            f"- Use - for bullet points\n\n"
            f"Avoid: {', '.join(anti)}\n\n"
            + (f"Background knowledge:\n{context}\n\n" if context else "")
            + "Write the complete report now. Format headings as ## Section Name."
        )

        return ollama.generate(model=self.model, prompt=prompt)

    def design_spreadsheet(self, topic: str, data_description: str = "") -> dict:
        structure = SPREADSHEET_LAYOUT["sheet_structure"]

        prompt = (
            f"You are a data analyst.\n\n"
            f"Design a structured Excel spreadsheet about: **{topic}**\n\n"
            f"Return ONLY valid JSON in this exact format:\n"
            f"{{\n"
            f"  \"headers\": [\"col1\", \"col2\", ...],\n"
            f"  \"sample_rows\": [[\"val\", \"val\"], [\"val\", \"val\"]],\n"
            f"  \"summary\": {{\"key_metric\": \"value\"}},\n"
            f"  \"insights\": [\"insight 1\", \"insight 2\"]\n"
            f"}}\n\n"
            + (f"Data context: {data_description}\n\n" if data_description else "")
            + "Output only valid JSON. No explanation."
        )

        raw = ollama.generate(model=self.model, prompt=prompt, temperature=0.1)

        import re
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                import json
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        return {
            "headers": ["Name", "Value", "Notes"],
            "sample_rows": [["Item 1", "100", topic], ["Item 2", "200", topic]],
            "summary": {"total_rows": 2},
            "insights": [f"Data about {topic}", "Requires more context"]
        }

    def design(self, output_type: str, topic: str, context: str = "") -> str:
        output_type = output_type.lower()

        if output_type in ("slides", "presentation", "pptx", "powerpoint"):
            return self.design_presentation(topic, context)
        elif output_type in ("report", "word", "docx", "pdf", "document"):
            return self.design_report(topic, context)
        elif output_type in ("excel", "spreadsheet", "xlsx", "csv", "data"):
            result = self.design_spreadsheet(topic, context)
            headers = result.get("headers", [])
            rows = result.get("sample_rows", [])
            insights = result.get("insights", [])
            text = f"Headers: {', '.join(headers)}\n"
            text += f"Sample rows: {len(rows)}\n"
            text += "Insights:\n" + "\n".join(f"- {i}" for i in insights)
            return text
        else:
            return self.design_report(topic, context)


# Singleton instance
designer = DesignerSkill()
