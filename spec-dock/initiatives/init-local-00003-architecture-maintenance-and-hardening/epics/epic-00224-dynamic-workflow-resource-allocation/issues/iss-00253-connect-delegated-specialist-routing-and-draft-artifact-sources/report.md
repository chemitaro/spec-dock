---
種別: 実装報告書（Issue）
ID: "iss-00253"
タイトル: "Connect Delegated Specialist Routing And Draft Artifact Sources"
関連GitHub: ["#253"]
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00253 Connect Delegated Specialist Routing And Draft Artifact Sources — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

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
| D-001 | resolved | implementation | system-architect / implementation-planner / orchestrator | `new doc` へ `AssuranceStore` / `ArtifactStore` をどう接続するか | Ports へ store を追加する; bootstrap closure から `AssuranceStore` / `ArtifactStore` を渡す; `create_node.py` 内で直接生成する | G2 implementation では bootstrap が生成済みの stores を `create_discussion_doc` へ渡し、application layer で profile-aware branch を分ける方針にする。domain へ filesystem store は持ち込まない。 | 既存 `compose_assurance` は bootstrap で store を注入している。`new doc` command surface は変更しない。 | applied | delegated design draft; delegated plan draft; `create_node.py`; `bootstrap.py`; `artifact_store.py`; `assurance_store.py` inspection | canonical design / plan に反映 |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| ID | adoption_status | source | source_role | claim | target_artifact | target_section | rationale | evidence_strength | evidence_path | adopter | reviewer | blocking | next_action |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EAL-001 | adopted | sub-agent | system-architect | Issue design/plan draft routing、pre-allocation fail-closed、profile template guard reuse、legacy normalization bypass、preservation boundary | `design.md` / `plan.md` / `report.md` | design sections 2〜9; plan S90 scope; report D-001 / Delegated Draft Evidence | Draft 内容を source inspection と既存 runtime/test surface に照合し、G2 scope 内の設計判断として採用できるため。 | strong: source-grounded draft + orchestrator inspection | `discussions/20260630t171026z-draft-design-g2-draft-artifact-source-routing-design.md`; `create_node.py`; `artifact_store.py`; `assurance_store.py` | orchestrator | final spec-review pass | no | adopted |
| EAL-002 | adopted | sub-agent | implementation-planner | S00〜S99 step contract、Red/Green tests、fail-closed/no-write確認、preservation tests、local handoff gate | `plan.md` / `report.md` | plan sections 2.1 / 6.1 / 7; report Delegated Draft Evidence | Draft 内容が active requirement AC-001〜AC-007 と Epic branch baton policy に対応し、strict issue execution に必要な step-local evidence destination を持つため。 | strong: source-grounded draft + orchestrator inspection | `discussions/20260630t171038z-disc-implementation-plan-draft-for-profile-aware-routing.md`; `tests/cli_runtime/test_new.py`; `tests/cli_runtime/test_assurance_compose.py` | orchestrator | final spec-review pass | no | adopted |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | G2 の主目的は Issue `draft-design` / `draft-plan` を `authorized_profile` 対応 profile template source に接続し、delegated specialist が canonical と同構造の draft evidence を作れるようにすること。 | fail-closed/no-write、preservation、compose regression、individual PR なしの local handoff を副次要件として plan に固定した。 | low | final spec-review pass |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | active requirement、Epic #224 requirement/design/plan、G1 completion commit `9d172bff` | blocking question なし | requirement を approved に昇格 | final spec-review pass | no | design / plan review |
| design | system-architect draft、`create_node.py`、`artifact_store.py`、`assurance_store.py`、profile templates、existing tests | blocking question なし | delegated draft を採用し、canonical design に反映 | final spec-review pass | no | plan review |
| plan | implementation-planner draft、existing CLI tests、Epic branch baton policy | blocking question なし | step contract / closure index / final local handoff を canonical plan に反映 | final spec-review pass | no | final spec-review |

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
| system-architect | iss-00253 | `discussions/20260630t171026z-draft-design-g2-draft-artifact-source-routing-design.md` | active issue docs、Epic docs、runtime code、profile templates、tests | `design.md`, `plan.md`, `report.md` | adopted | `design.md`, `plan.md`, `report.md` | passed | design decisions integrated | none | none | final spec-review pass | promoted |
| implementation-planner | iss-00253 | `discussions/20260630t171038z-disc-implementation-plan-draft-for-profile-aware-routing.md` | active issue docs、Epic docs、runtime code、profile templates、tests | `plan.md`, `report.md` | adopted | `plan.md`, `report.md` | passed | step contract integrated | none | none | final spec-review pass | promoted |

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
- Issue `draft-design` / `draft-plan` を verified `.assurance.json` の `authorized_profile` に対応する issue profile template へ接続した。
- missing assurance では discussion file を作らず fail-closed し、`draft-requirement` と Initiative / Epic draft は既存挙動を維持した。

## 実装記録（セッションログ） (必須)

### セッションログ（2026-07-01 G2 実装）

#### 対象
- Step: S00, S01, S02, S03, S04, S90
- AC/EC: AC-001, AC-002, AC-003, AC-004, AC-005, AC-006, AC-007
- 計画上の出典（Planned source）:
  - `plan.md` section: `6.1 実装ステップ / 実行ステップ契約`
  - closure ids: C-001, C-002, C-003, C-004, C-005, C-006, C-007, C-090

#### 実施内容
- S00: `create_node.py`、`artifact_store.py`、`assurance_store.py`、既存 `test_new.py` / `test_assurance_compose.py` を調査した。
- S01: `create_discussion_doc` に `AssuranceStore` / `ArtifactStore` を bootstrap から注入し、Issue `draft-design` / `draft-plan` だけ profile-aware route に通した。
- S02: verified contract がない場合は discussion filename allocation 前に `RuntimeError` で停止するようにした。
- S03: `ArtifactStore.load_profile_artifact_template_text()` を追加し、compose と同じ profile template filesystem guard を再利用した。
- S04: `draft-requirement` と Initiative / Epic draft route の preservation test を維持した。
- S90: provider / dogfooding issue discussion rules と templates README を profile-aware routing に更新した。

#### 実行コマンド / 結果
```bash
uv run pytest tests/cli_runtime/test_new.py tests/cli_runtime/test_assurance_compose.py

pass: 63 passed, 5 skipped
```

```bash
uv run pytest tests/cli_runtime/test_new.py tests/cli_runtime/test_assurance_compose.py tests/cli_runtime/test_runtime_new_doc_s09.py

pass: 92 passed, 5 skipped
```

```bash
uv run pytest tests/cli_runtime/test_runtime_new_doc_s09.py

pass: 29 passed
```

```bash
make lint

pass: ruff check / ruff format check / mypy
```

```bash
./spec-dock/scripts/spec-dock validate
git diff --check

pass: validate nodes=160; diff check clean
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S00 | 代替証跡（inspect-only） | current routing / reusable stores | Issue draft design/plan は common template + thin normalization。profile loader / assurance verifier は再利用可能。 | source inspection | pass | baseline fixed |
| S01 | 緑フェーズ（Green） | profile template success path | Standard / Strict / Critical の Issue design/plan draft が各 profile template heading を含む | `uv run pytest tests/cli_runtime/test_new.py` | pass | C-001, C-002, C-005, C-006 |
| S02 | 緑フェーズ（Green） | assurance contract no-write | missing / invalid JSON / stale binding / unsupported profile で non-zero、discussions file set unchanged | `uv run pytest tests/cli_runtime/test_new.py` | pass | C-003 |
| S03 | 緑フェーズ（Green） | profile template guard reuse | missing / non-file / symlink escape / empty profile template で `new doc` が no-write fail-closed。`test_assurance_compose.py` 既存 validation regression も維持 | `uv run pytest tests/cli_runtime/test_new.py tests/cli_runtime/test_assurance_compose.py` | pass | C-003, C-007 |
| S04 | 緑フェーズ（Green） | preservation behavior | Issue `draft-requirement` と Initiative / Epic draft route が維持。application-level S09 direct caller regression も維持 | `uv run pytest tests/cli_runtime/test_new.py tests/cli_runtime/test_runtime_new_doc_s09.py` | pass | C-004 |
| S90 | docs inspection | docs / rules / README alignment | issue discussion rules と templates README を provider/dogfooding で更新 | `rg` inspection; `git diff --check` | pass | C-090 |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S90 | `templates/README.md` に Issue design/plan も scope canonical source と読める古い説明が残っていた | docs inspection | provider / dogfooding README を更新 | C-090 | no | `rg` inspection |
| S95 | reviewer 指摘で `plan_discussion_doc` の返り値 arity 互換破壊が判明 | code-reviewer | public return shape を 3 要素に戻し、create 側だけ internal extended planner を使用 | C-004 | no | `uv run pytest tests/cli_runtime/test_runtime_new_doc_s09.py` |
| S95 | reviewer 指摘で Standard のみ / missing contract のみの証跡不足が判明 | qa-reviewer / spec-reviewer | Strict / Critical success と invalid / stale / template guard no-write tests を追加 | C-001, C-002, C-003 | no | `uv run pytest tests/cli_runtime/test_new.py tests/cli_runtime/test_assurance_compose.py` |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S00 | C-001〜C-007 | baseline routing / reusable store evidence | source inspection | pass | no code change |
| S01 | C-001, C-002, C-005, C-006 | profile design/plan success and no self-claim | CLI content assertions | pass | Standard / Strict / Critical profile fixtures |
| S02 | C-003 | invalid assurance fail-closed before write | CLI no-write assertions | pass | missing / invalid JSON / stale binding / unsupported profile |
| S03 | C-003, C-007 | profile template guard and compose validation regression | CLI no-write assertions / compose CLI tests | pass | missing / non-file / symlink escape / empty template |
| S04 | C-004 | preservation behavior and application caller compatibility | CLI preservation tests / S09 application tests | pass | non-Issue draft routes unchanged; `plan_discussion_doc` 3-tuple contract preserved |
| S90 | C-090 | docs/rules impact resolved | docs inspection | pass | provider/dogfooding updated |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| C-001 / C-002 | S01 | yes | red-required | old Issue draft source was common issue template | `uv run pytest tests/cli_runtime/test_new.py` | pass | Standard / Strict / Critical profile design/plan source |
| C-003 | S02 / S03 | yes | red-required | old Issue draft plan succeeded without assurance | `uv run pytest tests/cli_runtime/test_new.py` | pass | missing / invalid JSON / stale binding / unsupported profile / missing template / non-file template / symlink escape / empty template no-write |
| C-004 | S04 | yes | covered-existing | preservation cases existed | `uv run pytest tests/cli_runtime/test_new.py`; `uv run pytest tests/cli_runtime/test_runtime_new_doc_s09.py` | pass | expectation updated for Issue requirement; application-level tuple contract preserved |
| C-005 / C-006 | S01 | yes | content assertion | old thin normalization generated simplified body | `uv run pytest tests/cli_runtime/test_new.py` | pass | no self-claim assertions |
| C-007 | S03 | yes | regression | compose tests existed | `uv run pytest tests/cli_runtime/test_assurance_compose.py` | pass | unchanged compose behavior |
| C-090 | S90 | yes | docs inspection | stale README/rules wording | `rg` / diff inspection | pass | docs updated |

- `closure id / test id` は Spec-Locked Closure Index の `id` を指す。別 alias を使う場合は `Closure Delta` で対応を記録する。

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| C-001〜C-007 | S01〜S04 | focused CLI / application tests | pass | combined focused suite: 92 passed, 5 skipped |
| C-090 | S90 | docs inspection / diff check | pass | provider/dogfooding docs updated |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| reviewer-driven expansion | C-001, C-002, C-003, C-004 | test_new / test_assurance_compose / test_runtime_new_doc_s09 / docs inspection | C-001〜C-090 | final QA/code/spec review の指摘により、Strict/Critical、invalid/stale/template guard、public tuple contract の証跡を追加 | no | re-review required |

#### ワークフロー委任同意の証跡（Workflow Delegation Consent）
`workflow_issue.md` is the policy source for workflow-scoped delegation consent. This report records observed consent, boundary, expiry, and denied / unavailable handling only.

| 同意元（consent source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可理由（denied / unavailable reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user instruction / workflow issue execution | `/Volumes/990p2t/offloaded/home/iwasawayuuta/.codex/worktrees/cdfe/spec-dock` | iss-00253 | current session | system-architect / implementation-planner / spec-reviewer / code-reviewer / qa-reviewer | same repo, active issue, session, named role; no destructive action / publishing / credentialed access / scope expansion | issue complete / session end / scope change / host policy conflict / user revocation | none | proceed |

#### 実装委任ゲート（Implementation Delegation Gate）
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records observed evidence only.

| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planning | delegated | strict issue planning required specialist evidence | system-architect / implementation-planner | discussion draft evidence only | active issue docs / Epic docs | active issue `discussions/` direct child | canonical docs / implementation / tests | diff guard / validate | forbidden path / self-claim | draft artifact path / summary | pass |
| S01〜S90 | approved-local-execution | implementation is tightly coupled runtime/test/docs patch | N/A | parent execution | active plan | listed implementation paths | out-of-scope G3/G4 evidence gates | focused tests / lint / validate | reviewer blocker | report evidence | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| planning | system-architect | draft routing design evidence produced | discussion draft only | validate pass reported by worker | spec-review pass after fixes | none | accepted in EAL-001 |
| planning | implementation-planner | step contract and local handoff plan produced | discussion draft only | validate pass reported by worker | spec-review pass after fixes | none | accepted in EAL-002 |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| S01〜S90 | implementation changes require integrated parent coordination across runtime, tests, docs, and report | user asked to continue Epic implementation; risk accepted: no special waiver | listed implementation files | local edit / tests / docs update | revert commit or patch rollback | `make lint`; focused pytest; validate | final qa/code/spec reviewers passed after fixes | N/A |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| planning | spec-review | spec-reviewer | fresh | passed | no | proceed | P2 requirement scope clarified before implementation |
| S95 | final QA / code / spec review | qa-reviewer / code-reviewer / spec-reviewer | fresh first pass | failed-fixed | no | re-review required | P1 findings: missing Strict/Critical evidence, incomplete C-003 no-write matrix, `plan_discussion_doc` return arity regression. Fixes applied and tests passed. |

#### マイルストーン / commit 候補ゲート（Milestone / Commit Candidate Gate）
| マイルストーン / step | クロージャ状態（closure state） | コミット候補 / コミット範囲（commit candidate / scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S00〜S99 | completed | runtime / tests / docs / report | to be recorded by this implementation commit | post-commit clean check to run after commit | N/A | changed files | N/A | focused tests / lint / validate / reviewer pass |

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py` - profile-aware issue draft routing
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py` - store injection
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/artifact_store.py` - full profile template text loader
- `tests/cli_runtime/test_new.py` - profile source / no-write / preservation tests
- `src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md` and dogfooding mirror - issue draft source rules
- `src/spec_dock/assets/spec_dock/templates/README.md` and dogfooding mirror - template source explanation
- `report.md` - implementation evidence

#### コミット
- this implementation commit records S00〜S99 after final reviewer gates; no per-issue PR is created.

#### メモ
- Per-issue PR は作成しない。Epic #224 の単一 PR に含める。

---

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| docs / templates / README / workflow / skill / migration notes | yes | parent executor | provider / dogfooding issue discussion rules and templates README updated; `git diff --check`; `./spec-dock/scripts/spec-dock validate` | pass |

### 最終 QA ゲート（Final QA Gate）
| レビュアー（reviewer） | 範囲 | 統合テスト判断（integration test decision） | 証跡（evidence） | 結果（result） |
|---|---|---|---|---|
| qa-reviewer | whole issue obligation coverage | added | first pass failed on C-003 matrix and Strict/Critical coverage; tests added; re-review `019f19a6-8a61-7532-a72a-84edeaf086b8` pass | pass |

### 最終コードレビューゲート（Final Code Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| code-reviewer | issue-wide integrated diff | first pass failed on `plan_discussion_doc` return arity; public 3-tuple contract restored with internal extended planner | 1 | pass |

### 最終 spec review ゲート（Final Spec Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| spec-reviewer | requirement / design / plan / report / implementation / tests / docs alignment | first pass failed on C-001/C-002 profile breadth and C-003 matrix evidence; tests/report updated; re-review pass with P2 ledger cleanup applied | 1 | pass |

### 最終 commit（Final Commit）
| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| updated through S99 before commit | runtime create-node/profile-template routing, bootstrap injection, artifact store loader, CLI tests, docs/rules/README, report | final response; Epic branch baton to next issue; no per-issue PR | ready |

## 遭遇した問題と解決 (任意)
- 問題: 初回 code-review で `plan_discussion_doc` の返り値 arity 互換破壊が見つかった。
  - 解決: public function は従来の 3-tuple を維持し、`create_discussion_doc` 内部だけ extended planner を使う構造に変更した。
- 問題: 初回 QA/spec review で Strict/Critical routing と C-003 fail-closed matrix の証跡不足が見つかった。
  - 解決: Standard / Strict / Critical success tests と missing / invalid / stale / unsupported profile / invalid profile template no-write tests を追加した。

## 学んだこと (任意)
- Issue draft の source routing は CLI 成功系だけでなく、discussion filename allocation 前に止まる no-write 系を直接 CLI 経路で検証する必要がある。

## 今後の推奨事項 (任意)
- 後続 issue でも Epic 単一 PR 方針に従い、issue 完了時は commit checkpoint と report 証跡だけを残し、PR 作成は Epic 最終品質ゲートに集約する。

## 省略/例外メモ (必須)
- 該当なし
