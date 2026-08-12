---
種別: review
ID: "20260812t150257z-review"
タイトル: "Issue 359 Final Quality Gate"
状態: "approved"
作成者: "main orchestrator"
最終更新: "2026-08-13"
親: ["iss-00359"]
authority: "evidence"
reflected_to: ["report.md"]
---

# Issue 359 Final Quality Gate

## Gate policy

- stepごとのreviewは実施せず、実装・仕様・testが揃った後のS99だけを包括的品質gateとした。
- ChatGPT / Oracleは使用していない。
- P0 / P1だけをmerge blockerとし、P2 / P3は非blockerとしてR/D/P/companionへ統合していない。
- planning、canonical migration、CI証跡、publication、Issue #360の責務へscopeを拡張していない。

## Reviewed scope

- provider / dogfoodの二skill treeとparity
- recognized explicit-only policy metadata
- Current CLI side-effect classificationとgrillのwrite boundary
- collision-safe additive materialization
- no-follow / device / inode / `ctime_ns`-pinned Artifact finalizer
- Codex developer instructionsの旧workflow責務削除
- canonical Requirement / Design / Plan、companion、report、test

## Findings and repair loop

1. PR #363 reviewのP1三件を修正した。
   - explicit invocation policy
   - additive skill ownership
   - Artifact finalization TOCTOU
2. S99 Standards軸がpreflight-to-copy path swapをP1として検出した。
   - additive対象をgeneric `copy2`から分離し、descriptor-relative `O_NOFOLLOW`と`O_CREAT | O_EXCL`、no-follow final verificationへ変更した。
3. S99 Spec軸がbyte-identical hard-linked regular fileの過剰拒否をP1として検出した。
   - existing adoptionはread-onlyのためlink-count拒否を外し、新規作成fileだけ書込前に`nlink=1`を要求した。
4. S99後のrequired Provider CIが、Linuxでunlink直後の同名fileへinodeが再利用されるP1相当の安全blockerを検出した。
   - finalizer identityへ`ctime_ns`を追加し、lstat / open / fstatの三値が一致する場合だけtruncateするよう修正した。
   - deterministicなctime mismatch testを追加した。これは新しいreview gateではなく、同じ最終gateのrequired CI closureである。

## Verification

- skill-local finalizer contract: `6 passed`
- Issue 359 focused contract: `21 passed`
- `make lint`: ruff check / format / mypy pass
- ordinary `uv run pytest -q`: `1648 passed, 2200 skipped`
- `spec-dock sync`: pass
- `spec-dock validate`: pass、`nodes=221`
- affected full-regression diagnosis: `558 passed, 28 failed`。28件は旧workflow文書、退役済みruntime/API、旧planning asset等の既存契約であり、Issue 359のfocused testには失敗なし。

## Final verdict

| Axis | P0 | P1 | Status |
|---|---:|---:|---|
| Standards / safety | 0 | 0 | pass |
| Specification | 0 | 0 | pass |

local最終判定は`pass`。Issue 359のscope内に未解消P0 / P1はない。latest-headのrequired CIとCodex review完了はpush後のPR観測で確定する。
