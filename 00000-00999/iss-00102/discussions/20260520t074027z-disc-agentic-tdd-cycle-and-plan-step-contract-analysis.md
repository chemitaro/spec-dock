---
種別: disc
ID: "20260520t074027z-disc"
タイトル: "Agentic TDD cycle and plan step contract analysis"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-05-20"
親: ["iss-00102"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260520t074027z-disc Agentic TDD cycle and plan step contract analysis

## 位置づけ
- 用途: 集まった情報をもとに、論点、評価軸、選択肢、合意点/未合意点を整理する。
- authority default: `proposed`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- 人間から回答を引き出し、回答欄や未回答事項を管理する場合は `interview` を使う。
- 生ログや未整理の思考は `scratch`、事実確認や外部根拠は `research`、長期判断の固定は `adr` に分ける。
- doc が大きくなりすぎたら、質問回答は `interview`、事実調査は `research`、raw capture は `scratch`、長期決定は `adr` へ分割する。

## 議題 (必須)
- spec-dock の Issue 実行 workflow / plan template において、Agentic TDD をどの粒度で表現するかを整理する。
- 現行 `plan.md` template / `phase_plan_issue.md` にある「通常 Issue は step / behavior slice ごとに 1〜3 件程度の検証契約を書く」という記述を見直す。
- 実装前に用意するべきテスト情報を、完全な detailed test inventory ではなく、test obligation / concrete red tests / discovered test ledger の責務分担として定義する。
- `implementation step`、`behavior slice`、Agentic TDD cycle、review gate、commit boundary の関係を決める。

## 背景 (必須)
- 現行 workflow は `Agent-Native TDD` / `Spec-Locked Micro-Batch TDD` を掲げており、`Red -> Green -> Refactor` を捨てる設計ではない。
- 一方、現行 template / playbook は `1〜3 件程度` という件数目安を含んでおり、エージェントがこれを実質的な上限として解釈し、高リスク surface でもテスト設計が薄くなる懸念がある。
- GPT-5.5 / Codex 級のコーディングエージェントは、人間より広い文脈、複数ファイル、複数レイヤの整合を扱える。そのため、人間TDDの極小サイクルを機械的に適用すると、plan / report / review / commit の管理コストが大きくなりすぎる。
- ただし、エージェントは仕様が薄いままでも「それっぽく完成」させやすく、実装後テスト、仕様縮小、過剰実装、巨大 diff、review 不可能な変更を起こしうる。
- したがって、Agentic TDD では「小ささ」そのものではなく、実装前に oracle を固定し、期待どおり red を確認し、green 後に refactor し、証跡を review 可能に残すことが重要である。
- 今回の issue は、`iss-00098 Delegated Implementation Orchestration Contract` の follow-up として、plan step と Agentic TDD cycle の契約を明確化する。

## 選択肢 (必須)
- Option A: 人間TDDと同じく、1 micro behavior / 1 micro test を 1 plan step にする。
  - Pros:
    - red/green の因果関係が非常に小さく見える。
    - 失敗時の切り戻し単位は細かい。
  - Cons:
    - plan / report / review / commit が過度に細分化され、spec-dock workflow の運用コストが上がる。
    - GPT-5.5 / Codex の横断的な設計・実装能力を活かしにくい。
    - private helper や実装都合の分岐まで plan step 化し、テストが内部実装に結合しやすい。
- Option B: 1 issue / feature 全体を 1 Agentic TDD cycle としてまとめる。
  - Pros:
    - エージェントの大きな文脈処理能力を最大限使える。
    - plan の見た目は短くなる。
  - Cons:
    - red evidence が複数の失敗原因を含み、どの契約を通したのかが曖昧になる。
    - review scope と commit scope が大きくなり、revert / rollback が粗くなる。
    - 仕様変更、実装修正、回帰対応、refactor が混ざりやすい。
    - `1 implementation step = 1 review scope = 1 commit` の現行 contract と相性が悪い。
- Option C: 1 implementation step を、原則 1 reviewable behavior slice / contract slice に対応させる。
  - Pros:
    - Agentic TDD の red/green/refactor 証跡を、review / commit / report の単位と揃えられる。
    - 人間TDDより大きいが、issue / feature 全体より小さい粒度でエージェントの強みを活かせる。
    - scope creep、後付けテスト、巨大 diff を抑えやすい。
    - step 内で必要な micro red/green/refactor は複数回まわせるため、実装効率を落としすぎない。
  - Cons:
    - step の切り方に判断が必要。
    - 密結合した小さな behavior を厳密に分けすぎると、人工的な中間状態や plan 肥大化が起きる。
- Option D: 1 step に複数 behavior slices を自由に含める。
  - Pros:
    - docs-only / scaffold sync / 薄い option 追加のような関連作業はまとめやすい。
  - Cons:
    - 自由に許すと、review evidence / red evidence / rollback boundary が混ざる。
    - 「ついでに」の変更が step 内に入りやすい。

## 推奨案 (必須)
- 採用する基本方針:
  - `1 implementation step = 原則 1 reviewable behavior slice = 原則 1 Agentic TDD cycle = 1 review scope = 1 commit` とする。
  - ただし、ここでいう Agentic TDD cycle は人間TDDの micro loop ではなく、1つの観測可能な behavior / contract を成立させるための red/green/refactor 証拠プロトコルである。
  - 1 step の内部には、同じ behavior slice に閉じる限り、複数の Red-Green-Refactor micro cycles を含めてよい。
- `1〜3件程度` の記述:
  - 削除または明確に訂正する。
  - 件数で制御せず、acceptance criteria、changed contract、failure mode、invariant、regression risk を検証できるだけの test obligation を列挙する。
  - 初期 matrix は上限ではなく floor として扱う。
- テスト情報の責務分担:
  - `plan.md` の Issue 全体では `Test Obligation Matrix` を置く。これは要求・リスク・不変条件・失敗系・回帰観点の棚卸しであり、完全なテスト関数一覧ではない。
  - 各 implementation step の開始前には、その behavior slice の concrete Red tests を固定する。入力、期待結果、失敗理由、実行コマンドまたは evidence path まで明記する。
  - 実装中に見つかった追加テストは `discovered tests` として扱う。既存 obligation 内の補強なら report に記録し、新しい仕様・外部挙動・risk class 変更なら plan amendment と re-review を先に行う。
- 複数 behavior slices を 1 step に含める例外:
  - 原則は禁止寄りにし、`bounded bundled slices` として明示的に扱う。
  - 許可条件は、同じ実装面、同じ検証経路、同じ review / rollback boundary に閉じ、slice ごとの red/green evidence を残せる場合に限定する。
  - 独立した failure mode、新しい layer / command surface / persistence contract、別 manual validation、無関係な cleanup が出たら step を分割する。
- Green 判定:
  - targeted tests が通るだけでなく、provider source / dogfooding mirror / generated asset impact / docs impact の扱いを、変更種別に応じて確認する。

## 未決事項 (任意)
- plan template 上の名称:
  - `具体テストケース一覧` を維持して説明を強めるか、`Initial Concrete Red Tests` / `Test Obligation Matrix` などへ段階的に整理するか。
- QA gate の位置:
  - Medium / High risk の Issue で、実装前に `qa-reviewer` による Plan QA Gate を必須化するか。
- strict validation:
  - runtime の `validate` に opt-in `--strict-docs` のような docs lint を追加するか、まずは reviewer / template contract に留めるか。
- evidence naming:
  - `red_gate` / `green_gate` / `sensitivity_gate` / `discovered_tests` を report template に正式欄として追加するか。

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - requirement:
    - 現行の `1〜3件程度` 目安が高リスク領域でテスト不足を誘発する課題を記述する。
    - Agentic TDD でも Red-Green-Refactor を維持し、ただし標準サイクル粒度を reviewable behavior slice / contract slice とする要件を追加する。
    - `Test Obligation Matrix`、step-local concrete Red tests、implementation-time discovered tests、plan amendment rules を受け入れ条件にする。
  - design:
    - provider-side source of truth は `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`、`phase_plan_issue.md`、`docs/authoring/issue-plan.md`、`templates/issue/plan.md`、`templates/issue/report.md` を中心に整理する。
    - dogfooding mirror である `spec-dock/docs/...` / `spec-dock/templates/...` の更新方針を明記する。
    - plan step / behavior slice / Agentic TDD cycle / review gate / commit boundary の関係を図または表で固定する。
  - plan:
    - S01: Agentic TDD policy と `1 step = 1 behavior slice` 原則を workflow / phase docs に反映する。
    - S02: Issue plan template に `Test Obligation Matrix`、step-local concrete Red tests、bounded bundled slices、implementation-time expansion / amendment rules を反映する。
    - S03: report template に red/green evidence、discovered tests、closure delta / plan amendment evidence を記録できる欄を整える。
    - S90/S99: docs impact と QA / code / spec final gate を置く。
  - adr:
    - 今回の判断が長期運用の基本方針になるなら、別途 ADR 化を検討する。
- 追加で作る discussion docs:
  - 必要なら Plan QA Gate の導入可否を別 `disc` または `adr` で切る。
  - strict docs lint / runtime validation は implementation issue 化する前に `research` または `disc` で検討する。
