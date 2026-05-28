---
種別: research
ID: "<RESEARCH_ID>"
タイトル: "<RESEARCH_TITLE>"
状態: "draft | completed | archived"
作成者: "<YOUR_NAME>"
最終更新: "YYYY-MM-DD"
親: ["<SCOPE_ID>"]
関連: []
scope: "<issue | epic | initiative | local>"
scope_id: "<SCOPE_ID>"
created_at: "YYYY-MM-DDTHH:MM:SSZ"
created_by: "<orchestrator | role>"
status: "draft | completed | superseded | archived"
authority: "synthesized"
adoption_status: "unreviewed | adopted | partially_adopted | rejected | deferred | stale | blocked"
derived_from: []
reflected_to: []
---

# <RESEARCH_ID> <RESEARCH_TITLE>

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- sources、facts、inference、unverified、terms、edge cases、implications を混ぜない。

## 調査目的 (必須)
- 何を明らかにする調査かを記載する。

## Sources / 調査方法 (必須)
- 参照先:
  - ...
- 検証手順 / 実験条件:
  - ...

## Facts / 観測事実 (必須)
- 観測できた事実:
  - ...

## Inference / 推論 (必須)
- 事実から推論したこと:
  - ...

## Unverified / 未検証事項 (必須)
- 未確認のまま残ること:
  - ...

## Terms / 用語・境界の衝突 (必須)
- 用語:
  - ...
- 衝突 / 揺れ:
  - ...

## Edge cases / 例外・境界ケース (必須)
- ...

## Implications / 判断への含意 (必須)
- requirement / design / plan / adr へ影響する示唆:
  - ...

## リスク/制約 (任意)
- ...

## 反映先 (任意)
- reflected_to:
  - ...

## 参考（References） (任意)
- ...
