---
種別: 実装報告書（Issue）
ID: "iss-00276"
タイトル: "Epic Quality Gate Manual Tests And PR Delivery"
関連GitHub: ["#276"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00270", "init-local-00003"]
---

# iss-00276 Epic品質gate、手動テスト、PR delivery — レポート

## 進捗サマリー
- `iss-00276` を start 済みで、active Issue はこの final quality / PR delivery Issue である。
- `assurance classify --stage requirement` と `assurance compose --artifact all` を実行し、`.assurance.json`、正規 `design.md`、正規 `plan.md`、`report.md` を配置した。
- Runtime は `authorized_profile=standard` を返したが、Issue requirement / Epic plan は `critical` を明示しているため、critical-grade の specialist / reviewer / PR observation obligations を上乗せして扱う。
- Pre-start draft artifacts と specialist draft artifacts を採用判断し、正規 `design.md` / `plan.md` に統合した。
- Planning fresh `spec-reviewer` は re-review で pass。P2 として Epic report の stale handoff state が指摘されたため、current handoff state へ更新した。
- S00/S02 の自動検証を実施し、初回 `tests/unit` で dogfooding mirror / checked-in snapshot の未追従が4件検出された。provider 側 `workflow_epic.md` を dogfooding mirror へ同期し、`epic-00270` / `iss-00271` から `iss-00276` の `.meta.json` と dependency snapshot を `tests/unit/infra/test_init_update.py` へ追記した。
- 修正後、targeted regression、`tests/unit`、`tests/cli_runtime`、full `uv run pytest`、`validate`、`assurance verify`、`deps check iss-00276` は成功した。manual dogfooding summary、fresh reviewer gates、final local commit は実施済み。PR作成 / observation は未実施である。

## 仕様解釈・判断台帳
| ID | 状態 | 種別 | 判断 / 解釈 | 根拠 | 処置 | フォローアップ |
|---|---|---|---|---|---|---|
| D-276-001 | resolved | scope | この Issue だけが Epic final quality gate と PR readiness / PR creation を扱う。 | Epic plan, Issue requirement | adopted | `plan.md` S07 で PR 作成 / observation を扱う。 |
| D-276-002 | resolved | grade | Runtime `authorized_profile=standard` は compose template authority に限定し、Issue requirement の `critical` に基づき critical-grade evidence obligations を維持する。 | `requirement.md`, Epic plan Slice 06 | adopted | specialist drafts、fresh reviewers、PR observation を必須 gate として扱う。 |
| D-276-003 | resolved | delivery | 1PR delivery を維持する。破綻する場合は PR split 前に Epic plan amendment と fresh review に戻る。 | Epic `D-007`, `I276-AC-007` | adopted | S00 / S07 で feasibility を確認する。 |
| D-276-004 | resolved | evidence | 前段 report に古い「Issue完了未実施」文言が残っていても、current lifecycle state、dependency readiness、commit chain、後続 Issue start 実績を current evidence として優先する。 | `deps check iss-00276` ready, active start success, recent commits | adopted | S00 audit で古い文言と current state を分けて記録する。 |
| D-276-005 | resolved | boundary | Manual dogfooding は summary-only evidence とし、raw workspaces / logs / captures / temp artifacts は commit しない。 | `I276-AC-003`, `I276-EC-004` | adopted | S03 / S06 で hygiene を確認する。 |

## 証跡採用台帳（Evidence Adoption Ledger）
| ID | 採用状態 | 出所 | 対象 | 判断理由 | 証跡 | 次アクション |
|---|---|---|---|---|---|---|
| EAL-276-001 | adopted | `epic-00270` canonical docs | `requirement.md`, `design.md`, `plan.md` | Slice 06 の final quality / PR delivery 要件、one-PR delivery、日本語ファースト、draft boundary を採用した。 | `epic-00270/requirement.md`, `epic-00270/design.md`, `epic-00270/plan.md` | S00-S07 で閉じる。 |
| EAL-276-002 | partially_adopted | pre-start draft-design | `design.md` | final integrator、manual summary、reviewer gates、PR boundary の方針を採用した。`artifact_state: draft-before-issue-start` や正本自己主張は採用していない。 | `artifacts/20260702t081010z-draft-design-epic-quality-pr-delivery-pre-start-seed.md` | S01 planning review 対象にする。 |
| EAL-276-003 | partially_adopted | pre-start draft-plan | `plan.md` | S00-S05 の大枠、automated / manual / reviewer / PR readiness の順序を採用した。未実行 command claim は採用していない。 | `artifacts/20260702t081011z-draft-plan-epic-quality-pr-delivery-pre-start-seed.md` | S01 planning review 対象にする。 |
| EAL-276-004 | adopted | `system-architect` draft | `design.md` | `D276-001..012`、critical-grade evidence override、AC/EC trace、PR boundary、manual hygiene、reviewer gate を採用した。draft の authority / pass claim は採用していない。 | Sagan `019f22ca-4f69-71d0-8547-00eaf479e2aa`; `artifacts/20260702t122432z-draft-design-system-architect-final-quality-gate-design.md` | fresh `spec-reviewer` で正本統合を確認する。 |
| EAL-276-005 | adopted | `implementation-planner` draft | `plan.md` | S00-S07、closure mapping、automated / manual / reviewer / PR delivery gate、stop conditions を採用した。未実行 command / reviewer pass claim は採用していない。 | Carver `019f22ca-505c-72d3-a62d-e04a3b309d3f`; `artifacts/20260702t122432z-01-draft-plan-implementation-planner-final-quality-gate-plan.md` | fresh `spec-reviewer` で正本統合を確認する。 |
| EAL-276-006 | adopted | assurance commands | `.assurance.json`, `design.md`, `plan.md`, `report.md` | `assurance classify` / `assurance compose` により正本テンプレートを配置した後、main orchestrator が critical final gate として正本を再記述した。 | `assurance classify --stage requirement`, `assurance compose --artifact all` | `assurance verify` と fresh planning review を実行する。 |
| EAL-276-007 | adopted | local assurance verification | `.assurance.json`, `design.md`, `plan.md` | 正本 `design.md` / `plan.md` 再記述後に `assurance classify` を再実行し、現在 hash に対する `assurance verify` が成功した。 | `assurance classify --stage requirement` -> pass; `assurance verify` -> pass; `validate` -> pass (`nodes=178`) | reviewer finding を修正し、fresh re-review を行う。 |
| EAL-276-008 | adopted | fresh `spec-reviewer` initial finding | `report.md` | Sartre は正規 design / plan が substantive で critical intent を維持している一方、Step Evidence の `C276-004` closure が draft-only evidence を reviewer pass のように扱っていると指摘した。 | Sartre `019f22d4-fc6a-77b1-a2f0-1441a2cc226e`; `review_status: fail`; P1 `C276-004` draft-only evidence closure | Step Evidence と検証記録を修正し、fresh re-review する。 |
| EAL-276-009 | adopted | fresh `spec-reviewer` re-review | `requirement.md`, `design.md`, `plan.md`, `report.md` | Socrates は前回P1が解消され、draft-only evidence が reviewer pass として扱われていないこと、S01 verification evidence が report / EAL / Step Evidence に保存されていること、critical intent が維持されていることを確認した。P2 として Epic report stale handoff state が残った。 | Socrates `019f22d8-1185-7250-92b9-1d2c4787f600`; `review_status: pass`; `overall_confidence_score: 0.88` | Epic report stale handoff state を更新し、executionへ進む。 |
| EAL-276-010 | adopted | final automated validation | `spec-dock/docs/workflow_epic.md`, `tests/unit/infra/test_init_update.py` | Final gate の初回 `tests/unit` は、今回追加された dogfooding Epic / Issue metadata と provider-side `workflow_epic.md` 更新が checked-in dogfooding mirror / snapshot に未反映であることを検出した。これは実装本体の設計退行ではなく、dogfooding snapshot を current source に追従させる final-gate 修正として採用した。 | 初回 `tests/unit` -> 4 failed / 962 passed; targeted regression -> 4 passed; rerun `tests/unit` -> 966 passed; `tests/cli_runtime` -> 730 passed, 74 skipped; `validate` -> nodes=178; `assurance verify` -> ok; `deps check iss-00276` -> ready | fresh reviewer gates と PR delivery へ進む。 |

## 仕様 authoring ゲート（Spec Authoring Gate）
| フェーズ | 調査証跡 | 未確定事項 / 回答 | 採用判断 | レビュアー判定 | ブロック有無 | 昇格 / 次アクション |
|---|---|---|---|---|---|---|
| requirement | Epic docs、Issue requirement、pre-start artifacts、accepted ADRs | blocking open question はない。 | `requirement.md` を正本として採用 | pass | no | execute approved plan |
| design | system-architect draft、pre-start design seed、Epic design / plan、前段 reports | runtime standard と Issue critical の差分は `D-276-002` で解決。 | `design.md` に採用 | pass | no | execute approved plan |
| plan | implementation-planner draft、Issue design、Epic plan、PR workflow boundary | PR merge / Issue close は対象外として解決。 | `plan.md` に採用 | pass | no | execute approved plan |

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）
| ロール | 範囲 | ドラフトパス | 参照元 | 予定反映先 | 採用状態 | 反映先 | 差分ガード結果 | 統合結果 | 採用しなかった部分 | ブロッカー | レビュー結果 | 昇格判断 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| system-architect | iss-00276 | `artifacts/20260702t122432z-draft-design-system-architect-final-quality-gate-design.md` | active issue docs、pre-start draft artifacts、active epic docs、前段 Issue reports、git status / recent commits | `design.md` | partially_integrated | `design.md` | pass: artifact-only edit; `validate` pass; canonical docs not edited by delegate | `D276-001..011`、critical-grade evidence override、AC/EC trace、PR boundary、manual hygiene、reviewer gate を統合 | final authority claims、reviewer pass claims、template `standard` obligation downgrading | none | pass | execute approved plan |
| implementation-planner | iss-00276 | `artifacts/20260702t122432z-01-draft-plan-implementation-planner-final-quality-gate-plan.md` | active issue docs、pre-start draft artifacts、active epic docs、前段 Issue reports、workflow docs | `plan.md` | partially_integrated | `plan.md` | pass: artifact-only edit; `validate` pass; canonical docs not edited by delegate | S00-S07、closure mapping、automated / manual / reviewer / PR delivery gate、stop conditions を統合 | 未実行 command / reviewer pass claims、canonical edit claims | none | pass | execute approved plan |

## Grade Specialist Evidence Gate
| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |
|---|---|---|---|---|---|
| standard | system-architect / implementation-planner or explicit skip reason | used | `artifacts/20260702t122432z-draft-design-system-architect-final-quality-gate-design.md`; `artifacts/20260702t122432z-01-draft-plan-implementation-planner-final-quality-gate-plan.md` | pass | ready |
| critical | system-architect / implementation-planner + extra reviewer gates | used | Same specialist drafts; final plan requires `spec-reviewer`, `qa-reviewer`, conditional `code-reviewer`, PR observation | pass | ready |

## Reviewer Gate Status
| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | Socrates re-review passed after Sartre P1 report evidence repair. |
| final-automated | automated quality gate | local command verification | fresh | pass | no | proceed to manual / reviewer gates | Initial unit failures were repaired by syncing the dogfooding mirror and checked-in metadata/dependency snapshots. |

## Issue-local draft artifact path index
| 種別 | パス | 状態 | authority |
|---|---|---|---|
| pre-start draft-design | `artifacts/20260702t081010z-draft-design-epic-quality-pr-delivery-pre-start-seed.md` | partially_adopted | evidence-only |
| pre-start draft-plan | `artifacts/20260702t081011z-draft-plan-epic-quality-pr-delivery-pre-start-seed.md` | partially_adopted | evidence-only |
| specialist draft-design | `artifacts/20260702t122432z-draft-design-system-architect-final-quality-gate-design.md` | adopted | evidence-only |
| specialist draft-plan | `artifacts/20260702t122432z-01-draft-plan-implementation-planner-final-quality-gate-plan.md` | adopted | evidence-only |

## 実装記録
- S00/S02:
  - `tests/unit` 初回実行で、dogfooding mirror / checked-in snapshot の追従漏れにより4件失敗した。
  - `src/spec_dock/assets/spec_dock/docs/workflow_epic.md` を `spec-dock/docs/workflow_epic.md` に同期した。
  - `tests/unit/infra/test_init_update.py` の checked-in dogfooding metadata path snapshot、metadata dependency snapshot、non-empty dependency map に `epic-00270` と `iss-00271` から `iss-00276` を追加した。
  - targeted regression と `tests/unit` 再実行は成功した。
- S03-S07:
  - manual dogfooding summary は実施済み。fresh `code-reviewer` は pass 済み。`spec-reviewer` / `qa-reviewer` は初回P1を検出したが、closure ID 修正、full pytest 追加、scaffold dogfooding 追加後の re-review で pass となった。
  - final local commit は実施済み。この commit 自体を S06 の approved local diff 証跡とする。
  - PR作成 / observation は未実施。

## 検証
- 実施済み:
  - `./spec-dock/scripts/spec-dock assurance classify --stage requirement` -> pass。`authorized_profile=standard`。
  - `./spec-dock/scripts/spec-dock assurance compose --artifact all` -> pass。`.assurance.json`, `design.md`, `plan.md`, `report.md` を配置。
  - 正本 `design.md` / `plan.md` 再記述後の `./spec-dock/scripts/spec-dock assurance classify --stage requirement` -> pass。
  - 正本 `design.md` / `plan.md` 再記述後の `./spec-dock/scripts/spec-dock assurance verify` -> pass。
  - `./spec-dock/scripts/spec-dock validate` -> pass (`nodes=178`)。
  - `git diff --check` -> pass。
  - `implementation-planner` draft 作成時の `./spec-dock/scripts/spec-dock validate` -> pass (`nodes=178`)。
  - Planning fresh `spec-reviewer` initial review -> fail。P1: draft-only evidence で `C276-004` を閉じていた Step Evidence を修正対象とした。
  - Planning fresh `spec-reviewer` re-review -> pass。P2: Epic report stale handoff state。
  - `env UV_CACHE_DIR=/private/tmp/uv-cache-spec-dock uv run pytest tests/cli_runtime` -> pass。`730 passed, 74 skipped`。
  - 初回 `env UV_CACHE_DIR=/private/tmp/uv-cache-spec-dock uv run pytest tests/unit` -> fail。4 failures: provider / dogfooding mirror の `workflow_epic.md` mismatch、checked-in dogfooding `.meta.json` path snapshot の `epic-00270` 未追従、checked-in dependency snapshot の `iss-00272` から `iss-00276` 未追従。
  - 修正後 `env UV_CACHE_DIR=/private/tmp/uv-cache-spec-dock uv run pytest tests/unit/infra/test_init_update.py -k 'checked_in_dogfooding_mirror_docs_match_provider_assets or checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json or checked_in_dogfooding_runtime_subprocess_validate_and_sync_on_cutover_snapshot or issue_211_epic_execution_route_content_regression_contract'` -> pass。`4 passed, 540 deselected`。
  - 修正後 `env UV_CACHE_DIR=/private/tmp/uv-cache-spec-dock uv run pytest tests/unit` -> pass。`966 passed`。
  - 修正後 `./spec-dock/scripts/spec-dock validate` -> pass (`nodes=178`)。
  - 修正後 `./spec-dock/scripts/spec-dock assurance verify` -> pass。
  - 修正後 `./spec-dock/scripts/spec-dock deps check iss-00276` -> pass。`ready=true`, `blockers=0`。
  - `env UV_CACHE_DIR=/private/tmp/uv-cache-spec-dock uv run pytest` -> pass。`1699 passed, 74 skipped`。
  - S03 manual hygiene: `git diff --name-status` -> changed files are `spec-dock/docs/workflow_epic.md`, `iss-00276/report.md`, `epic-00270/report.md`, `tests/unit/infra/test_init_update.py` only.
  - S03 manual hygiene: `git diff --check` -> pass。
  - S03 manual hygiene: `git status --short` -> tracked changes only; no raw manual workspace / temporary log / capture files staged or tracked.
  - S03 manual read-through: targeted `rg` confirmed changed workflow / active docs preserve `handoff-ready` / `execution-ready` boundary, Japanese-first wording, and raw artifact / canonical authority boundary. Large matches under historical artifacts are expected evidence-only records.
  - S03 scaffold dogfooding: `/private/tmp/spec-dock-epic00270-final-smoke-20260703a` に対して `uvx --from . spec-dock init ...` を実行し、scaffold 生成は成功した。
  - S03 scaffold dogfooding: generated `spec-dock/docs` と provider `src/spec_dock/assets/spec_dock/docs` の `diff -qr` は差分なし。generated `spec-dock/templates` と provider `src/spec_dock/assets/spec_dock/templates` の `diff -qr` も差分なし。
  - S03 scaffold dogfooding: generated docs/templates の targeted `rg` で `handoff-ready` / `execution-ready`、`assurance compose` は canonical compose 専用、actor別 draft command 不採用、日本語ファースト guidance が生成物へ反映されていることを確認した。
  - S03 scaffold dogfooding: empty scaffold の `./spec-dock/scripts/spec-dock validate` は `No nodes found` を返した。これは initiative / epic / issue 未作成の新規 scaffold として expected limitation と扱う。
  - S03 scaffold dogfooding: generated runtime は `new initiative`, `new epic`, `new issue`, `new artifact` を認識した。`new initiative` は GitHub-backed identity 前提で origin / GitHub issue creation を要求するため、fake remote では `Could not resolve to a Repository` で停止した。外部 GitHub mutation は行っていない。
  - Fresh `code-reviewer` Harvey (`019f236e-2728-72e2-adf5-8848a086037f`) -> pass。provider / dogfooding `workflow_epic.md` mirror、metadata / dependency snapshot additions、report updates に correctness-blocking finding なし。
  - Fresh `spec-reviewer` Planck (`019f236e-265c-78e2-b7c4-aa9551622f4a`) -> fail。P1: automated evidence が manual / reviewer / PR closure IDs (`C276-003`, `C276-005`, `C276-006`, `C276-008`) まで閉じたように読める。
  - Fresh `qa-reviewer` Ramanujan (`019f236e-27e4-7602-a80b-647843af6ca2`) -> fail。P1: automated evidence の closure ID 過剰主張、PR observation 未実施。P2: full `uv run pytest` / skip rationale 不足。
  - Reviewer repair: `final-automated-*` Step Evidence の Closure を `C276-001`, `C276-002`, `C276-013`, `C276-014` に限定し、manual / reviewer / PR closure は S03 / S04 / S07 に残した。
  - Reviewer repair: full `uv run pytest` を追加実行して pass したため、P2 broad automated gate は解消済み。
  - Reviewer repair: S03 scaffold dogfooding evidence を追加し、`C276-003` の manual / scaffold gap を解消した。
  - Fresh `spec-reviewer` Planck re-review -> pass。P2: Epic E-AC-006 の manual status wording を現状に合わせること。
  - Fresh `qa-reviewer` Ramanujan re-review -> pass。P2: Epic E-AC-006 の manual status wording を現状に合わせること。
  - Reviewer repair: Epic E-AC-006 を、manual scaffold dogfooding / hygiene read-through は実施済み、reviewer gates final re-review と PR delivery は未実施、という文面へ更新した。
- 未実施:
  - PR creation / observation は未実施。

## 完了 / PR
- Issue完了: 未実施。
- PR作成: 未実施。この Issue の S07 で扱う。

<!-- spec-dock:managed-section begin id="report.step-evidence" -->
## Step Evidence
| Step | Closure | Verification | Result | Evidence | Next action |
|---|---|---|---|---|---|
| planning-compose | `C276-009`, `C276-010` | `assurance classify`, `assurance compose`, specialist drafts | pass | `.assurance.json`; Sagan and Carver draft artifacts | `assurance verify` and fresh `spec-reviewer` |
| planning-verify | `C276-009`, `C276-010` | current-source assurance verification | pass | `assurance classify` pass; `assurance verify` pass; `validate nodes=178`; `git diff --check` pass | fresh `spec-reviewer` re-review |
| planning-review-initial | `C276-004` | fresh `spec-reviewer` initial review | fail | Sartre `019f22d4-fc6a-77b1-a2f0-1441a2cc226e`; P1 draft-only closure evidence fixed in this report update | fresh re-review |
| planning-review-recheck | `C276-004` | fresh `spec-reviewer` re-review | pass | Socrates `019f22d8-1185-7250-92b9-1d2c4787f600`; `review_status: pass`; P2 Epic report stale handoff state | update Epic report and execute approved plan |
| final-automated-initial | `C276-001`, `C276-002`, `C276-013`, `C276-014` | `tests/unit`, `tests/cli_runtime`, `validate`, `assurance verify`, `deps check` | repair-needed | `tests/unit` initial run found dogfooding mirror / checked-in snapshot drift; `tests/cli_runtime` passed | sync mirror and snapshots, rerun focused and full unit checks |
| final-automated-recheck | `C276-001`, `C276-002`, `C276-013`, `C276-014` | targeted regression, `tests/unit`, `tests/cli_runtime`, `validate`, `assurance verify`, `deps check` | pass | targeted 4 tests passed; `tests/unit` 966 passed; `tests/cli_runtime` 730 passed, 74 skipped; `validate` nodes=178; `assurance verify` ok; `deps check iss-00276` ready | manual dogfooding summary and fresh reviewer gates |
| final-full-suite | `C276-002`, `C276-013` | full `uv run pytest` | pass | `1699 passed, 74 skipped` | reviewer re-check |
| manual-hygiene-readthrough | `C276-003`, `C276-008`, `C276-009`, `C276-010`, `C276-015` | `git diff --name-status`, `git diff --check`, `git status --short`, targeted `rg` read-through, temporary scaffold dogfooding | pass | changed files limited to workflow mirror, reports, and snapshot test; no raw manual files; readiness / Japanese-first / raw authority boundaries present; `spec-dock init` generated scaffold; generated docs/templates match provider assets; generated runtime exposes `new` subcommands; empty scaffold `validate` returns expected `No nodes found`; fake-remote `new initiative` stopped before external mutation | reviewer re-check |
| reviewer-gate-initial | `C276-004`, `C276-005`, `C276-013`, `C276-014` | fresh `spec-reviewer`, `qa-reviewer`, `code-reviewer` | repair-needed | Harvey code-review pass; Planck spec-review P1 closure ID overclaim; Ramanujan QA P1 closure ID overclaim and PR observation pending; QA P2 broad suite gap | re-review after closure ID repair and full pytest |
| reviewer-gate-recheck | `C276-004`, `C276-005`, `C276-013`, `C276-014` | fresh `spec-reviewer` and `qa-reviewer` re-review after repairs | pass | Planck re-review pass after closure ID repair; Ramanujan re-review pass after scaffold dogfooding evidence; Epic E-AC-006 stale manual wording repaired | final commit |
| final-local-commit | `C276-015` | staged diff review and local commit | pass | staged files were workflow mirror, active Epic / Issue reports, and checked-in dogfooding snapshot test; this commit is the S06 local commit evidence | PR delivery |
<!-- spec-dock:managed-section end id="report.step-evidence" -->
