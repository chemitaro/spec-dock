import hashlib
import json
from pathlib import Path
import re
import tempfile

from tests.cli_runtime.harness import CliRuntimeHarness, main


class TestArtifactImportChatGptOutput(CliRuntimeHarness):
    def _prepare_target(self, target: Path) -> Path:
        assert main(["init", str(target)]) == 0
        self._create_same_repo_linked_hierarchy(
            target,
            initiative_issue_number=301,
            epic_issue_number=312,
            issue_issue_number=317,
            initiative_title="Architecture",
            epic_title="Workbench",
            issue_title="Raw import",
        )
        issue_dirs = list((target / "spec-dock" / "initiatives").rglob("iss-00317-raw-import"))
        assert len(issue_dirs) == 1
        return issue_dirs[0]

    def test_binary_fixture_matrix_is_byte_preserving_and_content_free(self) -> None:
        fixtures = {
            "lf": b"line one\nline two\n",
            "crlf": b"line one\r\nline two\r\n",
            "bom": b"\xef\xbb\xbfheading\n",
            "no-final": b"no final newline",
            "japanese": "日本語の生出力\n".encode(),
            "nul": b"before\x00after\n",
            "invalid": b"before\xffafter\n",
            "empty": b"",
        }
        secret = "sk-secret-body-value"
        fixtures["secret"] = secret.encode()

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self._prepare_target(target)
            workbench = target / "spec-dock" / ".workbench"
            workbench.mkdir(parents=True, exist_ok=True)

            for slug, body in fixtures.items():
                source = workbench / f"{slug}.md"
                source.write_bytes(body)
                command = [
                    "artifact",
                    "import",
                    "chatgpt-output",
                    "--issue",
                    "317",
                    "--file",
                    source.relative_to(target).as_posix(),
                    "--title",
                    f"Raw {slug}",
                    "--slug",
                    slug,
                    "--json",
                ]
                completed = self._run_runtime_capture(target, command)
                assert completed.returncode == 0, completed.stdout + completed.stderr
                payload = json.loads(completed.stdout)
                destination = target / payload["destination"]

                assert payload["status"] == "ok"
                assert payload["import_kind"] == "chatgpt-output"
                assert payload["storage_identity"] == "blank"
                assert payload["scope_id"] == "iss-00317"
                assert payload["sha256"] == hashlib.sha256(body).hexdigest()
                assert payload["byte_count"] == len(body)
                assert payload["committed"] is True
                assert payload["source"] == source.relative_to(target).as_posix()
                assert re.fullmatch(
                    rf"[0-9]{{8}}t[0-9]{{6}}z(?:-[0-9]{{2}})?-chatgpt-output-{slug}\.md",
                    destination.name,
                )
                assert source.read_bytes() == body
                assert destination.read_bytes() == body
                combined = completed.stdout + completed.stderr
                assert secret not in combined
                assert str(target) not in combined
                for claim in ("canonical", "adopted", "reviewed"):
                    assert claim not in combined.lower()

    def test_text_success_and_json_failure_tokens_are_stable_and_content_free(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self._prepare_target(target)
            workbench = target / "spec-dock" / ".workbench"
            workbench.mkdir(parents=True, exist_ok=True)
            source = workbench / "text.md"
            source.write_bytes(b"opaque text path\n")

            success = self._run_runtime_capture(
                target,
                [
                    "artifact",
                    "import",
                    "chatgpt-output",
                    "--issue",
                    "317",
                    "--file",
                    str(source.resolve()),
                    "--title",
                    "Text result",
                ],
            )
            assert success.returncode == 0, success.stdout + success.stderr
            assert "spec-dock: ok (artifact import chatgpt-output)" in success.stdout
            assert "import_kind=chatgpt-output" in success.stdout
            assert "storage_identity=blank" in success.stdout
            assert "scope_id=iss-00317" in success.stdout
            assert "committed=true" in success.stdout
            assert "cleanup_state=removed" in success.stdout
            assert str(target) not in success.stdout + success.stderr

            outside = target / "outside.md"
            outside.write_text("OSError secret body", encoding="utf-8")
            failure = self._run_runtime_capture(
                target,
                [
                    "artifact",
                    "import",
                    "chatgpt-output",
                    "--issue",
                    "317",
                    "--file",
                    str(outside),
                    "--title",
                    "Rejected",
                    "--json",
                ],
            )
            assert failure.returncode == 1
            payload = json.loads(failure.stdout)
            assert payload == {
                "status": "error",
                "import_kind": "chatgpt-output",
                "storage_identity": "blank",
                "code": "source_ineligible",
                "committed": False,
                "cleanup_state": "not_created",
            }
            combined = failure.stdout + failure.stderr
            assert str(target) not in combined
            assert "OSError" not in combined
            assert "secret body" not in combined

    def test_existing_blank_chatgpt_output_slug_coexists_with_import(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            issue_dir = self._prepare_target(target)
            workbench = target / "spec-dock" / ".workbench"
            workbench.mkdir(parents=True, exist_ok=True)
            same_second_pair = None
            for attempt in range(5):
                slug = f"coexist-{attempt}"
                source = workbench / f"{slug}.md"
                source.write_bytes(b"raw\n")
                self._run_runtime(
                    target,
                    [
                        "new",
                        "artifact",
                        "blank",
                        "--issue",
                        "317",
                        "--title",
                        "Existing blank",
                        "--slug",
                        f"chatgpt-output-{slug}",
                    ],
                )
                imported = self._run_runtime_capture(
                    target,
                    [
                        "artifact",
                        "import",
                        "chatgpt-output",
                        "--issue",
                        "317",
                        "--file",
                        source.relative_to(target).as_posix(),
                        "--title",
                        "Imported blank",
                        "--slug",
                        slug,
                        "--json",
                    ],
                )
                assert imported.returncode == 0, imported.stdout + imported.stderr
                artifacts = sorted((issue_dir / "artifacts").glob(f"*-chatgpt-output-{slug}.md"))
                assert len(artifacts) == 2
                timestamps = [re.match(r"([0-9]{8}t[0-9]{6}z)", path.name).group(1) for path in artifacts]
                if len(set(timestamps)) == 1:
                    same_second_pair = artifacts
                    break

            assert same_second_pair is not None
            assert len({path.name for path in same_second_pair}) == 2
            assert any(re.match(r"[0-9]{8}t[0-9]{6}z-[0-9]{2}-", path.name) for path in same_second_pair)
