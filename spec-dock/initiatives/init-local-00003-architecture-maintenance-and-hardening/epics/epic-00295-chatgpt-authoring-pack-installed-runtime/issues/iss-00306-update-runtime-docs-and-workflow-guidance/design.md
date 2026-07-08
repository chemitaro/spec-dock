---
種別: 設計書（Issue）
ID: "iss-00306"
タイトル: "Runtime Workflow Guidance"
関連GitHub: ["#306"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
依存: ["requirement.md"]
親: ["epic-00295", "init-local-00003"]
---

# iss-00306 Runtime Workflow Guidance — Issue 設計書

## 1. Standard grade

このIssueは `standard` として扱う。

理由:

- 変更の中心はdocs / workflow guidanceだが、installed runtime command surface、installed skill taxonomy、authority boundary、relay PR delivery policyを説明する。
- 誤ったdocsは、ChatGPT outputのcanonical adoption誤認、reviewer pass誤認、execution-ready / PR-ready誤認につながる。
- 新しいruntime behavior、migration、永続データ変更、GitHub mutation、破壊的変更は行わない。

`strict` へ引き上げる条件:

- runtime command behaviorを変更する。
- `.assurance.json` / lifecycle / sync / validate / active の意味論を変更する。
- automatic Issue creation、canonical mutation、reviewer pass automation、PR-ready automationを実装対象に含める。

## 2. 正本と責任境界

| 種別 | パス | このIssueでの意味 |
|---|---|---|
| Provider docs | `src/spec_dock/assets/spec_dock/docs/` | shipped scaffold source of truth。先に更新する正本 |
| Dogfooding mirror docs | `spec-dock/docs/` | provider docs のローカル検証 mirror |
| Installed skill | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md` | ChatGPT evidence lane の操作kernel。docsはこのcontractを利用者向けに補足する |
| Runtime CLI | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/` | supported command surface の根拠 |
| Issue draft artifacts | `spec-dock/active/issue/artifacts/*draft*` | draft-adoption input。正本ではない |
| ChatGPT Use analysis | Issue-local artifact | planning補助 evidence。正本ではない |

## 3. Target docs architecture

### DES-001: ChatGPT authoring workflow guide

新規または更新対象:

- `src/spec_dock/assets/spec_dock/docs/workflow_chatgpt_authoring_pack.md`
- `spec-dock/docs/workflow_chatgpt_authoring_pack.md`

責務:

- ChatGPT / Oracle を SpecDock planning workflow の shared evidence lane として説明する。
- Initiative -> Epic、Epic -> Issue、Issue draft adoption の大きな流れを説明する。
- `github-synced` と `local-context` の evidence mode を説明する。
- ZIP/tree/candidate/stage/validation output は `authority: evidence_only` であり、main orchestratorのEAL採否とfresh reviewer passまで正本にならないと説明する。
- human approval before node creation と Issue draft adoption after node creation の順序を説明する。
- 中間IssueごとのPR deliveryは行わず、最終IssueでEpic品質ゲートとmergeable PR deliveryを行う relay policy を説明する。

### DES-002: Backend invocation reference

新規または更新対象:

- `src/spec_dock/assets/spec_dock/docs/reference_authoring_pack_backend.md`
- `spec-dock/docs/reference_authoring_pack_backend.md`

責務:

- `authoring backend invoke` の薄いbackend invocation contractを説明する。
- backend command はCLI引数または環境変数で設定される外部dependencyであり、SpecDock productが個人PC固有のwrapper pathへ依存しないことを説明する。
- 未設定時はfail-closedで、明確なerrorになることを説明する。
- prompt pack / output dir / evidence mode / dry-run / invocation summary の意味を説明する。
- backend invocationはChatGPT output取得であり、canonical adoptionやreviewer passを行わないと説明する。

### DES-003: Prompt pack / ZIP / staged evidence reference

新規または更新対象:

- `src/spec_dock/assets/spec_dock/docs/authoring/chatgpt-pack.md`
- `spec-dock/docs/authoring/chatgpt-pack.md`

責務:

- prompt pack、ZIP/tree output、review report、stage report、candidate pack、draft adoption input の関係を説明する。
- safe ZIP handling、path traversal rejection、unsafe symlink rejection、manifest / metadata / authority fields を説明する。
- tree fallback / local-context evidence は lower-authority evidence として扱い、EAL dispositionが必要だと説明する。

### DES-004: Existing workflow docs thin links

更新対象:

- `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_initiative.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
- 対応する `spec-dock/docs/` 配下の同名docs

責務:

- 長い手順は新規reference docsへ寄せ、既存workflow docsには薄い導線とstop gateだけを置く。
- `workflow_spec_authoring.md` は、ChatGPT outputもdelegated evidenceの一種であり、EAL + canonical rewrite + fresh `spec-reviewer` が必要だと示す。
- `workflow_initiative.md` は、InitiativeからEpic候補を作る場合のChatGPT evidence laneとhuman approval before Epic node creationを示す。
- `workflow_epic.md` は、EpicからIssue候補を作る場合のhuman approval before Issue node creation、Issue draft artifact handoff、relay no-per-Issue-PR policyを示す。
- `workflow_issue.md` は、Issue draft adoption、`validate issue-draft-adoption`、handoff-readyとexecution-readyの分離、validation pass is not reviewer passを示す。

### DES-005: Docs index

更新対象:

- `src/spec_dock/assets/spec_dock/docs/README.md` が存在する場合。
- `spec-dock/docs/README.md` が存在する場合。
- 存在しない場合は `guide.md` など既存indexの更新を検討する。

責務:

- 新しいChatGPT authoring pack docsへ到達できる導線を追加する。

## 4. Supported / deferred command contract

docsでsupportedとして説明してよいcommands:

- `authoring preflight github-sync`
- `authoring pack prepare`
- `authoring backend invoke`
- `authoring pack review`
- `authoring pack stage`
- `authoring validate initiative-epic-candidates`
- `authoring validate epic-issue-candidates`
- `authoring validate issue-draft-adoption`
- `authoring validate selected-skeleton-fill`
- `authoring approval check`

deferred / unsupported として説明するcommands:

- `authoring adopt`
- `authoring create-issues-from-zip`
- `authoring mark-reviewer-pass`
- `authoring set-authorized-profile`
- `authoring issue-execution-ready`
- `authoring pr-ready`

deferred commands はusage exampleに載せない。存在しない、または将来構想として触れる場合も、canonical adoption、Issue creation、reviewer pass、execution-ready、PR-readyを実行する手段として案内しない。

## 5. Evidence mode semantics

### `github-synced`

- repo-aware ChatGPT invocationのdefault mode。
- branch / commit / source manifest がGitHub connectorから参照可能であることを前提にする。
- GitHub上の状態を参照できる範囲だけがevidence対象である。

### `local-context`

- syncできない、またはsyncを使わない理由を明示して使うexplicit mode。
- local docs、diff summary、tree snapshot、artifactなどを明示添付する。
- `github_sync: not_verified` 相当のlower-authority evidenceとして扱う。
- `local-context` outputは、EAL採否、canonical rewrite、fresh reviewer gateなしに正本化できない。

## 6. Authority wording

docs全体で守る固定表現:

- ChatGPT / Oracle outputは evidence-only。
- runtime validation `pass` はcommand-local validation pass。
- review / stage / validate / approval check はcanonical docsを書き換えない。
- `.assurance.json`、`authorized_profile`、fresh reviewer pass、execution-ready、PR-ready、merge-ready、Issue finish、Epic completionはChatGPT authoring pack runtimeが主張しない。
- canonical docsのsingle-writerはmain orchestrator。

## 7. Failure modes

| ID | 失敗モード | 防止策 |
|---|---|---|
| FM-001 | 未実装commandをsupported usageとして載せる | supported / deferred command listをruntime helpで確認する |
| FM-002 | `local-context` を `github-synced` と同等に見せる | lower-authority evidence / explicit reason / EAL required と書く |
| FM-003 | validation `pass` を reviewer pass と誤読させる | command-local pass と明記する |
| FM-004 | provider docs と dogfooding mirror がずれる | providerとmirrorを同時更新し、差分点検する |
| FM-005 | C11でPR delivery / merge-readyを主張する | PR deliveryは`iss-00307`へdeferとreportに残す |

## 8. Plan handoff

実装計画は、docs-onlyを基本としつつ、runtime helpの文言が明らかに古い場合だけbehaviorを変えないtext-only correctionを許容する。

最終検証では、docs diff、runtime help smoke、deferred command wording grep、forbidden authority claim grep、`git diff --check`、`spec-dock validate`、fresh `spec-reviewer` passを必須にする。
