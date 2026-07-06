---
kind: chatgpt-use-planning-refresh-summary
issue: iss-00284
source_session_slug: required-repository-connector-context-github-2
source_transcript_sha256: d457974f114fa9a0d1a6105ac7ac67e5d61bc3c5ea99cafc60aaebfb453d6f20
source_transcript_lines: 1954
adoption_status: adopted
authority: evidence_only
created_at_utc: 2026-07-06T17:18:12Z
---

# ChatGPT Use planning refresh summary

この artifact は、ChatGPT Use session `required-repository-connector-context-github-2` の採用判断を repo 内で監査可能にするための要約証跡である。raw transcript はホストローカルの Oracle session artifact であり、正本でも durable repo evidence でもない。

## 採用した内容

- `iss-00284` は ZIP intake ではなく、事前確認と prompt-pack 作成に scope を限定する。
- prompt-pack 生成前に repo / ref / source paths / source hashes / `stale_if` / denylist / assurance snapshot を固定する。
- `.assurance.json` と `authorized_profile` は observation-only とし、ChatGPT の推奨や self-review では変更しない。
- prompt-pack は `authority: evidence_only`、`adoption_status: unreviewed`、`bundle_generation_not_promotion: true` を明示する。
- status taxonomy は `pass` / `fail` / `blocked` / `stale` / `rejected` / `deferred` とし、`unreviewed` は adoption state として分離する。
- valid / invalid fixture と focused pytest で、missing source、missing assurance、unsafe claim、stale hash を fail-closed に確認する。
- この Issue 単独では Pull Request を作成せず、最終 Issue `iss-00293` に Epic-level PR delivery を集約する。

## 採用時に補正した内容

- ChatGPT 出力では初期実装先が `manual-tests/authoring-pack/` とされていたが、`manual-tests/README.md` は README 以外の tracked manual test workspace / fixture / evidence を禁止している。
- main orchestrator は、tracked script を `scripts/authoring-pack/prepare_chatgpt_authoring_pack.py`、fixtures を `tests/fixtures/authoring_pack/**`、tests を `tests/manual_tests/test_prepare_chatgpt_authoring_pack.py` に置く方針へ補正した。
- `manual-tests/**` は untracked trial workspace 用のままとし、この Issue の tracked implementation path から除外する。
- ChatGPT self-review / reviewer focus は formal `spec-reviewer` pass として扱わない。

## 採用しなかった内容

- ZIP intake、ZIP schema validation、staged rendering、profile skeleton fill validation は `iss-00285` 以降へ分離する。
- 配布 runtime command への昇格はこの Issue で行わない。
- raw transcript、ChatGPT conversation URL、ホストローカル path は canonical evidence として参照しない。

## 使用先

- `iss-00284` `report.md` の Evidence Adoption Ledger。
- `iss-00284` の fresh `spec-reviewer` gate。
- 実装時の allowed / forbidden path 判断。
