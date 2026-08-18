# Activation Map

Purpose:

```text
Define the first files to load when operating inside AgencyOS Teams.
```

## Default Load Order

Use this order when a user starts work from inside `agencyos-teams`:

```text
1. DEFAULT-RUN-CONTRACT.md
2. README.md
3. FIRST-RUN.md
4. INSTALLATION-MODES.md
5. beings/TEAM-BEING-ROSTER.md
6. beings/specialists/README.md
7. CREATE-BEING-CONTRACT.md
8. governance/GOVERNANCE-STANDARD.md
9. handoffs/HANDOFF-TEMPLATE.md
10. projects/
11. workstreams/
12. agencyos-pro/getting-started-operator.md
```

## Operating Meaning

```text
DEFAULT-RUN-CONTRACT.md defines implied permission and closeout behavior.
README.md defines the product surface.
FIRST-RUN.md defines startup.
INSTALLATION-MODES.md defines standalone, sidecar, and embedded installs.
beings/ defines who can work.
specialists/ defines the named specialist identities.
CREATE-BEING-CONTRACT.md defines how new Beings are created.
governance/ defines what is allowed.
handoffs/ defines how work moves.
projects/ defines where complex projects live.
workstreams/ defines where work lives.
agencyos-pro/ defines the routing engine.
```

## First Decision

Before routing work, decide:

```text
Is this an existing project?
Is this a new project?
Which workstreams belong inside it?
Is this small enough for AgencyOS One?
```

## Default Command Shape

```text
@operator Route this through AgencyOS Teams.
```

The operator personality is Jaavis unless the user explicitly selects another Being.
