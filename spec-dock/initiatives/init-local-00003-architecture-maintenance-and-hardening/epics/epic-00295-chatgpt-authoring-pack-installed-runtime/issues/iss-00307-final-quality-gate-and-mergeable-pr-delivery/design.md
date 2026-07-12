---
種別: 設計書（Issue）
ID: "iss-00307"
タイトル: "Final Quality Gate PR Delivery"
関連GitHub: ["#307"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
依存: ["requirement.md"]
親: ["epic-00295", "init-local-00003"]
authorized_profile: "standard"
---

# iss-00307 Final Quality Gate PR Delivery — Issue 設計書

## 1. 設計結論

このIssueは、Epic 00295の実装機能を追加するIssueではなく、Epic全体のclosure / repair / PR delivery gateである。設計は次の6 gateに分ける。

| Gate | 目的 | 主な証跡 |
|---|---|---|
| G1 Closure Index Gate | C01〜C11の完了、deferred PR delivery、依存、blocking gapを確認する | Issue一覧、report確認、dependency確認 |
| G2 Installed Surface Gate | provider-side source of truthからconsumer repoへinstalled assetsが届くことを確認する | `uvx --isolated --from <absolute-repo-path> spec-dock init <tmp>`、installed file checks |
| G3 Runtime Contract Gate | `authoring` command groupとhelp / dispatch / status outputを確認する | help smoke、deferred command fail-closed |
| G4 Evidence Safety Gate | backend、preflight、local-context、ZIP、stage、validators、approvalのauthority boundaryを確認する | pytest、fixture/manual command output |
| G5 Docs / Skill Consistency Gate | docs、skills、runtime help、testsのcommand inventoryとauthority wordingを一致させる | grep / inspection / reviewer |
| G6 PR Delivery Gate | main同期、full gate再実行、PR作成、CI/reviewer/PR review repair loopを通す | PR URL、checks、reviewer findings、repair evidence |

各gateは`report.md`に観測結果を残す。`pass`と書けるのは実行・観測した証跡がある場合だけであり、ChatGPT提案やdraft artifactだけではpassにしない。

## 2. 正本と責任境界

| 種別 | パス / surface | 責任 |
|---|---|---|
| Provider source of truth | `src/spec_dock/assets/spec_dock/**`, `src/spec_dock/assets/install_root/**` | shipped runtime / docs / skillsの正本 |
| Dogfooding mirror | `spec-dock/**`, repo root `.agents/**` | local validation target。正本ではない |
| Runtime CLI | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**` | installed command behavior |
| Compatibility helpers | `src/spec_dock/assets/spec_dock/scripts/authoring-pack/**` | standalone helper / compatibility surface |
| Canonical SpecDock docs | active Epic / Issue docs | main orchestratorが採用・更新する正本 |
| ChatGPT / Oracle output | Issue artifact / staged evidence | evidence-only。正本・reviewer pass・readinessを主張しない |
| PR delivery | GitHub PR | final Issueでのみ実施するdelivery gate |

## 3. Local wrapper dependency audit

SpecDockはChatGPT / Oracle automation本体を内包しない。正式workflow / runtime / shipped docsは、個人PC固有のwrapper pathに依存してはならない。

検証対象:

- `src/spec_dock/assets/**`
- `spec-dock/docs/**`
- `spec-dock/scripts/**`
- repo root `.agents/skills/**`
- tests / docsでbackend command contractを説明する箇所

期待:

- `/Users/...` や `.codex/skills/chatgpt-use/scripts/oracle-chatgpt` が必須依存としてshipped surfaceに残っていない。
- local wrapperに触れる場合は、利用者が指定できるbackend exampleとしてのみ説明する。
- runtimeはbackend commandを `--backend-command`、`SPECDOCK_CHATGPT_COMMAND`、optional `ORACLE_CHATGPT_COMMAND` の順に解決する。
- 未設定時はfail-closedし、`SPECDOCK_CHATGPT_COMMAND` または `--backend-command` を設定するよう明確に案内する。
- backend argv / summary / path はsecret-like valueやhost-local pathを不要にdurable evidenceへ残さない。

## 4. Branch / PR readiness design

ChatGPT UseのGitHub connector観測では、現在branchは`main`に対してbehind / divergedの可能性がある。final PR readiness前にlocalで以下を確認する。

- `git fetch origin`
- `git rev-list --left-right --count origin/main...HEAD`
- 必要に応じて `git merge origin/main` または同等の安全なmain取り込み
- main取り込み後のfull final gate再実行

PR readinessは次の証跡が揃うまで主張しない。

- branch pushed
- PR URL
- selected base branch
- latest head SHA
- CI/check status
- reviewer status
- unresolved review threads / merge conflicts / visible blockersの有無
- repair loop結果

## 5. Evidence safety design

Epic 00295の中心は、ChatGPTに大きなplanning evidenceを作らせつつ、SpecDock正本権限を越えさせないことである。final gateは以下を確認する。

- runtime validation `pass` はcommand-local validation passである。
- ZIP / tree / staged evidenceは `authority: evidence_only` である。
- `bundle_generation_not_promotion: true` が維持される。
- `authorized_profile` decision、reviewer pass、execution-ready、PR-ready、merge-readyなどのforbidden authority claimは拒否される。
- pack stage / validators / approval checkはcanonical docs、`.assurance.json`、Issue node、reviewer resultを変更しない。

## 6. Reviewer / QA design

このIssueはfinal delivery Issueであるため、実装計画の承認後に次のgateを通す。

- planning `spec-reviewer`: requirement / design / plan / reportの実行可能性とEpic traceを確認する。
- final `spec-reviewer`: Epic requirement / design / plan、Issue report、docs / skills / runtime behaviorの整合を確認する。
- final `code-reviewer`: Epic全体のruntime / tests / scaffold / docs diffを確認する。
- final `qa-reviewer`: final test matrix、manual dogfood scenario、CI / PR observation十分性を確認する。

reviewerのP1以上は修正し、fresh re-reviewを通す。waiverはユーザーの明示的risk acceptanceがない限り使わない。
