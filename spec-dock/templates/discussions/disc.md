---
種別: disc
ID: "<DISC_ID>"
タイトル: "<DISC_TITLE>"
状態: "draft | proposed | archived"
作成者: "<YOUR_NAME>"
最終更新: "YYYY-MM-DD"
親: ["<SCOPE_ID>"]
関連: []
scope: "<issue | epic | initiative | local>"
scope_id: "<SCOPE_ID>"
created_at: "YYYY-MM-DDTHH:MM:SSZ"
created_by: "<orchestrator | role>"
status: "draft | proposed | superseded | archived"
authority: "proposed"
adoption_status: "unreviewed | adopted | partially_adopted | rejected | deferred | stale | blocked"
derived_from: []
reflected_to: []
---

# <DISC_ID> <DISC_TITLE>

## 位置づけ
- 用途: 集まった質問シート、research、draft を synthesis し、reflection proposal、ADR candidate triage、推奨反映先を整理する。
- authority default: `proposed`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- この文書は採否確定 ledger ではない。採否の最終証跡は canonical docs、ADR、または `report.md` の Evidence Adoption Ledger に昇格して記録する。
- 人間から回答を引き出し、回答欄や未回答事項を管理する場合は `interview` を使う。
- 生ログや未整理の思考は `scratch`、事実確認や外部根拠は `research`、長期判断の固定は `adr` に分ける。
- doc が大きくなりすぎたら、質問回答は `interview`、事実調査は `research`、raw capture は `scratch`、長期決定は `adr` へ分割する。

## 対象論点 (必須)
- 今回 synthesis する論点:
  - ...

## Derived question sheets / research (必須)
- `interview`:
  - ...
- `research`:
  - ...
- その他 source:
  - ...

## Synthesis (必須)
- 分かったこと:
  - ...
- 未確定のまま残ること:
  - ...

## 選択肢 / tradeoff (必須)
- Option A:
  - 内容:
    - ...
  - Pros:
    - ...
  - Cons:
    - ...
- Option B:
  - 内容:
    - ...
  - Pros:
    - ...
  - Cons:
    - ...

## Reflection proposal (必須)
- canonical docs / report / follow-up に反映する提案:
  - ...
- まだ提案に留まる理由:
  - ...

## ADR candidate triage (必須)
- hard to reverse:
  - yes | no | unclear
- surprising without context:
  - yes | no | unclear
- real tradeoff:
  - yes | no | unclear
- ADR 化判断:
  - create ADR | keep in disc | reflect to canonical docs | defer
- 理由:
  - ...

## 推奨反映先 (必須)
- `requirement.md`:
  - ...
- `design.md`:
  - ...
- `plan.md`:
  - ...
- `adr`:
  - ...
- `report.md` Evidence Adoption Ledger:
  - ...

## 未採用 / deferred 理由 (必須)
- 採用しない選択肢:
  - ...
- deferred の理由と revisit 条件:
  - ...

## 未決事項 (任意)
- ...

## 次アクション (必須)
- 追加で作る discussion docs:
  - ...
- orchestrator が判断する採否:
  - ...
