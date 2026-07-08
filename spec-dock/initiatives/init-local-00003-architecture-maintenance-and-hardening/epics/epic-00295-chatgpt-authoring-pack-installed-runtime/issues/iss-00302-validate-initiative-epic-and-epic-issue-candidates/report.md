---
種別: 実装報告書（Issue）
ID: "iss-00302"
タイトル: "Initiative Epic Validation"
関連GitHub: ["#302"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00295", "init-local-00003"]
---

# iss-00302 Initiative Epic Validation — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

> `report.md` は観測証跡台帳（observed evidence ledger）の scaffold です。planned requirements、evidence destination、closure 条件は `plan.md` が持ち、この文書は実際の Red / Green / Refactor evidence、発見された tests、closure delta、reviewer status、commit/no-op evidence を記録する evidence slot です。workflow / compliance authority は skills、docs、accepted ADRs、reviewer gates に置きます。

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger / 必須）

`report.md` は実装中・文書更新中に発生した material な仕様解釈、判断、plan 逸脱、tradeoff、open question、promotion / follow-up を記録する audit trail でもある。worker の raw note や作業 transcript を貼る場所ではなく、orchestrator が source docs、diff、tests、reviewer output と照合して issue-level の canonical entry に統合する。

Material な判断がない場合もこの section は残し、次を明示する。

- No material interpretation changes.
- No decision entries.

Ledger entry は次の契約値を使う。

- `Status`: `open` / `resolved` / `superseded`
- `Type`: `interpretation` / `scope` / `implementation` / `compatibility` / `test-strategy` / `operation` / `deviation` / `follow-up`
- `Disposition`: `applied` / `rejected` / `promoted_to_design` / `promoted_to_adr` / `promoted_to_plan` / `converted_to_followup` / `deferred` / `no_action` / `superseded`

完了時の意味論（completion semantics）:
- issue completion 前に `Status=open` の entry を残してはならない。
- `Status=resolved` は `Disposition`、evidence、必要な follow-up を持つ。
- `Status=superseded` または `Disposition=superseded` は置換先 entry ID を持つ。
- `Disposition=promoted_to_design` / `promoted_to_adr` / `promoted_to_plan` は昇格先 artifact と evidence を持つ。
- `Disposition=converted_to_followup` は follow-up issue / discussion / ADR candidate の参照を持つ。
- `Disposition=deferred` は scope 外である理由、blocking でない根拠、revisit 条件を持つ。
- `Disposition=no_action` は issue-local な判断で追加対応不要である理由を持つ。将来も効く durable decision を `report.md` だけに閉じ込めてはならない。

Disposition ごとの必須証跡:
- `applied`: 変更した artifact / 実装証跡と、issue-local 適用で十分な理由。
- `rejected`: 却下した選択肢、理由、blocking impact が残らない根拠。
- `promoted_to_design` / `promoted_to_adr` / `promoted_to_plan`: 昇格先 artifact 参照と証跡。
- `converted_to_followup`: follow-up issue / discussion / ADR candidate 参照と blocking / non-blocking の分類。
- `deferred`: scope-out 理由、non-blocking の根拠、revisit 条件。
- `no_action`: 判断が issue-local で durable ではない理由。
- `superseded`: 置換先 entry ID と置換理由。

| 識別子（ID） | 状態（Status） | 種別（Type） | 起票元（Raised By） | 契機 / 差分（Gap） | 検討した選択肢 | 判断 / 解釈 | 根拠（Rationale） | 処置（Disposition） | 証跡（Evidence） | フォローアップ（Follow-up） |
|---|---|---|---|---|---|---|---|---|---|---|
| D-001 | resolved | scope | orchestrator | Candidate validation pass が approval / adoption / reviewer pass と混同されるリスク | A: validation で node creation まで扱う; B: candidate-only evidence validation に限定 | B を採用 | Epic design は Authoring runtime plane と Authority plane を分離し、node creation / approval / adoption は後続 gate に残す | promoted_to_design | `requirement.md`, `design.md`, ChatGPT Use transcript | none |
| D-002 | resolved | operation | orchestrator | ChatGPT Use output をそのまま canonical docs に貼るか | A: raw output をそのまま採用; B: main orchestrator が検証・圧縮して canonical docs に統合 | B を採用 | Canonical docs は main orchestrator-owned であり、ChatGPT output は evidence である | applied | `/Users/iwasawayuuta/.oracle/sessions/specdock-iss-00302-planning/artifacts/transcript.md`, `requirement.md`, `design.md`, `plan.md` | none |
| D-003 | resolved | specification | spec-reviewer | Initiative -> Epic candidate payload schema が設計に不足していた | A: common schema のみで実装に委ねる; B: Initiative -> Epic 固有 schema を design に追加 | B を採用 | 2 promoted commands の片方が under-specified になると実装が分岐する | promoted_to_design | spec-reviewer P1; `design.md` Initiative -> Epic additions | none |
| D-004 | resolved | specification | spec-reviewer | review report non-pass status が valid command status に mapping されていなかった | A: `non-pass` の曖昧表現を残す; B: observed review status ごとに `blocked/fail/stale/rejected` へ mapping | B を採用 | `non-pass` は command status ではなく、tests と実装の契約にできない | promoted_to_design | spec-reviewer P1; `design.md` Review report gate mapping; `plan.md` tests | none |
| D-005 | resolved | test-strategy | spec-reviewer | review digest mismatch の明示テストが不足していた | A: CL-012 の総称で扱う; B: concrete test case と S04 test に追加 | B を採用 | AC-012 の close 条件を実装者が見落とさないよう固定する | promoted_to_plan | spec-reviewer P2; `plan.md` S04 and test table | none |
| D-006 | resolved | test-strategy | spec-reviewer | review report status `fail` / `blocked` / unsupported の明示テストが不足していた | A: rejected/stale tests に包含する; B: concrete test case と S04 test に追加 | B を採用 | requirement/design の status mapping 全体を executable contract にする | promoted_to_plan | spec-reviewer P1; `plan.md` S04 and concrete test table | none |
| D-007 | resolved | specification | spec-reviewer | unsupported grade/profile の source of truth と test が不足していた | A: 実装で既存値を推測する; B: `AssuranceProfile` / Issue grade matrix に合わせて allowed values を design に固定し、plan に test を追加 | B を採用 | candidate validator は profile authorization ではなく payload consistency を検査するため、allowed value set を明示する必要がある | promoted_to_design | spec-reviewer P1; `design.md` Epic -> Issue validation; `plan.md` tests | none |
| D-008 | resolved | test-strategy | spec-reviewer | unsafe file category の concrete test が path-shape に偏っていた | A: CL-008 の広い文言に任せる; B: unsupported suffix / symlink / executable / binary / oversized draft を concrete test table に追加 | B を採用 | AC-008 を path traversal だけで満たしたと誤解しないようにする | promoted_to_plan | spec-reviewer P2 pass finding; `plan.md` concrete test table | none |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | ChatGPT Use / Oracle GPT-5.5 Pro Extended | `requirement.md` | Issue 00302 の scope、non-scope、RQ/AC、failure modes、grade を具体化した | `artifacts/20260707t171259z-draft-requirement-validate-initiative-epic-and-epic-issue-candidates-draft-requirement.md`; Oracle transcript recorded outside repo | spec-review |
| EAL-002 | adopted | ChatGPT Use / Oracle GPT-5.5 Pro Extended | `design.md` | candidate validation の CLI/application/domain/presentation boundary と output authority contract を具体化した | `artifacts/20260707t171300z-draft-design-validate-initiative-epic-and-epic-issue-candidates-draft-design.md`; Oracle transcript recorded outside repo | spec-review |
| EAL-003 | adopted | ChatGPT Use / Oracle GPT-5.5 Pro Extended | `plan.md` | CL-001..CL-017、S01..S07、test cases、reviewer gates、relay policy を具体化した | `artifacts/20260707t171300z-01-draft-plan-validate-initiative-epic-and-epic-issue-candidates-draft-plan.md`; Oracle transcript recorded outside repo | spec-review |
| EAL-004 | adopted | assurance classify / compose | `.assurance.json`, `design.md`, `plan.md`, `report.md` | `authorized_profile=standard` を確定し、Standard report scaffold を生成した | `./spec-dock/scripts/spec-dock assurance classify --stage requirement`; `./spec-dock/scripts/spec-dock assurance compose --artifact all` | assurance verify |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | Candidate validators keep ChatGPT batch planning output as evidence-only before node creation | compatibility wrappers / dogfood mirror / report output are implementation aids | low | spec-review pass |

## Spec Authoring Gate（仕様 authoring ゲート / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | Epic docs、Issue draft artifacts、current authoring runtime/tests、ChatGPT Use transcript | none | adopted into `requirement.md` after reviewer fixes | pass | no | promote |
| design | `requirement.md`、ChatGPT Use design draft、existing layered runtime、scanner/ZIP contract | Initiative -> Epic schema and review status mapping fixed after reviewer P1 | adopted into `design.md` after reviewer fixes | pass | no | promote |
| plan | `requirement.md`、`design.md`、ChatGPT Use plan draft、verification queue | review digest mismatch and unsafe file category concrete tests added after reviewer findings | adopted into `plan.md` after reviewer fixes | pass | no | promote |

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）
- 委任 authoring の使用:
  - used / not used
- 未使用の場合:
  - manual authoring path / 委任ドラフトを昇格証跡として使っていない理由。
- lifecycle state（契約値）:
  - `requested`, `produced`, `integrated`, `partially_integrated`, `rejected`, `superseded`, `blocked`, `stale`
- 昇格不可 state:
  - `stale`, `rejected`, `superseded`, `blocked`
- 標準出力先:
  - 対象 scope の `artifacts/` direct child にある flat Markdown
  - filename: typed artifacts use `<ts>-<type>-<slug>.md` or `<ts>-<nn>-<type>-<slug>.md`; blank artifacts use `<ts>-<slug>.md` or `<ts>-<nn>-<slug>.md`
- 軽量 provenance:
  - `created_by_role`, `scope_id`, `source_paths`, `intended_targets`, `adoption_status: unreviewed`, `reflected_to: []`, `diff_guard_result`, fallback decision, report evidence destination, adoption ledger note
  - 互換 label: source artifacts, draft artifact path, status, integration result, rejected portions, blockers, reviewer result, promotion decision
- 禁止 self-claim:
  - `authority: accepted`, `adoption_status: adopted`, non-empty `reflected_to`, reviewer pass, phase completion, implementation readiness
- 禁止 wildcard token:
  - `*`, `grants.*`, `all`
- 標準必須にしない field:
  - task manifest hash, Permission Profile hash, session invocation hash, probe run id, session hash
- historical note:
  - legacy `discussions/` と既存 `iss-00126` などの manifest/Profile/probe/session artifacts は grandfathered evidence として残し、削除・rename・validation failure 化しない。

| ロール（created_by_role） | 範囲（scope_id） | ドラフトパス（artifact draft path） | 参照元（source_paths） | 予定反映先（intended_targets） | 採用状態（adoption_status） | 反映先（reflected_to） | 差分ガード結果（diff_guard_result） | 統合結果 | 採用しなかった部分 | ブロッカー | レビュー結果（reviewer result） | 昇格判断（promotion decision） |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ChatGPT Use / Oracle GPT-5.5 Pro Extended | iss-00302 | `artifacts/20260707t171259z-draft-requirement-validate-initiative-epic-and-epic-issue-candidates-draft-requirement.md`; `artifacts/20260707t171300z-draft-design-validate-initiative-epic-and-epic-issue-candidates-draft-design.md`; `artifacts/20260707t171300z-01-draft-plan-validate-initiative-epic-and-epic-issue-candidates-draft-plan.md` | active Epic docs; active Issue scaffold; Issue draft artifacts; authoring runtime files/tests; Oracle transcript path recorded in EAL-001..003 | `requirement.md`, `design.md`, `plan.md` | adopted | `requirement.md`, `design.md`, `plan.md` | pass | source draft preserved; adopted portions integrated by main orchestrator into canonical docs | raw verbosity and uncertainty notes not copied verbatim | none | pass | promote |

### 委任ドラフトの失敗モード（Delegated Draft Failure Modes）
| 失敗モード | 期待される判定 | 許可される次アクション | レポート証跡の記録先（report evidence destination） | 昇格可否 |
|---|---|---|---|---|
| ワークフロー単位の許可証跡不足（missing workflow-scoped authorization evidence） | blocked / incomplete | ワークフロー利用依頼の authorization source と boundary を記録する、または手動 authoring に戻す | ワークフロー単位の named role 許可（Workflow-Scoped Authorization） / この section | ineligible |
| 前段 reviewer pass 不足 / stale（missing/stale previous reviewer pass） | blocked / incomplete | レビューゲートを再実行する（rerun reviewer gate） | レビューゲート証跡（Reviewer Gate Status / Final Spec Review Gate） | ineligible |
| 設計中の要件 gap（requirement gap during design） | blocked / incomplete | requirement phase へ戻す | 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger） | ineligible |
| 計画中の設計 gap（design gap during plan） | blocked / incomplete | design phase へ戻す | 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger） | ineligible |
| ロール利用不可（role unavailable） | blocked / manual path | 利用不可を記録し、妥当なら手動で続行する | この section | ineligible |
| 禁止行為の試行（forbidden action attempt） | rejected | ドラフトを破棄し incident を記録する | この section / decision ledger | ineligible |
| 古いドラフト（stale draft） | stale | 再生成または差分調整する | この section | ineligible |
| 置換済みドラフト（superseded draft） | superseded | 置換先ドラフトを参照する | この section | ineligible |
| 委任使用主張に対する証跡不足（missing draft evidence when delegated use is claimed） | incomplete | 証跡を追加する、または委任使用 claim を外す | この section | ineligible |
| reviewer 利用不可 / 拒否 / waiver / provisional（reviewer unavailable/denied/waived/provisional） | blocked / incomplete | fresh な passed reviewer を取得する、または昇格なしの risk acceptance を記録する | レビューゲート証跡（Reviewer Gate Status / Final Spec Review Gate） | ineligible |

## 実装サマリー (任意)
- `authoring validate initiative-epic-candidates` と `authoring validate epic-issue-candidates` を deferred skeleton から runtime command へ昇格した。
- Candidate validation は ChatGPT authoring pack の staged evidence を evidence-only として検証し、node creation / canonical write / `.assurance.json` mutation / reviewer pass / execution readiness / PR readiness を一切成立させない。
- Provider-side shipped runtime と dogfood mirror の両方に domain / application / presentation / CLI wiring / compatibility wrapper を反映し、`tests/cli_runtime/test_authoring.py` で provider と dogfood smoke を確認した。

## 実装記録（セッションログ） (必須)

### セッションログ（2026-07-08 HH:MM - HH:MM）

#### 対象
- Step: Planning authoring
- AC/EC: AC-001..AC-017
- 計画上の出典（Planned source）:
  - `plan.md` section: 1-8
  - closure ids: CL-001..CL-017

#### 実施内容
- `iss-00302` を start し、branch `iss-00302-validate-initiative-epic-and-epic-issue-candidates` を作成・push した。
- ChatGPT Use / Oracle GPT-5.5 Pro Extended に current branch と repository context を渡し、Issue requirement/design/plan draft を作成した。
- ChatGPT output を main orchestrator が検証し、canonical `requirement.md` / `design.md` / `plan.md` に採用した。
- `assurance classify --stage requirement` と `assurance compose --artifact all` を実行し、Standard profile と source binding を更新した。
- fresh `spec-reviewer` を繰り返し実行し、P1/P2 findings を `requirement.md` / `design.md` / `plan.md` / `report.md` に反映した。最終 review は `review_status=pass`。
- `candidate_contract.py`、`candidate_validation.py`、`candidate_validation_renderer.py` を追加し、CLI / compatibility wrappers / dogfood mirror / tests を更新した。

#### 実行コマンド / 結果
```bash
/Users/iwasawayuuta/.codex/skills/chatgpt-use/scripts/oracle-chatgpt --slug specdock-iss-00302-planning --prompt-file <private prompt file>
# completed; model resolved=Pro Extended; transcript saved at /Users/iwasawayuuta/.oracle/sessions/specdock-iss-00302-planning/artifacts/transcript.md

./spec-dock/scripts/spec-dock assurance classify --stage requirement
# assurance classify: ok; authorized_profile=standard

./spec-dock/scripts/spec-dock assurance compose --artifact all
# assurance compose: ok; changed design.md, plan.md, report.md

./spec-dock/scripts/spec-dock assurance verify
# assurance verify: ok

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=202

uv run pytest tests/cli_runtime/test_authoring.py -q -k "validate_initiative_epic or validate_epic_issue or candidate or dogfood_runtime_path"
# 47 passed, 163 deselected

uv run pytest tests/cli_runtime/test_authoring.py -q
# 210 passed

./spec-dock/scripts/spec-dock assurance verify
# assurance verify: ok

git diff --check
# ok

rg -n "/Users/iwasawayuuta|\\.codex/skills/chatgpt-use|oracle-chatgpt" src/spec_dock/assets/spec_dock/scripts spec-dock/scripts tests/cli_runtime/test_authoring.py
# no matches
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S01 | 赤フェーズ / 代替証跡（Red / alternative） | promoted commands are still deferred before implementation | `_DEFERRED_COMMANDS` still contained promoted validate commands before test update | inspection and focused pytest after test edit | pass | tests now expect implemented contract |
| S01 | 緑フェーズ（Green） | help and fixture builders pass after command promotion tests | help and fixture tests pass | `uv run pytest tests/cli_runtime/test_authoring.py -q -k "validate_initiative_epic or validate_epic_issue or candidate"` | pass | 28 passed before dogfood expansion; later 34 passed |
| S01 | リファクタリング（Refactor） | provider/dogfood mirror and unrelated diff guard checked | provider/dogfood files copied intentionally; diff check ok | `git diff --check` | pass | no unrelated formatting failure |
| S02 | 赤フェーズ / 代替証跡（Red / alternative） | malformed/missing/duplicate/overlap/unsafe fixture tests fail before domain contract | negative fixtures added for duplicate, overlap, path, suffix, executable, binary, oversized | focused pytest | pass | final focused lane passed |
| S02 | 緑フェーズ（Green） | domain candidate contract validates schema and comparison deterministically | `candidate_contract.py` returns stable status/findings/candidates | focused pytest | pass | duplicate/overlap/status fixtures covered |
| S02 | リファクタリング（Refactor） | contract remains in domain layer without CLI coupling | domain file has no argparse/CLI dependency | diff inspection | pass | CLI wiring stays in commands layer |
| S03 | 赤フェーズ / 代替証跡（Red / alternative） | authority/sensitivity negative fixtures reject unsafe payloads | secret/raw transcript/forbidden claim/profile fixtures added | focused pytest | pass | raw secret value absent assertion included |
| S03 | 緑フェーズ（Green） | existing scanner reuse rejects claims/secrets/profile authority | existing scanner reused for Markdown payloads; JSON profile authority handled structurally | focused pytest | pass | `authorized_profile: null` allowed, non-null rejected |
| S03 | リファクタリング（Refactor） | scanner reuse avoids duplicate secret patterns | no new secret regex added | diff inspection | pass | reused `scan_authoring_payload` / `scan_sensitive_payload` |
| S04 | 赤フェーズ / 代替証跡（Red / alternative） | missing/malformed/non-pass/stale/report-path fixtures expose orchestration gaps | review non-pass, stale mismatch, unsafe report fixtures added | focused pytest | pass | stale/rejected/fail/blocked/unsupported covered |
| S04 | 緑フェーズ（Green） | application use case returns concrete status mapping and no-mutation flags | `candidate_validation.py` maps review gate and stale checks | focused pytest | pass | source/parent/review digest mismatch covered |
| S04 | リファクタリング（Refactor） | report path guard aligns with review/stage behavior | candidate validation reuses `_unsafe_report_path` | focused pytest and inspection | pass | canonical report path rejected without write |
| S05 | 赤フェーズ / 代替証跡（Red / alternative） | output boundary assertions fail if pass is confused with adoption/readiness | JSON assertions verify false no-mutation flags | focused pytest | pass | text renderer also includes boundary flags |
| S05 | 緑フェーズ（Green） | JSON/text render stable authority-separated result | renderer uses sorted JSON and explicit text fields | `tests/cli_runtime/test_authoring.py` | pass | no adoption/readiness success claim |
| S05 | リファクタリング（Refactor） | renderer does not embed raw payloads/secrets | findings only; no raw draft body in result | focused pytest | pass | `abc123secret` absent from stdout |
| S06 | 赤フェーズ / 代替証跡（Red / alternative） | CLI/wrapper/dogfood smoke fails before wiring | CLI skeleton was deferred; tests now exercise implemented command | focused pytest | pass | dogfood smoke added |
| S06 | 緑フェーズ（Green） | promoted CLI commands and compatibility wrappers call runtime use case | parser/commands/wrappers connected to use case | full authoring pytest | pass | `197 passed` |
| S06 | リファクタリング（Refactor） | no hardcoded personal ChatGPT path and provider/dogfood parity holds | no hardcoded local wrapper path found | `rg -n "/Users/iwasawayuuta|\\.codex/skills/chatgpt-use|oracle-chatgpt" ...` | pass | no matches |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S02/S03 | JSON scanner rejected `authorized_profile: null` because generic authority scanner saw the key name | focused pytest failure | JSON candidate payloads use `scan_sensitive_payload`; non-null `authorized_profile` remains structural rejection | CL-011 | no | focused pytest failure and fix |
| S07 | spec-reviewer P2 requested explicit unsafe file category tests | spec-review pass finding | unsupported suffix / symlink / executable / binary / oversized draft cases added to plan/tests | CL-008 | yes, applied before implementation closeout | `plan.md`, focused pytest |
| S07 | code-reviewer found source hash alias, unsafe candidate paths, empty index, and binary review report gaps | code-reviewer | implemented alias/path/index/report fixes and added regression tests | CL-006, CL-008, CL-012 | no | focused pytest `47 passed`; full authoring pytest `210 passed` |
| S07 | qa-reviewer found authority schema, epic dependency, secret draft path, report path category, forward dependency, schema version, and symlink draft gaps | qa-reviewer | implemented required schema/dependency/path checks and added regression tests | CL-006, CL-008, CL-013 | no | focused pytest `47 passed`; full authoring pytest `210 passed` |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S01 | CL-001, CL-002, CL-003 input | command promotion tests and fixture builders complete | help tests and candidate fixture positive tests pass | pass | focused lane passed |
| S02 | CL-006, CL-007, CL-008 | domain candidate contract rejects malformed/duplicate/unsafe candidates | negative fixture tests pass | pass | unsafe file categories included |
| S03 | CL-009, CL-010, CL-011, CL-014 | authority and sensitivity validation rejects forbidden claims/secrets/profile authority | secret/raw transcript/forbidden claim/profile tests pass | pass | raw secret not printed |
| S04 | CL-012, CL-013 | review gate, stale checks, parent/source/digest checks, and report path guard complete | non-pass/stale/report path tests pass | pass | concrete status mapping covered |
| S05 | CL-014 | JSON/text output preserves authority boundary | no-mutation flags asserted in JSON/text renderer | pass | no readiness/PR/canonical write claim |
| S06 | CL-001, CL-002, CL-015 | CLI wiring, wrappers, and dogfood smoke complete | full authoring test and dogfood smoke pass | pass | provider/dogfood runtime paths verified |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| CL-001 | S01/S06 | yes | red-required | deferred commands present before implementation | promoted command tests and CLI wiring tests | pass | implemented commands replace deferred skeleton |
| CL-002 | S01/S06 | yes | red-required | deferred help text before implementation | help and wrapper smoke tests | pass | implemented help exposes `--input` and expected parent args |
| CL-003 | S01 | yes | red-required | fixture helper absent before implementation | fixture builder based positive command tests | pass | Initiative/Epic and Epic/Issue positive fixtures pass |
| CL-006 | S02 | yes | red-required | schema validation absent before implementation | malformed/missing field tests | pass | covered by candidate contract fixtures |
| CL-007 | S02 | yes | red-required | duplicate/overlap validation absent before implementation | duplicate/overlap tests | pass | deterministic findings asserted |
| CL-008 | S02 | yes | red-required | unsafe category validation absent before implementation | unsafe path and payload tests | pass | path traversal, hidden, suffix, executable, binary, oversized covered |
| CL-009 | S03 | yes | red-required | sensitivity rejection absent before implementation | secret/raw transcript redaction tests | pass | raw secret absent from stdout |
| CL-010 | S03 | yes | red-required | forbidden authority claim rejection absent before implementation | forbidden authority claim tests | pass | `PR-ready` rejected |
| CL-011 | S03 | yes | red-required | profile authority validation absent before implementation | authorized profile advisory-only tests | pass | non-null `authorized_profile` rejected; unsupported grade/profile fail |
| CL-012 | S04 | yes | red-required | stale comparison absent before implementation | source/parent/review digest stale tests | pass | all stale comparisons covered |
| CL-013 | S04 | yes | red-required | unsafe report path absent before implementation | unsafe report path tests | pass | canonical report path rejected without write |
| CL-014 | S03/S05 | yes | red-required | output authority boundary absent before implementation | authority-separated output tests | pass | no-mutation flags asserted |
| CL-015 | S06 | yes | red-required | dogfood candidate validation absent before implementation | provider and dogfood smoke tests | pass | dogfood runtime path candidate smoke added |
| CL-016 | S07 | yes | manual-required | n/a | full pytest/validate/assurance/diff-check queue | pass | `210 passed`; validate/assurance/diff-check ok |
| CL-017 | S07 | yes | manual-required | n/a | finish handoff report evidence | pending | issue finish not yet run |

- `closure id / test id` は Spec-Locked Closure Index の `id` を指す。別 alias を使う場合は `Closure Delta` で対応を記録する。

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| CL-001..CL-016 | S01..S07 | focused/full pytest, validate, assurance, diff-check, rg local-wrapper inspection, spec/code/QA reviewer results | pass | fresh spec-reviewer / code-reviewer / qa-reviewer gates passed after fixes |
| CL-017 | S07 | issue finish and handoff to next Issue | pending | not finished yet |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| added | CL-008 | unsafe file category concrete cases | CL-008 | spec-reviewer P2 pass finding requested explicit suffix/symlink/executable/binary/oversized cases | yes, applied | no, spec-review had already passed with P2; added as implementation hardening |

#### ワークフロー単位の named role 許可（Workflow-Scoped Authorization）
`workflow_issue.md` is the policy source for workflow-scoped authorization. This report records observed authorization source, boundary, expiry, and denied / unavailable / host conflict handling only.

Authorization source は、ユーザーによる SpecDock workflow 利用依頼でよい。範囲は active repo/worktree、active SpecDock scope、current session、SpecDock-defined named roles、documented role responsibility に限る。この section は role ごと・phase ごとの追加承認 gate ではなく、scope 内の named role 利用前に追加許可を求める根拠にしてはならない。

別途確認が必要なのは scope expansion、破壊的操作、外部公開、credential を伴う外部 mutation、private external system、SpecDock workflow 外の role 利用である。unavailable / denied / host conflict は fail-closed とし、fresh `passed` reviewer gate の代替にしてはならない。

| 許可元（authorization source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可 / host conflict 理由（denied / unavailable / host conflict reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| User request to execute this Epic with SpecDock workflow | `/Users/iwasawayuuta/.codex/worktrees/aa9c/spec-dock` / branch `iss-00302-validate-initiative-epic-and-epic-issue-candidates` | iss-00302 | current session | spec-reviewer / code-reviewer / qa-reviewer / ChatGPT Use planning evidence | 範囲: active repo/worktree、active SpecDock scope、current session、SpecDock-defined named roles、documented role responsibility。破壊的操作 / 外部公開 / credentialed external mutation / scope expansion / private external system use / out-of-workflow role は含めない | issue complete / session end / scope change / host policy conflict / user revocation | none observed | proceed to commit, push, and `issue finish` after final guidance clears |

#### 実装委任ゲート（Implementation Delegation Gate）
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records observed evidence only.

| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | approved-local-execution | bounded runtime/test/report integration after ChatGPT planning and reviewer feedback; parent orchestrator retained integration responsibility | N/A | provider-side runtime, dogfood mirror, CLI wrappers, tests, and issue report only | active issue docs and provider-side `src/spec_dock/assets/spec_dock/scripts/` | candidate validator implementation, parser/command wiring, compatibility wrappers, dogfood mirror parity, tests, report evidence | node creation, canonical adoption command, `.assurance.json` mutation by authoring runtime, reviewer pass claim, execution-ready/PR-ready claim, personal backend path dependency | focused/full authoring pytest, validate, assurance verify, diff-check, local-wrapper path scan, fresh spec/code/QA review | unresolved spec gap, failing tests, reviewer fail, unsafe authority claim, external mutation need | changed files / verification / risks / integration decision recorded below | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S01 | N/A, approved-local-execution | Parent orchestrator implemented the bounded candidate validators and incorporated reviewer feedback directly because the active work combined provider/dogfood parity, report evidence, and small fail-closed fixes | provider runtime files, dogfood mirror files, `tests/cli_runtime/test_authoring.py`, active issue docs/report | `uv run pytest tests/cli_runtime/test_authoring.py -q` -> 210 passed; focused lane -> 47 passed; `spec-dock validate` -> ok; `assurance verify` -> ok; `git diff --check` -> ok | spec-reviewer pass; code-reviewer pass; qa-reviewer pass | none blocking; commit/finish pending | accepted |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| S01 | delegation not used because the remaining work was a bounded local integration/fix loop after reviewer findings, and splitting provider/dogfood/report edits would increase coordination risk | User requested continued SpecDock execution; no degraded waiver or risk acceptance used | active issue docs/report; provider `authoring_pack` runtime files; dogfood mirror files; `tests/cli_runtime/test_authoring.py` | implement and test only the approved candidate validation scope | rollback by reverting the single commit before `issue finish`; no external mutation before push | focused/full authoring pytest pass; `spec-dock validate` pass; `assurance verify` pass; `git diff --check` pass | fresh spec-reviewer / code-reviewer / qa-reviewer all passed after fixes | no unavailable/denied/host conflict observed; proceed to commit |

#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）
Lite は specialist / fallback evidence を必須化しないが、not applicable / skip reason を記録する。Standard は specialist evidence、skip reason、または manual fallback を記録する。Strict / Critical は specialist evidence または明示的な manual fallback を記録し、skip reason だけでは readiness evidence にしない。

| グレード（Grade） | 必要な専門家 / 代替（required specialist / fallback） | 使用状況（usage） | 証跡（evidence） | 鮮度 spec-reviewer 判定（fresh spec-reviewer verdict） | 実行可否（execution readiness） |
|---|---|---|---|---|---|
| `standard` | manual fallback | used | manual fallback evidence: ChatGPT Use planning evidence in EAL-001..003 plus main-orchestrator adopted canonical docs | pass | ready |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S01 | final spec review | spec-reviewer | fresh | pass | no | promote | Final pass after P1/P2 planning fixes; P2 unsafe file category hardening was incorporated before closeout |
| S01 | final code review | code-reviewer | fresh | pass | no | promote | Final pass after source hash alias, unsafe path, empty index, binary/unreadable report, dependency, and OSError fixes |
| S01 | final QA review | qa-reviewer | fresh | pass | no | promote | Final pass after schema/profile/dependency/path/report/symlink coverage fixes |

#### マイルストーン / commit 候補ゲート（Milestone / Commit Candidate Gate）
| マイルストーン / step | クロージャ状態（closure state） | コミット候補 / コミット範囲（commit candidate / scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S01 | ready-for-commit | candidate validation runtime/tests/docs for iss-00302 | pending before commit | pending after commit | not a no-op | N/A | N/A | N/A |

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/candidate_contract.py` - candidate payload contract and fail-closed validation rules.
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/candidate_validation.py` - validation use case, review gate mapping, stale digest checks, and no-mutation authority boundary.
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/authoring_pack/candidate_validation_renderer.py` - text/JSON rendering for candidate validation results.
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/authoring.py` and `cli/parser.py` - promoted command wiring.
- `src/spec_dock/assets/spec_dock/scripts/authoring-pack/validate_issue_candidates.py` and `validate_initiative_epic_candidates.py` - compatibility wrappers.
- `spec-dock/scripts/**` mirrored runtime files - dogfood installed surface parity.
- `tests/cli_runtime/test_authoring.py` - positive, negative, authority, stale, report, dependency, and dogfood smoke coverage.
- active issue `requirement.md`, `design.md`, `plan.md`, `.assurance.json`, `report.md` - canonical planning, assurance, and evidence ledger.

#### コミット
- pending before final commit.

#### メモ
- 中間 Issue のため PR delivery は行わず、`iss-00307` の final quality gate / mergeable PR delivery に defer する。

---

### セッションログ（2026-07-08 HH:MM - HH:MM）

#### 対象
- Step: S07 final closeout
- AC/EC: CL-001..CL-017

#### 実施内容
- Fresh code-reviewer / qa-reviewer / spec-reviewer gates were completed after focused fixes.
- Focused and full `tests/cli_runtime/test_authoring.py` lanes passed.
- `spec-dock validate`, `assurance verify`, `git diff --check`, and local-wrapper dependency scan passed.
- Remaining action is commit, push, and `issue finish`.

---

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| docs / templates / README / workflow / skill / migration notes | no | N/A | This Issue adds runtime candidate validators only; user-facing workflow docs are deferred to `iss-00306` by Epic plan | pass |

### 最終 QA ゲート（Final QA Gate）
| レビュアー（reviewer） | 範囲 | 統合テスト判断（integration test decision） | 証跡（evidence） | 結果（result） |
|---|---|---|---|---|
| qa-reviewer | whole issue obligation coverage | added | Fresh QA review passed after schema/profile/dependency/path/report/symlink regression coverage was added | pass |

### 最終コードレビューゲート（Final Code Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| code-reviewer | issue-wide integrated diff | P1/P2 findings fixed: source hash alias, unsafe candidate paths, empty index, binary/unreadable review report, dependency validation, OSError handling | 1 | pass |

### 最終 spec review ゲート（Final Spec Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| spec-reviewer | requirement / design / plan / report / implementation / tests / docs alignment | P1/P2 planning findings fixed; unsafe file category hardening incorporated | 1 | pass |

### 最終 commit（Final Commit）
| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| this report plus staged commit candidate | iss-00302 candidate validation runtime/tests/docs | final response after commit/push/issue finish; no per-Issue PR | ready-for-commit |

## 遭遇した問題と解決 (任意)
- 問題: candidate validation initially lacked several fail-closed edges found by code/QA review.
  - 解決: source hash alias, unsafe host/local/secret paths, empty index, unreadable/binary report, dependency, schema, symlink, and OSError regression coverageを追加した。

## 学んだこと (任意)
- Candidate validation は node creation や adoption ではなく、evidence-only の integrity gate として閉じる方が安全である。

## 今後の推奨事項 (任意)
- `iss-00303` では Issue draft adoption と selected skeleton validation を、candidate validation とは別の authority boundary として扱う。

## 省略/例外メモ (必須)
- 該当なし

<!-- spec-dock:managed-section begin id="report.step-evidence" -->
## Step Evidence
- Record Red, Green, and refactor evidence for each executed step.
- Link each closure id to its observed verification result.
<!-- spec-dock:managed-section end id="report.step-evidence" -->
