---
種別: disc
ID: "20260520t081426z-disc"
タイトル: "Plan as executable Agentic TDD workflow contract"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-05-20"
親: ["iss-00102"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260520t081426z-disc Plan as executable Agentic TDD workflow contract

## 位置づけ
- 用途: 集まった情報をもとに、論点、評価軸、選択肢、合意点/未合意点を整理する。
- authority default: `proposed`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- 人間から回答を引き出し、回答欄や未回答事項を管理する場合は `interview` を使う。
- 生ログや未整理の思考は `scratch`、事実確認や外部根拠は `research`、長期判断の固定は `adr` に分ける。
- doc が大きくなりすぎたら、質問回答は `interview`、事実調査は `research`、raw capture は `scratch`、長期決定は `adr` へ分割する。

## 議題 (必須)
- Agentic TDD を単に docs / policy に説明するだけではなく、生成される Issue `plan.md` 自体が実装エージェント向けの executable workflow contract になるべきかを整理する。
- `requirement.md` に「plan.md の構造が Red / Green / Refactor / Evidence / Closure を実行させる」要求を追加すべきか判断する。

## 背景 (必須)
- これまでの分析では、`1〜3件程度` の test count guidance を削除または非規範化し、risk-calibrated test obligation coverage に置換する方針を採った。
- ただし、Agentic TDD の作業ステップを `workflow_issue.md` や authoring docs に説明しても、実装担当エージェントが実際に読む `plan.md` が従来の作業一覧のままなら、Red / Green / Refactor が再現よく実行されるとは限らない。
- 実装エージェントは通常、active issue の `plan.md` を step queue / handoff contract として読む。そのため、Agentic TDD の実行圧は説明文ではなく、`plan.md` の step schema、必須欄、closure gate、reviewer gate に埋め込む必要がある。
- 追加 consultant / deep-consultant の見解は一致している:
  - `plan.md` は単なる作業一覧ではなく、実装者向けの executable workflow contract として要件化すべき。
  - 各 implementation step は原則 behavior slice であり、Agentic TDD cycle / review scope / commit boundary を表すべき。
  - 各 step には Red / Green / Refactor / Evidence / Closure またはそれに相当する欄と gate を持たせるべき。
  - report template や execute prompt だけに規律を置くと後追い作文になり、実装中の制御として弱い。

## 選択肢 (必須)
- Option A: Agentic TDD の説明を workflow / authoring docs に置き、plan template は薄い作業一覧に留める。
  - Pros:
    - plan template は軽い。
    - 既存の step template 変更量は小さい。
  - Cons:
    - 実装エージェントが `plan.md` だけを見て大きな横断実装へ進むリスクが残る。
    - Red / Green / Refactor evidence が report 側の後追い記録になりやすい。
    - reviewer は「文書に説明があるか」は見られても、各 step が TDD cycle として閉じているかを検査しにくい。
- Option B: `plan.md` を executable Agentic TDD workflow contract にする。
  - Pros:
    - 実装エージェントが step を順に辿るだけで、Red / Green / Refactor / Evidence / Closure の流れに乗りやすい。
    - step closure が「実装した」ではなく、evidence と reviewer gate で閉じる契約になる。
    - plan review と execution review が、同じ step schema を基準にできる。
    - report が plan step の実績・逸脱・amendment を trace する ledger として機能する。
  - Cons:
    - template が重くなりやすい。
    - docs-only / inspect-only / no-new-test の例外をうまく表現しないと、形式主義になる。
    - template だけでは強制力が弱く、authoring docs / execute prompt / skill / reviewer config と同期が必要。

## 推奨案 (必須)
- Option B を採用する。
- `requirement.md` には、次の要求を追加する:
  - generated Issue `plan.md` は、外部 docs を参照するだけでなく、Agentic TDD の実行手順を内包する executable workflow contract である。
  - 各 implementation step は原則 1 behavior slice / 1 Agentic TDD cycle / 1 review scope / 1 commit boundary を表す。
  - 各 step は少なくとも behavior goal、test obligation、Red evidence または正当な代替、implementation scope、Green verification、refactor / cleanup 方針、closure evidence、amendment trigger を持つ。
  - 新規テスト不要の step は許容するが、no-new-test / inspect-only / manual-only の理由、既存 coverage、risk assessment、代替 evidence を step 内に残す。
  - step closure は Red / Green / Refactor / Evidence / report update / reviewer gate が満たされるまで閉じられない。
- `templates/issue/plan.md` は「Agentic TDD の説明文」ではなく、実装エージェントが埋めて実行する checklist / handoff schema として再構成する。
- `docs/authoring/issue-plan.md` は、その schema をどう書くかの正本にする。良い step / 悪い step、risk-calibrated test obligation、amendment trigger の例を持つ。
- `workflow_issue.md` は、`plan.md` を command queue / executable workflow contract として扱う execution policy を短く固定する。
- `execute-issue.md` / skill は、実装 agent に `plan.md` の step を順に実行させ、step 外実装や evidence なし closure を止める routing に寄せる。
- reviewer config は、plan review gate と execution/report review gate の両方で、各 step が executable TDD cycle として閉じているかを見る。

## 未決事項 (任意)
- plan template の必須欄名を `Red / Green / Refactor` と明示するか、既存の `pre-implementation evidence` / `behavior slice execution` / `step gate` を整理して対応させるか。
- `plan.md` に実行中 evidence 欄をどこまで持たせ、`report.md` にどこから final evidence summary を持たせるか。
- 軽微な docs-only / inspect-only step でも同じ schema を使うか、短縮形を許可するか。

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - requirement:
    - `plan.md` は executable workflow contract であることを目的・スコープ・受け入れ条件・用語に追加する。
    - step closure が Red / Green / Refactor / Evidence / reviewer gate を満たすまで閉じられないことを追加する。
    - docs-only / no-new-test 例外は silent skip ではなく rationale と代替 evidence を必須にする。
  - design:
    - `plan.md` step schema と report ledger の対応を設計する。
    - workflow / authoring / template / execute prompt / skill / reviewer config のどこが plan-as-command-queue を担保するかを設計する。
  - plan:
    - `templates/issue/plan.md` の step schema を Agentic TDD cycle が表現される構造へ更新する step を追加または明確化する。
    - `execute-issue.md` / skill / reviewer config が plan step schema を検査・実行する step を追加または明確化する。
- 追加で作る discussion docs:
  - 現時点では不要。設計時に plan step schema の候補比較が大きくなる場合だけ追加する。
