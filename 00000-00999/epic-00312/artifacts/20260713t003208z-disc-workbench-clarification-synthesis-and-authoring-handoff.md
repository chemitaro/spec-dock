---
種別: disc
ID: "20260713t003208z-disc"
タイトル: "Workbench Clarification Synthesis And Authoring Handoff"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
親: ["epic-00312"]
関連: []
authority: "proposed"
derived_from:
  - "artifacts/20260712t235647z-research-workbench-clarification-baseline-and-decision-inventory.md"
  - "artifacts/20260712t235757z-interview-initial-workbench-copy-file-policy.md"
  - "artifacts/20260713t000250z-interview-root-workbench-cross-worktree-handoff.md"
  - "artifacts/20260713t001708z-interview-scope-workbench-copy-collision-policy.md"
  - "artifacts/20260713t002530z-interview-experimental-workbench-rollout-boundary.md"
reflected_to: []
---

# 20260713t003208z-disc Workbench Clarification Synthesis And Authoring Handoff

## 位置づけ
- 用途: 集まった質問回答や調査をもとに、意思決定前の synthesis、選択肢、tradeoff、reflection proposal、ADR candidate triage、推奨反映先を整理する。
- authority default: `proposed`。通常は artifact type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は synthesis / reflection proposal / adoption target / ADR triage の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 人間から回答を引き出し、回答欄や未回答事項を管理する場合は `interview` を使う。
- 生ログや未整理の思考は `blank`、事実確認や外部根拠は `research`、長期判断の固定は `adr` に分ける。
- この doc は proposal / synthesis であり、issue `report.md` の observed evidence ledger ではない。採否の最終証跡は canonical docs / ADR / `report.md` Evidence Adoption Ledger に昇格する。
- doc が大きくなりすぎたら、質問回答は `interview`、事実調査は `research`、raw capture は `blank`、長期決定は `adr` へ分割する。

## 対象論点 (必須)
- 今回整理する論点:
  - ChatGPT-firstで雑に使えるGit ignored Workbenchの配置、authority、lifecycle、runtime safety、Scope copy、root handoff、rollout。
- この synthesis が必要な理由:
  - 複数回の設計分析と4件の正式ユーザー回答を、Epic requirement / design / plan authoringへ矛盾なく渡すため。

## derived question sheets / research (必須)
- `interview`:
  - `20260712t235757z-interview-initial-workbench-copy-file-policy.md`: Workbench全体を形式不問でcopyする。
  - `20260713t000250z-interview-root-workbench-cross-worktree-handoff.md`: Rootは自動・一括copyせず、必要fileだけモデルが手動copyする。
  - `20260713t001708z-interview-scope-workbench-copy-collision-policy.md`: Recursive merge、same-pathはSource優先上書き。
  - `20260713t002530z-interview-experimental-workbench-rollout-boundary.md`: Provider runtimeへ実装し全consumerへexperimental提供する。
- `research`:
  - `20260712t235647z-research-workbench-clarification-baseline-and-decision-inventory.md`。
- その他の根拠:
  - Parent Initiative、Epic 259 / 295 / 107、managed gitignore、recursive scanners、authoring source manifest、worktree runtime / tests。

## synthesis (必須)
- 合意済みのこと:
  - Scope作成前・横断作業は`spec-dock/.workbench/YYYY-MM-DD/`。
  - Scope固有作業はInitiative / Epic / Issue direct childの`.workbench/`。
  - WorkbenchはGit ignored、local-only、disposable、non-canonical。Session / manifest / TTL / catalogは持たない。
  - Scope / worktree削除時に消えてよく、delete blockerを設けない。
  - `.workbench/`はruntime-wide reserved opaque subtreeとしてdefault traversalから除外する。
  - Root Workbenchはcopy commandの対象外。必要fileだけモデルが手動copyする。
  - Scope-local copyは明示commandで、Source=current worktree、Scope 1件、Target worktree 1件、no sync。
  - Copyは内容を選別せず、nested `.git`等も含めWorkbench全体をcopyする。
  - Destination directoryを置換せずrecursive mergeし、same-path fileはSourceで上書きする。
  - Provider runtime / assetsへ一度だけ実装し、`init/update`で全consumerへexperimental提供する。
  - Durable evidenceは`artifacts/`、adopted authorityはcanonical docs / accepted ADR / report EAL。
- 未合意 / 未確定のこと:
  - User-intent blockerはなし。Target worktree resolver、file-directory collision、partial I/O failure、CLI JSON shapeはIssue-local technical designで決められる。
- source-grounded に解決できたこと:
  - Existing Epic再利用ではなく新Epic 00312が適切。3 Issue程度の直列分割が妥当。Provider source of truthとdogfooding parityが必要。

## 選択肢 / tradeoff (必須)
- Option A:
  - Pros:
    - 現在の合意案。Minimal Workbench semantics、Scope-only copy command、provider experimental rolloutで一貫する。
  - Cons:
    - Copy内容を選別しないため、利用者が置いた不要物も複製する。
- Option B:
  - Pros:
    - Safety catalog、root copy、shared store、automatic syncを追加すれば制御は強くなる。
  - Cons:
    - 低摩擦性を失い、第二の管理systemとpublic surfaceを増やすため棄却済み。

## reflection proposal (必須)
- canonical docs / workflow / template / skill guidance へ反映すべき候補:
  - 上記合意をEpic cross-Issue invariantとしてrequirement / design / planへ採用する。
  - SkillはRoot manual selection、Scope copyの明示ユーザー指示、copy後no sync、artifact化境界を持つ。
- まだ proposal に留める理由:
  - Canonical authoringとfresh spec-reviewer gateが未実施のため。

## adoption target / 採用先候補 (必須)
- `requirement.md`:
  - Capability、scope/non-scope、authority、use cases、experimental availability、acceptance criteria。
- `design.md`:
  - Reserved subtree policy、provider layers、recursive merge / source-wins copy、root/manual boundary、failure semantics。
- `plan.md`:
  - Issue 1 safety foundation、Issue 2 copy command、Issue 3 docs/dogfood/final gateの直列relay。
- `ADR`:
  - 現時点では不要。Experimentalで可逆なEpic-local contract。
- `report.md` Evidence Adoption Ledger:
  - Research、4 interview、synthesisの採用判断と各phase reviewer gate。

## ADR triage / ADR candidate triage (必須)
- ADR candidate か:
  - no
- hard to reverse:
  - no
- surprising without context:
  - no
- real tradeoff:
  - yes
- ADR 化しない場合の反映先:
  - `requirement.md`, `design.md`, `plan.md`, `report.md` Evidence Adoption Ledger

## 推奨案 (必須)
- 合意済みminimal hybridをそのままcanonical authoringへ採用する。Workbenchを管理systemへ発展させず、runtime safetyと明示Scope copyだけを製品化することで、低摩擦とworktree handoffを両立できる。

## 推奨反映先 (必須)
- `requirement.md`:
  - Primary objective、user scenarios、scope/non-scope、authority、experimental rollout、E-RQ / E-AC。
- `design.md`:
  - Opaque subtree contract、copy sequence、merge semantics、provider parity、scanner inventory boundary。
- `plan.md`:
  - 3 Issue、dependency `safety -> copy -> dogfood/final gate`、no per-Issue PR方針の検討。
- `ADR`:
  - なし。
- `report.md` Evidence Adoption Ledger:
  - 本artifact群をadopted evidenceとして記録する。

## 未採用 / deferred 理由 (必須)
- 未採用:
  - Central scope bucket、shared store、symlink sharing、automatic copy-on-create、root copy command、file allowlist / denylist、secret scan、TTL、manifest DB、automatic sync / copy-back。
- deferred:
  - Root attach helper、export/import、active-lineage batch copy、advanced safety mode。Dogfoodで需要が実証された場合だけ別Issue候補とする。

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - 本synthesisの合意済み項目をEpic canonical docsへauthoringし、各phaseでfresh spec-reviewer gateを通す。
- 追加で作る artifacts:
  - Requirement / design / plan draft evidenceはChatGPT-first Epic planning workflowに従って必要時に作成する。Clarificationの追加interviewは現時点では不要。
