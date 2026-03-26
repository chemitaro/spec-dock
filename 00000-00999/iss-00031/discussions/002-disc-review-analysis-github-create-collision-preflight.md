# 002-disc-review-analysis-github-create-collision-preflight

## 対象指摘
- 指摘:
  - GitHub issue 作成前の collision preflight について、create-mode の実 collision を固定する test が不足している。
- 参照:
  - `tests/cli_runtime/test_runtime_new_s08.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`

## 結論
- 妥当性:
  - 妥当
- 修正必要性:
  - 高い
- 推奨:
  - create-mode の collision regression test を追加し、`pre_github_fail` / gateway call 0 件 / local write なし、を 1 本の focused test 群で固定する。

## 妥当性の分析
- この指摘は、実装の「fail fast before remote side effect」という設計意図を直接見ている。
- 現在の coverage は `Missing rules source` と symlink capability failure を押さえているが、destination collision は別系統の失敗モードである。
- GitHub 連携付き create は local failure より先に remote side effect が起きると後始末コストが高い。
- そのため、collision が pre-GitHub で止まることは仕様上も運用上も重要で、単なる追加テスト要望ではなく contract の欠落補完に近い。

## いま修正すべきか
- 修正した方がよい。
- 理由:
  - この issue は GitHub create 前の preflight を明示的に導入して close しようとしており、その主要価値の一つが remote side effect の予防だから。
  - ここを未固定のままにすると、「実装はあるが最も痛い failure mode が test で守られていない」状態が残る。
  - dogfooding 専用でシンプルさ優先という制約とも矛盾しない。必要なのは汎用化ではなく focused な regression test だけである。

## 修正案

### 案A
- `tests/cli_runtime/test_runtime_new_s08.py` に create-mode collision case を追加する。
- 内容:
  - `initiative` / `epic` / `issue` の create request を使う。
  - `epics/` もしくは `issues/` 配下に file または symlink の collision を事前配置する。
  - `Outcome: pre_github_fail`
  - GitHub gateway call 0 件
  - local write なし
  - を assert する。
- 利点:
  - 既存の pre-GitHub fail-fast test 群と同じ責務の中で読める。
  - 実装変更なしでも contract を強く固定できる。
  - 最小変更で今回の指摘に正面から答えられる。
- 欠点:
  - ケースを増やしすぎると test ファイルが長くなる。

### 案B
- `tests/cli_runtime/test_new.py` に black-box 的な CLI integration test として追加する。
- 利点:
  - ユーザー視点の観測に近い。
- 欠点:
  - 失敗原因の切り分けが荒くなる。
  - pre-GitHub boundary の保証としては、今の S08 系 test より責務がぼやける。

### 案C
- collision preflight を helper 単位の unit test に切り出して追加する。
- 利点:
  - failure mode を細かく分けて検証できる。
- 欠点:
  - 現状の test 構成に対して粒度が細かすぎる。
  - 「remote side effect が起きない」という end-to-end contract までは直接保証しづらい。

## 採用方針
- 案A を採用するのが最も良い。
- 理由:
  - issue の設計意図に最も近い。
  - 実装を複雑化せず、回帰価値が高い。
  - dogfooding repo の「過度に汎用化しない」方針にも合う。

## 推奨する具体修正
- create-mode の collision fixture を 2 パターン程度に絞る。
  - child container path が file
  - child container path が symlink
- assertion は次に限定する。
  - exception message に `Outcome: pre_github_fail`
  - `issue_gateway.calls == []`
  - created path / event が空
- `initiative` と `epic` または `issue` の 2 scope を押さえれば十分で、全 scope 完全総当たりまでは不要。

## 見送る場合の判断
- 見送りは非推奨。
- どうしても分割するなら、後続 issue に「GitHub create preflight regression hardening」として明示的に積むべきで、黙って close するのは避ける。
