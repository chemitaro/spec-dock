---
種別: 実装計画書
機能ID: "q-018"
機能名: "bus request typed responses"
関連Issue: ["なし（current discussion / adr 起点）"]
状態: "draft"
作成者: "codex"
最終更新: "2026-03-10"
依存: ["requirement.md", "design.md"]
---

# q-018 bus request typed responses — 実装計画（TDD: Red → Green → Refactor）

## この計画で満たす要件ID (必須)
- 対象AC: AC-001, AC-002, AC-003, AC-004, AC-005
- 対象EC: EC-001, EC-002, EC-003
- 対象制約（該当があれば）:
  - runtime dispatch / HTTP 契約を変えない
  - helper / overload へ逃がさない
  - 局所 `cast` は infrastructure 内に限定する
  - Query / Message を段階的に進め、節目ごとにコミットとレビューを行う

## ステップ一覧（観測可能な振る舞い） (必須)
- [ ] S01: Query core の generic 契約が shared 層で成立し、shared QueryBus テストが通る
- [ ] S02: concrete Query / BC wrapper / endpoint call site から `cast` が消え、Query フェーズのレビューが通る
- [ ] S03: MessageBus の `CommandEnvelope[..., ResultT]` 前提が小さな spike で成立し、実装着手可否が確定する
- [ ] S04: Message core の generic 契約が shared messaging 層で成立し、unit / typing check が通る
- [ ] S05: concrete Command handler / UoW stub / integration tests が新契約に追従し、Message フェーズのレビューが通る
- [ ] S06: 全差分に対する品質ゲート（code review / QA / spec review / テスト）が通る

## ネスト運用ルール (必須)
- 各ステップ配下のサブステップとサブサブステップは、実施任意ではなく計画上の必須実行単位として扱う
- S01〜S05 は TDD を前提とし、各サブステップとサブサブステップに `Red / Green / Refactor` の所属を明示する
- S06 は品質ゲート工程のため、TDD ではなく `検証 / 是正 / 再検証` サイクルとして扱う

### 要件 ↔ ステップ対応表 (必須)
- AC-001 → S01, S02
- AC-002 → S01
- AC-003 → S03, S04, S05
- AC-004 → S01, S04
- AC-005 → S02, S05, S06
- EC-001 → S01, S04
- EC-002 → S02, S03, S05, S06
- EC-003 → S01, S04, S06
- 非交渉制約（runtime 契約維持） → S01, S04, S06
- 非交渉制約（局所 `cast` 制限） → S01, S04, S06

## レビュー / QA ゲート方針 (必須)
- R1（Query 実装レビュー）:
  - タイミング: S02 完了時
  - 担当: `code_reviewer`
  - レビュー範囲:
    - `taikyohiyou_management_api/shared/app_services/queries/query_base.py`
    - `taikyohiyou_management_api/shared/app_services/queries/interfaces.py`
    - `taikyohiyou_management_api/shared/app_services/query_bus/interfaces.py`
    - `taikyohiyou_management_api/shared/app_services/query_bus/base_bus.py`
    - `taikyohiyou_management_api/shared/app_services/query_bus/base_registry.py`
    - `taikyohiyou_management_api/shared/app_services/query_bus/contributions.py`
    - `taikyohiyou_management_api/authentication/app_services/query_bus/interfaces.py`
    - `taikyohiyou_management_api/authentication/app_services/query_bus/bus.py`
    - `taikyohiyou_management_api/authentication/app_services/query_bus/registry.py`
    - `taikyohiyou_management_api/sample/app_services/query_bus/interfaces.py`
    - `taikyohiyou_management_api/sample/app_services/query_bus/bus.py`
    - `taikyohiyou_management_api/sample/app_services/query_bus/registry.py`
    - `taikyohiyou_management_api/taikyohiyou/app_services/query_bus/interfaces.py`
    - `taikyohiyou_management_api/taikyohiyou/app_services/query_bus/bus.py`
    - `taikyohiyou_management_api/taikyohiyou/app_services/query_bus/registry.py`
    - `taikyohiyou_management_api/toolkit/app_services/query_bus/interfaces.py`
    - `taikyohiyou_management_api/toolkit/app_services/query_bus/bus.py`
    - `taikyohiyou_management_api/toolkit/app_services/query_bus/registry.py`
    - `taikyohiyou_management_api/toolkit/app_services/queries/get_outbox_config_query.py`
    - `taikyohiyou_management_api/toolkit/app_services/handlers/query_handlers/get_outbox_config_query_handler.py`
    - `taikyohiyou_management_api/sample/app_services/queries/get_sample_aggregate_read_model_query.py`
    - `taikyohiyou_management_api/sample/app_services/handlers/query_handlers/get_sample_aggregate_read_model_query_handler.py`
    - `taikyohiyou_management_api/toolkit/infras/api/endpoints/outbox_read_endpoint.py`
    - `taikyohiyou_management_api/toolkit/tests/unit/app_services/queries/test_outbox_query_bus_dispatch.py`
    - `taikyohiyou_management_api/sample/tests/unit/app_services/queries/test_sample_query_bus_dispatch.py`
    - `taikyohiyou_management_api/shared/tests/unit/app_services/query_bus/test_query_bus.py`
    - `taikyohiyou_management_api/shared/tests/unit/app_services/query_bus/test_query_bus_interfaces.py`
    - `taikyohiyou_management_api/shared/tests/unit/app_services/query_bus/test_query_handler_registry.py`
    - `taikyohiyou_management_api/shared/tests/unit/app_services/query_bus/test_query_handler_contributions.py`
    - `taikyohiyou_management_api/shared/tests/unit/app_services/query_bus/test_query_bus_di_responsibility.py`
    - `taikyohiyou_management_api/toolkit/tests/unit/app_services/handlers/query_handlers/test_get_outbox_config_query_handler.py`
- R2（Message 実装レビュー）:
  - タイミング: S05 完了時
  - 担当: `code_reviewer`
  - レビュー範囲:
    - `taikyohiyou_management_api/shared/app_services/messaging/envelopes.py`
    - `taikyohiyou_management_api/shared/app_services/messaging/interfaces.py`
    - `taikyohiyou_management_api/shared/app_services/messaging/bus.py`
    - `taikyohiyou_management_api/shared/app_services/messaging/handler_registry_if.py`
    - `taikyohiyou_management_api/shared/app_services/messaging/handler_registry.py`
    - `taikyohiyou_management_api/shared/app_services/messaging/handler_contributions.py`
    - `taikyohiyou_management_api/shared/app_services/handlers/command_handlers/abstract_command_handler_base.py`
    - `taikyohiyou_management_api/management_core/messaging/handler_registry_builder.py`
    - `taikyohiyou_management_api/sample/app_services/interfaces/sample_increment_command_handler_if.py`
    - `taikyohiyou_management_api/sample/app_services/handlers/command_handlers/sample_increment_command_handler.py`
    - `taikyohiyou_management_api/shared/tests/unit/app_services/messaging/test_message_bus.py`
    - `taikyohiyou_management_api/shared/tests/unit/app_services/messaging/test_handler_registry.py`
    - `taikyohiyou_management_api/shared/tests/unit/app_services/messaging/test_handler_registry_merge.py`
    - `taikyohiyou_management_api/shared/tests/unit/app_services/messaging/test_envelopes.py`
    - `taikyohiyou_management_api/shared/tests/integration/infras/di_container/test_message_bus_observability_wiring.py`
    - `taikyohiyou_management_api/shared/tests/unit/infras/uow/test_abstract_unit_of_work.py`
    - `taikyohiyou_management_api/shared/tests/unit/infras/uow/test_unit_of_work_factory.py`
    - `taikyohiyou_management_api/shared/tests/unit/infras/uow/test_seen_aggregate_collection.py`
    - `taikyohiyou_management_api/shared/tests/integration/infras/inbox/test_inbox_idempotency_integration.py`
    - `taikyohiyou_management_api/authentication/tests/unit/infras/uow/test_authentication_unit_of_work.py`
    - `taikyohiyou_management_api/sample/tests/unit/infras/uow/test_sample_unit_of_work.py`
    - `taikyohiyou_management_api/sample/tests/integration/infras/uow/test_eventing_unit_of_work_integration.py`
    - `taikyohiyou_management_api/taikyohiyou/tests/unit/infras/uow/test_taikyohiyou_unit_of_work.py`
    - `taikyohiyou_management_api/sample/tests/unit/app_services/handlers/command_handler_result_typing_check.py`
- QG-1（QA テスト観点レビュー）:
  - タイミング: S05 完了後、S06 内
  - 担当: `qa_engineer`
  - レビュー範囲:
    - `taikyohiyou_management_api/toolkit/tests/unit/app_services/queries/test_outbox_query_bus_dispatch.py`
    - `taikyohiyou_management_api/sample/tests/unit/app_services/queries/test_sample_query_bus_dispatch.py`
    - `taikyohiyou_management_api/shared/tests/unit/app_services/query_bus/test_query_bus.py`
    - `taikyohiyou_management_api/shared/tests/unit/app_services/query_bus/test_query_bus_interfaces.py`
    - `taikyohiyou_management_api/shared/tests/unit/app_services/query_bus/test_query_handler_registry.py`
    - `taikyohiyou_management_api/shared/tests/unit/app_services/query_bus/test_query_handler_contributions.py`
    - `taikyohiyou_management_api/shared/tests/unit/app_services/query_bus/test_query_bus_di_responsibility.py`
    - `taikyohiyou_management_api/toolkit/tests/unit/app_services/handlers/query_handlers/test_get_outbox_config_query_handler.py`
    - `taikyohiyou_management_api/shared/tests/unit/app_services/messaging/test_message_bus.py`
    - `taikyohiyou_management_api/shared/tests/unit/app_services/messaging/test_handler_registry.py`
    - `taikyohiyou_management_api/shared/tests/unit/app_services/messaging/test_handler_registry_merge.py`
    - `taikyohiyou_management_api/shared/tests/unit/app_services/messaging/test_envelopes.py`
    - `taikyohiyou_management_api/shared/tests/integration/infras/di_container/test_message_bus_observability_wiring.py`
    - `taikyohiyou_management_api/shared/tests/unit/infras/uow/test_abstract_unit_of_work.py`
    - `taikyohiyou_management_api/shared/tests/unit/infras/uow/test_unit_of_work_factory.py`
    - `taikyohiyou_management_api/shared/tests/unit/infras/uow/test_seen_aggregate_collection.py`
    - `taikyohiyou_management_api/shared/tests/integration/infras/inbox/test_inbox_idempotency_integration.py`
    - `taikyohiyou_management_api/authentication/tests/unit/infras/uow/test_authentication_unit_of_work.py`
    - `taikyohiyou_management_api/sample/tests/unit/infras/uow/test_sample_unit_of_work.py`
    - `taikyohiyou_management_api/sample/tests/integration/infras/uow/test_eventing_unit_of_work_integration.py`
    - `taikyohiyou_management_api/taikyohiyou/tests/unit/infras/uow/test_taikyohiyou_unit_of_work.py`
    - `taikyohiyou_management_api/sample/tests/unit/app_services/handlers/command_handler_result_typing_check.py`
    - `test strategy` と AC/EC の対応
  - 観点:
    - テスト不足の有無
    - 境界条件 / 回帰条件 / typing check の不足
    - flaky / 過不足ある検証の洗い出し
- QG-2（最終 spec review）:
  - タイミング: S06 終盤
  - 担当: `spec_reviewer`
  - レビュー範囲:
    - `develop...chemitaro/issue1730` の差分全体
    - requirement / design との整合
    - このブランチで変更したファイルすべて
  - 観点:
    - 要件達成
    - 設計逸脱の有無
    - 不自然なコード / スコープ逸脱 / 未反映 spec の有無

---

## 実装ステップ（各ステップは“観測可能な振る舞い”を1つ） (必須)

## ネスト方針（実装者向け） (必須)
- トップレベルステップ `Sxx` は「観測可能な成果」で分ける
- サブステップは `作業ブロック` とし、同じ関心事や同じ変更境界を持つ小仕事の束で分ける
- サブサブステップは `イテレーション` とし、1つの `Red → Green → Refactor` を完結できる最小単位で分ける
- したがって、`作業ブロック1 = Red`, `作業ブロック2 = Green`, `作業ブロック3 = Refactor` の固定対応は採らない
- 1つの作業ブロックの中で、必要な回数だけ小さな TDD サイクルを繰り返す
- S06 は新規実装ではなく品質ゲート工程なので、`検証 → 是正 → 再検証` を最小単位とする

### S01 — Query core の generic 契約が shared 層で成立し、shared QueryBus テストが通る (必須)
- 対象: AC-002 / AC-004 / EC-001 / EC-003
- 設計参照:
  - 対象IF/API: IF-001, IF-002, IF-003, IF-004
  - 対象テスト:
    - `taikyohiyou_management_api/shared/tests/unit/app_services/query_bus/test_query_bus.py`
    - `taikyohiyou_management_api/shared/tests/unit/app_services/query_bus/test_query_bus_interfaces.py`
    - `taikyohiyou_management_api/shared/tests/unit/app_services/query_bus/test_query_handler_registry.py`
    - `taikyohiyou_management_api/shared/tests/unit/app_services/query_bus/test_query_handler_contributions.py`
    - `taikyohiyou_management_api/shared/tests/unit/app_services/query_bus/test_query_bus_di_responsibility.py`
- このステップで「追加しないこと（スコープ固定）」:
  - concrete Query / endpoint / MessageBus には踏み込まない

#### update_plan（着手時に登録） (必須)
- [ ] `update_plan` に、このステップの作業ブロックを登録した
- 登録する作業ブロック:
  - S01-B1: Query model / interface generic 化
  - S01-B2: registry resolve 契約と internal cast 境界整理
  - S01-B3: base bus / contribution wiring 完結
  - S01-B4: shared Query 品質ゲート / 報告 / コミット

#### 期待する振る舞い（テストケース） (必須)
- Given: shared QueryBus core が generic 化されている
- When: registered query を `BaseQueryBus.ask()` に渡す
- Then: handler dispatch と戻り値型契約が保たれ、未登録 query や handler 例外の既存挙動も維持される
- 観測点（UI/HTTP/DB/Log など）: shared QueryBus unit tests / mypy
- 追加/更新するテスト:
  - `shared/tests/unit/app_services/query_bus/test_query_bus.py`
  - `shared/tests/unit/app_services/query_bus/test_query_bus_interfaces.py`
  - `shared/tests/unit/app_services/query_bus/test_query_handler_registry.py`
  - `shared/tests/unit/app_services/query_bus/test_query_handler_contributions.py`
  - `shared/tests/unit/app_services/query_bus/test_query_bus_di_responsibility.py`

#### 作業ブロック（必須）
- S01-B1: Query model / interface generic 化
  - S01-B1-I1:
    - Red: `QueryBase[OutputT]` と `QueryHandlerIf[QueryT, OutputT]` を前提に interface tests / typing expectation を失敗させる
    - Green: `query_base.py` と `queries/interfaces.py` を最小変更で generic 化する
    - Refactor: TypeVar 名、bound、import 位置を整える
  - S01-B1-I2:
    - Red: `QueryBusIf.ask(query) -> OutputT` を前提に interface tests を失敗させる
    - Green: `query_bus/interfaces.py` を更新して ask の public contract を固定する
    - Refactor: IF 命名と docstring / comment の冗長さを整理する
- S01-B2: registry resolve 契約と internal cast 境界整理
  - S01-B2-I1:
    - Red: `QueryHandlerRegistryIf.resolve()` の output 型保持を前提に registry tests を失敗させる
    - Green: `query_bus/interfaces.py` と `base_registry.py` の resolve 契約を最小変更で通す
    - Refactor: public contract と implementation escape hatch を分離し、局所 `cast` を registry 実装内部へ閉じ込める
  - S01-B2-I2:
    - Red: DI 責務テストで registry / bus の責務分離が崩れないことを失敗で固定する
    - Green: `test_query_bus_di_responsibility.py` が通るよう wiring を整える
    - Refactor: runtime behavior 差分が出ていないことを確認する
- S01-B3: base bus / contribution wiring 完結
  - S01-B3-I1:
    - Red: bus dispatch tests と contribution tests を失敗させる
    - Green: `base_bus.py` と `contributions.py` を更新して dispatch を通す
    - Refactor: contribution 側の generic 受け渡しと import 循環を整理する
- S01-B4: shared Query 品質ゲート / 報告 / コミット
  - S01-B4-I1:
    - Red: 該当なし
    - Green: shared QueryBus 系テストと mypy を実行して green を確認する
    - Refactor: `.spec-dock/current/report.md` を更新し、`C1: shared query core 完了` のコミット境界を確定する

#### ステップ末尾（省略しない） (必須)
- [ ] shared QueryBus 系テストと mypy を実行し、成功した
- [ ] `.spec-dock/current/report.md` に記録した
- [ ] `update_plan` を更新した
- [ ] `C1: shared query core 完了` のコミットを作成した

### S02 — concrete Query / BC wrapper / endpoint call site から `cast` が消え、Query フェーズのレビューが通る (必須)
- 対象: AC-001 / AC-005 / EC-002
- 設計参照:
  - 対象IF/API: IF-005, IF-006, IF-007
  - 対象テスト:
    - `taikyohiyou_management_api/toolkit/tests/unit/app_services/queries/test_outbox_query_bus_dispatch.py`
    - `taikyohiyou_management_api/sample/tests/unit/app_services/queries/test_sample_query_bus_dispatch.py`
    - `taikyohiyou_management_api/toolkit/tests/unit/app_services/handlers/query_handlers/test_get_outbox_config_query_handler.py`
    - 必要なら endpoint 回帰テスト
- このステップで「追加しないこと（スコープ固定）」:
  - MessageBus core / handlers には踏み込まない

#### update_plan（着手時に登録） (必須)
- [ ] `update_plan` に、このステップの作業ブロックを登録した
- 登録する作業ブロック:
  - S02-B1: concrete Query / handler の型追従
  - S02-B2: BC wrapper 群の追従
  - S02-B3: endpoint cast 除去
  - S02-B4: Query フェーズ review / 報告 / コミット

#### 期待する振る舞い（テストケース） (必須)
- Given: concrete Query / handler / BC wrapper が新 generic 契約へ追従している
- When: `GetOutboxConfigQuery` を toolkit QueryBus から呼び出す
- Then: endpoint と tests から `cast` が消え、具体 output をそのまま扱える
- 観測点（UI/HTTP/DB/Log など）: toolkit query tests / endpoint code / code review
- 追加/更新するテスト:
  - `toolkit/tests/unit/app_services/queries/test_outbox_query_bus_dispatch.py`
  - `sample/tests/unit/app_services/queries/test_sample_query_bus_dispatch.py`
  - `toolkit/tests/unit/app_services/handlers/query_handlers/test_get_outbox_config_query_handler.py`

#### 作業ブロック（必須）
- S02-B1: concrete Query / handler の型追従
  - S02-B1-I1:
    - Red: `GetOutboxConfigQuery` と sample Query contract を新 generic 契約前提に更新し、dispatch tests を失敗させる
    - Green: concrete Query 定義と handler 戻り値型を最小変更で具体化する
    - Refactor: query output type alias や import 順を整理する
  - S02-B1-I2:
    - Red: handler unit tests が旧シグネチャ依存で落ちる状態を作る
    - Green: concrete handler 実装を新契約へ追従させる
    - Refactor: handler signature の冗長型注釈を整理する
- S02-B2: BC wrapper 群の追従
  - S02-B2-I1:
    - Red: authentication / sample / taikyohiyou / toolkit の wrapper 呼び出しが新契約未追従で落ちる状態を作る
    - Green: 各 query_bus wrapper の interface / bus / registry を追従させる
    - Refactor: wrapper 間で揃えるべき generic 記述を統一する
- S02-B3: endpoint cast 除去
  - S02-B3-I1:
    - Red: endpoint 回帰確認で `cast(...)` 前提のコードを失敗として固定する
    - Green: `outbox_read_endpoint.py` から `cast(...)` を除去し、具体 output を直接扱う
    - Refactor: endpoint 内ローカル変数名と戻り値整形を読みやすく整える
- S02-B4: Query フェーズ review / 報告 / コミット
  - S02-B4-I1:
    - Red: 該当なし
    - Green: Query フェーズのテスト / mypy を実行して green を確認する
    - Refactor: R1 code review の範囲を固定し、指摘反映後に `.spec-dock/current/report.md` を更新して `C2` を確定する

#### ステップ末尾（省略しない） (必須)
- [ ] Query フェーズのテスト / mypy を実行し、成功した
- [ ] R1 code review を実施し、指摘対応まで完了した
- [ ] `.spec-dock/current/report.md` に記録した
- [ ] `update_plan` を更新した
- [ ] `C2: query call site / concrete query 完了` のコミットを作成した

### S03 — MessageBus の `CommandEnvelope[..., ResultT]` 前提が小さな spike で成立し、実装着手可否が確定する (必須)
- 対象: AC-003 / EC-002
- 設計参照:
  - 対象IF/API: IF-008, IF-009
  - 対象テスト:
    - `taikyohiyou_management_api/sample/tests/unit/app_services/handlers/command_handler_result_typing_check.py`
    - 必要なら一時的 typing check
- このステップで「追加しないこと（スコープ固定）」:
  - Message 全体の本実装完了までは進めない

#### update_plan（着手時に登録） (必須)
- [ ] `update_plan` に、このステップの作業ブロックを登録した
- 登録する作業ブロック:
  - S03-B1: envelope / bus / registry 仮説の成立確認
  - S03-B2: 周辺依存の破綻点調査
  - S03-B3: spike 結果整理 / コミット

#### 期待する振る舞い（テストケース） (必須)
- Given: MessageBus は `CommandEnvelope` を bus request として使う
- When: `CommandEnvelope[..., ResultT]` を前提に最小の型検証を行う
- Then: 現行 stack で本実装に進めるか、どのファイルが本変更のボトルネックかが明確になる
- 観測点（UI/HTTP/DB/Log など）: typing check 結果 / 変更量確認メモ
- 追加/更新するテスト:
  - `sample/tests/unit/app_services/handlers/command_handler_result_typing_check.py`

#### 作業ブロック（必須）
- S03-B1: envelope / bus / registry 仮説の成立確認
  - S03-B1-I1:
    - Red: `CommandEnvelope[..., ResultT]` を前提とした typing check を作り、現状失敗を観測する
    - Green: envelope / bus / registry 仮説に対する最小スパイクを当てる
    - Refactor: 仮説のうち成立した契約と成立しなかった契約を分けて記録する
- S03-B2: 周辺依存の破綻点調査
  - S03-B2-I1:
    - Red: UoW スタブ群と observability wiring の破綻箇所を失敗ログとして固定する
    - Green: 本実装で必要になる変更境界を確認できる程度まで最小追従する
    - Refactor: exact file set とリスクメモへ整理する
- S03-B3: spike 結果整理 / コミット
  - S03-B3-I1:
    - Red: 該当なし
    - Green: feasibility 結果を本実装着手判断に必要な粒度へ整理する
    - Refactor: `.spec-dock/current/report.md` を更新し、`C3: message carrier feasibility spike 完了` を確定する

#### ステップ末尾（省略しない） (必須)
- [ ] feasibility 結果を記録した
- [ ] `.spec-dock/current/report.md` に記録した
- [ ] `update_plan` を更新した
- [ ] `C3: message carrier feasibility spike 完了` のコミットを作成した

### S04 — Message core の generic 契約が shared messaging 層で成立し、unit / typing check が通る (必須)
- 対象: AC-003 / AC-004 / EC-001 / EC-003
- 設計参照:
  - 対象IF/API: IF-008, IF-009
  - 対象テスト:
    - `taikyohiyou_management_api/shared/tests/unit/app_services/messaging/test_message_bus.py`
    - `taikyohiyou_management_api/shared/tests/unit/app_services/messaging/test_handler_registry.py`
    - `taikyohiyou_management_api/shared/tests/unit/app_services/messaging/test_handler_registry_merge.py`
    - `taikyohiyou_management_api/shared/tests/unit/app_services/messaging/test_envelopes.py`
- このステップで「追加しないこと（スコープ固定）」:
  - concrete command handlers / UoW スタブまで広げすぎない

#### update_plan（着手時に登録） (必須)
- [ ] `update_plan` に、このステップの作業ブロックを登録した
- 登録する作業ブロック:
  - S04-B1: envelope / interface public contract 固定
  - S04-B2: registry / bus core 追従
  - S04-B3: builder / abstract base / contribution 整理
  - S04-B4: shared Message 品質ゲート / 報告 / コミット

#### 期待する振る舞い（テストケース） (必須)
- Given: Message core が `CommandEnvelope[..., ResultT]` を bus request として扱う
- When: `message_bus.send(command_envelope)` を呼ぶ
- Then: bus / registry / handler IF の public API で `ResultT` が保持され、shared messaging tests が通る
- 観測点（UI/HTTP/DB/Log など）: shared messaging unit tests / mypy
- 追加/更新するテスト:
  - `shared/tests/unit/app_services/messaging/test_message_bus.py`
  - `shared/tests/unit/app_services/messaging/test_handler_registry.py`
  - `shared/tests/unit/app_services/messaging/test_handler_registry_merge.py`
  - `shared/tests/unit/app_services/messaging/test_envelopes.py`

#### 作業ブロック（必須）
- S04-B1: envelope / interface public contract 固定
  - S04-B1-I1:
    - Red: `test_envelopes.py` と interface 期待値を更新して envelope generic を失敗させる
    - Green: `envelopes.py` と `interfaces.py` を最小変更で generic 化する
    - Refactor: envelope 型引数順と alias を統一する
  - S04-B1-I2:
    - Red: `MessageBusIf.send(...) -> ResultT` を前提に message bus interface tests を失敗させる
    - Green: bus public API の戻り型契約を固定する
    - Refactor: handler IF / bus IF 間の TypeVar 命名を統一する
- S04-B2: registry / bus core 追従
  - S04-B2-I1:
    - Red: `test_handler_registry.py` / `test_handler_registry_merge.py` を更新して registry generic 未追従を失敗させる
    - Green: `handler_registry_if.py` と `handler_registry.py` を追従させる
    - Refactor: internal `cast` を registry 実装内部へ限定する
  - S04-B2-I2:
    - Red: `test_message_bus.py` を更新して dispatch の戻り型保持失敗を観測する
    - Green: `bus.py` を更新して send の generic dispatch を通す
    - Refactor: runtime dispatch を変えずに型境界だけを整理する
- S04-B3: builder / abstract base / contribution 整理
  - S04-B3-I1:
    - Red: builder / abstract base の追従漏れを失敗として観測する
    - Green: `handler_registry_builder.py` と `abstract_command_handler_base.py` を追従させる
    - Refactor: `handler_contributions.py` を含め、shared core の型契約を review しやすく整える
- S04-B4: shared Message 品質ゲート / 報告 / コミット
  - S04-B4-I1:
    - Red: 該当なし
    - Green: shared messaging tests と mypy を実行して green を確認する
    - Refactor: `.spec-dock/current/report.md` を更新し、`C4: shared message core 完了` を確定する

#### ステップ末尾（省略しない） (必須)
- [ ] shared messaging tests と mypy を実行し、成功した
- [ ] `.spec-dock/current/report.md` に記録した
- [ ] `update_plan` を更新した
- [ ] `C4: shared message core 完了` のコミットを作成した

### S05 — concrete Command handler / UoW stub / integration tests が新契約に追従し、Message フェーズのレビューが通る (必須)
- 対象: AC-003 / AC-005 / EC-002
- 設計参照:
  - 対象IF/API: IF-008, IF-009
  - 対象テスト:
    - `taikyohiyou_management_api/sample/tests/unit/app_services/handlers/command_handler_result_typing_check.py`
    - `taikyohiyou_management_api/shared/tests/integration/infras/di_container/test_message_bus_observability_wiring.py`
    - UoW stub test 群
- このステップで「追加しないこと（スコープ固定）」:
  - spec の追加変更は行わない

#### update_plan（着手時に登録） (必須)
- [ ] `update_plan` に、このステップの作業ブロックを登録した
- 登録する作業ブロック:
  - S05-B1: representative command handler / IF 追従
  - S05-B2: UoW stub / observability / integration 追従
  - S05-B3: Message フェーズ review / 報告 / コミット

#### 期待する振る舞い（テストケース） (必須)
- Given: Message core が新契約に更新されている
- When: representative command handler と UoW / integration path を実行する
- Then: concrete handler・observability wiring・UoW stub 群が新契約に追従し、`message_bus.send(command_envelope)` の戻り型前提が崩れない
- 観測点（UI/HTTP/DB/Log など）: Message integration tests / code review
- 追加/更新するテスト:
  - `sample/tests/unit/app_services/handlers/command_handler_result_typing_check.py`
  - `shared/tests/integration/infras/di_container/test_message_bus_observability_wiring.py`
  - `shared/tests/unit/infras/uow/test_abstract_unit_of_work.py`
  - `shared/tests/unit/infras/uow/test_unit_of_work_factory.py`
  - `shared/tests/unit/infras/uow/test_seen_aggregate_collection.py`
  - `shared/tests/integration/infras/inbox/test_inbox_idempotency_integration.py`
  - `authentication/tests/unit/infras/uow/test_authentication_unit_of_work.py`
  - `sample/tests/unit/infras/uow/test_sample_unit_of_work.py`
  - `sample/tests/integration/infras/uow/test_eventing_unit_of_work_integration.py`
  - `taikyohiyou/tests/unit/infras/uow/test_taikyohiyou_unit_of_work.py`

#### 作業ブロック（必須）
- S05-B1: representative command handler / IF 追従
  - S05-B1-I1:
    - Red: representative command handler と handler IF を新契約前提に更新し、旧シグネチャ依存を失敗として固定する
    - Green: `sample_increment_command_handler.py` と IF を最小変更で追従させる
    - Refactor: handler result 型記述と command envelope 受け渡しを読みやすく整える
  - S05-B1-I2:
    - Red: `command_handler_result_typing_check.py` で call site の戻り型保持失敗を観測する
    - Green: handler result typing check を通す
    - Refactor: representative path の型サンプルとして読めるよう整理する
- S05-B2: UoW stub / observability / integration 追従
  - S05-B2-I1:
    - Red: observability wiring と integration tests を更新し、Message core 未追従を失敗として観測する
    - Green: `test_message_bus_observability_wiring.py` と関連 wiring を通す
    - Refactor: observability 側の補助コードと変数名を整理する
  - S05-B2-I2:
    - Red: UoW stub 群の unit / integration tests を更新し、旧契約依存を失敗として固定する
    - Green: authentication / sample / taikyohiyou / shared の UoW スタブ群を追従させる
    - Refactor: stub 間で重複する型注釈や helper を最小限に整理する
- S05-B3: Message フェーズ review / 報告 / コミット
  - S05-B3-I1:
    - Red: 該当なし
    - Green: Message フェーズの tests / mypy を実行して green を確認する
    - Refactor: R2 のレビュー範囲を固定し、指摘反映後に `.spec-dock/current/report.md` を更新して `C5` を確定する

#### ステップ末尾（省略しない） (必須)
- [ ] Message フェーズの tests / mypy を実行し、成功した
- [ ] R2 code review を実施し、指摘対応まで完了した
- [ ] `.spec-dock/current/report.md` に記録した
- [ ] `update_plan` を更新した
- [ ] `C5: message concrete / uow / integration 完了` のコミットを作成した

### S06 — 全差分に対する品質ゲート（code review / QA / spec review / テスト）が通る (必須)
- 対象: AC-005 / EC-002 / EC-003
- 設計参照:
  - 対象IF/API: 全体
  - 対象テスト: 全変更差分
- このステップで「追加しないこと（スコープ固定）」:
  - 新機能追加
  - 設計変更を伴う別 issue の混入

#### update_plan（着手時に登録） (必須)
- [ ] `update_plan` に、このステップの作業ブロックを登録した
- 登録する作業ブロック:
  - S06-B1: 全体検証
  - S06-B2: QA / spec review
  - S06-B3: 指摘是正 / 再検証 / コミット

#### 期待する振る舞い（テストケース） (必須)
- Given: Query / Message 両フェーズの実装が完了している
- When: 全体品質ゲートを実施する
- Then: tests / mypy / code review / QA / spec review がすべて pass し、`develop...chemitaro/issue1730` 差分全体で要件と設計を満たしている
- 観測点（UI/HTTP/DB/Log など）: テスト結果、QA 所見、spec review 判定
- 追加/更新するテスト:
  - 本ブランチで変更した全テスト

#### 作業ブロック（必須）
- S06-B1: 全体検証
  - S06-B1-I1:
    - 検証: targeted pytest 群をすべて実行する
    - 是正: 必要があれば軽微なテスト修正を反映する
    - 再検証: `mypy .` と必要なら lint を実行して全体 green を確認する
- S06-B2: QA / spec review
  - S06-B2-I1:
    - 検証: `qa_engineer` にテスト観点レビューを依頼する
    - 是正: テスト不足指摘があれば反映する
    - 再検証: テスト観点の再確認を行う
  - S06-B2-I2:
    - 検証: `spec_reviewer` に `develop...chemitaro/issue1730` diff 全体レビューを依頼する
    - 是正: requirement / design 逸脱があれば反映する
    - 再検証: diff 全体が spec と整合していることを確認する
- S06-B3: 指摘是正 / 再検証 / コミット
  - S06-B3-I1:
    - 検証: 最終差分、最終テスト、最終レビュー結果を突き合わせる
    - 是正: 残件があれば最後の微修正を行う
    - 再検証: `.spec-dock/current/report.md` を更新し、`C6: final quality gate 反映完了` を確定する

#### ステップ末尾（省略しない） (必須)
- [ ] 全体品質ゲートを実行し、成功した
- [ ] QA review と final spec review を pass した
- [ ] `.spec-dock/current/report.md` に記録した
- [ ] `update_plan` を更新した
- [ ] `C6: final quality gate 反映完了` のコミットを作成した

---

## 未確定事項（TBD） (必須)
- 該当なし

## 完了条件（Definition of Done） (必須)
- 対象AC/ECがすべて満たされ、テストとレビューで保証されている
- MUST NOT / OUT OF SCOPE を破っていない
- Query フェーズと Message フェーズの各節目でコミット・レビュー・報告が完了している
- `code_reviewer`, `qa_engineer`, `spec_reviewer` の最終ゲートが pass している
- `develop...chemitaro/issue1730` 差分全体で requirement / design と整合している

## 省略/例外メモ (必須)
- ネストした実行順序は、Markdown の見出しとサブステップ列挙で表現している。実際の `update_plan` は各ステップ着手時に同等粒度へ分解して登録する。
- S06 は品質ゲート工程のため、`Red / Green / Refactor` の新規機能開発サイクルではなく、`検証 / 是正 / 再検証` として運用する。
