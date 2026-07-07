---
種別: 要件定義書（Epic）
ID: "epic-00295"
タイトル: "ChatGPT Authoring Pack Installed Runtime"
関連GitHub: ["#295"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
親: ["init-local-00003"]
---

# epic-00295 ChatGPT Authoring Pack Installed Runtime — 要件定義

## 目的

この Epic は、SpecDock 自身の dogfood helper として実験されてきた ChatGPT / GPT-5.5 Pro Extended authoring pack workflow を、consumer repository へ `spec-dock init/update` で配布される installed runtime surface と installed skill surface へ昇格する。

成果は、repo-aware ChatGPT authoring を安全かつ再現可能に実行するための runtime command group、installed skill taxonomy、GitHub sync preflight、ZIP / tree evidence contract、candidate validation、staged adoption evidence generation である。

この Epic は ChatGPT に canonical authority を与えない。ChatGPT output は requirement / design / plan / Issue slicing / reviewer-focus / risk analysis の evidence-only producer であり、canonical adoption、`.assurance.json` mutation、`authorized_profile` 決定、fresh reviewer pass、execution-ready、PR-ready、Issue / Epic 完了を主張してはならない。

## 背景

Epic 00283 では、ChatGPT ZIP authoring pack を dogfood-only helper として扱い、`scripts/authoring-pack/` 配下で preflight、ZIP review、stage、selected skeleton validation、Issue candidate validation を検証した。この helper は runtime command でも shipped contract でもなかった。

Epic 00295 では、この実験結果を受けて、provider-side source of truth を `src/spec_dock/assets/spec_dock/...` と `src/spec_dock/assets/install_root/...` へ移し、consumer repository に installed runtime / installed skills として配布可能にする。

## ユースケース

- UC-001: 人間が大きく曖昧な作業依頼を与え、ChatGPT が Initiative / Epic / Issue 候補、requirement / design / plan draft、risk / reviewer focus を evidence-only pack として返す。
- UC-002: 既存 Initiative から Epic portfolio 案を作り、人間の承認前で停止する。
- UC-003: 既存 Epic から Issue decomposition proposal と per-Issue draft requirement / design / plan を作り、Issue Decomposition Approval Gate で停止する。
- UC-004: Issue node 作成後、ChatGPT 由来 draft を `spec-dock-issue-planning` の `draft-adoption` mode で canonical Issue docs へ採否判断・再記述する。
- UC-005: repo-aware ChatGPT invocation 前に、local branch / GitHub connector-visible branch / HEAD / source hashes が一致することを fail-closed に確認する。
- UC-006: ChatGPT backend が設定されている環境では runtime command から prompt pack を渡し、未設定環境では明確に fail-closed する。
- UC-007: ZIP / tree output を unsafe entry / forbidden authority claim / source mismatch / stale condition で拒否し、pass した output だけを staged evidence として扱う。
- UC-008: ChatGPT や GitHub connector が使えない場合でも、manual authoring path へ戻れる。
- UC-009: GitHub と同期できない事情がある場合、人間が明示的に `local-context` evidence mode を選び、十分な差分ファイル / source bundle / prompt context を渡して ChatGPT authoring を実行する。
- UC-010: Epic に複数 Issue が属する場合、中間 Issue ごとの PR は作らず、Issue を一つずつ start / planning / execution / finish でリレーし、最後の final quality gate / PR delivery Issue で Epic 単位の品質確認、修正、mergeable PR 作成を行う。

## スコープ

必須:

- Provider-side asset layout への authoring pack helper 移設。
- Installed runtime command group `./spec-dock/scripts/spec-dock authoring ...` の追加。
- Installed skill `spec-dock-chatgpt-authoring` の追加。
- 既存 planning skills の責務説明、modes、stop gate の更新。
- GitHub sync preflight の block-first contract。
- GitHub sync preflight が満たせない場合の explicit `local-context` evidence mode。
- Prompt pack / backend invocation / ZIP review / stage / validate command の runtime 化。
- ZIP root `specdock-authoring-pack/` と metadata schema の installed contract 化。
- Evidence Adoption Ledger candidate、approval check、validation report、staged artifacts の出力。
- Tests / fixtures / manual dogfood evidence。
- Docs / reference / workflow updates。

対象外:

- `authoring adopt` command。
- `authoring create-issues-from-zip` command。
- `authoring mark-reviewer-pass` command。
- `authoring set-authorized-profile` command。
- `authoring issue-execution-ready` command。
- `authoring pr-ready` command。
- ChatGPT による canonical docs 直接更新。
- ChatGPT による `.assurance.json` 作成・更新。
- ChatGPT による `authorized_profile` 決定。
- ChatGPT self-review を `spec-reviewer` pass と扱うこと。
- ZIP をリポジトリへ直接展開すること。
- raw transcript、secret、credential、host-local absolute path の保存契約。
- PR 作成、CI 修正、merge readiness の自動化。
- `-f` / `--force` のような意味の広い bypass flag。
- 中間 Issue ごとの pull request delivery。

## 権限境界

- `authority: evidence_only` を固定する。
- `adoption_status: unreviewed` は artifact adoption state であり、validator success ではない。
- `bundle_generation_not_promotion: true` を固定する。
- ChatGPT output は canonical docs、`.assurance.json`、fresh reviewer gate、execution readiness、PR readiness の authority を持たない。
- Candidate ZIP / tree は claim / section / artifact 単位で review / stage / adopt 判断される。
- Canonical adoption は main orchestrator または scope owner が再記述し、必要な fresh reviewer gate を通した後にだけ成立する。
- Epic-level Issue decomposition は human explicit approval before Issue node creation で停止する。
- Issue node 作成後の Issue draft adoption / canonicalization は `spec-dock-issue-planning` の `draft-adoption` mode で自動化できるが、fresh reviewer pass 前に execution-ready と扱わない。

## Epic requirements

- E-RQ-ST-001: Human-visible skill names は `spec-dock-` prefix を持つ。
- E-RQ-ST-002: 既存 skill names は可能な限り維持する。
- E-RQ-ST-003: ユーザーが選びやすい順序を、Initiative -> Epic -> Issue -> ChatGPT evidence lane として文書化する。
- E-RQ-ST-004: `spec-dock-initiative-planning` は Initiative Authoring / Epic Slicing を担い、Epic node creation 前の human approval gate で停止する。
- E-RQ-ST-005: `spec-dock-epic-planning` は Epic Authoring / Issue Slicing を担い、Issue Decomposition Approval Gate で停止する。
- E-RQ-ST-006: `spec-dock-issue-planning` は Issue Authoring / Draft Adoption を担い、`zero-base` / `requirement-first` / `draft-adoption` modes を持つ。
- E-RQ-ST-007: `spec-dock-chatgpt-authoring` は ChatGPT Batch Evidence Lane として shared evidence producer を担い、canonical adoption / execution を行わない。
- E-RQ-ST-008: Issue planning は初期実装では分割せず、mode と stop condition で制御する。
- E-RQ-RT-001: `authoring` command group を repo-local runtime parser / registry に追加する。
- E-RQ-RT-002: runtime command は provider-side assets から installed repo へ配布される。
- E-RQ-RT-003: command output は machine-readable summary と human-readable diagnostics を持つ。
- E-RQ-RT-004: status taxonomy は `pass` / `fail` / `blocked` / `stale` / `rejected` / `deferred` / `unreviewed` を維持する。
- E-RQ-RT-005: pass は validation pass であり、canonical adoption / reviewer pass ではない。
- E-RQ-RT-006: runtime command は canonical docs を直接上書きしない。
- E-RQ-RT-007: staging output は explicit output directory または scope-local artifact target に限定し、ownership marker を持つ。
- E-RQ-RT-008: backend command は `--backend-command`、`SPECDOCK_CHATGPT_COMMAND`、optional `ORACLE_CHATGPT_COMMAND` の順に解決し、未設定時は fail-closed する。
- E-RQ-GH-001: repo-aware ChatGPT invocation 前に `authoring preflight github-sync` を必須にする。
- E-RQ-GH-002: preflight は local repo root、origin URL、current branch、local HEAD、remote tracking branch、GitHub connector-visible branch、GitHub HEAD、default branch、source paths、source hashes を記録する。
- E-RQ-GH-003: local branch は GitHub connector-visible branch と一致し、local HEAD は GitHub HEAD と一致しなければならない。
- E-RQ-GH-004: dirty tracked changes、staged changes、untracked files、unpushed commits、behind、diverged、branch missing on GitHub、origin mismatch、source hash mismatch、connector failure、unknown default branch は block する。
- E-RQ-GH-005: default branch fallback は explicit opt-in の場合だけ許可し、`requested_ref` と `effective_ref` を記録する。
- E-RQ-GH-006: fallback pack は adoption 時に requested / effective ref mismatch を明示し、silent fallback しない。
- E-RQ-GH-007: connector が使えない場合は repo-aware invocation を実行せず、manual fallback evidence を残す。
- E-RQ-GH-008: GitHub sync preflight を満たせない場合でも、`--evidence-mode local-context` のような明示 mode で ChatGPT authoring を許容する。
- E-RQ-GH-009: `local-context` mode は `github-synced` repo-aware evidence ではなく、provided files / diff bundle / prompt context evidence として provenance に記録する。
- E-RQ-GH-010: `local-context` mode は `sync_state: local_context`、`github_sync: not_verified`、`adoption_requires: explicit_eal_disposition` を記録し、同期済み evidence と同じ authority を主張しない。
- E-RQ-GH-011: `local-context` mode は canonical adoption、Issue slicing approval、execution readiness の自己主張を禁止し、正本採用時には EAL で同期なしの理由、提供 context、残存リスクを記録する。
- E-RQ-DEL-001: Epic に複数 Issue が属する場合、原則として中間 Issue では PR を作成しない。
- E-RQ-DEL-002: Epic Execution は Issue を一つずつ start / planning / execution / finish でリレーし、次の Issue へ進む。
- E-RQ-DEL-003: Epic plan は必ず最後に final quality gate / PR delivery Issue candidate を含める。
- E-RQ-DEL-004: final quality gate / PR delivery Issue は Epic 単位の品質ゲート、手動テスト、reviewer / CI / PR review 指摘修正、mergeable PR 作成を担う。
- E-RQ-DEL-005: 中間 Issue の finish evidence には、PR delivery を final quality gate / PR delivery Issue に defer した根拠、final Issue への dependency edge、no-per-Issue-PR rationale を記録する。
- E-RQ-ZIP-001: ZIP root は `specdock-authoring-pack/` の単一 root とする。
- E-RQ-ZIP-002: 必須 metadata は `manifest.json`、`provenance.json`、`source-manifest.json`、`stale-if.json`、`safe-output-constraints.md`、`adoption/adoption-map.json`、`adoption/eal-candidates.json` を含む。
- E-RQ-ZIP-003: Initiative / Epic / Issue candidates と drafts は `candidates/epics/*`、`candidates/issues/*`、`drafts/initiative/*`、`drafts/epic/*`、`drafts/issue/*` に置く。
- E-RQ-ZIP-004: selected skeleton fill は `selected-skeleton-fill/section-fills.json` に限定する。
- E-RQ-ZIP-005: path traversal、absolute / host-local path、hidden path、secret-looking path、raw transcript、credential / token / private key、nested archive、executable、symlink、binary、oversized file、unsupported suffix、encrypted entry、wrong ZIP root、metadata missing、source hash mismatch、forbidden authority claim を拒否する。
- E-RQ-ZIP-006: ZIP は safe review 前に展開しない。
- E-RQ-ZIP-007: tree input fallback は ZIP central directory safety evidence を欠くため、fallback evidence として扱う。

## 非機能要件

- E-RQ-NF-001: fail-closed を原則にする。
- E-RQ-NF-002: validation は deterministic で、同じ input から同じ status / diagnostics を返す。
- E-RQ-NF-003: command は consumer repository の private data、secret、raw transcript を保存しない。
- E-RQ-NF-004: provider-side source of truth と dogfood workspace を混同しない。
- E-RQ-NF-005: installed docs / skills / runtime command help は、未実装 command を利用可能と誤読させない。
- E-RQ-NF-006: tests は safe positive / negative fixtures を持ち、manual-tests に tracked workspace evidence を置かない。
- E-RQ-NF-007: old workspace の in-place migration を保証しない既存 update contract と矛盾しない。
- E-RQ-NF-008: human-facing skill names は短く、scope と stop gate が分かる名前にする。

## Epic acceptance criteria

- E-AC-001: `spec-dock update` または `spec-dock init` 後の consumer repo に `spec-dock-chatgpt-authoring` skill が installed managed skill として存在する。
- E-AC-002: existing planning skills の names は維持され、Initiative / Epic / Issue / ChatGPT evidence lane の順序と責務が docs に明記される。
- E-AC-003: `./spec-dock/scripts/spec-dock authoring --help` が command group と supported subcommands を表示する。
- E-AC-004: `authoring preflight github-sync` は clean / synced branch で `pass` し、`requested_ref`、`effective_ref`、local HEAD、GitHub HEAD、source hashes を出力する。
- E-AC-005: preflight は dirty tracked、staged、untracked、unpushed、behind、diverged、branch missing、origin mismatch、connector failure、unknown default branch を `blocked` にする。
- E-AC-006: default branch fallback は explicit opt-in なしでは行われず、opt-in 時は `requested_ref` と `effective_ref` が異なることを記録する。
- E-AC-006a: `local-context` evidence mode は明示指定された場合だけ実行でき、`github-synced` mode と別の provenance / risk / adoption requirements を出力する。
- E-AC-007: backend command 未設定時、`authoring backend invoke` は推測実行せず fail-closed する。
- E-AC-008: backend command 設定時、prompt pack を渡して invocation summary を生成し、secret / host-local path を canonical docs に保存しない。
- E-AC-009: `authoring pack prepare` は evidence-only prompt pack を作り、ChatGPT に forbidden authority claims と ZIP contract を明示する。
- E-AC-010: `authoring pack review` は unsafe ZIP entry と forbidden authority claim を safe extraction 前に拒否する。
- E-AC-011: `authoring pack stage` は valid pack から staged evidence / dry-run diff / EAL candidate を作るが、canonical docs を直接上書きしない。
- E-AC-012: `authoring validate epic-issue-candidates` は Issue candidates の parent trace、scope / non-scope、draft files、profile recommendation advisory-only、`authorized_profile: null` を検証する。
- E-AC-013: `authoring validate initiative-epic-candidates` は Epic candidates の parent Initiative trace と human approval before Epic node creation を検証する。
- E-AC-014: `authoring validate issue-draft-adoption` は Issue node 作成後の draft adoption input を検証し、fresh reviewer pass 前に execution-ready を主張しない。
- E-AC-015: `authoring approval check` は Issue / Epic node creation 前の明示承認 evidence がない場合に block する。
- E-AC-016: ChatGPT output、ZIP、tree、review report、stage report は `authority: evidence_only` / `adoption_status: unreviewed` / `bundle_generation_not_promotion: true` を維持する。
- E-AC-017: `authoring adopt`、`authoring create-issues-from-zip`、`authoring mark-reviewer-pass`、`authoring set-authorized-profile`、`authoring issue-execution-ready`、`authoring pr-ready` は初期実装で存在しないか、存在しても unsupported / deferred として fail-closed する。
- E-AC-018: Positive / negative tests が provider-side assets と installed runtime path の両方で通る。
- E-AC-019: Dogfood scenario として Epic 00295 自身または sibling fixture で Initiative/Epic/Issue candidate pack、GitHub preflight block、ZIP rejection、Issue draft adoption validation を確認する。
- E-AC-020: Final quality gate は `git diff --check`、`./spec-dock/scripts/spec-dock validate`、関連 pytest/manual tests、installed asset verification、docs consistency を記録する。
- E-AC-021: Epic plan は no-per-Issue-PR relay policy と final quality gate / PR delivery Issue candidate を含む。
- E-AC-022: final quality gate / PR delivery Issue の handoff package は、全 preceding Issues の completion evidence、manual test summary、reviewer / CI repair loop、mergeable PR readiness を確認対象に含む。

## 未確定事項

- Q-001: `authoring preflight github-sync` の default branch fallback flag 名。
- Q-002: `spec-dock-chatgpt-authoring` の managed skill list 上の正確な挿入位置。
- Q-003: `ORACLE_CHATGPT_COMMAND` fallback の廃止時期。
- Q-004: Initiative/Epic candidate schema の exact shape。
- Q-005: approval evidence の保存場所と署名強度。
