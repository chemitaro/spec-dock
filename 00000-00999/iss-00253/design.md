---
種別: 設計書（Issue）
ID: "iss-00253"
タイトル: "Connect Delegated Specialist Routing And Draft Artifact Sources"
Issue Grade: "strict"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Plan: ["plan.md"]
関連Report: ["report.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00253 Connect Delegated Specialist Routing And Draft Artifact Sources — Issue 設計書（Strict）

## 1. Strict とする理由

`new doc draft-design` / `draft-plan` は delegated specialist の入力 artifact を作る workflow surface であり、template contract と runtime command behavior に影響するため strict とする。

## 2. 設計要約

- `[N]` Issue `draft-design` / `draft-plan` だけを profile-aware branch に通す。
- `[N]` `.assurance.json` は `AssuranceStore.verify_contract()` で discussion filename allocation 前に検証する。
- `[N]` profile template は `ArtifactStore.load_profile_artifact_template()` を使い、`assurance compose` と同じ filesystem guard を再利用する。
- `[N]` profile-sourced draft は legacy thin normalization を通さない。
- `[N]` `draft-requirement` と Initiative / Epic `draft-design` / `draft-plan` は既存 routing を維持する。
- `[N]` draft artifacts は discussion evidence であり canonical docs、reviewer pass、phase completion、implementation readiness を自己主張しない。

## 3. コンポーネント

| Component | 責務 | 配置候補 |
|---|---|---|
| Draft Profile Resolver | Issue draft design/plan の profile source を決定する | `application/create_node.py` |
| Assurance Contract Verifier | `.assurance.json` の schema / source binding / stale を確認する | `infra/assurance_store.py` |
| Profile Template Loader | full markdown template を安全に読む | `infra/artifact_store.py` |
| Draft Writer | issue `discussions/` へ1ファイルだけ書く | existing create doc flow |
| Legacy Draft Router | requirement / initiative / epic の既存 draft path を維持する | existing create doc flow |

## 4. Flow

```text
new doc draft-design/draft-plan --issue <id>
  -> target issue lookup
  -> if scope.kind == issue and doc_type in {draft-design, draft-plan}
       -> AssuranceStore.resolve_issue_target(scope.id)
       -> AssuranceStore.verify_contract(target)
       -> fail if status != valid
       -> profile = contract.classification.authorized_profile.value
       -> artifact = design | plan
       -> ArtifactStore.load_profile_artifact_template(artifact, profile)
       -> use profile template body as render source
     else
       -> existing scope canonical template route
  -> discussion filename allocation
  -> render replacements
  -> skip legacy thin normalization for profile-sourced drafts
  -> discussion file write
```

## 5. 失敗設計

- missing `.assurance.json`: fail with classification / compose guidance。
- invalid schema: fail without write。
- stale source binding: fail without write。
- unsupported profile / missing template / symlink escape / empty template: fail without write。
- file allocation failure: no canonical docs are modified。
- fail-closed は discussion filename allocation 前に発生させ、失敗時に new discussion file を残さない。
- missing / invalid / stale assurance で Standard fallback を作らない。
- `.assurance.json` を silent repair しない。

## 6. 要件追跡

| 要件 | 設計 |
|---|---|
| AC-001 / AC-002 | Draft Profile Resolver |
| AC-003 | Assurance Contract Verifier + Profile Template Loader |
| AC-004 | Legacy Draft Router |
| AC-005 | bypass legacy thin normalization |
| AC-006 | provenance / authority guard |
| AC-007 | compose regression tests |

## 7. Runtime Interface Contract

| Input | Expected result |
|---|---|
| Issue `new doc draft-design` with valid Standard / Strict / Critical contract | `templates/issue-profiles/<authorized_profile>/design.md` に由来する Issue discussion draft を1件作成する |
| Issue `new doc draft-plan` with valid Standard / Strict / Critical contract | `templates/issue-profiles/<authorized_profile>/plan.md` に由来する Issue discussion draft を1件作成する |
| Issue `new doc draft-design` / `draft-plan` without valid contract | non-zero failure; no new discussion file |
| Issue `draft-requirement` | existing `templates/issue/requirement.md` route |
| Initiative / Epic `draft-design` / `draft-plan` | existing `templates/<scope>/design.md` / `plan.md` route |

## 8. 実装境界

- command layer は `new doc` の引数 contract を変更しない。
- application layer は scope / doc_type によって profile-aware route と legacy route を分ける。
- infra layer は `.assurance.json` と profile template の filesystem validation を担う。
- domain layer へ filesystem store を持ち込まない。
- `new doc` で canonical `design.md` / `plan.md` / `.assurance.json` を更新しない。

## 9. 非対象

- G2 は profile template 本文を再設計しない。
- G2 は specialist role skill を新設しない。
- G2 は readiness preflight の広範な修正を行わない。
- G2 は G3 の Evidence Adoption Ledger enforcement や G4 smoke matrix 実装を行わない。
