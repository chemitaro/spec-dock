---
種別: research
ID: "20260713t005118z-research"
タイトル: "PR Merge Preparer Repair Limit Clarification Baseline"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
親: ["iss-00313"]
関連: []
authority: "synthesized"
derived_from:
  - "../../../../../../../../../../src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md"
  - "../../../../../../../../../../src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md"
  - "../../../../../../../../../../spec-dock/templates/artifacts/pr-repair-batch.md"
  - "../../../../../../../../../../spec-dock/adrs/20260623t074447z-adr-blocker-centric-pr-risk-closure-rereview.md"
reflected_to:
  - "interview: repair continuation after same-family recurrence"
  - "requirement.md authoring input"
---

# 20260713t005118z-research PR Merge Preparer Repair Limit Clarification Baseline

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約、用語衝突、edge case など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は artifact type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は source-grounded research evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- 事実、推測、未検証事項、用語衝突、edge case、判断への含意を混ぜない。
- local context で解ける疑問は人間に聞かず、この artifact に source-grounding を残す。

## 調査目的 (必須)
- `github-pr-merge-preparer` が持つ回数ベースの停止条件と、それ以外の安全上の human gate を分離し、夜間自動実行を不必要に止める契約を特定する。

## sources / 調査方法 (必須)
- 参照先:
  - Provider authority: `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`
  - Skill-local repair batch scaffold: `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md`
  - Runtime artifact template: `spec-dock/templates/artifacts/pr-repair-batch.md`
  - Accepted ADR: `spec-dock/adrs/20260623t074447z-adr-blocker-centric-pr-risk-closure-rereview.md`
  - Dogfooding mirror: `.agents/skills/github-pr-merge-preparer/`
- 検証手順:
  - `Fix loop limits`、`Loop Control`、`Stop Conditions` を横断検索し、同じ停止契約の重複を確認した。
  - Provider sourceとdogfooding mirrorの配置を確認した。
- 実験条件:
  - 文書・skill contractの静的調査のみ。PR修復ループ自体は実行していない。

## facts / 観測できた事実 (必須)
- Skillは次の数値上限を持つ: `P0` familyは原則1回、同一`P1 root_cause_family`は2回、PR preparation invocation全体は4回。
- Skillは数値上限とは別に、同じ`root_cause_family`がrepair commit後に再出現した時点でhuman gateへ止める。これは実質的に同一familyの継続修復を1回で止める。
- Skill-local templateとruntime artifact templateも、same-family recurrenceとloop limit到達をStop Conditionsとして重複保持する。
- `permission_or_auth`、`external_or_flaky`、`base_branch_conflict`、`unknown`、requirement expansion、breaking change、migration、secret/deployment setting、ambiguous review intent、platform-only conversation resolution等は、回数と無関係なhuman gateである。
- Accepted ADRは「Stagnationはhuman gate」「loop countだけでrisk acceptanceしない」と定めるが、stagnationを固定回数としては定義していない。
- 変更のauthorityはprovider-side `src/spec_dock/assets/install_root/.agents/skills/`であり、`.agents/`はdogfooding mirrorである。

## inference / 推測 (必須)
- 事実から推測したこと:
  - ユーザーが問題視する夜間停止を解消するには、3つの数値上限だけでなくsame-family recurrenceによる即時停止も見直す必要がある可能性が高い。
  - 安全性は回数ではなく、各iterationで新しい有効なrepair strategyがあり、scope内で検証可能かというprogress判定で維持できる。
- 推測の根拠:
  - 数値上限を削除してもsame-family recurrence stopが残れば、典型的な再レビュー修正は一度の再出現で停止し、ユーザーが「続けてください」と再開する状態が残るため。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - ユーザーがsame-family recurrence stopも撤廃対象と考えているか。
  - Stagnationの具体的な判定を「同じ修正を繰り返す」「新しい根拠やstrategyがない」「検証が前進しない」のどこまでIssue契約に含めるか。
- 確認できない理由:
  - これは夜間自律性とfail-closed safetyのproduct-owner判断であり、local sourceだけでは意図を確定できない。

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - 数値上限だけを削除するか、same-family recurrence stopもprogress-based継続へ置き換えるか。
- pressure-test question として切り出すべき候補:
  - 同じ`root_cause_family`が修正後に再出現しても、新しい修正戦略と検証可能な前進がある限り自律継続してよいか。
- 質問せずに解決できた候補:
  - permission/auth、外部障害、scope/requirement expansion、breaking change等の人間判断が必要な停止条件は維持する。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - `loop limit`、`same root_cause_family reappears`、`stagnation`。
- 既存 docs / code / tests / artifacts / primary sources での使われ方:
  - Skillは前二者を機械的停止条件として使い、ADRはstagnationをhuman gateとする一方で固定回数を要求しない。
- 判断が必要な理由:
  - same-family recurrenceをstagnationと同一視すると、異なる修正戦略で前進可能なrepairまで停止する。

## edge cases / 具体シナリオ (必須)
- edge case:
  - 修正Aで一部を直した結果、同じfamilyの別境界条件がfresh reviewで見つかる。
  - 同一failureが同一head/同一strategyで反復し、新しいevidenceも修正案もない。
  - 修復可能だが新しいtrigger承認、権限、migration、requirement expansionが必要になる。
- その edge case が requirement / design / plan に与える影響:
  - 1件目は自律継続候補、2件目はstagnation human gate、3件目は既存の安全human gate維持とする境界が必要。

## implications / 判断への含意 (必須)
- Requirementでは「固定回数では止めない」と「前進不能または新しい権限・scope判断が必要なら止める」を別々の受け入れ条件にする。
- Designではiteration ledgerを維持し、回数を停止判定ではなく監査証跡として扱う。
- Planではprovider skill、skill-local template、runtime artifact template、dogfooding mirrorの整合確認が必要。
- Accepted ADRのblocker-centric方針とstagnation human gateは維持でき、ADR新設は現時点で不要。

## リスク/制約 (任意)
- 無条件の無限再試行へ変更すると、同一修正の反復、token/CI消費、外部サービス負荷が増える。固定回数撤廃は「progressがある限り継続」であり「停止条件なし」ではない。

## 反映先 (任意)
- reflected_to:
  - 次の`interview`回答
  - `requirement.md`

## 参考（References） (任意)
- GitHub Issue `#313`
