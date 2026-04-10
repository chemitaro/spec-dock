---
種別: 設計書（Epic）
ID: "epic-00059"
タイトル: "Dependency metadata unification and command mutation"
関連GitHub: ["#59"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-04-10"
依存: ["requirement.md"]
親: ["init-local-00003"]
---

# epic-00059 Dependency metadata unification and command mutation — 設計（HOW）

## 全体像
- target boundary:
  - dependency SoT を `deps.json` から `.meta.json` へ寄せ、read/write と validation の責務を metadata 境界に統合する。
- impacted area:
  - runtime の reader/repo adapter/application flow（delete/set-active/sync/validate）と docs/templates/tests。
- existing relation:
  - 現状は `deps check` で読み取り検査のみ可能、mutation API が欠落している。

## 契約
### CLI command contract
- CMD-001 `spec-dock deps add --from <node> --to <node>`:
  - behavior:
    - `.meta.json` の dependency field を更新する。
    - mutation 前に current graph を検証し、破損・不整合なら fail-closed error で終了する。
    - current graph が正常で edge が既に存在する場合は success/no-op とし、response contract は `result=unchanged` を返す。
    - 新規 edge を追加する場合の参照不正/自己依存/循環依存は fail-closed error。
    - 新規 edge を追加した場合だけ `result=updated` を返し、dependency 配列へ重複 edge を書き込まない。
- CMD-002 `spec-dock deps remove --from <node> --to <node>`:
  - behavior:
    - `.meta.json` の dependency edge を削除する。
    - edge 不在は no-op にせず error を返し、mutation 未実施として扱う。
- CMD-003 `spec-dock deps check`:
  - behavior:
    - `.meta.json` SoT に基づき整合性検証を実行する。
    - legacy `deps.json` fallback read は持たず、cutover 前提から外れた checked-in data は manual fix 対象として案内する。

### Data boundary
- SoR:
  - `.meta.json` に dependency field を追加し canonical state とする。
- consistency model:
  - single-writer（command 経由）+ atomic write + validate-before-commit。
  - `deps add` は current graph validation を通過した場合に限って set-like semantics を取り、同一 node の dependency 配列に同一 target を 2 回以上保存しない。

## データモデル
- schema options:
  - Option A: `.meta.json` に `depends_on: ["node-id", ...]` を持つ（node 単位）。
  - Option B: `.meta.json` に `dependencies: {"from": ["to", ...]}` を持つ（graph 単位）。
- chosen direction:
  - Option A を採用。node metadata と同居させることで delete/sync/active の局所更新と整合しやすい。
- invariants:
  - node id は既存命名規則に一致。
  - `depends_on` は node ごとに重複なし配列で保持する。
  - self loop 不可。
  - unresolved target 不可。
  - cycle 不可（DAG 制約）。

## 主要フロー
- Flow-A add dependency:
  1. command parser が `from`/`to` を受理。
  2. `infra/deps_reader.py` が現行 graph を `.meta.json` から読み込み。
  3. current graph 自体を validate し、破損・不整合なら fail-closed error で終了する。
  4. current graph が正常で既存 edge なら保存せず `result=unchanged` を返す。
  5. 新規 edge の場合だけ domain validation が unresolved/self/cycle を検査する。
  6. `infra/fs_repo.py` が atomic write で保存する。
  7. success と変更差分を出力する。
- Flow-B remove dependency:
  1. edge の存在確認。
  2. edge 不在なら not-found error で終了し保存しない。
  3. 削除後 graph を validation。
  4. 保存し結果を出力。
- Flow-C delete node scrub:
  1. node 削除前に inbound dependency を抽出。
  2. scrub policy に従って除去。
  3. scrub 後 graph を validate して保存。

## 失敗設計
- failure mode:
  - parse error、node not found、edge not found、cycle detected、legacy cutover precondition miss、write failure。
- retry:
  - write failure 時のみ再実行可能（状態不変で終了）。
- idempotency:
  - add は current graph validation が通過した場合に限り、同一 edge に対して deterministic な success/no-op（`result=unchanged`）を返し、配列重複を発生させない。
  - remove は同一 edge に対して deterministic な結果を返すが、edge 不在時は success に丸めず error で固定する。
- partial failure:
  - 保存前に失敗した場合はファイル更新しない。

## 移行戦略
- migration policy:
  - hard cutover only:
    - runtime の read/write path は `.meta.json` のみを対象に実装する。
    - 初回リリースで `deps.json` reader/writer/compat code を一括で除去する。
    - dogfooding 側は checked-in data を手動修正して cutover に追従する。
- cutover gate:
  - hard cutover judgment は T3 integration 完了時に固定する。
  - T3 integration tranche が docs 更新、dogfooding checked-in data manual fix、`./spec-dock/scripts/spec-dock validate` / `sync` evidence 採取を実施し、entry 条件充足を確認してから judgment を固定する。
  - evidence owner / placement:
    - T3 integration owner の issue-level `report.md` を hard cutover judgment の正本にする。
    - T4 closure owner の issue-level `report.md` を E-AC-005 final closure と final parity / spec review の正本にし、epic `report.md` は close summary だけを保持する。
  - minimum evidence bundle:
    - docs 更新対象の差分要約。
    - dogfooding checked-in data manual fix 対象 path / scope。
    - targeted regression summary。
    - `./spec-dock/scripts/spec-dock validate` / `sync` の command line、exit code、結果要約。
    - cutover または final parity の verdict。
- dogfooding manual fix boundary:
  - manual fix 対象は checked-in data と runbook/doc 反映に限定する。
  - runtime 側で legacy `deps.json` を自動変換・救済する fallback は持たない。
- rollback:
  - feature flag や fallback reader は持たない。
  - rollback は issue 単位の差分 revert で扱い、旧 contract を runtime に戻さない。

## 影響コンポーネント
- `infra/deps_reader.py`:
  - `.meta.json` 読み取りと legacy artifact 検出。
- `infra/fs_repo.py`:
  - dependency field 更新/atomic write API。
- `application/delete_node.py`:
  - delete scrub の dependency cleanup。
- `application/set_active.py` / `application/sync_state.py` / `application/validate_tree.py`:
  - SoT 変更後の graph 解釈統一。
- docs/templates/tests:
  - 新 command 契約、schema、migration 手順、regression を反映。

## 観測性 / セキュリティ
- observability:
  - mutation 実行ログに `from/to/result/error-code` を出す。
  - cutover precondition miss 時に remediation message を出す。
- security:
  - node id の入力検証。
  - path injection 不可。

## テスト戦略
- Unit:
  - schema read/write、cycle/self/unresolved 検証、scrub ロジック。
- Integration:
  - command add/remove/check、delete/set-active/sync/validate parity。
- Regression:
  - legacy `deps.json` が残る workspace を dual-read せず manual fix に導く boundary シナリオ。
- E-AC mapping:
  - E-AC-001 -> schema reader/write test。
  - E-AC-002 -> command contract test（`result=updated|unchanged` と non-dup invariant を含む）。
  - E-AC-003 -> migration test + T3 issue `report.md` evidence bundle。
  - E-AC-004 -> delete scrub test。
  - E-AC-005 -> sync/active/validate parity test + T4 issue `report.md` / epic `report.md` close summary（T3 judgment fixed 後の final closure）。

## ロールバック / 運用
- rollback trigger:
  - cutover entry 条件未充足、unexpected cycle false positive。
- rollback action:
  - issue 単位で変更差分を戻す。fallback reader や read-only 退避は導入しない。
- operational guard:
  - T3 で docs 更新、dogfooding checked-in data manual fix、`validate` / `sync` evidence 採取を完了して cutover gate を閉じる。
  - T4 ではその judgment を前提に final regression / parity confirmation / spec review / close summary だけを行う。

## 未確定事項
- 現時点ではなし。
