---
種別: 実装報告書（Issue）
ID: "iss-00252"
タイトル: "Compile Grade Aware Issue Planning Guidance"
関連GitHub: ["#252"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00252 Compile Grade Aware Issue Planning Guidance — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

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
| D-001 | resolved | test-strategy / evidence-ledger | spec-reviewer | Decision Ledger のテンプレート行が未解決 decision に見える | placeholder を残す; explicit no_action として閉じる | 実装判断は既存 plan / ADR に従っており、新規 durable decision はない。placeholder は削除し、no_action として閉じる。 | report evidence ledger の曖昧さを残さないため | no_action | spec-reviewer finding; this row | none |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | sub-agent / doc-writer | provider/dogfooding docs and issue-planning skill | S01〜S03 の grade-aware authoring guidance は docs-only wording であり、親が diff、provider/dogfooding parity、required wording、validate、lint、focused pytest を確認したため採用する。runtime code、templates、active issue requirement/design/plan、G2/G3/G4 implementation は採用対象外。 | worker summary; `diff -u`; `rg`; `git diff --check`; `./spec-dock/scripts/spec-dock validate`; `make lint`; `uv run pytest tests/cli_runtime/test_workflow.py tests/unit/domain/test_workflow_state.py` | fresh reviewer re-review |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | G1 の主目的は Issue grade 別 authoring matrix、Lite non-default、unknown fallback、`authorized_profile` authority、specialist fallback、G2/G3/G4 stable terms を docs / skill guidance に固定すること。S01〜S03 / C-001〜C-005 と `rg` / parity / reviewer pass で確認。 | docs-only 実装として provider/dogfooding parity、report evidence、reviewer gate、focused pytest、lint、validate を副次要件として実施。runtime routing、report validation、smoke implementation は G2/G3/G4 へ残した。 | low | pass: QA/code/spec re-review passed; P2 OAL cleanup applied before final report cleanup |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement/design/plan | Epic #224 requirement/design/plan、ADR `20260630t111316z`、`iss-00251` completion result、`./spec-dock/scripts/spec-dock guidance issue-planning`、fresh spec-reviewer fail/pass findings | blocking question なし。G1 は grade-aware authoring rules を docs / skill guidance に落とし、G2 / G3 / G4 の runtime routing / evidence enforcement / smoke は対象外にする。 | requirement/design/plan を approved に昇格。review fail findings を受け、plan に step-local source/paths/verification/reviewer/report destination、Spec-Locked Closure Index、三者 final quality gate、Parent Implementation Exception 境界、P0/P1 vs P2/P3 review semantics を追加した。 | passed: fresh `spec-reviewer` returned findings none / `review_status: pass` / confidence 0.90. Re-review agents: Hubble, Hypatia, Feynman, Copernicus, Pauli. | no | promote to issue execution |

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

## 実装サマリー (任意)
- G1 grade-aware issue planning guidance を provider / dogfooding docs と issue-planning skill に追加した。
- Lite non-default、unknown grade fallback、`authorized_profile` hard stop、specialist fallback、G2/G3/G4 stable terms を文書化し、runtime / template 実装は G2〜G4 の対象として残した。

## 実装記録（セッションログ） (必須)

### セッションログ（2026-07-01 G1 実装）

#### 対象
- Step: S00, S01, S02, S03, S90, S95, S99
- AC/EC: AC-001, AC-002, AC-003, AC-004, AC-005, AC-006, AC-007
- 計画上の出典（Planned source）:
  - `plan.md` section: `7. 実装ステップ / 実行ステップ契約（Executable Step Contract）`
  - closure ids: C-001, C-002, C-003, C-004, C-005, C-090, C-095, C-099

#### 実施内容
- S00: 現行 provider / dogfooding docs と issue-planning skill を調査し、grade-aware authoring matrix は未整備、fresh reviewer / delegated evidence / direct-write draft policy は既に存在することを確認した。
- S01〜S03: shipped docs / skill wording の編集は `doc-writer` に委任した。
- S01〜S03: doc-writer output を親側で確認し、provider / dogfooding mirror parity、required wording、lint、validate を検証した。

#### 実行コマンド / 結果
```bash
rg -n "Lite|Standard|Strict|Critical|authorized_profile|manual escalation|specialist|fallback|report evidence|draft routing|integrated smoke|grade" \
  src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md \
  src/spec_dock/assets/spec_dock/docs/phase_requirement.md \
  src/spec_dock/assets/spec_dock/docs/phase_design.md \
  src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md \
  src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md \
  spec-dock/docs/workflow_spec_authoring.md \
  spec-dock/docs/phase_requirement.md \
  spec-dock/docs/phase_design.md \
  spec-dock/docs/phase_plan_issue.md \
  .agents/skills/spec-dock-issue-planning/SKILL.md

pass: reviewer / delegated draft / report evidence / compose profile wording は存在するが、G1 の grade matrix、Lite non-default、unknown fallback、authority split、specialist fallback、G2/G3/G4 stable wording は散在または不足。
```

```bash
diff -u src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md spec-dock/docs/workflow_spec_authoring.md
diff -u src/spec_dock/assets/spec_dock/docs/phase_requirement.md spec-dock/docs/phase_requirement.md
diff -u src/spec_dock/assets/spec_dock/docs/phase_design.md spec-dock/docs/phase_design.md
diff -u src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md spec-dock/docs/phase_plan_issue.md
diff -u src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md .agents/skills/spec-dock-issue-planning/SKILL.md

pass: no output; provider / dogfooding mirror parity confirmed.
```

```bash
rg -n "Issue grade 別 authoring matrix|Lite は automatic default|unknown / ambiguous|Standard 以上|authorized_profile|manual escalation|specialist|manual fallback|draft routing|report evidence gate|integrated smoke matrix" <provider-and-dogfooding-docs-and-skill>

pass: required wording exists in provider and dogfooding surfaces.
```

```bash
git diff --check
./spec-dock/scripts/spec-dock validate
make lint
uv run pytest tests/cli_runtime/test_workflow.py tests/unit/domain/test_workflow_state.py

pass: diff check clean; validate nodes=160; ruff check / ruff format check / mypy pass; focused pytest 40 passed.
```

```bash
diff -u src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md .agents/skills/spec-dock-issue-planning/SKILL.md

pass: no output after reviewer fix; provider / dogfooding skill mirror parity confirmed.
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S00 | 代替証跡（inspect-only） | baseline owner surface と wording gap | provider / dogfooding docs、issue-planning skill を確認 | `rg` / file inspection | pass | 実装変更なし |
| S01 | 代替証跡（inspect-only） | grade matrix / Lite non-default / authority split gap | grade matrix は未整備、`authorized_profile` は compose文脈に限定 | `rg` / file inspection | pass | doc-writer に実装委任 |
| S02 | 代替証跡（inspect-only） | specialist / fallback wording gap | reviewer / delegated draft policy はあるが grade別 specialist fallback は未整備 | `rg` / file inspection | pass | doc-writer に実装委任 |
| S03 | 代替証跡（inspect-only） | downstream stable wording gap | direct-write draft / report evidence はあるが G2/G3/G4 stable terms は未整備 | `rg` / file inspection | pass | doc-writer に実装委任 |
| S01 | 緑フェーズ（Green） | grade matrix / Lite non-default / authority split | docs / skill に required wording を追加 | `rg` / parity inspection | pass | C-001〜C-003 |
| S02 | 緑フェーズ（Green） | specialist / fallback wording | docs / skill に Standard / Strict / Critical specialist rule と fallback evidence を追加 | `rg` / parity inspection | pass | C-004 |
| S03 | 緑フェーズ（Green） | downstream stable wording | `draft routing` / `report evidence gate` / `integrated smoke matrix` stable terms を追加 | `rg` / parity inspection | pass | C-005 |
| S90 | 緑フェーズ（Green） | provider / dogfooding parity | provider と dogfooding mirror が一致 | `diff -u` / validate | pass | C-090 |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S00 | docs / skill の既存 wording は delegated draft policy に寄っており、grade matrix が不足 | baseline inspection | G1 implementation target として記録 | C-001〜C-005 | no | `rg` inspection |
| S01〜S03 | skill 本体の既存見出しは英語のまま残る | doc-writer | 追加部分は日本語本文に寄せ、既存 skill 見出し全体の日本語化は scope 外として記録 | C-001〜C-005 | no | worker summary |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S00 | C-001〜C-005 | baseline owner surface と wording gap が report にある | `rg` inspection | pass | S01〜S03 は doc-writer に委任 |
| S01 | C-001〜C-003 | grade matrix / Lite non-default / authority split が docs / skill にある | `rg` / parity inspection | pass | provider / dogfooding mirror 確認済み |
| S02 | C-004 | specialist recommended / required / fallback evidence wording がある | `rg` / parity inspection | pass | Standard / Strict / Critical を確認 |
| S03 | C-005 | G2 / G3 / G4 stable terms がある | `rg` / parity inspection | pass | draft routing / report evidence gate / integrated smoke matrix |
| S90 | C-090 | provider / dogfooding docs and skill parity | `diff -u` no output; validate pass | pass | source of truth は provider 側 |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| tc-s00-001 | S00 | yes | inspect-only | grade-aware matrix不足 | `rg` inspection | pass | owner surface と gap を固定 |
| tc-s01-001 | S01 | yes | inspect-only | grade matrix 不足 | `rg` / parity inspection | pass | C-001 |
| tc-s01-002 | S01 | yes | inspect-only | Lite default / unknown fallback wording 不足 | `rg` / parity inspection | pass | C-002 |
| tc-s01-003 | S01 | yes | inspect-only | authority split wording 不足 | `rg` / parity inspection | pass | C-003 |
| tc-s02-001 | S02 | yes | inspect-only | Standard specialist skip reason wording 不足 | `rg` / parity inspection | pass | C-004 |
| tc-s02-002 | S02 | yes | inspect-only | Strict/Critical fallback evidence wording 不足 | `rg` / parity inspection | pass | C-004 |
| tc-s03-001 | S03 | yes | inspect-only | downstream stable terms 不足 | `rg` / parity inspection | pass | C-005 |
| tc-s90-001 | S90 | yes | inspect-only | mirror parity | `diff -u`; validate | pass | C-090 |

- `closure id / test id` は Spec-Locked Closure Index の `id` を指す。別 alias を使う場合は `Closure Delta` で対応を記録する。

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| C-001〜C-005 | S00 | baseline `rg` inspection | pass | 実装後に S01〜S03 で個別 closure を更新する |
| C-001 | S01 | docs / skill `rg` inspection | pass | grade matrix |
| C-002 | S01 | docs / skill `rg` inspection | pass | Lite non-default / unknown fallback |
| C-003 | S01 | docs / skill `rg` inspection | pass | authority split |
| C-004 | S02 | docs / skill `rg` inspection | pass | specialist / fallback evidence |
| C-005 | S03 | docs / skill `rg` inspection | pass | G2/G3/G4 stable terms |
| C-090 | S90 | provider/dogfooding `diff -u`; validate | pass | mirror parity |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none | C-001〜C-090 | tc-s00-001〜tc-s90-001 | C-001〜C-090 | 計画された closure で充足 | no | S95 final spec review required |

#### ワークフロー委任同意の証跡（Workflow Delegation Consent）
`workflow_issue.md` is the policy source for workflow-scoped delegation consent. This report records observed consent, boundary, expiry, and denied / unavailable handling only.

| 同意元（consent source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可理由（denied / unavailable reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user instruction / workflow issue execution | `/Volumes/990p2t/offloaded/home/iwasawayuuta/.codex/worktrees/cdfe/spec-dock` | iss-00252 | current session | doc-writer / spec-reviewer / code-reviewer / qa-reviewer | same repo, active issue, session, named role; no destructive action / publishing / credentialed access / scope expansion beyond allowed paths | issue complete / session end / scope change / host policy conflict / user revocation | none | proceed |

#### 実装委任ゲート（Implementation Delegation Gate）
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records observed evidence only.

| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01〜S03 | delegated | shipped docs / skill wording change | doc-writer | G1 grade-aware issue planning wording | active issue docs、ADR、Epic #224 docs | provider/dogfooding docs and issue-planning skill allowed paths | runtime code、tests、templates、G2/G3/G4 implementation、canonical issue docs | docs inspection、provider/dogfooding parity、rg | scope expansion / forbidden path / implementation need | changed files、verification、risks | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S01〜S03 | doc-writer | G1 grade-aware docs/skill wording を追加。runtime code、tests、templates、active issue requirement/design/plan、G2/G3/G4 実装は未変更。 | provider/dogfooding workflow_spec_authoring、phase_requirement、phase_design、phase_plan_issue、issue-planning skill | `rg`; `diff -u`; `git diff --check`; `./spec-dock/scripts/spec-dock validate` | pending final reviewers | 既存 skill 見出し全体の日本語化は scope 外 | accepted |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| S01〜S03 | N/A | N/A | N/A | N/A | N/A | delegated doc-writer path used | final reviewers pending | N/A |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S95 | first final QA review | qa-reviewer | fresh | fail | no | blocked until fix | P1: 初回時点では final reviewer gates の完了証跡が未記録; Evidence Adoption Ledger missing concrete delegated adoption entry |
| S95 | first final code review | code-reviewer | fresh | fail | no | blocked until fix | P1: `authorized_profile` stop condition too weak; Evidence Adoption Ledger missing concrete delegated adoption entry |
| S95 | first final spec review | spec-reviewer | fresh | fail | no | blocked until fix | P1: Evidence Adoption Ledger missing concrete delegated adoption entry; P2: final quality gate placeholders pending |
| S95 | reviewer fix | orchestrator | current | fixed | no | re-review required | Split `authorized_profile` hard stop from grade Standard+ escalation; added EAL-001 adopted entry; reran parity, validate, lint, focused pytest |
| S95 | final QA re-review | qa-reviewer | fresh | pass | no | pass | No P0/P1 QA findings remain; docs-only verification judged adequate |
| S95 | final code re-review | code-reviewer | fresh | pass | no | pass | `authorized_profile` hard stop and EAL evidence accepted; diff remained docs/skill/report scoped |
| S95 | final spec re-review | spec-reviewer | fresh | pass | no | pass | D-001 resolved/no_action; EAL and AC/EC closure accepted. P2 OAL cleanup was applied before final cleanup |

#### マイルストーン / commit 候補ゲート（Milestone / Commit Candidate Gate）
| マイルストーン / step | クロージャ状態（closure state） | コミット候補 / コミット範囲（commit candidate / scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S00 | completed | baseline evidence only | N/A | N/A | inspect-only | provider/dogfooding docs and skill | N/A | `rg` inspection |
| S01〜S90 | committed | docs / skill wording and parity | `9d172bff` docs(workflow): issue planningにgrade別authoring方針を追加 / `180578ea` docs(issue-planning): iss-00252のレビュー証跡を補足 | `git status --short` clean after checkpoint commit / issue finish completed | N/A | provider/dogfooding docs and skill | N/A | `rg`; `diff -u`; validate; lint; focused pytest |
| S95 | completed | final reviewer evidence | N/A | N/A | review-only | report reviewer gate records | N/A | QA/code/spec re-review pass |
| S99 | committed | final issue checkpoint | `180578ea` docs(issue-planning): iss-00252のレビュー証跡を補足 | issue finish completed; Epic baton continued without per-issue PR | N/A | docs / skill / report diff | N/A | final quality gate pass |

#### 変更したファイル
- `report.md` - S00 baseline / delegation evidence
- `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md` - grade matrix / authority split / downstream stable terms
- `src/spec_dock/assets/spec_dock/docs/phase_requirement.md` - requirement grade guidance
- `src/spec_dock/assets/spec_dock/docs/phase_design.md` - design specialist / fallback guidance
- `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md` - plan specialist / downstream term guidance
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md` - issue-planning first-read / stop condition guidance
- dogfooding mirrors under `spec-dock/docs/` and `.agents/skills/spec-dock-issue-planning/SKILL.md`

#### コミット
- committed: `9d172bff` docs(workflow): issue planningにgrade別authoring方針を追加
- committed: `180578ea` docs(issue-planning): iss-00252のレビュー証跡を補足

#### メモ
- Per-issue PR は作成しない。Epic #224 の最終 PR にバケツリレー方式で引き継ぐ。

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| docs / workflow / skill | yes | doc-writer + orchestrator adoption | provider/dogfooding docs and skill diff; EAL-001; parity `diff -u`; required wording `rg`; validate | pass |
| templates / README / migration notes | no | N/A | G1 scope is wording guidance only; runtime routing / report validation / smoke implementation deferred to G2/G3/G4 | pass |

### 最終 QA ゲート（Final QA Gate）
| レビュアー（reviewer） | 範囲 | 統合テスト判断（integration test decision） | 証跡（evidence） | 結果（result） |
|---|---|---|---|---|
| qa-reviewer | whole issue obligation coverage | already sufficient for docs-only G1 | `git diff --check`; `./spec-dock/scripts/spec-dock validate`; `make lint`; `uv run pytest tests/cli_runtime/test_workflow.py tests/unit/domain/test_workflow_state.py`; provider/dogfooding parity | pass |

### 最終コードレビューゲート（Final Code Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| code-reviewer | issue-wide integrated diff | P1 `authorized_profile` hard stop weakness and EAL missing were fixed; provider/dogfooding mirror parity retained | 1 | pass |

### 最終 spec review ゲート（Final Spec Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| spec-reviewer | requirement / design / plan / report / implementation / tests / docs alignment | P1 EAL missing and D-001 placeholder were fixed; P2 OAL placeholder was cleaned before final cleanup | 2 | pass |

### 最終 commit（Final Commit）
| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| S00〜S99 closure, EAL, OAL, reviewer pass, validation commands recorded | provider/dogfooding docs and issue-planning skill; issue report | Epic baton / final Epic PR evidence | committed: `180578ea`; no per-issue PR |

## 遭遇した問題と解決 (任意)
- 問題: 初回 reviewer gate で Evidence Adoption Ledger と final reviewer evidence の不足が見つかった。
  - 解決: EAL-001 と S95 reviewer gate / final quality gate 証跡を追加し、final QA / code / spec re-review で pass を得た。

## 学んだこと (任意)
- docs-only の G1 でも、委任証跡と reviewer gate の完了状態は report 上で明示しないと Epic final gate で監査不能になる。

## 今後の推奨事項 (任意)
- 後続 issue でも Epic 単一 PR 方針に従い、issue 完了時は checkpoint commit と report 証跡だけを残し、PR 作成は Epic 最終品質ゲートに集約する。

## 省略/例外メモ (必須)
- 該当なし
