#!/usr/bin/env python3
"""Run dev-team diagnostic intake and collect optional uploads."""

from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


DEFAULT_PROJECT = Path("projects") / "first-run"

QUESTIONS = [
    (
        "work_boundary",
        "What user work is this system expected to support, and where does that work begin and end?",
    ),
    (
        "input_sources",
        "What inputs, tools, files, or systems does the work currently depend on?",
    ),
    (
        "source_of_truth",
        "Which input or system should be treated as the source of truth when outputs disagree?",
    ),
    (
        "deterministic_steps",
        "Which steps must be handled by deterministic logic, rules, formulas, code, or another verified process before AI is used?",
    ),
    (
        "validation_checks",
        "What checks prove the generated output matches the source material and approved process?",
    ),
    (
        "ai_boundary",
        "What is the AI allowed to draft, summarize, classify, or recommend, and what must it never decide?",
    ),
    (
        "output_format",
        "What final output format does the user need, and what structure must stay consistent?",
    ),
    (
        "handoff_and_approval",
        "Who reviews the output, what approval gates are required, and what evidence should be attached before the work continues?",
    ),
]

USE_CASES = {
    "diana-spend-reporting-assistant": {
        "name": "Diana Spend Reporting Assistant",
        "user": "Diana",
        "work": "spend reporting assistant work",
        "summary": (
            "The user has an automated assistant that generates analysis, observations, "
            "recommendations, and client-ready text, but outputs require manual correction. "
            "The use case should preserve the user's expert interpretation while requiring "
            "verified source-grounded outputs before AI-generated narrative."
        ),
        "source_paths": [
            r"C:\Users\felix\Downloads\DianaBrief.md-1.pdf",
            r"C:\Users\felix\Downloads\Diana_DevTeam.md-1.pdf",
            r"C:\Users\felix\Downloads\Diana_ExecutiveTeam.md-1.pdf",
        ],
    }
}


@dataclass(frozen=True)
class Answer:
    question_id: str
    question: str
    answer: str
    uploads: list[Path]


@dataclass(frozen=True)
class PacketResult:
    markdown_path: Path
    json_path: Path
    upload_dir: Path


def parse_uploads(raw: str) -> list[Path]:
    if not raw.strip():
        return []
    return [Path(part.strip()).expanduser() for part in raw.split(";") if part.strip()]


def default_project(root: Path = Path.cwd()) -> Path:
    context = root / ".first-run.json"
    if context.exists():
        data = json.loads(context.read_text(encoding="utf-8"))
        slug = data.get("slug")
        if slug:
            return root / "projects" / slug
    return root / DEFAULT_PROJECT


def _unique_destination(upload_dir: Path, source: Path) -> Path:
    candidate = upload_dir / source.name
    if not candidate.exists():
        return candidate

    stem = source.stem
    suffix = source.suffix
    index = 2
    while True:
        candidate = upload_dir / f"{stem}-{index}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def _validate_uploads(answers: list[Answer]) -> None:
    for answer in answers:
        for upload in answer.uploads:
            if not upload.exists() or not upload.is_file():
                raise FileNotFoundError(f"Upload not found: {upload}")


def write_response_packet(
    project: Path,
    answers: list[Answer],
    use_case: dict | None = None,
) -> PacketResult:
    _validate_uploads(answers)

    evidence_dir = project / "evidence"
    upload_dir = evidence_dir / "dev-team-diagnostic-uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    stored_responses = []
    for answer in answers:
        stored_uploads = []
        for upload in answer.uploads:
            destination = _unique_destination(upload_dir, upload)
            shutil.copy2(upload, destination)
            stored_uploads.append(
                {
                    "source_path": str(upload),
                    "stored_path": str(destination),
                }
            )
        stored_responses.append(
            {
                "question_id": answer.question_id,
                "question": answer.question,
                "answer": answer.answer,
                "uploads": stored_uploads,
            }
        )

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        "project": str(project),
        "generated_at": generated_at,
        "use_case": use_case or {},
        "responses": stored_responses,
    }

    json_path = evidence_dir / "dev-team-diagnostic-responses.json"
    markdown_path = evidence_dir / "dev-team-diagnostic-responses.md"

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    markdown_path.write_text(render_markdown(payload), encoding="utf-8")

    return PacketResult(
        markdown_path=markdown_path,
        json_path=json_path,
        upload_dir=upload_dir,
    )


def render_markdown(payload: dict) -> str:
    lines = [
        "# Dev-Team Diagnostic Responses",
        "",
        "Generated:",
        "",
        "```text",
        payload["generated_at"],
        "```",
        "",
    ]

    use_case = payload.get("use_case") or {}
    if use_case:
        lines.extend(
            [
                "## Use Case",
                "",
                f"Name: {use_case.get('name', '')}",
                "",
                f"User: {use_case.get('user', '')}",
                "",
                f"Work: {use_case.get('work', '')}",
                "",
                "Summary:",
                "",
                "```text",
                use_case.get("summary", ""),
                "```",
                "",
                "Sources:",
                "",
            ]
        )
        for source_path in use_case.get("source_paths", []):
            lines.append(f"- {source_path}")
        lines.append("")

    lines.extend(["## Responses", ""])

    for item in payload["responses"]:
        lines.extend(
            [
                f"### {item['question_id']}",
                "",
                "Question:",
                "",
                "```text",
                item["question"],
                "```",
                "",
                "Answer:",
                "",
                "```text",
                item["answer"],
                "```",
                "",
                "Uploads:",
                "",
            ]
        )
        if item["uploads"]:
            for upload in item["uploads"]:
                lines.append(f"- {upload['stored_path']}")
        else:
            lines.append("- none")
        lines.append("")

    return "\n".join(lines)


def collect_interactive() -> list[Answer]:
    answers = []
    print("Dev-team diagnostic intake")
    print("Upload paths: paste file paths separated by semicolons. Leave blank for none.\n")

    for question_id, question in QUESTIONS:
        print(f"[{question_id}]")
        print(question)
        answer = input("Answer: ").strip()
        uploads = parse_uploads(input("Uploads: ").strip())
        print()
        answers.append(
            Answer(
                question_id=question_id,
                question=question,
                answer=answer,
                uploads=uploads,
            )
        )

    return answers


def resolve_use_case(name: str) -> dict | None:
    if not name:
        return None
    return USE_CASES.get(name)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run dev-team diagnostic intake and collect uploads."
    )
    parser.add_argument(
        "--project",
        default="",
        help="Project packet path.",
    )
    parser.add_argument(
        "--use-case",
        choices=sorted(USE_CASES),
        default="",
        help="Optional named use case context.",
    )
    args = parser.parse_args()

    project = Path(args.project) if args.project else default_project()
    answers = collect_interactive()
    result = write_response_packet(project, answers, use_case=resolve_use_case(args.use_case))

    print(f"Wrote: {result.markdown_path}")
    print(f"Wrote: {result.json_path}")
    print(f"Uploads: {result.upload_dir}")


if __name__ == "__main__":
    main()
