# Epic Close Status Reconciliation Analysis

## 対象の問題
- epic-level spec review finding:
  - `epic-00033/report.md` が `E-AC-005: Partial` と `iss-00038` open を維持したままで、`iss-00038/report.md` の close-out pass と一致していない。

## 現在の状態
- `epic-00033/report.md` は `E-AC-005` を Partial とし、残 open issue を `iss-00038` と記録している。
- generated state (`spec-dock/.agent/index*.json`, `dashboard.md`) も `iss-00038=open` / epic progress=`done=5 open=1` を返している。
- 一方で `iss-00038/report.md` は final spec review record を `pass` とし、issue docs の front matter も `approved` になっている。

## あるべき状態
- epic close を主張する authority が 1 つの結論に揃っていること。
- 少なくとも次の 4 つが矛盾しないこと:
  - `iss-00038/report.md`
  - `epic-00033/report.md`
  - generated state (`index*.json`, `dashboard.md`)
  - GitHub / sync 後の issue status

## ギャップ
- issue artifact approval と issue lifecycle closure が docs 上で明確に区別されていない。
- close-status authority を `index-all.json` と epic report に委譲しているのに、issue report だけが先行して完了ニュアンスを持っている。
- epic report をいつ `Partial -> Pass` に進めてよいかの contract が issue plan に定義されていない。

## 修正案
- Option A:
  - epic report だけを先に `Pass` / close 相当に更新する。
  - 長所:
    - 最短で epic completion 文言を揃えられる。
  - 短所:
    - generated state / GitHub が open のままだと authority drift を増やす。
- Option B:
  - issue docs 側を「approved だが lifecycle は open」の表現に下げ、epic report は現状維持にする。
  - 長所:
    - 現在の generated state と矛盾しない。
  - 短所:
    - issue close-out pass の意味が読み手依存になりやすい。
- Option C:
  - issue-level corrective scope に status reconciliation を追加し、GitHub close、sync/generated state 更新、epic report 更新まで終わったときだけ epic completion を主張する。
  - 長所:
    - authority が一貫する。
    - branch-diff review と close-out audit trail を両立できる。
  - 短所:
    - corrective scope が少し広がる。

## consultant の客観分析
- consultant 観点では、「approved」と「closed」を同義に扱わないことが重要。
- `iss-00038` の report が pass でも、authority 側が open のままなら epic report を先に close しない方が監査性が高い。
- 最善順序は、依存/履歴整合を先に直し、その後で status reconciliation を行う流れ。

## 推奨案
- Best practice:
  - Option C
- 理由:
  - epic close は単一ファイルの宣言ではなく、authority reconciliation の結果として扱うべきだから。
  - `approved != closed` を issue requirement/design で明示し、plan に status reconciliation step を追加すると再発防止になる。
  - GitHub / generated state が open の間は epic report を無理に `Pass` にしない方が truthful。

## 実装計画への反映ポイント
- `iss-00038` issue docs に branch-diff corrective scope を追加する。
- plan に epic status reconciliation step を追加する。
- final exit contract に「epic report / generated state / issue report が同じ結論へ収束していること」を加える。

## 備考
- repo_analyst 観測では、`epic-00033/report.md` だけでなく generated state も `iss-00038=open` を返しているため、現時点で epic close を主張するのは premature。
