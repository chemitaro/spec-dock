---
種別: interview
ID: "20260803t024349z-interview"
タイトル: "iss-00354 出力形式とテンプレートの添付契約"
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

# 20260803t024349z-interview iss-00354 出力形式とテンプレートの添付契約

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
    - phaseごとの出力形式、テンプレート添付の必須性、形式不一致・余分なファイル・ZIP／JSON破損時の受理条件。
  - `design.md`:
    - output contract resourceのversion、本文からの参照、ZIP／JSON validator、保存するartifact identityとbyte／SHA検証。
  - `plan.md`:
    - 既存planner／reviewer／revision／transport resourceの整理、出力templateの添付化、negative test、provider／dogfood parityの実装順。
  - `ADR`:
    - 複数scopeで長期再利用する出力形式標準へ昇格する場合だけ候補化する。
- chat 上の軽微な一問では足りない理由:
  - 出力形式を曖昧にすると、ChatGPTの本文回答が長大化し、複数ファイル・ZIP・closed JSONを確実に取得できず、後続の検証・採用境界が崩れるため。

## 質問の目的 (必須)
- 対象者:
  - Issue owner（ユーザー）。
- 何を明確にする質問か:
  - 出力テンプレートを本文ではなくphase別の添付Markdownとして提供し、どのphaseでどの形式を必須受理条件にするか。
- 回答が後続判断へ与える影響:
  - Planner／RevisionのZIP契約、Formal Reviewのclosed JSON契約、Clarificationの回答・artifact保存方法、template versionとvalidatorの責務が決まる。

## 質問 (必須)
- pressure-test question:
  - 「本文はゴール、テンプレートは添付」という方針を、出力形式の厳密さと要件・設計・計画本文の柔軟性を両立したまま実装できるかを確認する。
- 質問:
  - ChatGPTへの出力形式・テンプレートは、どの契約で運用しますか？
- 回答してほしいこと:
  - **Option A（推奨）**: phaseごとにversionedなoutput-contract Markdownを必須添付し、本文ではゴールと「このtemplateに従う」ことだけを指示する。Planning／Semantic Revisionは仕様書一式と必要なonboarding companionを含む一つのZIP、Formal Reviewは許可フィールドだけのclosed JSON、Clarificationは短い回答をCodexがinterview／research artifactへ保存する。要件定義書・設計書・実装計画書の章構成はtemplateで過剰固定しない。
  - **Option B**: 出力テンプレート全文を本文へ埋め込み、添付は補足にする。形式は固定しやすいが、本文長と保守負荷が増える。
  - **Option C**: 出力形式をChatGPTに任せ、受信後にCodex側で可能な範囲を変換・検証する。柔軟だが、複数ファイル・ZIP・closed JSONを安定して得られない。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / artifacts / primary source:
  - Issue #354調査artifact、親Epicのauthoring protocol、`issue_planning_prompt.py`、`issue_planning.py`、`issue_planning_chatgpt.py`、planner／reviewer／revision／transport resource、`workflow_chatgpt_authoring_pack.md`、focused transport／validator tests。
- local context で解決できたこと:
  - 現行planner／semantic revisionは仕様書三文書とonboarding companionを含む一つのauthoring ZIP、reviewerは`reviewed_identity`／`verdict`／`findings`等のclosed JSONを期待する。template／transport resourceはproviderのprompt synthesisへ合成され、personal wrapperはruntime dependencyではない。
- まだ人間判断が必要な理由:
  - ユーザーが望む「templateは添付、本文はゴール」の運用を、既存のZIP／JSON契約へどこまで厳密に適用し、canonical三文書の自由度をどの程度残すかは人間判断が必要なため。

## 回答案 (必須)
- Option A:
  - templateはversioned Markdown添付、本文は参照だけ。ZIP／closed JSONは厳密に受理し、canonical三文書の内容は過剰固定しない。
- Option B:
  - template全文を本文へ埋め込む。保守と本文長に不利。
- Option C:
  - 出力形式をモデル任せにし、後処理で吸収する。再現性と完全性に不利。

## Codex の分析 (必須)
- 判断軸:
  - ChatGPT入力欄の上限、ファイル形式の再現性、既存ZIP／JSON contract、templateの変更追跡、canonical docsの柔軟性、validatorのfail-closed、将来のprovider／dogfood parity。
- tradeoff:
  - Aは本文を短く保ちつつ形式を検証できる。Bは明示的だが本文が肥大化し、phaseごとの重複・driftが増える。Cは自由だが受信後の変換で情報欠落や誤受理が起きる。
- リスク:
  - template versionの記録がない、ZIP内rootやfilenameが変わる、JSONに許可外フィールドが混ざる、Clarification回答をcanonical authorityとして誤採用する危険がある。
- 具体シナリオ / edge case:
  - Plannerが三文書を本文に貼り付けて回答し、ZIPを返さない場合は受理しない。
  - Reviewerが対象Candidateと異なるidentityをJSONで返した場合は保存してもPASS扱いにしない。
  - Template更新時に古いthreadが旧versionを参照していたら、manifest／template SHAを再検証する。
  - Clarificationの回答はinterview artifactへ記録し、ユーザー承認前にcanonical三文書へ自動反映しない。

## Codex の推奨案 (必須)
- 推奨:
  - Option A。output-contract Markdownをphase別の必須添付とし、本文はゴール・identity・制約・template参照に限定する。
- 理由:
  - ユーザーのコンテキスト節約とメンテナンス性の期待を満たしつつ、既存のZIP／closed JSONの機械検証とcanonical authority boundaryを維持できるため。
- 未回答時の影響:
  - ChatGPTの出力受理条件、template version、validatorの責務が確定せず、canonical三文書のauthoringへ進めない。

## ユーザー回答 (回答後に必須)
- answer capture:
  - 原文: 「オプションAを採用します。」
- 回答:
  - Option Aを採用する。phaseごとの詳細手順と出力形式はversionedなMarkdown添付へ集約し、本文はゴール・最低限の入力・identity・制約・template参照に限定する。Planning／Semantic Revisionは仕様書一式を含む一つのZIP、Formal Reviewはclosed JSON、ClarificationはCodexがinterview／research artifactへ捕捉する。要件定義書・設計書・実装計画書の内容テンプレートは過剰固定しない。
- 回答日時:
  - 2026-08-03（Codex会話上の回答時刻）

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes。「その他のChatGPT利用」へ共通契約をどこまで適用するかを別の一問で確認する。
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - Issue Planningの4 phase以外のChatGPT利用（Clarification、実装ブリーフ、オンボーディング資料、将来のgeneral role等）への適用範囲。

## 採用判断 (回答後に必須)
- adoption_status:
  - `adopted`（ユーザーがOption Aを明示承認）。
- adoption target:
  - Issue #354の`requirement.md`、`design.md`、`plan.md`、phase別output-contract resource、`report.md`のEvidence Adoption Ledger（canonical authoring時に反映）。
- 採用 / 棄却 / deferred の理由:
  - ユーザーがOption Aを採用し、コンテキスト節約・手順の保守性・形式検証を同時に満たす方針を明示した。ChatGPT advisoryも、container／inventory／closed fieldsを強制し、文書の意味内容は過剰固定しない案を推奨している。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - phase別output contractを必須添付とし、本文の短いゴール／identity／制約と、ZIP／closed JSONの受理形式を要件化する。
- `design.md`:
  - contract ID／version／SHA、本文・manifest・validatorのbinding、output kind／inventory／closed fieldsの分離を設計する。
- `plan.md`:
  - output-contract resourceの整理、prompt／transport／validatorの更新、形式不一致のnegative test、provider／dogfood parityの順で計画する。
- `ADR`:
  - 複数scopeで長期再利用する出力形式標準へ昇格する場合のみ候補化する。現時点ではIssue-local方針として扱う。
- reflected_to 更新方針:
  - canonical authoring時に回答artifactとChatGPT分析artifactをEvidence Adoption Ledgerへ結び付ける。
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
