---
種別: 実装計画書（Issue）
ID: "iss-00250"
タイトル: "Route Issue Draft Design And Plan Through Profile Templates"
関連GitHub: ["#250"]
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-30"
依存: ["requirement.md", "design.md"]
親: ["epic-00224", "init-local-00003"]
Issue Grade: "strict"
authorized_profile: "standard"
manual_escalation: "strict"
---

# iss-00250 Route Issue Draft Design And Plan Through Profile Templates — Issue 実装計画書

## 1. 計画前提

この Issue は、Issue scope の `new doc draft-design` / `new doc draft-plan` が grade 別 profile template を使わず、旧来の `templates/issue/design.md` / `templates/issue/plan.md` 由来の薄い discussion draft を作る問題を修正する。

Runtime の `assurance classify` は現時点で `authorized_profile=standard` を返している。一方、変更対象は CLI runtime、profile template authority、discussion draft governance、tests、provider docs、dogfooding docs にまたがるため、実装とレビューは manual escalation として strict 相当で扱う。

## 2. 実装戦略

- CLI から観測できる Red test を先に追加し、現在の誤った template source を固定してから実装する。
- `assurance compose` と `new doc` の profile template 読み込み guard が分岐しないよう、可能な限り `ArtifactStore` 側の validation logic を再利用または抽出する。
- `create_node.py` では、Issue scope かつ `draft-design` / `draft-plan` の場合だけ profile-aware routing に切り替える。
- missing / invalid / stale `.assurance.json` や unsafe template は、discussion filename allocation と write の前に fail-closed にする。
- `draft-requirement` と Initiative / Epic scope の `draft-design` / `draft-plan` は、既存挙動を regression test として維持する。
- 実装結果、Red / Green / Refactor、レビュー、未実施検証、commit / no-op は `report.md` に記録する。

## 3. 変更範囲

| 種別 | 主対象 | 変更内容 |
|---|---|---|
| runtime | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py` | Issue `draft-design` / `draft-plan` の profile-aware routing を追加する。 |
| infra | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/artifact_store.py` | profile template の full text 読み込み、または reusable validation helper を追加する。 |
| wiring | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py`, `cli/bootstrap.py` | loader 抽出に必要な場合だけ最小変更する。 |
| tests | `tests/cli_runtime/test_new.py` | profile source、fail-closed、既存挙動維持を CLI regression として固定する。 |
| tests | `tests/cli_runtime/test_assurance_compose.py` | template guard 共有で compose contract が変わらないことを確認する。 |
| docs | `src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md` | Issue design / plan draft の source を profile template として説明する。 |
| dogfooding docs | `spec-dock/docs/rules/issue/discussions.md` | provider docs と整合させる。 |

禁止範囲:

- `assurance compose` の profile 判定方針を再設計しない。
- profile template 本文の全面改訂は行わない。
- missing contract 時に Standard へ automatic fallback しない。
- `Issue Grade` frontmatter、`lite_candidate`、コマンド title を profile selection authority にしない。
- `new doc` から canonical `design.md` / `plan.md` を変更しない。

## 4. マイルストーン

| マイルストーン | 成果 | 主な対象 | 完了ゲート |
|---|---|---|---|
| M01 | Red contract tests | `tests/cli_runtime/test_new.py` | profile source と fail-closed の Red が旧挙動で失敗する。 |
| M02 | Shared profile template loader | `artifact_store.py`, 必要な port / bootstrap | compose と draft routing の template guard が分岐しない。 |
| M03 | Issue draft routing behavior | `create_node.py` | Issue design / plan draft が `authorized_profile` template を使い、fail-closed する。 |
| M04 | Docs and dogfooding mirror | provider docs, dogfooding docs | docs が新しい source authority と矛盾しない。 |
| M99 | Final quality gate | issue diff 全体 | focused tests、必要な regression、report 証跡、review gate が完了する。 |

## 5. 振る舞いバックログ

| Behavior ID | マイルストーン | 振る舞い / 保証 | 関連要件 | 優先度 |
|---|---|---|---|---|
| BH-001 | M01 / M03 | classified Issue の `draft-design` は `authorized_profile` の design template から discussion draft を作る。 | REQ-001, AC-001, AC-003 | high |
| BH-002 | M01 / M03 | classified Issue の `draft-plan` は `authorized_profile` の plan template から discussion draft を作る。 | REQ-002, AC-002, AC-003 | high |
| BH-003 | M01 / M03 | Issue `draft-requirement` は `.assurance.json` なしで従来通り成功する。 | REQ-003, AC-006 | high |
| BH-004 | M01 / M03 | Initiative / Epic の `draft-design` / `draft-plan` は従来通り scope template を使う。 | REQ-004, AC-006 | high |
| BH-005 | M01 / M03 | missing / invalid / stale `.assurance.json` は write 前に fail-closed する。 | REQ-005, REQ-006, AC-004, AC-005 | high |
| BH-006 | M02 / M03 | unsupported profile と unsafe / missing / empty / non-file template は fallback せず fail-closed する。 | REQ-005, REQ-010 | high |
| BH-007 | M03 | generated draft は canonical authority、adoption、reviewer pass、phase completion を自己主張しない。 | REQ-008 | medium |
| BH-008 | M04 | docs は Issue design / plan draft の source を profile template と説明する。 | REQ-009 | medium |

## 6. 仕様固定クロージャ

| Closure ID | 閉じる内容 | 検証レベル | 報告証跡 |
|---|---|---|---|
| CLOS-001 | Issue `draft-design` が profile design template を使う。 | CLI test | `report.md` の M01 / M03 evidence |
| CLOS-002 | Issue `draft-plan` が profile plan template を使う。 | CLI test | `report.md` の M01 / M03 evidence |
| CLOS-003 | profile selection authority が `.assurance.json` の `authorized_profile` に限定される。 | test / code review | `report.md` の M03 evidence |
| CLOS-004 | missing / invalid / stale contract で no-write fail-closed する。 | CLI test | `report.md` の M01 / M03 evidence |
| CLOS-005 | `draft-requirement` と Initiative / Epic drafts の既存挙動が維持される。 | regression test | `report.md` の M03 evidence |
| CLOS-006 | provider docs と dogfooding docs が新方針と整合する。 | docs inspection / spec review | `report.md` の M04 evidence |

## 7. 詳細実装計画

### M01 Red Contract Tests

作業:

- `tests/cli_runtime/test_new.py` で、classified Issue の `draft-design` / `draft-plan` が Standard profile template の主要見出しを含むことを期待する Red test を追加する。
- missing / invalid / stale `.assurance.json` で non-zero exit と no-write を期待する Red test を追加する。
- `draft-requirement` と Initiative / Epic `draft-design` / `draft-plan` の既存 success path を regression として確認する。

想定 test seeds:

- `tc-s01-001`: Standard Issue `draft-design` に `Issue 設計書（Standard）` が含まれる。
- `tc-s01-002`: Standard Issue `draft-plan` に `Issue 実装計画書（Standard / TDD）` と Standard 固有 section が含まれる。
- `tc-s02-001`: missing `.assurance.json` では `draft-design` / `draft-plan` が失敗し、discussion file が増えない。
- `tc-s02-002`: invalid / stale `.assurance.json` では fallback draft が作られない。
- `tc-s03-001`: Issue `draft-requirement` は contract なしで成功する。
- `tc-s03-002`: Initiative / Epic design / plan draft は scope template のまま成功する。

commit:

- commit候補: Red contract tests をレビュー可能な単位としてコミットする。
- commit前確認:
  - [ ] 追加 test が旧挙動に対して意図した理由で失敗している。
  - [ ] 既存 test の期待値変更が target behavior に限定されている。
  - [ ] `report.md` に Red evidence を記録している。
  - [ ] M02 以降の実装差分が混ざっていない。

### M02 Shared Profile Template Loader

作業:

- `ArtifactStore` の profile template validation を、compose と draft routing の両方で使える形に整理する。
- 必要なら full Markdown text と repo-relative source path を返す loader を追加する。
- 既存 `load_profile_artifact_template()` の compose 向け body-only contract は壊さない。
- path containment、regular file、existence、non-empty、unsupported profile の guard を弱めない。

完了条件:

- loader 追加後も `tests/cli_runtime/test_assurance_compose.py` が期待する profile template validation contract と矛盾しない。
- `create_node.py` に filesystem validation が重複実装されていない。

commit:

- commit候補: profile template loader / validation reuse をレビュー可能な単位としてコミットする。
- commit前確認:
  - [ ] compose 既存 contract を壊していない。
  - [ ] draft routing 実装前でも差分の意味が説明できる。
  - [ ] `report.md` に検証または未実施理由を記録している。
  - [ ] M03 の routing 差分が混ざっていない、または分離不能な理由を記録している。

### M03 Issue Draft Routing Behavior

作業:

- `create_node.py` で `scope.kind == "issue"` かつ `doc_type in {"draft-design", "draft-plan"}` の branch を追加する。
- 対象 Issue の `.assurance.json` を `AssuranceStore` で verify し、`classification.authorized_profile.value` だけを selection authority とする。
- profile template full text を読み、既存 discussion draft replacement を適用して出力する。
- profile-sourced Issue design / plan drafts では、旧 thin draft 用の `_normalize_draft_discussion_text()` を適用しない。
- filename allocation と write は contract verification / template validation 成功後に行う。
- `draft-requirement` と Initiative / Epic draft paths は既存 branch のまま維持する。

検証:

```bash
uv run pytest tests/cli_runtime/test_new.py tests/cli_runtime/test_assurance_compose.py
```

commit:

- commit候補: Issue design / plan draft routing behavior をレビュー可能な単位としてコミットする。
- commit前確認:
  - [ ] profile source success tests が成功している。
  - [ ] fail-closed no-write tests が成功している。
  - [ ] legacy behavior preservation tests が成功している。
  - [ ] `report.md` に Green / regression evidence がある。

### M04 Docs And Dogfooding Mirror

作業:

- `src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md` を更新し、Issue `draft-design` / `draft-plan` は `templates/issue-profiles/<authorized_profile>/{design,plan}.md` を source とすると説明する。
- Issue `draft-requirement` は common Issue requirement template を使う、と明確に分ける。
- unclassified / stale Issue の design / plan draft は fail-closed し、分類前の調査や論点整理は `disc` / `research` を使う、と説明する。
- provider asset 変更に応じて `spec-dock/docs/rules/issue/discussions.md` を整合させる。

commit:

- commit候補: docs と dogfooding mirror の整合をレビュー可能な単位としてコミットする。
- commit前確認:
  - [ ] provider docs と dogfooding docs の記述が矛盾していない。
  - [ ] `lite` automatic default や Standard fallback を示唆していない。
  - [ ] `report.md` に docs inspection evidence がある。
  - [ ] runtime 未完了差分が混ざっていない。

### M99 Final Quality Gate

作業:

- focused tests、必要な regression、SpecDock validation、final review を実行する。
- 実行できない検証があれば、理由と代替確認を `report.md` に記録する。
- PR 作成前に、ローカルで静的解析 / lint / tests のうちこの repo に設定された該当コマンドを実行する。

検証候補:

```bash
uv run pytest tests/cli_runtime/test_new.py tests/cli_runtime/test_assurance_compose.py
uv run pytest tests/cli_runtime
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync --no-github
```

commit:

- commit候補: 最終品質ゲート通過後の成果をレビュー可能な単位としてコミットする。
- commit前確認:
  - [ ] 静的解析 / lint が完了している、または未実施理由と代替確認が `report.md` にある。
  - [ ] 必要なテストが完了している。
  - [ ] `report.md` に証跡がある。
  - [ ] 未完了差分が混ざっていない。

## 8. Red / Green 方針

- 最初の Red は private helper ではなく public CLI behavior で観測する。
- Success path の Red は、旧 generic draft には含まれない profile template 見出しを期待して失敗させる。
- Fail-closed の Red は、non-zero exit だけでなく discussion file count が増えないことを確認する。
- `test_new.py` では draft routing の contract を固定し、profile template validation の詳細は既存 `test_assurance_compose.py` を guardrail として使う。
- Unknown Red や既存 regression Red が出た場合は実装を進めず、原因を `report.md` に記録して再計画する。

## 9. レビューゲート

| Gate | 対象 | 判定 |
|---|---|---|
| code-reviewer | M02 / M03 の runtime と tests | profile authority、fail-closed、no-write、既存挙動維持が妥当である。 |
| spec-reviewer | M04 docs と issue artifacts | docs / requirement / design / plan が矛盾していない。 |
| qa-reviewer | M99 final quality | focused tests、regression、manual / local verification の証跡が十分である。 |

## 10. 停止・再計画条件

- `AssuranceStore` の verification API を `create_node.py` から安全に使えない。
- profile template validation を共有できず、compose と draft routing の guard が分岐する。
- public CLI output shape の破壊的変更が必要になる。
- `draft-requirement` または Initiative / Epic draft の既存挙動を壊さないと実装できない。
- profile template の authority 自体を再設計する必要が出る。

## 11. 報告証跡への対応

| 証跡 | 記録先 |
|---|---|
| Red test の失敗理由 | `report.md` の TDD evidence |
| Green test / regression test 結果 | `report.md` の session log |
| docs inspection / spec review | `report.md` の review gate status |
| commit / no-op | `report.md` の milestone / commit candidate gate |
| 未実施検証と代替確認 | `report.md` の final quality gate |

## 12. 委任ドラフト採用

この計画は `implementation-planner` delegated draft `discussions/20260630t124640z-disc-implementation-planner-plan-draft.md` を採用し、main orchestrator が requirement / design と整合するように統合した。

採用した内容:

- Red tests first、shared loader、Issue routing、docs、final quality gate のマイルストーン構成。
- BH-001 から BH-008 の behavior backlog。
- success path、fail-closed path、legacy behavior preservation の test seeds。
- PR 前に local focused tests と repository validation を行う品質ゲート。

採用しなかった内容:

- shipped role skill の追加や role workflow の再設計は、この Issue の実装範囲ではないため含めない。
