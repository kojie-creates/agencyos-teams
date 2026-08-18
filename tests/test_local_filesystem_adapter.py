import tempfile
import unittest
from pathlib import Path

from tools.enforcement_kernel import EnforcementKernel, KernelRequest, TransitionError


class LocalFilesystemAdapterTests(unittest.TestCase):
    def test_adapter_writes_artifact_inside_runtime_artifact_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kernel = EnforcementKernel(root)
            run = kernel.start(
                KernelRequest(
                    request_id="req-local-adapter",
                    title="Local adapter",
                    actor_id="actor-operator",
                    requested_outcome="Write a local artifact.",
                    action_class="internal_artifact",
                    reversible=True,
                    external=False,
                    sensitive=False,
                    required_workstreams=["research"],
                )
            )
            kernel.dispatch_ready(run.run_id)

            completed = kernel.complete_artifact(
                run.run_id,
                "research",
                "notes/research.md",
                "Research output",
                actor_id="actor-research",
            )

            artifact_path = root / completed.artifacts[-1].path
            self.assertEqual(artifact_path.read_text(encoding="utf-8"), "Research output")
            self.assertTrue(artifact_path.is_relative_to(root / ".agencyos-runtime" / "artifacts" / run.run_id))

    def test_adapter_works_with_relative_root_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            original = Path.cwd()
            try:
                root = Path(tmp)
                import os
                os.chdir(root)
                kernel = EnforcementKernel(Path("."))
                run = kernel.start(
                    KernelRequest(
                        request_id="req-local-adapter-relative",
                        title="Local adapter relative",
                        actor_id="actor-operator",
                        requested_outcome="Write a local artifact from a relative root.",
                        action_class="internal_artifact",
                        reversible=True,
                        external=False,
                        sensitive=False,
                        required_workstreams=["research"],
                    )
                )
                kernel.dispatch_ready(run.run_id)

                completed = kernel.complete_artifact(
                    run.run_id,
                    "research",
                    "notes/research.md",
                    "Relative root output",
                    actor_id="actor-research",
                )

                artifact_path = root / completed.artifacts[-1].path
                self.assertEqual(artifact_path.read_text(encoding="utf-8"), "Relative root output")
            finally:
                os.chdir(original)

    def test_adapter_blocks_path_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kernel = EnforcementKernel(root)
            run = kernel.start(
                KernelRequest(
                    request_id="req-local-adapter-block",
                    title="Local adapter block",
                    actor_id="actor-operator",
                    requested_outcome="Block unsafe local artifact path.",
                    action_class="internal_artifact",
                    reversible=True,
                    external=False,
                    sensitive=False,
                    required_workstreams=["research"],
                )
            )
            kernel.dispatch_ready(run.run_id)

            with self.assertRaisesRegex(TransitionError, "outside runtime artifact root"):
                kernel.complete_artifact(
                    run.run_id,
                    "research",
                    "../escape.md",
                    "Escaped output",
                    actor_id="actor-research",
                )


if __name__ == "__main__":
    unittest.main()
