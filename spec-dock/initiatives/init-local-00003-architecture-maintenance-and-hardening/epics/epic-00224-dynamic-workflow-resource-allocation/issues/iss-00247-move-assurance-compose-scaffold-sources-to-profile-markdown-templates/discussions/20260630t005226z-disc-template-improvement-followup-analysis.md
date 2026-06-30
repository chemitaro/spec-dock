---
種別: disc
ID: "20260630t005226z-disc"
タイトル: "テンプレート改善フォローアップ分析"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-06-30"
親: ["iss-00247"]
関連:
  - "src/spec_dock/assets/spec_dock/templates/issue/requirement.md"
  - "src/spec_dock/assets/spec_dock/templates/issue/report.md"
  - "src/spec_dock/assets/spec_dock/templates/issue-profiles/*/{design,plan}.md"
  - "src/spec_dock/assets/spec_dock/docs/workflow_issue.md"
  - "src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md"
  - "src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md"
authority: "proposed"
derived_from:
  - "ユーザー共有メモ: テンプレート改善フォローアップ"
  - "repo search: 001/002, PlantUML inheritance, commit gate, step/review/commit wording"
reflected_to: []
---

# 20260630t005226z-disc テンプレート改善フォローアップ分析

## 位置づけ
- この artifact は、ユーザーが別チャットで整理したテンプレート改善案を、現在の `iss-00247` / PR 修正候補としてどう反映すべきか分析する discussion evidence である。
- `./spec-dock/scripts/spec-dock guidance issue-planning` は `state: no-active` / `next_action: issue-start-required` を返したため、ここでは canonical `requirement.md` / `design.md` / `plan.md` / `report.md` は更新しない。
- 反映する場合は provider 側の `src/spec_dock/assets/spec_dock/...` を source of truth とし、dogfooding 側の `spec-dock/...` は整合確認または同期対象として扱う。
- この artifact 自体は `authority: proposed` であり、採用は canonical docs / template への反映と `report.md` Evidence Adoption Ledger への記録で成立する。

## 対象論点 (必須)
- 今回整理する論点:
  - `001`, `002` の例示が「2件限定」に見える問題を、テンプレート上でどう防ぐか。
  - PlantUML クラス図で継承・実装矢印が下向きに描かれやすい問題を、設計書テンプレートでどう誘導するか。
  - `standard` / `strict` / `critical` の実装計画書テンプレートに、マイルストーン完了ゲート内の `commit候補` をどう埋め込むか。
  - 古い `1 implementation step = 1 review scope = 1 commit` 方針を、grade 別の `milestone / behavior / gate` 中心設計へどう更新するか。
  - `report.md` が、実際の review evidence、verification evidence、commit または no-op result を記録できる形と整合しているか。
- この synthesis が必要な理由:
  - 既存テンプレートは profile Markdown 化で構造が強くなった一方、例示行や古い workflow 文言が agent の過剰固定を誘発する可能性が残っている。
  - PR はすでに review / CI が通る状態まで進んでいるため、追加修正を同じ PR に入れる場合は、修正範囲と再検証対象を明確にしてから進める必要がある。

## derived question sheets / research (必須)
- `interview`:
  - なし。今回の入力はユーザー共有メモとして十分に具体的で、追加質問なしで実装修正案へ分解できる。
- `research`:
  - 現時点では別 artifact は作成していない。repo search と対象ファイルの直接確認に基づく。
- その他の根拠:
  - `src/spec_dock/assets/spec_dock/templates/issue-profiles/{lite,standard,strict,critical}/plan.md`
  - `src/spec_dock/assets/spec_dock/templates/issue-profiles/{lite,standard,strict,critical}/design.md`
  - `src/spec_dock/assets/spec_dock/templates/issue/{requirement,report}.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md`
  - dogfooding mirror: `spec-dock/templates/...` と `spec-dock/docs/...`

## synthesis (必須)
- 合意済みのこと:
  - テンプレートの見出し・説明は原則日本語にし、日本語だけで正しく表現しにくい用語だけ括弧で英語名を補う。
  - 複数項目を持つリスト・テーブル・レコードは、必要な数だけ追加できることをテンプレート上で示す。
  - `lite` の実装計画書テンプレートには途中 `commit` 項目を追加しない。
  - `standard` / `strict` / `critical` の実装計画書テンプレートには、主要なマイルストーン完了ゲートに共通型の `commit` 項目を追加する。
  - `review` と `commit` は同じゲート内に置いてよいが、常に同一単位であるとは定義しない。
  - 継承・実装の PlantUML 例では `Child --|> Parent` / `Implementation ..|> Interface` を使い、見た目として矢印が下から上へ向くよう誘導する。
- 未合意 / 未確定のこと:
  - `001` / `002` 例示への補正を、すべての表へ機械的に入れるか、誤解されやすい主要表に絞るか。
  - `XXX` 行を可視例として入れるか、HTML comment による作成者向け指示を基本にするか。
  - 現在の PR に追加 commit として反映するか、PR #248 相当の merge-ready 状態を保ち、別 follow-up issue に分けるか。
- source-grounded に解決できたこと:
  - provider / dogfooding 双方に `001` / `002` の例示が多数残っている。特に profile 別 design / plan と issue requirement / report が対象になる。
  - `standard` / `strict` / `critical` の plan はすでに `マイルストーン計画` と各種 gate を持つため、`commit` は workflow ルール追加ではなく、各 milestone gate の定型項目として自然に追加できる。
  - `lite` plan には軽量チェックリストと最終 lite gate があり、途中 commit を入れない方針と相性がよい。
  - `workflow_issue.md` と `phase_plan_issue.md` には、古い `1 implementation step = 1 review scope = 1 commit` および step commit 前提の completion 文言が残っている。
  - `report.md` には `コミット範囲（commit scope）` の台帳があるため、文言を `step` 固定から `milestone / commit candidate / no-op result` を記録できる表現へ寄せる余地がある。

## 選択肢 / tradeoff (必須)
- Option A:
  - 内容:
    - 現在の PR / issue に追加修正として、テンプレート・docs・tests をまとめて反映する。
  - Pros:
    - ユーザー共有メモの意図を、profile Markdown 化の一連の変更として閉じられる。
    - template と workflow docs の矛盾を残さず、次に使う agent がすぐ新方針に従える。
  - Cons:
    - 既に clean / review 済みの PR に追加差分が入り、CI と review を再度やり直す必要がある。
    - 触るファイルが provider / dogfooding / tests に広がるため、修正粒度を誤ると PR の焦点がぼやける。
- Option B:
  - 内容:
    - この artifact で分析を確定し、follow-up issue として別 PR へ切り出す。
  - Pros:
    - 現 PR の merge-ready 状態を保ちやすい。
    - テンプレート品質改善を専用 issue として、テスト追加まで丁寧に設計できる。
  - Cons:
    - 現 PR を merge した直後の dogfooding では、古い誤誘導が一時的に残る。
    - grade 別テンプレートの利用開始タイミングで、今回の知見を反映し忘れるリスクがある。

- Option C:
  - 内容:
    - 最小差分として、`commit候補` と PlantUML コメントだけを現在 PR に入れ、`001/002` 補正と docs 方針更新は follow-up にする。
  - Pros:
    - 変更量を抑えつつ、特に実行履歴と図の誤誘導を早めに潰せる。
  - Cons:
    - `001/002` の誤読と古い step/review/commit 文言が残り、方針の一貫性が弱い。

## reflection proposal (必須)
- canonical docs / workflow / template / skill guidance へ反映すべき候補:
  - `src/spec_dock/assets/spec_dock/templates/issue/requirement.md`
    - `SC-001` / `SC-002`, `BH-001` / `BH-002`, `AC-001` / `AC-002`, `EC-001` / `EC-002`, `EX-001` / `EX-002`, `CON-001` / `CON-002`, `B-CAND-001`, `TERM-001`, `Q-001` / `Q-002` などに「必要な数だけ追加」の誘導を入れる。
  - `src/spec_dock/assets/spec_dock/templates/issue-profiles/*/design.md`
    - 多数行の trace / decision / evidence / risk table に、2件限定でないことを示す comment または `XXX` 行を入れる。
    - class diagram の section に PlantUML 継承方向コメントと最小例を入れる。
  - `src/spec_dock/assets/spec_dock/templates/issue-profiles/{standard,strict,critical}/plan.md`
    - 主要 milestone gate に共通の `commit` ブロックを追加する。
    - `lite/plan.md` には追加しない。
  - `src/spec_dock/assets/spec_dock/templates/issue/report.md`
    - commit / no-op evidence の記録欄を、固定 step 前提から milestone / commit candidate にも対応できる語彙へ寄せる。
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
    - `1 implementation step = 1 review scope = 1 commit` を標準とする文言を撤去し、`standard` 以上では milestone gate に `commit候補` を置く、review と commit は一致してもよいが常に一致とは定義しない、という方針へ更新する。
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
    - step 中心の authoring checklist / review gate を、grade 別の `milestone / behavior / gate` と `commit候補` に合わせる。
  - `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md`
    - 既存の `implementation step` schema を残す場合でも、profile plan では `milestone` を上位単位、behavior slice / gate を実行単位として扱うことを明記する。
  - dogfooding mirror:
    - `spec-dock/templates/...` と `spec-dock/docs/...` に provider 側反映後の内容を整合させる。
- まだ proposal に留める理由:
  - 現時点では実装差分を入れていない。
  - issue active state は `no-active` であり、canonical artifact の更新ではなく discussion evidence として残している。
  - 現 PR に追加するか follow-up issue に分けるかは、PR の再レビューコストと merge タイミングの判断が必要である。

## adoption target / 採用先候補 (必須)
- `requirement.md`:
  - `templates/issue/requirement.md` に、複数シナリオ・振る舞い・受け入れ条件・制約・未確定事項が任意件数であることを示す指示を追加する。
- `design.md`:
  - profile 別 `design.md` に、複数表の任意行追加指示と PlantUML 継承方向コメントを追加する。
- `plan.md`:
  - profile 別 `plan.md` に、複数表の任意行追加指示を追加する。
  - `standard` / `strict` / `critical` の milestone gate に共通 `commit` ブロックを追加する。
  - `lite` には commit ブロックを追加しない。
- `ADR`:
  - ADR 化は不要。これは実装不可能な長期アーキテクチャ判断ではなく、テンプレート・workflow 文言の整合修正である。
- `report.md` Evidence Adoption Ledger:
  - 採用する場合は、この discussion artifact を `adopted` または `partially_adopted` として記録し、反映先 template / docs / tests を列挙する。

## ADR triage / ADR candidate triage (必須)
- ADR candidate か:
  - no
- hard to reverse:
  - no
- surprising without context:
  - yes
- real tradeoff:
  - yes
- ADR 化しない場合の反映先:
  - `disc`, `templates/issue/*`, `templates/issue-profiles/*`, `docs/workflow_issue.md`, `docs/phase_plan_issue.md`, `docs/authoring/issue-plan.md`, `templates/issue/report.md`

## 推奨案 (必須)
- 推奨案:
  - Option A を基本とし、現在の PR に追加修正として反映する。
- 理由:
  - これは `iss-00247` の中核である profile Markdown template の完成度に直接関わる。
  - `commit候補` と古い step/review/commit 方針の不整合は、テンプレートを使う agent の実行履歴設計を誤らせる可能性がある。
  - `001/002` の任意件数明示と PlantUML 継承方向は、テンプレート品質の小さな補正に見えるが、生成物の構造品質に効く。
- 実装時の粒度:
  - 1 commit で巨大に混ぜるのではなく、少なくとも `template content update`、`workflow/docs alignment`、`tests/update verification` の単位へ分けるのが望ましい。
  - ただし user が PR churn を避けたい場合は、Option B として follow-up issue 化できる。

## 推奨反映先 (必須)
- `requirement.md`:
  - provider: `src/spec_dock/assets/spec_dock/templates/issue/requirement.md`
  - dogfooding: `spec-dock/templates/issue/requirement.md`
- `design.md`:
  - provider: `src/spec_dock/assets/spec_dock/templates/issue-profiles/{lite,standard,strict,critical}/design.md`
  - dogfooding: `spec-dock/templates/issue-profiles/{lite,standard,strict,critical}/design.md`
- `plan.md`:
  - provider: `src/spec_dock/assets/spec_dock/templates/issue-profiles/{lite,standard,strict,critical}/plan.md`
  - dogfooding: `spec-dock/templates/issue-profiles/{lite,standard,strict,critical}/plan.md`
- `ADR`:
  - なし。
- `report.md` Evidence Adoption Ledger:
  - provider: `src/spec_dock/assets/spec_dock/templates/issue/report.md`
  - dogfooding: `spec-dock/templates/issue/report.md`
  - issue-local: `iss-00247/report.md` へ採用結果を記録する場合は、PR 修正時に active / report authority を確認してから行う。

## 未採用 / deferred 理由 (必須)
- 未採用:
  - 現時点ではなし。
- deferred:
  - 実装そのものは、この artifact 作成時点では deferred。ユーザーの今回依頼は「どのような修正を加えるべきかの分析」と `discussions/` への書き出しである。
  - PR へ反映するか follow-up issue に切り出すかは、次アクションで決める。

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - provider 側テンプレートへ以下を実装する。
    - 複数要素テーブル・リストの任意件数追加指示。
    - PlantUML 継承・実装矢印方向コメントと上向き例。
    - `standard` / `strict` / `critical` plan の milestone gate への共通 `commit` ブロック。
    - `lite` plan への commit ブロック不追加確認。
  - provider 側 docs へ以下を実装する。
    - step/review/commit 完全一致を標準化する古い記述の撤去。
    - grade 別の `milestone / behavior / gate` と `commit候補` 中心への更新。
    - `report.md` で review evidence、verification evidence、commit または no-op result を記録する方針の整合。
  - dogfooding 側テンプレート・docs を provider 側と整合させる。
  - 既存テストを更新または追加する。
    - `lite/plan.md` に `commit候補` がないこと。
    - `standard` / `strict` / `critical` plan に共通 `commit候補` と `commit前確認` があること。
    - PlantUML 継承例が `--|>` / `..|>` を正しい方向で示すこと。
    - provider / dogfooding 側の該当テンプレートが同期していること。
    - 古い `1 implementation step = 1 review scope = 1 commit` 文言が残っていないこと。
- 追加で作る discussion docs:
  - 原則不要。
  - ただし PR に入れず follow-up issue にする場合は、この artifact を根拠に新しい issue requirement の draft を作る。

## 実装時の検証候補
- `rg -n "commit候補|commit前確認" src/spec_dock/assets/spec_dock/templates/issue-profiles spec-dock/templates/issue-profiles`
- `rg -n "1 implementation step = 1 review scope = 1 commit|1 implementation step = 1 review|1 review scope = 1 commit" src/spec_dock/assets/spec_dock/docs spec-dock/docs`
- `rg -n "Child --\\|> Parent|Implementation \\.\\.\\|> Interface|継承・実装の矢印" src/spec_dock/assets/spec_dock/templates/issue-profiles spec-dock/templates/issue-profiles`
- `uv run pytest tests/unit tests/cli_runtime` から、変更範囲に応じて最小セットを選ぶ。
- template parity を扱う既存テストがあれば優先し、なければ content contract test を追加する。
