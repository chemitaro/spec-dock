---
種別: research
ID: "20260713t011949z-research"
タイトル: "ChatGPT Consultation On Integrated PR Repair Workflow"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
親: ["iss-00313"]
関連: []
authority: "synthesized"
derived_from:
  - "20260713t005118z-research-pr-merge-preparer-repair-limit-clarification-baseline.md"
  - "20260713t005207z-interview-same-family-repair-recurrence-continuation-policy.md"
  - "20260713t005848z-user-proposal-chatgpt-assisted-integrated-pr-repair-batch.md"
reflected_to:
  - "next interview: mandatory consultation scope"
  - "requirement.md authoring input"
  - "design.md authoring input"
  - "plan.md authoring input"
---

# 20260713t011949z-research ChatGPT Consultation On Integrated PR Repair Workflow

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約、用語衝突、edge case など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は artifact type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は source-grounded research evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- 事実、推測、未検証事項、用語衝突、edge case、判断への含意を混ぜない。
- local context で解ける疑問は人間に聞かず、この artifact に source-grounding を残す。

## 調査目的 (必須)
- ChatGPT-Useを組み込んだprogress-based PR repair workflow、integrated repair-batch構造、生成fileのauthority境界、stagnation判定、変更対象を具体化する。

## sources / 調査方法 (必須)
- 参照先:
  - ChatGPT-Use session: `pr-merge-preparer-integrated-repair` (`gpt-5.5-pro`, browser, 2026-07-13, completed)
  - Current provider skill、skill-local template、runtime artifact template、blocker-centric ADR。
  - Issue-local clarification baseline、answered interview、raw product-owner proposal。
- 検証手順:
  - 約23.9k tokenの9-file bundleをdry-run確認後、ChatGPT Proへ一括consultationした。
  - 回答のfile inventoryとworkflow提案をローカルrepository paths、current skill、accepted ADRと照合した。
- 実験条件:
  - GitHub connectorはcurrent local branchをGitHub上で開けず、default branch `main`と添付local evidenceを分析した。したがってcurrent branch固有内容はlocal側で独立検証する。

## facts / 観測できた事実 (必須)
- ChatGPTは固定回数とsame-family即停止の廃止、progress/stagnation判定への移行を支持した。
- 推奨sequenceはcurrent-head review completion、blocking coarse routing、ChatGPT-Use consultation、runtime batch生成、body candidate採用、repair delegation、commit/push、latest-head re-observation、progress/stagnation判定。
- ChatGPTへfront matter込みcomplete fileを直接書かせず、runtime-generated front matter/H1/pathを保持したschema-complete Markdown body candidateを作らせるhybrid案を推奨した。
- Candidate採用前にrepo/branch/head SHA、review evidence coverage、source coverage、禁止操作、未実施claim、scope expansion、front matter/H1不在をfail-closed検査する案を提示した。
- 外部`disc` repair unitをfamilyごとの必須artifactから外し、一つのbatchにRaw Intake、family analysis、cross-family synthesis、integrated repair scope、design/plan、validation、results、commit/push、re-observation、progress ledgerを統合する案を支持した。
- `research`/`disc`/`interview`は必要時のsupporting evidenceとして残し、採用内容をbatchへ反映する。
- Progressは新しいcausal hypothesis/invariant/mechanism/boundary/validation/edge-case evidenceとfalsifiable validationを要求し、iteration countはtelemetryで停止predicateにしない。
- Stagnationはcurrent evidenceのままmaterially new strategyがない、同じstrategy/patch/failureを反復する、または検証可能な期待差分を定義できない状態とする案を提示した。
- Existing authority/scope/external/observation/trigger/platform human gatesとforbidden writesは維持する。
- ChatGPT固有gateとしてexact PR head unavailable、repository access failure、source coverage incomplete、candidate stale/unsafe/incomplete、runtime adoption conflictを提案した。
- Provider skillだけでなく`agents/openai.yaml`、skill-local template、runtime artifact template、dogfooding mirrors、legacy discussion template copiesの整合が必要と指摘した。

## inference / 推測 (必須)
- 事実から推測したこと:
  - Product-owner proposalはbody-candidate hybridで実現でき、runtime identityとChatGPTによる一括authoringを両立できる。
  - ChatGPT consultationをclean/P2-P3-onlyにも必須化するかは、外部availability gateの影響が大きいため明示決定が必要。
- 推測の根拠:
  - Clean/P2-P3-onlyではbranch mutationもrepair batchも不要なため、consultation failureが新しい停止要因にしかならない。一方、ユーザー文言は「レビュー完了後にChatGPT-Use」と広く読める。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - Mandatory consultationの適用範囲。
  - Hard-unrecoverable ChatGPT failure時のmanual fallback authority。
  - Legacy discussion templateを今回同期更新するかdeprecateするか。
- 確認できない理由:
  - いずれも運用availability、外部gate強度、compatibility scopeを変えるproduct-owner判断である。

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - Completed reviewの全てでconsultationするか、blocking/uncertainだけで必須にするか。
  - Recovery不能時は必ずhuman gateか、一回限りの明示waiverでmanual authoringを許すか。
- pressure-test question として切り出すべき候補:
  - Cleanまたは明白なP2/P3-onlyまでChatGPT/browser availabilityへ依存させる必要があるか。
- 質問せずに解決できた候補:
  - Blocking repairではChatGPT-Use consultationを必須にし、integrated batch body candidateを作成する。
  - Runtime front matter/H1/pathはlocal authorityとして保持する。
  - Optional supporting artifactsは許可するがbatchがrepair source of truthであり続ける。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - `complete file`、`body candidate`、`canonical batch`。
- 既存 docs / code / tests / artifacts / primary sources での使われ方:
  - Runtimeはidentity/pathを生成し、skill-local templateはbody scaffoldを提供する。ChatGPT outputはadvisory evidenceでcanonical authorityではない。
- 判断が必要な理由:
  - ChatGPTにcomplete file ownershipを与えるとruntime identityを壊し、analysis-onlyでは一括authoringの利点を失うため、body-only adoption boundaryが必要。

## edge cases / 具体シナリオ (必須)
- edge case:
  - ChatGPTがdefault branchしか参照できない、consultation後にheadが変わる、review body coverageが欠落する、candidateがfront matter/H1や未実施pass claimを含む、final P2/P3-onlyをbatchへ記録するためだけにpushしたくなる。
- その edge case が requirement / design / plan に与える影響:
  - Exact-head/source-coverage/stale/unsafe gates、terminal record-only push禁止、final responseへのterminal evidence handoffを仕様化する。

## implications / 判断への含意 (必須)
- Requirement: fixed countを停止条件にせず、blocking repairでconsultationとintegrated batchを要求し、unresolved blockerを黙認しない。
- Design: runtime identity + ChatGPT body candidate + local adoption reviewのtrust boundaryを定義する。
- Design: familyとrepair scopeを多対多で扱い、一batch内でanalysis/design/plan/resultを閉じる。
- Plan: provider/mirror/current templatesの整合、negative wording scan、artifact generation、manual scenariosを検証する。
- ADR: blocker-centric ADRは維持可能。Mandatory external consultationとbatch authority統合は長期trust-boundary decisionのためADR candidate triageが必要。

## リスク/制約 (任意)
- `materially new strategy`が主観化するリスクはstrategy ID、prior strategy、material delta、expected observable delta、falsifiable validationで抑える。
- ChatGPT failureでclean PRまで止めるavailability regressionを避けるにはmandatory scope決定が必要。
- Terminal evidenceのrecord-only pushは新しいhead/review loopを作るため禁止を維持する。

## 反映先 (任意)
- reflected_to:
  - 次の`interview`回答
  - Canonical Issue authoring
  - `report.md` Evidence Adoption Ledger

## 参考（References） (任意)
- Oracle session slug: `pr-merge-preparer-integrated-repair`
- GitHub Issue `#313`
