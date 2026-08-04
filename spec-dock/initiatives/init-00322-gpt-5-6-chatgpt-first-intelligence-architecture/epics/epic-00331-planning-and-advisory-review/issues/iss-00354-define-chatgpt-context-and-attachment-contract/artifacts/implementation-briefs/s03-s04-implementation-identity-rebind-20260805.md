# iss-00354 S03/S04 実装ブリーフ — Identity Rebind Addendum

> 本 addendum は source identity の再結合だけを行う。元ブリーフの実装 scope、不変条件、allowlist、検証項目および停止条件は変更しない。

## Current identity

| 項目                         | 値                                                       |
| -------------------------- | ------------------------------------------------------- |
| Repository                 | `chemitaro/spec-dock`                                   |
| Branch                     | `codex/iss-00354-chatgpt-context-contract`              |
| Current source HEAD        | `f2238d12313b36a002185d3e101154c20f19993c`              |
| GitHub connector 確認        | named branch と指定 SHA は `identical`、ahead `0`、behind `0` |
| Original brief source HEAD | `8b44eb6da5d8be4f2178ce3be09d25e968f14747`              |
| Default branch fallback    | 使用していない                                                 |

Current HEAD の commit identity は GitHub 上でも `f2238d12313b36a002185d3e101154c20f19993c` である。

## Docs-only lineage

GitHub connector による `8b44eb6da5d8be4f2178ce3be09d25e968f14747...f2238d12313b36a002185d3e101154c20f19993c` の比較結果は、ahead `2`、変更対象は次の四パスだけである。

* `<issue-root>/report.md`
* `<issue-root>/artifacts/implementation-briefs/s03-input-path-model-v2.md`
* `<issue-root>/artifacts/implementation-briefs/s03-s04-atomic-implementation-brief-20260805.md`
* `<issue-root>/artifacts/implementation-briefs/s04-direct-attachment-transport.md`

Canonical `requirement.md`、`design.md`、`plan.md`、provider runtime 3ファイル、対象 tests、provider projection、Review resourceには差分がない。現在の relevant sourceにも、元ブリーフが対象とした bytes/exact-attachment contract、generated prompt-pack transport、旧 Review identity attachment wordingがそのまま存在する。

## Brief validity and atomic binding

元の S03/S04 atomic implementation brief を、source HEAD だけ `f2238d12313b36a002185d3e101154c20f19993c` へ再結合する。Production/test contract に変更がないため、path-only producer、direct repeated `--file` consumer、Review identity の minimal-body binding、union allowlist、read/run-only 境界、禁止事項、必須検証および停止条件は、そのまま有効である。   

将来の resulting implementation HEAD は未確定である。`cl-s03-path-input` / `tc-s03-001` と `cl-s04-direct-transport` / `tc-s04-001` は、同一 resulting HEAD、同一 pushed branch、同一後続確認対象に結び付ける。S03 または S04 の片側だけを Green、commit candidate、closure、rollback unit として扱わない。

## Worker preconditions

実装開始直前に worker は次を再確認する。

1. Named branch が引き続き exact HEAD `f2238d12313b36a002185d3e101154c20f19993c` であり、default branch fallback を使用していないこと。
2. Scope 外の既存 worktree change がなく、必要な変更を atomic S03/S04 change-set として隔離できること。
3. Provider runtime、tests、provider projection、Review resourceが上記 baselineから変更されていないこと。Production/test差分が先行している場合は、この addendum を流用せず停止すること。
4. 元ブリーフの write allowlist、read/run-only境界、provider-owned sync機構、focused suite、legacy-symbol search、projection parity、および same-resulting-HEAD 条件を変更せず適用できること。

## GPT-5.6 Luna / Reasoning Effort Max

* `GPT-5.6 Luna`: **実測未確認**
* `Reasoning Effort Max`: **実測未確認**

既存 report と元ブリーフにも Luna / Max の成功 receipt は存在しない。記録済みの requested `gpt-5.6`、target `GPT-5.6 Sol`、resolved label `Pro`、strategy `current`、`verified=no` は、Luna / Max の実測証跡として扱わない。 
