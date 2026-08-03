---
種別: interview
ID: "20260803t023549z-interview"
タイトル: "iss-00354 フェーズ別の本文と添付資料の契約"
状態: "draft | answered | archived"
作成者: "iwasawayuuta"
最終更新: "2026-08-03"
親: ["iss-00354"]
関連: []
scope: "<initiative | epic | issue | local-topic>"
scope_id: "iss-00354"
created_at: "2026-08-03THH:MM:SSZ"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from: []
reflected_to: []
---

# 20260803t023549z-interview iss-00354 フェーズ別の本文と添付資料の契約

## 位置づけ
- 用途: 重要判断に関わる一つの質問を、回答前の source-grounded 正式質問シートとして作成し、回答後に同じ artifact を完成 record にする。
- authority default: `proposed`。ユーザー回答と採用判断を反映した後は、必要に応じて `user-approved` または `synthesized` に更新する。
- この artifact は answer capture / adoption target / reflection の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 技術的に調べられることは先に docs / code / tests / ADR / artifacts / primary source を確認する。
- 一つの `interview` artifact には one essential question / 一つの本質的な質問だけを書く。回答によって新しい高影響な曖昧さが見つかった場合は、追加質問をこの file に増やさず、次の unanswered `interview` を作成する。
- trivial な yes/no は、重要な判断、後続反映、回答証跡が必要なら `interview` を使い、そうでなければ issue comment や `blank` で足りる。
- 回答から複数質問の synthesis が必要になったら `disc`、追加調査が必要になったら `research`、長期判断が固まったら `adr` を新規作成する。

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - 本文に置く最小の目的・identity・制約と、phaseごとの必須添付・任意添付・添付不足時の停止条件。
  - `design.md`:
    - 共通context envelope、phase-specific attachment manifest、requiredness／classification／SHA、本文と添付の authority boundary。
  - `plan.md`:
    - prompt synthesis、transport、validator、Oracle adapter、negative testをどの入力契約から更新するか。
  - `ADR`:
    - Initiative／Epicを越えて再利用する入力契約や添付分類の長期標準になった場合だけ候補化する。
- chat 上の軽微な一問では足りない理由:
  - 本文と添付の境界を誤ると、入力欄の長さ制限、必須資料の欠落、Candidate／Review identity混同、秘匿情報の過剰送信を同時に引き起こすため。

## 質問の目的 (必須)
- 対象者:
  - Issue owner（ユーザー）。
- 何を明確にする質問か:
  - Clarification／Planning／Formal Review／Semantic Revisionの各phaseで、チャット本文に置く情報と、添付ファイルとして必ず渡す情報の基本方針。
- 回答が後続判断へ与える影響:
  - context envelopeの共通schema、phaseごとのattachment matrix、添付不足・重複・SHA不一致時のfail-closed判定、プロンプト長の上限管理が決まる。

## 質問 (必須)
- pressure-test question:
  - 「本文は短い目的と契約、詳細は添付」というユーザーの意図を保ちつつ、phaseごとの必須証跡を落とさず、過剰添付によるidentity混同を防げるかを確認する。
- 質問:
  - ChatGPTへ渡す情報の本文／添付の分担について、どの契約を採用しますか？
- 回答してほしいこと:
  - **Option A（推奨）**: 全phaseで短い共通context envelope（goal、role、operation_id、repository／branch／source HEAD、scope、thread mode、authority／mutation制約、output contract）だけを本文に置く。詳細はphase別manifestで必須添付として渡し、欠落・重複・SHA不一致ならfail-closedにする。Clarificationはresearch／interviewと関連source、Planningはcanonical三文書・親scope・relevant source／tests、Formal Reviewは対象Candidate ZIPとidentity／checksum、Semantic Revisionは直前Candidate・正式Review結果・保持前提を添付する。
  - **Option B**: phaseごとの詳細な指示・設計判断も本文へ記載し、添付は補足資料として任意扱いにする。送信は簡単だが、入力欄の肥大化と必須資料欠落を許す。
  - **Option C**: 全phaseで同じ完全bundle（canonical docs、source、Candidate／Reviewを含む）を添付する。契約は単純だが、不要な資料の過剰送信、Candidate／Reviewのidentity混同、添付上限超過を招く。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / artifacts / primary source:
  - Issue #354調査artifact、親Epicのrequirement／design／plan、`issue_planning_prompt.py`、`issue_planning.py`、`issue_planning_chatgpt.py`、planner／reviewer／revision／transport resource、`workflow_chatgpt_authoring_pack.md`、`chatgpt-pack.md`、focused tests。
- local context で解決できたこと:
  - 現行promptはgoal／identity／output contractを本文へ合成し、canonical三文書とrelevant sourceを添付する。Review／RevisionはCandidate／Review identityをexact attachmentとして扱い、personal `chatgpt-use` wrapperはruntime dependencyではない。
- まだ人間判断が必要な理由:
  - 現行schemaは`relevant_source_paths`等に限定され、phaseごとの添付requiredness、本文の最小共通項目、添付不足時の扱いはIssue #354で新たに定義する必要があるため。

## 回答案 (必須)
- Option A:
  - 本文は短い共通envelope、詳細はphase-specific required attachments。添付manifestを検証し、必須資料が不足したら送信しない。
- Option B:
  - 詳細を本文へ集約し、添付は任意補足。実装は単純だが長文化と欠落検知が弱い。
- Option C:
  - 全資料を全phaseで添付。指定は単純だが過剰送信とidentity混同が起きやすい。

## Codex の分析 (必須)
- 判断軸:
  - ユーザーの入力欄制限、再現可能な添付契約、exact identity、Blue／Red分離、秘匿情報最小化、ZIP／JSON出力契約、既存prompt／transportとの後方互換。
- tradeoff:
  - Aは本文を短く保ちながら必須資料を機械検証できる。Bは実装変更が小さいが情報欠落を検出しにくい。Cはphase判定が単純でも不要な資料と古いidentityを毎回持ち込む。
- リスク:
  - phase-specific requirednessが曖昧だと、Formal ReviewへBlue文脈を混ぜる、Revisionへ別Candidateを添付する、添付失敗時に本文だけで続行するなどの事故が起きる。
- 具体シナリオ / edge case:
  - Formal ReviewでCandidate ZIPのfilename／SHA／Candidate IDがmanifestと一致しない場合は送信しない。
  - Semantic Revisionで正式Review JSONが欠落した場合は、レビューなしの修正を開始しない。
  - Clarificationで未確定事項を本文へ詰め込まず、interview／research artifactを添付し、質問だけを本文で明示する。
  - source HEAD更新後は古いsource添付を再利用せず、manifestを再生成する。

## Codex の推奨案 (必須)
- 推奨:
  - Option A。共通envelopeとphase-specific attachment matrixを分離し、必須添付の欠落・重複・SHA不一致をfail-closedで検出する。
- 理由:
  - ユーザーが求める「目的は本文、詳細は添付」のバランスを守り、現行のexact branch／HEAD、Candidate／Review、ZIP／JSON契約を機械的に検証できる最小の拡張だから。
- 未回答時の影響:
  - ChatGPT入力契約を確定できず、canonical三文書のauthoringとprompt／transport実装計画を開始できない。

## ユーザー回答 (回答後に必須)
- answer capture:
  - 原文要旨: 「オプションAを採用します。チャットの文字数・コンテキストが溢れないようにし、合成メッセージと各作業手順を一枚のMarkdownファイルとして保守しやすくする。本文にはゴールと最低限必要な情報を置き、詳細と出力テンプレートは別ファイルに切り出す。」
- 回答:
  - Option Aを採用する。本文はタスクのコアとなるゴールと最低限の入力・identity・制約に限定し、詳細な作業手順、レビュー観点、リビジョン規則、出力テンプレート（例: JSON形式）はphase別の添付Markdownへ分離する。要件定義書・設計書・実装計画書の本文テンプレートは過度に固定せず、ChatGPTの能力を活用する。
- 回答日時:
  - 2026-08-03（Codex会話上の回答時刻）

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes。出力テンプレートをphase別にどの範囲で必須化し、ZIP／JSONなどの形式をどのauthorityで固定するかを別の一問で確認する。
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - 出力形式・テンプレートの添付契約（Planning／RevisionのZIP、Formal Reviewのclosed JSON、Clarificationの回答・artifact形式）。

## 採用判断 (回答後に必須)
- adoption_status:
  - `adopted`（ユーザーがOption Aと追加方針を明示承認）。
- adoption target:
  - Issue #354の`requirement.md`、`design.md`、`plan.md`、phase別prompt／attachment resource、および`report.md`のEvidence Adoption Ledger（canonical authoring時に反映）。
- 採用 / 棄却 / deferred の理由:
  - ユーザーがOption Aを採用し、本文のコンテキスト肥大化を抑えながら、詳細手順と出力テンプレートを一枚のMarkdown添付として保守する方針を明示した。ChatGPT advisoryも、短い共通envelopeとphase別必須添付manifestを推奨している。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - 本文は最低限のゴール・入力・identity・制約、詳細は添付ファイルという入力契約と、コンテキスト上限を超えないことを要件化する。
- `design.md`:
  - 共通context envelope、phase別手順Markdown、出力template Markdown、attachment manifestのauthorityとversionを分離して設計する。
- `plan.md`:
  - まずphase別入力・出力template resourceを整理し、その後prompt synthesis／transport／validator／testsへ反映する。canonical三文書の内容テンプレートは必要最小限に留める。
- `ADR`:
  - 複数Issue／Epicで再利用する長期的なprompt／attachment template標準へ昇格する場合のみ候補化する。現時点ではIssue-local方針として扱う。
- reflected_to 更新方針:
  - canonical authoring時に、回答artifactとChatGPT分析artifactをEvidence Adoption Ledgerへ紐付け、phase別resourceの採用先を記録する。
- adoption reflection:
  - canonical三文書未作成のため`reflected_to: []`を維持する。

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
- 追加で作る artifacts:
  - ...
