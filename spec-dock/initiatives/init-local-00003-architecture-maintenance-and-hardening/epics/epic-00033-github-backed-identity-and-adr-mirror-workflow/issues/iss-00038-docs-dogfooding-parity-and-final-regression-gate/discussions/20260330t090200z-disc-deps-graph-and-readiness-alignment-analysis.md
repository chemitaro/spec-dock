# Deps Graph And Readiness Alignment Analysis

## 対象の問題
- epic-level spec review finding:
  - `iss-00038/deps.json` に `iss-00040` が入っておらず、narrative spec と machine-readable DAG が不一致。

## 現在の状態
- `iss-00038/deps.json` の `depends_on` は `iss-00034/35/36/37` のみ。
- しかし `iss-00038` requirement/design/plan と epic plan は、`iss-00040` の完了 evidence を前提に docs/spec-review slice を閉じる契約になっている。
- generated deps graph にも `iss-00038 -> iss-00040` edge が出ていない。

## あるべき状態
- hard prerequisite が narrative spec と machine-readable deps graph の両方に同じ意味で表現されていること。
- `deps.ready=true` が human docs の前提と矛盾しないこと。

## ギャップ
- `iss-00040` が blocker 的 prerequisite なのか、参考 evidence なのかが narrative では強く、deps graph では弱い。
- readiness 判定が `iss-00040` 未考慮でも true になりうる。

## 修正案
- Option A:
  - `iss-00040` を `iss-00038/deps.json` に追加し、sync/generated artifacts も更新する。
  - 長所:
    - 現行 spec と最も素直に一致する。
    - readiness semantics が明確になる。
  - 短所:
    - DAG が変わるため generated state 更新が必要。
- Option B:
  - issue docs から `iss-00040` を blocker prerequisite として扱う記述を外し、reference/evidence 参照に格下げする。
  - 長所:
    - JSON を変えずに済む。
  - 短所:
    - 既存 acceptance contract を弱める方向で、設計意図がぶれやすい。
- Option C:
  - `depends_on` とは別に `evidence_ref` などの新しい依存種別を設計する。
  - 長所:
    - ownership 再取得を避けつつ意味を分離できる。
  - 短所:
    - 今回の corrective としては過大。

## consultant の客観分析
- consultant 観点では、現在の spec は `iss-00040` evidence を pass 条件に使っているため、今の schema では `depends_on` に載せるのが最も truthful。
- ただし docs 側で「依存は evidence availability であり ownership 再取得ではない」と明記しておくと、scope conflict 再発を防ぎやすい。

## 推奨案
- Best practice:
  - Option A
- 理由:
  - 現行 requirement/design/plan の意味を保ったまま、generated readiness を正しくできる。
  - 今回の corrective work の範囲で実現可能で、追加 schema 設計を持ち込まない。

## 実装計画への反映ポイント
- plan に dependency graph alignment step を追加する。
- report では `iss-00040` 依存を edge として追加したこと、ownership 再取得ではないこと、sync 後の generated deps が一致したことを記録する。
- final diff review では `deps.json` と `.agent/deps-issues.json` の両方を観測対象にする。

## 備考
- repo_analyst 観測では、epic plan はすでに `iss-00040` dependency を明記しているため、`deps.json` 側が遅れている形。
