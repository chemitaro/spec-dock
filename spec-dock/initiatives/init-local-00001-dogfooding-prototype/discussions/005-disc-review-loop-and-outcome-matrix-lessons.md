---
種別: disc
ID: "005-disc"
タイトル: "Review Loop And Outcome Matrix Lessons"
状態: "accepted"
作成者: "Codex CLI"
最終更新: "2026-03-25"
親: ["init-local-00001"]
関連: [
  "004-adr-runtime-cli-layered-architecture.md",
  "002-adr-agentic-cli-roadmap.md"
]
---

# 005-disc Review Loop And Outcome Matrix Lessons

## 目的
- issue-28 の corrective loop で得られた、個別 bugfix ではなく engineering method の学びを残す。
- 将来また review loop が長引いたとき、同じ失敗を繰り返さないための基準を持つ。

## 結論
- review ごとに新しい欠陥が見つかった主因は、review が厳しいことではなく、failure contract が outcome matrix で閉じていないまま枝ごとの patch を積み増したことにあった。
- create/post-create のように失敗枝が多い surface では、例外発生点ベースではなく outcome class ベースで契約と test matrix を固定するべきである。
- provider runtime と checked-in runtime の parity は、実装完了後の付帯確認ではなく contract の一部として扱うべきである。

## 残すべき lesson

### 1. 例外点ではなく outcome class で設計する
- 「どこで失敗したか」だけでは復旧 guidance が決まらない。
- `remote-only failure` と `local-write-committed failure` のように、同じ post-create failure でも safe next action が異なる。
- したがって、失敗設計は exception taxonomy より outcome taxonomy を優先する。

### 2. guidance は error text ではなく evidence から作る
- created issue number
- local write が committed 済みか
- cleanup / release failure の有無
- parent selector 再現に必要な request context

- これらが揃わないと safe rerun / inspect / manual recovery の判断が崩れる。

### 3. test は representative case ではなく matrix を固定する
- 一枝だけ直して安心すると、隣接枝や複合枝が review で再露出しやすい。
- failure-heavy surface は最初から matrix を作り、provider / checked-in parity も同じ exit criteria に入れる。

## 今後の適用先
- create/import の failure guidance
- sync / validate / doctor の combined failure branch
- active recovery や metadata migration の self-heal / fail-closed 境界

## 具体的な運用ルール
- corrective patch を始める前に、まず state space を列挙する。
- review comment を 1 件ずつ潰すだけでなく、同じ surface の未閉塞枝が残っていないかを discussion で言語化する。
- provider / checked-in の片側だけ直す変更を完了扱いにしない。

## 移設メモ
- 本 discussion は `spec-deps/current/discussions/047-disc-pr29-review-loop-root-cause-analysis.md` と `048-disc-pr29-create-outcome-matrix-remediation.md` の durable な知見を統合した。
- 旧 issue-28 固有の corrective scope 名や review 番号は落とし、将来も使える lesson に抽象化している。
