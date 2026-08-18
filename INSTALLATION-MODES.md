# Installation Modes

Purpose:

```text
Define how AgencyOS Teams can be installed or added to a working environment.
```

## Standalone

Use when AgencyOS Teams is the whole operating surface.

```text
Desktop/
  agencyos-teams/
```

Best for:

```text
client delivery systems
multi-lane launches
research-to-GTM work
operations buildouts
parallel AI team workflows
```

## Sidecar

Use when AgencyOS Teams supports an existing project without mixing into source files.

```text
existing-project/
  agencyos-teams/
  src/
  docs/
```

Best for:

```text
adding multi-agent operating support to an existing product
keeping source code clean
tracking projects, workstreams, governance, and handoffs outside runtime code
```

## Embedded

Use when AgencyOS Teams should live inside a project as its local operating layer.

```text
existing-project/
  agencyos/
```

Best for:

```text
project-specific governance
client handoff packages
portable operating systems
```

## Recommended Default

```text
Sidecar
```

Sidecar lets AgencyOS Teams govern or support a project without polluting runtime code.
