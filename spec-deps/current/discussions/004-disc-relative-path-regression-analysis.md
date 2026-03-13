---
種別: "discussion"
ID: "disc-00004"
タイトル: "active manifest と state artifact の絶対パス化レビュー指摘の分析"
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-03-13"
関連: ["issue-25", "PR #27"]
---

# active manifest と state artifact の絶対パス化レビュー指摘の分析

## 背景
PR #27 に対する Codex review で、次の 2 件の指摘が出ている。

1. `application/set_active.py` の `build_active_manifest()` が `ActiveManifestEntry.path` に絶対パスを保存しており、`.agent/active.json` の portability を壊している。
2. `presentation/json_state.py` の `render_index_artifact()` / `render_tree_artifact()` 系が node `path` を絶対パスで出力しており、state artifact の portability と diff 安定性を壊している。

本シートでは、この 2 件の妥当性と、修正の必要性、修正案の比較、推奨案を整理する。

## 結論
- 2 件とも **妥当**。
- しかも単なる style 指摘ではなく、**既存契約からの回帰** と評価するのが適切。
- 修正は必要。
- 最適案は、**runtime の永続化/artifact に出す path を repo-relative に統一し、境界でだけ絶対パスへ解決する** 方針である。

## 分析

### 1. active manifest の指摘
現行実装:
- [set_active.py](/srv/mount/spec-dock/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py) の `build_active_manifest()` は `node.path.as_posix()` をそのまま `ActiveManifestEntry.path` へ格納している。

受け側:
- [active_store.py](/srv/mount/spec-dock/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/active_store.py) の `_active_entry_path()` は `repo_root / entry.path` で実体パスを組み立てる前提になっている。

この組み合わせだと:
- `entry.path` が `spec-dock/...` のような repo-relative path なら正しく動く。
- しかし `entry.path` が `/tmp/.../spec-dock/...` のような絶対パスだと、`repo_root / entry.path` という不正な join 前提に依存する。
- Python の `Path` では絶対パス右辺が勝つため「今いる repo ではたまたま動く」が、manifest 自体は repo 移動後に stale absolute path を抱える。

既存契約との比較:
- 旧 `app.py` 実装の `_active_entry()` は [app.py](/srv/mount/spec-dock/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py) で `node.path.relative_to(repo_root).as_posix()` を書いていた。
- 既存 test fixture でも [test_runtime_active_s05.py](/srv/mount/spec-dock/tests/cli_runtime/test_runtime_active_s05.py) は `spec-dock/initiatives/...` 形式を使っている。

評価:
- これは「現行でも動く場合がある」ものの、**repo 移動・clone し直し・workspace rename に対する durability regression** であり、レビューは妥当。

### 2. state artifact の指摘
現行実装:
- [json_state.py](/srv/mount/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py) の `_build_state_payloads()` は node item に `node.path.as_posix()` を出している。

既存契約との比較:
- [design.md](/srv/mount/spec-dock/spec-deps/current/design.md) の artifact appendix では `root` が `spec-dock/initiatives` 契約で整理されており、artifact path 群も repo-relative naming で記述されている。
- 旧 `app.py` 実装では state artifact の `path` は [app.py](/srv/mount/spec-dock/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py) で `n.path.relative_to(repo_root).as_posix()` を使っていた。

影響:
- machine-specific absolute path が `index*.json` / `tree*.json` に混入する。
- clone 先や CI 実行環境が変わるだけで diff が不安定になる。
- downstream consumer が `spec-dock/...` 形式を前提にしている場合に壊れる。

評価:
- これも **artifact portability / stable diff regression** とみなすのが妥当。

## 妥当性の評価

### 総合評価
- 妥当性: **高い**
- 深刻度: **P2 相当は妥当**

### 理由
- どちらも repo-local persistence / artifact に absolute path を出してしまっている。
- どちらも旧実装は repo-relative path を採っていた。
- 既存 fixture / docs / artifact appendices とも整合しない。
- 今すぐ crash しないため P1 ではないが、運用 durability と artifact stability を損なうため「直したほうがよい」ではなく **修正すべき**。

## 修正案

### 案A: 最小修正
- `build_active_manifest()` だけ repo-relative 化する。
- `json_state.py` だけ repo-relative 化する。

長所:
- 修正量が小さい。
- 直接の指摘 2 件は消せる。

短所:
- `relative path をどこで作るか` のルールが散る。
- 今後ほかの出力が absolute path を再混入させやすい。

評価:
- 応急処置としては成立するが、再発防止力が弱い。

### 案B: 境界責務を明文化して統一
- 永続化/artifact に出す path は **repo-relative を canonical** とする。
- `application/set_active.py` で active manifest 用 path を repo-relative に変換する。
- `presentation/json_state.py` でも state artifact 用 path を repo-relative に変換する。
- 必要なら小さな helper を追加し、`repo_root` からの相対化を 1 箇所のルールとして使う。
- read path / active symlink 更新のような実 filesystem 操作は infra 側で絶対パスに解決する。

長所:
- persistence / artifact / runtime resolution の責務境界が自然。
- reviewer 指摘の本質に沿っている。
- 再発防止しやすい。

短所:
- `repo_root` を presentation までどう渡すか、または helper をどこに置くかを少し考える必要がある。

評価:
- **最もバランスがよい。推奨。**

### 案C: absolute path を受け入れ、read 側だけ頑健化
- `_active_entry_path()` を absolute/relative 両対応にする。
- state artifact は absolute path のまま仕様として受け入れる。

長所:
- 実行時 breakage は減らせる。

短所:
- portability regression を放置する。
- artifact diff instability が残る。
- 旧契約からの回帰を正当化する追加仕様変更が必要。

評価:
- 今回のレビューへの回答としては弱い。採用非推奨。

### 案D: path field 自体を削除/縮小
- active manifest / state artifact の `path` をなくし、`id` 中心へ寄せる。
- path は consumer が再解決する。

長所:
- portability 問題そのものを減らせる。

短所:
- 既存 schema 契約・consumer・tests への影響が大きい。
- issue #25 の修正としては過剰。

評価:
- 将来の設計見直し候補ではあるが、今回の対処としては不適切。

## 採用案
**案B を採用するのが最適**。

### 採用理由
- 2 件の指摘を同じ原則で一貫して解決できる。
- 旧 `app.py` 実装と整合する。
- docs / tests / artifact contract とも自然に揃う。
- scope を広げすぎず、issue #25 の PR fix として適切なサイズに収まる。

## 修正方針

### active manifest
- `application/set_active.py`
  - `build_active_manifest()` が `repo_root` 基準で repo-relative path を保存するよう変更する。
- `infra/active_store.py`
  - read 側は引き続き repo-relative を正本として扱う。
  - 互換性のため、absolute path を読んだ場合の fallback を入れるかは別判断だが、少なくとも write 正本は repo-relative に戻す。

### state artifact
- `presentation/json_state.py`
  - node item の `path` を repo-relative にする。
- 必要に応じて:
  - `SyncStateResult` に `repo_root` がすでにあるため、それを presentation 側で利用して相対化する。
  - あるいは tiny helper を追加して変換ロジックを集約する。

### test
- active manifest の write/read roundtrip で repo-relative path を明示的に assert する test を追加/更新する。
- `index*.json` / `tree*.json` の `nodes[*].path` が `spec-dock/...` 形式であることを assert する focused regression を追加する。
- 可能なら repo を別パスへ move した後でも active placeholder へ落ちない durability smoke を 1 本追加する。

## 実施判断
- **修正すべき**。
- PR #27 はこの 2 件を取り込んでから update するのが望ましい。

