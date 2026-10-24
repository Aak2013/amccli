from __future__ import annotations

import re

LATEX_RE = re.compile(r"\$([^$]+)\$")


def plainify(text: str | None) -> str:
    if not text:
        return ""
    return LATEX_RE.sub(lambda m: m.group(1).strip(), text)


def render_question(question: dict, plain: bool = False, with_answer: bool = False, with_solution: bool = False) -> str:
    text = [
        f"#{question.get('id', '?')} | {question.get('contest', '')} {question.get('year', '')} {question.get('paper', '')} {question.get('problem_no', '')}".strip(),
        f"Difficulty: {question.get('difficulty', '-')}",
        "",
        question.get("stem", ""),
    ]
    options = question.get("options") or {}
    if options:
        for key in sorted(options):
            value = options[key]
            if plain:
                value = plainify(value)
            text.append(f"{key.upper()}. {value}")
    if with_answer and question.get("answer"):
        text.extend(["", f"Answer: {question['answer']}"])
    if with_solution and question.get("solution"):
        text.extend(["", "Solution:", question["solution"]])
    rendered = "\n".join(filter(None, text))
    return plainify(rendered) if plain else rendered
