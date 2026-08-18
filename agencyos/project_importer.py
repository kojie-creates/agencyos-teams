"""Import existing markdown-led project packets into typed runtime records."""

from __future__ import annotations

import re
import hashlib
from pathlib import Path

from agencyos.schemas import (
    Agency,
    Artifact,
    Being,
    Claim,
    CloseoutPacket,
    EvidenceItem,
    Handoff,
    LearningProposal,
    Policy,
    Project,
    Registry,
    Request,
    EvidenceStatus,
    RuntimeStatus,
    WorkItem,
    Workstream,
)


def import_project_folder(project_path: Path, output_path: Path | None = None) -> Registry:
    project_path = Path(project_path)
    project_id = f"project-{project_path.name}"
    project_brief = _read(project_path / "project-brief.md")
    plan = _read(project_path / "plan.md")
    assigned_beings = _read(project_path / "assigned-beings.md")
    assigned_agencies = _read(project_path / "assigned-agencies.md")
    governance_notes = _read(project_path / "governance-notes.md")
    handoffs = _read(project_path / "handoffs.md")
    closeout = _read(project_path / "closeout.md")
    learning = _read(project_path / "learning.md")

    project_name = _section_code(project_brief, "Project Name") or _title_from_slug(project_path.name)
    owner = _section_code(project_brief, "Owner") or "human-unknown"
    outcome = _section_code(project_brief, "Outcome") or _section_code(project_brief, "Value Hypothesis") or "Imported project packet."

    project = Project(
        id=project_id,
        actor_id=_actor_id(owner),
        name=project_name,
        human_owner_id=_human_owner_id(owner),
        source_path=str(project_path),
        status=RuntimeStatus.PLANNED,
    )
    request = Request(
        id=f"request-{project_path.name}",
        actor_id=_actor_id(owner),
        human_owner_id=project.human_owner_id or "human-unknown",
        desired_outcome=outcome,
        source_inputs=[str(project_path / "project-brief.md")],
        definition_of_done=_section_lines(project_brief, "Success Criteria"),
        off_limits_actions=_section_lines(project_brief, "Non-Goals"),
        status=RuntimeStatus.RECEIVED,
    )

    workstreams = [
        Workstream(
            id=f"workstream-{_slug(row['Workstream'])}",
            actor_id="actor-athena",
            project_id=project_id,
            name=row["Workstream"],
            owner_actor_id=_owner_actor_id(row.get("Owner", "")),
            definition_of_done=[row.get("Purpose", "")],
            status=_status(row.get("Status", "")),
        )
        for row in _markdown_table(plan, ["Workstream", "Purpose", "Owner", "Status"])
    ]

    beings = [
        Being(
            id=f"being-{_slug(row['Being'])}",
            actor_id="actor-operator",
            display_name=row["Being"],
            runtime_actor_id=_handle_to_actor(row.get("Handle", row["Being"])),
            role_ids=[_slug(row.get("Project Role", ""))],
            capability_ids=[_slug(item) for item in _split_list(row.get("Workstreams", ""))],
            permission_ids=[],
            status=RuntimeStatus.READY,
        )
        for row in _markdown_table(assigned_beings, ["Being", "Handle", "Project Role", "Workstreams", "Approval Limits"])
    ]

    agencies = [
        Agency(
            id=f"agency-{_slug(row['Agency'])}",
            actor_id="actor-operator",
            name=row["Agency"],
            member_actor_ids=[_handle_to_actor(item) for item in _split_list(row.get("Members", "")) if item.startswith("@")],
            capability_ids=[_slug(item) for item in _split_list(row.get("Workstreams", ""))],
            status=RuntimeStatus.READY,
        )
        for row in _markdown_table(assigned_agencies, ["Agency", "Lead", "Members", "Workstreams", "Output"])
    ]

    policy = Policy(
        id=f"policy-{project_path.name}",
        actor_id="actor-operator",
        name=f"{project_name} governance notes",
        version="imported-markdown-v1",
        rules=_code_blocks(governance_notes),
        status=RuntimeStatus.READY,
    )

    imported_handoffs = [
        Handoff(
            id=_stable_handoff_id(row.get("Handoff ID", "")),
            actor_id=_handle_to_actor(row.get("Source", "@operator")),
            project_id=project_id,
            workstream_id=f"workstream-{_slug(row.get('Workstream', 'general'))}",
            destination=_handle_to_actor(row.get("Destination", "review")),
            status=_status(row.get("Status", "")),
        )
        for row in _markdown_table(handoffs, ["Handoff ID", "Workstream", "Source", "Destination", "Status", "Evidence Status"])
    ]
    evidence = [
        EvidenceItem(
            id=f"evidence-{project_path.name}-{_slug(path.name)}",
            actor_id="actor-vera",
            project_id=project_id,
            workstream_id="workstream-source-synthesis",
            summary=f"Imported evidence file {path.name}.",
            source_ref=_relative_project_path(project_path, path),
            evidence_status="unknown",
            sensitive=path.suffix.lower() == ".json",
            status=RuntimeStatus.READY,
        )
        for path in sorted((project_path / "evidence").glob("*"))
        if path.is_file()
    ]
    artifacts = [
        Artifact(
            id=f"artifact-{project_path.name}-{_slug(path.name)}",
            actor_id="actor-jaavis",
            project_id=project_id,
            workstream_id="workstream-source-synthesis",
            path=_relative_project_path(project_path, path),
            content_hash=_sha256(path),
            creator_actor_id="actor-jaavis",
            release_status=RuntimeStatus.HOLD,
            status=RuntimeStatus.UNDER_REVIEW,
        )
        for path in sorted((project_path / "deliverables").glob("*"))
        if path.is_file()
    ]
    claims = [
        claim
        for path in sorted((project_path / "deliverables").glob("*"))
        if path.is_file()
        for claim in _claims_from_deliverable(project_path, path)
    ]
    work_items = _import_workstream_readmes(project_path, project_id)
    closeout_packet = CloseoutPacket(
        id=f"closeout-{project_path.name}",
        actor_id="actor-jaavis",
        project_id=project_id,
        status=RuntimeStatus.CLOSED if "First-run packet created" in closeout else RuntimeStatus.UNDER_REVIEW,
        artifact_ids=_section_lines(closeout, "Completion State") + [artifact.id for artifact in artifacts],
        evidence_ids=[item.id for item in evidence],
    )
    learning_records = [
        LearningProposal(
            id=f"learning-{project_path.name}-{index + 1}",
            actor_id="actor-elias",
            project_id=project_id,
            proposed_learning=note,
            evidence_ids=[item.id for item in evidence],
            status=RuntimeStatus.UNDER_REVIEW,
        )
        for index, note in enumerate(_section_lines(learning, "Reuse Notes"))
    ]

    registry = Registry(
        projects=[project],
        requests=[request],
        workstreams=workstreams,
        work_items=work_items,
        beings=beings,
        agencies=agencies,
        policies=[policy],
        handoffs=imported_handoffs,
        evidence=evidence,
        artifacts=artifacts,
        claims=claims,
        closeouts=[closeout_packet],
        learning=learning_records,
    )
    if output_path:
        output_path.write_text(registry.model_dump_json(indent=2), encoding="utf-8")
    return registry


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _import_workstream_readmes(project_path: Path, project_id: str) -> list[WorkItem]:
    items = []
    for readme in sorted((project_path / "workstreams").glob("*/README.md")):
        markdown = _read(readme)
        workstream_id = f"workstream-{_slug(readme.parent.name)}"
        purpose = _plain_section(markdown, "Purpose") or "Imported workstream task."
        outputs = _section_lines(markdown, "Outputs")
        checks = _section_lines(markdown, "Checks")
        stages = _section_lines(markdown, "Stages")
        definition_of_done = checks or stages or outputs or [purpose]
        pause_condition = _plain_section(markdown, "Blocked Until") or None
        items.append(
            WorkItem(
                id=f"workitem-{_slug(readme.parent.name)}",
                actor_id=_owner_actor_id(_plain_section(markdown, "Owner")),
                project_id=project_id,
                workstream_id=workstream_id,
                task=purpose,
                assigned_actor_id=_owner_actor_id(_plain_section(markdown, "Owner")),
                expected_output="\n".join(outputs),
                inputs=_section_lines(markdown, "Inputs"),
                source_of_truth_refs=_section_lines(markdown, "Inputs"),
                risk_level="low",
                required_evidence=[],
                definition_of_done=definition_of_done,
                pause_condition=pause_condition,
                status=_status(_plain_section(markdown, "Status")),
            )
        )
    return items


def _claims_from_deliverable(project_path: Path, path: Path) -> list[Claim]:
    artifact_id = f"artifact-{project_path.name}-{_slug(path.name)}"
    markdown = _read(path)
    claims = []
    for row in _markdown_table(markdown, ["Claim", "Status"]):
        text = row.get("Claim", "").strip()
        if not text:
            continue
        claims.append(
            Claim(
                id=f"claim-{project_path.name}-{_slug(path.name)}-{len(claims) + 1}",
                actor_id="actor-vera",
                artifact_id=artifact_id,
                text=text,
                claim_type="evidence_status_table",
                evidence_status=_evidence_status(row.get("Status", "")),
                status=RuntimeStatus.UNDER_REVIEW,
            )
        )
    return claims


def _section_code(markdown: str, heading: str) -> str:
    pattern = rf"## {re.escape(heading)}\s+```text\s+(.*?)\s+```"
    match = re.search(pattern, markdown, flags=re.DOTALL)
    return " ".join(match.group(1).strip().split()) if match else ""


def _plain_section(markdown: str, heading: str) -> str:
    text = _plain_section_raw(markdown, heading)
    return " ".join(text.strip().split()) if text else ""


def _plain_section_raw(markdown: str, heading: str) -> str:
    pattern = rf"{re.escape(heading)}:\s+```text\s+(.*?)\s+```"
    match = re.search(pattern, markdown, flags=re.DOTALL)
    return match.group(1).strip() if match else ""


def _section_lines(markdown: str, heading: str) -> list[str]:
    text = _section_code(markdown, heading) or _plain_section_raw(markdown, heading)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) > 1:
        return lines
    return [line.strip() for line in text.split(".") if line.strip()]


def _code_blocks(markdown: str) -> list[str]:
    return [" ".join(match.strip().split()) for match in re.findall(r"```text\s+(.*?)\s+```", markdown, flags=re.DOTALL)]


def _markdown_table(markdown: str, expected_headers: list[str]) -> list[dict[str, str]]:
    lines = [line.strip() for line in markdown.splitlines() if line.strip().startswith("|")]
    for index, line in enumerate(lines):
        headers = _table_cells(line)
        if headers == expected_headers and index + 1 < len(lines):
            rows = []
            for row_line in lines[index + 2 :]:
                cells = _table_cells(row_line)
                if len(cells) != len(headers):
                    break
                rows.append(dict(zip(headers, cells)))
            return rows
    return []


def _table_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip("|").split("|")]


def _title_from_slug(slug: str) -> str:
    return " ".join(part.capitalize() for part in slug.split("-"))


def _slug(value: str) -> str:
    value = value.strip().lstrip("@").lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "unknown"


def _actor_id(owner: str) -> str:
    slug = _slug(owner)
    if slug in {"kojie", "felix"}:
        return "human-kojie"
    if slug.startswith("human-"):
        return slug
    return f"actor-{slug}"


def _human_owner_id(owner: str) -> str:
    slug = _slug(owner)
    if slug in {"kojie", "felix"}:
        return "human-kojie"
    if slug.startswith("human-"):
        return slug
    return f"human-{slug}"


def _handle_to_actor(value: str) -> str:
    first = _split_list(value)[0] if _split_list(value) else value
    slug = _slug(first)
    if slug == "operator":
        return "actor-operator"
    return f"actor-{slug}"


def _owner_actor_id(value: str) -> str:
    first = _split_list(value)[0] if _split_list(value) else value
    return _handle_to_actor(first)


def _split_list(value: str) -> list[str]:
    return [item.strip() for item in re.split(r"\+|,", value) if item.strip() and item.strip().lower() != "all"]


def _status(value: str) -> RuntimeStatus:
    normalized = _slug(value)
    if normalized in {"started", "planned"}:
        return RuntimeStatus.PLANNED
    if normalized == "complete":
        return RuntimeStatus.CLOSED
    return RuntimeStatus.RECEIVED


def _evidence_status(value: str) -> EvidenceStatus:
    normalized = _slug(value).replace("-", "_")
    try:
        return EvidenceStatus(normalized)
    except ValueError:
        return EvidenceStatus.UNKNOWN


def _stable_handoff_id(value: str) -> str:
    slug = _slug(value)
    return slug if slug.startswith("handoff-") else f"handoff-{slug}"


def _relative_project_path(project_path: Path, path: Path) -> str:
    return path.relative_to(project_path).as_posix()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return f"sha256:{digest}"
