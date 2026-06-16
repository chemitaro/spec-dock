---
種別: disc
ID: "20260613t084318z-disc"
タイトル: "Issue Execution Skill Update Direction"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-13"
親: ["iss-00186"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260613t084318z-disc Issue Execution Skill Update Direction

## 対象論点 (必須)
- 今回整理する論点:
  - `spec-dock-issue-execution` skill を、既存ADRの責務分担に準拠しながら、Issue execution の逐次 step 実行、per-step review、per-step commit、delegated mutation をより確実に守らせる方向性。
- この synthesis が必要な理由:
  - 既存 `workflow_issue.md` には詳細な execution policy があるが、agent が first-read の skill / prompt / template surface で踏み外す余地が残っている。
  - 一方で、skill へ詳細 policy を全文移植すると、既存ADRが採用した `compact workflow spine in skills + details in docs/templates` 方針と衝突する。

## derived question sheets / research (必須)
- `interview`:
  - なし。現時点では local source と prior research で方向性を整理できる。
- `research`:
  - `20260613t082454z-research-issue-execution-step-gate-analysis.md`
  - `20260613t082641z-research-skill-workflow-spine-policy-analysis.md`
  - `20260613t083027z-research-deep-consultant-skill-policy-findings.md`
- その他の根拠:
  - Accepted ADR: `20260605t080509z-adr-skill-docs-template-context-surface-ownership.md`
  - Prior synthesis: `20260605t040338z-disc-skill-docs-workflow-spine-synthesis.md`
  - Prior inventory: `iss-00162/.../20260606t040013z-disc-context-surface-inventory.md`
  - Existing `spec-dock-hub` skill policy.

## synthesis (必須)
- 合意済みのこと:
  - 新しいADRは現時点では不要。今回の方向性は、既存の accepted ADR「Skills / Docs / Templates の context-surface ownership」に準拠する形で整理できる。
  - Skill は「薄いが空ではない」first-read operational workflow spine を持つべきである。
  - Docs は lifecycle policy、field meanings、hard cases、failure/recovery semantics などの詳細正本を持つべきである。
  - Templates は scaffold / evidence slots / good examples であり、compliance authority ではない。
  - `spec-dock-issue-execution` の問題は、workflow policy が存在しないことではなく、最重要の実行 loop が first-read surface で十分に目立っていないことにある。
- 未合意 / 未確定のこと:
  - `iss-00186` の実装 scope に templates / `/execute-issue` prompt / empirical harness まで含めるか、skill + workflow docs の最小補強に絞るか。
  - `approved-local-execution` / `degraded mode` の語彙を変更するか、既存語彙を残して例外境界だけ明確化するか。
- source-grounded に解決できたこと:
  - `spec-dock-issue-execution` は workflow policy の全文移植先ではない。
  - `workflow_issue.md` は引き続き issue execution lifecycle / reviewer / delegation / completion policy の detail authority である。
  - `authoring/issue-plan.md` は step field semantics / executable step schema / concrete test case / reviewer fail conditions の detail authority である。

## 選択肢 / tradeoff (必須)
- Option A: skill をほぼ現状維持し、`workflow_issue.md` だけを補強する
  - Pros:
    - skill の肥大化を避けられる。
    - detail authority を docs に保てる。
  - Cons:
    - agent の first action が変わりにくく、今回の追随性問題が残る可能性が高い。
    - mandatory execution loop が docs 内に隠れ続ける。
- Option B: `workflow_issue.md` の execution policy を skill へ全文移植する
  - Pros:
    - agent が一読で多くの policy を見られる。
  - Cons:
    - skill が肥大化し、docs と二重正本になる。
    - drift が増え、既存ADRの ownership model と衝突する。
- Option C: skill に compact gate spine を追加し、詳細 semantics は docs / authoring docs / templates に残す
  - Pros:
    - agent が first-read で mandatory loop と stop condition を見られる。
    - docs は detail authority のまま保てる。
    - 既存ADRの採用方針と一致する。
    - 既存 test fragment を壊さず additive に進めやすい。
  - Cons:
    - skill / docs / template / prompt の整合確認が必要。
    - どこまでを今回 scope に含めるかを requirement / design で明確にしないと広がりやすい。

## reflection proposal (必須)
- canonical docs / workflow / template / skill guidance へ反映すべき候補:
  - `spec-dock-issue-execution` skill の先頭近くに、single current step / delegation / review / commit / clean / next-step unlock を含む compact reminder を追加する。
  - `workflow_issue.md` に、`Step Result Approval` として next step へ進んでよい条件を明文化する。
  - `workflow_issue.md` に、final commit は earlier implementation step の未 commit diff をまとめる救済 commit ではないことを明文化する。
  - `approved-local-execution` / `degraded mode` は通常成功値ではなく、例外 / availability evidence であることを明確化する。
  - `authoring/issue-plan.md` / templates / `/execute-issue` prompt は、scope に応じて alignment check または follow-up とする。
- まだ proposal に留める理由:
  - `requirement.md` / `design.md` / `plan.md` がまだ scaffold 状態であり、正式採用には spec authoring と fresh reviewer gate が必要。
  - skill / workflow docs / templates / prompt のどこまでを同一 issue に含めるかは scope decision が必要。

## adoption target / 採用先候補 (必須)
- `requirement.md`:
  - Non-negotiable constraints と acceptance criteria に、single-step execution、delegated mutation、per-step review、per-step commit/clean、next-step unlock を観測可能な要件として入れる。
- `design.md`:
  - Skill / workflow docs / authoring docs / templates / prompt の surface responsibility table を置く。
  - Provider-side source と dogfooding mirror の扱いを明記する。
  - Skill は compact gate spine、workflow docs は detail authority、templates は scaffold/evidence slot という設計制約を明記する。
- `plan.md`:
  - Research adoption -> skill wording -> workflow wording -> tests/assertions -> docs/templates/prompt alignment check -> validation/review の順に step 分割する。
- `ADR`:
  - 追加ADRなし。既存 accepted ADR への準拠として扱う。
- `report.md` Evidence Adoption Ledger:
  - この `disc` と3本の `research` の採否を記録する。

## ADR triage / ADR candidate triage (必須)
- ADR candidate か:
  - no
- hard to reverse:
  - no。今回の方向性は既存ADRを具体 issue に適用するもので、別の長期意思決定ではない。
- surprising without context:
  - no。既存ADR、hub skill、prior synthesis、inventory に根拠がある。
- real tradeoff:
  - yes。skill を厚くするか薄くするかの tradeoff はあるが、既存ADRが Option C をすでに採用している。
- ADR 化しない場合の反映先:
  - `disc`, `requirement.md`, `design.md`, `plan.md`, `report.md` Evidence Adoption Ledger

## 推奨案 (必須)
- Option C を採用候補にする。
- `spec-dock-issue-execution` skill は、詳細 schema や completion matrix を抱え込まず、first-read で実行者が踏むべき gate spine を目立たせる。
- 追加する spine は、少なくとも次を含む:
  - implementation step は常に single current step として扱う。
  - 次 step の実装 / 委任 / review / commit を始める前に、現在 step の Step Contract Closure、required verification、fresh step reviewer pass、Step Commit Gate、post-commit clean check を閉じる。
  - file mutation は step の implementation delegation gate を通して `dev-coder` / `doc-writer` に委任する。
  - parent direct implementation は事前記録済み `Parent Implementation Exception` だけに限定する。
  - unavailable / denied / host conflict / waiver は required gate pass ではなく blocked / incomplete または explicit risk acceptance として扱う。
- `workflow_issue.md` はこの spine の詳細正本として、`Step Result Approval`、exception semantics、final commit boundary を明文化する。
- `authoring/issue-plan.md` と templates は必要に応じて、mutating step の `N/A` や multi-step bundled log が通常成功に見えないよう alignment する。ただし template を compliance authority にしない。

## 推奨反映先 (必須)
- `requirement.md`:
  - AC / EC / non-negotiable constraints として、step bundling 防止、parent direct mutation 防止、review/commit gate 欠落防止を定義する。
- `design.md`:
  - Surface responsibility mapping と最小変更方針を明記する。
  - Tests / assertion impact を明記する。
- `plan.md`:
  - Provider skill update、workflow docs update、test assertion update、mirror/sync validation、review gates を分離する。
- `ADR`:
  - 追加しない。
- `report.md` Evidence Adoption Ledger:
  - この direction を採用 / 部分採用 / 棄却 / deferred のどれにするか記録する。

## 未採用 / deferred 理由 (必須)
- 未採用:
  - Workflow policy の全文 skill 移植: 既存ADRに反し、skill bloat と drift を招くため採用しない。
  - Workflow docs のみの補強: first-read の踏み外しを直接改善しにくいため単独案としては採用しない。
  - Runtime enforcement 先行: 今回の主問題は agent action selection であり、runtime gate は将来 follow-up とする。
- deferred:
  - Empirical skill compliance harness: 有用だが、初回 hardening の必須範囲に入れると scope が大きい。
  - `dev-coder` / `doc-writer` agent definition の権限変更: 今回は issue execution surface の方向性整理が主眼。
  - 過去 issue report の backfill: 今回の対象外。

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - `requirement.md`: Option C を前提に、観測可能な AC / EC と non-scope を書く。
  - `design.md`: Skill / workflow docs / authoring docs / templates / prompt / tests の responsibility と変更候補を整理する。
  - `plan.md`: 実装 step を小さく分け、per-step review / commit gate を plan 自体に入れる。
  - `ADR`: 追加しない。既存ADR準拠として `report.md` に採用判断を残す。
- 追加で作る discussion docs:
  - 現時点では不要。requirement authoring 中に scope 判断が割れた場合だけ `interview` を作る。
