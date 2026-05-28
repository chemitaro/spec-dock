---
種別: 要件定義書（Issue）
ID: "iss-00134"
タイトル: "Matt Pocock grill-style clarification workflow を spec-dock に取り込む"
関連GitHub: ["#134"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-05-28"
親: ["epic-00067", "init-local-00003"]
derived_from:
  - "discussions/20260528t004419z-research-mattpocock-skills-source-capture.md"
  - "discussions/20260528t010000z-disc-adopt-mattpocock-grill-patterns.md"
  - "discussions/20260528t011700z-research-spec-dock-requirement-grill-skill-design.md"
  - "discussions/20260528t013700z-research-requirement-grill-template-design.md"
  - "discussions/20260528t020135z-interview-grill-scope-and-surfaces.md"
  - "discussions/20260528t021116z-interview-question-sheet-artifact-unit.md"
  - "discussions/20260528t021530z-interview-question-sheet-promotion-lifecycle.md"
  - "discussions/20260528t021838z-interview-question-sheet-external-analysis-evidence.md"
  - "discussions/20260528t023921z-interview-question-sheet-template-artifact-set.md"
  - "discussions/20260528t024729z-interview-question-sheet-common-template-catalog.md"
  - "discussions/20260528t032050z-interview-question-sheet-missing-template-criteria.md"
  - "discussions/20260528t032332z-interview-question-sheet-reflection-record-location.md"
  - "discussions/20260528t032913z-interview-question-sheet-grill-trigger-policy.md"
  - "discussions/20260528t033128z-interview-question-sheet-interview-template-migration.md"
  - "discussions/20260528t033641z-interview-question-sheet-question-artifact-threshold.md"
  - "discussions/20260528t034100z-interview-question-sheet-required-fields.md"
  - "discussions/20260528t034302z-interview-question-sheet-lifecycle-status.md"
  - "discussions/20260528t035117z-disc-deep-consultant-template-workflow-followup.md"
  - "discussions/20260528t040240z-disc-cleanup-and-simplification-requirement.md"
  - "discussions/20260528t041343z-disc-consultant-grill-essence-integration-review.md"
  - "discussions/20260528t041831z-disc-consultant-requirement-update-proposal.md"
---

# iss-00134 Matt Pocock grill-style clarification workflow を spec-dock に取り込む — 要件定義

## 目的

Matt Pocock `grill-me` / `grill-with-docs` の本質である「既存ドキュメントとコードを踏まえ、一問ずつユーザーに確認し、曖昧さを解消して共有理解に到達する」考え方を、spec-dock の要件定義・設計・計画 workflow に適した形で取り込む。

この issue の目的は、直接的な移植や実装を急ぐことではない。
spec-dock において、質問、回答、分析、採用判断を `discussions/` に記録し、それらを積み上げて `requirement.md`、`design.md`、`plan.md`、必要に応じて ADR へ昇華できる clarification workflow の要件を定義することである。

## 背景・現状

- Matt Pocock skills の source snapshot は、issue-local `discussions/mattpocock-skills-source/` に取り込み済みである。
- 既存分析では、`grill-me` / `grill-with-docs` をそのまま import するのではなく、spec-dock-native に変形して採用する方針が妥当と整理されている。
- spec-dock では、root `CONTEXT.md` を新しい正本にするのではなく、active docs、parent docs、issue-local discussions、関連 source/tests/templates を context source とする必要がある。
- ユーザーは、要件定義書・設計書・実装計画書を作成する前段として、憶測や曖昧な理解を残さないための壁打ち workflow を求めている。
- ユーザーは、質問前に未回答の質問シートを作成し、回答後に同じシートを完成させる方式を採用した。

## 対象ユーザー / 利用シナリオ

- 主な利用者:
  - spec-dock を使って issue / epic / initiative の要件、設計、計画を詰める人間ユーザー。
  - ユーザーとの対話を取りまとめる orchestrator。
  - 設計書や計画書を作る専門 agent。

- 代表シナリオ:
  - 要件定義前に、既存 docs / source / discussions を踏まえて曖昧な論点を一つずつ確認する。
  - 複数の質問回答を積み上げ、中間レポートや上位レポートへまとめる。
  - 中間レポートを根拠に、ADR candidate、要件定義書、設計書、計画書へ反映する。
  - issue より小さい局所論点、issue、epic、initiative など、異なる粒度で同じ clarification workflow を使う。
  - canonical docs 作成までは行わず、特定の分析レポートや設計ドラフトを作る目的で workflow を使う。

## スコープ

### 必須

- 一問ずつユーザーに確認する clarification workflow を定義する。
- 質問前に、未回答の質問シートを `discussions/` に作成する。
- 質問シートには、質問の目的、質問内容、回答候補、Codex の分析、Codex の推奨案を含める。PlantUML 図、詳細 tradeoff、後続反映案は、質問の性質に応じて理解を助ける場合に含める。
- PlantUML 図と本文は、日本語話者のユーザーが理解しやすいよう日本語を基本にする。
- ユーザー回答後、同じ質問シートに回答、採用判断、要件への含意を追記して完成させる。
- 原則として、一つの質問につき一つのファイルを作成する。
- 既存の複数質問をまとめて扱う `interview` template / guidance は、一問一答形式の質問シート template へ差し替える。
- agent から人間への質問方式は、一問一答を標準とする。複数の質問をまとめて一括提示することは基本的に行わない。
- 重要判断に関わる質問では、事前に未回答の正式質問シートを作成する。軽微な確認は chat 上の一問一答で扱ってよい。
- 正式質問シートには、判断に必要な構造を必須項目として持たせる。PlantUML 図、詳細 tradeoff、後続反映案は、質問の性質に応じた条件付き項目とする。
- 正式質問シートの lifecycle は、質問状態を表す `status` と、採用状態を表す `adoption_status` と、反映先を表す `reflected_to` を分けて扱う。
- 既存 `research` / `interview` / `disc` / `adr` / `report` は、grill 専用 variant を重複追加するのではなく、共通 template として再設計する。
- 複数の質問シートを参照し、中間レポート / 上位レポートを作成できるようにする。
- 中間レポートを通じて、質問回答を ADR candidate、要件定義書、設計書、計画書へ昇華できるようにする。
- 質問シート、中間レポート、上位レポート、ADR candidate triage など、今回の workflow で必要になる artifact 概念は、まず共通 template catalog 上で表現する。
- 既存の共通 template で表現できない doc type / template が明確に必要な場合だけ、新しい template を追加する。
- 新しい template の追加可否は、独立した lifecycle / status / reflection rule が必要かどうかで判断する。
- `disc.md` は synthesis / 中間レポート / 上位レポート / reflection proposal を扱い、`report.md` は実際の採否と canonical docs への反映結果を evidence ledger として扱う。
- reflection 専用 template は初期要件として追加せず、`disc.md` / `report.md` では責務が衝突すると設計で確認された場合だけ追加を検討する。
- 既存 workflow / template / skill / agent guidance を見直し、今回の方針と矛盾する文言、使われなくなる guidance、重複概念、不要な document / workflow を整理する。
- agent の context を圧迫し、生産性や挙動を悪化させる documentation bloat を避ける。
- main workflow では、最終成果物として `requirement.md`、`design.md`、`plan.md` の作成までを含む。
- skill として利用する場合は、canonical docs 作成を必須にせず、分析レポートや設計ドラフトなどの成果物にも利用できるようにする。
- 一問一答の質問作法は標準とする。一方で、質問前シート、PlantUML、中間レポートまで含む徹底分析 / artifact-heavy grill workflow の起動条件は設計で具体化する。
- ユーザーへの質問は orchestrator が取りまとめ、一度に一つだけ行う。
- 専門 agent は、ユーザーに直接質問せず、質問候補、質問理由、影響する artifact、推奨回答を orchestrator へ渡す。
- 細かい設計判断は deep consultant が一次回答役を担える。deep consultant が判断材料不足、権限不足、人間の価値判断が必要と判断した場合のみ、orchestrator が人間ユーザーへ一問ずつ確認する。

### 禁止

- Matt Pocock skills を無加工で spec-dock に直接移植したものとして扱うこと。
- repo/doc/source を読めば解ける質問を、人間ユーザーに聞くこと。
- unresolved ambiguity を、確定済みの要件・設計・計画として canonical docs に書くこと。
- discussion artifact を、採用判断なしに canonical source of truth として扱うこと。
- 質問をまとめて大量に投げ、ユーザーに一括回答を求めること。
- 新しい workflow / template / skill guidance と矛盾する古い文言や不要 guidance を残したままにすること。
- 似た template や似た workflow を重複して増やし、agent がどれを使うべきか迷う状態にすること。
- 外部ツール固有の操作手順や責務を、spec-dock の要件として定義すること。

### 対象外

- この要件定義時点では、具体的な実装ファイル、CLI command、template file の最終設計は確定しない。
- 外部分析ツール、ブラウザ操作、外部セッション管理、外部出力の取得手順は、この issue の spec-dock 要件では扱わない。
- `CONTEXT.md` を spec-dock の新しい正本として導入することは、この issue の目的ではない。

## 境界

### 常に行う

- 既存の active issue / parent epic / parent initiative docs を確認する。
- issue-local `discussions/` と関連 source / tests / templates を確認する。
- local context で解ける曖昧さは、ユーザーへ質問する前に解く。
- 用語、責務境界、domain relationship が曖昧または既存 docs / source と衝突する場合は、既存表現を照合し、必要に応じて具体シナリオや edge case で境界を明確化する。
- ユーザーに聞く必要がある場合は、質問シートを先に作る。
- 回答後は、回答内容、採用判断、要件への含意を同じ質問シートに記録する。

### 判断が必要

- 軽微な論点を質問シートから直接 canonical docs へ反映するか。
- 複数質問にまたがる大きな判断として、中間レポート / 上位レポートを経由するか。
- ADR candidate として扱うべきか。ADR candidate として扱うのは、原則として、後から戻しにくい、将来の読者にとって意外性がある、実質的な tradeoff がある、の三条件を満たす判断に限る。満たさない判断は、質問シート、`disc.md`、または canonical docs への通常反映に留める。
- requirement / design / plan のどの artifact に反映するか。

### 行わない

- 専門 agent が人間ユーザーへ直接質問すること。
- agent が複数の本質的な質問をまとめて一括提示すること。
- requirement / design / plan / ADR / scope / workflow / template / agent role に影響する重要質問を、証跡なしの chat だけで確定事項として扱うこと。
- 外部ツールの利用方法を spec-dock の構成要素として定義すること。
- 実装に入る前に、未確認の前提を確定事項として扱うこと。

## 非交渉制約

- ユーザー向けの discussion / interview / requirement / design / plan の本文は日本語を基本とする。
- file path、command、identifier、frontmatter key、class 名などの technical token は必要に応じて英語のまま保持する。
- 一度にユーザーへ提示する本質的な質問は一つにする。
- 質問には、Codex の推奨案を添える。
- 質問前のシートには、ユーザーが回答前に判断できるだけの文脈、選択肢、tradeoff を含める。図は、判断の構造や境界を理解しやすくする場合に含める。
- 質問回答 record は、後から追跡できる `discussions/` artifact として保存する。
- canonical docs への反映は、採用判断を通して行う。

## 前提

- `spec-dock/active/issue/requirement.md`、`design.md`、`plan.md` は active issue の canonical docs として扱う。
- `discussions/` は canonical docs 作成前の evidence / research / interview / discussion layer として扱う。
- 要件定義書は orchestrator がユーザーとの discussion を通じて作成する。
- 設計書と計画書は、必要に応じて専門 agent が高度な分析を行って作成する。
- 専門 agent が見つけた追加質問は、orchestrator が取りまとめてユーザーに確認する。

## 受け入れ条件

- AC-001: source-grounded clarification
  - アクター: orchestrator
  - 前提: issue / epic / initiative の要件、設計、計画に曖昧さがある。
  - 操作: active docs、parent docs、`discussions/`、関連 source / tests / templates を確認する。用語の衝突、曖昧語、責務境界の不一致がある場合は、具体シナリオや edge case を使って確認する。
  - 期待結果: local context で解決できる疑問はユーザーへ質問せず、未解決の高影響な曖昧さだけを質問候補にする。
  - 観測点: source-grounding research、質問シート、または中間レポートに根拠が記録されている。

- AC-002: one-question-at-a-time
  - アクター: orchestrator
  - 前提: ユーザー確認が必要な質問候補が複数ある。
  - 操作: 優先順位を判断し、次に答えるべき質問を一つ選ぶ。
  - 期待結果: ユーザーには一度に一つの本質的な質問だけが提示される。
  - 観測点: 質問シート単位で質問と回答が分離されている。

- AC-003: unanswered question sheet
  - アクター: orchestrator
  - 前提: 重要判断に関わる質問をユーザーへ確認する必要がある。
  - 操作: 回答前に `discussions/` へ質問シートを作成する。
  - 期待結果: 質問シートには、目的、質問、回答候補、分析、推奨案、回答欄、採用判断欄、要件 / 設計 / 計画への含意が含まれる。PlantUML 図や詳細 tradeoff は、理解を助ける場合に条件付きで含まれる。
  - 観測点: `status: unanswered`、`authority: proposed`、`adoption_status: unreviewed` の interview artifact が存在する。

- AC-004: answered question completion
  - アクター: orchestrator
  - 前提: ユーザーが質問に回答した。
  - 操作: 同じ質問シートにユーザー回答、採用判断、要件への含意を追記する。
  - 期待結果: 質問シートが回答済み record として完成する。
  - 観測点: `status: answered`、`authority: user-approved`、採用判断に応じた `adoption_status`、回答内容が同じ artifact に記録されている。

- AC-005: artifact unit and synthesis
  - アクター: orchestrator
  - 前提: 複数の質問が同じ上位概念に関わる。
  - 操作: 原則一問一ファイルで質問シートを作成し、必要に応じて複数シートを束ねた中間レポートを作る。
  - 期待結果: 個別質問の追跡性と、上位概念の分析を両立できる。
  - 観測点: 中間レポートが `derived_from` で複数質問シートを参照できる。

- AC-006: promotion lifecycle
  - アクター: orchestrator / 専門 agent
  - 前提: 質問回答 record が十分に積み上がっている。
  - 操作: 軽微な論点は直接 canonical docs へ反映し、大きな判断は中間レポート / 上位レポートを経由する。
  - 期待結果: ADR candidate、requirement、design、plan への反映経路が追跡できる。ADR candidate は原則として、後から戻しにくい、将来の読者にとって意外性がある、実質的な tradeoff がある判断に絞られる。
  - 観測点: canonical docs または中間レポートに採用判断と根拠 artifact が残る。

- AC-007: role boundary
  - アクター: 専門 agent / orchestrator
  - 前提: 専門 agent が設計または計画の分析中にユーザー確認が必要な曖昧さを見つける。
  - 操作: 専門 agent は質問候補をまとめ、orchestrator に返す。
  - 期待結果: 人間ユーザーへの質問は orchestrator が取りまとめ、一問ずつ行う。
  - 観測点: 専門 agent の output に質問候補、理由、影響 artifact、推奨回答が含まれる。

- AC-008: canonical authoring mode
  - アクター: orchestrator / 専門 agent
  - 前提: main workflow として要件定義、設計、計画を作成する。
  - 操作: interview / research / discussion record を積み上げ、必要に応じて中間レポートを作成し、canonical docs へ反映する。
  - 期待結果: `requirement.md`、`design.md`、`plan.md` が、曖昧な推測ではなく記録済みの理解に基づいて作成される。
  - 観測点: canonical docs の内容が `discussions/` の根拠 artifact へ遡れる。

- AC-009: clarification / analysis mode
  - アクター: orchestrator
  - 前提: canonical docs 作成までは目的としないが、特定の論点を深掘りしたい。
  - 操作: 同じ質問シート / record / synthesis の仕組みで、分析レポートや draft を作成する。
  - 期待結果: canonical docs 作成を必須にせず、完全な理解に近づくための skill として利用できる。
  - 観測点: output artifact が目的に応じて analysis report、draft、decision record などになる。

- AC-010: cleanup and simplification
  - アクター: orchestrator / 専門 agent
  - 前提: workflow、template、skill、agent guidance を変更する。
  - 操作: 既存 docs / templates / guidance を見直し、矛盾、重複、不要文言、使われなくなる workflow を整理する。
  - 期待結果: 新しい方針と古い guidance が併存して agent を迷わせる状態を避ける。
  - 観測点: design / plan に cleanup 対象と維持する legacy artifact の扱いが明記され、不要な重複 template や不要 guidance が残っていない。

## 例外・エッジケース

- EC-001: 質問が local context で解ける
  - 条件: active docs、parent docs、source、tests、既存 discussions で答えが確認できる。
  - 期待: ユーザーに質問せず、確認結果を research / discussion artifact に記録する。
  - 観測点: 人間への質問ではなく source-grounding record が作られる。

- EC-002: 回答が別の未確認事項を生む
  - 条件: ユーザー回答により新しい高影響な曖昧さが見つかる。
  - 期待: ただちに複数質問を投げず、次の未回答質問シートを作成して一つずつ確認する。
  - 観測点: 新しい `interview-*` artifact が作成される。

- EC-003: 大きな判断が複数質問にまたがる
  - 条件: 複数の質問シートを読まないと意思決定できない。
  - 期待: 中間レポート / 上位レポートを作成し、選択肢、tradeoff、採用判断、反映先を整理する。
  - 観測点: `disc.md` を使った synthesis / 中間レポート / 上位レポート artifact が複数質問シートを `derived_from` として参照する。ここでいう report は issue の `report.md` evidence ledger ではない。

- EC-004: 専門 agent が追加確認を必要とする
  - 条件: 設計書または計画書の作成中に、専門 agent がユーザー判断を必要とする。
  - 期待: 専門 agent は直接質問せず、orchestrator が質問シートを作ってユーザーへ確認する。
  - 観測点: 専門 agent output と orchestrator の質問シートが分離されている。

- EC-005: 外部支援による artifact が存在する
  - 条件: ユーザー指示により、外部支援を使って分析 artifact が作られている。
  - 期待: spec-dock は外部ツール固有の操作を定義せず、作成済み artifact を通常の evidence として扱う。
  - 観測点: canonical docs への反映時に、artifact と採用判断が追跡できる。

## 入力→出力例

- EX-001: 要件定義前の確認
  - 入力: active issue docs が template に近く、ユーザーが「要件定義書を作る前に壁打ちしたい」と依頼する。
  - 出力: 未回答質問シート、回答済み質問シート、中間レポート、要件定義書。

- EX-002: 設計 agent からの追加確認
  - 入力: 専門 agent が design draft 作成中に、責務境界の曖昧さを検出する。
  - 出力: 専門 agent の質問候補 record、orchestrator が整形した未回答質問シート、回答済み質問シート、design 反映候補。

## 用語

- TERM-001: clarification workflow
  - 既存 docs / source / discussions を踏まえ、未解決の曖昧さを一つずつユーザーに確認して共有理解へ近づける workflow。

- TERM-002: 質問シート
  - 質問前に作成する `discussions/` artifact。目的、選択肢、分析、推奨案、必要に応じた図、回答欄、採用判断欄を持ち、回答後に同じ file が完成 record になる。

- TERM-003: 中間レポート / 上位レポート
  - 複数の質問シートや research / discussion artifact を束ね、上位概念の分析、意思決定、ADR candidate、canonical docs 反映候補を整理する artifact。

- TERM-004: canonical docs
  - active scope の `requirement.md`、`design.md`、`plan.md`。discussion artifact は、採用判断を経て反映されるまでは canonical ではない。

- TERM-005: orchestrator
  - 人間ユーザーとの対話を取りまとめ、質問シートを作成し、一問ずつ確認し、採用判断と canonical docs への反映を管理する役割。

- TERM-006: 専門 agent
  - 設計、計画、ADR などの専門分析を担当する agent。人間ユーザーには直接質問せず、質問候補を orchestrator に返す。

## 設計で具体化する事項

- shipped skill としての名称、配置、呼び出し方。
- 一問一答形式の質問シート template の具体的な構造、frontmatter、provider-side path。
- 既存の複数質問型 `interview` template / guidance を、一問一答形式へ差し替える具体的な migration 方針。
- `research` / `interview` / `disc` / `adr` / `report` を共通 template として再設計する具体的な section / frontmatter。
- 中間レポート template の種類と frontmatter。
- 上位レポート、ADR candidate triage、canonical docs reflection report など、新しく追加する artifact 概念の粒度と template。
- 不足 template を追加する場合の lifecycle / status / reflection rule。
- `disc.md` に置く reflection proposal と、`report.md` に置く observed adoption ledger の境界。
- canonical docs への `derived_from` / `reflected_to` 更新規則。
- ADR candidate triage の詳細条件。
- 用語 sharpening、責務境界、domain relationship、具体シナリオ / edge case を質問設計や research template にどう表現するか。
- 既存 skill / agent との責務重複の整理。
- 標準の一問一答質問と、質問シート / PlantUML / 中間レポートまで含む artifact-heavy workflow の境界。
- 正式質問シートが必須になる重要質問の判定基準と、軽微な確認の扱い。
- 正式質問シートの必須 frontmatter、本文 section、条件付き項目。
- 正式質問シートの `status` / `authority` / `adoption_status` / `reflected_to` の状態遷移。
- deep consultant が回答できる質問と、人間確認へ戻す質問の判定基準。
- 既存 workflow / template / skill / agent guidance の cleanup 対象と、残す legacy artifact / grandfathered artifact の扱い。
- agent の context 圧迫や誤作動につながる重複文言、不要 document、不要 workflow の削減方針。

## 未確定事項

現時点で、要件定義書作成を妨げる未確認事項はない。

上記の「設計で具体化する事項」は、要件の未確定事項ではなく、次工程の design / plan で決定する事項として扱う。

deep consultant による追加確認でも、人間に追加確認しないと requirement を進められない論点は残っていないと判断された。
