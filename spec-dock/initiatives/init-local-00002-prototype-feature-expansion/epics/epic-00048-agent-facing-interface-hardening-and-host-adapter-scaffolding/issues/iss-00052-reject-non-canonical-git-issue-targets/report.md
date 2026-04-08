---
種別: 実装報告書（Issue）
ID: "iss-00052"
タイトル: "Reject Non Canonical Git Issue Targets"
関連GitHub: ["#52"]
状態: "draft"
作成者: "Codex"
最終更新: "2026-04-07"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00048", "init-local-00002"]
---

# iss-00052 Reject Non Canonical Git Issue Targets — 実装報告（LOG）

## 実装サマリー (任意)
- `commands/targets.py` の shared parser を fail-closed 化し、canonical GitHub issue URL 以外の URL-like target を `active set` / `deps check` で reject するように修正した。
- `active set` の non-canonical target reject + active state 不変を回帰テストで固定し、`deps check` の shared parser 経由 reject も runtime entry test で追加した。
- 既存の canonical URL / `#<n>` / `<n>` / node id 経路、および `import issue` の strict parser 意味論は維持されることを回帰テストで確認した。

## 実装記録（セッションログ） (必須)

### 2026-04-07 07:43 - 07:50 (UTC)

#### 対象
- Step: S01, S02, S90, S99
- AC/EC: AC-001, AC-002, AC-003, AC-004, EC-001, EC-002, EC-003

#### 実施内容
- S01 (Red): `active set git@github.com:owner/repo/issues/123` が誤受理される現行バグを `test_active.py` の failing test で固定した。
- S02 (Green): `parse_active_like_target()` の broad `/issues/<n>` 部分一致経路を廃止し、canonical full match 以外の URL-like target を reject する fail-closed ガードへ変更した。
- S02 (Regression): `deps check` の legacy runtime entry で non-canonical URL-like target が reject される回帰テストを追加した。
- S90: `workflow_issue.md` / `reference_github.md` / `reference_deps.md` の契約と実装差分の整合を確認し、docs 更新不要と判断した。
- S99: final diff を確認し、実装・QA・spec の各 gate を pass 判定した。

#### 実行コマンド / 結果
```bash
python -m unittest tests.cli_runtime.test_active.TestCliActive.test_active_set_rejects_non_canonical_url_like_target_and_keeps_active_state -v

# S01 Red: FAIL (returncode==0 で bug 再現)
# S02 後: OK

python -m unittest tests.cli_runtime.test_runtime_deps_s04.TestRuntimeDepsS04.test_legacy_deps_path_rejects_non_canonical_url_like_target -v

# OK

python -m unittest tests.cli_runtime.test_active tests.cli_runtime.test_runtime_deps_s04 tests.cli_runtime.test_import -v

# Ran 80 tests in 17.712s / OK

./spec-dock/scripts/spec-dock validate

# spec-dock: ok (validate) nodes=14

rg --files | rg '[A-Z]'

# 既存の uppercase path のみ検出（今回変更で新規 uppercase path の追加なし）
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/targets.py` - shared parser を fail-closed 化し、non-canonical URL-like target を reject
- `tests/cli_runtime/test_active.py` - `active set` non-canonical target reject + active state 不変の回帰テスト追加
- `tests/cli_runtime/test_runtime_deps_s04.py` - `deps check` runtime entry で non-canonical target reject の回帰テスト追加

#### コミット
- 未実施（このセッションでは commit 要求なし）

#### メモ
- 現在の分類: 未完了
- 理由: required step の `./spec-dock/scripts/spec-dock sync --github` 証跡がまだないため、`workflow_issue.md` の complete 条件を満たしていない
- next action: `./spec-dock/scripts/spec-dock sync --github` を実行し、成功または環境 blocker をこの report に追記する
- SG1 spec review: pass
- RG1 implementation review: pass
- QG1 QA review: pass
- review 判定根拠:
  - `parse_active_like_target()` の URL-like reject は parser 層に閉じており、application 層や checkout/deps guard 契約へ副作用なし
  - `import issue` の strict parser (`parse_github_issue_target_ref`) は public contract を維持
  - 指定された回帰テスト群 (`test_active` / `test_runtime_deps_s04` / `test_import`) は全件 green

---

### 2026-04-07 08:00 - 08:01 (UTC)

#### 対象
- Step: S99
- AC/EC: AC-001, AC-002, AC-003, AC-004

#### 実施内容
- required step の `./spec-dock/scripts/spec-dock sync --github` を実行し、success 証跡を追加した。
- 最低限検証として指定の unittest 3 本セットを main session で再実行し、green を再確認した。
- final gate として implementation / QA / spec review の pass 結果を確定し、report の未完了メモを解消した。

#### 実行コマンド / 結果
```bash
./spec-dock/scripts/spec-dock sync --github

# spec-dock: ok (sync) wrote=spec-dock/.agent/index-all.json,spec-dock/.agent/tree-all.json,spec-dock/.agent/index.json,spec-dock/.agent/tree.json,spec-dock/tree-all.puml,spec-dock/tree.puml,spec-dock/.agent/deps-issues.json,spec-dock/deps-issues.puml,spec-dock/dashboard.md
# spec-dock: sync: active unchanged (matched id in branch: iss-00052)

python -m unittest tests.cli_runtime.test_active tests.cli_runtime.test_runtime_deps_s04 tests.cli_runtime.test_import -v

# Ran 80 tests in 28.889s / OK
```

#### 変更したファイル
- `spec-dock/active/issue/report.md` - required `sync --github` 証跡と final gate の確定結果を追記

#### コミット
- 未実施（このセッションでは commit 要求なし）

#### メモ
- 現在の分類: complete 相当
- SG1 spec review: pass
- RG1 implementation review: pass
- QG1 QA review: pass
- residual risk:
  - `owner/repo/issues/123` や `foo/issues/123` の reject は helper 条件で担保されるが、明示テストは未追加
  - `:` や `/` を含む自由文入力は fail-closed で reject されるため、旧来の緩い入力運用があれば挙動差分になりうる

---

## 遭遇した問題と解決 (任意)
- 問題: `test_runtime_deps_s04.py` への新規テスト挿入時に、既存テスト関数の途中へ誤挿入して `NameError` が発生した。
- 解決: 新規テストをクラス末尾へ移動し、既存 finally ブロックの復元を戻して再実行した。

## 学んだこと (任意)
- shared parser の permissive fallback は `active set` と `deps check` 両方に同時に影響するため、parser 層で fail-closed を優先する方が drift を防げる。

## 今後の推奨事項 (任意)
- `parse_active_like_target()` と `parse_github_issue_target_ref()` の reject 条件を将来的にさらに共通化する場合は、error message 契約も含めて fixture 化すると回帰検知しやすい。

## 省略/例外メモ (必須)
- 該当なし
