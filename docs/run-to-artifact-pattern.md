# Run-to-Artifact Pattern

This repo follows a clear split between the request input and the generated evidence artifact.

## 1) Submit a request form

Store a valid request in the `requests/` folder before execution.

```json
{
  "request_id": "local-lmstudio-runbook",
  "title": "Draft a local LM Studio validation runbook",
  "actor_id": "actor-operator",
  "requested_outcome": "Draft a short internal runbook for validating a local LM Studio setup before using it on team workflows.",
  "action_class": "internal_artifact",
  "reversible": true,
  "external": false,
  "sensitive": false,
  "required_workstreams": ["research"],
  "deliverable_format": "markdown",
  "constraints": {
    "tone": "internal and professional",
    "length": "short",
    "audience": "team members validating local AI workflows",
    "approval_required": true
  }
}
```

## 2) Run the model-draft workflow

The runtime accepts the request, routes it to the correct workstream, and writes the result to an artifact directory managed by AgencyOS.

Typical runtime output path:

```text
.agencyos-runtime/artifacts/<run_id>/drafts/<artifact-name>.md
```

For the live validation run, the artifact was created at:

```text
.agencyos-runtime/artifacts/run-2b0020d0ff1d/drafts/runbook.md
```

## 3) Keep a shareable copy outside the runtime folder

For easier access, the generated markdown can also be mirrored into a human-facing folder such as:

```text
artifacts/local-lmstudio-runbook.md
```

This keeps the runtime-managed artifact as the source of truth while still creating a usable copy for review, sharing, or archival.

## Why this matters

The model response alone is not the final output. The artifact is the durable deliverable. In AgencyOS, the run is not complete until the document is written to a real file path and can be inspected, approved, and reused.
