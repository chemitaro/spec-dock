---
種別: レポート（Epic）
ID: "epic-00384"
タイトル: "Provider Test Strategy Simplification and Execution Cost Reduction"
関連GitHub: ["#384"]
最終更新: "2026-09-01"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["init-local-00003"]
---

# Result Summary

詳細: [Report Guide](../../../../docs/authoring/report.md)

## Outcome

- Epic #384をactive Epicとして維持し、planning branch `codex/epic-00384-provider-test-strategy-planning`で具体化した。
- root-cause researchとaccepted ADR `20260831t005139z-adr`により、4 disposable roots、2 fixed skill slots、user data protection、external rerun convergenceを確定した。
- 旧10-Issue案をvertical-slice / merge-point safetyの観点で再評価し、同じChatGPT 5.6 Pro Strict会話とlocal evidenceの双方で`ONE_ISSUE`と判断した。
- Product定義として、Issueは実装とその検証を一体で完了・受入する一つの実装ユニットであり、調査・分析・意思決定だけのIssueは成立しないと確定した。
- #388〜#390の判断を実装前のEpic authoringへ吸収し、accepted ADR `20260831t152024z-adr-single-implementation-unit-and-provider-hard-cutover-policy.md`へ正本化した。
- 唯一のimplementation-and-verification IssueとしてGitHub #392 / `iss-00392 Provider Lifecycle And Regression Gate Hard Cutover`を作成し、Requirement / Design / Planを具体化した。
- C4〜C11、`DEC-*`、`FIX-*`、verification-only closeoutをIssueとして作らず、#392内のmilestone / stepへ整理した。
- 人間向けHTML `epic-00384-single-implementation-unit-guide.html` を4つのPlantUML図付きで作成し、旧10-Issue版と同じTailscale URL名へ付け替えた。
- production code、test code、workflowはplanning段階では変更していない。

## Accepted decisions

- combined hard cutover。uninstall-first bridge / intermediate generationなし。
- exact clean `0.2.3`だけをone-shot migrateし、active legacy recoveryは推測変換しない。
- old `0.2.3` packageのfinal workspace mutation-zeroをmerge acceptanceにする。
- `.gitignore`とshipped consumer `ci.yml`はfresh-init-only consumer-owned seeds。
- `init --force`はinstall / update aliasで、追加authorityなし。
- uninstallはtooling-only、`--apply`がconfirmation、`--keep-specs`はcompatibility alias。
- purge capabilityを廃止し、`--remove-specs`はnon-mutating exit 2 trap。
- one packaging invocationでwheel / sdistをbuildし、Linux canonical / macOS deltaがsame wheelを使う。
- main push Full Regression、failure ledger、timing、sharder、policy skipsをfinal stateから撤去する。
- required contextは既存名再利用を優先し、human merge gateを維持する。
- uninstall後もfixed recordを`state=tooling-absent-preserved-data`として保持し、never-installed `absent`と識別する。reinstallはconsumer seed absenceを保持する。
- old `0.2.3` mutation-zeroはPython filesystem eventsとnative `renameat2` / `renameatx_np` callsを覆うtarget-scoped startup composite tripwire event 0を主証拠、native positive controlsの捕捉とtree digest不変を補助証拠とする。

## Planning verification

- exact Strict source: repository `chemitaro/spec-dock`、branch `codex/epic-00384-provider-test-strategy-planning`、SHA `d8f9d02f2400cbc084e5ee92a5fbba339f93f015`。
- `uv run pytest --run-full-regression --collect-only -qq`: 2,710 nodes。
- sorted node-set SHA-256: `f607b007d167231ed27f2a17391b0d8b3aa452d67ce6532565463e193486a04c`。
- `uv run pytest -q`: 1,574 passed、1,136 skipped、57.02s。
- `/usr/bin/time -lp` reference: real 58.42、user 24.41、sys 31.29。pytestは直前にexit 0、time wrapperはsandboxの`sysctl kern.clockrate: Operation not permitted`でexit 1。
- ledger: 27 total、26 active、1 resolved。
- 26 active node focused rerun: 26 failed in 14.69s。
- GitHub API: rulesets 0、repo permission admin。classic protectionはcurrent PATで403。
- current package / recognized workspace: `0.2.3`。
- `managed_distribution.py` 999,468 bytes、主要tests 774,072 / 454,511 bytes。
- HTML validation: static 4 sources、official `@plantuml/core@1.2026.6`、browser 4/4 inline SVG、zoom interaction PASS。
- Tailscale URL: `http://100.85.74.8:8765/epic-00384-provider-test-strategy-vertical-slices-guide.html`。sourceは新しいsingle-implementation-unit guideへのlive symlink。
- first independent Strict specification review（session `required-strict-github-connector-verificati-566`、SHA `638404525610ea08c7b1ba95ed546939bfab6db9`）はP1を2件検出した。uninstall後record削除によるstate識別不能と、tree digestだけでは一時mutation attemptを検出できない点である。
- 両P1を採用し、durable tooling-absent recordとtarget-scoped startup audit-hook tripwireをRequirement / Design / Plan / ADR / HTMLへ反映した。
- second independent Strict re-review（same reviewer identity、session run `required-strict-github-connector-verificati-572`、SHA `41ebcd9e068138f7a06ab924b2c2ca977b3af61e`）は、4 roots / 2 slots限定表現がfixed record / seed creationと矛盾する点と、Python audit hookがexact 0.2.3のnative rename pathを捕捉しない点をP1として検出した。
- 両P1を採用し、固定mutation setを4 roots、2 slots、fixed record、fresh-init-only seed creationへ明確化し、tripwireをnative `renameat2` / `renameatx_np`とpositive controlsまで覆うcomposite detectorへ修正した。

## Remaining lifecycle gates

- P1修正版をGitHub #384 / #392へ再同期し、SpecDock validateを実行する。
- planning修正版をcommit / pushし、同じStrict review sessionで再審査してP0 / P1 = 0を確認する。
- implementationは#392の別lifecycleで開始し、final acceptanceまでIssueをopenに保つ。

## Residual dynamic evidence

次はplanning不足ではなく、final formatまたはlive PRが存在してからしか取得できない#392 acceptance evidenceである。

- final node set / artifact digests / build invocation count
- old `0.2.3` package mutation-zero
- seeded fault後rerun convergence
- final 5-run wall / CPU、rolling 20、duplicate 0、policy skip 0
- effective required contexts / classic protection / merge queue / canary
- merged treeとverified PR treeの一致

未達なら追加Issueを作らず、#392をopenのまま修正する。
