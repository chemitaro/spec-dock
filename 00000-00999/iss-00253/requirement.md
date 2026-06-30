---
種別: 要件定義書（Issue）
ID: "iss-00253"
タイトル: "Connect Delegated Specialist Routing And Draft Artifact Sources"
関連GitHub: ["#253"]
Issue Grade: "strict"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
親: ["epic-00224", "init-local-00003"]
---

# iss-00253 Connect Delegated Specialist Routing And Draft Artifact Sources — Issue 要件定義

## 1. 目的

classified Issue の `draft-design` / `draft-plan` が `.assurance.json` の `authorized_profile` に対応する profile template を source とし、delegated specialist が canonical artifact と同じ構造で draft evidence を作れるようにする。

## 2. 背景

`new doc draft-design` / `draft-plan` は現在も機能するが、Issue scope では `templates/issue/design.md` / `templates/issue/plan.md` の compose-before placeholder を入口にし、薄い独自 draft へ正規化している。これは Issue #247 の profile template pack と grade-aware authoring rules に反する。

## 3. 観測可能な成果

- classified Standard / Strict / Critical Issue の `draft-design` は対応する `issue-profiles/<profile>/design.md` の構造を持つ。
- classified Standard / Strict / Critical Issue の `draft-plan` は対応する `issue-profiles/<profile>/plan.md` の構造を持つ。
- missing / invalid / stale `.assurance.json` では no-write fail-closed になる。
- `draft-requirement` は従来通り common issue requirement template を使う。
- Initiative / Epic の `draft-design` / `draft-plan` は従来挙動を維持する。
- generated discussion draft は authority / adoption / reviewer pass / phase completion / implementation readiness を自己主張しない。

## 4. スコープ

対象:

- `application/create_node.py`
- `cli/bootstrap.py`
- `infra/assurance_store.py`
- `infra/artifact_store.py`
- `tests/cli_runtime/test_new.py`
- profile template validation reuse
- issue discussions docs / rules

対象外:

- readiness classifier の本体修正（R0）
- grade matrix wording の初期導入（G1）
- evidence gate enforcement（G3）
- role skill の新規 shipped asset 化

## 5. 親 Epic との対応

- `E-RQ-022`
- `E-AC-022`
- Epic design: `Profile Template Resolver`, `Template Materializer`, `Issue Draft Authoring Router`
- Epic plan: `G2`

## 6. 受け入れ条件

- AC-001: Issue `draft-design` は verified `.assurance.json` の `authorized_profile` から profile design template を選ぶ。
- AC-002: Issue `draft-plan` は verified `.assurance.json` の `authorized_profile` から profile plan template を選ぶ。
- AC-003: missing / invalid / stale / unsupported profile / missing template / empty template は discussion path allocation 前に失敗する。
- AC-004: Issue `draft-requirement` と Initiative / Epic draft docs は既存挙動を維持する。
- AC-005: legacy thin draft normalization は Issue profile-sourced design / plan に適用されない。
- AC-006: generated draft frontmatter / body は canonical authority や reviewer pass を主張しない。
- AC-007: existing `assurance compose` profile template behavior は退行しない。

## 7. 制約

- template selection authority は `authorized_profile` のみである。
- fail-closed 時に Standard fallback を作らない。
- `.assurance.json` を silent repair しない。
