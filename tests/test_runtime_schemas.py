import unittest

from pydantic import ValidationError

from agencyos.schemas import (
    Actor,
    ActorKind,
    Agency,
    Approval,
    ApprovalDecision,
    ApprovalRequest,
    Artifact,
    ArtifactVersion,
    Capability,
    Claim,
    CloseoutPacket,
    Dependency,
    EvidenceItem,
    Handoff,
    Permission,
    Project,
    Registry,
    Request,
    Being,
    RiskLevel,
    RuntimeEvent,
    RuntimeStatus,
    SchemaMigrationError,
    ToolGrant,
    Verification,
    WorkItem,
    WorkPacket,
    Workstream,
    migrate_record,
    schema_catalog,
    validate_transition,
)


class RuntimeSchemaTests(unittest.TestCase):
    def test_valid_runtime_record_set_loads(self):
        project = Project(
            id="project-demo",
            actor_id="actor-operator",
            name="Demo",
            status=RuntimeStatus.PLANNED,
        )
        workstream = Workstream(
            id="workstream-research",
            actor_id="actor-operator",
            project_id=project.id,
            name="Research",
            status=RuntimeStatus.READY,
            owner_actor_id="actor-athena",
            definition_of_done=["artifact created"],
        )
        work_item = WorkItem(
            id="workitem-1",
            actor_id="actor-athena",
            project_id=project.id,
            workstream_id=workstream.id,
            task="Create artifact",
            assigned_actor_id="actor-specialist",
            status=RuntimeStatus.READY,
            risk_level=RiskLevel.LOW,
            definition_of_done=["evidence attached"],
        )

        registry = Registry(projects=[project], workstreams=[workstream], work_items=[work_item])

        self.assertEqual(registry.projects[0].id, "project-demo")

    def test_missing_required_authority_is_rejected(self):
        with self.assertRaises(ValidationError):
            WorkItem(
                id="workitem-no-authority",
                actor_id="actor-athena",
                project_id="project-demo",
                workstream_id="workstream-demo",
                task="Create artifact",
                status=RuntimeStatus.READY,
                risk_level=RiskLevel.LOW,
            )

    def test_unknown_status_is_rejected(self):
        with self.assertRaises(ValidationError):
            Project(id="project-demo", actor_id="actor-operator", name="Demo", status="done")

    def test_invalid_transition_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_transition(RuntimeStatus.RECEIVED, RuntimeStatus.CLOSED)

    def test_broken_references_are_rejected(self):
        project = Project(
            id="project-demo",
            actor_id="actor-operator",
            name="Demo",
            status=RuntimeStatus.PLANNED,
        )
        work_item = WorkItem(
            id="workitem-orphan",
            actor_id="actor-athena",
            project_id=project.id,
            workstream_id="missing-workstream",
            task="Create artifact",
            assigned_actor_id="actor-specialist",
            status=RuntimeStatus.READY,
            risk_level=RiskLevel.LOW,
            definition_of_done=["artifact created"],
        )

        with self.assertRaises(ValueError):
            Registry(projects=[project], work_items=[work_item])

    def test_duplicate_identifiers_are_rejected(self):
        first = Project(id="project-demo", actor_id="actor-operator", name="Demo", status=RuntimeStatus.PLANNED)
        second = Project(id="project-demo", actor_id="actor-operator", name="Other", status=RuntimeStatus.PLANNED)

        with self.assertRaises(ValueError):
            Registry(projects=[first, second])

    def test_display_name_cannot_impersonate_stable_actor_id(self):
        with self.assertRaises(ValidationError):
            Actor(
                id="Jaavis",
                actor_id="actor-operator",
                display_name="actor-jaavis",
                kind=ActorKind.BEING,
                roles=["operator"],
            )

    def test_old_schema_version_migrates_or_errors_clearly(self):
        migrated = migrate_record({"schema_version": "agencyos.runtime.v0", "id": "old-id"})
        self.assertEqual(migrated["schema_version"], "agencyos.runtime.v1")

        with self.assertRaises(SchemaMigrationError):
            migrate_record({"schema_version": "agencyos.runtime.v99", "id": "future-id"})

    def test_critical_schema_inventory_instantiates(self):
        actor = Actor(id="actor-jaavis", actor_id="actor-operator", display_name="Jaavis", kind=ActorKind.BEING, roles=["operator"])
        capability = Capability(id="cap-create", actor_id=actor.id, name="Create artifact", status=RuntimeStatus.READY)
        permission = Permission(id="perm-local", actor_id=actor.id, action="local_write", resource="project")
        tool_grant = ToolGrant(id="tool-local", actor_id=actor.id, tool_name="local_files", allowed_actions=["read", "write"])
        agency = Agency(id="agency-core", actor_id=actor.id, name="Core Agency", member_actor_ids=[actor.id])
        request = Request(id="request-demo", actor_id=actor.id, human_owner_id="human-kojie", desired_outcome="Demo")
        artifact = Artifact(id="artifact-demo", actor_id=actor.id, project_id="project-demo", workstream_id="workstream-demo", path="deliverable.md", content_hash="sha256:abc")
        claim = Claim(id="claim-demo", actor_id=actor.id, artifact_id=artifact.id, text="Supported claim")
        evidence = EvidenceItem(id="evidence-demo", actor_id=actor.id, project_id="project-demo", workstream_id="workstream-demo", summary="Evidence")
        verification = Verification(id="verification-demo", actor_id="actor-verifier", artifact_id=artifact.id, verifier_actor_id="actor-verifier", result="supported")
        approval = Approval(id="approval-demo", actor_id="human-kojie", approver_id="human-kojie", exact_action="release artifact", decision="approve", scope="artifact-demo")
        handoff = Handoff(id="handoff-demo", actor_id=actor.id, project_id="project-demo", artifact_ids=[artifact.id])
        event = RuntimeEvent(id="event-demo", actor_id=actor.id, correlation_id="run-demo", project_id="project-demo", previous_state=RuntimeStatus.READY, new_state=RuntimeStatus.RUNNING, trigger="dispatch")
        closeout = CloseoutPacket(id="closeout-demo", actor_id=actor.id, project_id="project-demo", status=RuntimeStatus.CLOSED, artifact_ids=[artifact.id], evidence_ids=[evidence.id])

        self.assertEqual(tool_grant.allowed_actions, ["read", "write"])
        self.assertEqual(agency.member_actor_ids, [actor.id])
        self.assertEqual(request.human_owner_id, "human-kojie")
        self.assertEqual(claim.artifact_id, artifact.id)
        self.assertEqual(verification.verifier_actor_id, "actor-verifier")
        self.assertEqual(approval.decision, "approve")
        self.assertEqual(handoff.artifact_ids, [artifact.id])
        self.assertEqual(event.new_state, RuntimeStatus.RUNNING)
        self.assertEqual(closeout.status, RuntimeStatus.CLOSED)

    def test_priority2_spec_schema_names_instantiate(self):
        being = Being(
            id="being-jaavis",
            actor_id="actor-operator",
            display_name="Jaavis",
            runtime_actor_id="actor-jaavis",
            role_ids=["operator"],
            capability_ids=["cap-intake"],
            permission_ids=["perm-local"],
            personality_id="personality-jaavis",
            behavioral_posture_id="posture-sentinel",
        )
        dependency = Dependency(
            id="dependency-build-after-research",
            actor_id="actor-operator",
            project_id="project-demo",
            upstream_work_item_id="workitem-research",
            downstream_work_item_id="workitem-build",
        )
        work_packet = WorkPacket(
            id="packet-research",
            actor_id="actor-athena",
            project_id="project-demo",
            workstream_id="workstream-research",
            work_item_id="workitem-research",
            assigned_actor_id="actor-atlas",
            task="Create research artifact.",
            risk_level=RiskLevel.LOW,
            definition_of_done=["artifact created"],
        )
        version = ArtifactVersion(
            id="artifact-version-1",
            actor_id="actor-atlas",
            artifact_id="artifact-demo",
            content_hash="sha256:abc",
            version_number=1,
        )
        approval_request = ApprovalRequest(
            id="approval-request-1",
            actor_id="actor-operator",
            requested_action="release artifact",
            resource_id="artifact-demo",
            required_approver_id="human-kojie",
            reason="External release requires human approval.",
        )
        approval_decision = ApprovalDecision(
            id="approval-decision-1",
            actor_id="human-kojie",
            approval_request_id=approval_request.id,
            approver_id="human-kojie",
            decision="approve",
            exact_action="release artifact",
            scope="artifact-demo",
        )

        self.assertEqual(being.runtime_actor_id, "actor-jaavis")
        self.assertEqual(dependency.upstream_work_item_id, "workitem-research")
        self.assertEqual(work_packet.assigned_actor_id, "actor-atlas")
        self.assertEqual(version.version_number, 1)
        self.assertEqual(approval_decision.approval_request_id, approval_request.id)

        registry = Registry(
            beings=[being],
            dependencies=[dependency],
            work_packets=[work_packet],
            artifact_versions=[version],
            approval_requests=[approval_request],
            approval_decisions=[approval_decision],
        )
        self.assertEqual(registry.beings[0].id, "being-jaavis")

    def test_schema_catalog_exports_json_schema_for_priority2_contracts(self):
        catalog = schema_catalog()

        self.assertIn("Request", catalog)
        self.assertIn("Being", catalog)
        self.assertIn("WorkPacket", catalog)
        self.assertIn("ApprovalDecision", catalog)
        self.assertEqual(catalog["Request"]["type"], "object")


if __name__ == "__main__":
    unittest.main()
