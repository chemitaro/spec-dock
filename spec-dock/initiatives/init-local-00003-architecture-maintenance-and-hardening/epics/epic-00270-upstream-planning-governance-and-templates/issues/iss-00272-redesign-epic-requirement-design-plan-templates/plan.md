---
種別: 実装計画書（Issue）
ID: "iss-00272"
タイトル: "Redesign Epic Requirement Design Plan Templates"
関連GitHub: ["#272"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
依存: ["requirement.md", "design.md"]
親: ["epic-00270", "init-local-00003"]
---

# iss-00272 Epic テンプレート再設計 — 実装計画

## 証跡採用
| 証跡 | 採用判断 | 理由 |
|---|---|---|
| `artifacts/20260702t081003z-draft-plan-epic-template-redesign-pre-start-seed.md` | partially_adopted | 実行順と対象ファイル候補は有用だが、正本計画としては検証ゲートとテスト対応が不足していた。 |
| `artifacts/20260702t093345z-draft-plan-implementation-plan-epic-template-redesign.md` | partially_adopted | TDD / verification ladder の考え方は採用するが、汎用 Standard scaffold が中心のため、この Issue 固有の実行計画へ再構成する。 |

## 実装方針
- provider-side Epic templates を先に更新し、dogfooding mirror を同内容へ同期する。
- 3 templates を一つの語彙セットとして扱い、capability / model envelope から Issue handoff package までつながるようにする。
- template tests は全文一致ではなく、主要契約 fragment と禁止事項を確認する。
- shipped template に dogfooding 固有 Issue ID や未作成 reference への dangling link を入れない。

## 変更許可範囲
| 種別 | パス | 内容 |
|---|---|---|
| provider templates | `src/spec_dock/assets/spec_dock/templates/epic/{requirement,design,plan}.md` | Epic template prompt の再設計。 |
| dogfooding mirror | `spec-dock/templates/epic/{requirement,design,plan}.md` | provider template と同内容へ同期。 |
| tests | `tests/unit/infra/test_init_update.py` | Epic template contract の focused assertion 追加。 |
| issue report | `spec-dock/active/issue/report.md` | 採用判断、実装証跡、検証結果、reviewer gate を記録。 |

## 禁止変更
- Initiative templates、Issue grade templates、Issue profile templates、runtime command、dependency algorithm を変更しない。
- workflow docs / skills の本格更新をこの Issue に含めない。
- `src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md` を作成しない。
- PR 作成、GitHub Issue close、merge 操作を行わない。

## Spec-Locked Closure Index
| closure | 要件 | 閉じる内容 | primary step | evidence |
|---|---|---|---|---|
| C272-001 | `I272-AC-001` | Epic requirement template が capability / model envelope、主要ユースケース、Epic-level acceptance、scope / non-scope、downstream Issue seed を持つ。 | S02 | `report.md#Step Evidence`, T272-001 |
| C272-002 | `I272-AC-002` | Epic design template が cross-Issue boundary、design slice catalog、contract portfolio、failure / migration / test strategy を持つ。 | S03 | `report.md#Step Evidence`, T272-001 |
| C272-003 | `I272-AC-003` | Epic plan template が Issue handoff package、suggested grade、dependencies、integration checkpoints、final quality gate を持つ。 | S04 | `report.md#Step Evidence`, T272-001 |
| C272-004 | `I272-AC-004` | Epic templates が Issue-level TDD step、private implementation design を必須化しない。 | S05 | T272-004, reviewer gate |
| C272-005 | `I272-AC-005` | Epic templates が raw artifact と canonical adoption / report EAL を分離する。 | S02-S04 | T272-001, reviewer gate |
| C272-006 | `I272-AC-006` | Epic templates が日本語ファースト authoring guidance を持つ。 | S02-S05 | Japanese-primary focused test |
| C272-007 | `I272-AC-007` | 後続 Issue が parent trace、allowed local delta、forbidden parent boundary changes、expected evidence を受け取れる。 | S04 | T272-001, reviewer gate |

## 実行ステップ契約
| step | delegated role | allowed paths | forbidden paths | pre-implementation evidence | verification | report destination | amendment trigger |
|---|---|---|---|---|---|---|---|
| S00 | main orchestrator | `spec-dock/active/issue/{design.md,plan.md,report.md}`, `spec-dock/active/issue/artifacts/*` | provider templates, tests | `iss-00271` issue finish / report / commit evidence, assurance classify / compose / verify, delegated draft artifacts, fresh spec-reviewer | `deps check iss-00272`, `guidance issue-execution`, `assurance verify`, `validate` | `report.md#Spec Authoring Gate`, `report.md#Delegated Draft Evidence`, `report.md#Evidence Adoption Ledger` | previous issue not finished, reviewer fail, authority invalid, unresolved EAL |
| S01 | dev-coder | `tests/unit/infra/test_init_update.py` | provider templates, dogfooding mirror | approved `design.md` / `plan.md`, C272-001..007 | focused test expected Red | `report.md#Step Evidence` | test passes before template change, assertion requires dogfooding ID, assertion overfits wording |
| S02 | doc-writer | `src/spec_dock/assets/spec_dock/templates/epic/requirement.md`, `spec-dock/templates/epic/requirement.md` | Initiative templates, Issue templates, workflow docs | S01 Red evidence, C272-001/C272-004/C272-005/C272-006 | focused test partial Green / read-through | `report.md#Step Evidence` | requirement template needs runtime behavior or workflow change |
| S03 | doc-writer | `src/spec_dock/assets/spec_dock/templates/epic/design.md`, `spec-dock/templates/epic/design.md` | Initiative templates, Issue templates, workflow docs | S02 complete, C272-002/C272-004/C272-005/C272-006 | focused test partial Green / read-through | `report.md#Step Evidence` | design template requires DDD/EDA mandatory wording or private implementation detail |
| S04 | doc-writer | `src/spec_dock/assets/spec_dock/templates/epic/plan.md`, `spec-dock/templates/epic/plan.md` | Initiative templates, Issue templates, workflow docs | S03 complete, C272-003/C272-004/C272-005/C272-006/C272-007 | focused test Green / read-through | `report.md#Step Evidence` | Issue handoff package cannot be expressed without workflow doc/runtime change |
| S05 | main orchestrator | changed files from S01-S04, `report.md` | unrelated files | S02-S04 complete | mirror parity, targeted wording inspection | `report.md#Step Evidence`, `report.md#検証` | provider/mirror mismatch, forbidden wording, dangling link |
| S90 | main orchestrator | none unless report update | production/template files | S05 complete | T272-001..T272-004, `validate`, `diff --check` | `report.md#検証` | focused test failure, validate failure, dirty unrelated changes |
| S99 | reviewers + main orchestrator | `report.md` | template/test changes unless reviewer repair is required | S90 complete | spec-reviewer, code-reviewer or qa-reviewer | `report.md#Reviewer Gate Status`, `report.md#完了--PR` | P0/P1/P2 finding requiring repair |

## Step Closure Contract
| step | closure ids | done condition | reviewer focus |
|---|---|---|---|
| S00 | planning gate | `design.md` / `plan.md` が Issue 固有の正本で、report evidence gate が fresh reviewer pass 後に ready になる。 | 未実施 gate を pass と記録していないこと。 |
| S01 | C272-001..C272-007 | Epic template contract assertion が Red evidence を出し、期待する不足を検出する。 | assertion が dogfooding 固有 ID や過度に脆い全文一致になっていないこと。 |
| S02 | C272-001, C272-004, C272-005, C272-006 | requirement provider / mirror が同期され、capability / model envelope と artifact authority が記述できる。 | Epic requirement に Issue execution detail を入れていないこと。 |
| S03 | C272-002, C272-004, C272-005, C272-006 | design provider / mirror が同期され、cross-Issue boundary と design slice catalog が記述できる。 | DDD / EDA を必須化していないこと。 |
| S04 | C272-003, C272-004, C272-005, C272-006, C272-007 | plan provider / mirror が同期され、Issue handoff package と final quality gate が記述できる。 | downstream Issue が必要な handoff field を受け取れること。 |
| S05 | C272-004, C272-006 | provider/mirror parity、Japanese-primary、forbidden wording、dangling link 回避を確認する。 | scaffold 汎用性を壊していないこと。 |
| S90 | C272-001..C272-007 | focused tests、targeted inspection、`validate`、`diff --check` が通る。 | 検証範囲が AC を覆っていること。 |
| S99 | all | fresh reviewers が pass し、PR は作らず `issue finish` へ進める。 | one-PR delivery とリレー方針に反していないこと。 |

## 実装ステップ

### S00 正規計画化
- `iss-00271` の完了証跡を確認する:
  - `deps check iss-00272` が `ready=true` であること。
  - `iss-00271` report が Issue完了済みであること。
  - `iss-00271` の template vocabulary / reviewer fixes が現在の branch に存在すること。
- `assurance classify --stage requirement`、`assurance compose --artifact all`、`assurance verify` を実行する。
- delegated design / plan draft を report EAL へ採用または部分採用として記録する。
- `design.md` / `plan.md` を Issue 固有の正本候補へ更新する。
- fresh `spec-reviewer` を通す。
- Closure:
  - planning gate
- Delegation:
  - main orchestrator only。canonical spec authoring と report EAL は親が所有する。
- Stop:
  - `iss-00271` 完了証跡が確認できない場合、実装に進まず停止する。
  - fresh `spec-reviewer` が fail した場合、実装に進まず S00 を修正する。

### S01 Red: Epic template contract test
- `tests/unit/infra/test_init_update.py` に Epic templates の主要 fragment assertion を追加する。
- 期待する Red:
  - 現行 templates に `capability / model envelope`、`cross-Issue boundary`、`design slice catalog`、`Issue handoff package`、`suggested grade`、`final quality gate` などが不足して失敗する。
- 実行:
  - `uv run pytest tests/unit/infra/test_init_update.py -k spec_document_templates_keep_policy_out_of_scaffold`
- Closure:
  - C272-001..C272-007
- Delegation:
  - `dev-coder`。許可パスは `tests/unit/infra/test_init_update.py` のみ。
- Stop:
  - 新規 assertion が現行 template で成功する場合、Red evidence がないため停止する。

### S02 Green: Epic requirement template
- `src/spec_dock/assets/spec_dock/templates/epic/requirement.md` を更新する。
- `spec-dock/templates/epic/requirement.md` を同期する。
- 閉じる要件:
  - `I272-AC-001`, `I272-AC-004`, `I272-AC-005`, `I272-AC-006` の一部。
- Delegation:
  - `doc-writer`。許可パスは provider / mirror の Epic requirement template のみ。
- Stop:
  - runtime behavior、workflow docs、Issue template 変更が必要になった場合は停止して replan する。

### S03 Green: Epic design template
- `src/spec_dock/assets/spec_dock/templates/epic/design.md` を更新する。
- `spec-dock/templates/epic/design.md` を同期する。
- 閉じる要件:
  - `I272-AC-002`, `I272-AC-004`, `I272-AC-005`, `I272-AC-006` の一部。
- Delegation:
  - `doc-writer`。許可パスは provider / mirror の Epic design template のみ。
- Stop:
  - DDD / EDA mandatory wording、private implementation design の必須化が必要に見えた場合は停止する。

### S04 Green: Epic plan template
- `src/spec_dock/assets/spec_dock/templates/epic/plan.md` を更新する。
- `spec-dock/templates/epic/plan.md` を同期する。
- 閉じる要件:
  - `I272-AC-003`, `I272-AC-004`, `I272-AC-005`, `I272-AC-006`, `I272-AC-007`。
- Delegation:
  - `doc-writer`。許可パスは provider / mirror の Epic plan template のみ。
- Stop:
  - Issue handoff package が workflow docs / runtime change なしに表現できない場合は停止する。

### S05 Refactor / parity
- provider templates と dogfooding mirror の差分がないことを確認する。
- template wording を日本語ファーストに整え、policy の長文複製を避ける。
- dogfooding 固有 Issue ID、mandatory DDD / EDA、Issue-level TDD、private design、dangling scope-layering link がないことを確認する。
- Delegation:
  - main orchestrator。必要に応じて read-only reviewer を使う。
- Stop:
  - provider / mirror mismatch、forbidden wording、dangling link が残る場合は S02-S04 へ戻る。

### S90 検証
- Focused test:
  - `uv run pytest tests/unit/infra/test_init_update.py -k spec_document_templates_keep_policy_out_of_scaffold`
- Mirror parity:
  - `uv run pytest tests/unit/infra/test_init_update.py -k checked_in_dogfooding_mirror_templates_match_provider_assets`
- SpecDock validation:
  - `./spec-dock/scripts/spec-dock validate`
- Targeted inspection:
  - `rg -n "iss-00272|iss-00273|^## [A-Za-z]|docs/authoring/scope-layering\.md|mandatory DDD|mandatory EDA|TDD cycle|private class / file design" src/spec_dock/assets/spec_dock/templates/epic spec-dock/templates/epic tests/unit/infra/test_init_update.py`

### S99 完了ゲート
- report に Red / Green / Refactor、検証コマンド、未実施理由、残リスクを記録する。
- `spec-reviewer` で要件・設計・計画・実装差分の整合性を確認する。
- 実装差分があるため `code-reviewer` または `qa-reviewer` によるレビューを通す。
- PR は作らず、完了後に `issue finish` で `iss-00273` へ進む。

## 具体テストケース
| テストID | 対象 | 目的 | コマンド / 観測 |
|---|---|---|---|
| T272-001 | Epic template contract | `requirement` / `design` / `plan` template が Epic handoff prompts を持つことを確認する。 | `uv run pytest tests/unit/infra/test_init_update.py -k spec_document_templates_keep_policy_out_of_scaffold` |
| T272-002 | provider / dogfooding parity | provider templates と checked-in dogfooding mirror が一致することを確認する。 | `uv run pytest tests/unit/infra/test_init_update.py -k checked_in_dogfooding_mirror_templates_match_provider_assets` |
| T272-003 | SpecDock tree | active Issue と spec tree が構造的に妥当であることを確認する。 | `./spec-dock/scripts/spec-dock validate` |
| T272-004 | forbidden wording | dogfooding 固有 ID、mandatory DDD / EDA、Issue-level TDD、private design、dangling scope-layering link がないことを確認する。 | targeted `rg` inspection |

## 報告証跡の記録先
| 証跡 | 記録先 |
|---|---|
| S00 planning normalization / reviewer pass | `report.md#Spec Authoring Gate` |
| Red / Green / Refactor 実行結果 | `report.md#Step Evidence` |
| テストコマンド結果 | `report.md#検証` |
| reviewer verdict | `report.md#Reviewer Gate Status` |
| Issue完了判断 | `report.md#完了--PR` |

## Reviewer obligations
- `spec-reviewer`: 正本 requirement / design / plan / report と template diff の整合性を確認する。
- `code-reviewer`: tests または scaffold behavior assertion を変更した場合に、実装差分とテストの妥当性を確認する。
- `qa-reviewer`: 検証範囲が Issue acceptance criteria を十分に覆っているかを確認する。

## 受け入れ条件とステップ対応
| 要件 | 主ステップ | 検証 |
|---|---|---|
| `I272-AC-001` | S01, S02 | focused assertion / template read-through |
| `I272-AC-002` | S01, S03 | focused assertion / template read-through |
| `I272-AC-003` | S01, S04 | focused assertion / template read-through |
| `I272-AC-004` | S02-S05 | grep / reviewer |
| `I272-AC-005` | S02-S05 | focused assertion / reviewer |
| `I272-AC-006` | S02-S05 | Japanese-primary test / reviewer |
| `I272-AC-007` | S04-S05 | focused assertion / reviewer |

## バトン出力
- `iss-00273` が workflow docs / skills / reference へ接続する Epic handoff 語彙。
- `iss-00274` が readiness inspection の入力にできる Issue handoff package。
- `iss-00276` が final PR description に含められる Issue完了証跡。
