---
種別: interview
ID: "20260701t044839z-interview"
タイトル: "Blank Versus Scratch Artifact Template"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
親: ["epic-00259"]
関連: []
scope: "<initiative | epic | issue | local-topic>"
scope_id: "epic-00259"
created_at: "2026-07-01THH:MM:SSZ"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "/Users/iwasawayuuta/.codex/attachments/dbb970bc-ae71-4b5a-a1bd-88959357eade/spec-dock-phase2-artifacts-pack.zip"
  - "src/spec_dock/assets/spec_dock/templates/README.md"
  - "src/spec_dock/assets/spec_dock/templates/discussions/scratch.md"
  - "src/spec_dock/assets/spec_dock/docs/guide.md"
  - "src/spec_dock/assets/spec_dock/docs/workflow_clarification.md"
reflected_to:
  - "../artifacts/20260701t055644z-adr-artifacts-future-only-command-unification.md"
---

# 20260701t044839z-interview Blank Versus Scratch Artifact Template

## 位置づけ
- 用途: 重要判断に関わる一つの質問を、回答前の source-grounded 正式質問シートとして作成し、回答後に同じ artifact を完成 record にする。
- authority default: `proposed`。ユーザー回答と採用判断を反映した後は、必要に応じて `user-approved` または `synthesized` に更新する。
- この artifact は answer capture / adoption target / reflection の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 技術的に調べられることは先に docs / code / tests / ADR / discussions / primary source を確認する。
- 一つの `interview` artifact には one essential question / 一つの本質的な質問だけを書く。回答によって新しい高影響な曖昧さが見つかった場合は、追加質問をこの file に増やさず、次の unanswered `interview` を作成する。
- trivial な yes/no は、重要な判断、後続反映、回答証跡が必要なら `interview` を使い、そうでなければ issue comment や `scratch` で足りる。
- 回答から複数質問の synthesis が必要になったら `disc`、追加調査が必要になったら `research`、長期判断が固まったら `adr` を新規作成する。

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - artifact template catalog と raw capture policy。
  - `design.md`:
    - `new artifact` の creatable template enum、filename parser / generator、legacy `new doc scratch` との関係。
  - `plan.md`:
    - Issue 02 / 03 / 04 / 07 の acceptance criteria と tests。
  - `ADR`:
    - `blank` を raw/freeform の標準にするか、`scratch` を artifact catalog に残すかの長期用語判断。
- chat 上の軽微な一問では足りない理由:
  - `scratch` は現行 docs で raw capture の標準用語だが、ZIP pack は artifact templates から除外し、自由記述用途を `blank` に寄せている。どちらを標準にするかで docs と runtime contract が変わる。

## 質問の目的 (必須)
- 対象者:
  - spec-dock maintainer / product owner。
- 何を明確にする質問か:
  - Phase 2 の `artifacts/` template catalog に `scratch` を含めるか、`blank` へ統合するか。
- 回答が後続判断へ与える影響:
  - Supported templates、filename rules、template files、skills/docs wording、legacy `new doc scratch` の説明が決まる。

## 質問 (必須)
- pressure-test question:
  - 既存では raw capture は `scratch` ですが、Phase 2 の artifact catalog では自由記述を `blank` と呼びます。今後の標準用語をどちらにしますか。
- 質問:
  - `artifacts/` の creatable template に `scratch` を含めますか。それとも ZIP 案どおり、`scratch` は legacy `new doc` 側に残し、新しい `artifacts/` では自由記述・raw capture を `blank` template に統合しますか。
- 回答してほしいこと:
  - 下の Option A / B / C のどれを採用するか、または近い案を指定してください。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - ZIP pack: supported artifact templates は `blank`, `research`, `interview`, `disc`, `decision-candidate`, `pr-repair-batch`。`scratch` は含まれていない。
  - `templates/README.md`: current discussion catalog は `scratch` を含み、`note` は retired、新規 raw capture は `scratch` と説明している。
  - `templates/discussions/scratch.md`: raw capture / low-friction notes の template として定義されている。
  - `workflow_clarification.md`: `scratch` は raw capture、`research` / `interview` / `disc` / `adr` と並ぶ artifact selection の一種。
- local context で解決できたこと:
  - `note` は既に retired で、raw capture の新規作成先は `scratch` に整理済み。
  - Phase 2 で `blank` を導入すると、raw/freeform の最小テンプレート役割が `scratch` と重複する。
- まだ人間判断が必要な理由:
  - ZIP 案を優先して `blank` に統合するか、現行用語の連続性を優先して `scratch` を artifact catalog に残すかは product terminology の判断である。

## 回答案 (必須)
- Option A:
  - ZIP-aligned: `artifacts/` catalog は `blank`, `research`, `interview`, `disc`, `decision-candidate`, `pr-repair-batch` の 6 種にする。`scratch` は legacy `new doc scratch` と既存 discussions に残すが、新規 artifact では `blank` を使う。
- Option B:
  - Continuity: `artifacts/` catalog に `scratch` も追加し、raw capture の標準用語を継続する。`blank` はさらに自由度の高い無分類メモとして別扱いにする。
- Option C:
  - Rename-by-policy: `blank` は採用せず、artifact catalog の自由記述 template を `scratch` にする。ZIP の filename rule / command examples を `scratch` 前提に書き換える。

## Codex の分析 (必須)
- 判断軸:
  - template catalog の小ささ、既存用語との連続性、agent が迷わないこと、filename contract の単純さ。
- tradeoff:
  - `blank` は自由度が高く template type を filename に含めない特別規則と相性がよい。一方で、raw capture という意味は `scratch` の方が明確。
- リスク:
  - Option B は `blank` と `scratch` の使い分けが曖昧になり、過去の `note` retirement と同じ認知負荷を再導入するリスクがある。Option C は ZIP pack の前提と filename contract を大きく書き換える。
- 具体シナリオ / edge case:
  - 低摩擦に「とりあえず置く」用途は `blank` で足りるが、後から「これは raw capture だった」と分かるよう front matter に `template: "blank"` と `authority: "raw"` を持たせる必要がある。

## Codex の推奨案 (必須)
- 推奨:
  - Option A。
- 理由:
  - ZIP pack と command / filename contract を保てる。`note` retirement の教訓どおり、自由記述系 template を増やしすぎない方が agent guidance が明確になる。既存 `scratch` は legacy `new doc` と既存 discussions の互換として残せば破壊は避けられる。
- 未回答時の影響:
  - Artifact template catalog、docs rewrite、`new artifact` accepted template enum、validation tests を確定できない。

## ユーザー回答 (回答後に必須)
- answer capture:
  - Option A を採用する。
- 回答:
  - 「オプションAを採用します。」
- 回答日時:
  - 2026-07-01

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - ADR original location を Phase 2 でも legacy `new doc adr` / `discussions/` に残すか、`artifacts/` 移行対象に含めるか。

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `ADR`
  - `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - ユーザーが Option A を明示採用した。`artifacts/` の creatable template catalog は ZIP 案どおり 6 種にし、raw/freeform 用途は `blank` に統合する。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - Phase 2 の artifacts template catalog は `blank`, `research`, `interview`, `disc`, `decision-candidate`, `pr-repair-batch` の 6 種とする。
- `design.md`:
  - `new artifact blank` は freeform / raw capture の標準 entrypoint とし、filename に `blank` を含めない。`scratch` は artifact template enum に入れない。
- `plan.md`:
  - Issue 02 / 03 / 04 / 07 の acceptance criteria と tests は 6 種 template 前提で記述する。
- `ADR`:
  - `scratch` は Phase 2 の new artifact catalog には含めず、legacy `new doc scratch` / existing discussions compatibility として残す Decision を記録する。
- reflected_to 更新方針:
  - ADR draft 作成後に `reflected_to` を更新し、canonical docs へ採用した時点で report ledger に記録する。
- adoption reflection:
  - Option A は採用済み。これにより `blank` と `scratch` の二重標準化は避ける。

## 条件付き補足 (必要な場合だけ)
- PlantUML 図:
  ```plantuml
  @startuml
  ' TODO: 質問依存、意思決定フロー、before/after、責務境界が必要なら追加する
  @enduml
  ```
- 詳細 tradeoff:
  - ...
- 後続 reflection proposal:
  - ...
- 追加で作る discussion docs:
    - ...
