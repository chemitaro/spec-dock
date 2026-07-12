---
種別: research
ID: "20260708-chatgpt-use-planning-evidence-summary"
タイトル: "ChatGPT Use Planning Evidence Summary"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
親: ["iss-00300", "epic-00295", "init-local-00003"]
authority: "evidence_only"
adoption_status: "unreviewed"
reflected_to: []
---

# ChatGPT Use Planning Evidence Summary

## Purpose

`iss-00300 Backend Invocation Adapter` の正式な `requirement.md` / `design.md` / `plan.md` を作成するために、ChatGPT Use / GPT-5.5 Pro Extended で生成した planning package を evidence-only input として要約する。

この artifact は canonical docs ではない。Codex orchestrator が採用判断を `report.md` に記録し、`spec-reviewer` gate を通すまで、reviewer pass、execution-ready、PR-ready、PR delivery は主張しない。

## Session Evidence

| 項目 | 値 |
| --- | --- |
| Oracle slug | `iss-00300-planning` |
| Model | `gpt-5.5-pro` |
| ChatGPT label | `Pro Extended` |
| Status | `completed` |
| Started | `2026-07-07T20:27:28Z` |
| Completed | `2026-07-07T20:38:54Z` |
| Input tokens | `59356` |
| Output tokens | `13871` |
| Total tokens | `73227` |
| Transcript SHA-256 | `43f051e99fd682afbf7b970649f83f482380a1233e4aecf339eb0191d2f998e6` |
| Transcript bytes | `63496` |

## Attached Inputs

- `spec-dock/active/epic/requirement.md`
- `spec-dock/active/epic/design.md`
- `spec-dock/active/epic/plan.md`
- `spec-dock/active/issue/requirement.md`
- `spec-dock/active/issue/design.md`
- `spec-dock/active/issue/plan.md`
- `spec-dock/active/issue/report.md`
- `spec-dock/active/issue/artifacts/20260707t171251z-draft-requirement-implement-backend-invocation-adapter-draft-requirement.md`
- `spec-dock/active/issue/artifacts/20260707t171251z-01-draft-design-implement-backend-invocation-adapter-draft-design.md`
- `spec-dock/active/issue/artifacts/20260707t171252z-draft-plan-implement-backend-invocation-adapter-draft-plan.md`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/authoring.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/pack_prepare.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/prompt_pack_contract.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/authoring_pack/pack_prepare_renderer.py`
- `tests/cli_runtime/test_authoring.py`

## Adopted Planning Claims

- `authoring backend invoke` を deferred command から implemented installed runtime command へ昇格する。
- backend command は `--backend-command`、`SPECDOCK_CHATGPT_COMMAND`、optional compatibility fallback `ORACLE_CHATGPT_COMMAND` の順で解決する。
- command string は `shlex.split(..., posix=True)` 相当で argv 化し、shell execution は使わない。
- backend command 未設定、malformed command、missing prompt pack、unsafe output target、backend non-zero、timeout は fail-closed に扱う。
- `--dry-run` は backend process を起動せず、resolved command と invocation summary だけを出力する。
- stdout / stderr / diagnostics summary では secret-looking data と host-local absolute path を redact する。
- `local-context` は lower authority evidence として扱い、explicit EAL disposition なしに canonical adoption や execution-ready を主張しない。
- 中間 Issue として PR delivery は行わず、final quality gate / PR delivery は `iss-00307` に defer する。

## Rejected Or Deferred Claims

- backend provider registry はこの Issue では実装しない。
- ZIP review / stage / extraction は `iss-00301` 以降へ defer する。
- candidate validation、draft adoption validation、approval stop gate は後続 Issue へ defer する。
- `.assurance.json` mutation、`authorized_profile` 決定、reviewer pass、execution-ready、PR-ready、PR delivery の claim はこの evidence からは採用しない。
- `ORACLE_CHATGPT_COMMAND` fallback の deprecation schedule はこの Issue では決めず、Epic-level open question として残す。

## Adoption Destination

- `requirement.md`: purpose、scope、non-scope、functional requirements、acceptance criteria、failure modes。
- `design.md`: runtime responsibility split、CLI contract、command resolution、prompt pack validation、subprocess adapter、redaction、presentation、compatibility script boundary。
- `plan.md`: implementation milestones、closure index、tests、verification commands、PR delivery defer policy。
- `report.md`: Evidence Adoption Ledger、Spec Authoring Gate、Reviewer Gate Status、PR Delivery Defer Evidence。
