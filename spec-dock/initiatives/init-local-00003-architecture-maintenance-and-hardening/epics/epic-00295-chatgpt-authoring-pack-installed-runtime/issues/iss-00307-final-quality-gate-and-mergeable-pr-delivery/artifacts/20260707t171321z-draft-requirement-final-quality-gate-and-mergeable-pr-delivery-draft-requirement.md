---
種別: 要件定義書（Issue）
ID: "iss-00307"
タイトル: "Final Quality Gate PR Delivery"
関連GitHub: ["#307"]
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
親: ["epic-00295", "init-local-00003"]
---

# C12 final quality gate と mergeable PR delivery を実施する — draft requirement

## Purpose

Epic 00295 全体を installed runtime / installed skills として dogfood し、final quality gate、manual tests、reviewer / CI / PR review repair loop を通して一つの mergeable PR を作る。

## Parent Epic trace

- Parent Epic: `epic-00295` `ChatGPT Authoring Pack Installed Runtime`
- Repository: `chemitaro/spec-dock`
- Branch: `codex/authoring-pack-installed-runtime`
- Epic path: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00295-chatgpt-authoring-pack-installed-runtime/`
- Trace requirement groups: skill taxonomy、runtime command surface、GitHub sync/evidence mode、ZIP safety、candidate validation、approval boundary、relay delivery。
- Authority: this draft is evidence-only and is not canonical Issue docs until adopted through `spec-dock-issue-planning` `draft-adoption` mode.

## Scope

- C01〜C11 の completion evidence を確認する。
- installed repo simulation と `spec-dock init/update` asset verification を行う。
- `authoring` commands の help、preflight、local-context fixture、pack prepare、backend dry-run、pack review/stage、validators、approval check を確認する。
- deferred command absence / fail-closed behavior を確認する。
- full test / lint / validation、manual scenario、docs consistency を実行する。
- reviewer / CI / PR review findings を修正し、Epic 単位の mergeable PR を作成する。

## Non-scope

- C01〜C11 で deferred とした新機能を追加実装すること。
- per-Issue PR delivery の作成。
- ChatGPT output に reviewer pass / PR readiness を主張させること。
- merge そのものの実行を ChatGPT evidence として主張すること。

## Requirements

- final Issue は Epic-wide final quality gate と PR delivery の唯一の Issue である。
- 全 preceding Issues は deferred PR delivery evidence を持って finish していることを確認する。
- manual tests、automated tests、docs consistency、installed asset verification を記録する。
- reviewer / CI / PR review repair loop を完了させる。
- mergeable PR URL と readiness evidence を finish evidence に含める。

## Acceptance criteria

- `./spec-dock/scripts/spec-dock validate` が通る、または未通過項目が明確な repair queue として解消されている。
- `git diff --check` が通る。
- related pytest / cli_runtime tests と manual scenarios が記録される。
- installed skill / runtime asset simulation が通る。
- unsafe ZIP rejection、forbidden claim rejection、candidate validation、issue draft adoption validation、approval check の evidence がある。
- C01〜C11 の no-per-Issue-PR relay evidence が確認される。
- mergeable PR が作成され、reviewer / CI / PR review 指摘への repair evidence が残る。

## Evidence expectations

- Implementation or doc changes must produce a machine-readable or reviewer-readable finish evidence bundle.
- Evidence must keep `authority: evidence_only` for ChatGPT-derived draft/stage outputs.
- Forbidden authority claims must be absent: canonical adoption、`.assurance.json` mutation、authorized profile、fresh reviewer pass、execution-ready、PR-ready。
- Verification output must distinguish validation pass from adoption/reviewer pass.
- この Issue は final quality gate / PR delivery Issue であり、Epic 全体で唯一の mergeable PR delivery を担う。

## Suggested grade

- Suggested grade: final-quality-gate / PR-delivery（最終 Issue）
