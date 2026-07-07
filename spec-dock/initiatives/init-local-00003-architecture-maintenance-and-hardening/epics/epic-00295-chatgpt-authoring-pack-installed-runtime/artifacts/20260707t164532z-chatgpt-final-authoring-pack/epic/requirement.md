---
種別: "要件定義書（Epic draft）"
ID: "epic-00295"
タイトル: "ChatGPT Authoring Pack Installed Runtime"
関連GitHub: ["#295"]
状態: "adoption-candidate"
作成者: "ChatGPT"
最終更新: "2026-07-07"
依存: []
親: ["init-local-00003"]
authority: "evidence_only"
adoption_status: "unreviewed"
bundle_generation_not_promotion: true
---

# epic-00295 ChatGPT Authoring Pack Installed Runtime — 要件定義

## 結論

この Epic は、dogfood helper として検証されてきた ChatGPT authoring pack workflow を、SpecDock の installed runtime surface と installed skill surface に昇格する。成果物は `spec-dock authoring ...` command group、`spec-dock-chatgpt-authoring` skill、既存 planning skills の stop gate 更新、GitHub sync preflight、prompt pack / backend / ZIP review / stage / validation の evidence-only runtime contract である。

ChatGPT output は正本ではない。ChatGPT は requirement / design / plan draft、Issue slicing proposal、draft pack、risk、reviewer focus、EAL candidate を作れるが、canonical adoption、`.assurance.json` mutation、`authorized_profile` 決定、fresh reviewer pass、execution-ready、PR-ready、Issue/Epic completion を主張してはならない。

## 目的

- 大きく曖昧な作業依頼を Initiative / Epic / Issue へ分解する batch planning evidence lane を提供する。
- 既存 planning workflow の human quality gate を維持したまま、ChatGPT に draft / candidate evidence の大量生成を委任できるようにする。
- repo-aware ChatGPT invocation 前に GitHub と local context の同期性を fail-closed に確認する。
- 同期できない場合でも、明示的な `local-context` evidence mode と低い authority で作業を継続できる path を提供する。
- 中間 Issue ごとの PR を避け、最後の final quality gate / PR delivery Issue で Epic 単位の mergeable PR を作る relay workflow を定着させる。

## 背景

Epic 00283 の dogfood helper は `scripts/authoring-pack/` で preflight、ZIP review、stage、candidate validation を試したが、consumer repository へ installed runtime として配布される source of truth ではなかった。Epic 00295 では provider-side assets へ移し、`spec-dock init/update` で導入先 repository に届く installed runtime / installed skills / docs として扱う。

## スコープ

必須スコープ:

- Provider-side asset layout への authoring pack helper 移設。
- Runtime command group `./spec-dock/scripts/spec-dock authoring ...` の追加。
- Shared evidence lane skill `spec-dock-chatgpt-authoring` の追加。
- 既存 planning skills の名称維持と責務・mode・stop gate 更新。
- `authoring preflight github-sync` の block-first contract。
- `github-synced` default mode と、明示 opt-in の `local-context` evidence mode。
- Prompt pack prepare、backend invocation adapter、ZIP/tree review、stage、candidate validators、issue draft adoption validators、approval check。
- ZIP root `specdock-authoring-pack/` と required metadata / safety validation contract。
- Evidence Adoption Ledger candidate、stage report、validation report、dry-run diff。
- Tests、fixtures、manual dogfood evidence、runtime docs、workflow guidance。
- Epic execution relay policy と final quality gate / PR delivery Issue。

## 対象外

- `authoring adopt` command。
- `authoring create-issues-from-zip` command。
- `authoring mark-reviewer-pass` command。
- `authoring set-authorized-profile` command。
- `authoring issue-execution-ready` command。
- `authoring pr-ready` command。
- ChatGPT による canonical docs 直接更新。
- ChatGPT による `.assurance.json` 作成・更新。
- ChatGPT による `authorized_profile` 決定。
- ChatGPT self-review を fresh `spec-reviewer` pass と扱うこと。
- ZIP を canonical docs へ直接展開すること。
- raw transcript、secret、credential、host-local absolute path の durable 保存契約。
- PR 作成、CI 修正、merge readiness の中間 Issue 自動化。
- `-f` / `--force` のような広い bypass flag。
- 中間 Issue ごとの pull request delivery。

## 権限境界

- 全 generated pack / staged evidence は `authority: evidence_only` を固定する。
- `adoption_status: unreviewed` は artifact adoption state であり、validator pass や reviewer pass ではない。
- `bundle_generation_not_promotion: true` を固定する。
- Stage は EAL candidate を作るだけで、final EAL row ではない。
- Canonical adoption は main orchestrator または scope owner が claim / section / artifact 単位で再記述し、必要な fresh reviewer gate を通した後に成立する。
- `local-context` evidence は `github-synced` evidence より低い authority であり、canonical adoption 時に EAL disposition を必須とする。

## Skill requirements

- E-RQ-ST-001: user-visible skill names は `spec-dock-` prefix を持つ。
- E-RQ-ST-002: 既存 skill names は可能な限り維持する。
- E-RQ-ST-003: user-facing order は Initiative -> Epic -> Issue -> ChatGPT evidence lane とする。
- E-RQ-ST-004: `spec-dock-initiative-planning` は Initiative Authoring / Epic Slicing を担い、Epic node creation 前の human approval gate で停止する。
- E-RQ-ST-005: `spec-dock-epic-planning` は Epic Authoring / Issue Slicing を担い、Issue Decomposition Approval Gate で停止する。
- E-RQ-ST-006: `spec-dock-issue-planning` は Issue Authoring / Draft Adoption を担い、`zero-base` / `requirement-first` / `draft-adoption` modes を持つ。
- E-RQ-ST-007: `spec-dock-chatgpt-authoring` は ChatGPT Batch Evidence Lane として shared evidence producer を担い、canonical adoption / execution / PR readiness を行わない。
- E-RQ-ST-008: Issue planning は初期実装では split せず、mode と stop condition で制御する。

## Runtime requirements

- E-RQ-RT-001: `authoring` command group を repo-local runtime parser / registry に追加する。
- E-RQ-RT-002: runtime command は provider-side assets から installed repo へ配布される。
- E-RQ-RT-003: command output は machine-readable summary と human-readable diagnostics を持つ。
- E-RQ-RT-004: status taxonomy は `pass` / `fail` / `blocked` / `stale` / `rejected` / `deferred` / `unreviewed` を維持する。
- E-RQ-RT-005: `pass` は command-local validation pass であり、canonical adoption / reviewer pass ではない。
- E-RQ-RT-006: runtime command は canonical docs を直接上書きしない。
- E-RQ-RT-007: staging output は explicit output directory または scope-local artifact target に限定し、ownership marker を持つ。
- E-RQ-RT-008: backend command は `--backend-command`、`SPECDOCK_CHATGPT_COMMAND`、optional `ORACLE_CHATGPT_COMMAND` の順に解決し、未設定時は fail-closed する。

## GitHub sync / evidence mode requirements

- E-RQ-GH-001: repo-aware ChatGPT invocation 前に `authoring preflight github-sync` を必須にする。
- E-RQ-GH-002: preflight は local repo root、origin URL、current branch、local HEAD、remote tracking branch、GitHub connector-visible branch、GitHub HEAD、default branch、source paths、source hashes を記録する。
- E-RQ-GH-003: local branch は GitHub connector-visible branch と一致し、local HEAD は GitHub HEAD と一致しなければならない。
- E-RQ-GH-004: dirty tracked changes、staged changes、untracked files、unpushed commits、behind、diverged、branch missing on GitHub、origin mismatch、source hash mismatch、connector failure、unknown default branch は block する。
- E-RQ-GH-005: default branch fallback は explicit opt-in の場合だけ許可し、`requested_ref` と `effective_ref` を記録する。
- E-RQ-GH-006: fallback pack は adoption 時に requested / effective ref mismatch を明示し、silent fallback しない。
- E-RQ-GH-007: connector が使えない場合は repo-aware invocation を実行しない。
- E-RQ-GH-008: GitHub sync preflight を満たせない場合でも、`--evidence-mode local-context` 相当の明示 mode で ChatGPT authoring を許容する。
- E-RQ-GH-009: `local-context` は provided files / diff bundle / prompt context evidence として provenance に記録する。
- E-RQ-GH-010: `local-context` は `sync_state: local_context`、`github_sync: not_verified`、`adoption_requires: explicit_eal_disposition` を記録する。
- E-RQ-GH-011: `local-context` は canonical adoption、Issue slicing approval、execution readiness の自己主張を禁止する。

## ZIP / tree artifact requirements

- E-RQ-ZIP-001: ZIP root は `specdock-authoring-pack/` の単一 root とする。
- E-RQ-ZIP-002: required metadata は `manifest.json`、`provenance.json`、`source-manifest.json`、`stale-if.json`、`safe-output-constraints.md`、`adoption/adoption-map.json`、`adoption/eal-candidates.json` を含む。
- E-RQ-ZIP-003: candidates と drafts は fixed paths に置く。
- E-RQ-ZIP-004: selected skeleton fill は `selected-skeleton-fill/section-fills.json` に限定する。
- E-RQ-ZIP-005: path traversal、absolute / host-local path、hidden path、secret-looking path、raw transcript、credential / token / private key、nested archive、executable、symlink、binary、oversized file、unsupported suffix、encrypted entry、wrong ZIP root、metadata missing、source hash mismatch、forbidden authority claim を拒否する。
- E-RQ-ZIP-006: ZIP は safe review 前に展開しない。
- E-RQ-ZIP-007: tree input fallback は ZIP central directory safety evidence を欠くため fallback evidence として扱う。

## Candidate / adoption requirements

- E-RQ-VAL-001: Initiative/Epic candidates は parent Initiative trace、scope/non-scope、dependencies、duplicate/overlap diagnostics を持つ。
- E-RQ-VAL-002: Epic/Issue candidates は parent Epic trace、Issue boundaries、dependency order、draft requirement/design/plan を持つ。
- E-RQ-VAL-003: profile recommendation は advisory-only とし、`authorized_profile` claim は拒否する。
- E-RQ-VAL-004: Issue draft adoption validation は Issue node 作成後にだけ使用し、fresh reviewer pass 前に execution-ready を主張しない。
- E-RQ-VAL-005: approval check は node creation 前の explicit human approval evidence がない場合に block する。

## Delivery requirements

- E-RQ-DEL-001: Epic に複数 Issue が属する場合、原則として中間 Issue では PR を作成しない。
- E-RQ-DEL-002: Epic Execution は Issue を一つずつ start / planning / execution / finish でリレーし、次の Issue へ進む。
- E-RQ-DEL-003: Epic plan は必ず最後に final quality gate / PR delivery Issue candidate を含める。
- E-RQ-DEL-004: final quality gate / PR delivery Issue は Epic 単位の品質ゲート、手動テスト、reviewer / CI / PR review 指摘修正、mergeable PR 作成を担う。
- E-RQ-DEL-005: 中間 Issue の finish evidence は PR delivery defer rationale、final Issue dependency、no-per-Issue-PR rationale を記録する。

## 非機能要件

- E-RQ-NF-001: fail-closed を原則にする。
- E-RQ-NF-002: validation は deterministic で、同じ input から同じ status / diagnostics を返す。
- E-RQ-NF-003: command は consumer repository の private data、secret、raw transcript を保存しない。
- E-RQ-NF-004: provider-side source of truth と dogfood workspace を混同しない。
- E-RQ-NF-005: installed docs / skills / runtime help は未実装 command を利用可能と誤読させない。
- E-RQ-NF-006: tests は safe positive / negative fixtures を持つ。
- E-RQ-NF-007: old workspace の in-place migration を保証しない既存 update contract と矛盾しない。
- E-RQ-NF-008: human-facing skill names は短く、scope と stop gate が分かる名前にする。

## Epic acceptance criteria

- E-AC-001: `spec-dock update` または `spec-dock init` 後の consumer repo に `spec-dock-chatgpt-authoring` skill が installed managed skill として存在する。
- E-AC-002: existing planning skills の names は維持され、Initiative / Epic / Issue / ChatGPT evidence lane の順序と責務が docs に明記される。
- E-AC-003: `./spec-dock/scripts/spec-dock authoring --help` が command group と supported subcommands を表示する。
- E-AC-004: `authoring preflight github-sync` は clean / synced branch で `pass` し、requested/effective ref、local HEAD、GitHub HEAD、source hashes を出力する。
- E-AC-005: preflight は dirty tracked、staged、untracked、unpushed、behind、diverged、branch missing、origin mismatch、connector failure、unknown default branch を `blocked` にする。
- E-AC-006: default branch fallback は explicit opt-in なしでは行われず、opt-in 時は `requested_ref` と `effective_ref` が異なることを記録する。
- E-AC-007: `local-context` evidence mode は明示指定された場合だけ実行でき、`github-synced` と別の provenance / risk / adoption requirements を出力する。
- E-AC-008: backend command 未設定時、`authoring backend invoke` は推測実行せず fail-closed する。
- E-AC-009: `authoring pack prepare` は evidence-only prompt pack を作り、forbidden authority claims と ZIP contract を明示する。
- E-AC-010: `authoring pack review` は unsafe ZIP entry と forbidden authority claim を safe extraction 前に拒否する。
- E-AC-011: `authoring pack stage` は valid pack から staged evidence / dry-run diff / EAL candidate を作るが、canonical docs を直接上書きしない。
- E-AC-012: `authoring validate epic-issue-candidates` は Issue candidates の parent trace、scope/non-scope、draft files、profile recommendation advisory-only、`authorized_profile: null` を検証する。
- E-AC-013: `authoring validate initiative-epic-candidates` は Epic candidates の parent Initiative trace と human approval before Epic node creation を検証する。
- E-AC-014: `authoring validate issue-draft-adoption` は Issue node 作成後の draft adoption input を検証し、fresh reviewer pass 前に execution-ready を主張しない。
- E-AC-015: `authoring approval check` は Issue / Epic node creation 前の明示承認 evidence がない場合に block する。
- E-AC-016: ChatGPT output、ZIP、tree、review report、stage report は `authority: evidence_only` / `adoption_status: unreviewed` / `bundle_generation_not_promotion: true` を維持する。
- E-AC-017: `authoring adopt`、`authoring create-issues-from-zip`、`authoring mark-reviewer-pass`、`authoring set-authorized-profile`、`authoring issue-execution-ready`、`authoring pr-ready` は初期実装で存在しないか、unsupported / deferred として fail-closed する。
- E-AC-018: Positive / negative tests が provider-side assets と installed runtime path の両方で通る。
- E-AC-019: Dogfood scenario で candidate pack、GitHub preflight block、ZIP rejection、Issue draft adoption validation を確認する。
- E-AC-020: Final quality gate は `git diff --check`、`./spec-dock/scripts/spec-dock validate`、関連 pytest/manual tests、installed asset verification、docs consistency を記録する。
- E-AC-021: Epic plan は no-per-Issue-PR relay policy と final quality gate / PR delivery Issue candidate を含む。
- E-AC-022: final quality gate / PR delivery Issue の handoff package は全 preceding Issues completion evidence、manual test summary、reviewer / CI repair loop、mergeable PR readiness を確認対象に含む。

## 未確定事項

- `authoring preflight github-sync` の default branch fallback flag 名。
- `spec-dock-chatgpt-authoring` の managed skill list insertion position。
- `ORACLE_CHATGPT_COMMAND` fallback の deprecation schedule。
- Initiative/Epic candidate schema の exact shape。
- approval evidence の保存場所と署名強度。
- `local-context` mode の exact flag 名。現時点候補は `--evidence-mode local-context`。
