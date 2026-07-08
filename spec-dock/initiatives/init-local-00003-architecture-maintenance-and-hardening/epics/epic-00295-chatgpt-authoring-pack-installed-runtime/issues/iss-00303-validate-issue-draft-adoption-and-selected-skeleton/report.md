---
種別: 実装報告書（Issue）
ID: "iss-00303"
タイトル: "Issue Draft Adoption Validation"
関連GitHub: ["#303"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00295", "init-local-00003"]
---

# iss-00303 Issue Draft Adoption Validation — 実装報告

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger / 必須）

| 識別子（ID） | 状態（Status） | 種別（Type） | 起票元（Raised By） | 契機 / 差分（Gap） | 検討した選択肢 | 判断 / 解釈 | 根拠（Rationale） | 処置（Disposition） | 証跡（Evidence） | フォローアップ（Follow-up） |
|---|---|---|---|---|---|---|---|---|---|---|
| D-001 | resolved | scope | orchestrator | Issue 作成前 candidate validation と Issue 作成後 draft adoption validation が混同されるリスク | A: `validate epic-issue-candidates` に adoption validation を寄せる; B: post-node validator を独立させる | B を採用 | `iss-00302` は pre-node candidate evidence、`iss-00303` は existing Issue node に対する draft adoption input integrity を扱う | promoted_to_design | `design.md` section 1 and 6 | none |
| D-002 | resolved | implementation | ChatGPT Use planning | selected skeleton fill validation が authorized profile decision と誤解されるリスク | A: `.assurance.json` を runtime が更新する; B: `.assurance.json` を observation-only として読む | B を採用 | Parent Epic は authoring runtime に `.assurance.json` mutation と authorized profile decision を許可しない | promoted_to_design | `requirement.md` BH-003/BH-004, `design.md` section 4.3 | none |
| D-003 | resolved | operation | ChatGPT Use planning | ChatGPT connector が current branch を開けず main fallback を検査した | A: GitHub connector evidence を branch-current として扱う; B: fallback observation と local attachment evidence を分ける | B を採用 | ChatGPT report は repository access succeeded だが current branch verification は不確実と明記した | applied | Oracle session `specdock-iss-00303-planning`; `report.md` Evidence Adoption Ledger | none |

## Evidence Adoption Ledger（証跡採用台帳 / 必須）

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | Issue-local draft requirement | `requirement.md` | Purpose / scope / non-scope / acceptance criteria を採用し、authority boundary と status taxonomy を補強した | `artifacts/20260707t171303z-draft-requirement-validate-issue-draft-adoption-and-selected-skeleton-draft-requirement.md` | spec-review |
| EAL-002 | adopted | Issue-local draft design | `design.md` | target paths、runtime boundary、selected skeleton validation、adoption boundary を採用し、post-node validator として再構成した | `artifacts/20260707t171304z-draft-design-validate-issue-draft-adoption-and-selected-skeleton-draft-design.md` | spec-review |
| EAL-003 | adopted | Issue-local draft plan | `plan.md` | Red/Green/Refactor sequence、test matrix、finish evidence、no-per-Issue-PR policy を採用した | `artifacts/20260707t171304z-01-draft-plan-validate-issue-draft-adoption-and-selected-skeleton-draft-plan.md` | spec-review |
| EAL-004 | adopted | ChatGPT Use / Oracle GPT-5.5 Pro Extended | `requirement.md`, `design.md`, `plan.md`, `report.md` | draft artifacts を evidence-only として再評価し、Issue 00303 の planning pack を具体化した | Oracle session `specdock-iss-00303-planning`; prompt retained as private scratch and not durable canonical evidence | spec-review |
| EAL-005 | rejected | ChatGPT Use / Oracle GPT-5.5 Pro Extended | branch evidence claim | ChatGPT connector は repository と GitHub Issue #303 を確認したが current branch を開けず `main` fallback を使ったため、current branch verified claim は採用しない | Oracle session `specdock-iss-00303-planning` | no_action |
| EAL-006 | adopted | Runtime implementation | provider and dogfood `authoring validate issue-draft-adoption` | Issue node exists 後の draft adoption payload、review report supplied bytes digest、draft pack digest、source hash、canonical target boundary、draft file hash/path safety を検証する installed runtime command を実装した | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/{application,domain,presentation}/authoring_pack/*draft_adoption*`; `commands/authoring.py`; dogfood mirror | final review |
| EAL-007 | adopted | Runtime implementation | provider and dogfood `authoring validate selected-skeleton-fill` | `.assurance.json` と selected skeleton を observation-only として読み、section inventory、section hash、profile drift、template hash / selected skeleton hash stale を検証する installed runtime command を実装した | `draft_adoption_contract.py`; `draft_adoption_validation.py`; `tests/cli_runtime/test_authoring.py` | final review |
| EAL-008 | adopted | Compatibility wrapper fix | `validate_issue_draft_adoption.py`, `validate_selected_skeleton_fill.py` | provider/dogfood wrappers を runtime CLI 委譲に統一し、legacy-only selected wrapper contract と dogfood missing helper failure を解消した | focused wrapper smoke and `--help` assertions | final review |
| EAL-009 | adopted | QA/code reviewer feedback | P1/P2 repair set | missing or unreadable prerequisite を status blocked として扱う修正、real source hash stale coverage、symlink report path rejection、selected skeleton negative matrix、draft/section/template/skeleton digest required/stale gate、documented authority claim names、merge-ready and PR-delivery claim rejection、`report_evidence` canonical target、EAL disposition requirement、canonical-doc path rejection、unexpected canonical target rejection、canonical target output evidence、provider/dogfood/installed wrapper parity proof を追加した | source/report focused tests `71 passed`; selected source hash focused tests `33 passed`; authoring focused tests `98 passed`; focused validator subset `60 passed`; full authoring suite `268 passed`; final code/QA reviewer pass | no_action |

## 目的整合台帳（Objective Alignment Ledger / 必須）

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | Existing Issue node に対する draft adoption / selected skeleton fill input integrity を検証する | CLI help、compatibility wrappers、dogfood mirror、report output は実装補助 | low | pending spec-review |

## Spec Authoring Gate（仕様 authoring ゲート / 必須）

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | Epic docs, active Issue drafts, `iss-00302` candidate validator design, ChatGPT Use planning output | current branch was not accessible to ChatGPT connector; local context used as supplementary evidence | adopted into `requirement.md` | pass | no | promote |
| design | `requirement.md`, existing authoring runtime layers, candidate validator contracts, draft design | review digest contract fixed after spec-review P1 | adopted into `design.md` | pass | no | promote |
| plan | `requirement.md`, `design.md`, draft plan, existing test style in `tests/cli_runtime/test_authoring.py` | executable step contract added after spec-review P1 | adopted into `plan.md` | pass | no | promote |

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）

| ロール（created_by_role） | 範囲（scope_id） | ドラフトパス（artifact draft path） | 参照元（source_paths） | 予定反映先（intended_targets） | 採用状態（adoption_status） | 反映先（reflected_to） | 差分ガード結果（diff_guard_result） | 統合結果 | 採用しなかった部分 | ブロッカー | レビュー結果（reviewer result） | 昇格判断（promotion decision） |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ChatGPT Use / Oracle GPT-5.5 Pro Extended | iss-00303 | `artifacts/20260707t171303z-draft-requirement-validate-issue-draft-adoption-and-selected-skeleton-draft-requirement.md`; `artifacts/20260707t171304z-draft-design-validate-issue-draft-adoption-and-selected-skeleton-draft-design.md`; `artifacts/20260707t171304z-01-draft-plan-validate-issue-draft-adoption-and-selected-skeleton-draft-plan.md` | active Epic docs; active Issue scaffold; Issue draft artifacts; `iss-00302` runtime files/tests; Oracle prompt and response | `requirement.md`, `design.md`, `plan.md`, `report.md` | adopted | `requirement.md`, `design.md`, `plan.md`, `report.md` | pass: `git diff --check`, `spec-dock validate`, and `assurance verify` were run after canonical rewrite | source drafts preserved; selected claims rewritten by main orchestrator into canonical docs | current branch verified claim from ChatGPT connector fallback | none | pass | promote |

## グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）

| グレード（Grade） | 必要な専門家 / 代替（required specialist / fallback） | 使用状況（usage） | 証跡（evidence） | 鮮度 spec-reviewer 判定（fresh spec-reviewer verdict） | 実行可否（execution readiness） |
|---|---|---|---|---|---|
| `standard` | manual fallback | used | manual fallback evidence: ChatGPT Use planning evidence in EAL-004 plus main-orchestrator adopted canonical docs | pass | ready |

## レビューゲート状態（Reviewer Gate Status）

| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| planning | spec authoring review | spec-reviewer | fresh | pass | no | promote | fresh re-review returned no findings and `review_status=pass` |
| implementation | code review | code-reviewer | fresh | pass | no | promote | final re-review returned no findings and `review_status=pass` |
| implementation | QA review | qa-reviewer | fresh | pass | no | promote | final re-review returned no P0/P1 findings and `review_status=pass`; P2 selected source hash sensitivity was also strengthened |

## 実装サマリー

- `authoring validate issue-draft-adoption` を installed runtime command として実装し、Issue node / supplied review report / draft payload / canonical target boundary / draft file integrity を evidence-only で検証できるようにした。
- `authoring validate selected-skeleton-fill` を installed runtime command として実装し、`.assurance.json` と selected skeleton を observation-only として参照しながら、section fills と profile / digest drift を検証できるようにした。
- provider-side source of truth と dogfood mirror を同期し、compatibility wrappers は runtime CLI 委譲に統一した。
- Per-Issue PR は作成せず、Epic relay workflow に従って PR delivery は `iss-00307` に委譲する。

## 実装記録（セッションログ）

### セッションログ（2026-07-08）

#### 対象

- Step: S00 Planning and draft adoption evidence
- Closure IDs: CLOS-011 partial

#### 実施内容

- `iss-00303` を start し、branch `iss-00303-validate-issue-draft-adoption-and-selected-skeleton` を push した。
- ChatGPT Use / Oracle GPT-5.5 Pro Extended に current branch、active Issue drafts、Epic docs、`iss-00302` runtime context、workflow docs を渡し、Issue planning pack を依頼した。
- ChatGPT Use resultを main orchestrator が検証し、canonical `requirement.md`, `design.md`, `plan.md`, `report.md` へ採用した。
- ChatGPT connector が current branch を開けなかったため、branch-current claim は EAL-005 で rejected とした。
- `assurance classify --stage requirement` により `authorized_profile=standard` を確認した。
- `assurance compose --artifact report` により Standard report scaffold を生成し、その後 planning evidence に置換した。

#### 実行コマンド / 結果

```bash
./spec-dock/scripts/spec-dock issue start iss-00303
# spec-dock: ok (issue start) target=iss-00303 initiative=init-local-00003 epic=epic-00295 issue=iss-00303
# spec-dock: ok (issue checkout) branch=iss-00303-validate-issue-draft-adoption-and-selected-skeleton

git push -u origin iss-00303-validate-issue-draft-adoption-and-selected-skeleton
# branch pushed and upstream set

chatgpt-use oracle wrapper --slug specdock-iss-00303-planning --file private prompt
# completed; model resolved=Pro Extended; ChatGPT reported repository access succeeded but current branch unavailable, default branch fallback used

./spec-dock/scripts/spec-dock assurance classify --stage requirement
# assurance classify: ok; authorized_profile=standard

./spec-dock/scripts/spec-dock assurance compose --artifact all
# failed safely with substantive_content_conflict because design.md and plan.md already contained main-orchestrator-authored substantive content

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=202

./spec-dock/scripts/spec-dock assurance verify
# assurance verify: ok

git diff --check
# ok
```

#### 実装内容

- Provider runtime:
  - `draft_adoption_contract.py` を追加し、draft adoption / selected skeleton fill の evidence-only result contract、status classification、path safety、secret/raw transcript scan、digest comparison を実装した。
  - `draft_adoption_validation.py` を追加し、review report gate、Issue node gate、assurance / selected skeleton observation、safe report output を実装した。
  - `draft_adoption_renderer.py` を追加し、JSON/text output を提供した。
  - `commands/authoring.py` と `cli/parser.py` を更新し、2 command を deferred skeleton から implemented contract に切り替えた。
- Dogfood mirror:
  - provider runtime changes を `spec-dock/scripts/spec_dock_runtime/...` に反映した。
  - `validate_issue_draft_adoption.py` と `validate_selected_skeleton_fill.py` を runtime CLI delegate wrapper として配置した。
- Tests:
  - help contract、positive path、review/source digest stale、missing Issue node blocked、documented authority claim rejection、merge-ready / PR-delivery claim rejection、canonical-doc path rejection、safe/unsafe/symlink report path rejection、selected skeleton missing/extra/duplicate/empty inventory、required/mismatched profile/digest/source drift、secret path rejection、wrapper smoke を追加した。
  - installed authoring-pack helper inventory test を新規 wrapper に合わせて更新した。
- Reviewer repair:
  - QA/code reviewer P1 を受け、selected wrapper を legacy helper から runtime delegate に変更した。
  - missing Issue node を `fail` ではなく `blocked` にした。
  - selected skeleton `template_hash` / `selected_skeleton_hash` mismatch を stale comparison として扱うようにした。
  - `issue-draft-adoption --review-report` を required にし、暗黙 discovery を廃止した。
  - approved schema に合わせ、入力 payload の authority claim keys を `canonical_adoption`, `canonical_written`, `assurance_mutation`, `authorized_profile_decision`, `reviewer_pass`, `execution_ready`, `pr_ready` として検証するようにした。
  - `merge_ready`, `pr_delivery`, `pr_delivered` が truthy な場合も forbidden authority claim として reject するようにした。
  - draft / section fill paths が canonical docs (`requirement.md`, `design.md`, `plan.md`, `report.md`, `.assurance.json`) を指す場合は `rejected` にし、`artifacts/` 配下の提案成果物だけを受け付けるようにした。
  - `draft_pack_digest`, selected skeleton `template_hash`, `selected_skeleton_hash` を必須 evidence とし、欠落時は `fail`、不一致時は `stale` として扱うようにした。
  - draft/section item の `sha256` 欠落を `fail` とし、`canonical_targets.report_evidence` と `eal_disposition_required` を approved schema として検証するようにした。
  - extra canonical target keys を `fail` とし、passing result に verified `canonical_targets` を含めるようにした。
  - QA final re-review P1/P2 を受け、`--expected-source-hash` stale comparison を issue draft adoption / selected skeleton fill の両方で CLI test coverage に追加した。
  - QA final re-review P2 を受け、両 validator の `--report-path` symlink rejection を command-level test coverage に追加した。
  - QA final pass 後の P2 を受け、selected skeleton fill fixture に実 `source_manifest_hash` を追加し、positive/stale の両方で observed source hash を assertion した。

#### 実行コマンド / 結果（implementation）

```bash
uv run pytest tests/cli_runtime/test_authoring.py -q -k "source_hash or report_path or issue_draft_adoption or selected_skeleton_fill"
# 71 passed, 194 deselected in 63.19s

uv run pytest tests/cli_runtime/test_authoring.py -q -k "selected_skeleton_fill_valid_payload_passes or selected_skeleton_fill_detects_source_hash_stale"
# 2 passed, 266 deselected in 1.84s

uv run pytest tests/cli_runtime/test_authoring.py -q -k "source_hash or selected_skeleton_fill"
# 33 passed, 235 deselected in 27.29s

uv run pytest tests/cli_runtime/test_authoring.py -q -k "issue_draft_adoption or selected_skeleton_fill or provider_and_dogfood_wrapper_smoke or authoring_validate"
# 98 passed, 167 deselected in 86.71s

uv run pytest tests/unit/infra/test_init_update.py -q -k authoring_pack
# 1 passed, 544 deselected in 0.26s

uv run pytest tests/cli_runtime/test_authoring.py -q
# 268 passed in 202.42s

./spec-dock/scripts/spec-dock authoring validate issue-draft-adoption --help
# implemented help exposes --input, --issue-dir, --review-report, --expected-review-digest, --expected-draft-pack-digest, --report-path

./spec-dock/scripts/spec-dock authoring validate selected-skeleton-fill --help
# implemented help exposes --input, --issue-dir, --assurance, --selected-skeleton, --expected-profile, --report-path

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=202

./spec-dock/scripts/spec-dock assurance verify
# assurance verify: ok; authorized_profile=standard

git diff --check
# ok

rg -n "/Users/iwasawayuuta|\\.codex/skills/chatgpt-use|oracle-chatgpt" src/spec_dock/assets/spec_dock/scripts spec-dock/scripts tests/cli_runtime/test_authoring.py
# no matches
```

## クロージャ網羅（Closure Coverage）

| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| CLOS-001 | S01/S06/S07 | help commands and focused help tests | pass | deferred wording removed |
| CLOS-002 | S02/S03 | `issue-draft-adoption` result contract and positive fixture | pass | evidence-only fields verified; no adoption/readiness claims |
| CLOS-003 | S02/S04 | `selected-skeleton-fill` result contract and positive fixture | pass | profile/section summary verified; no adoption/readiness claims |
| CLOS-004 | S03/S08 | issue draft adoption negative matrix | pass | non-pass review statuses, missing Issue node, parent/draft/review/source digest mismatch, unsafe targets, safe/unsafe report path covered |
| CLOS-005 | S04/S08 | selected skeleton negative matrix | pass | missing/extra/duplicate/empty inventory, profile/hash/source mismatch, missing/invalid prerequisites covered |
| CLOS-006 | S05/S08 | report path fixtures | pass | safe report writes noncanonical output; unsafe canonical and symlink report paths rejected |
| CLOS-007 | S06 | renderer / CLI output assertions | pass | output remains validation evidence and does not claim adoption/readiness |
| CLOS-008 | S06/S07 | parser and invocation tests | pass | both commands promoted from deferred placeholders |
| CLOS-009 | S07 | provider/dogfood/installed wrapper parity smoke | pass | provider, dogfood, and installed wrappers delegate to runtime command and avoid legacy selected helper surface |
| CLOS-010 | S03/S04/S08 | forbidden authority and sensitive path fixtures | pass | forbidden claims and secret/unsafe paths rejected |
| CLOS-011 | S00 | requirement/design/plan/report rewritten from draft adoption evidence | pass | fresh planning spec-review passed |
| CLOS-012 | S99 | `./spec-dock/scripts/spec-dock validate` | pass | nodes=202 |
| CLOS-013 | S99 | `./spec-dock/scripts/spec-dock assurance verify` | pass | authorized_profile=standard |
| CLOS-014 | S99 | `git diff --check` | pass | no output |
| CLOS-015 | S99 | local-wrapper path scan | pass | no hardcoded personal ChatGPT wrapper path found |
| CLOS-016 | S99 | commit/push/issue finish | pending | run after final code-reviewer and qa-reviewer pass |

## マイルストーン / commit 候補ゲート（Milestone / Commit Candidate Gate）

| マイルストーン / step | クロージャ状態（closure state） | コミット候補 / コミット範囲（commit candidate / scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） |
|---|---|---|---|---|---|
| implementation | ready | `iss-00303` runtime validators, wrappers, tests, dogfood mirror, planning/report evidence | not committed | pending | not a no-op |

## 最終品質ゲート（Final Quality Gate）

| Gate | Status | Evidence |
|---|---|---|
| spec-reviewer | pass | fresh planning re-review returned no findings; `review_status=pass` |
| code-reviewer | pass | final re-review returned no findings; `review_status=pass` |
| qa-reviewer | pass | final re-review returned no P0/P1 findings; P2 selected source hash sensitivity strengthened and focused tests pass |
| PR delivery | deferred | final PR delivery belongs to `iss-00307` |

## 省略/例外メモ

- This is an intermediate Issue. Per-Issue PR delivery is intentionally omitted and deferred to `iss-00307`.
- Runtime implementation is complete for this Issue; final code/QA reviewer pass must be recorded before `issue finish`.
