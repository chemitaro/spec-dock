---
種別: 実装報告書（Issue）
ID: "iss-00227"
タイトル: "Introduce Assurance Contract And Classification Runtime"
関連GitHub: ["#227"]
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00227 Introduce Assurance Contract And Classification Runtime — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

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
| D-001 | resolved | compatibility | spec-reviewer | `assurance verify` の missing contract exit behavior が未固定 | missing を exit 1; missing を strict-legacy exit 0 | missing `assurance.json` は strict-legacy candidate として exit 0、invalid JSON/schema は exit 1 | Existing Issue compatibility を守り、corruption detection と missing compatibility を分離するため | promoted_to_design | `design.md` インターフェース契約 / Schema validation v1 | なし |
| D-002 | resolved | implementation | spec-reviewer | `source_binding.path` が `active/issue` symlink path だと durable stale detection に不向き | active path を保存; resolved path を保存; 両方保存 | persisted `path` は resolved issue-local repo-relative path、`display_path` は optional active path | 後続 stale detection が mutable pointer に依存しないようにするため | promoted_to_design | `design.md` `assurance.json` v1 contract | なし |
| D-003 | resolved | test-strategy | spec-reviewer | hard-trigger / Lite predicate policy matrix が未固定 | 実装者判断; compact policy table | v1 deterministic classification policy table を設計に固定 | deterministic JSON と reviewable tests を実装者判断にしないため | promoted_to_design | `design.md` Deterministic classification policy v1 | なし |
| D-004 | resolved | implementation | spec-reviewer | requirement が explicit issue path を要求する一方、design が v1 path target を拒否していた | requirement を縮小; design で path target 対応 | v1 `--issue` は issue id / GitHub number / repo-contained filesystem issue path を受け付け、explicit target が active issue より優先する | Approved requirement を design で弱めないため | promoted_to_design | `design.md` インターフェース契約 | なし |
| D-005 | resolved | implementation | spec-reviewer | `RiskFact` domain model と schema validation table の fields が不一致 | key/value のみ保存; source/reason_code も保存 | v1 persisted `risk_facts[]` は `key`、`value`、`source`、`reason_code` を必須にする | Store / validator / audit expectation を一致させるため | promoted_to_design | `design.md` Schema validation v1 | なし |
| D-006 | resolved | implementation | spec-reviewer | v1 classification の RiskFact derivation が未固定 | requirement text から自然言語抽出; 全 fact unknown/default; empty facts を許容 | v1 public CLI は自然言語抽出を行わず、全 supported fact を deterministic default で出力する | byte-identical output と安全な unknown fail-closed を優先するため | promoted_to_design | `design.md` RiskFact derivation v1 | 後続 Issue で structured fact extraction を検討 |
| D-007 | resolved | implementation | spec-reviewer | `proposed_profile` の意味が未固定 | `lite_candidate` と別に定義; `authorized_profile` と同一に固定; v1 から削除 | v1 persisted schema から `proposed_profile` を削除し、`lite_candidate` と `authorized_profile` に集約する | downstream interpretation と deterministic schema を単純化するため | promoted_to_design | `design.md` `assurance.json` v1 contract / Schema validation v1 | なし |
| D-008 | resolved | implementation | spec-reviewer | default classification example が unknown protected facts / reason codes を欠いていた | 例を簡略化; canonical default fixture を明記 | default JSON 例に protected-domain unknown facts、全 default fact reason code、policy consequence reason code を stable sort で明示する | plan / tests が fail-closed audit signal を落とさないため | promoted_to_design | `design.md` RiskFact derivation v1 / `assurance.json` v1 contract | なし |
| D-009 | resolved | implementation | spec-reviewer | `proposed_profile` が unknown field として許可され得る | unknown fields 全許可; classification 配下は strict | `classification` / `risk_facts[]` 配下の unknown fields は v1 invalid とし、semantics-neutral fields だけ限定許可する | 二重 profile authority を防ぐため | promoted_to_design | `design.md` Schema validation v1 | なし |
| D-010 | resolved | test-strategy | spec-reviewer | canonical plan が step-local delegation contract / evidence / closure gate を十分に持っていなかった | supporting draft を参照に留める; canonical plan に詳細を復元 | S01-S04/S90/S99 に delegated role、input docs、acceptance criteria、required output、reviewer focus、stop conditions、Red evidence、refactor guardrail、closure/commit gate を追加 | Worker / reviewer が canonical plan だけで実行判断できるようにするため | promoted_to_plan | `plan.md` S01-S04/S90/S99 step contracts | fresh plan re-review |
| D-011 | resolved | test-strategy | spec-reviewer | canonical plan の concrete tests が card schema ではなく一行要約だった | 一行要約を維持; card schema へ展開 | S01-S04 の concrete tests を `前提`、`操作`、`期待結果`、`失敗検出`、`検証方法`、`関連 closure id` を持つ step-local cards に展開 | Worker が fixture / expected observation / failure mode を推測しないようにするため | promoted_to_plan | `plan.md` S01-S04 concrete test cards | fresh plan re-review |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | partially_adopted | sub-agent `system-architect` | `design.md` | Layered architecture、module responsibilities、CLI contract、strict-legacy compatibility、classification safety、test strategy は requirement と既存 runtime pattern に合致。`generated_at` example と未固定 exit-code 表現は deterministic / compatibility decision と衝突するため不採用。 | `discussions/20260623t124355z-draft-design-system-architect-design-draft.md`; manual diff guard: `git status --short` で allowed discussion path 以外の delegated write なし | fresh design re-review |
| EAL-002 | partially_adopted | sub-agent `implementation-planner` | `plan.md` | Requirement/design trace、step slicing、closure index、test cards、S90/S99 gates、Epic-level PR deferred note を採用。Delegated provenance / HEAD observation / reviewer-pass claim は canonical authority として採用しない。 | `discussions/20260623t130929z-draft-plan-implementation-planner-plan-draft.md`; manual diff guard: `git status --short` で allowed discussion path 以外の delegated write なし | fresh plan review |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | `requirement.md` 目的: tracked `assurance.json` と deterministic classification runtime | Static analysis baseline と provider/mirror authority | low | requirement pass; design pass; plan review pending |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | Epic requirement/design/plan、accepted ADR、draft requirement/design、current Ruff/MyPy baseline | 初回 reviewer P1/P2 に回答済み: Lite all-positive/no-opt-in safety、Epic draft baseline clarification | draft requirement を採用し reviewer findings を反映 | pass (`spec-reviewer`, 2026-06-23) | no | design authoring へ昇格 |
| design | requirement、system-architect discussion draft、runtime parser/registry/usecase/json_store pattern、reviewer findings | P1/P2 に回答済み: delegated adoption ledger、durable source binding、policy table、schema validation、path targeting、RiskFact derivation、reason-code defaults | discussion draft を部分採用し reviewer findings を design / report に反映 | pass (`spec-reviewer`, 2026-06-23) | no | plan authoring へ昇格 |
| plan | requirement、design、implementation-planner discussion draft、issue plan authoring docs、plan reviewer findings | P1 に回答済み: step-local delegation contract、Red evidence、closure gate、concrete test card schema | discussion draft を部分採用し canonical plan へ統合、reviewer findings を反映 | pass (`spec-reviewer`, 2026-06-23) | no | execution handoff ready |

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
| system-architect | iss-00227 | `discussions/20260623t124355z-draft-design-system-architect-design-draft.md` | `requirement.md`; Epic requirement/design/plan; existing runtime source; tests layout | `design.md`; `plan.md` | partially_adopted | [`design.md`] | manual_pass: `git status --short` showed only orchestrator requirement/design changes plus allowed discussion file | canonical design integration by main orchestrator | `generated_at` persisted JSON example; undecided missing-contract exit-code language | none after design re-review pass | fail -> re-review pending | eligible after fresh `spec-reviewer` pass |
| implementation-planner | iss-00227 | `discussions/20260623t130929z-draft-plan-implementation-planner-plan-draft.md` | `requirement.md`; `design.md`; `report.md`; issue plan authoring docs; runtime source layout; tests layout | `plan.md`; `report.md` | partially_adopted | [`plan.md`, `report.md`] | manual_pass: `git status --short` showed only orchestrator canonical planning changes plus allowed discussion file | canonical plan integration by main orchestrator | delegated provenance claims, raw HEAD observation, and reviewer-pass / implementation-readiness claims | none after plan review pass | pass (`spec-reviewer`, 2026-06-23) | eligible; execution handoff ready |

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
- [実装した内容の概要を2-3文で記載]

## 実装記録（セッションログ） (必須)

### セッションログ（2026-06-23 HH:MM - HH:MM）

#### 対象
- Step: S01, S02, ...
- AC/EC: AC-___, EC-___
- 計画上の出典（Planned source）:
  - `plan.md` section:
  - closure ids:

#### 実施内容
- ...

#### 実行コマンド / 結果
```bash
<command>

<result>
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S01 | 赤フェーズ / 代替証跡（Red / alternative） | red-required | Initial focused test run failed before `domain.assurance` existed; follow-up review tests failed before raw fact, explicit empty facts, and source binding validation fixes | `uv run pytest tests/unit/domain/test_assurance.py` | pass | Red evidence observed by delegated worker and bounded review follow-ups |
| S01 | 緑フェーズ（Green） | S01 focused tests pass | Domain assurance contract/policy/serialization tests pass after fixes | `uv run pytest tests/unit/domain/test_assurance.py` -> 9 passed | pass | Parent verification after reviewer P1 fix |
| S01 | リファクタリング（Refactor） | guardrail satisfied / no refactor needed | No behavior-preserving refactor needed after minimal validation/test additions | diff inspection | approved-no-op | Domain module remains pure stdlib/domain and no adapter imports |
| S02 | 赤フェーズ / 代替証跡（Red / alternative） | red-required | Focused infra tests failed before `infra.assurance_store` existed | `uv run pytest tests/unit/infra/test_assurance_store.py` -> 4 failed | pass | Red evidence observed by delegated worker: `ModuleNotFoundError: No module named 'spec_dock_runtime.infra.assurance_store'` |
| S02 | 緑フェーズ（Green） | S02 focused tests pass | Infra assurance store tests pass after implementation and review follow-ups | `uv run pytest tests/unit/infra/test_assurance_store.py` -> 5 passed; `uv run pytest tests/unit/domain/test_assurance.py tests/unit/infra/test_assurance_store.py` -> 14 passed | pass | Parent verification repeated after reviewer P1 fixes |
| S02 | リファクタリング（Refactor） | guardrail satisfied / no refactor needed | Ruff passed and no behavior-preserving refactor needed after bounded infra implementation | `uv run ruff check src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/assurance_store.py tests/unit/infra/test_assurance_store.py` -> pass | approved-no-op | Store remains in infra and reuses domain validation without duplicating policy |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S01 | raw `RiskFact` duplicate / invalid value must fail closed | code-reviewer | added test and fixed domain validation | `cl-ac003-lite-safety`, `cl-ec002-hard-trigger-monotonic` | no | `tests/unit/domain/test_assurance.py` -> 6 passed |
| S01 | explicit empty `risk_facts=()` must not fall back to defaults | code-reviewer | added test and fixed `build_assurance_contract` None/empty distinction | `cl-dc010-default-facts`, `cl-ac003-lite-safety` | no | `tests/unit/domain/test_assurance.py` -> 7 passed |
| S01 | empty source binding artifacts must be invalid | code-reviewer | added validation and test for missing source artifacts | `cl-ac002-deterministic-json`, `cl-ac006-layer-boundary` | no | `tests/unit/domain/test_assurance.py` -> 8 passed |
| S01 | source binding path must be resolved repo-relative issue-local path | code-reviewer | added validation and test rejecting absolute and `spec-dock/active/` artifact paths | `cl-ac002-deterministic-json`, `cl-ac006-layer-boundary` | no | `tests/unit/domain/test_assurance.py` -> 9 passed |
| S02 | target/path safety and missing/invalid contract distinctions | implementation | added focused infra tests and bounded `AssuranceStore` implementation | `cl-ac001-classify-contract-write`, `cl-ac004-strict-legacy-missing`, `cl-ac005-invalid-contract`, `cl-dc008-target-resolution`, `cl-ac006-layer-boundary` | no | `tests/unit/infra/test_assurance_store.py` -> 4 passed |
| S02 | semantic invalid risk facts and obligations mismatch must fail as invalid schema | code-reviewer | added tests and fixed store validation to catch domain validation errors and validate `obligations.profile_preset` | `cl-ac005-invalid-contract` | no | Red: `tests/unit/infra/test_assurance_store.py` -> 1 failed / 3 passed; Green: 4 passed |
| S02 | persisted `issue_id` and source binding path must be target-local | code-reviewer | added tests and fixed target-aware schema validation | `cl-ac005-invalid-contract`, `cl-ac001-classify-contract-write` | no | Red: `tests/unit/infra/test_assurance_store.py` -> 1 failed / 4 passed; Green: 5 passed |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S01 | `cl-ac002-deterministic-json`, `cl-ac003-lite-safety`, `cl-ec002-hard-trigger-monotonic`, `cl-ac006-layer-boundary`, `cl-dc010-default-facts` | S01 domain policy/serializer tests pass, import boundary inspection/test passes, code-reviewer pass required before commit | `uv run pytest tests/unit/domain/test_assurance.py` -> 9 passed; fresh code-reviewer pass | pass | Red evidence observed by worker: initial focused tests failed before `domain.assurance` existed; follow-up red tests reproduced duplicate/invalid raw fact, explicit empty facts, empty source binding, and non-durable source path gaps |
| S02 | `cl-ac001-classify-contract-write`, `cl-ac004-strict-legacy-missing`, `cl-ac005-invalid-contract`, `cl-dc008-target-resolution`, `cl-ac006-layer-boundary` | S02 infra source binding, store read/write/verify, missing/invalid distinction, and target safety tests pass; code-reviewer pass required before commit | `uv run pytest tests/unit/infra/test_assurance_store.py` -> 5 passed; `uv run pytest tests/unit/domain/test_assurance.py tests/unit/infra/test_assurance_store.py` -> 14 passed; fresh code-reviewer pass | pass | Red evidence observed by worker: initial focused tests failed before `infra.assurance_store` existed; follow-up red tests reproduced semantic invalid schema crash and target-local schema gaps before validation fixes |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| tc-001 | S01 | yes | red-required | worker observed initial domain test failure before implementation | `uv run pytest tests/unit/domain/test_assurance.py` | pass | S01 focused domain assurance test set passed after implementation and review follow-ups |
| `cl-ac002-deterministic-json` | S01 | yes | red-required | worker observed initial domain test failure before implementation | `uv run pytest tests/unit/domain/test_assurance.py` | pass | deterministic bytes, no volatile fields, no `proposed_profile` |
| `cl-ac003-lite-safety` | S01 | yes | red-required | worker observed initial domain test failure; follow-up duplicate/invalid/empty tests failed before validation fix | `uv run pytest tests/unit/domain/test_assurance.py` | pass | Lite unknown/all-positive-no-opt-in fail closed; duplicate/invalid/empty raw facts rejected |
| `cl-ec002-hard-trigger-monotonic` | S01 | yes | red-required | worker observed initial domain test failure; follow-up invalid raw fact test failed before validation fix | `uv run pytest tests/unit/domain/test_assurance.py` | pass | strict/critical escalation and duplicate/invalid raw facts rejected |
| `cl-ac006-layer-boundary` | S01 | yes | inspect-only plus test | new module import inspection planned; code-review follow-ups identified source binding validation gaps | `uv run pytest tests/unit/domain/test_assurance.py` | pass | domain module has no infra/commands/cli/presentation/GitHub/filesystem adapter imports; persisted contract validation rejects missing source artifacts and non-durable artifact paths |
| `cl-dc010-default-facts` | S01 | yes | red-required | worker observed initial domain test failure before implementation; code-review follow-up identified explicit empty tuple fallback | `uv run pytest tests/unit/domain/test_assurance.py` | pass | default facts and reason/consequence codes are stable; omitted facts (`None`) and explicit empty facts are distinct |
| `cl-ac001-classify-contract-write` | S02 | yes | red-required | worker observed initial infra test failure before implementation | `uv run pytest tests/unit/infra/test_assurance_store.py` | pass | store writes and reads issue-local `assurance.json` with durable requirement source binding |
| `cl-ac004-strict-legacy-missing` | S02 | yes | red-required | worker observed initial infra test failure before implementation | `uv run pytest tests/unit/infra/test_assurance_store.py` | pass | missing `assurance.json` returns `missing` / `strict-legacy`, not invalid |
| `cl-ac005-invalid-contract` | S02 | yes | red-required | worker observed initial infra test failure before implementation; follow-up tests reproduced semantic invalid schema crash and target-local schema gaps | `uv run pytest tests/unit/infra/test_assurance_store.py` | pass | invalid JSON, required-field schema invalid, semantic risk fact invalid, obligations mismatch, invalid issue id, and non issue-local source binding return invalid outcomes without crashing |
| `cl-dc008-target-resolution` | S02 | yes | red-required | worker observed initial infra test failure before implementation | `uv run pytest tests/unit/infra/test_assurance_store.py` | pass | active, issue id, GitHub number, repo-contained path accepted; missing/non-issue/repo escape/symlink escape rejected |

- `closure id / test id` は Spec-Locked Closure Index の `id` を指す。別 alias を使う場合は `Closure Delta` で対応を記録する。

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| tc-001 | S01 | `uv run pytest tests/unit/domain/test_assurance.py` | pass | S01 focused test contract covered by 9 passed parent verification |
| `cl-ac002-deterministic-json` | S01 | `uv run pytest tests/unit/domain/test_assurance.py` | pass | 9 passed in parent verification |
| `cl-ac003-lite-safety` | S01 | `uv run pytest tests/unit/domain/test_assurance.py` | pass | includes unknown/no-opt-in and raw fact validation hardening |
| `cl-ec002-hard-trigger-monotonic` | S01 | `uv run pytest tests/unit/domain/test_assurance.py` | pass | strict/critical escalation covered |
| `cl-ac006-layer-boundary` | S01 | `uv run pytest tests/unit/domain/test_assurance.py` | pass | import-boundary static inspection covered |
| `cl-dc010-default-facts` | S01 | `uv run pytest tests/unit/domain/test_assurance.py` | pass | default fact/reason-code fixture covered |
| `cl-ac001-classify-contract-write` | S02 | `uv run pytest tests/unit/infra/test_assurance_store.py` | pass | source binding, issue-local write/read, and target-local persisted path validation covered |
| `cl-ac004-strict-legacy-missing` | S02 | `uv run pytest tests/unit/infra/test_assurance_store.py` | pass | missing contract compatibility covered |
| `cl-ac005-invalid-contract` | S02 | `uv run pytest tests/unit/infra/test_assurance_store.py` | pass | invalid JSON/schema distinction, semantic invalid schema handling, and target-aware schema checks covered |
| `cl-dc008-target-resolution` | S02 | `uv run pytest tests/unit/infra/test_assurance_store.py` | pass | explicit target path containment and active fallback safety covered |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none / added / removed / changed / alias-mapped | tc-001 | tc-001 / test-name | tc-001 | ... | yes / no | yes / no |
| added | `cl-ac003-lite-safety`, `cl-ec002-hard-trigger-monotonic` | `test_classification_rejects_duplicate_raw_risk_fact_keys`, `test_classification_rejects_invalid_raw_risk_fact_values` | existing S01 closure IDs | code-reviewer found ambiguous raw `RiskFact` tuples could silently downscope policy; tests strengthen approved S01 fail-closed contract | no | no |
| added | `cl-dc010-default-facts`, `cl-ac003-lite-safety` | `test_build_contract_rejects_explicit_empty_risk_facts` | existing S01 closure IDs | code-reviewer found explicit empty tuple could silently fall back to defaults; test preserves omitted-vs-empty distinction | no | no |
| added | `cl-ac002-deterministic-json`, `cl-ac006-layer-boundary` | `test_contract_validation_rejects_missing_source_binding_artifacts` | existing S01 closure IDs | code-reviewer found empty source binding artifacts were accepted despite the persisted schema requiring source traceability | no | no |
| added | `cl-ac002-deterministic-json`, `cl-ac006-layer-boundary` | `test_contract_validation_rejects_non_durable_source_binding_paths` | existing S01 closure IDs | code-reviewer found absolute and active symlink artifact paths could pass despite the resolved repo-relative source binding requirement | no | no |

#### ワークフロー委任同意の証跡（Workflow Delegation Consent）
`workflow_issue.md` is the policy source for workflow-scoped delegation consent. This report records observed consent, boundary, expiry, and denied / unavailable handling only.

| 同意元（consent source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可理由（denied / unavailable reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user instruction / explicit approval / none | ... | iss-00227 | current session / ... | spec-reviewer / code-reviewer / qa-reviewer / read-only specialist | same repo, active issue, session, named role; no destructive action / publishing / credentialed access / scope expansion / write-capable delegation / private external system use | issue complete / session end / scope change / host policy conflict / user revocation | none / denied / unavailable / host conflict | proceed / ask user / block gate / record waiver request |

#### 実装委任ゲート（Implementation Delegation Gate）
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records observed evidence only.

| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | delegated / approved-local-execution / degraded mode | multi-layer / shipped scaffold / pattern analysis / integration / large worker scope / none | repo-analyst / dev-coder / doc-writer / N/A | ... | ... | ... | ... | ... | ... | worker summary / changed files / verification / risks / integration decision | pass / fail / blocked |
| S01 | delegated | runtime domain implementation | dev-coder | S01 domain assurance model/policy/serialization only | `plan.md` S01 | `domain/assurance.py`, `tests/unit/domain/test_assurance.py` | infra/application/CLI/presentation/mirror/docs/config/skills/GitHub state | `uv run pytest tests/unit/domain/test_assurance.py` | policy/table conflict, domain requiring adapters, non-deterministic serializer | changed files, tests, risks, ledger note | pass |
| S02 | delegated | runtime infra implementation | dev-coder | S02 assurance store, target resolution, source binding, schema validation only | `plan.md` S02 | `infra/assurance_store.py`, `tests/unit/infra/test_assurance_store.py` | parser/registry/bootstrap/application/presentation/domain policy/mirror/docs/config/skills/GitHub state | `uv run pytest tests/unit/infra/test_assurance_store.py` | broad target refactor, path behavior conflict, schema validator requiring domain semantic changes | changed files, tests, target/path notes, risks, ledger note | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S01 | dev-coder / doc-writer / repo-analyst | ... | `path/to/file` | `command` -> pass / docs-only inspection -> pass | pass / fail / unavailable / denied / waived / provisional | none / ... | accepted / rejected / needs follow-up |
| S01 | dev-coder | Implemented pure domain assurance contract/policy/serializer and tests; bounded follow-ups added duplicate/invalid raw fact validation, explicit empty tuple rejection, empty source binding validation, and non-durable source path validation. | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/assurance.py`; `tests/unit/domain/test_assurance.py` | `uv run pytest tests/unit/domain/test_assurance.py` -> 9 passed | pass | none | accepted |
| S02 | dev-coder | Implemented infra assurance store, target resolution, source binding hash, read/write/verify, and missing/invalid distinctions; bounded follow-ups fixed semantic invalid schema and target-aware schema handling. | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/assurance_store.py`; `tests/unit/infra/test_assurance_store.py` | `uv run pytest tests/unit/infra/test_assurance_store.py` -> 5 passed; `uv run pytest tests/unit/domain/test_assurance.py tests/unit/infra/test_assurance_store.py` -> 14 passed; `uv run ruff check src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/assurance_store.py tests/unit/infra/test_assurance_store.py` -> pass | pass | none | accepted |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| S01 | unavailable / denied / host conflict / impossible because ... | approval source / risk accepted: yes / no | `path/to/file` | ... | ... | `command` -> pass / docs-only inspection -> pass | reviewer role + passed / failed / unavailable / denied / waived / provisional | blocked / incomplete / waived with explicit risk acceptance / next action |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S01 | step reviewer / final reviewer | code-reviewer / spec-reviewer / qa-reviewer | fresh / stale | passed / failed / unavailable / denied / waived / provisional | yes / no / N/A | proceed / blocked / incomplete / follow-up required | ... |
| S01 | step reviewer | code-reviewer | fresh | failed -> pass | no | proceed | Initial review found missing report evidence and raw fact validation gap. Follow-up reviews surfaced empty tuple, source binding edge cases, and TDD ledger gaps; bounded fixes applied. Fresh re-review passed with no findings. |
| S02 | step reviewer | code-reviewer | fresh | failed -> pass | no | proceed | Reviews found semantic invalid schema crash, missing obligations validation, invalid issue id, and non issue-local source binding gaps. Bounded fixes applied; fresh re-review passed with no findings. |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S01 | committed / approved-no-op | ... | <hash or final ledger reference> | `git status --short` -> clean | ... | ... | ... | ... |
| S01 | committed | `domain/assurance.py`, `tests/unit/domain/test_assurance.py`, S01 report evidence | `9a5f694f` | `git status --short` -> clean | N/A | N/A | N/A | N/A |
| S02 | committed | `infra/assurance_store.py`, `tests/unit/infra/test_assurance_store.py`, S02 report evidence | S02 commit in git history: `feat(assurance): Assurance Contractの保存基盤を追加` | `git status --short` -> clean | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `path/to/file1` - ...
- `path/to/file2` - ...
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/assurance.py` - Assurance Contract v1 domain model, deterministic policy, serializer, validation helpers
- `tests/unit/domain/test_assurance.py` - S01 domain tests for deterministic output, Lite safety, hard triggers, raw fact validation, and import boundary
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/assurance_store.py` - S02 issue target resolution, source binding, issue-local contract store, schema/missing/invalid distinction
- `tests/unit/infra/test_assurance_store.py` - S02 infra tests for source binding, strict-legacy missing, invalid JSON/schema, explicit target safety

#### コミット
- `9a5f694f` `feat(assurance): Assurance Contractのドメイン分類を追加`
- S02 commit in git history: `feat(assurance): Assurance Contractの保存基盤を追加`

#### メモ
- ...

---

### セッションログ（2026-06-23 HH:MM - HH:MM）

#### 対象
- Step: ...
- AC/EC: ...

#### 実施内容
- ...

---

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| docs / templates / README / workflow / skill / migration notes | yes / no | doc-writer / N/A | ... | pass / fail / blocked |

### 最終 QA ゲート（Final QA Gate）
| レビュアー（reviewer） | 範囲 | 統合テスト判断（integration test decision） | 証跡（evidence） | 結果（result） |
|---|---|---|---|---|
| qa-reviewer | whole issue obligation coverage | added / already sufficient / not applicable | ... | pass / fail / blocked |

### 最終コードレビューゲート（Final Code Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| code-reviewer | issue-wide integrated diff | ... | 0 | pass / fail / blocked |

### 最終 spec review ゲート（Final Spec Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| spec-reviewer | requirement / design / plan / report / implementation / tests / docs alignment | ... | 0 | pass / fail / blocked |

### 最終 commit（Final Commit）
| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| ... | ... | final response / PR / issue comment / other external delivery evidence | ready / blocked |

## 遭遇した問題と解決 (任意)
- 問題: ...
  - 解決: ...

## 学んだこと (任意)
- ...

## 今後の推奨事項 (任意)
- ...

## 省略/例外メモ (必須)
- 該当なし
