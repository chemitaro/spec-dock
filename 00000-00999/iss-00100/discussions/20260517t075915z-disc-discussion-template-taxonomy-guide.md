---
種別: disc
ID: "20260517t075915z-disc"
タイトル: "discussion template taxonomy guide"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-05-17"
親: ["iss-00100"]
関連: ["#100", "20260517t103746z-disc"]
---

# 20260517t075915z-disc discussion template taxonomy guide

## 議題
- `spec-dock` の `discussions/` 用テンプレート群を、情報ライフサイクル上の役割で整理する。
- 文書そのものを別種別へ昇格させるのではなく、蓄積した文脈をもとに新しい正本 artifact を作成・修正する方針を明確化する。
- 要件定義書へ細部を押し込まず、エージェントが情報を外部化し、固定化する流れを理解するための説明資料として残す。

## 要約
- 本質的な不足は、`elicitation` と `raw capture` である。
  - `elicitation`: 人間から未確定情報、判断基準、制約、回答を引き出す。
  - `raw capture`: まだ分類できない発話、観察、会話ログ、思考を低摩擦に置く。
- 初期 catalog の暫定案は `scratch` / `interview` / `research` / `disc` / `adr` の5種類である。
- `note` は新規 type としては廃止し、`scratch` に統合する。既存 `note` は grandfathered として壊さない。
- `interview` の日本語表示名は「ヒアリング記録」とする。
- `disc` や `research` を `adr` に昇格させるのではなく、それらの文脈を踏まえて新しい `adr` を作成する。
- 作成した `adr` の内容は、必要に応じて `requirement.md` / `design.md` / `plan.md` へ織り込む。

## 情報ライフサイクル

```plantuml
@startuml
title discussion docs information lifecycle

skinparam backgroundColor #ffffff
skinparam shadowing false
skinparam roundcorner 8
skinparam defaultFontName "Hiragino Sans"

state "capture\n未整理の発話・観察・思考を失わず置く" as capture
state "elicitation\n人間から未確定情報や判断を引き出す" as elicitation
state "research\n事実・仕様・実装・先例を確認する" as research
state "framing\n論点・選択肢・評価軸を整理する" as framing
state "decision\n長期判断と理由を記録する" as decision
state "execution handoff\nrequirement/design/planへ織り込む" as handoff

[*] --> capture
capture --> elicitation : 人間の回答が必要
capture --> research : 事実確認が必要
capture --> framing : 論点が見えた
elicitation --> research : 回答が追加調査を要求
research --> framing : 比較・合意形成が必要
elicitation --> framing : 回答が論点を生む
framing --> decision : 新しいADRを作成
decision --> handoff : 決定内容を仕様へ反映
framing --> handoff : ADR不要の合意を仕様へ反映
handoff --> [*]

@enduml
```

## 推奨 catalog

| template | 日本語名 | lifecycle | 主な役割 | 正本性 |
|---|---|---|---|---|
| `scratch` | 作業メモ | capture | 未整理メモ、思考途中、下書き、会話ログを一時保存する | 低い |
| `interview` | ヒアリング記録 | elicitation | 人間が判断しやすいように、事前分析、選択肢、推奨案、回答欄をまとめる | 中 |
| `research` | 調査記録 | research | 事実、根拠、未検証事項、判断への示唆を分離する | 中 |
| `disc` | 議論記録 | framing | 論点、選択肢、評価軸、合意/未合意を整理する | 中 |
| `adr` | 意思決定記録 | decision | 採用した判断、理由、影響、見直し条件を固定化する | 高い |

```plantuml
@startuml
title current recommended discussion template map

skinparam backgroundColor #ffffff
skinparam shadowing false
skinparam roundcorner 8
skinparam defaultFontName "Hiragino Sans"
skinparam packageStyle rectangle

package "capture" {
  rectangle "scratch\n作業メモ\n未整理・非正本" as scratch #f4f4f4
}

package "elicitation" {
  rectangle "interview\nヒアリング記録\n選択肢・分析・推奨・回答欄" as interview #e8f7ee
}

package "research" {
  rectangle "research\n調査記録\n事実・根拠・未検証" as research #e8f7ee
}

package "framing" {
  rectangle "disc\n議論記録\n論点・比較・合意形成" as disc #eef6ff
}

package "decision" {
  rectangle "adr\n意思決定記録\n決定・理由・影響" as adr #fff4df
}

rectangle "requirement/design/plan\n実行用正本" as spec #fff4df

scratch --> interview : 人間に聞く
scratch --> research : 調査する
scratch --> disc : 論点化する
interview --> disc : 回答が比較を生む
research --> disc : 根拠から比較へ
disc --> adr : 文脈をもとに新規ADR作成
interview --> adr : 判断基準をもとに新規ADR作成
research --> adr : 根拠をもとに新規ADR作成
adr --> spec : 決定を仕様へ織り込む
disc --> spec : ADR不要の合意を仕様へ反映

@enduml
```

## 選択フロー

```plantuml
@startuml
title discussion template selection flow

skinparam backgroundColor #ffffff
skinparam shadowing false
skinparam roundcorner 8
skinparam defaultFontName "Hiragino Sans"

start

if ("長期的・横断的・戻しにくい\n決定を固定化する?") then (yes)
  :adr;
  stop
endif

if ("人間から回答・判断・制約・優先順位を\n引き出す?") then (yes)
  :interview\nヒアリング記録;
  stop
endif

if ("docs/code/tests/外部仕様など\n検証可能な根拠を集める?") then (yes)
  :research;
  stop
endif

if ("論点・選択肢・評価軸・推奨案を\n整理して合意形成する?") then (yes)
  :disc;
  stop
endif

if ("まだ分類できない発話・思考・ログを\nまず失わず置く?") then (yes)
  :scratch;
  stop
endif

:scratch;
stop

@enduml
```

## `disc` と `interview` の境界

| 観点 | `interview`（ヒアリング記録） | `disc` |
|---|---|---|
| 主目的 | 人間から未確定情報や判断を引き出す | 集まった情報を整理し、合意形成する |
| 読者 | 回答者、意思決定者、依頼者 | reviewer、maintainer、設計参加者 |
| 中心要素 | 質問、事前分析、回答候補、選択肢比較、推奨案、回答欄 | 論点、選択肢、評価軸、比較、推奨案、合意点 |
| 完了条件 | 回答が得られ、正本への反映方針が決まる | 合意または次の判断材料が揃う |
| 反映先 | `requirement` / `design` / `plan` / 新規 `adr` | `requirement` / `design` / `plan` / 新規 `adr` |

## `scratch` と旧 `note` の境界

| 観点 | `scratch` | 旧 `note` |
|---|---|---|
| 主目的 | 未整理情報を失わず置く | 軽量だが整理済みの記録を残す |
| 今回の扱い | 新規作成 type として採用候補 | grandfathered。新規作成は `scratch` へ寄せる |
| 構造 | 最小限。自由記述を妨げない | 背景、事実、検討、次アクション程度の整理あり |
| 正本性 | 低い。正本ではない | 低から中 |
| 必須 guidance | 整理先候補、破棄条件、次にすること | 既存 artifact として保持 |

## 反映フロー

```plantuml
@startuml
title reflection rules, not document promotion

skinparam backgroundColor #ffffff
skinparam shadowing false
skinparam roundcorner 8
skinparam defaultFontName "Hiragino Sans"

rectangle "scratch\n未整理ログ・思考" as raw #f4f4f4
rectangle "interview\n質問・分析・回答" as interview #e8f7ee
rectangle "research\n事実・根拠・未検証" as res #e8f7ee
rectangle "disc\n論点・比較・合意" as disc #eef6ff
rectangle "adr\n新規作成される決定記録" as adr #fff4df
rectangle "requirement/design/plan\n修正または作成される正本" as spec #fff4df

raw --> interview : 人間の回答が必要
raw --> res : 事実確認が必要
raw --> disc : 論点や選択肢が見えた
interview --> disc : 回答が比較・合意形成を要求
res --> disc : 調査から選択肢比較へ
disc --> adr : 文脈をもとに新規ADR作成
interview --> adr : 判断基準をもとに新規ADR作成
res --> adr : 根拠をもとに新規ADR作成
adr --> spec : 決定内容を織り込む
disc --> spec : ADR不要の合意を反映

@enduml
```

## 設計方針
- `interview` は単なる聞き取りログではなく、人間が回答しやすい意思決定支援シートとして扱う。
  - 回答案
  - 選択肢比較
  - メリット / デメリット
  - リスク
  - ベストプラクティス分析
  - 推奨案
  - 回答欄
- `scratch` は旧 `note` と `freeform` の受け皿を統合する。
- `promotion` type は初期実装では作らない。
- discussion docs は作業面であり、正本化は新規 `adr` の作成、または `requirement.md` / `design.md` / `plan.md` への織り込みで行う。

## 次アクション
- 設計フェーズで `interview` / `scratch` の exact template を確定する。
- authority level は doc type 既定値 + 例外 override 方式で設計する。
- 反映履歴は `derived_from` / `reflected_to` または本文の「反映メモ」で軽量に扱う。
