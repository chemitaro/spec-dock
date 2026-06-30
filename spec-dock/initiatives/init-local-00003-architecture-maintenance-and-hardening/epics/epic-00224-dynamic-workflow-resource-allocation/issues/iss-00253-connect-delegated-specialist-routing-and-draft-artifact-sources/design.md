---
種別: 設計書（Issue）
ID: "iss-00253"
タイトル: "Connect Delegated Specialist Routing And Draft Artifact Sources"
Issue Grade: "strict"
状態: "draft"
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

- `[N]` Issue `draft-design` / `draft-plan` は profile-aware branch を通る。
- `[N]` Assurance verification は write 前に完了する。
- `[N]` profile template validation は `assurance compose` と同等の filesystem guard を再利用する。
- `[N]` profile-sourced draft は legacy thin normalization を通さない。
- `[N]` draft artifacts は discussion evidence であり canonical docs ではない。

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
  -> assurance contract verify
  -> authorized_profile resolve
  -> profile template full markdown load
  -> provenance / draft frontmatter normalize without authority claim
  -> discussion file write
```

## 5. 失敗設計

- missing `.assurance.json`: fail with classification / compose guidance。
- invalid schema: fail without write。
- stale source binding: fail without write。
- unsupported profile / missing template / symlink escape / empty template: fail without write。
- file allocation failure: no canonical docs are modified。

## 6. 要件追跡

| 要件 | 設計 |
|---|---|
| AC-001 / AC-002 | Draft Profile Resolver |
| AC-003 | Assurance Contract Verifier + Profile Template Loader |
| AC-004 | Legacy Draft Router |
| AC-005 | bypass legacy thin normalization |
| AC-006 | provenance / authority guard |
| AC-007 | compose regression tests |

## 7. 非対象

- G2 は profile template 本文を再設計しない。
- G2 は specialist role skill を新設しない。
- G2 は readiness preflight の広範な修正を行わない。
