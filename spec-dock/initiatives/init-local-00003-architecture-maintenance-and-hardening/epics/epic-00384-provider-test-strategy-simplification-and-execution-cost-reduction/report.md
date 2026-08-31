---
種別: レポート（Epic）
ID: "epic-00384"
タイトル: "Provider Test Strategy Simplification and Execution Cost Reduction"
関連GitHub: ["#384"]
最終更新: "2026-08-31"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["init-local-00003"]
---

# Result Summary

詳細: [Report Guide](../../../../docs/authoring/report.md)

## Outcome

- GitHub Epic #384 `Provider Test Strategy Simplification and Execution Cost Reduction` をactive Epicとして維持し、専用branch `codex/epic-00384-disposable-root-replacement` を作成した。
- previous investigationで、Issue #372の4-shard Full Regressionが約99分wall・約5.51 shard-process-hoursを使い、2,708 tests、22,332行の `managed_distribution.py`、主要distribution tests約35,000行という根本原因を固定した。
- Product ownerが、Initiatives / Artifactsを利用者データとして保持し、provider-owned `spec-dock/{docs,templates,system,scripts}` をupdate時に全量置換する方針を受理した。
- detailed synthesis Artifact `20260831t005132z-disc-disposable-root-replacement-and-skill-lifecycle-design.md` を作成し、ownership、update failure、skill marker、uninstall、test削除、移行、Issue境界を具体化した。
- accepted ADR `20260831t005139z-adr-disposable-provider-roots-and-fixed-skill-slots.md` を作成し、Option C2 — Disposable Root ReplacementとFixed Skill Slotsをdurable authorityにした。
- accepted ADRはEpic #365 ADRのper-file operation grammar、Operation Journalによるarbitrary checkpoint recovery、deprovision / purge共通engine、skillの無期限historical file identityを部分的にsupersedeする。pre-write fail-closed、root binding、shared unknown preservation、purge authority separationは維持する。
- Requirement / Design / Planをaccepted ADRへ反映し、旧immutable payload / activation pointer案を4 fixed-root replacement + external rerun convergenceへ置換した。
- `assess-issue-granularity` の結果を `PROPOSED_ISSUE_CANDIDATES` とし、4つのend-to-end候補へ整理した。子Issueはまだaccepted / created / startedではない。
- 人間向けHTML `disposable-root-replacement-and-skill-lifecycle.html` を4つのPlantUML図付きで作成し、Tailscale限定URLへlive symlinkで配信した。
- production code、test code、Issue #372 worktreeは変更していない。commit / pushも実施していない。

## Accepted policy

- durable user data: `spec-dock/initiatives/**` とnested Artifacts。update / tooling uninstallは変更しない。
- opaque preserve: `.workbench/**`、unknown paths、unrelated skills。探索・正規化・削除しない。
- generated projections: `active/**`、`.agent/**`、dashboard、tree / deps、ADR mirror。配布差分として管理しない。
- disposable provider roots: `spec-dock/docs`、`templates`、`system`、`scripts`。candidate全stage後、固定順でroot全量置換し、`scripts`を最後にする。
- failure: cross-root atomicity / rollback / checkpoint resumeを約束せず、ready markerを最後に書き、external installerからsame desired versionを再実行して収束させる。
- managed skills: `.agents/skills/spec-dock` と `.agents/skills/spec-dock-grill-with-docs` のexact slotsだけをsmall owner markerでroot単位管理する。共有parentと他skillsは触れない。
- uninstall: tooling-only。spec-history purgeを通常uninstall authorityから外す。
- tests: deep service interfaceとownership boundaryへ置換し、retired per-file / journal / recovery testsを同じchangeで削除する。

## Proposed Issue boundaries

1. Disposable provider root lifecycle
2. Fixed skill slot lifecycle
3. Tooling-only uninstall and compatibility cutover
4. Test portfolio and CI budget cutover

各候補はtechnical layerではなく、production behavior、migration、documentation、test replacementを含むobservable outcomeである。Issue 4は1〜3に依存する。

## Verification

- current provider sourceに `src/spec_dock/assets/spec_dock/{docs,scripts,system,templates}` の4 rootsだけがあることを確認した。
- current installed-skill provider sourceが `spec-dock` と `spec-dock-grill-with-docs` の2 roots、4 filesであり、`.github/workflows/ci.yml` が別shared surfaceとして存在することを確認した。
- `src/spec_dock/assets/managed_distribution.json` にobsolete skill filesとhistorical identitiesが多数残ることをsource inspectionした。
- `./spec-dock/scripts/spec-dock new artifact disc ...` と `new artifact adr ...` でEpic #384配下にcanonical Artifactsを作成した。
- `./spec-dock/scripts/spec-dock sync --no-github --no-update-active`: generated index / tree / dashboardとaccepted ADR mirrorを同期した。
- `validate-plantuml-html.mjs .../disposable-root-replacement-and-skill-lifecycle.html`: static 4 sources、official `@plantuml/core@1.2026.6`、browser 4/4 inline SVG、zoom interactionすべてPASS。
- Tailscale preview entryはauthoritative HTMLへのsymlinkであり、`readlink` がArtifact pathを返した。
- `curl --head http://100.85.74.8:8765/disposable-root-replacement-and-skill-lifecycle.html`: `HTTP/1.0 200 OK`、`Cache-Control: no-store`。
- `./spec-dock/scripts/spec-dock validate`: `ok`、`nodes=228`。
- `git diff --check`: errorなし。新規Markdownのtrailing whitespace検査も該当なし。
- `./spec-dock/scripts/spec-dock active show`: Initiative `init-local-00003`、Epic `epic-00384`、Issue none。
- `git status --short --branch`: branch `codex/epic-00384-disposable-root-replacement`、変更範囲は新規Epic directoryだけ。commit / pushなし。
- ADR mirror `spec-dock/adrs/20260831t005139z-adr-disposable-provider-roots-and-fixed-skill-slots.md` がcanonical Artifactへのsymlinkであることを確認した。

## Residual Risks / Follow-ups

- `.github/workflows/ci.yml` をinit-once consumer-ownedにするか、reusable workflowへ変えるかは未決である。
- markerなしlegacy workspaceを支援するversion / date windowは未決である。
- `--remove-specs` を完全廃止するか、独立purge commandへ移すか、そのdeprecation / JSON compatibilityは未決である。
- `.gitignore` init seedの既存consumer file collision policyは未決である。
- wheel / sdist / macOS smokeのtriggerは未決である。
- single-process 10分、平均論理core1.1、duplicate 0は設計上のacceptanceであり、implementation前の現時点では未達・未計測である。
- root replacementはprovider toolingの一時的な欠落 / mixed versionを許容する。external installer recovery routeを実装・文書化するまでproduction cutoverしない。
- provider root / managed skill内のlocal editsがupdateで失われるbreaking behaviorをpublic docsとdiagnosticへ明記する必要がある。
- 子Issueはまだ作成していない。各candidate開始前に該当Product gateを確定し、granularityを再評価する。

## Publication

- authoritative HTML: `artifacts/disposable-root-replacement-and-skill-lifecycle.html`
- live URL: http://100.85.74.8:8765/disposable-root-replacement-and-skill-lifecycle.html
- publication mode: authoritative sourceへのlive symlink
- unpublish: `/Users/iwasawayuuta/.agents/skills/tailscale-html-preview/scripts/tailscale-html-preview unpublish disposable-root-replacement-and-skill-lifecycle.html`

## Notes

- 主な判断は「provider bytesを丁寧に一件ずつ保存する」ことから、「user dataとshared parentだけを強く守り、provider内部は捨てられる」に責務を移すことである。
- 4 shardは依然として移行中のdiagnosticとして使えるが、Epic完了後の正規gateには残さない。
- HTMLは理解補助であり、authorityはaccepted ADRとEpic Requirement / Design / Planにある。
