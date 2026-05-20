---
種別: disc
ID: "20260520t075709z-disc"
タイトル: "Current workflow and plan template remediation analysis"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-05-20"
親: ["iss-00102"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260520t075709z-disc Current workflow and plan template remediation analysis

## 位置づけ
- 用途: 集まった情報をもとに、論点、評価軸、選択肢、合意点/未合意点を整理する。
- authority default: `proposed`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- 人間から回答を引き出し、回答欄や未回答事項を管理する場合は `interview` を使う。
- 生ログや未整理の思考は `scratch`、事実確認や外部根拠は `research`、長期判断の固定は `adr` に分ける。
- doc が大きくなりすぎたら、質問回答は `interview`、事実調査は `research`、raw capture は `scratch`、長期決定は `adr` へ分割する。

## 議題 (必須)
- `iss-00102` で修正すべき、現行の Issue 実行 workflow / plan template / authoring docs / skill / prompt / agent configs の問題点を整理する。
- Agentic TDD の新方針を「どこに何を書くか」へ分解し、追加すべき内容だけでなく、削除・統合・簡素化すべき内容を決める。
- 特に `1〜3件程度` のテスト件数目安を残すか削るかを、現行の進め方の問題点と合わせて判断する。

## 背景 (必須)
- 現行 workflow はすでに `Agent-Native TDD` / `Spec-Locked Micro-Batch TDD` を掲げ、`Spec-Locked Closure Index`、step-local `具体テストケース一覧`、pre-implementation evidence、review gate、commit gate を持っている。
- しかし、これらの契約が `workflow_issue.md`、`phase_plan_issue.md`、`docs/authoring/issue-plan.md`、`templates/issue/plan.md`、`report.md`、`execute-issue.md`、`spec-dock-issue-execution/SKILL.md`、agent configs に少しずつ重複しており、どこが正本かが読みにくい。
- 現行の `1〜3件程度` は `phase_plan_issue.md` と `templates/issue/plan.md` にあり、テスト十分性を件数で誘導する危険がある。
- 一方で、テンプレートや workflow は何度も追記され、すでにかなり重い。単純に Agentic TDD の節を追加すると、さらに重複と drift が増える。
- 今回の修正は「追加」より先に、正本分離、重複削減、テンプレートの薄さ、skill/prompt のルーティング化を行う必要がある。
- 参照した consultant 観点:
  - 高抽象度レビュー: `1〜3件` 削除、risk-calibrated obligation coverage へ置換を推奨。
  - テスト設計レビュー: `1〜3件` を残す場合は「初期 obligation の通常目安」に限定し、上限ではないと明記する案。
  - 文書アーキテクチャレビュー: workflow / authoring / template / report / prompt / skill の所有境界を再固定し、template と skill/prompt を薄くする案。
  - 詳細監査レビュー: 重複節、横長 table、hard cutover の標準 workflow 混入、agent configs の出力契約不足を指摘。

## 選択肢 (必須)
- Option A: 現行構造に Agentic TDD の説明を追加する。
  - Pros:
    - 実装は小さく見える。
    - 現行文書の大きな再編を避けられる。
  - Cons:
    - すでに重複している契約がさらに増える。
    - workflow、phase playbook、authoring docs、template、prompt、skill の drift が悪化する。
    - `1〜3件程度`、`具体テストケース一覧`、`test bundle`、`step closure contract` などの曖昧な関係が残る。
- Option B: `1〜3件程度` を残し、初期 planning heuristic として意味を限定する。
  - Pros:
    - 小さな低リスク step で過剰な test matrix を作る圧を避けられる。
    - 「完全なテスト一覧を plan に置かない」という方針とは両立しやすい。
  - Cons:
    - エージェントは数字へ吸着しやすく、上限・十分条件として読まれる危険が残る。
    - `dev-coder` の “minimal tests” 指示と組み合わさると、薄いテストを正当化しやすい。
    - High-risk surface での不足を QA final gate まで持ち越しやすい。
- Option C: `1〜3件程度` を削除し、risk-calibrated test obligation coverage に置換する。
  - Pros:
    - テスト十分性を件数ではなく、AC / changed contract / failure mode / invariant / regression risk で判断できる。
    - 高リスク領域で必要なケース数を自然に増やせる。
    - 「初期 matrix は floor であり cap ではない」という方針をより明確にできる。
  - Cons:
    - 低リスク step でどの程度書けばよいか、authoring docs 側の説明が必要になる。
    - reviewer が raw 件数ではなく obligation coverage を見る前提を agent configs にも反映する必要がある。
- Option D: workflow/document architecture を再整理したうえで Agentic TDD 方針を配置する。
  - Pros:
    - 長期的な drift を抑えられる。
    - 何を削るか、どこへ移すか、どこが正本かが明確になる。
    - template と prompt/skill を薄く保ち、実 issue docs の可読性を保てる。
  - Cons:
    - 修正範囲が docs/templates/prompts/skills/agent configs/tests に広がる。
    - 一度にやりすぎるとこの issue 自体が大きくなるため、step 分割が必要。

## 推奨案 (必須)
- 採用する方針:
  - Option C + D。
  - `1〜3件程度` は Agentic TDD / issue plan の規範文としては削除する。
  - 代わりに、`risk-calibrated test obligation coverage` を `phase_plan_issue.md` / `authoring/issue-plan.md` に定義する。
  - 低リスク step で少数の obligation で足りることは認めるが、数字を規範にしない。
- 理由:
  - `1〜3件程度` を「初期目安」として残す案も成立するが、エージェントが数字を上限・十分条件として扱うリスクが高い。
  - 今回の問題はテスト数だけではなく、「何を事前固定し、何を実装中に発見・追加し、何を report / amendment に流すか」が不明瞭なことにある。
  - 件数を残すより、`Test Obligation Matrix`、step-local `Concrete Red / Characterization Seeds`、`Discovered Test Ledger`、`Plan Amendment Rules` の責務分担を明確にした方が、Agentic TDD の品質ゲートとして強い。
- あるべき構造:
  - `workflow_issue.md`:
    - Issue lifecycle、execution order、delegation、reviewer gate、commit/no-op、complete/block 判定を所有する。
    - Agentic TDD は execution evidence protocol として短く定義する。
    - 具体テストケースの書式や plan field 詳細は持たない。
  - `docs/authoring/issue-plan.md`:
    - Issue plan の書き方の正本にする。
    - `Test Obligation Matrix`、step-local concrete tests/seeds、docs-only verification、bundled slices、plan amendment rules を所有する。
  - `phase_plan_issue.md`:
    - plan の考え方と review checklist に絞る。
    - field-level の詳細や reviewer fail 条件は `authoring/issue-plan.md` へ寄せる。
  - `templates/issue/plan.md`:
    - 最小 scaffold と copyable S01 例に薄くする。
    - 長い説明、重複 checklist、横長 table の既定列を減らす。
  - `templates/issue/report.md`:
    - 実行後の evidence ledger として、Red/Green evidence、Discovered Tests、Closure Delta、reviewer result、residual risk を記録する。
  - `execute-issue.md` / `spec-dock-issue-execution/SKILL.md`:
    - active docs と正本文書への短い routing に寄せる。
    - policy 詳細や template 書式の重複は避ける。
  - agent configs:
    - `dev-coder`: plan の test obligations / concrete seeds / allowed paths / closure ids を満たす最小十分な実装とテストを返す。
    - `qa-reviewer`: raw 件数ではなく obligation coverage、red/green/sensitivity evidence、missing high-value tests を見る。
    - `spec-reviewer`: issue plan review 時は `authoring/issue-plan.md` を正本として見る。
    - `code-reviewer`: step review 時は allowed paths、forbidden changes、closure ids、verification evidence に照らす。
- 抽象設計上の P0 問題:
  - 正本が多すぎる。複数文書が同じ contract を再定義している。
  - `1〜3件程度` が risk-based test obligation を件数ヒューリスティックへ引き戻している。
  - plan template が「最小 scaffold」ではなく準仕様書化しており、実 issue の可読性を下げる。
  - agent configs が docs の契約を実行する入出力契約に追いついていない。
- 具体的な P1 問題:
  - `Spec-Locked Closure Index`、`test bundle`、`具体テストケース一覧`、`step closure contract`、`Closure Coverage`、`Closure Delta` の用語が多く、役割が近い。
  - `execute-issue.md` の `1 implementation step = 1 code-reviewer scope = 1 commit` は docs-only step と矛盾するため、`review scope` / reviewer mapping に言い換える必要がある。
  - `templates/issue/plan.md` の `ステップ一覧` と `実装ステップ` は二重管理になりやすい。
  - `Spec-Locked Closure Index` の既定 table は横長すぎる。
  - docs-only / no-op の説明が `具体テストケース一覧` に混ざっている。
  - `report draft update before review` はテストケース欄ではなく step gate / report evidence に属する。
  - `workflow_issue.md` の `hard cutover evidence contract` は標準 workflow から optional pattern / reference doc へ分離候補。

## 未決事項 (任意)
- `phase_plan_issue.md` を thin redirect に近づけるか、plan philosophy + review checklist として残すか。
- `具体テストケース一覧` という名称を維持するか、`Step Test Obligations / Concrete Seeds` のような名称へ変更するか。
- `hard cutover evidence contract` の移動先を既存 `reference_deps.md` / `reference_sync.md` にするか、新しい reference doc にするか。
- Plan QA Gate をこの issue で必須化するか、まず agent config / final QA の観点追加に留めるか。
- `validate --strict-docs` のような runtime lint をこの issue の対象外にするか、後続 issue 化するか。

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - requirement:
    - 現行の `1〜3件程度` がテスト不足を誘発する課題を明記する。
    - 正本分離と重複削減を要件に含める。
    - Agentic TDD を、件数ではなく obligation coverage / red-green evidence / discovered tests / amendment rules で運用する受け入れ条件にする。
    - template / prompt / skill を薄くし、agent configs に必要な入出力契約を足すことを含める。
  - design:
    - workflow / authoring / phase playbook / templates / report / prompt / skill / agent configs の所有責務表を作る。
    - plan step / behavior slice / Agentic TDD cycle / review gate / commit boundary の関係を固定する。
    - 削除・統合候補を file-level に落とす。
    - provider source と dogfooding mirror の更新対象を整理する。
  - plan:
    - S01: ownership contract を docs に反映し、`1〜3件程度` を削除・置換する。
    - S02: `authoring/issue-plan.md` を正本化し、Test Obligation Matrix / Concrete Seeds / Discovered Tests / Plan Amendment Rules を整理する。
    - S03: `templates/issue/plan.md` を薄くし、横長 table / 重複 checklist / docs-only 混在を整理する。
    - S04: `report.md` に Red/Green evidence と Discovered Tests ledger を追加する。
    - S05: `execute-issue.md` / skill を薄い routing に寄せ、`code-reviewer scope` の誤表現を直す。
    - S06: dev-coder / qa-reviewer / spec-reviewer / code-reviewer の agent config を step contract 入出力へ合わせる。
    - S07: structural assertions を `tests/test_init_update.py` に追加する。
    - S90/S99: docs impact / final QA / code / spec review。
  - adr:
    - Agentic TDD を長期の workflow 原則として固定するなら ADR 化する。
- 追加で作る discussion docs:
  - Plan QA Gate / strict docs validation / hard cutover reference split は必要に応じて別 discussion へ分離する。
