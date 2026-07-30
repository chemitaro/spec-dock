---
種別: disc
ID: "20260730t093657z-disc"
タイトル: "ChatGPT First Review and Tier Follow Up Handoff"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-07-30"
親: ["epic-00331"]
関連: ["init-00322", "epic-00331", "iss-00334"]
authority: "proposed"
derived_from:
  - "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/artifacts/20260730t093657z-research-chatgpt-first-time-analysis-and-optimization.md"
reflected_to:
  - "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/report.md"
  - "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00334-implement-chatgpt-issue-planning-workflow/report.md"
---

# 20260730t093657z-disc ChatGPT First Review and Tier Follow Up Handoff

## 位置づけ

- 本書は`iss-00334`の完了範囲と後続Issueの境界を保持するEpic-level handoff evidenceである。
- canonical authorityではない。後続IssueのRequirement／Design／Planへ採用するときは、current `main`、親正本、完了済みIssue、依存状態を再確認し、fresh Planning Reviewを通す。
- 元の時間分析はInitiative artifact `20260730t093657z-research-chatgpt-first-time-analysis-and-optimization.md`にbyte-identicalで保存されている。

## 対象論点

- ChatGPT Firstの時間分析で得たPlanning Review契約強化とrole-based intelligence profileを、進行中の`iss-00334`へ追加するか、後続Issueへ分離するか。
- 後続Issueへ分離した場合に、Initiative／Epic／Issueのどの正本と実装面へ反映するか。

## 根拠

- Humanは2026-07-30、分析結果を踏まえた現Issueと後続Issueの適切な境界分析を依頼した。
- `iss-00334`のRequirement／Design／append-only Plan／Report。
- provider-owned `issue_planning_chatgpt.py`とReviewer Prompt。
- exact branch／HEADを確認したbounded ChatGPT Pro decision consult `iss00334-amend-or-split-decision`。
- Initiative research artifact `20260730t093657z-research-chatgpt-first-time-analysis-and-optimization.md`。

## 採用した境界

- Option Bを採用する。
- `iss-00334`は現行accepted contractを完走不能にする欠陥だけを修正し、現行S12〜S14、commit／push、merge-ready PRまで完了させる。
- same-session publication raceは`REQ-020`／`AC-020`に直接結び付くため`iss-00334`で修正する。
- Planning Review契約のcross-scope hardeningとrole-based intelligence profileは、Human merge後の`main`から後続Issueとして実施する。
- current accepted contractに直接結び付かない「より良いarchitecture」、generic framework、任意設定、将来拡張は`iss-00334`のblocking scopeへ追加しない。

## source-groundedな現在地

- 現行RequirementとReviewer Promptにはfresh／read-only／defect-only境界がすでに存在する。
- 現行adapterは全roleを`--model Pro`へ固定し、High／Extra High routingは未実装である。
- valid authoring ZIP生成後にpublic commandが`oracle_session_recovery_required`となるpublication raceをlive dogfoodで再現した。
- High／Extra Highのmanaged Chrome selector、品質、所要時間、recovery、no-fallback、distribution parityは未実証である。

## 後続Issue候補1 — Planning Review contract hardening

### 目的

- 全Planning targetに共通するdefect成立条件を閉じる。
- 新しいarchitecture、schema、workflow、abstraction、optional hardening、future extension、style preferenceをfindingとして採用しない。
- architecture判断が必要な場合はReviewerが解かず、`planning-gap`としてHuman gate経由でPlanningへ戻す。
- Promptとvalidatorが同じReview contractを参照し、lexical／semantic driftを検出する。

### 主な採用候補

- Initiative／Epic／Issue／Targeted／Final Reviewの責務分離。
- findingの必須要素: exact location、accepted requirementまたは直接矛盾、concrete impact、architecture再開なしで修正可能であること。
- suggestionとblocking defectの分離。
- P0／P1が0件ならPASSという既存severity gateの維持。

### 非目標

- Reviewerによる再設計。
- generic Review frameworkの先行構築。
- 改善提案をP1へ昇格すること。

## 後続Issue候補2 — Role-based ChatGPT intelligence profile

### 目的

- Planning authoring／Semantic Revision、bounded Review、final integrationへ役割別のprofileを割り当て、同じ分析を全工程で重複させない。
- requested／resolved profileとfallbackを証跡化し、silent fallbackを禁止する。

### 評価仮説

- Initiative／Epic／Issue Planning authoringとSemantic Revision: Pro。
- step concretization、bounded Planning／implementation Review、repair／closure: High。
- final combined／Epic Delivery／Initiative Final Review: Extra High。
- architecture ambiguityはtier escalationでReviewerに解かせず、`planning-gap`としてPro Planningへ戻す。

### 必須評価

- managed ChromeでのHigh／Extra High selector availabilityとlive evidence。
- exact argv、recovery時profile維持、no-fallback、provider／projection／distribution parity。
- duration、error class、finding count、accepted finding、repair count、final-only finding。
- High ReviewとExtra High final Reviewのincremental finding quality。

### 非目標

- generic tier registry。
- arbitrary operator configuration。
- Grade-based routing。
- `chatgpt-use`等の個人wrapperをSpecDock product dependencyにすること。

## 推奨する実施順

1. `iss-00334`を現行scopeでmerge-readyにし、Humanがmergeする。
2. 最新`main`からPlanning Review contract hardening Issueを作成する。
3. そのIssueの契約を前提に、role-based intelligence profile Issueを作成する。
4. 各Issueはone Issue／one branch／one PR、fresh Review、Human-only mergeを維持する。
5. 既存`iss-00335`／`iss-00336`へ吸収するか新規Issueにするかは、materialize時のcurrent parent docsとdependency graphで決める。

## 推奨を反転する条件

- exact current-HEAD Reviewerが既存defect-only契約に反してscope外findingを繰り返しP0／P1化し、現行Review gateを完走できない。
- all-Pro routingが単なる遅延ではなく、明示Requirement／AC違反、selector failure、安全性欠陥、またはcurrent workflowの再現可能な完走不能原因になる。
- fresh final Reviewがrole routingまたは追加Review境界を既存accepted contractへ直接結び付くP0／P1として報告する。
- Humanが`iss-00334`のaccepted scopeをPR前に明示変更し、identity全面再確立と追加delivery時間を受け入れる。

## 永続handoff checklist

- 後続Issue planningは本artifactとInitiative research artifactをrequired sourceとして読む。
- current `main`、完了済みIssue、既存Issue seeds、dependency edge、親正本のdriftを確認する。
- 未実証のHigh／Extra Highを事実としてRequirementへ書かず、evaluation hypothesisとして開始する。
- current `iss-00334`のCandidate／Reviewを後続Issueのauthorityとして再利用しない。
- live evidence取得後にだけ長期ADRの要否を再評価する。
- 後続Issue ID、依存edge、採用先、review結果をEpic `report.md` Evidence Adoption Ledgerへ追記する。
