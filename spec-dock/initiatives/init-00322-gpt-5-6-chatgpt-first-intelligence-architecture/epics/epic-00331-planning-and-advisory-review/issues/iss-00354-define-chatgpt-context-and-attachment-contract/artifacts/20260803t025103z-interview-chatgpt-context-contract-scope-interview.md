---
種別: interview
ID: "20260803t025103z-interview"
タイトル: "iss-00354 共通ChatGPT入力契約の適用範囲"
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
adoption_status: "partially_adopted"
derived_from: []
reflected_to: []
---

# 20260803t025103z-interview iss-00354 共通ChatGPT入力契約の適用範囲

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
    - 共通context／attachment／output contractを適用するChatGPT operationの範囲と、対象外にするoperator-only利用の境界。
  - `design.md`:
    - role／phase profileの登録、共通envelopeとphase-specific拡張、未登録operationの拒否または暫定扱い。
  - `plan.md`:
    - Planning／Review／RevisionからClarification・実装ブリーフ・オンボーディング等へ広げる順序、scope creepを防ぐ移行単位とテスト。
  - `ADR`:
    - Initiative／Epicを越えて全ChatGPT operationに適用する恒久ポリシーへ昇格する場合のみ候補化する。
- chat 上の軽微な一問では足りない理由:
  - 範囲を広げすぎるとIssue #354がアーキテクチャ全体や個人wrapperの再設計へ肥大化し、狭すぎると「その他のChatGPT利用」がphase外の無契約運用として残るため。

## 質問の目的 (必須)
- 対象者:
  - Issue owner（ユーザー）。
- 何を明確にする質問か:
  - Issue #354で定義する共通入力・添付・出力契約を、既存4 phase以外のChatGPT利用へどこまで適用するか。
- 回答が後続判断へ与える影響:
  - operation profile一覧、実装対象と後続Issueへの切り出し、未登録roleの扱い、共通validatorの適用範囲が決まる。

## 質問 (必須)
- pressure-test question:
  - Planning／Review／Revisionの契約を再利用可能な共通基盤にしつつ、Issue #354の実装範囲を過剰に広げず、Clarificationや将来roleの抜け漏れを防げるか確認する。
- 質問:
  - 共通ChatGPT入力・添付・出力契約を、どの範囲のoperationへ適用しますか？
- 回答してほしいこと:
  - **Option A（推奨）**: product-ownedの全ChatGPT operationに共通envelope／manifest／output-contractの基盤を適用する。今回のIssueではPlanning／Formal Review／Semantic Revision／Clarificationのprofileを具体化し、実装ブリーフ・オンボーディング・将来のgeneral roleは同じprofile登録方式で後続Issueへ展開する。個人のChatGPT-Use wrapperや自由なoperator相談はruntime contractの対象外とする。
  - **Option B**: 今回はPlanning／Formal Review／Semantic Revisionだけに限定し、Clarificationやその他のoperationは後続Issueで別設計する。Issueは小さくなるが、Clarificationの入力契約が未統一になる。
  - **Option C**: ChatGPTに関するすべての利用（個人wrapper、operatorの自由相談、将来roleを含む）を今回一括で共通契約化する。網羅性は高いが、scopeと実装量が過大になる。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / artifacts / primary source:
  - Issue #354 body、親Epic／Initiative docs、前四つのinterview／ChatGPT advisory artifacts、`issue_planning_prompt.py`、`issue_planning.py`、`issue_planning_chatgpt.py`、planner／reviewer／revision／transport resource、`spec-dock-chatgpt-authoring` skill。
- local context で解決できたこと:
  - product runtimeはprovider-owned direct Oracleを使い、personal `chatgpt-use` wrapperには依存しない。現行Issue Planningにはplanner／reviewer／semantic revisionのroleがあり、Clarificationは別skillで一問ずつartifactを保存する。Issue #354 bodyは「その他のChatGPT利用」も対象に含めるが、PR #351の実装ロジック再設計は対象外としている。
- まだ人間判断が必要な理由:
  - 「その他」の意味がClarification・実装ブリーフ等のproduct-owned operationを指すのか、operatorの自由相談まで含むのかは、Issue bodyとコードだけでは一意に決まらないため。

## 回答案 (必須)
- Option A:
  - 共通基盤は全product-owned operationへ適用し、今回のIssueで主要profileを具体化。個人wrapper／自由相談は対象外、未対応profileは後続Issueへ切り出す。
- Option B:
  - 今回はPlanning／Review／Revisionだけ。Clarification等は後続Issueで扱う。
- Option C:
  - 個人wrapperや自由相談まで含め、すべてを今回一括で契約化する。

## Codex の分析 (必須)
- 判断軸:
  - Issue bodyの対象範囲、共通契約の再利用性、実装可能な最小差分、ChatGPT Firstの一貫性、personal wrapperとの責務分離、後続Issueへ安全に引き継げるprofile設計。
- tradeoff:
  - Aは共通基盤の目的を満たしつつ、profileごとの実装を分割できる。Bは小さいがClarificationや将来roleの契約が断片化する。Cは網羅的だがoperator／wrapperの責務まで混ぜ、Issueを肥大化させる。
- リスク:
  - product-ownedとoperator-onlyを区別しない、未登録profileを暗黙に許す、将来roleのrequired attachmentを定義しない、後続Issueへ引き継ぐ情報を記録しない危険がある。
- 具体シナリオ / edge case:
  - Clarificationが同じcommon envelopeを使わず、回答artifactのidentityが追跡不能になる。
  - 実装ブリーフを今回対象に含めるが、output contractやrequired attachmentsを定義しきれず、暫定自由形式のまま残る。
  - personal wrapperの挙動をproduct runtimeの保証と誤認する。
  - 未登録のgeneral operationがdefault fallbackで送信される。

## Codex の推奨案 (必須)
- 推奨:
  - Option A。ただし今回の実装対象を4つの既存profile（Planning／Formal Review／Semantic Revision／Clarification）に限定し、実装ブリーフ・オンボーディング・general roleはprofile登録を要求する後続Issueとして記録する。
- 理由:
  - ユーザーの「その他のChatGPT利用も整理したい」という意図を共通基盤で受け止めながら、personal wrapperや自由相談を混ぜず、実装可能なprofile単位へ分割できるため。
- 未回答時の影響:
  - Issue #354の責務境界と後続Issueへの引き継ぎ範囲が定まらず、canonical三文書のscope記述を確定できない。

## ユーザー回答 (回答後に必須)
- answer capture:
  - 原文要旨: 「テンプレートや出力形式は必ずしも全ChatGPT利用で必須にしない。スクリプト単位で添付資料を一つのディレクトリにまとめ、その中身をまとめて添付する。合成プロンプトと添付ディレクトリは分離し、ファイルの増減でコード変更を不要にする。内容は一律検査せず、ケースバイケースで柔軟に運用する。Issue Planning／Revisionの出力はディレクトリ構成を保ったZIP形式として指定する。」
- 回答:
  - Option Aの「product-owned全operationに共通基盤」という方向性のうち、責務分離と再利用可能な共通枠は採用する。ただし、すべてのoperationにversioned templateやclosed schemaを必須化する厳格なprofile契約は採用しない。各ChatGPT利用スクリプトは、合成プロンプトMarkdownと、任意の添付資料・手順・出力形式説明を格納するoperation-specific directoryを分離して持つ。スクリプトは指定ディレクトリ内の資料をまとめて添付し、資料の追加・削除でコードを変更しない。内容の意味検査は一律に行わず、必要な作業だけ本文で指定する。出力形式が重要なスクリプトでは、ディレクトリ構成を保持したZIPなどを本文で明示する。
- 回答日時:
  - 2026-08-03（Codex会話上の回答時刻）

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes。添付ディレクトリを機械的に収集する際の再帰範囲、相対path保持、隠しファイル・symlink・secret・サイズ超過などの安全境界を別の一問で確認する。
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - operation-specific attachment directoryの収集・除外・安全検査の最小規則。

## 採用判断 (回答後に必須)
- adoption_status:
  - `partially_adopted`。Option Aのproduct／personal責務分離は採用するが、全operationへの厳格な必須template／schema契約は採用せず、operation-specific directoryを基本単位とする柔軟な運用へ修正した。
- adoption target:
  - Issue #354の`requirement.md`、`design.md`、`plan.md`、ChatGPT operation packの配置・収集設計、および`report.md`のEvidence Adoption Ledger（canonical authoring時に反映）。
- 採用 / 棄却 / deferred の理由:
  - ユーザーは、固定的な全operation契約よりも、スクリプトごとに合成promptと添付ディレクトリを分け、ディレクトリの全資料をまとめて渡せる柔軟性を優先した。出力形式は必要なoperationだけ本文で指定し、Planning／RevisionのZIPはディレクトリ構成を保持する。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - ChatGPT operationごとに合成promptと添付ディレクトリを分離し、資料の増減でコード変更を不要にする。出力形式はoperationごとに必要な場合だけ指定し、内容の一律意味検査は要求しない。
- `design.md`:
  - operation pack（prompt Markdown、attachments directory、必要時のoutput-format guidance）の収集境界と、ZIP等の形式指定を分離して設計する。厳格なschemaは適用するoperationだけが持つ。
- `plan.md`:
  - まずpack directoryの発見・再帰収集・相対path保持を実装し、次にPlanning／RevisionのZIP形式指定と必要なvalidatorをoperation単位で追加する。全operation共通の内容検査は実装しない。
- `ADR`:
  - operation packの配置・収集方式が複数scopeで長期再利用する標準になった場合のみ候補化する。現時点ではIssue-local方針として扱う。
- reflected_to 更新方針:
  - canonical authoring時に、回答artifactと後続disc、ChatGPT advisoryをEvidence Adoption Ledgerへ紐付ける。
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
