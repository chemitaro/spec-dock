# Upstream Evidence Normalization For Iss 00040 Report Analysis

## 対象の問題
- latest fresh review finding:
  - final close-out が参照する `iss-00040/report.md` に provisional marker が残っており、upstream evidence をそのまま latest rereview input に使うと完了状態を誤読しやすい。

## 現在の状態
- `iss-00040/report.md` の front matter は `状態: "draft | approved"` になっている。
- session log には時点依存の `コミット: なし` 記録が残っており、本文でも「close/handoff 向けメモが後続で最新 commit 状態をまとめる」と補足している。
- `iss-00038` 側は `iss-00040` を final evidence prerequisite として参照しているため、この ambiguity が downstream review input にそのまま波及する。

## あるべき状態
- `iss-00038` final rereview が `iss-00040/report.md` を参照するとき、artifact quality と final evidence anchor が一意に読めること。
- upstream report normalization は report artifact の整列だけに限定され、`iss-00040` の implementation / test / regression ownership を reopen しないこと。

## ギャップ
- `draft | approved` のような複数状態表記は、session log 型 report では経緯としては理解できても、upstream close evidence としては曖昧である。
- downstream reviewer が `コミット: なし` を最新状態と誤認すると、完了済み evidence を取りこぼす。
- 現行 issue docs には「`iss-00040/report.md` を触るとしても report-artifact normalization に限る」という narrow boundary が十分に強調されていない。

## 修正案
- Option A:
  - `iss-00040` を再実行し、report 全体を作り直す。
  - 長所:
    - ambiguity を根本的に消せるように見える。
  - 短所:
    - 完了済み issue の implementation ownership を不必要に reopen する。
- Option B:
  - `iss-00040/report.md` は upstream report-artifact normalization だけを行い、final evidence anchor を明確にする。
  - 長所:
    - narrow corrective scope を守れる。
    - downstream rereview の参照品質だけを改善できる。
  - 短所:
    - session log 由来の provisional wording をどこまで残すか判断が必要。
- Option C:
  - `iss-00040/report.md` 参照をやめ、`iss-00038` からの narrative summary だけで代替する。
  - 長所:
    - upstream report を編集しなくて済む。
  - 短所:
    - close evidence の正本参照が弱くなり、traceability が落ちる。

## consultant の客観分析
- consultant 観点では、completed issue の upstream report を参照品質のために正規化すること自体は妥当だが、scope は artifact normalization に厳密に限定すべきである。
- implementation re-execution を伴わないことを requirement/design/plan に明記しておけば、ownership conflict の再発を防ぎつつ evidence traceability を改善できる。

## 推奨案
- Best practice:
  - Option B
- 理由:
  - latest blocker は implementation 不足ではなく、report artifact の読解 ambiguity だから。
  - consultant-backed rationale としても、正本 report の citation layer を整える方が、完了済み issue を再実行するより監査コストが低い。

## 実装計画への反映ポイント
- requirement/design に「`iss-00040/report.md` を触る場合は report-artifact normalization only」を明記する。
- plan に upstream evidence normalization step を追加し、`iss-00040/report.md` の touch が implementation/test rerun ではないことを review gate に入れる。
- final rereview step は normalized upstream evidence を引用して closure verdict を残す。

## 備考
- この論点は `iss-00040` の完了を否定するものではなく、`iss-00038` の final review input を unambiguous にするための narrow corrective である。
