---
種別: disc
ID: "20260517t103746z-disc"
タイトル: "discussion template catalog design proposal"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-05-17"
親: ["iss-00100"]
関連: ["#100", "20260517t075915z-disc", "20260517t104954z-disc", "20260517t104958z-disc"]
---

# 20260517t103746z-disc discussion template catalog design proposal

## 議題
- `spec-dock` の discussion template catalog を、ゼロベースの最終採用案として整理する。
- 項目名は日本語にし、各 template を「必須項目」と「任意項目」に分ける。
- ADR 必須を前提に、エージェントが思考、知識、未確定情報を外部化し、必要な情報だけを正本へ固定化する workflow を template に埋め込む。

## コンサルタント統合結論
- 初期採用候補は、`adr` / `disc` / `research` / `interview` / `scratch` の5種類とする。
- `hearing` は日本語の業務会話では自然だが、英語 type key としては「公聴会」「聴聞」の意味が強い。内部 type key は `interview`、日本語表示名は「ヒアリング記録」とする案を推奨する。
- `note` は廃止し、`scratch` に統合する。`note` と `scratch` を分けると、利用者もエージェントも「これは整理済みメモか、作業中メモか」で迷いやすい。
- `freeform` は type 名にしない。自由記述の体験は `scratch` の本文で提供する。
- `promotion-record` は独立 type にしない。文書そのものを昇格させるのではなく、蓄積した文脈をもとに新しい `adr` / `requirement.md` / `design.md` / `plan.md` を作成または修正する。
- authority level は、doc type 既定値 + 例外時のみ front matter override とする。詳細は別 question sheet `20260517t104954z-disc-question-authority-level-placement.md` にユーザー回答として記録済み。

## 推奨する初期 catalog

| type key | 日本語名 | lifecycle | 主用途 | authority 既定値 |
|---|---|---|---|---|
| `scratch` | 作業メモ | capture | 未整理メモ、思考途中、下書き、会話ログを一時保存する | `raw` |
| `interview` | ヒアリング記録 | elicitation | 利用者・関係者から得た事実、要望、制約、判断基準を残す | `raw` |
| `research` | 調査記録 | research | 外部/内部根拠、比較、検証結果、未確実性を残す | `synthesized` |
| `disc` | 議論記録 | framing | 未決の論点、選択肢、評価軸、合意/未合意を整理する | `proposed` |
| `adr` | 意思決定記録 | decision | 採用した判断、理由、影響、見直し条件を固定化する | `accepted` |

```plantuml
@startuml
title proposed discussion template catalog

skinparam backgroundColor #ffffff
skinparam shadowing false
skinparam roundcorner 8
skinparam defaultFontName "Hiragino Sans"
skinparam packageStyle rectangle

package "capture" {
  rectangle "scratch\n作業メモ\nraw" as scratch #f4f4f4
}

package "elicitation" {
  rectangle "interview\nヒアリング記録\nraw" as interview #e8f7ee
}

package "research" {
  rectangle "research\n調査記録\nsynthesized" as research #e8f7ee
}

package "framing" {
  rectangle "disc\n議論記録\nproposed" as disc #eef6ff
}

package "decision" {
  rectangle "adr\n意思決定記録\naccepted" as adr #fff4df
}

scratch --> interview : 人間に聞く
scratch --> research : 調査する
scratch --> disc : 論点化する
interview --> disc : 回答を比較・整理する
interview --> adr : 判断基準を決定化する
research --> disc : 根拠から選択肢比較へ
research --> adr : 根拠を決定へ反映
disc --> adr : 合意を固定化

@enduml
```

## 共通 metadata 案
- front matter の key は runtime / automation で扱いやすい英語 slug を維持する。
- template 本文の見出しと項目名は日本語にする。
- authority は doc type ごとの既定値を持ち、例外時だけ front matter の `authority` で override できるようにする。反映履歴の exact field は設計フェーズで確定する。

### 必須 metadata
| key | 日本語名 | 説明 |
|---|---|---|
| `type` | 種別 | `adr`, `disc`, `research`, `interview`, `scratch` のいずれか |
| `title` | タイトル | 文書の日本語タイトル |
| `status` | 状態 | `draft`, `active`, `accepted`, `superseded`, `archived` など |
| `created_at` | 作成日 | 作成日 |
| `updated_at` | 最終更新日 | 最終更新日 |
| `owner` | 主担当 | 主にこの文書を管理する人または agent |

### 任意 metadata
| key | 日本語名 | 説明 |
|---|---|---|
| `authority` | 権威レベル | `raw`, `synthesized`, `proposed`, `accepted`, `superseded` など |
| `related` | 関連先 | issue / PR / ADR / discussion docs |
| `source_refs` | 情報源 | 参照した docs、code、URL、発言記録 |
| `derived_from` | 参照元 | この文書を作成する際に参照した discussion docs |
| `reflected_to` | 反映先 | この文書の内容がどこへ反映されたか |
| `supersedes` | 置き換える文書 | この文書が置き換える過去文書 |
| `superseded_by` | 置き換え先 | この文書を置き換えた文書 |
| `tags` | タグ | 検索・分類用タグ |

## `scratch`: 作業メモ
- 目的:
  - 未整理の発話、思考、下書き、作業ログ、断片的な気づきを失わず置く。
  - 長期保存の正本ではなく、整理・反映・破棄を前提にする。
- 使わない場面:
  - 事実根拠として引用するなら `research`。
  - 人間からの聞き取り記録なら `interview`。
  - 論点や選択肢が明確なら `disc`。
  - 決定済みなら `adr`。

### 必須項目
| 項目名 | 説明 |
|---|---|
| メモ | 思考、下書き、作業ログ、断片的な気づき。自由記述を主役にする |

### 任意項目
| 項目名 | 説明 |
|---|---|
| 目的 | 何のための作業メモか |
| 文脈 | このメモが生まれた背景や作業状況 |
| 仮説 | まだ検証していない考え |
| 気になる点 | 違和感、懸念、後で確認したい点 |
| 参考 | 関連リンク、コード、既存資料 |
| 整理先候補 | `interview`, `research`, `disc`, `adr` のどれに整理するか |
| 破棄条件 | いつ、どの条件で捨てるか |
| 次にすること | 残す、捨てる、整理する、別文書を作成する、など |

## `interview`: ヒアリング記録
- 目的:
  - 利用者、クライアント、上司、プロダクトオーナー、reviewer から、事実、要望、制約、判断基準、優先順位を引き出す。
  - 発言とエージェントの解釈を混ぜずに残す。
- 使わない場面:
  - 人間に聞く必要がない技術調査は `research`。
  - 選択肢比較や合意形成は `disc`。
  - 決定済みの方針は `adr`。

### 必須項目
| 項目名 | 説明 |
|---|---|
| 聞き取り目的 | 何を明らかにするためのヒアリングか |
| 対象者・立場 | 誰から、どの立場の情報を得るか。必要なら匿名化する |
| 背景 | なぜこの聞き取りが必要か |
| 質問主題 | 何について回答してほしいか |
| 回答してほしいこと | 人間に判断・確認してほしい具体的な問い |
| なぜ質問するのか | なぜエージェントだけで決めず、人間の判断が必要なのか |
| 詳細説明 | 回答者が判断するために必要な補足、制約、前提 |
| 事前分析 | エージェントが質問前に調査・分析した内容 |
| 回答欄 | 得られた回答。発言と解釈を混ぜない |
| 確認した事実 | 回答から客観情報として扱えるもの |
| 要望・課題 | 相手が求めていること、困っていること |
| 回答案 | 人間が選びやすいように、エージェントが事前分析した複数の回答候補 |
| 選択肢比較 | 各回答案の利点、欠点、リスク、可逆性、実装・運用影響 |
| ベストプラクティス分析 | 一般的な推奨、既存実装との整合、長期保守性の観点で最もよい案を分析する |
| 推奨案 | エージェントが最も推奨する案と理由 |
| 未回答時の影響 | 回答が得られない場合に止まる判断、リスク、暫定対応 |
| 未確認事項 | 追加で確認すべきこと |
| 仕様・判断への影響 | requirement / design / plan / ADR にどう影響するか |
| 回答後フォローアップ | 回答後に作成・修正する `requirement` / `design` / `plan` / `adr` / `research` / `disc` |

### 任意項目
| 項目名 | 説明 |
|---|---|
| 実施日 | ヒアリング日 |
| 前提条件 | 相手の環境、制約、前提 |
| 重要な発言 | そのまま残す価値がある短い発言 |
| 解釈 | 回答から読み取れる仮説 |
| 合意事項 | 明示的に合意できた内容 |
| 非合意事項 | 合意できなかった内容 |
| フォローアップ | 追加質問、確認、次回対応 |
| 関連する議論・調査 | `disc` / `research` / issue へのリンク |
| 機微情報 | 取り扱い注意の有無。詳細を書きすぎない |

## `research`: 調査記録
- 目的:
  - docs、code、tests、issue、PR、外部仕様、ベストプラクティスなどの検証可能な根拠を整理する。
  - 事実、推測、未検証事項、判断への示唆を分ける。
- 使わない場面:
  - 人間への聞き取りは `interview`。
  - 選択肢比較と合意形成は `disc`。
  - 決定の正本は `adr`。

### 必須項目
| 項目名 | 説明 |
|---|---|
| 調査目的 | 何を明らかにするための調査か |
| 調査範囲 | 調査対象と対象外 |
| 問い | 調査で答えるべき質問 |
| 情報源 | 参照した docs、code、URL、issue、PR、実験結果 |
| 分かったこと | 確認できた事実 |
| 不確実な点 | まだ確認できていないこと |
| 意思決定への示唆 | requirement / design / ADR にどう効くか |

### 任意項目
| 項目名 | 説明 |
|---|---|
| 比較表 | 複数案の比較 |
| 推測・解釈 | 事実から導いた解釈。事実と混ぜない |
| 除外した選択肢 | 検討したが外したもの |
| 制約・前提 | 調査結果が成立する条件 |
| リスク | 採用時の懸念 |
| 再調査条件 | どの条件で再調査が必要か |
| 推奨アクション | 次に取るべき判断・作業 |

## `disc`: 議論記録
- 目的:
  - 未決の論点、選択肢、評価軸、推奨案、合意/未合意を整理する。
  - 決定前の decision support として使う。
- 使わない場面:
  - 生ログや作業中メモは `scratch`。
  - 聞き取り記録は `interview`。
  - 事実調査は `research`。
  - 決定済みの正本は `adr`。

### 必須項目
| 項目名 | 説明 |
|---|---|
| 議題 | 何について議論するか |
| 背景 | なぜこの議論が必要か |
| 目的 | この議論で決めたいこと、整理したいこと |
| 現状 | いま分かっていること |
| 論点 | 判断に必要な争点 |
| 選択肢 | 検討中の案 |
| 未解決事項 | まだ決まっていないこと |
| 次のアクション | 誰が何を確認・実施するか |

### 任意項目
| 項目名 | 説明 |
|---|---|
| 参加者・関係者 | 議論に関わる人や agent |
| 評価軸 | 選択肢を比較する基準 |
| 比較表 | 選択肢ごとの利点、欠点、リスク、可逆性 |
| 暫定結論 | 現時点の推奨または仮結論 |
| 合意事項 | 途中で合意できた内容 |
| 反対意見・懸念 | リスクや反対理由 |
| 判断保留の理由 | 何が不足していて決められないか |
| ADR 作成条件 | どの状態になったら、この議論を踏まえて ADR を新規作成するか |

## `adr`: 意思決定記録
- 目的:
  - 長期的に参照される決定、後続作業の前提になる判断、戻しにくい方針を固定化する。
  - `scratch` / `interview` / `research` / `disc` から得た材料を受け、決定、理由、影響、見直し条件を記録する。
- 使わない場面:
  - まだ決めていない探索段階。
  - 単なる会話ログ。
  - 調査結果の羅列。
  - 一時メモ。

### 必須項目
| 項目名 | 説明 |
|---|---|
| 決定 | 採用する方針 |
| 背景 | なぜこの決定が必要になったか |
| 制約 | 決定時点の制約や前提 |
| 検討した選択肢 | 比較した主要案 |
| 採用理由 | なぜその案を採用したか |
| 却下した選択肢 | 採用しなかった案と理由 |
| 影響 | 機能、運用、利用者、データ、互換性などへの影響 |
| 検証方法 | 決定が妥当か確認する方法 |
| 見直し条件 | どの事実が出たら見直すか |

### 任意項目
| 項目名 | 説明 |
|---|---|
| 関連 issue / PR | 関連する作業単位 |
| 関連 discussion | 関連する `disc` / `research` / `interview` / `scratch` |
| 移行方針 | 既存実装・既存運用からの移行方法 |
| ロールバック条件 | 戻す条件や戻し方 |
| セキュリティ影響 | security / privacy / compliance 上の影響 |
| 運用影響 | 運用手順、監視、保守への影響 |
| 再確認日 | 見直し予定日 |

## 採用しない候補

| candidate | 判断 | 理由 |
|---|---|---|
| `note` | 廃止 / `scratch` へ統合 | `scratch`, `disc`, `research` との境界が曖昧で、汎用メモ化しやすい |
| `freeform` | 不採用 | 自由記述は `scratch` の体験要件として扱う |
| `hearing` | type key としては不採用候補 | 日本語表示名は「ヒアリング記録」。内部 key は `interview` がより一般的 |
| `inquiry` | 不採用 | 調査・照会・質問が混ざり、`research` / `interview` と重なりやすい |
| `proposal` | 不採用 | `disc` の暫定結論または `adr` draft と重複する |
| `review` | 不採用 | review は workflow/status の性質が強く、PR / issue / report と散りやすい |

## 質問として分離した論点
- Q3: authority level を front matter に持たせるか。
  - discussion doc: `20260517t104954z-disc-question-authority-level-placement.md`
- Q4: promotion record を独立 type にするか。
  - discussion doc: `20260517t104958z-disc-question-promotion-record-type.md`

## 次アクション
- 要件定義書を、初期採用案 `adr` / `disc` / `research` / `interview` / `scratch` に合わせて更新する。
- Q3 / Q4 の回答を受けて、front matter と反映履歴の exact design を確定する。
- 設計フェーズで runtime allowlist、filename validation、template assets、docs、tests、dogfooding mirror の変更点を具体化する。
