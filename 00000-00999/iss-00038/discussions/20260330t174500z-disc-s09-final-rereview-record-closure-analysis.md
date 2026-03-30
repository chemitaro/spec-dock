# S09 Final Rereview Record Closure Analysis

## 対象の問題
- latest fresh review finding:
  - S09 は status reconciliation の execution evidence まで記録されているが、fresh final rereview の reviewer / verdict / committed closure record が存在しない。

## 現在の状態
- `iss-00038/report.md` の S09 entry は `reviewer: 未実施`、`verdict: pending`、`コミット: なし` のまま止まっている。
- 同 entry では `remaining gate: fresh final re-review` と明記されている。
- 一方で requirement/design/plan は S09 を最終 corrective path の終点に近い形で読めてしまい、fresh rereview record 欠落が contract 上で十分に強調されていない。

## あるべき状態
- S09 は execution evidence step、final closure は fresh final rereview step として分離されていること。
- final close judgement は、reviewer / verdict / referenced evidence / actual commit hash を含む committed record から追えること。
- latest rereview が未記録なら、issue close-out は未完了だと一読で判定できること。

## ギャップ
- execution evidence と rereview closure が同じ corrective stream に載っているため、S09 実施済みをもって close 済みと誤読しやすい。
- S09 の残 gate は report には書かれているが、issue requirement/design/plan の execution contract では後段 step として固定されていない。
- branch-diff review では committed rereview record が必要なのに、その受け皿が plan にない。

## 修正案
- Option A:
  - S09 の既存 entry をそのまま final rereview pass に上書きする。
  - 長所:
    - 変更箇所が少ない。
  - 短所:
    - execution evidence と reviewer verdict の時系列が混ざり、監査性が落ちる。
- Option B:
  - S09 は execution evidence step のまま保持し、後続に fresh final rereview closure step を追加する。
  - 長所:
    - 既存 chronology を壊さず、latest blocker だけを後段 corrective scope として扱える。
    - committed rereview record の要件を contract に固定できる。
  - 短所:
    - step 数は 1 つ増える。
- Option C:
  - rereview 結果は discussion だけに残し、issue plan には追加しない。
  - 長所:
    - issue docs の差分が小さい。
  - 短所:
    - issue close-out の正本が分散し、report 参照だけで完了判定できなくなる。

## consultant の客観分析
- consultant 観点では、execution evidence と approval evidence は別 artifact として扱う方が review audit に強い。
- 特に committed branch-diff review を quality gate にしている以上、latest rereview closure は report 正本に独立 entry として残すのが妥当である。

## 推奨案
- Best practice:
  - Option B
- 理由:
  - 既存 S09 を rewrite せず、未了 blocker だけを S10/S11 相当の後段 path へ押し出せる。
  - consultant-backed rationale としても、execution evidence と final reviewer verdict を分離した方が再読性と監査性が高い。

## 実装計画への反映ポイント
- plan に「fresh final rereview closure」の独立 step を追加する。
- requirement/design に「S09 execution evidence 単独では close 完了扱いにしない」を明記する。
- final exit contract に、latest rereview record が committed history から追えることを追加する。

## 備考
- この論点は新しい実装作業を増やすためではなく、既に存在する S09 execution evidence を final closure まで正しく接続するための contract 補強である。
