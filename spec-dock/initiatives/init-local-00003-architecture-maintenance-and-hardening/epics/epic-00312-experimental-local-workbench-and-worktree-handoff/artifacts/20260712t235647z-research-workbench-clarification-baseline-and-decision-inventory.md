---
種別: research
ID: "20260712t235647z-research"
タイトル: "Workbench Clarification Baseline And Decision Inventory"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-07-12"
親: ["epic-00312"]
関連: []
authority: "synthesized"
derived_from:
  - "Epic 00312 creation request and preceding ChatGPT-first workbench design discussion"
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/{requirement.md,design.md,plan.md}"
  - "epic-00259 / epic-00295 / epic-00107 canonical docs and evidence"
  - "src/spec_dock/cli.py"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/"
  - "tests/cli_runtime/test_worktree.py"
reflected_to: []
---

# 20260712t235647z-research Workbench Clarification Baseline And Decision Inventory

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約、用語衝突、edge case など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は artifact type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は source-grounded research evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- 事実、推測、未検証事項、用語衝突、edge case、判断への含意を混ぜない。
- local context で解ける疑問は人間に聞かず、この artifact に source-grounding を残す。

## 調査目的 (必須)
- Epic `epic-00312` の requirement / design / plan 具体化前に、会話で合意済みの Workbench 契約、現行 runtime の制約、未解決のユーザー判断を分離する。
- ローカル source で解ける事項を人間へ再質問せず、次の一問が downstream artifact を本当に変えるものか確認する。

## sources / 調査方法 (必須)
- 参照先:
  - active Epic `epic-00312` の scaffold と親 Initiative `init-local-00003` の canonical docs。
  - `epic-00259` の artifact domain 契約、`epic-00295` の ChatGPT authoring / local-context 契約、`epic-00107` の worktree runtime 契約。
  - `src/spec_dock/cli.py` の managed `.gitignore` fallback と recursive traversal。
  - runtime の filesystem repository、delete recovery、authoring source manifest、worktree application / command / presentation surface。
  - `tests/cli_runtime/test_worktree.py`、authoring / validate / init-update 系 tests。
- 検証手順:
  - `active show`、Git branch / status、GitHub Issue state、Epic / parent docs、artifact inventory、repository-wide `rg` を照合した。
  - `./spec-dock/scripts/spec-dock validate` が `nodes=204` で成功することを確認した。
- 実験条件:
  - 現在 branch は `main`。Epic scaffold以外の実装変更は行っていない。

## facts / 観測できた事実 (必須)
- `epic-00312` は `init-local-00003` 配下に作成され、GitHub Issue `#312` と連携し、active Epic に設定されている。
- 親 Initiative は source-of-truth、state boundary、runtime / scaffold / docs parity hardening を受け入れる open-ended architecture scope である。
- 既存 `epic-00259` と `epic-00107` は GitHub 上で closed。`epic-00295` は open だが ChatGPT authoring installed runtime を所有する別Epicである。
- 現在の managed `spec-dock/.gitignore` と installer fallback に `.workbench/` rule はない。
- 現在の metadata / legacy / recovery / source-manifest surface には broad recursive traversal があり、scope-local `.workbench/` を opaque subtree として prune する共通契約はない。
- 現在の `worktree create` は tracked Git tree と bootstrap を扱うが、ignored Workbench transfer は扱わない。
- 会話で次が合意済みである:
  - scope作成前・横断作業は `spec-dock/.workbench/YYYY-MM-DD/`。
  - scope固有作業は Initiative / Epic / Issue direct child の `.workbench/`。
  - fixed session tree / manifest DB / TTL daemon は導入しない。
  - Workbench は Git ignored、local-only、disposable、non-canonical。
  - scope / worktree delete 時に Workbench が消失してよく、delete blocker は設けない。
  - durable evidence は既存 `artifacts/`、adopted authority は canonical docs / accepted ADR / EAL。
  - raw ZIP は repository 外 quarantine で検査する。
  - Worktree作成時の自動copyは行わず、作成後にユーザー指示で専用 `workbench copy` command を実行する。
  - 初期 copy command は source=current worktree、scope ID 1件、target worktree 1件、no overwrite、no sync に限定する。

## inference / 推測 (必須)
- 事実から推測したこと:
  - Epicは3 Issue程度（reserved subtree safety、experimental copy command、dogfood/docs/final gate）で閉じられる。
  - Runtime scanner safetyを先に実装しないと、scope-local Workbenchの正式dogfoodは開始できない。
  - Copy commandの主要な未決契約は「Workbench内のどのfile kindを忠実にコピーするか」である。
- 推測の根拠:
  - Workbenchは低摩擦で雑に使うことが主要目的だが、過去案にはtext-only / secret scan / size capという安全制約も含まれ、両者は受け入れ条件と実装量を大きく変える。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - `.workbench/` ignore patternのroot / nested全階層での実動作。
  - 全recursive walkerの完全inventoryと共通prune設計。
  - Workbench copyの実ファイル構成、容量、binary / image / archive利用頻度。
  - Target worktree identityの最終CLI表現。
- 確認できない理由:
  - Epicはclarification開始直後であり、実装fixtureとdogfood corpusはまだ存在しない。

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - Experimental `workbench copy` を、symlink / special fileだけ拒否して通常fileを形式不問で忠実にコピーするか、text allowlist / secret scan / strict size capを初期必須にするか。
- pressure-test question として切り出すべき候補:
  - 上記は「雑に使える」主要目的と安全・実装コストの境界を決め、requirement / design / tests / Issue 2 scopeを変えるため正式質問にする。
- 質問せずに解決できた候補:
  - Workbench配置、root日付形式、session不要、delete時消失、copyの明示実行、単一scope copy、no overwrite / no sync、既存Epic再利用可否は会話とrepository factsで解決済み。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - `promotion`: Workbenchからtracked artifactへの保存と、artifactからcanonical authorityへの採用を同じ語で呼ぶと混同する。
  - `copy` / `sync`: Workbench transferは一回の独立snapshotであり継続同期ではない。
- 既存 docs / code / tests / artifacts / primary sources での使われ方:
  - 既存 artifact workflowはevidenceとcanonical adoptionを分離する。Worktree runtimeはlinked checkoutの作成・削除を扱うがignored payload同期を持たない。
- 判断が必要な理由:
  - Canonical docsでは `workbench copy`、`artifact capture`、`canonical adoption` を別の状態変化として固定する必要がある。

## edge cases / 具体シナリオ (必須)
- edge case:
  - Workbench内にcopied projectの`.meta.json`があり、metadata scannerが偽nodeとして読む。
  - Source / targetの同一scope Workbenchが両方存在し、copyが暗黙mergeする。
  - Workbenchにimage、binary、archive、private key、symlink、巨大logが混在する。
  - Copy後にsource / targetが独立変更され、どちらが正本かという誤認が生じる。
- その edge case が requirement / design / plan に与える影響:
  - Runtime-wide prune、no overwrite、no sync、local-only authority、copy対象file policyをcross-Issue invariantとして固定する必要がある。

## implications / 判断への含意 (必須)
- Requirementは低摩擦、disposable、Git ignored、explicit copy、authority境界を主要目的として固定する。
- Designは`.workbench/`をreserved opaque subtreeとして一元的にpruneし、copyを独立snapshotとして扱う。
- Planはsafety foundationをcopy commandより先に置き、dogfood/docsを最終Issueで統合する。
- Copy対象file policyへのユーザー回答が得られるまで、Issue 2の安全要件とtest matrixは確定できない。

## リスク/制約 (任意)
- 過度な安全catalogはWorkbenchの低摩擦性を損ない、過度に自由なcopyは秘密情報や巨大payloadを別worktreeへ複製しうる。
- WorkbenchはGitHub connectorから不可視であり、共有・レビュー・正本化が必要な内容はartifact化とcommit / pushが必要である。

## 反映先 (任意)
- reflected_to:
  - `epic-00312/requirement.md`
  - `epic-00312/design.md`
  - `epic-00312/plan.md`
  - `epic-00312/report.md` Evidence Adoption Ledger / Spec Authoring Gate

## 参考（References） (任意)
- `spec-dock/docs/workflow_clarification.md`
- `spec-dock/docs/authoring/decision-routing.md`
- `spec-dock/docs/authoring/scope-layering.md`
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00259-artifacts-directory-future-only-adoption/`
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00295-chatgpt-authoring-pack-installed-runtime/`
