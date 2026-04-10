---
種別: 要件定義書（Epic）
ID: "epic-00059"
タイトル: "Dependency metadata unification and command mutation"
関連GitHub: ["#59"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-04-10"
親: ["init-local-00003"]
---

# epic-00059 Dependency metadata unification and command mutation — 要件定義（WHAT / WHY）

## 目的（Initiative との紐づき）
- initiative goal / metric:
  - source-of-truth と persistence boundary を `deps.json` + `.meta.json` 分離から `.meta.json` 集約へ再定義し、architecture initiative の guardrail（SoT/境界/移行の明示）を満たす。
  - command 経由で安全に依存を変更できる contract を導入し、手編集による corruption risk を下げる。
- この epic が提供する能力:
  - dependency mutation command（add/remove 等）と validation を runtime contract として提供する。
  - dependency metadata の canonical storage を `.meta.json` に統合する。

## ユースケース
- happy path:
  - ユーザーは `spec-dock deps ...` の command で `depends on` を追加/削除できる。
  - command は更新内容を `.meta.json` に保存し、`validate` と `sync` が同じ依存状態を解釈する。
  - `deps add --from A --to B` は現行 graph の整合性確認が通った場合に限り、edge が既に存在していれば success/no-op として扱われ、`.meta.json` の dependency 配列に重複は保存されない。
- exception / operation scenario:
  - 未解決参照、自己依存、循環依存の追加要求は error として拒否される。
  - `deps remove` は対象 edge が不在なら error で終了し、warning/no-op にはしない。
  - `deps add` / `deps remove` は現行 graph が破損・不整合なら fail-closed error で終了し、duplicate-edge no-op より先に保存を拒否する。

## Epic requirements
- E-RQ-001:
  - dependency metadata の SoT を `.meta.json` に統一し、初回リリースで `deps.json` backward compatibility を廃止する。
- E-RQ-002:
  - command-based mutation contract（依存追加/削除/確認）を導入し、JSON 直編集を前提にしない運用へ移行する。`deps add` は現行 graph の整合性確認が通ったときだけ既存 edge を success/no-op とし、dependency 配列へ重複 edge を保存しない。
- E-RQ-003:
  - validation contract を強化し、未解決参照・自己依存・循環依存を mutation 時点で拒否する。
- E-RQ-004:
  - delete/sync/active/validate の各処理で依存参照の整合を維持し、保存境界変更後も同等の動作保証を提供する。

## Epic acceptance criteria
- E-AC-001 schema:
  - Given:
    - node metadata が `.meta.json` で管理されている。
  - When:
    - dependency を保持・読み取りする。
  - Then:
    - canonical schema が `.meta.json` に定義され、runtime は同 schema を唯一の SoT として解釈する。
  - 観測点:
    - schema docs、reader 実装、unit test が一致する。
- E-AC-002 command contract:
  - Given:
    - 利用者が dependency mutation command を実行し、runtime が mutation 前の current graph を読み込む。
  - When:
    - 有効な参照/無効な参照を入力する。
  - Then:
    - current graph が破損・不整合なら fail-closed error で終了し、`deps add` の duplicate-edge success/no-op には進まない。
    - 有効入力のみ保存され、未解決参照・自己依存・循環依存は明示 error で拒否される。
    - current graph が正常で `deps add` の既存 edge を指定した場合は success/no-op を返し、`.meta.json` の dependency 配列は非重複 invariant を維持する。
    - `deps remove` は edge 不在を明示 error として返し、契約を fail-closed に保つ。
  - 観測点:
    - CLI response / error code / message と integration test。
- E-AC-003 migration:
  - Given:
    - 既存 dogfooding workspace に legacy `deps.json` が残っている。
  - When:
    - T3 integration tranche で docs 更新、dogfooding checked-in data manual fix、`./spec-dock/scripts/spec-dock validate` / `sync` evidence 採取を実施し、entry 条件充足を確認したうえで hard cutover judgment を固定する。
  - Then:
    - runtime は `.meta.json` だけを SoT として扱い、`deps.json` の dual-read を持たない。
    - dogfooding 側は checked-in data を手動修正して cutover に追従し、整合が崩れない。
    - hard cutover judgment の primary evidence は T3 integration owner の issue-level `report.md` に集約され、docs 更新結果、dogfooding checked-in data manual fix 完了、`./spec-dock/scripts/spec-dock validate` / `sync` 実測結果、judgment verdict を reviewer が追跡できる。
    - T4 はこの judgment を前提に final regression / parity confirmation / spec review を行い、entry 条件自体は再充足対象にしない。
  - 観測点:
    - cutover docs、dogfooding manual fix 手順、T3 issue `report.md`、`validate` / `sync` 実測証跡、boundary/validation test。
- E-AC-004 delete scrub parity:
  - Given:
    - 削除対象 node を他 node が依存参照している。
  - When:
    - delete を実行する。
  - Then:
    - dangling dependency が scrub/検出され、保存状態に不整合を残さない。
  - 観測点:
    - `application/delete_node.py` 系テスト。
- E-AC-005 sync/active/validate parity:
  - Given:
    - T3 integration tranche で hard cutover judgment と entry 条件充足が記録済みで、active store / sync artifact / validate が同一 repo 状態を扱う。
  - When:
    - dependency mutation 後に T4 closure tranche で `set-active` / `sync` / `validate` を最終回帰と parity confirmation として実行する。
  - Then:
    - すべて同じ dependency graph を観測し、結果が一致する。
    - E-AC-005 の final closure owner は T4 closure owner とし、final parity / close review の primary evidence は T4 issue-level `report.md` に残り、epic `report.md` には close summary だけが転記される。
  - 観測点:
    - regression test、dogfooding 実測、T4 issue `report.md`、epic `report.md` close summary。

## スコープ
- MUST:
  - `.meta.json` dependency schema 定義。
  - dependency mutation command 追加。
  - downstream command（delete/sync/active/validate）の整合更新。
  - docs/templates/tests の更新。
- MUST NOT:
  - 削除済みの `epic-00058` を復元・再オープンして正本として扱うこと。
  - architecture initiative 外（`init-local-00002` 側）を正本化する変更。
- OUT OF SCOPE:
  - dependency priority や weight など新しい依存意味論。
  - GitHub issue lifecycle と無関係な別機能拡張。

## 境界
- Always:
  - SoT/persistence boundary/migration/contract impact を明示した上で変更する。
  - `deps.json` dual-read を増やさず、`.meta.json` 単一 SoT を維持する。
- Fixed:
  - `deps add` は current graph の整合性確認を先に実施し、graph が不正なら fail-closed error に固定する。graph が正常な場合だけ既存 edge 時レスポンスを success/no-op とし、`.meta.json` の dependency 配列に重複 edge を保存しない。
  - `deps remove` の edge 不在時レスポンスは error に固定する。
  - hard cutover judgment は T3 integration 完了時に固定する。
  - hard cutover entry 条件は docs 更新、dogfooding checked-in data manual fix、`./spec-dock/scripts/spec-dock validate` / `sync` evidence を必須にする。
  - cutover evidence の正本は issue-level `report.md` に置き、T3 issue が entry 条件の実施・充足・judgment 固定を記録し、T4 issue が E-AC-005 の final parity / spec review / close summary を記録する。
- Never:
  - validation を迂回して dependency を書き込まない。

## 非機能要件
- performance:
  - mutation/validate は既存 tree サイズで実用応答を維持する。
- reliability / consistency:
  - fail-closed、部分書き込み禁止、atomic write。
- security:
  - path traversal や不正 ID 文字列を拒否。
- operations:
  - hard cutover entry 条件と manual fix 完了状態を docs / validate / sync evidence で観測可能にする。
  - dogfooding manual fix は checked-in data の追従に限定し、runtime fallback や自動 migration は導入しない。

## 依存 / 影響範囲
- impacted components:
  - `infra/deps_reader.py`
  - `infra/fs_repo.py`
  - `application/delete_node.py`
  - `application/set_active.py`
  - `application/sync_state.py`
  - `application/validate_tree.py`
  - docs/templates/tests
- external dependency:
  - なし（repo 内 runtime/asset 更新）。
- compatibility:
  - 既存 `deps check` command surface は維持しつつ、`deps.json` backward compatibility は持たない。

## 未確定事項
- 現時点ではなし。
