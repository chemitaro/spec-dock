---
種別: 設計書（Issue）
ID: "iss-00266"
タイトル: "Delegated authoring artifacts boundary"
Issue Grade: "standard"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Plan: ["plan.md"]
関連Report: ["report.md"]
親: ["epic-00259", "init-local-00003"]
---

# iss-00266 Delegated authoring artifacts boundary — 設計

## 目的と判断
system-architect / implementation-planner / delegated authoring の future output boundary を、scope-local `discussions/` から `artifacts/` direct child へ切り替える。delegated draft は canonical docs を直接変更せず、`artifacts/` に 1 件だけ flat Markdown を作成し、main orchestrator が report ledger を通じて採否を記録してから requirement / design / plan / report へ反映する。

この Issue は diff guard、provenance validation、report evidence guidance の境界変更に限定する。general `new artifact` command、legacy `discussions/` evidence の移動、docs/skills 全面改訂は扱わない。legacy `discussions/` は historical evidence として残せるが、future delegated output としては compliant output に数えない。

## 現行構造
- Runtime diff guard:
  - `domain/delegated_authoring.py` は `scope_dir / "discussions"` を target とし、exactly one new discussion draft を許可する。
  - discussion filename validation は `domain/discussion_docs.py` の timestamp discussion parser に依存している。
  - required provenance fields、supported roles、self-claim rejection、forbidden side-effect rejection は domain layer にある。
- Application baseline guard:
  - `application/delegated_authoring.py` は repo 外 baseline status、HEAD mismatch、baseline-only side effects、ignored forbidden roots を検査する。
  - baseline dirty check は `dirty_baseline_discussion` として discussion subtree を特別扱いしている。
  - `--allow-existing-discussion` は existing discussion allowance として application request に渡される。
- CLI / manifest:
  - `commands/delegated_authoring.py` は `diff-guard --role --scope --baseline-status` を提供する。
  - manifest generation は既に deprecated result を返す。
- Artifact domain:
  - `domain/artifacts.py` は `parse_artifact_filename()`、`is_direct_artifact_type()`、`scan_artifact_duplicate_state()` を持ち、future artifact filename grammar の source of truth になっている。
- Report guidance:
  - active report scaffold は `artifacts/` への delegated draft evidence を表現できる。
  - provider-side report templates / workflow docs には旧 `discussions/` guidance が残るため、Issue 266 では report evidence guidance の最小整合だけを対象にする。

## 変更方針
- Target boundary を `scope_dir / "artifacts"` に変更する。
  - allowed mutation は exactly one new direct-child Markdown artifact のみ。
  - nested path、non-Markdown、symlink artifact、`rules.md` output、existing update、delete、rename/copy、mixed staged/unstaged、unmerged、out-of-scope、canonical docs、forbidden root side effects は fail-closed にする。
  - `artifacts/` 自体が symlink / non-directory / unreadable の場合も fail にする。
- Filename validation は `discussion_docs.py` ではなく `artifacts.py::parse_artifact_filename()` を使う。
  - typed artifact と blank artifact の grammar を受ける。
  - `rules.md` は artifacts guidance file として存在可能だが、delegated output としては count しない。
  - artifact duplicate / malformed checks は既存 artifact domain contract と矛盾しないように扱う。
- Provenance validation は field 名と意味を維持し、artifact 用語へ diagnostics を寄せる。
  - required fields: `created_by_role`, `scope_id`, `source_paths`, `intended_targets`, `adoption_status`, `reflected_to`, `diff_guard_result`。
  - supported roles: `system-architect`, `implementation-planner`。
  - `created_by_role` と CLI role、`scope_id` と CLI scope は一致必須。
  - `source_paths` / `intended_targets` は non-empty list 必須。
  - `adoption_status: unreviewed` と `reflected_to: []` 以外の self-claim は拒否する。
- Legacy `discussions/` は historical-only とする。
  - pre-existing legacy discussions は移動・rename・削除しない。
  - future run が `scope_dir / "discussions"` に新規/変更 output を作った場合は `future_noncompliant_discussion_output` または同等の artifact-target diagnostics で fail する。
  - `--allow-existing-discussion` は互換のため parse してもよいが、artifact boundary の許可拡張には使わない。指定があっても existing update や discussion output を compliant にしてはならない。
- Report guidance は最小更新に絞る。
  - Evidence Adoption Ledger / Delegated Draft Evidence の標準出力先を `artifacts/` direct child にする。
  - legacy `discussions/` は historical evidence と明記した場合だけ source として記録できる。
  - workflow docs / skills の全面更新は `iss-00267` へ defer する。ただし Issue 266 で更新しない残存旧記述は report に non-blocking known stale guidance として記録する。

## 設計契約
| ID | 契約 | 対応 AC | 実装面 | 検証 |
|---|---|---|---|---|
| DES-266-001 | allowed mutation は target scope の `artifacts/` direct child Markdown 新規作成 1 件のみ | AC-266-001 | domain diff guard path classifier | positive diff-guard test |
| DES-266-002 | zero / multiple allowed artifacts は fail し、allowed count を diagnostics に出す | AC-266-001 | artifact count aggregation | zero/multiple negative tests |
| DES-266-003 | artifact filename は `parse_artifact_filename()` を source of truth にし、`rules.md` / malformed / non-md は output として拒否する | AC-266-001, AC-266-002 | artifact filename classifier | filename negative tests |
| DES-266-004 | symlinked `artifacts/`、artifact symlink、nested path、existing update、delete、rename/copy、mixed staged/unstaged、unmerged は fail-closed | AC-266-002 | domain diff guard status classifier | negative side-effect tests |
| DES-266-005 | canonical docs / provider source / tests / `.agents` / `.codex` / `.github` / `.env*` / forbidden roots への side effect は fail-closed | AC-266-002 | application + domain side-effect guard | forbidden root tests |
| DES-266-006 | required provenance fields と role/scope/list/self-claim validation は artifacts draft に対して維持する | AC-266-003 | metadata validator | missing/mismatch/self-claim tests |
| DES-266-007 | future output to `discussions/` は compliant artifact output として採用不可にする | AC-266-004 | classifier special-case or outside-target diagnostics | discussion-output negative test |
| DES-266-008 | pre-existing legacy discussions は historical evidence として残し、Issue 266 で移動・rename・削除しない | AC-266-004 | no migration behavior | inspection / regression |
| DES-266-009 | baseline status は repo 外必須、HEAD mismatch は committed side effect として fail を維持する | AC-266-002 | application baseline guard | existing baseline tests |
| DES-266-010 | baseline dirty check は target artifact subtree に移し、legacy discussions の存在だけでは block しない | AC-266-002, AC-266-004 | application baseline helper | baseline dirty tests |
| DES-266-011 | `--allow-existing-discussion` は existing artifact/discussion update を許可しない | AC-266-002, AC-266-004 | command/application compatibility handling | CLI compatibility negative test |
| DES-266-012 | report ledger guidance は artifact draft path、adoption/rejection、diff guard result を記録できる | AC-266-005 | report templates / active report guidance | docs inspection / template tests |

## Diagnostics 方針
- New artifact count failure:
  - 推奨 reason: `expected_exactly_one_new_artifact_draft`
  - detail: `allowed_new_artifact_count=<N>`
- Artifact boundary failures:
  - 推奨 reason/detail: `outside_target_artifacts`, `nested_artifact_output`, `artifact_name_noncompliant`, `artifact_symlink`, `artifacts_dir_symlink`, `existing_artifact_update_unsupported`
- Legacy discussion future output:
  - 推奨 reason/detail: `future_noncompliant_discussion_output`
  - 代替として `outside_target_artifacts` を使う場合も、detail で `legacy_discussion_output_unsupported=true` を明示する。
- Backward compatibility:
  - reason wording は artifact-first に寄せる。旧 discussion reason に依存するテストは Issue 266 で更新する。
  - manifest deprecated reason は既存互換のため維持してよい。delegated draft manifest の再設計は scope 外。

## 対象ファイル境界
- Runtime:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/delegated_authoring.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/delegated_authoring.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/delegated_authoring.py`
- Tests:
  - `tests/unit/domain/test_delegated_authoring.py`
  - `tests/cli_runtime/test_delegated_authoring.py`
  - focused assertions in `tests/unit/infra/test_init_update.py` if report template scaffolding changes require it.
- Provider-side report guidance:
  - `src/spec_dock/assets/spec_dock/templates/{initiative,epic,issue}/report.md`
  - `src/spec_dock/assets/spec_dock/system/active-none/{initiative,epic,issue}/report.md`
  - Narrow delegated draft evidence sections in workflow docs only if required to keep report guidance internally consistent.

## 非対象 / defer
- `new artifact` command の一般作成実装。
- legacy `discussions/` evidence の migration。
- `.codex/agents` / `.agents/skills` の全面更新。
- workflow docs / skills の全面改訂。これは `iss-00267` に引き渡す。
- Epic PR 作成。全 Issue 完了後の Epic gate で扱う。

## テスト戦略
- Domain tests:
  - exactly one direct-child artifact pass。
  - zero / multiple artifacts fail。
  - discussions output fail。
  - nested, non-md, malformed, symlink, existing update, delete, rename/copy, mixed, unmerged fail。
  - provenance missing / role mismatch / scope mismatch / self-claim fail。
- CLI runtime tests:
  - baseline status repo outside requirement。
  - forbidden side effects and ignored guarded paths。
  - `--allow-existing-discussion` does not widen artifact boundary。
- Template / docs inspection:
  - report templates use `artifact draft path` / `artifacts/` as future delegated draft destination。
  - legacy `discussions/` wording is historical-only or deferred to `iss-00267`。

## 後続 Issue への引き渡し
- `iss-00267` updates docs/skills broadly to this artifact boundary and removes stale `new doc` / future `discussions/` authoring guidance。
- `iss-00268` can run integrated smoke only after this diff guard behavior exists。
