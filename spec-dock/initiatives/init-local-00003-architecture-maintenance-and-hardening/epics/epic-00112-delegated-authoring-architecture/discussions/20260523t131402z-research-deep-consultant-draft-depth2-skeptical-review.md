---
type: research
source: deep-consultant
created_at: 2026-05-23T13:14:02+09:00
epic: epic-00112
topic: skeptical review of draft canonical authoring and depth-2 delegation
status: current
---

# Deep Consultant 懐疑レビュー: draft canonical authoring と depth=2 のリスク

## 問い

`status: draft` の canonical artifact と bounded depth=2 specialist delegation は、本当に安全に採用できるか。採用するとして、何が壊れやすいか。

## 懐疑側の結論

素のままでは No-Go。

`status: draft` だけでは弱い。`design.md` / `plan.md` という canonical path は、それ自体が強い authority signal である。人間、agent、context-pack、lifecycle command、reviewer のどれかが draft を見落とすと、未承認案が実装や完了判断の根拠になり得る。

depth=2 も、単に便利な fan-out として許可すると、責任の拡散、証拠の選択バイアス、レビュー対象の肥大化、ユーザー認知負荷の増大を招く。

## 主な failure mode

- canonical path にある draft が、承認済み source of truth と誤認される。
- `status: draft` の有無だけで downstream gate が動き、実際の authority と一致しない。
- 子 specialist の出力が多すぎて、親 authoring agent が都合の良い証拠だけ採用する。
- preflight reviewer と final reviewer の責任が混ざる。
- main orchestrator が draft の全体責任を追えなくなる。
- discussion report が増えるだけで、何が採用され何が棄却されたかが不明になる。

## 採用する場合の最低条件

- `status` と別に `authority` を導入する。
- downstream の実装開始、issue finish、phase completion は `authority: approved` のみ許可する。
- `status: draft` / `authority: proposed` は review input にはできるが implementation baseline にはできない。
- child specialist の出力は ledger に入り、採用・部分採用・棄却・保留を明示する。
- depth=2 は manifest で許可された specialist と cap の範囲だけに限定する。
- final promotion は main orchestrator だけが行う。
- preflight spec-reviewer は advisory、final spec-reviewer は blocking として分離する。

## 代替案

権威管理が未実装の間は、canonical draft editing をすぐに有効化しない。まず discussions/proposals に evidence と draft proposal を残し、authority-aware gate を実装してから `design.md` / `plan.md` への draft authoring を解禁する。

## 判断

この懐疑レビューは、draft canonical model を否定するものではない。むしろ採用条件を明確にするもの。結論は「status だけなら危険、authority-aware workflow まで含めるなら採用可能」。
