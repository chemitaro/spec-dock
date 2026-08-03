---
種別: research
ID: "20260803t005640z-research"
タイトル: "iss-00354 現行 ChatGPT 入力コンテキストと添付契約の調査"
状態: "draft | completed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-08-03"
親: ["iss-00354"]
関連: []
authority: "synthesized"
derived_from: []
reflected_to: []
---

# 20260803t005640z-research iss-00354 現行 ChatGPT 入力コンテキストと添付契約の調査

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約、用語衝突、edge case など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は artifact type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は source-grounded research evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- 事実、推測、未検証事項、用語衝突、edge case、判断への含意を混ぜない。
- local context で解ける疑問は人間に聞かず、この artifact に source-grounding を残す。

## 調査目的 (必須)
- Issue #354 の要件定義・設計・実装計画を作る前に、ChatGPTへ渡す情報の現行実装、既存契約、未確定の利用意図を分離する。
- 特に、本文プロンプトと添付資料の役割、GitHubの対象ブランチ固定、Planning／Review／Revisionの出力境界、同一ChatGPTスレッド継続の現状を確認する。

## sources / 調査方法 (必須)
- 参照先:
  - GitHub `chemitaro/spec-dock` Issue #354、現在ブランチ `codex/iss-00354-chatgpt-context-contract`、現在 HEAD `39c67ef736e34c0131b2a0e38b64085561571f49`
  - `spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/requirement.md`
  - 親 Epic `epic-00331` の `requirement.md`、`design.md`、`plan.md`、`report.md`
  - Issue #354 の `requirement.md` placeholder、`design.md`／`plan.md` placeholder、`report.md` scaffold、`artifacts/rules.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py`
  - `.agents/skills/spec-dock-issue-planning/resources/{planner-prompt.md,reviewer-prompt.md,revision-prompt.md,transport-output-contract.md}`
  - `spec-dock/docs/workflow_issue.md`、`spec-dock/docs/workflow_chatgpt_authoring_pack.md`、`spec-dock/docs/authoring/chatgpt-pack.md`
  - Issue Planningのunit／integration test（`tests/unit/application/test_issue_planning_prompt.py`、`tests/unit/infra/test_issue_planning_chatgpt.py`、`tests/integration/test_issue_planning_chatgpt_transport.py` など）
- 検証手順:
  - `git status --short --branch`、`git rev-parse HEAD`、`gh repo view`、`gh issue view 354` で live identity を確認。
  - prompt synthesis と Oracle adapter の実装・テストを静的に照合し、Planning／Review／Revisionの入力・出力と session 生成を追跡。
  - 上位スコープとIssue bodyの対象範囲・対象外を照合。
- 実験条件:
  - clarification の analysis-only mode。canonical `requirement.md`／`design.md`／`plan.md` は変更しない。
  - 事実と推測を分離し、外部ChatGPTの回答は後続の採用判断まで evidence として扱う。

## facts / 観測できた事実 (必須)
- 対象は `chemitaro/spec-dock` の OPEN Issue #354、親は `epic-00331`、上位は `init-00322` である。現在の作業ブランチは `codex/iss-00354-chatgpt-context-contract`、HEAD は `39c67ef736e34c0131b2a0e38b64085561571f49` で、origin の同名ブランチと一致している。
- Issue #354 の目的は、Planning・Review・Revision およびその他のChatGPT利用について、本文に置く情報、添付する情報、厳密添付する情報、出力契約、秘匿情報の除外を明示的な契約として整理すること。PR #351 の実装ロジック再設計、Candidate履歴の上書き、ChatGPTによるGitHub mutation、アーキテクチャ全体の再設計は対象外と明記されている。
- Issue #354 のcanonical三文書は未具体化である。`requirement.md` は共通要件テンプレート、`design.md` と `plan.md` は `assurance classify`／`assurance compose` 前の placeholder であり、この clarification では埋めない。
- 親 Epic は、Issue Planning の正式経路を `planning create` → `review planning` → 必要時 `planning revise` → fresh PASS → Human decision → `planning apply` と定義し、Candidate／Reviewをevidence-only、Human approval前のrepository mutation禁止、exact current repository／branch／HEAD検証、default branch fallback禁止としている。
- provider側 `PlanningContext` は、Issue ID、repository、branch、source HEAD、親Epic／Initiative、依存summary、canonical Issue三文書の相対path、明示された relevant source paths、operator context、onboarding companion path を持つ。
- prompt synthesis は、役割別 resource（planner／reviewer／revision）と transport contract を本文へ合成し、exact source identity、GitHub connector gate、exact branch／HEAD verification、connector failure時の `repository access failed`、attachment authority、role-specific output expectation を本文へ置く。
- planner／semantic revision の出力期待値は、`requirement.md`・`design.md`・`plan.md` と exactly-one onboarding companion を含む一つの authoring ZIP。reviewerの出力期待値は `reviewed_identity`、`reviewed_identity_sha256`、`verdict`、`findings` の閉じたJSONである。
- 通常のprompt synthesisで添付されるのは canonical Issue三文書と、context manifestで明示された relevant source paths。各添付はprovider内で `context-<index>.md` に包まれ、source pathを本文に付加したうえでOracleへ渡される。context manifestのschemaは `relevant_source_paths` と `operator_context` の二配列に閉じている。
- ReviewではCandidate ZIP、`reviewed-identity.json`、そのSHAファイルをexact attachmentとして扱い、git-boundではcanonical三文書と onboarding companion もexact target attachmentになる。Revisionではprior Candidate ZIP、formal Review JSON、prior canonical三文書、preserved assumptionsを添付する。
- provider-owned Oracle adapterは `PATH` から `oracle` executableを解決し、browser engine、`Pro` selector、managed loopback Chrome、direct argv、API fallbackなしで実行する。個人 `chatgpt-use` wrapperはproduct runtime dependencyではない。
- adapterは各planner／reviewer／semantic-revision invocationで新しい session ID／slugを生成する。同一 invocation内では timeout／disconnect後に同一sessionのstatus／harvestを行うが、別phaseの呼び出し間で既存ChatGPT conversationを `follow-up` する処理は確認できない。
- 既存のPlanning skill／workflowは、long-running browser runのwait／same-session recovery、fresh Review、immutable Candidate、Human gateを要求するが、会話スレッドの業務上の寿命や継続単位はIssue #354の現行実装には定義されていない。
- ChatGPT-Use の clarification advisory は、GitHub exact branch／HEAD一致を確認したうえで受信できた。実行時のモデル証跡は `requested=GPT-5.6 Sol`、`resolved=GPT-5.6 Sol`、`verified=yes` であり、ユーザーが想定する「GPT-5.6 Luna／最大推論」はこのwrapper証跡からは確認できない。
- 最初の短いslugで実行したrunは、detached worker終了後のharvestで別repositoryの古い会話を返したため廃棄した。slugが内部で切り詰められたこと、recover時に誤った既存conversationを返したことが観測された。3〜5語で十分に一意な別slugへcontrolled retryしたrunは、正しい `chemitaro/spec-dock` の回答を返した。
- 同じclarification conversationへ二度目以降の追補を行った際、第三追補では送信確認がtimeoutし、`sendExists=false` のまま同一conversation URLからharvestした回答が得られた。回答内容は追補質問に対応していたため evidence-only artifactとして保存したが、送信成功の一次証跡とモデル選択のverified証跡は欠落している。wrapperのprompt送信確認とharvest／model evidenceの整合性に関する不具合候補として扱い、再送は行っていない。
- その後の同一conversationへの追補でも同じ `Prompt did not appear in conversation before timeout` が発生し、harvest結果は `sendExists=false`、表示上の `model=Instant`、モデル選択 `verified=false` だった。一方、保存された回答本文は依頼したscope questionに対応していた。送信成功・モデル同一性を検証できない回答は advisory evidenceとしてのみ扱い、確定的なモデル能力や送信保証の根拠にしない。

## inference / 推測 (必須)
- 事実から推測したこと:
  - Issue #354の実装では、本文と添付の役割分担をデータ構造・prompt resource・transport pack・validatorで再現可能にする必要がある。
  - 「同じChatGPTスレッドを継続利用する」という新しい利用意図は、現行の各run新規session契約と衝突するため、単なるprompt文言追加ではなく、thread identity、継続範囲、fresh Reviewとの境界、再送／復旧、証跡の保持を定義する仕様判断になる可能性が高い。
  - PlanningのBlue Team文脈を継続しながらRed Team Reviewをfresh conversationに分離する既存のCandidateレビュー方針を維持するかどうかは、同一スレッドの適用範囲を決める中心論点になる。
- 推測の根拠:
  - adapterの `_new_session_id` はphaseごとに新規slugを生成し、`followup`相当の引数や永続thread handleを保持していない。
  - Initiative／Epic／Issueのscope authorityとCandidate／Review／Human/applyのauthority boundaryは既存docsで確定しているため、Issue #354で変更できるのは入力情報契約と、その実装・証跡の局所境界に限られる。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - ChatGPT conversationの継続単位（Issue全体、Planningのみ、Blue Teamのみ等）と、formal Reviewのfresh conversation要件との優先関係。
  - Oracle本体が持つbrowser conversation follow-upの安定した識別子・保持期間・同一threadへの添付更新能力を、provider runtimeが安全に参照できるか。
  - 継続スレッドへ次回送る差分情報（deltaのみか、identity／current source／添付の再送を含むか）と、source HEAD／Candidate identityの不一致時に継続を停止する条件。
  - Planning／Review／Revision以外のChatGPT利用を同じcontext contractへ適用する際の最小共通フィールドとphase-specific拡張。
- 確認できない理由:
  - これらはrepositoryの現行コードだけから決まらず、ユーザーの運用意図とOracleのbrowser transport capabilityの両方に依存するため。

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - 同一ChatGPTスレッドをどの役割・phaseの境界で継続するか。
  - Blue Teamの設計・修正履歴を保持するthreadと、fresh Red Team Review threadを分けるか。
  - thread continuityが使えない／期限切れ／identity mismatchの場合に、停止・新規thread・完全context再送のどれを選ぶか。
- pressure-test question として切り出すべき候補:
  - 「Issueのclarification／Planning／Semantic Revisionは同一Blue threadで継続し、Formal Red Team ReviewはCandidate versionごとにfresh threadとする」方針を採るか。これが既存のfresh Review・immutable Candidate・Human gateと最も衝突が少ないが、Reviewも同一threadにする場合はfresh Review要件を明示的に変更する必要がある。
- 質問せずに解決できた候補:
  - exact repository／branch／HEADを必須にしdefault branch fallbackを禁止すること。
  - task goal・identity・output contractを本文、詳細資料を添付へ分離すること。
  - Candidate／Reviewをevidence-onlyとし、Human approval前のcanonical mutationを禁止すること。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - 「同じスレッド」と、現行adapterの「同一invocation内のsame-session recovery」。
  - 「添付資料」と、providerが作るprompt pack内の `context-*.md` と、Oracleへ直接渡すexact attachment。
  - 「ChatGPT Use」と、operator-sideのpersonal wrapperおよびproduct runtimeのPATH Oracle adapter。
- 既存 docs / code / tests / artifacts / primary sources での使われ方:
  - workflow／skillはsame-session recoveryを実行中sessionの再接続として使い、phaseをまたぐconversation continuityは定義していない。
  - `PlanningPromptAttachment` は `review-target`／`supplemental-context`／`formal-evidence` の分類を持ち、review／revisionのexact attachmentと通常contextのinline attachmentを区別する。
  - product runtimeはprovider-owned direct Oracleを使用し、personal `chatgpt-use`はauthoring／operator work surfaceに限定する。
- 判断が必要な理由:
  - 用語を分けないと、fresh Red Team Reviewを誤ってBlue Team threadへ続ける、または同一session recoveryを別turn continuityと誤認する危険がある。

## edge cases / 具体シナリオ (必須)
- edge case:
  - source HEADが変わった状態で継続threadへfollow-upを送る。
  - Candidate vNのReview結果をthreadが保持しているが、入力ZIPがvN+1へ差し替わっている。
  - Blue Team threadの文脈をRed Team Reviewへ引き継いでしまい、review-only／fresh conversation境界が崩れる。
  - ChatGPT／Oracleが添付を受信できず、本文だけで三文書生成を続行しようとする。
  - conversation handleが失われた、期限切れ、または別repository／branchに結び付いている。
  - prompt本文が長大化し、詳細資料を添付へ分離した契約を実質的に破る。
- その edge case が requirement / design / plan に与える影響:
  - 継続前に repository／branch／HEAD、Candidate identity、attachment manifest／SHAを再検証し、不一致なら停止する必要がある。
  - Reviewは対象Candidateごとにfresh read-only threadを維持するか、方針変更なら既存review protocolを上位scopeで改訂する必要がある。
  - 添付準備失敗は情報不足として扱い、inline代替や無断のdefault branch fallbackを許可しない必要がある。
  - Prompt budget、attachment count、filename preservation、ZIP-only outputの上限と失敗形式を明示する必要がある。

## implications / 判断への含意 (必須)
- requirement / design / plan / adr へ影響する示唆:
  - requirementでは、phaseごとの入力情報を「本文の短い目的・identity・禁止事項」と「添付の詳細・正本・証跡」に分け、exact branch／HEAD、Candidate identity、source／attachment SHA、秘匿情報除外、closed outputを観測可能条件として定義する必要がある。
  - designでは、context manifest、attachment classification、thread handle、continuity state、identity revalidation、fresh Review isolationをprovider／Oracle境界に配置する必要がある。personal wrapper固有の挙動をproduct contractへコピーしない。
  - planでは、まずclarificationでthread scopeとfresh Review境界を確定し、その後に既存prompt／transport／testsの契約を更新し、provider／installed／dogfood parityとnegative testsを追加する順序が妥当である。現段階で三文書を生成してはならない。
  - durableなconversation identity／retention／security判断がscope treeを越えて再利用される場合のみADR候補とし、現時点ではIssue-local clarificationで判断を止める。

## リスク/制約 (任意)
- 長時間のChatGPT利用で同一threadを優先しすぎると、古い設計判断や誤ったCandidate identityが残り、fresh reviewの独立性を損なう。
- 逆に毎回新threadへ戻すと、ユーザーが求める継続的な文脈保持と、長い本文の再送削減を満たせない。
- 既存runtimeは複数phaseのthread handleを持たないため、仕様決定前に実装へ着手すると、後方互換性と証跡の境界を誤る可能性が高い。

## 反映先 (任意)
- reflected_to:
  - 未反映。clarification回答後にIssue-local `interview`／`disc`へ回答と採用判断を記録し、canonical三文書はauthoring phaseまで作成しない。

## 参考（References） (任意)
- `gh issue view 354 --json number,title,state,body,parent,url`
- `git branch --show-current`、`git rev-parse HEAD`、`gh repo view --json nameWithOwner,defaultBranchRef,url`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py`
- `.agents/skills/spec-dock-issue-planning/SKILL.md` と resources 4ファイル
- `spec-dock/docs/workflow_issue.md`、`spec-dock/docs/workflow_clarification.md`、`spec-dock/docs/authoring/scope-layering.md`、`spec-dock/docs/authoring/decision-routing.md`
