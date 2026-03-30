# Epic Report #33 Open Closed Authority Mismatch Analysis

## 対象の問題
- latest fresh review finding:
  - `epic-00033/report.md` に GitHub issue `#33` の OPEN/CLOSED authority が混在しており、final rereview がどの記述を正本として読むべきか曖昧である。

## 現在の状態
- `epic-00033/report.md` の本文は child issue 完了、`E-AC-005: Pass`、open child issue なしという close-ready な記述になっている。
- 一方で同 report の `省略/例外メモ` には epic GitHub issue `#33` 自体は `OPEN` のままだと書かれている。
- `iss-00038/report.md` の S09 execution evidence は `#33=CLOSED` を前提に記録されている。

## あるべき状態
- epic report の中で GitHub issue `#33` state が単一の authority conclusion に揃っていること。
- `approved`、child completion、epic GitHub lifecycle close の違いが読み分け可能であること。
- final rereview では、epic report / generated state / `iss-00038/report.md` が同じ結論を返すこと。

## ギャップ
- 同一 report 内で close-ready narrative と `#33 OPEN` note が共存し、latest authority を誤読しやすい。
- issue-level S09 evidence と epic report の exception note が衝突しているため、authority order を知っていても rereview の入力が不安定になる。
- `approved` と `closed` の区別はあるが、`#33` の最終 state をどこで確定するかが report wording に固定されていない。

## 修正案
- Option A:
  - `iss-00038/report.md` 側でだけ epic `#33` state の説明を補い、epic report は触らない。
  - 長所:
    - issue close-out の差分だけで済む。
  - 短所:
    - epic report 自体の ambiguity が残り、authority mismatch を解消できない。
- Option B:
  - `epic-00033/report.md` を最小差分で正規化し、`#33` state と `approved` の関係を final authority に合わせて明記する。
  - 長所:
    - rereview input が単純になる。
    - epic report 自身を読んだ maintainer が誤読しにくい。
  - 短所:
    - upstream report artifact に触れる必要がある。
- Option C:
  - exception note を残したまま、「authority order を知っていれば読める」として運用で吸収する。
  - 長所:
    - 最少工数。
  - 短所:
    - final review のたびに補足説明が必要になり、再発防止にならない。

## consultant の客観分析
- consultant 観点では、同一 artifact 内で lifecycle state が競合する記述を残すのは避けるべきである。
- 特に epic summary は close judgement の入口になるため、`#33` OPEN/CLOSED の両義性は upstream report 側で解消してから issue rereview に渡す方が安全である。

## 推奨案
- Best practice:
  - Option B
- 理由:
  - authority mismatch を report 正本で閉じる方が、issue 側の補足説明より durable である。
  - consultant-backed rationale としても、summary artifact は single-source interpretation を返すべきであり、latest rereview 前に upstream report normalization を済ませるのが妥当である。

## 実装計画への反映ポイント
- plan に epic report authority normalization step を追加する。
- requirement/design に `#33` state は本文・例外メモ・generated state・issue report で単一結論へ揃えることを明記する。
- final rereview は upstream authority normalization 完了後にだけ実行する。

## 備考
- この corrective は epic implementation の再実行ではなく、final review input としての report-artifact normalization を扱う。
