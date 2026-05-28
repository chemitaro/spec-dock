---
種別: 実装報告書（Issue）
ID: "iss-00134"
タイトル: "Matt Pocock grill-style clarification workflow を spec-dock に取り込む"
関連GitHub: ["#134"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-05-28"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00067", "init-local-00003"]
---

# iss-00134 Matt Pocock grill-style clarification workflow を spec-dock に取り込む — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

> `report.md` は観測証跡台帳（observed evidence ledger）です。planned requirements、evidence destination、closure 条件は `plan.md` が所有し、この文書は実際の Red / Green / Refactor evidence、発見された tests、closure delta、reviewer status、commit/no-op evidence を記録する。

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger / 必須）

`report.md` は実装中・文書更新中に発生した material な仕様解釈、判断、plan 逸脱、tradeoff、open question、promotion / follow-up を記録する audit trail でもある。worker の raw note や作業 transcript を貼る場所ではなく、orchestrator が source docs、diff、tests、reviewer output と照合して issue-level の canonical entry に統合する。

Material な判断がない場合もこの section は残し、判断なしであることを明示する。この issue では実装中判断が発生したため、下表に `D-IMPL-*` として記録する。

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
| D-IMPL-001 | resolved | implementation | dev-coder | `spec-dock-issue-planning` asset が managed skill catalog に未登録 | catalog 追加; tests 弱化; planning skill 不採用 | catalog へ追加 | AC-011 / cl-009 は shipped skill として install/update 対象化を要求 | applied | `src/spec_dock/cli.py`, `tests/test_init_update.py` | none |
| D-IMPL-002 | resolved | compatibility | parent | S90 で旧 `workflow_issue.md` execution-policy 正本参照を検出 | 放置; direct cleanup; follow-up issue | bounded cleanup と design/plan追補 | AC-010 / cl-007 / cl-009 の cleanup and split consistency に該当 | applied | provider docs + dogfooding mirror + tests | none |
| D-IMPL-003 | resolved | compatibility | code-reviewer | `workflow_issue_execution.md` が参照される実行 gate 定義を十分に持たず dangling policy reference になっていた | 旧定義を戻す; 参照を戻す; P1 を waiver | execution-only 正本に Parent Agent Invariant / Implementation Delegation Gate / reviewer gate mapping / final quality gate を復元 | split 後も `authoring/issue-plan.md` と `phase_plan_issue.md` の参照先が実体を持つ必要がある | applied | `src/spec_dock/assets/spec_dock/docs/workflow_issue_execution.md`, `spec-dock/docs/workflow_issue_execution.md`, `tests/test_init_update.py`, code-reviewer re-review pass | none |
| D-IMPL-004 | resolved | plan-alignment | spec-reviewer | installed role config edits が S04 target files に明示されていなかった | role config edits を戻す; design/plan に target と scope を追補; follow-up issue | design/plan に Codex / GitHub role config routing を S04 対象として追補 | role configs は `workflow_issue.md` umbrella と planning/execution source split を agent に伝える shipped guidance であり、AC-011 / cl-009 の一部 | applied | `design.md`, `plan.md`, role config files, final spec-reviewer pass | none |
| D-IMPL-005 | resolved | plan-alignment | spec-reviewer | S05/S06 の実差分に対して plan target / allowed paths が不足していた | out-of-scope diff を戻す; design/plan/report に随伴変更を追補; follow-up issue | `src/spec_dock/cli.py` catalog-only 変更、`tests/cli_runtime/harness.py` shared expectation、root `.codex` / `.github` installed mirror、active-none report mirror を S05/S06 対象として追補 | これらは `spec-dock-issue-planning` を配布対象にするための catalog / test support と、provider asset update の dogfooding mirror であり、AC-011 / cl-008 / cl-009 の実行に必要 | applied | `design.md`, `plan.md`, `report.md`, final spec-reviewer pass | none |
| D-IMPL-006 | resolved | provenance | spec-reviewer | adopted discussion evidence の frontmatter が current `disc` template の adoption semantics とずれていた | 放置; report で grandfathered と明記; frontmatter を current semantics に同期 | discussion frontmatter を `status: proposed`, `authority: proposed`, `adoption_status: adopted`, `reflected_to` ありに更新 | EAL-IMPL-004 で採用済み evidence として扱うため、source artifact 側も採用状態を読み取れる方が将来レビューで誤解されにくい | applied | `discussions/20260528t070322z-disc-deep-consultant-issue-planning-execution-split.md`, current frontmatter/report update evidence | none |
| D-IMPL-007 | resolved | compatibility | spec-reviewer | issue `plan.md` template に旧 `workflow_issue.md` execution-policy 正本参照が残っていた | 放置; provider template を修正; follow-up issue | provider issue plan template を `workflow_issue.md` umbrella、`workflow_issue_planning.md` authoring / planning、`workflow_issue_execution.md` execution / reviewer / completion policy へ同期 | issue plan template は future `plan.md` artifacts の seed であり、AC-010 / AC-011 / cl-009 の stale guidance cleanup 対象 | applied | `src/spec_dock/assets/spec_dock/templates/issue/plan.md`, `spec-dock/templates/issue/plan.md`, `tests/test_init_update.py`, final spec-reviewer pass | none |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-IMPL-001 | `adopted` | `doc-writer` | S01-S04 provider assets | approved plan の docs/templates/skills scope と一致 | changed provider assets, step spec-reviewer pass | none |
| EAL-IMPL-002 | `adopted` | `dev-coder` | S05 tests and catalog integration | tests は採用、production catalog gap は親が統合し code-reviewer pass 済み | `tests/*`, `src/spec_dock/cli.py`, final code-reviewer pass | none |
| EAL-IMPL-003 | `adopted` | command | S06 dogfooding mirror | local checkout update で provider assets を mirror へ反映 | `uv run python -m spec_dock.cli update .` | none |
| EAL-IMPL-004 | `adopted` | discussion | requirement / design / plan Issue planning-execution split | deep-consultant analysis が AC-011 / EC-006 と D-005、S04-S06 / S90 / S99 の分離設計へ反映された | `discussions/20260528t070322z-disc-deep-consultant-issue-planning-execution-split.md` | none |

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
  - 対象 scope の `discussions/` direct child にある flat Markdown
  - filename: `<ts>-<kind>-<slug>.md` または same-second collision 用 `<ts>-<nn>-<kind>-<slug>.md`
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
  - 既存 `iss-00126` などの manifest/Profile/probe/session artifacts は grandfathered evidence として残し、削除・rename・validation failure 化しない。

| ロール（created_by_role） | 範囲（scope_id） | ドラフトパス（discussion draft path） | 参照元（source_paths） | 予定反映先（intended_targets） | 採用状態（adoption_status） | 反映先（reflected_to） | 差分ガード結果（diff_guard_result） | 統合結果 | 採用しなかった部分 | ブロッカー | レビュー結果（reviewer result） | 昇格判断（promotion decision） |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | 未使用（not used） | なし（[]） | 未実行（not_run） | 手動 authoring | 該当なし | なし（none） | 該当なし | 委任ドラフト昇格なし |

### 委任ドラフトの失敗モード（Delegated Draft Failure Modes）
| 失敗モード | 期待される判定 | 許可される次アクション | レポート証跡の記録先（report evidence destination） | 昇格可否 |
|---|---|---|---|---|
| 同意なし（missing consent） | blocked / incomplete | 範囲付き同意を取得する、または手動 authoring に戻す | この section | ineligible |
| 前段 reviewer pass 不足 / stale（missing/stale previous reviewer pass） | blocked / incomplete | レビューゲートを再実行する（rerun reviewer gate） | レビューゲート証跡（Reviewer Gate Status / Final Spec Review Gate） | ineligible |
| 設計中の要件 gap（requirement gap during design） | blocked / incomplete | requirement phase へ戻す | 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger） | ineligible |
| 計画中の設計 gap（design gap during plan） | blocked / incomplete | design phase へ戻す | 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger） | ineligible |
| ロール利用不可（role unavailable） | blocked / manual path | 利用不可を記録し、妥当なら手動で続行する | この section | ineligible |
| 禁止行為の試行（forbidden action attempt） | rejected | ドラフトを破棄し incident を記録する | この section / decision ledger | ineligible |
| 古いドラフト（stale draft） | stale | 再生成または差分調整する | この section | ineligible |
| 置換済みドラフト（superseded draft） | superseded | 置換先ドラフトを参照する | この section | ineligible |
| 委任使用主張に対する証跡不足（missing draft evidence when delegated use is claimed） | incomplete | 証跡を追加する、または委任使用 claim を外す | この section | ineligible |
| reviewer 利用不可 / 拒否 / waiver / provisional（reviewer unavailable/denied/waived/provisional） | blocked / incomplete | fresh な passed reviewer を取得する、または昇格なしの risk acceptance を記録する | レビューゲート証跡（Reviewer Gate Status / Final Spec Review Gate） | ineligible |

## 仕様作成ゲート（Spec Authoring Gate）

`workflow_spec_authoring.md` に従い、requirement -> design -> plan の順で fresh `spec-reviewer` pass を得た。下表は実装開始前の handoff evidence であり、現在は implementation / final gate 実行中である。

| phase | artifact | reviewer | freshness | state | investigated facts | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| requirement | `requirement.md` | `spec-reviewer` | fresh | passed | discussions / prior analysis / Matt Pocock `grill-me` essence / spec-dock workflow constraints / Issue planning-execution split analysis | design phase へ進行可 | EC-003 の `disc.md` synthesis と issue `report.md` ledger の混同を修正後に pass。追加で AC-011 / EC-006 を反映し、planning は authoring + fresh reviewer pass、execution は approved plan 実行以降に分離する要件として pass |
| design | `design.md` | `spec-reviewer` | fresh | passed | requirement, workflow docs, template catalog, installed skill boundaries, frontmatter compatibility, Issue planning-execution split, issue report template handoff evidence | plan phase へ進行可 | formal question trigger、EC-002 re-question loop、root `.agents/skills` mirror、frontmatter compatibility を修正後に pass。追加で D-005 と issue `report.md` template の Spec Authoring Gate 変更対象化を反映後に pass |
| plan | `plan.md` | `spec-reviewer` | fresh | passed | requirement, design, `workflow_issue.md`, `workflow_spec_authoring.md`, `authoring/issue-plan.md`, `phase_plan_issue.md`, Issue planning-execution split, issue report Spec Authoring Gate | implementation handoff 可。ただし実装開始はユーザー提出後の明示指示待ち | S01/S02/S04/S05/S90 と report evidence destinations の指摘を修正後に pass。追加で cl-009、S04/S05/S06/S90/S99 への planning-execution split と report handoff coverage を反映後に pass |

### Reviewer Gate History

| phase | reviewer result | disposition |
|---|---|---|
| requirement | first review: fail / final review: pass | EC-003 の report artifact ambiguity を `disc.md` synthesis と `report.md` ledger に分離して解消 |
| design | multiple review cycles: fail -> pass | re-question loop、dogfooding path、external support artifact route、AC/EC verification mapping、formal question trigger、frontmatter compatibility を反映 |
| plan | multiple review cycles: fail -> pass | input docs、verification order、report/no-op gates、interview/disc full field contract、external evidence adoption、delegated-authoring verification、S90 inspect-only gate を反映 |
| requirement |追加 review cycle: pass | Issue planning / execution 分離を AC-011 / EC-006 として追加し、scope 外（runtime CLI split / lifecycle redesign / artifact auto migration / PR-finish redesign）を固定 |
| design |追加 review cycle: fail -> pass | `spec-dock-issue-planning` / `spec-dock-issue-execution`、`workflow_issue_planning.md` / `workflow_issue_execution.md`、issue `report.md` template の Spec Authoring Gate handoff evidence を設計対象に追加。初回 fail は report template target 不足、修正後 pass |
| plan |追加 review cycle: pass | S04/S05/S06/S90/S99 に AC-011 / EC-006、cl-009、new issue-planning skill、execution-only skill、hub routing、issue report Spec Authoring Gate assertion、runtime catalog unchanged を織り込み pass |

## 実装サマリー

provider-side の discussion templates / docs / installed skill guidance を、source-grounded clarification、一問一答の formal `interview`、common template catalog、Issue planning / execution 分離に合わせて更新した。新しい runtime discussion doc type は追加せず、`new doc` catalog は維持し、dogfooding mirror と root `.agents/skills` mirror を local checkout から同期した。

## 実装記録（セッションログ）

### セッションログ（2026-05-28 17:00 - 18:30）

#### 対象
- Step: S01, S02, S03, S04, S05, S06, S90
- AC/EC: AC-001 through AC-011, EC-001 through EC-006
- 計画上の出典:
  - `plan.md` sections: S01-S06, S90, S99
  - closure ids: `cl-001` through `cl-009`

#### 実施内容
- `doc-writer` が S01-S04 の provider-side templates / docs / skills を更新した。
- S01-S04 の step review で `workflow_issue.md` umbrella 化不足と draft `adr.md` の `authority: accepted` self-claim が指摘され、bounded follow-up で修正した。
- `dev-coder` が S05 の regression assertions を追加し、`spec-dock-issue-planning` provider asset が managed skill catalog に含まれていない blocker を Ledger Note として返した。
- 親 orchestrator が `src/spec_dock/cli.py` の managed skill catalog に `spec-dock-issue-planning` を追加し、dogfooding `.meta.json` snapshot と mirror asset map を実装範囲へ統合した。
- S90 inspection で旧 `workflow_issue.md` execution-policy 正本参照が周辺 docs に残っていることを検出した。編集は S04 の bounded follow-up として `design.md` / `plan.md` に対象を追補し、provider docs、installed entrypoints、dogfooding mirror、tests を同期した。
- code-reviewer final gate で、split 後の `workflow_issue_execution.md` に実行 gate 定義の実体が不足している P1 が見つかったため、旧 `workflow_issue.md` にあった Parent Agent Invariant / Implementation Delegation Gate / reviewer gate mapping / step commit / final quality gate を execution-only 正本へ復元し、dogfooding mirror と regression tests を更新した。

#### 実行コマンド / 結果
```bash
uv run python -m spec_dock.cli update .
# result: pass

python -m unittest tests.cli_runtime.test_runtime_new_doc_s09 -v
# result: OK, 16 tests

python -m unittest tests.domain_runtime.test_delegated_authoring -v
# result: OK, 23 tests

python -m unittest tests.cli_runtime.test_delegated_authoring -v
# result: OK, 49 tests

python -m unittest tests.test_init_update -v
# result: OK, 176 tests

python -m unittest discover -v
# result: OK, 959 tests

git diff --check
# result: pass

./spec-dock/scripts/spec-dock validate
# result: ok, nodes=68

./spec-dock/scripts/spec-dock sync
# result: ok, active unchanged, wrote index/tree/deps/dashboard artifacts
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ | フェーズ | 計画した証跡要件 | 観測した証跡 | 証跡手段 | 結果 | メモ |
|---|---|---|---|---|---|---|
| S01-S04 | 代替証跡 | inspect-only | templates / docs / skills diff inspection と `spec-reviewer` step review | docs inspection / reviewer | pass | S01-S04 初回 review fail 後に bounded follow-up |
| S05 | Red / characterization | changed shipped contracts を tests で固定 | old catalog expectation では new planning skill を検出できず、`test_init_update` snapshot が fail | `python -m unittest tests.test_init_update...` | pass after fix | managed skill catalog と dogfooding metadata snapshot を更新 |
| S05 | Green | targeted tests pass | `test_runtime_new_doc_s09`, delegated authoring tests, `test_init_update` が pass | unittest | pass | runtime new-doc catalog は unchanged |
| S06 | Green | dogfooding mirror parity | local checkout update 後、mirror parity tests / `git diff --check` / `spec-dock validate` / `spec-dock sync` が pass | `uv run python -m spec_dock.cli update .`, unittest, `git diff --check`, `./spec-dock/scripts/spec-dock validate`, `./spec-dock/scripts/spec-dock sync` | pass | `.venv` は update 後に削除 |
| S90 | Inspection | stale guidance / duplicate concept を検出 | 周辺 docs の stale `workflow_issue.md` execution-policy 参照を検出し、cleanup 後に `git diff --check` / `spec-dock validate` / `spec-dock sync` が pass | `rg` / diff inspection / `git diff --check` / `spec-dock validate` / `spec-dock sync` | pass | 変更は S04 bounded follow-up として design / plan に追補済み |
| S99 | Code review fix / full regression | execution policy dangling reference を解消し、統合差分を full regression で確認 | code-reviewer P1 指摘を受けて `workflow_issue_execution.md` に実行 gate 定義を復元し、content regression を追加。`python -m unittest discover -v` は 959 tests OK | code-reviewer re-review / unittest discover | pass | split 後の execution-only 正本が policy 実体を保持 |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ | 発見されたテスト / リスク | 起票元 | 実施した対応 | クロージャID / 新規ID | 計画修正要否 | 証跡 |
|---|---|---|---|---|---|---|
| S05 | `spec-dock-issue-planning` skill asset が provider にあるが managed catalog に未登録 | dev-coder Ledger Note | `_MANAGED_SKILL_NAMES` と tests / mirror snapshot を更新 | `cl-009` | no | `src/spec_dock/cli.py`, `tests/test_init_update.py` |
| S90 -> S04 follow-up | 旧 `workflow_issue.md` execution-policy 正本参照が周辺 docs / installed entrypoints / role configs に残存 | parent inspection / code-reviewer P2 | `design.md` / `plan.md` に S04 target を追補し、provider docs / installed entrypoints / role configs / dogfooding mirror / tests を更新 | `cl-007`, `cl-009` | yes, completed | `docs/README.md`, `phase_plan*.md`, `authoring/issue-plan.md`, `reference_*.md`, installed adapters/prompts, `spec-manager` / `spec-reviewer` configs |
| S99 code-review | `workflow_issue_execution.md` に実行 gate 定義の実体が不足 | code-reviewer P1 | execution-only 正本へ旧実行 policy を復元し、日本語 primary heading と regression assertion を追加 | `cl-007`, `cl-009` | no | `workflow_issue_execution.md`, `tests/test_init_update.py`, code-reviewer re-review pass |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ | クロージャID | 計画上の close 条件 | 観測した証跡 | 結果 | メモ |
|---|---|---|---|---|---|
| S01 | `cl-002`, `cl-003`, `cl-007` | `interview.md` が一問一答 formal lifecycle を表現 | template diff + shipped content tests | pass | runtime catalog 追加なし |
| S02 | `cl-001`, `cl-004`, `cl-007` | `research` / `disc` / `adr` semantics が分離 | template diff + shipped content tests | pass | `adr.md` self-claim は reviewer 指摘で修正 |
| S03 | `cl-004`, `cl-006`, `cl-007` | catalog / rules docs が common semantics に同期 | docs diff + mirror parity tests | pass | grill-specific duplicate template は追加なし |
| S04 | `cl-001`, `cl-002`, `cl-005`, `cl-006`, `cl-007`, `cl-009` | workflows / skills / report template が role boundary と split を案内 | docs/skills/prompts/role-config diff + shipped content tests + spec-reviewer step pass + code-reviewer re-review + final spec-reviewer pass | pass | `workflow_issue.md` は umbrella、`workflow_issue_execution.md` は execution policy 実体を保持。S90/code-reviewer findings は S04/S99 follow-up として整理 |
| S05 | `cl-001`-`cl-009` | targeted regression tests pass | 16 + 23 + 49 + 176 unittest pass | pass | `_MANAGED_SKILL_NAMES` 統合あり |
| S06 | `cl-008`, `cl-009` | dogfooding mirror / root skill mirror parity | local update + mirror tests + `git diff --check` + `spec-dock validate` + `spec-dock sync` pass | pass | `uv run python -m spec_dock.cli update .` |
| S90 | `cl-007`, `cl-008`, `cl-009` | stale guidance / duplicate concept が残らない | docs inspection; required edits were routed to amended S04/S99 follow-up; `git diff --check` / `spec-dock validate` / `spec-dock sync` pass | pass | S90 自体は inspect-only gate として維持 |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID | ステップ | 必須 | 証跡レベル | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ |
|---|---|---|---|---|---|---|---|
| `cl-001` | S02/S04/S05 | yes | inspect-only + regression | old template assertions insufficient | `python -m unittest tests.test_init_update -v` | pass | source-grounding fields covered |
| `cl-002` | S01/S04/S05 | yes | inspect-only + regression | old interview template multi-field but not one-question lifecycle | `python -m unittest tests.test_init_update -v` | pass | unanswered / answered lifecycle covered |
| `cl-003` | S01/S05 | yes | inspect-only + regression | old template did not require answer completion fields | `python -m unittest tests.test_init_update -v` | pass | same artifact completion covered |
| `cl-004` | S02/S03/S05 | yes | inspect-only + regression | old `disc` contract mixed concerns | `python -m unittest tests.test_init_update -v` | pass | synthesis / ADR triage covered |
| `cl-005` | S04/S05 | yes | inspect-only + regression | specialist direct-question boundary needed assertion | `python -m unittest tests.test_init_update -v` | pass | specialist returns question candidates |
| `cl-006` | S03/S04/S05 | yes | inspect-only + regression | external evidence adoption needed template/report path | `python -m unittest tests.test_init_update -v` | pass | Evidence Adoption / Spec Authoring Gate covered |
| `cl-007` | S01-S05/S90 | yes | inspect-only + regression | accidental doc type expansion risk | `python -m unittest tests.cli_runtime.test_runtime_new_doc_s09 -v` | pass | `report` / `reflection` remain unsupported doc types |
| `cl-008` | S06/S90/S99 | yes | manual-required | provider/dogfood drift possible after update | `python -m unittest tests.test_init_update -v`; `python -m unittest discover -v`; `git diff --check`; `./spec-dock/scripts/spec-dock validate`; `./spec-dock/scripts/spec-dock sync` | pass | mirror parity and full regression covered |
| `cl-009` | S04/S05/S06 | yes | inspect-only + regression | planning skill asset initially absent from managed catalog | `python -m unittest tests.test_init_update -v` | pass | planning/execution split covered |

#### クロージャ網羅（Closure Coverage）
| クロージャID | ステップ | 検証証跡 | 観測結果 | メモ |
|---|---|---|---|---|
| `cl-001` | S02/S04/S05 | templates/docs/tests | pass |  |
| `cl-002` | S01/S04/S05 | templates/docs/tests | pass |  |
| `cl-003` | S01/S05 | template/tests | pass |  |
| `cl-004` | S02/S03/S05 | templates/catalog/tests | pass |  |
| `cl-005` | S04/S05 | skill/docs/tests | pass |  |
| `cl-006` | S03/S04/S05 | report/workflow/tests | pass |  |
| `cl-007` | S01-S05/S90 | runtime catalog tests + docs inspection | pass | no new doc type |
| `cl-008` | S06/S90/S99 | local update + mirror tests + `git diff --check` + `spec-dock validate` + `spec-dock sync` | pass | dogfooding synced |
| `cl-009` | S04/S05/S06 | workflow/skill tests | pass | split shipped |

#### クロージャ差分（Closure Delta）
| 変更種別 | クロージャID | テストID alias | 解決先クロージャID | 理由 | 計画修正要否 | 再レビュー要否 |
|---|---|---|---|---|---|---|
| none | `cl-001`-`cl-009` | N/A | same | closure ids unchanged | no | final reviewers only |

#### ワークフロー委任同意の証跡（Workflow Delegation Consent）
| 同意元 | リポジトリ / worktree | 対象課題 | セッション | 指名ロール | 境界 | 期限 / 無効化条件 | 拒否 / 利用不可理由 | 次アクション |
|---|---|---|---|---|---|---|---|---|
| user instruction + approved `plan.md` delegation contract | current worktree | `iss-00134` | current session | `doc-writer`, `dev-coder`, `spec-reviewer`, `code-reviewer`, `qa-reviewer` | same repo, active issue, named roles; no destructive action / credentialed external system expansion | issue complete / session end / scope change | none | proceed |

#### 実装委任ゲート（Implementation Delegation Gate）
| ステップ | 判断 | 必須理由 | 委任ロール | 委任範囲 | 正本 | 許可変更 | 禁止変更 | 必須検証 | 停止条件 | 必須出力 | 観測結果 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01-S04 | delegated | shipped docs/templates/skills | `doc-writer` | provider-side assets | `plan.md` S01-S04 | listed target files | runtime/tests | docs inspection / S05 tests | policy scope expansion | changed files + Ledger Note | pass |
| S05 | delegated | tests / scaffold behavior | `dev-coder` | test files + catalog-only integration | `plan.md` S05 | listed tests, `tests/cli_runtime/harness.py`, `src/spec_dock/cli.py` catalog-only change | provider docs/templates/skills unless approved; runtime command/lifecycle changes | targeted unittest | runtime behavior change beyond managed skill catalog needed | changed files + Ledger Note | pass with parent integration |
| S06 | approved-local-execution | dogfooding command operation | parent | local update / parity | `plan.md` S06 | dogfooding scaffold mirror + root installed mirror listed in S06 | arbitrary source update; unlisted `.codex` / `.github` | local update + tests | update failure | command output | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ | 委任ロール | 委任 worker 要約 | 変更ファイル | 実行 tests または docs-only 検証 | レビュアー判定 | 未解決リスク | 親統合判断 |
|---|---|---|---|---|---|---|---|
| S01-S04 | `doc-writer` | provider-side templates / docs / skills を更新 | provider templates/docs/skills | docs-only inspection | initial fail -> final pass | none | accepted after bounded fixes |
| S05 | `dev-coder` | template/docs/skill/runtime-catalog regression tests を追加 | `tests/test_init_update.py`, `tests/cli_runtime/test_runtime_new_doc_s09.py`, `tests/cli_runtime/harness.py` | targeted/full unittest pass after integration | final code-reviewer pass | managed catalog gap resolved | accepted with parent integration |

#### 親実装例外（Parent Implementation Exception）
| ステップ | 委任不可 / 不可能理由 | ユーザー承認 / risk acceptance | 許可ファイル | 許可操作 | ロールバック計画 | 変更後検証 | レビューゲート | 利用不可 / 拒否 / host conflict / waiver 対応 |
|---|---|---|---|---|---|---|---|---|
| S05 | dev-coder Ledger Note が production catalog gap を返し、親が issue-wide contract と worker diff を統合する必要があった | user requested full issue execution; risk accepted: no extra behavior beyond shipped skill catalog | `src/spec_dock/cli.py`, `tests/test_init_update.py`, `tests/cli_runtime/harness.py` | add `spec-dock-issue-planning` to managed skill catalog and dogfooding snapshot expectations | revert catalog/test additions if reviewer fails | targeted unittest + full `test_init_update` pass + full discover pass | code-reviewer pass; final spec-reviewer pass | no waiver |
| S04/S99 follow-up | S90/code-reviewer inspection で stale workflow reference / dangling execution policy が見つかり、計画追補と bounded cleanup が必要になった | user requested full issue execution; plan/design amendment recorded | active `design.md`, active `plan.md`, provider docs, installed entrypoints, dogfooding mirror, root `.codex` / `.github` installed mirror, `tests/test_init_update.py` | synchronize stale workflow references and restore execution policy definitions | revert docs/test changes if spec-reviewer fails | targeted/full unittest pass | code-reviewer pass; final spec-reviewer pass | no waiver |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ | ゲート名 | レビュアーロール | 鮮度 | 状態 | リスク受容 | 昇格 / 完了判断 | メモ |
|---|---|---|---|---|---|---|---|
| S01-S04 | step reviewer | `spec-reviewer` | fresh | passed | no | proceed | first review failed, bounded fixes applied, final pass |
| S05 | step reviewer | `code-reviewer` | fresh | passed | no | proceed | final integrated diff review pass |
| S90 | docs impact reviewer | `code-reviewer` | fresh | passed | no | proceed to final spec-reviewer | stale reference P2 and dangling execution policy P1 were fixed, then re-review passed |
| S99 | final spec reviewer | `spec-reviewer` | fresh | passed | no | proceed to commit / PR | final rerun findings none |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ | クロージャ状態 | コミット範囲 | コミットハッシュ / 最終台帳 | コミット後 clean 確認 | 差分なし根拠 | 差分なし確認済み契約 / ファイル | 差分なし diff-clean コマンド | 差分なし read-only 確認 |
|---|---|---|---|---|---|---|---|---|
| S01-S06/S90 | committed | integrated issue diff | final commit hash is external evidence in PR / final response | clean check after commit | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/templates/discussions/*.md` - common discussion template semantics
- `src/spec_dock/assets/spec_dock/docs/**/*.md` - workflow / catalog / reference guidance
- `src/spec_dock/assets/spec_dock/docs/workflow_issue_planning.md`, `src/spec_dock/assets/spec_dock/docs/workflow_issue_execution.md` - split Issue planning / execution正本
- `src/spec_dock/assets/spec_dock/templates/issue/report.md` - Spec Authoring Gate
- `src/spec_dock/assets/install_root/.agents/skills/**/SKILL.md` - planning/execution skill routing
- `src/spec_dock/cli.py` - managed skill catalog
- `tests/test_init_update.py`, `tests/cli_runtime/test_runtime_new_doc_s09.py`, `tests/cli_runtime/harness.py` - regression coverage
- `.agents/skills/**`, `.codex/**`, `.github/agents/spec-manager.agent.md`, `spec-dock/docs/**`, `spec-dock/templates/**`, `spec-dock/system/**` - dogfooding mirror / root installed mirror

#### コミット
- committed; final commit hash is reported in PR / final response.

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 対象 | 更新要否 | 担当 | 証跡 | 仕様レビュアー結果 |
|---|---|---|---|---|
| docs / templates / README / workflow / skill / reference docs | yes | parent + `doc-writer` | provider docs/templates/skills update, dogfooding mirror update, S90 inspection -> S04/S99 follow-up cleanup, code-reviewer re-review pass | passed |

### 最終 QA ゲート（Final QA Gate）
| レビュアー | 範囲 | 統合テスト判断 | 証跡 | 結果 |
|---|---|---|---|---|
| `qa-reviewer` | whole issue obligation coverage | targeted regression suite added / sufficient | review_status pass。P2: `git diff --check` / `validate` / `sync` evidence を report に記録すべき -> 反映済み | passed |

### 最終コードレビューゲート（Final Code Review Gate）
| レビュアー | 範囲 | 指摘 / 修正 | 再 review 回数 | 結果 |
|---|---|---|---|---|
| `code-reviewer` | issue-wide integrated diff | initial P1: `workflow_issue_execution.md` に execution gate 定義不足 -> 復元。re-review findings none | 1 | passed |

### 最終 spec review ゲート（Final Spec Review Gate）
| レビュアー | 範囲 | 指摘 / 修正 | 再 review 回数 | 結果 |
|---|---|---|---|---|
| `spec-reviewer` | requirement / design / plan / report / implementation / tests / docs alignment | initial P1/P2 findings were fixed; final rerun findings none | 4 | passed |

### 最終 commit（Final Commit）
| 最終 report 台帳 | 最終 commit 範囲 | コミット後の外部証跡送付先 | 結果 |
|---|---|---|---|
| committed | integrated issue diff | PR / final response | committed; PR delivery follows |

## 遭遇した問題と解決
- 問題: `./spec-dock/scripts/spec-dock update .` は installed upstream wrapper を使うため、local checkout の provider asset diff を dogfooding mirror に反映しない。
  - 解決: `uv run python -m spec_dock.cli update .` を使い、local provider assets から同期した。

## 今後の推奨事項
- final reviewers が pass した後、commit / PR / merge-preparation evidence をこの report に追記して issue finish へ進める。

## 省略/例外メモ
- S01-S04 の step commit は、実行中の追加 scope clarification と S05/S06 integration が続いたため未分割。最終 commit は integrated issue diff として作成し、Parent Implementation Exception に統合理由を残す。
