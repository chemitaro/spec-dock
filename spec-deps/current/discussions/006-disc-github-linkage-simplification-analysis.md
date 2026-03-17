# Discussion: GitHub 連携境界の単純化分析

## 背景

manual regression により、`local-only` と `GitHub-linked` を混在させたときの複雑さが実在することが見えた。

- local/stub manual regression:
  - `duplicate id` race
  - local-only issue の `deps/active` 不整合
  - required artifact 欠損の未検知
- GitHub live manual regression:
  - wrong-repo risk
  - stale projection
  - identifier ambiguity

このため、設計の単純化として次の案を検討する。

- `initiative` と `epic` は GitHub 非連携
- `issue` は GitHub と必ず連携

本資料は、この単純化案の妥当性を評価し、prototype 期間の推奨方針を決めるための分析である。

## 問い

`issue` を常に GitHub-linked に固定すると、設計・運用・dogfooding の全体最適として本当に有利か。

## 事実

### 1. 現行実装でも issue は GitHub create が既定

`create_node.py` の `_resolve_github_mode()` は、`issue` の既定を `create`、`initiative/epic` の既定を `local_only` にしている。

```py
if req.github_mode is None:
    return "create" if kind == "issue" else "local_only"
```

参照:
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`

つまり、現行設計もすでに「issue を GitHub 側に寄せる」方向性は持っている。

### 2. 今回の重大バグの一部は GitHub/local 混在とは別軸

`duplicate epic id` / `duplicate issue id` は、`load_graph() -> _next_id() -> write` がロックなしで並列実行される race condition であり、GitHub 連携の有無ではなく create flow の排他不足が原因である。

参照:
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_repo.py`
- `spec-deps/current/discussions/005-disc-duplicate-epic-id-race-analysis.md`

### 3. GitHub live で見つかった問題は、issue mandatory だけでは解消しない

manual regression で次が確認された。

- `import` は URL の `owner/repo` を見ず、issue number だけを使う
- `active set 13` のような入力は GitHub issue number 解釈が優先される
- GitHub close 後も `deps check` は `--github` なしだと stale のまま

参照:
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/import_cmd.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/targets.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/status.py`
- `manual-tests/reports/2026-03-15-manual-regression-sweep-github-live/summary.md`

### 4. prototype 期間は dogfooding と local-first の逃げ道が必要

現時点の目的は production 運用ではなく prototype の完成である。GitHub 連携そのものに未解決 bug が残っている段階で、全 issue を GitHub 必須にすると、prototype の自由度と調査速度を落とす。

## 案の比較

## 案 A: `initiative/epic` は local-only、`issue` は必ず GitHub-linked

### 利点

- local-only issue status という設計論点をかなり減らせる
- issue completion authority を GitHub に一本化しやすい
- planning scope と execution scope の境界が分かりやすい

### 欠点

- GitHub targeting bug が全 issue に波及する
- GitHub token / permission / repo availability への依存が強くなる
- bootstrap / offline / local-only で issue を切る逃げ道がなくなる
- wrong-repo risk や stale projection は残る
- duplicate id race には効かない

### 評価

`複雑性削減` には効くが、`主要 reliability 問題の解決策` としては過大評価できない。

## 案 B: `initiative/epic` は local-only 固定、`issue` は GitHub-linked を既定にするが `--no-github` を残す

### 利点

- planning scope の単純化を得られる
- 通常運用では GitHub-linked issue を基本にできる
- prototype / dogfooding / bootstrap では local-only issue を明示例外として使える
- GitHub 障害時にも作業継続性を確保できる

### 欠点

- local-only issue lifecycle の実装は残る
- CLI surface と status contract の明示が必要
- user education が少し必要

### 評価

prototype 段階と将来運用の両方にバランスがよい。

## consultant の客観評価

consultant の結論は次だった。

- `initiative/epic` を GitHub 非連携に固定するのは筋が良い
- ただし `issue を必ず GitHub-linked` は勧めない
- 推奨は `issue は GitHub-linked default` とし、`issue --no-github` を例外として残すこと

consultant の理由:

- 単純化効果は中程度で、wrong-repo risk / stale projection / race は残る
- prototype 期間の dogfooding には local-only issue の逃げ道が必要
- 問題の一部を「GitHub に押し出しただけ」になりやすい

## 推奨判断

採用するべきなのは次である。

1. `initiative` は local-only 固定
2. `epic` は local-only 固定
3. `issue` は GitHub-linked を default にする
4. ただし `issue --no-github` は明示例外として残す

## 理由

- planning scope は GitHub 非依存の方が自然
- execution scope は GitHub と結びつけた方が実務上便利
- ただし prototype 段階では GitHub mandatory は硬すぎる
- 現在の主要 bug は `always GitHub` だけでは直らない

## この方針でも別途必要な修正

この単純化だけでは不十分で、少なくとも次が必要である。

1. create 系の repo-level lock
2. repo-aware GitHub targeting
3. `authority / effective / source / stale` の status contract
4. `link/unlink` の明示仕様
5. `doctor` / preflight / validate 強化

## 結論

`initiative/epic local-only` は採用価値が高い。  
一方で `issue always GitHub-linked` は prototype 段階では採用しない方がよい。

最終推奨は次である。

- `initiative/epic`: local-only 固定
- `issue`: GitHub-linked default
- `issue --no-github`: 残す

この形が、複雑性削減、柔軟性、bug 回避、dogfooding 互換性のバランスとして最も現実的である。
