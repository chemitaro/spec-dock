---
種別: 要件定義書（Issue）
ID: "iss-00100"
タイトル: "Discussion template hearing sheet and flexible note expansion"
関連GitHub: ["#100"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-05-17"
親: ["epic-00067", "init-local-00003"]
---

# iss-00100 Discussion template taxonomy and elicitation/capture expansion — 要件定義（WHAT / WHY）

## 目的
- `spec-dock` の `discussions/` 用テンプレート群を、単なる doc type の追加ではなく、情報ライフサイクル、権威性、後続 artifact への反映ルールに基づいて再整理する。
- 既存の `adr` / `disc` / `research` / `note` の責務を再評価し、特に `note` と raw capture の衝突、`disc` とユーザーへのヒアリング用シートの重複を解消する。
- ユーザー、上司、クライアント、プロダクトオーナーなど人間から未確定情報を引き出す elicitation 用のシートと、まだ分類できない思考や会話ログを低摩擦に受ける raw capture 用のシートを、既存テンプレートとの境界を壊さずに扱えるようにする。
- 追加 type は、設計素案では `interview`（表示名: ヒアリング記録）と `scratch` を有力な初期採用候補とする。ただし設計フェーズで runtime impact と naming を確認し、最終確定する。

## 背景・現状
- 現状の discussion doc は `./spec-dock/scripts/spec-dock new doc {adr|disc|research|note} --{initiative|epic|issue} <id> --title "..."` で作成される。
- provider-side 正本は `src/spec_dock/assets/spec_dock/templates/discussions/`、dogfooding mirror は `spec-dock/templates/discussions/` にある。
- 既存テンプレートの概略:
  - `adr`: 長期的に参照される architecture / contract / migration decision の記録。
  - `disc`: 論点整理、選択肢比較、合意形成の叩き台。
  - `research`: 外部仕様、実装事実、先例、制約などの調査記録。
  - `note`: 背景、事実、検討、次アクションを持つ軽量な整理済みメモ。
- 現状の主な問題:
  - `disc` が、論点整理、設計比較、ヒアリング、軽量意思決定、合意形成、次アクション整理を広く吸収できてしまい、doc type 選択の判断が曖昧になっている。
  - 人間に質問するための資料が `disc` / `note` に散らばり、質問主題、質問理由、背景、事前分析、回答候補、推奨案、回答欄、回答後の反映先が揃いにくい。
  - 既存 `note` は軽量だが十分に構造化されており、ヘッダーとタイトルだけ固定して自由に書きたい raw capture の入口としてはまだ硬い。
  - `research` は事実調査に適しているが、事実、推測、未検証事項、判断への含意を分ける guidance が弱く、調査結果がそのまま決定のように見える余地がある。
  - discussion docs の文脈をもとに、いつ新しい `adr` を作成し、いつ `requirement` / `design` / `plan` へ織り込むかの反映ルールが弱い。

## コンサルタント分析の統合
- 詳細な分類説明と図解は、discussion doc `20260517t075915z-disc-discussion-template-taxonomy-guide.md` を参照する。具体的な初期 catalog 設計素案は、discussion doc `20260517t103746z-disc-discussion-template-catalog-design-proposal.md` を参照する。この要件定義書では、実装要件と acceptance criteria に必要な要点だけを保持する。
- 合意点:
  - 安易な type 追加は、選択コストと重複を増やすため危険である。
  - `disc` とヒアリングの重複は実在する。`disc` は「集まった情報をもとに論点、選択肢、合意点を整理する場」、ヒアリング用シートは「人間から未確定情報を引き出し、回答を記録する場」と分けるべきである。
  - `freeform` という type 名は役割を表しにくく、公式のごみ箱になりやすい。raw capture を入れる場合は、非 authoritative であり、後続 artifact へ反映するための入口として制約する必要がある。
  - 既存4種類を壊すより、まず責務、authority level、selection guide、反映ルールを明確化するべきである。
  - 人間への質問では、エージェントが先に調査・分析し、複数案と推奨案を出したうえで、なぜ人間の判断が必要なのかを明示する必要がある。
- 意見が分かれた点:
  - elicitation を新 type `interview` として独立させるか、`hearing` / `inquiry` / `disc mode: hearing` / `research method: interview` にするか。
  - raw capture を新 type `scratch` として独立させるか、既存 `note` を維持して分離するか。
  - `decision-request`、`review-request`、`risk-brief`、`assumption-check` などを初期実装に含めるか。初期実装では候補整理に留める方が安全という意見が強い。
- 要件上の判断:
  - 本 issue の主目的は「`hearing` と `freeform` を機械的に2種類追加すること」ではなく、「discussion template 群の taxonomy を整理し、欠落している elicitation / raw capture の受け皿を最小十分な形で実装すること」とする。
  - 初期 catalog の暫定推奨は `adr` / `disc` / `research` / `interview` / `scratch` の5種類とする。`note` は廃止して `scratch` に統合する方向を第一候補とする。ただし、最終名と implementation shape は設計フェーズの decision gate で決める。

## 目標 taxonomy
- `discussions/` は、次の情報ライフサイクルを支える補助 artifact 群として設計する。

```text
capture -> elicitation -> research -> framing -> decision -> execution handoff
```

| lifecycle | 目的 | 既存/候補 template |
|---|---|---|
| capture | 未整理の発話、観察、思考、会話ログを失わず置く | `scratch` |
| elicitation | 人間から目的、制約、期待、判断基準、未決事項を引き出す | `interview`（表示名: ヒアリング記録） |
| research | 事実、仕様、実装、先例、外部制約を確認する | `research` |
| framing | 論点、選択肢、評価軸、合意すべき点を整理する | `disc` |
| decision | 長期的な判断と理由を記録する | `adr` |
| execution handoff | 合意内容を `requirement` / `design` / `plan` / issue work へ反映する | 各 template の follow-up / reflected_to 欄 |

## type 増減の判断基準
- 新 type は、次の条件をすべて満たす場合だけ追加する。
  - 既存 type と workflow phase が明確に異なる。
  - 主な読者、作成タイミング、完了条件、authority level が既存 type と異なる。
  - 後続 artifact への出力が既存 type と異なる。
  - 既存 type の section / mode / kind 追加では、利用者の選択負荷や誤用を十分に下げられない。
- 次の条件に当てはまる場合は、新 type ではなく既存 type の改善を優先する。
  - 違いが見出し構成だけである。
  - `disc` / `research` / `scratch` の selection guide を明確にすれば解決できる。
  - 長期的な正本にならない一時的な情報である。
  - 将来候補だが利用頻度や boundary がまだ検証されていない。

## スコープ
- 必須:
  - 既存 `adr` / `disc` / `research` の責務と、追加候補 `interview` / `scratch` の authority level、使い分けを docs または template guidance で明確化する。
  - `disc` は主に framing / decision support のための template であり、ヒアリング回答の主たる記録先ではないことを明確にする。
  - elicitation 用の支援を実装する。暫定推奨は新 type `interview` とし、日本語表示名は「ヒアリング記録」とする。
  - raw capture / freestyle writing 用の支援を実装する。暫定推奨は新 type `scratch` とする。
  - 既存 `note` は `scratch` へ統合する前提で、互換性、migration 不要方針、既存 `note` の grandfathering を設計で扱う。
  - template selection guide を更新し、少なくとも `adr` / `disc` / `research` / `interview` / `scratch` の使い分けを説明する。
  - エージェント向け docs に、information lifecycle、authority level、反映ルール、思考・知識・未確定情報を外部化する原則を追加する。
  - 文書そのものを昇格させるのではなく、discussion docs の文脈をもとに新しい `adr` を作成し、`requirement` / `design` / `plan` を作成・修正する guidance を追加する。
  - 採用した新 type がある場合は、runtime allowlist、template assets、installer/update、tests、dogfooding mirror を一貫して更新する。
- 推奨:
  - elicitation 用シートには PlantUML または図解用の任意 section を置き、質問の依存関係、意思決定フロー、before/after、責務境界を可視化できるようにする。
  - `research` には、事実、推測、未検証、判断への含意を分ける guidance を追加する。
  - `scratch` には、自由記述を妨げない一方で、整理先候補、破棄条件、次にすることを記録できる guidance を置く。
- 禁止:
  - `hearing` / `interview` / `freeform` を、境界分析なしに無条件で追加しない。
  - `disc` をさらに万能化し、elicitation / research / decision / scratch の役割をすべて吸収させない。
  - raw capture 用 template を authoritative decision / investigation / requirement の代替正本にしない。
  - `adr` を汎用議事録や合意形成ワークスペースとして肥大化させない。
  - エージェントが調査可能な技術事項を、未調査のまま人間への質問で代替しない。
- 対象外:
  - `decision-request`、`approval-request`、`review-request`、`risk-brief`、`assumption-check`、`experiment`、`meeting`、`postmortem`、`traceability` の独立 type 化。
  - 回答待ち dashboard、notification、承認 workflow、状態遷移 command。
  - raw capture から他 type への自動変換 command。
  - 既存 discussion doc の migration / rename。

## 非交渉制約
- 新規または変更する path / doc type 名は lowercase とする。
- 人間への質問は、短時間で回答できる構造を持たなければならない。
- 人間への質問は、質問ごとに質問主題、質問理由、背景、事前分析、回答候補、選択肢分析、推奨案、回答欄、回答後 follow-up を持たなければならない。
- 人間への質問は、調査可能事項を質問で代替しないための guardrail を持たなければならない。
- raw capture は、front matter / header / title 以外の本文構造を強制しないか、強制する場合でも自由記述を妨げない最小限に留めなければならない。
- raw capture は、非 authoritative であり、必要に応じて `research` / `disc` / `adr` / `requirement` / `design` / `plan` を作成・修正する guidance を持たなければならない。

## 反映ルール
- `capture` / raw capture:
  - 事実確認や外部根拠が必要になったら、文脈をもとに `research` を新規作成する。
  - 論点、選択肢、合意形成が必要になったら、文脈をもとに `disc` を新規作成する。
  - 人間の回答や判断が必要になったら、文脈をもとに `interview` を新規作成する。
  - 長期的な方針決定になったら、文脈をもとに `adr` を新規作成する。
- elicitation:
  - 回答は `requirement` / `design` / `plan` / `adr` のどこへ反映するかを明示する。
  - 回答が新しい論点や選択肢を生む場合は `disc` へつなぐ。
  - 回答が追加調査を必要とする場合は `research` へつなぐ。
- `research`:
  - 調査結果が選択肢比較を必要とする場合は `disc` へつなぐ。
  - 調査結果が長期判断を支える場合は `adr` へつなぐ。
- `disc`:
  - 合意内容は `requirement` / `design` / `plan` へ反映する。
  - 長期的・横断的・不可逆寄りの判断は、議論の積み上げをもとに新しい `adr` を作成する。
- `scratch`:
  - 未整理情報の一時的な置き場として扱う。長期保存する価値が出た場合は、文脈をもとに `interview` / `research` / `disc` / `adr` を新規作成する。

## 受け入れ条件
- AC-001: 既存 taxonomy が明文化される
  - アクター: エージェント / maintainer / reviewer
  - 前提: docs または template guidance を読む
  - 期待結果:
    - `adr` / `disc` / `research` / `interview` / `scratch` の目的、authority level、使う場面、使わない場面が説明されている。
    - `disc` と `interview` の違いが説明されている。
    - `note` を廃止して `scratch` に統合する理由が説明されている。
- AC-002: elicitation 用シートまたは variant が実装される
  - アクター: エージェント / user / reviewer
  - 前提: 採用した実装形態の template または template variant を読む
  - 期待結果:
    - 質問主題、回答してほしいこと、なぜ質問するのか、背景、詳細説明、事前分析、回答候補、選択肢比較、メリット/デメリット、リスク、ベストプラクティス分析、推奨案、未回答時の影響、回答欄、回答後 follow-up を記録できる。
    - エージェントが事前に調査・分析したことを示す欄または guardrail がある。
    - 回答が `requirement` / `design` / `plan` / `adr` のどこへ反映されるかを記録できる。
- AC-003: elicitation と `disc` の重複が制御される
  - アクター: reviewer
  - 前提: selection guide を読む
  - 期待結果:
    - 人間から回答を引き出し、回答欄と未回答事項を管理する場合は elicitation 用シートを使うことが分かる。
    - 集まった情報をもとに論点、評価軸、選択肢、推奨案、合意点を整理する場合は `disc` を使うことが分かる。
    - ひとつの doc が両方を過剰に兼ねないよう、分割または新規 artifact 作成の guidance がある。
- AC-004: raw capture / freestyle writing が実装される
  - アクター: エージェント / maintainer
  - 前提: 採用した実装形態の template を読む
  - 期待結果:
    - ヘッダーとタイトル以外は、自由記述を妨げない。
    - 非 authoritative であることが分かる。
    - 後で facts / questions / decisions / actions / links などを抽出できる最小 guidance がある。
    - `scratch` は正本ではなく、必要に応じて他 artifact を新規作成または修正する入口であることが説明されている。
- AC-005: 反映ルールが実装 guidance に入る
  - アクター: エージェント / reviewer
  - 前提: docs または template guidance を読む
  - 期待結果:
    - raw capture の文脈をもとに `research` / `disc` / `interview` / `adr` を新規作成する条件が分かる。
    - elicitation -> `requirement` / `design` / `plan` / `research` / `disc` / `adr` の反映先が分かる。
    - `research` や `disc` の内容をもとに新しい `adr` を作成し、ADR の内容を `requirement` / `design` / `plan` へ織り込む流れが分かる。
- AC-006: runtime / installer / tests は採用した type set と整合する
  - アクター: maintainer
  - 前提: 設計フェーズで新 type を採用した場合
  - 期待結果:
    - `new doc <type>` の allowlist、template assets、installer/update、dogfooding mirror、CLI/runtime tests が採用 type と一致する。
    - 採用しなかった候補は runtime supported type として追加されない。
    - 既存 `adr` / `disc` / `research` の作成は regression しない。
    - 既存 `note` は grandfathered artifact として壊さず、新規作成 type として継続するか廃止するかの互換性方針が明確である。
- AC-007: 初期実装は候補 type を増やしすぎない
  - アクター: reviewer
  - 前提: issue diff を確認する
  - 期待結果:
    - 初期実装で新規 product type を追加する場合、`interview` と `scratch` の最小セットに留まる。
    - `decision-request` / `approval-request` / `review-request` / `risk-brief` / `assumption-check` / `experiment` / `meeting` / `postmortem` などは future candidate または既存 type の guidance に留まる。
- AC-008: 視覚的・構造的に分かりやすい
  - アクター: user / reviewer
  - 前提: docs または template を読む
  - 期待結果:
    - selection guide または template に、表、手順、または PlantUML / Mermaid 用の任意 section があり、回答者や reviewer が構造を把握しやすい。
    - 図がなくても本文だけで意味が通る。
- AC-009: エージェント向け lifecycle guidance が残る
  - アクター: エージェント / maintainer / reviewer
  - 前提: shipped docs または agent-facing workflow docs を読む
  - 期待結果:
    - discussion docs は思考、知識、未確定情報を外部化する作業面であることが説明されている。
    - discussion docs 自体を正本化せず、discussion docs の文脈をもとに新しい `adr` を作成し、`requirement.md` / `design.md` / `plan.md` へ織り込んで固定化することが説明されている。
    - authority level、reflected_to、stale / discard condition の考え方が説明されている。

## 例外・エッジケース
- EC-001: 単純な yes/no 確認
    - 重要な判断、後続反映、回答証跡が必要なら `interview` を使う。
    - trivial な確認なら issue comment や `scratch` で足りる場合がある。
- EC-002: open-ended なヒアリング
  - 原則として回答候補、選択肢比較、推奨案を出す。
  - 本当に回答候補を出せない場合でも、質問理由、背景、事前分析、期待する回答形式、候補を出せない理由、回答後 follow-up は記録する。
- EC-003: 技術的に調べられる質問
  - まず docs / code / tests / ADR / discussions / primary source を調査する。
  - 調査後に user intent、policy、priority、risk tolerance、private context に依存する判断だけを人間に聞く。
- EC-004: interview transcript
  - 生ログや transcript は raw capture として受けられる。
  - 証拠や調査結果として扱う場合は `research` を作成し、回答管理として扱う場合は `interview` を作成する。
- EC-005: raw capture に decision が混ざる
  - raw capture のまま決定済み扱いにしない。
  - 必要に応じて `disc` / `adr` / authoritative docs を新規作成または修正する。
- EC-006: `disc` が膨らみすぎる
  - 質問回答の収集は elicitation へ、事実調査は `research` へ、生ログは raw capture へ分離する。
- EC-007: 既存 `note` の扱い
  - 既存 `note` artifact は grandfathered として壊さない。
  - 新規作成では `scratch` を使い、必要に応じて `research` / `disc` / `adr` を新規作成する。

## 用語
- `elicitation`
  - 人間から目的、制約、期待、判断基準、未決事項を引き出す活動。
- `raw capture`
  - まだ `research` / `disc` / `adr` / `interview` に分類しない発話、観察、思考、会話ログの仮置き。
- `authority level`
  - artifact がどの程度、後続作業の正本として扱われるかの強さ。raw capture は低く、ADR と authoritative docs は高い。
- `reflected_to`
  - discussion doc の文脈をもとに作成・修正された `adr` / `requirement.md` / `design.md` / `plan.md` などの反映先。

## 未決事項
- Q-001: elicitation の type key
  - A: 新 type `interview`
    - 利点: 英語 type key として一般的で、UX research / 要件聞き取り / stakeholder interview の文脈に合う。
    - 懸念: 日本語利用者には「ヒアリング」よりやや硬く見える可能性がある。
  - B: 新 type `hearing`
    - 利点: 日本語業務の「ヒアリング」には直感的。
    - 懸念: 英語では公聴会・聴聞の意味が強く、machine-readable key として誤解されやすい。
  - 暫定推奨: type key は `interview`、日本語表示名は「ヒアリング記録」とする。
- Q-002: `note` を廃止して `scratch` へ統合するか
  - A: `note` を廃止し、新規 raw / lightweight memo は `scratch` に統合する
    - 利点: 境界が明確で、汎用メモの増殖を避けられる。
    - 懸念: 既存 `note` との互換性方針が必要。
  - B: `note` と `scratch` を分ける
    - 利点: 整理済みメモと未整理メモを分けられる。
    - 懸念: 実務上、境界が崩れやすく、情報が散る。
  - 暫定推奨: A。既存 `note` は grandfathered とし、新規作成は `scratch` に寄せる。
- Q-003: `disc` の強化範囲
  - A: `disc` を decision support / framing に絞って明確化する。
  - B: `disc` に hearing / interview section を追加して吸収する。
  - 暫定推奨: A。`disc` の肥大化を避ける。
- Q-004: future candidate の扱い
  - `decision-request`、`approval-request`、`review-request`、`risk-brief`、`assumption-check`、`experiment`、`meeting`、`postmortem` は有用候補だが、本 issue では独立 type 化しない。
