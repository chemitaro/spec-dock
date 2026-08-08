---
種別: interview
ID: "20260808t092131z-interview"
タイトル: "Target Issue Finish Semantics Interview"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-08-09"
親: ["iss-00357"]
関連:
  - "iss-00358"
  - "20260808t082616z-research"
  - "20260808t085519z-interview"
scope: "issue"
scope_id: "iss-00357"
created_at: "2026-08-08T09:21:31Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "original ChatGPT thread: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115/c/6a7509b4-8640-83ee-a26d-60c5d59d8479"
  - "ChatGPT clarification session: required-repository-connector-context-repository-60"
reflected_to: []
---

# 20260808t092131z-interview Target Issue Finish Semantics Interview

## 位置づけ

- Planning Levelをdocumentation-onlyとするOption A採用後、元のChatGPTスレッドが残存Gapを再評価し、次の最優先質問として選定した。
- 現行`issue finish`に残るWorkflow gateを除去し、Storage CoreのLifecycle責務を固定するための一問である。
- 回答後は同じArtifactへ記録し、同じChatGPTスレッドへ返す。Canonical docsへの反映は別工程で行う。

## 正式質問として扱う理由

- `requirement.md`:
  - Storage Coreが保証するLifecycle操作と、外部へ委ねる品質・完了判断を分ける。
- `design.md`:
  - GitHub close、active clear、post-sync、partial failure、idempotencyの契約を決める。
- `plan.md`:
  - Authority、Promotion、Delegated Artifact、EAL依存の削除範囲と回帰テストを決める。
- `ADR`:
  - Storage Coreと外部Workflowの長期境界として必要かを判断する。
- chat上の軽微な一問では足りない理由:
  - Issue 357の主要Runtime削除範囲と、Issue 358のPlan / ReportがRuntime gateか純粋なAuthoring guidanceかを左右する。

## 質問の目的

- 対象者:
  - SpecDockのProduct Ownerであるユーザー。
- 何を明確にする質問か:
  - Targetの`issue finish`をthin lifecycle primitiveとして残すか、廃止するか、品質gateを一部残すか。
- 回答が後続判断へ与える影響:
  - Issue 357のLifecycle application contractとIssue 358のCompletion guidance境界を固定する。

## 質問

- pressure-test question:
  - `issue finish`がPlan、Test、Review、EAL等を判定すると、完全撤去を決めたWorkflow gateがRuntimeへ再侵入しないか。
- 質問:
  - Targetの`issue finish`をどの契約にしますか？
- 回答してほしいこと:
  - Option A、B、Cのいずれかを選択してほしい。

## source-grounded context

- 現行`issue finish`はGitHub Issue closeとactive clearだけでなく、Authority、Promotion Record、Delegated Artifact、Evidence Adoption Ledgerを評価する。
- Planning Levelはdocumentation-onlyであり、Runtimeがparse / validate / enforceしない方針が採用済みである。
- Issue 358のPlan Completion criteriaとVerificationはAuthoring guidanceであり、Lifecycle close許可条件ではない方向と整合する必要がある。
- GitHub close失敗時のactive保持、close成功後のclear失敗に対するpartial success診断、再実行安全性はStorage Coreの構造的安全性として残せる。
- どこまでConvenience operationを残すかはProduct boundaryの判断であり、local sourceだけでは確定できない。

## 回答案

- Option A — Thin Lifecycle Primitive:
  - Active Issueを特定する。
  - Linked GitHub Issueをcloseする。既にclosedなら成功扱いとする。
  - close成功後にactive pointerをclearする。
  - post-syncする。
  - Planning Level、Plan完了、Test、Review、EAL、Delegated Authorityは判定しない。
  - GitHub close失敗時はactiveを保持し、close後のclear失敗はpartial successとして診断する。
- Option B — Convenience Commandを廃止:
  - `close <issue>`と`active clear`を個別に実行する。
  - Runtimeは複合Lifecycle操作を提供しない。
- Option C — 一部の完了Gateを残す:
  - Plan、Test、Review等の状態を確認してからcloseする。
  - 残すgateとauthorityを別途定義する必要がある。

## Codex の分析

- 判断軸:
  - Runtime軽量化、利用者の操作性、partial failureの安全性、Workflow gateの再侵入防止、再実行可能性。
- tradeoff:
  - Aは利便性と構造的安全性を残し、品質判断を外へ出せる。BはRuntimeをさらに小さくできるが、複合操作の順序と部分失敗対応を毎回利用者へ委ねる。Cは自動品質gateを残せるが、今回の簡素化方針と衝突する。
- リスク:
  - Aで「finish」という名称が品質完了を連想させるため、DocsでLifecycle close operationであることを明示する必要がある。
- 具体シナリオ / edge case:
  - GitHub close成功後にactive clearが失敗した場合、再実行時に既closedを成功扱いし、active clearとsyncを継続できる。

## Codex の推奨案

- 推奨:
  - Option A。
- 理由:
  - Storage Coreの利便性と整合性を保ちながら、品質・実装完了判断をRuntimeから完全に除去できる。
- 未回答時の影響:
  - Issue 357は現行Lifecycle dependencyの削除範囲を固定できず、Issue 358もPlan / Report / Completion guidanceがRuntime gateではないことを最終確定できない。

## ユーザー回答

- answer capture:
  - 「オプションAを採用します。issue finishについてはこれまでと同じでよいです。基本同じでよいと思います」と明示された。
- 回答:
  - Option AのThin Lifecycle Primitiveを採用する。
  - 利用者から見える従来の基本フロー、すなわちLinked GitHub Issueのclose、close成功後のactive pointer clear、post-syncという利便性は維持する。
  - GitHub close失敗時のactive保持、既closedを成功扱いする再実行安全性、close成功後のclear失敗をpartial successとして診断する構造的安全性も維持する。
  - 一方、「これまでと同じ」は現行のAuthority、Promotion Record、Delegated Artifact、Evidence Adoption Ledger、Plan、Test、Review等のWorkflow gateを残す意味ではない。Option Aに従い、これらの品質・完了判断はRuntimeから除去する。
- 回答日時:
  - 2026-08-09

## 追加確認の要否

- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - `report.md`のTarget semantics。

## 採用判断

- adoption_status:
  - adopted
- adoption target:
  - Issue 357のRequirement / Design / Planと、Issue 358のCompletion guidance境界。
- 採用 / 棄却 / deferred の理由:
  - Product OwnerがOption Aを明示採用し、`issue finish`の利用者向け基本フローは従来どおりでよいと回答したため。
  - Storage Coreの利便性とpartial failureの安全性を維持しつつ、Workflow gateのRuntimeへの再侵入を防ぐ。
- `report.md` Evidence Adoption Ledger への反映要否:
  - 旧EALを必須化せず、Canonical reflection時に通常の採用証跡を残す。

## requirement / design / plan / ADR への含意

- `requirement.md`:
  - Lifecycle operationが品質・Planning Level・Reviewを判定しない契約を採用候補として反映する。
- `design.md`:
  - close / clear / sync順序、idempotency、partial failure、再実行契約を採用候補として反映する。
- `plan.md`:
  - 旧gate依存除去とLifecycle edge caseテストを採用候補として反映する。
- `ADR`:
  - Product boundaryの長期判断として必要か、回答後に判定する。
- reflected_to 更新方針:
  - Canonicalへ実際に採用した時点で更新する。
- adoption reflection:
  - Interview Artifact上で採用済み。Canonical docsにはまだ未反映。
