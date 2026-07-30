# ChatGPT Proによるepic-00312再計画ZIPの検査・採用記録

## 位置づけ

- 対象: `epic-00312`
- 種別: ChatGPT Pro advisory evidence
- authority: evidence only
- canonical adoption: このファイル単体では行わない
- GitHub repository: `chemitaro/spec-dock`
- observed branch: `epic-00312-experimental-local-workbench-and-worktree-handoff`
- observed commit: `1aa5fd8e7f3cf899bfefa6e1cedb864c2de3dba0`
- evidence mode: `github-synced`
- ChatGPT model selection evidence:
  - requested: `Pro`
  - resolved: `Pro`
  - verified: `yes`

## 依頼した分析

現在の実装、旧Epic文書、2026-07-28の再調査・interview結果をGitHubの指定branchで照合し、次を中心とするEpic要件定義書・設計書・計画書を再構成するよう依頼した。

1. fresh `spec-dock init` と今後のInitiative / Epic / Issue作成時に、tracked shellを持つWorkbenchを自動生成する。
2. Workbenchの中身はGit管理せず、worktree-localかつdisposableとする。
3. Workbench内外、repository内外を問わず、明示されたsingle regular non-symlink fileをroot / Initiative / Epic / IssueのArtifactへimportする。
4. import先filenameはtimestamp/collision prefixとoriginal basename/extensionを組み合わせ、title / slugやtyped `file` tokenを必須にしない。
5. `workbench copy`はlinked worktree間のignored contentを必要時に移すmanual one-shot helperとして残す。
6. Issue候補は必要最小限のvertical sliceとし、最終統合品質を所有するIssueを含める。

## 受領物

初回ZIP:

- filename: `epic-00312-replanning-authoring-pack.zip`
- SHA-256: `26fd8ddaa54fa6cf3845d9d80b7efd5b8dc6964a25c8e1197ef74fcdabfd4bae`
- size: `46,300 bytes`
- files: `24`
- outcome: SpecDock reviewでreject
- finding: `safe-output-constraints.md`自身が禁止対象名を列挙したため、`raw_transcript:raw transcript`を自己検出

同一ChatGPT conversationで最小修正したZIP:

- filename: `epic-00312-replanning-authoring-pack-review-fixed.zip`
- SHA-256: `ecd4c65a608ee4474fd5e06b0230150ba56106a5eee7418811367c9cbadca371`
- size: `46,307 bytes`
- files: `24`
- 変更: `safe-output-constraints.md`の禁止対象表現一箇所のみ
- その他23ファイル: 初回ZIPとbyte-identicalであるとのChatGPT申告

## SpecDock evidence-lane結果

- GitHub sync preflight: `pass`
- source manifest hash: `f40f3dac04774c04df9a0d3fb015d59a2f250f246b5e2a9403c17139fcd14577`
- fixed ZIP review: `pass`
- findings: `[]`
- pack tree digest: `932eb6c683fd14c869247cd5aa835857e0c2bada13241dd2e11d6989e9a4cb67`
- stage: `pass`
- `epic-issue-candidates` validation: `pass`
- candidate count: `3`
- valid candidate count: `3`
- node creation performed: `false`
- approval required: `true`

## Issue候補

1. `candidate-epic-00312-01-workbench-shell`
   - title: `Workbench Shell Scaffolding`
   - value: fresh rootおよびfuture nodeでWorkbenchを直ちに利用可能にする。
2. `candidate-epic-00312-02-generic-file-import`
   - title: `Generic Single File Artifact Import`
   - value: 任意single fileをrootまたはnodeのArtifactへ明示importする。
3. `candidate-epic-00312-03-final-quality`
   - title: `Integration Distribution And Final Quality`
   - value: provider / package / installed consumer / dogfood / full regression / Epic acceptance closureを統合する。

候補1と2は並行可能で、候補3は両者に依存する。Issue nodeは人間が分割を承認するまで作成しない。

## 採用判断

- current `epic-00312`を再利用する。
- 旧 `iss-00315`〜`iss-00319` は履歴として保持し、新Issue候補には再利用しない。
- ChatGPTのMarkdownはadvisory draftであり、main orchestratorがユーザー判断とrepository factsに照らして正本へ再記述する。
- 要件定義、設計、計画は順番に採用し、それぞれfresh `spec-reviewer` gateを通す。
- ZIP review / candidate validation passはcanonical adoption、Issue作成承認、実装開始承認を意味しない。
