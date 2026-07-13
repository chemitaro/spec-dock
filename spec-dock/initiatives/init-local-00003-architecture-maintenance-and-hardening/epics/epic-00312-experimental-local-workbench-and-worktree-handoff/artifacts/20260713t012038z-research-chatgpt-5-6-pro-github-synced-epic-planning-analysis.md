# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a543730-1998-83e8-9250-1536d1561c0d

## Prompt

Required repository connector context:
- @GitHub chemitaro/spec-dock
- Current branch: main
- Default branch: main
- MUST inspect this GitHub repository with the GitHub connector before answering.
- First inspect the current branch. If the current branch does not exist or cannot be opened, inspect the default branch instead.
- Hard failure condition: if the GitHub connector/app is unavailable, or if the repository, current branch, and default branch cannot be accessed, return immediately with exactly: repository access failed.
- Do not continue from attached files, prompt context, memory, or general knowledge when repository access fails.
- Attached files and prompt-provided context are supplementary only after repository access succeeds.

Use the attached planning brief. Inspect @GitHub chemitaro/spec-dock on main at commit 081ba64823f66d4efb051fb88e2a160915efdfa0 before answering, including Epic 00312 clarification artifacts and relevant runtime, tests, and parent Initiative documents. Produce the requested Japanese Epic planning proposal. Treat the answer as evidence-only.

### File: ../../../../../private/tmp/codex-agent-work/501/session-20260712t154229z-specdock-chatgpt-first-storage-analysis-ac120a25/epic-00312-planning-prompt.md
Lines: 1-53
```md
 1 | # SpecDock Epic 00312 planning brief
 2 | 
 3 | ## Context
 4 | 
 5 | - Project: `spec-dock`, a specification and execution workflow tool that dogfoods its shipped scaffold.
 6 | - Current branch: local `main`.
 7 | - Current goal: plan Epic `epic-00312 Experimental Local Workbench And Worktree Handoff`.
 8 | - Evidence mode: `github-synced`. Epic scaffold and clarification artifacts are committed and pushed on `main` at `081ba64823f66d4efb051fb88e2a160915efdfa0`; SpecDock preflight verified that local and remote heads match. GitHub synchronization still does not make ChatGPT output canonical.
 9 | - The attached repository files, parent Initiative documents, code, tests, and clarification artifacts are the evidence base.
10 | - ChatGPT output is advisory evidence. Canonical adoption requires Codex review, explicit EAL disposition, staged spec review, and human approval before Issue nodes are created.
11 | 
12 | ## Adopted product decisions
13 | 
14 | 1. Introduce an experimental, Git-ignored, local-only, disposable `.workbench/` facility.
15 | 2. Root/pre-scope workbench: `spec-dock/.workbench/YYYY-MM-DD/`. It is expected to become messy. No automatic or bulk handoff command exists for it. A model manually selects and copies only needed files into a scoped workbench.
16 | 3. Scoped workbench: a direct child `.workbench/` under an Initiative, Epic, or Issue directory. Files may be placed there without fine organization and may disappear with the worktree/scope.
17 | 4. `.workbench/` is non-canonical and must be an opaque reserved subtree excluded from default scanners, validators, dependency/ADR/context/source-manifest discovery, and similar recursive interpretation.
18 | 5. Do not add mandatory session folders, manifests, inbox/curated subtrees, TTL, catalogs, promotion state, or deletion blockers.
19 | 6. Add an explicit scoped-workbench copy command for use after a worktree is created and only when the user directs it. Inputs are source current worktree, exactly one Initiative/Epic/Issue identifier, and a target worktree.
20 | 7. Copy the complete scoped `.workbench/` recursively with no content interpretation, allowlist, denylist, file-type filtering, secret scanning, size selection, or special handling for nested `.git` directories.
21 | 8. Merge into an existing destination `.workbench/`: preserve destination-only files; overwrite same relative paths with source files; source wins. Do not replace the destination directory wholesale. No continuous sync or copy-back.
22 | 9. Root workbench is never handled by the command.
23 | 10. Implement the facility once in provider-side shipped runtime/assets and distribute through `spec-dock init/update`; expose it as clearly experimental. Avoid dogfood-only duplicated implementation.
24 | 11. Durable evidence belongs in `artifacts/`; accepted authority belongs in canonical specs/accepted ADR/EAL. Raw ZIP quarantine policy remains separate; the copy command does not inspect content.
25 | 
26 | ## Task
27 | 
28 | Analyze the attached evidence and produce a rigorous Epic planning proposal in Japanese. Reconcile the adopted decisions with the actual repository architecture and identify any repository facts that contradict or constrain them.
29 | 
30 | Prepare:
31 | 
32 | 1. A candidate Epic `requirement.md` with problem, goals, non-goals, actors/use cases, functional and non-functional requirements, acceptance criteria, scope boundaries, assumptions, risks, and unresolved items.
33 | 2. A candidate Epic `design.md` grounded in the current layered/runtime/provider architecture. Specify directory contracts, ignore/scanner invariants, command semantics, target-worktree and scope resolution, merge/collision behavior, safety boundaries, error behavior, update/install propagation, testing strategy, observability/output, and rejected alternatives.
34 | 3. A candidate Epic `plan.md` with dependency-ordered implementation phases, verification gates, provider/dogfood synchronization, and an explicit final quality/mergeable-PR Issue as required for a multi-Issue implementation Epic.
35 | 4. Recommended child Issue decomposition. For each Issue provide title, objective, scope/non-scope, dependencies, deliverables, acceptance criteria, tests, and draft-requirement handoff content. These are evidence drafts only; do not claim that Issue nodes exist or are execution-ready.
36 | 5. A decision table: adopted / refined / rejected / needs-human-decision, with reasoning and evidence paths.
37 | 6. Failure modes and blind spots, especially path containment, symlinks, copying into the same worktree, nonexistent/ambiguous scope IDs, partially failed copies, scanner regressions, installer updates, and worktree path identification. Keep mechanisms simple unless repository evidence makes added complexity necessary.
38 | 
39 | ## Constraints
40 | 
41 | - Preserve all explicitly adopted product decisions unless they are technically impossible or unsafe; if so, flag the conflict rather than silently changing the requirement.
42 | - Do not invent repository APIs, commands, or current behavior. Cite attached file paths for material claims.
43 | - Distinguish requirement-level policy from design mechanics and implementation steps.
44 | - Do not produce code or a patch.
45 | - Do not promote ChatGPT output to canonical authority.
46 | - Mark insufficient evidence explicitly.
47 | - Prefer the smallest coherent experimental surface and avoid speculative extensibility.
48 | 
49 | ## Requested output format
50 | 
51 | - Japanese Markdown.
52 | - Sections: Executive recommendation; repository-grounded findings; candidate requirement; candidate design; candidate plan; Issue decomposition; decision disposition; risks/failure modes; assumptions and insufficient evidence.
53 | - Make the documents detailed enough for subsequent independent spec-reviewer passes.
```

## Answer

# Executive recommendation

## 結論

GitHub connector で `chemitaro/spec-dock` の `main` と指定コミット `081ba64823f66d4efb051fb88e2a160915efdfa0` を確認した。Epic #312 は open であり、指定コミット上の Epic `requirement.md` / `design.md` / `plan.md` は依然として authoring scaffold である。以下は canonical 文書への**採用候補となる evidence draft**であり、Issue の作成、実装準備完了、承認済み仕様を意味しない。

推奨は、採用済み判断を維持したまま、次の三つの child Issue 候補へ直列分解することである。

1. **Workbench ignore と opaque traversal の基盤**
2. **scoped Workbench copy command と deterministic merge**
3. **installed-runtime / dogfood parity / final quality / mergeable PR**

三つ目を明示的な final quality Issue とし、前二つの全実装 Issue に依存させる。これは Epic scaffold が multi-Issue Epic に要求している final-quality policy と、clarification synthesis の `safety -> copy -> dogfood/final gate` 分割に一致する。

ただし canonical authoring の承認前に、次の二点を明示的に disposition する必要がある。

| 項目                                                              | 判定                                                         | 推奨 disposition                                                                                                                                                                    |
| --------------------------------------------------------------- | ---------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 親 Initiative の「local-only は完全廃止」と、本 Epic の local-only Workbench | **needs-human-decision / approval blocker**                | 「廃止対象は local-only node・identity・authority・永続状態であり、Git-ignored disposable scratch は対象外」と解釈することを、親または Epic の承認記録に明記する。解釈を採用しない場合、本 Epic は親 Initiative と矛盾するため reparent または親仕様変更が必要。 |
| FIFO、socket、device node 等を含む「すべて copy」の意味                       | **needs-human-decision / implementation-contract blocker** | regular file、directory、symlink は完全対象とする。安全かつ portable に複製できない special entry は、黙って除外せず preflight error にする案を採る。ただし、これは literal な「file-type filtering なし」との技術的緊張を明示的に承認する必要がある。     |

親 Initiative は「local-only は完全廃止」と定め、temporary local-only workaround の恒久化も受け入れない。一方で Epic 00312 の clarification は Workbench を Git-ignored、local-only、disposable として採用している。これは文書上の実質的な衝突であり、推測で解消してはならない。

---

# Repository-grounded findings

## 1. Epic の現在状態

Epic #312 自体は存在するが、canonical spec は未 authoring である。Epic report も Evidence Adoption Ledger、Objective Alignment Ledger、Spec Authoring Gate の空 scaffold であり、clarification artifact の採用記録はまだ反映されていない。

Clarification synthesis で確定している内容は次のとおりである。

* root/pre-scope Workbench は `spec-dock/.workbench/YYYY-MM-DD/`
* scoped Workbench は Initiative / Epic / Issue directory の direct child `.workbench/`
* Git-ignored、local-only、disposable、non-canonical
* session folder、manifest、TTL、catalog、delete blocker を持たない
* `.workbench/` は runtime-wide reserved opaque subtree
* root Workbench は command で一括 handoff しない
* scoped copy は source=current worktree、scope 一件、target worktree 一件
* nested `.git` を含め、内容による選別をしない
* destination-only file を残し、same-relative-path file は source wins
* provider runtime に一度だけ実装し、`init/update` で experimental 配布する。

Root Workbench はゴミや不要物を含む前提であり、必要な file だけをモデルが通常の filesystem 操作で scoped Workbench へ手動選択する判断が採用されている。

Scoped copy については、形式、拡張子、binary、archive、`.git` 等で選別せず、destination directory 自体を置換しないことが採用されている。当初候補だった symlink / special-file 除外も clarification では採用されなかった。

## 2. 現行 worktree architecture は再利用可能

現行 runtime は、CLI、commands、application、ports、infra、presentation に分離されている。既存 Worktree Epic でも、argparse と command outcome は command layer、target resolution と policy は application layer、Git subprocess は infra adapter、text/JSON は presentation layerという責務が固定されている。

現在の parser は `worktree create/list/show/remove` を公開し、registry は `commands/worktree.py` を module 単位で登録している。新しい Workbench capability は、この構造に沿って別の `workbench` command group として追加できる。

既存 target resolver とテストは次の semantics をすでに持つ。

* stable worktree ID
* absolute path
* directory basename
* branch name は非対応
* 複数候補は `ambiguous_target` と candidates
* Git worktree records を正本とし、SpecDock-managed でない external linked worktree も扱う。

したがって新 command は独自の target-path grammar を追加せず、この resolver **semantics**を再利用すべきである。既存 private function の直接利用を前提にはせず、必要なら shared application-level resolver へ抽出する。

`NodeRepository` port は任意の `specdock_dir` を受けて node records を読み込めるため、source worktree と target worktree の scope を独立に ID 解決できる。一方、現行 `FilesystemGateway` は存在確認と削除のみであり、copy/merge capability の追加または専用 port が必要である。

## 3. `.gitignore` だけでは opaque subtree 契約を満たさない

現在の shipped `.gitignore` には `.workbench/` rule がない。hidden `.gitignore` 自体は package data に明示的に含まれているため、provider asset と installer fallback の両方を更新すれば `init/update` で配布可能である。

より重大なのは recursive scanner である。node metadata loader は `initiatives_root.rglob(".meta.json")` と `rglob("meta.json")` を使用している。このままでは、scoped `.workbench/` 内の scratch `.meta.json` が canonical node metadata として解釈され得る。

legacy runtime path にも同様の recursive scan がある。

Authoring source manifest も selected directory を `rglob("*")` し、現在の除外は symlink と Python cache 程度である。広い source path が選択された場合、Workbench 内 file が source hash へ混入する可能性がある。

Repository-wide search では、provider と dogfood の双方に、template scaffolding、authoring pack、create/delete、delegated authoring、ZIP handling 等の追加 `rglob` callsite が存在する。すべてを無差別に変更するのではなく、Issue 1 で「default repository discovery」と「明示的に指定された file operation」を分類する inventory が必要である。

設計上の invariant は単なる「結果から `.workbench` path を filter する」では不十分である。巨大 subtree、特殊 file、壊れた link、偽 metadata を読まないため、default traversal は `.workbench` directory を見つけた時点で**内部へ descend しない**必要がある。

## 4. Provider / dogfood / update 境界

Provider runtime の正本は `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**`、dogfood mirror は `spec-dock/scripts/spec_dock_runtime/**` である。既存の parity contract は、provider 変更を dogfood 側へ反映し、`spec-dock/initiatives/**`、active metadata、unmanaged file を update で失わないことを要求している。

Repo-local `update` command は upstream package の installer `update` を `uvx --no-cache` で呼び出す thin wrapper である。したがって Workbench 実装と `.gitignore` の authority は provider assets に置き、dogfood 側に別 implementation を置いてはならない。

## 5. Parent Initiative との整合条件

親 Initiative が受け入れるのは architecture concern、state/source-of-truth cleanup、runtime/scaffold/docs parity hardening である。feature value enhancement は受け入れない。

したがって Epic 00312 は「新しい canonical local storage」を追加する Epic としてではなく、次の限定された architecture hardening として記述する必要がある。

* canonical scanner が disposable scratch を解釈しないための reserved-subtree boundary
* linked worktree 間の明示的な local file handoff
* provider/runtime/update parity
* canonical evidence への promotion とは明確に分離された temporary workspace

---

# Candidate requirement — `requirement.md`

```yaml
種別: 要件定義書（Epic）
ID: epic-00312
タイトル: Experimental Local Workbench And Worktree Handoff
状態: draft
親: init-local-00003
関連GitHub: ["#312"]
```

## 1. Problem

SpecDock は canonical specs、accepted ADR/EAL、durable `artifacts/` を管理する一方、調査途中の screenshot、large model output、temporary database、raw notes、downloaded material 等を置く、低摩擦で disposable な local scratch boundary を明示していない。

これらを canonical node directory の通常 file として置くと、recursive scanner、validator、dependency/ADR/context discovery、source manifest が scratch content を意味のある SpecDock artifact として誤解釈する危険がある。逆に OS-level temporary directory だけに置くと、linked worktree 作成後に scope-specific material を引き継ぐ標準経路がない。

## 2. Goals

**E-GOAL-001 — disposable local scratch**

Git-ignored、local-only、non-canonical、scope または worktree とともに消えてよい scratch area を提供する。

**E-GOAL-002 — opaque runtime boundary**

`.workbench/` 内の file name、extension、metadata-like content を、default runtime discovery が canonical artifact として解釈しない。

**E-GOAL-003 — explicit scoped handoff**

利用者が明示した場合だけ、current worktree の Initiative / Epic / Issue 一件の Workbench を、同一 repository の target linked worktree へ copy できる。

**E-GOAL-004 — minimal experimental surface**

Workbench を第二の storage/catalog/session/promotion system にせず、ignore、opaque boundary、明示 copy のみに限定する。

**E-GOAL-005 — provider distribution**

Capability を provider assets/runtime へ一度だけ実装し、`spec-dock init/update` で consumer repository に experimental 配布する。

## 3. Non-goals

次は Epic scope 外とする。

* Workbench content の canonical promotion command
* root Workbench の自動・一括・bulk handoff
* automatic copy-on-worktree-create
* continuous synchronization、bidirectional sync、copy-back
* manifest、session ID、catalog、inbox/curated tree、TTL、retention policy
* secret scanning、archive validation、file allowlist/denylist、size-based selection
* deletion blocker、undelete、backup、transaction log
* arbitrary directory copy または cross-repository copy
* Workbench 内 file の dependency、ADR、context、source artifact としての解釈
* exact filesystem metadata、owner、ACL、extended attribute の cross-platform preservation guarantee
* Codex-managed worktree lifecycle の再実装
* durable evidence の `artifacts/` 以外への移動
* accepted authority の canonical specs / accepted ADR / EAL 以外への移動

Clarification でも shared store、symlink sharing、automatic copy、root copy、filtering、secret scan、TTL、manifest DB、sync/copy-back は棄却または deferred とされている。

## 4. Actors and use cases

### ACT-001 Maintainer / model conducting pre-scope research

`spec-dock/.workbench/YYYY-MM-DD/` に雑多な temporary material を保存する。日付 directory は convention であり、runtime validation 対象ではない。

### ACT-002 Scoped implementation agent

Initiative / Epic / Issue direct child の `.workbench/` に、当該 scope の temporary material を保存する。

### ACT-003 Worktree handoff operator

Worktree 作成後、明示的に一つの scope ID と一つの target worktree を指定し、current worktree の scoped `.workbench/` を target へ copy する。

### ACT-004 Runtime scanner

Default scan 中に `.workbench/` を検出した場合、内部へ descend せず、内容を parse、validate、index、hash、manifest 化しない。

### ACT-005 Consumer repository maintainer

`init/update` 後に capability が experimental と認識でき、既存 Workbench content が update により失われないことを確認する。

## 5. Scope boundaries

### Supported locations

```text
<repo>/
  spec-dock/
    .workbench/
      YYYY-MM-DD/
        ...

    initiatives/
      <initiative-dir>/
        .workbench/
          ...

        epics/
          <epic-dir>/
            .workbench/
              ...

            issues/
              <issue-dir>/
                .workbench/
                  ...
```

User-facing supported placement は上記に限定する。ただし defensive scanner policy は location にかかわらず、path component が `.workbench` であれば opaque として prune する。

### Authority

* `.workbench/`: non-canonical、disposable
* `artifacts/`: durable evidence
* `requirement.md` / `design.md` / `plan.md` / accepted ADR / report EAL: adopted authority
* `.workbench/` の存在または内容は phase completion、review pass、Issue readiness、acceptance の証拠にならない

## 6. Functional requirements

### E-RQ-001 — Git ignore

`spec-dock` は root および任意の supported scope 配下の `.workbench/` を Git ignored にする managed rule を配布しなければならない。

### E-RQ-002 — Root Workbench

Root/pre-scope Workbench は `spec-dock/.workbench/YYYY-MM-DD/` convention を持つ。ただし runtime は date directory を作成、列挙、検証、expire してはならない。

### E-RQ-003 — Scoped Workbench

Initiative / Epic / Issue direct child の `.workbench/` を supported scoped Workbench とする。fine-grained internal organization は要求しない。

### E-RQ-004 — Opaque reserved subtree

Default scanner、validator、node metadata loader、dependency/ADR/context discovery、source-manifest discovery、derived-state generation は `.workbench/` 内へ descend してはならない。

### E-RQ-005 — No content semantics

Runtime は Workbench content を canonical document、node metadata、dependency declaration、ADR、EAL、review evidence、source manifest input として解釈してはならない。

### E-RQ-006 — Explicit scoped copy

Workbench copy は automatic hook ではなく、利用者が command を明示実行した場合だけ発生する。

入力は次の三つに固定する。

1. source: current worktree。明示 source path option は持たない。
2. scope: Initiative / Epic / Issue ID を正確に一件。
3. target: 同一 Git repository の linked worktree を一件。

### E-RQ-007 — Root exclusion

Copy command は root `.workbench/`、date bucket、任意 relative path、topic directory を入力として受け付けてはならない。

### E-RQ-008 — Independent scope resolution

Source worktree と target worktree で scope ID を独立解決する。Directory name や source relative path を target へ文字列置換してはならない。

### E-RQ-009 — Complete scoped tree

Scoped `.workbench/` の directory structure、regular file bytes、symlink entries を再帰的に copy する。extension、binary/text、archive、`.env`、nested `.git` 等による選別を行わない。

### E-RQ-010 — Merge semantics

Destination `.workbench/` を wholesale replacement してはならない。

* destination-only entry は保持する
* source-only entry は作成する
* same-relative-path regular file または symlink は source で置換する
* directory-directory は再帰 merge する
* content-level merge は行わない

### E-RQ-011 — Deterministic incompatible collision

File-like entry と directory の same-path collision は、silent deletion や destination subtree loss を起こしてはならない。Candidate design では mutation 前に fail する。

### E-RQ-012 — No synchronization

Copy 完了後の変更は同期しない。Copy-back、watcher、background process、continuous sync を作らない。

### E-RQ-013 — Safety boundary

Command は次を mutation 前に検証する。

* source と target が同一 canonical worktree でない
* 両 worktree が同一 Git repository の records に属する
* target path が存在し、bare/stale record でない
* source/target scope が expected worktree root 内に containment される
* scoped `.workbench` root とその parent chain が symlink redirection でない
* destination Workbench が effective Git ignore 対象である
* incompatible path-type collision がない

### E-RQ-014 — Failure transparency

Overall tree merge の full transactionality は要求しない。I/O failure 後に一部 mutation が残る場合、command は success を返さず、`partial=true`、完了件数、失敗 relative path を表示する。自動 rollback は行わない。

### E-RQ-015 — Deletion behavior

Scope delete または worktree remove の際、Workbench の存在を blocker にしてはならない。Workbench は scope/worktree とともに消えてよい。

既存 `worktree remove` は untracked content を含む directory を削除できるため、この disposable contract と整合する。

### E-RQ-016 — Experimental exposure

CLI help、text output、JSON output、reference docs は capability が experimental であることを明示する。

### E-RQ-017 — Provider authority and propagation

Implementation authority は `src/spec_dock/assets/spec_dock/**` とする。Dogfood `spec-dock/**` は generated/installed validation surface とし、別実装を持たない。

### E-RQ-018 — Update preservation

`spec-dock update` は既存 root/scoped `.workbench/` content を削除・置換してはならない。Managed runtime/assets は更新し、user-authored initiative tree と unmanaged content は保持する既存契約を維持する。

## 7. Non-functional requirements

### E-NFR-001 — Determinism

Source と destination の同一 snapshot に対して、merge result は deterministic であること。Concurrent mutation がない限り、同一 command の再実行は idempotent であること。

### E-NFR-002 — Containment

Command 自身が source/target scope 外の content を dereference または write しないこと。Descendant symlink は link object として扱い、copy traversal では follow しない。

### E-NFR-003 — No content disclosure

Default output は file contents、secret-like values、full entry listingを表示しない。必要な diagnostic は counts、scope/worktree paths、失敗 relative path に限定する。

### E-NFR-004 — Complexity

Traversal cost は source tree と destination collision check に対して線形を基本とする。Catalog、database、hash manifest、content scanner を導入しない。

### E-NFR-005 — Portability

Python 3.10 以上および repository が既にサポートする filesystem 環境で動作する。Ownership、ACL、xattr、device semantics の portable fidelity は保証しない。Python requirement と test/static-analysis dependencies は現行 package metadata に定義されている。

### E-NFR-006 — Testability

Resolution、path policy、merge planning、copy execution、rendering は既存 layer boundary に従い、subprocess と filesystem を adapter 経由で差し替え可能にする。

## 8. Acceptance criteria

| ID       | Given / When                                                                                                                                  | Then                                                                                                                                       |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| E-AC-001 | Fresh `init` または `update` 後に root、Initiative、Epic、Issue 配下へ `.workbench/probe` を置く                                                            | 全 location が Git ignored である                                                                                                               |
| E-AC-002 | `.workbench/` 内に偽 `.meta.json`、legacy `meta.json`、dependency-like JSON、ADR-like Markdown を置き、validate/sync/deps/context/source-manifest を実行する | それらは読まれず、エラー、node、dependency、manifest entry を生成しない                                                                                         |
| E-AC-003 | Root `.workbench/YYYY-MM-DD/` に file がある                                                                                                      | CLI に root bulk-copy route がなく、scoped copy でも root は選択できない                                                                                 |
| E-AC-004 | Current worktree の既存 Issue scoped Workbench と、別 linked worktree の同一 Issue が存在する                                                               | Explicit copy により target Issue direct childへ内容が配置される                                                                                       |
| E-AC-005 | Target を worktree ID、absolute path、basename で指定する                                                                                             | 既存 resolver semantics と同じ target が選ばれる。Branch-only は拒否される                                                                                  |
| E-AC-006 | Target basename が複数 record に一致する                                                                                                              | mutation 前に ambiguous error と candidates を返す                                                                                               |
| E-AC-007 | Destination-only file、source-only file、same-path file、directory-directory が混在する                                                               | destination-only を保持、source-only を追加、same-path file を source で上書き、directory を merge する                                                     |
| E-AC-008 | Source に binary、ZIP、`.env`、nested `.git`、relative/broken symlink がある                                                                          | 内容分類をせず、regular entries と symlink entries を copy する。Symlink target は traversal しない                                                         |
| E-AC-009 | Same canonical worktree を別 selector または symlink alias で target にする                                                                            | `same_worktree` 相当の error で mutation しない                                                                                                   |
| E-AC-010 | Source/target scope 不在、unsupported scope kind、duplicate/ambiguous scope metadata がある                                                          | 明示 error で mutation しない                                                                                                                    |
| E-AC-011 | Source file と destination directory、またはその逆が same-relative-path で衝突する                                                                          | preflight で停止し、既存 destination content を削除しない                                                                                               |
| E-AC-012 | Copy 中に permission、disk-full、race 等の I/O failure を注入する                                                                                        | nonzero exit、`partial` state、completed counts、failed relative path を返し、success を主張しない                                                      |
| E-AC-013 | Command 完了後に source または target を変更する                                                                                                          | 反対側へ自動同期されない                                                                                                                               |
| E-AC-014 | Scope/worktree delete を実行する                                                                                                                   | Workbench の存在は blocker にならず、通常の scope/worktree lifecycle に従って消える                                                                           |
| E-AC-015 | Package/install/update smoke を実行する                                                                                                            | Provider runtime、installed consumer runtime、dogfood mirror が一致し、既存 Workbench content が保持される                                                |
| E-AC-016 | CLI help、text、JSON を確認する                                                                                                                      | `experimental` state、scope、source/target、merge result、partial/error state が観測可能で、file contents は表示されない                                     |
| E-AC-017 | Epic spec approval を試みる                                                                                                                       | 親 Initiative の local-only wording と special-entry policy の human disposition が report EAL / spec-review evidence に記録されていなければ promotion しない |

## 9. Assumptions

* Copy 対象は同一 Git repository の linked worktree に限定する。
* Managed classification は diagnostic であり、external linked worktree も target にできる。
* Target worktree に同一 scope ID が存在しない場合、自動作成しない。
* Empty source `.workbench/` は success とし、empty destination `.workbench/` を作成する。
* Regular file bytes と symlink target が content contract であり、full POSIX metadata fidelity は contract 外とする。
* No concurrent writer を通常利用前提とする。Concurrent mutation は race/error として扱う。

## 10. Risks

* `.workbench/` pruning の callsite 漏れ
* Symlink root による containment escape
* Old target branch に ignore rule がなく、copied content が untracked になる
* Partial copy と operator の誤認
* Nested `.git` による third-party tooling の混乱
* Secret や不要物をそのまま target へ複製すること
* Scope/worktree deletionで唯一の copy が消えること
* Parent Initiative の local-only policy との文書衝突

## 11. Unresolved items

**U-001 — Parent Initiative interpretation**

Canonical approval blocker。親の「local-only 完全廃止」を local-only canonical state に限定して解釈するか、人間による明示判断が必要。

**U-002 — Special filesystem entries**

Socket、FIFO、device node 等について、portable complete copy は安全に保証できない。推奨は silent skip せず、mutation 前に `unsupported_entry_type` とすること。Literal な adopted wording からの例外として human disposition が必要。

---

# Candidate design — `design.md`

## 1. Architecture

新 capability は既存 layered runtime に次のように配置する。

| Layer                           | Candidate responsibility                                                               |
| ------------------------------- | -------------------------------------------------------------------------------------- |
| `cli/parser.py`                 | `workbench copy` parser と experimental help                                            |
| `cli/registry.py`               | `commands/workbench.py` の command specs 登録                                             |
| `commands/workbench.py`         | Args → application request、result/error → presentation                                 |
| `application/contracts.py`      | Copy request/result、target/scope views、structured error                                |
| `application/workbench.py`      | Worktree resolution、scope resolution、preflight、merge policy、partial-result aggregation |
| `application/ports.py`          | Git ignore probe、filesystem inspect/copy/replace operations                            |
| `infra/git_cli.py`              | Git worktree records と effective-ignore check                                          |
| `infra/fs_cli.py` または専用 adapter | `lstat`、non-following traversal、directory creation、regular file/symlink replacement    |
| `infra/fs_repo.py` 等            | Default scanner の opaque-prune policy                                                  |
| `presentation`                  | Text/JSON rendering                                                                    |
| `cli/bootstrap.py`              | Use case と adapter wiring                                                              |

既存 Worktree contract は request/result dataclass、structured `WorktreeCommandError`、Git gateway、filesystem gateway を持つ。新 design はこの形式を踏襲し、command layer から `subprocess` や `shutil` を直接呼ばない。

## 2. Candidate CLI contract

```text
spec-dock workbench copy --scope <init-|epic-|iss-ID> --to <WORKTREE_TARGET> [--json]
```

### Arguments

* `--scope`: 必須、exactly one Initiative / Epic / Issue ID
* `--to`: 必須、既存 worktree resolver semantics に従う ID / absolute path / basename
* `--json`: machine-readable output
* source option: なし。Source は current worktree
* root path、relative path、date、glob、複数 scope option: なし

### Availability

* Worktree 作成 command の hook にはしない
* `worktree create` の成功直後でも自動実行しない
* `SPEC_DOCK_WORKTREE_ROOT` は要求しない
* Git worktree records を正本とする
* managed / external classification は diagnostic であり eligibility blocker ではない

既存 `list/show/remove` も Git records を正本とし、`SPEC_DOCK_WORKTREE_ROOT` がない場合は classification unavailable として動作する。

## 3. Worktree resolution

### Source

1. Runtime の current repository root を取得する。
2. `git worktree list --porcelain` の records を読む。
3. Current repository root の canonical path と一致する record を一件解決する。
4. Record 不在、bare、path missing は fail する。

Git adapter は既に porcelain records を path/head/branch/detached/bare/locked へ変換する。

### Target

既存 resolver semantics を使用する。

* exact stable ID
* exact canonical absolute path
* exact basename
* branch-only は拒否
* zero match は `target_not_found`
* multiple match は `ambiguous_target` と candidates
* path missing / bare は拒否

### Same-worktree guard

Source と target は lexical path ではなく canonical filesystem identity で比較する。ID、basename、symlink alias が異なっても同一 resolved path なら拒否する。

### Repository identity

Target は source の `git worktree list` に含まれる record だけを認める。任意 directory を `--to` へ渡して copy する route は設けない。

## 4. Scope resolution

Source と target で独立して次を行う。

1. `<worktree>/spec-dock/` の存在を確認する。
2. `NodeRepository.load_node_records(specdock_dir)` 相当で node records を読む。
3. Exact ID が一件だけ存在することを確認する。
4. Kind が `initiative | epic | issue` であることを確認する。
5. Record path が当該 worktree の `spec-dock/initiatives/` 配下に containment されることを確認する。
6. Source scope path と target scope path をそれぞれ確定する。
7. `<scope>/.workbench/` を source/destination とする。

Source directory name を target へ転写しない。Branch 間で slug rename や hierarchy change があっても、ID 解決結果を使う。

Target scope 不在時に node、directory、`.meta.json` を自動作成しない。

## 5. Reserved opaque subtree policy

### Invariant

Default repository traversal は、directory entry の basename が `.workbench` なら、その entry 自体を opaque boundary として扱い、descendant を列挙しない。

### Applies to

最低限、Issue 1 の scanner inventory で次を確認する。

* canonical `.meta.json` discovery
* legacy `meta.json` detection
* expected node-directory checks
* validate/sync/deps readers
* ADR/context/active discovery
* source-manifest discovery
* provider installer fallback lookup
* derived-state and authoring default source discovery

### Does not automatically apply to

* `workbench copy` の明示 source traversal
* 利用者が明示的に指定した generic file input のうち、canonical repository discovery ではないもの

したがって、各 `rglob` callsite は次の分類を持つ。

1. **default semantic discovery**: `.workbench` を prune
2. **explicit opaque-copy operation**: `.workbench` を意図的に traverse
3. **explicit unrelated file input**: 既存 contract を維持し、個別判断

単に `rglob` 後の list comprehension で path を除外するのではなく、directory walker 自体で descend を止める。

## 6. Git ignore contract

Provider asset の managed `.gitignore` と installer fallback の双方へ、任意階層の `.workbench/` に適用される rule を追加する。

Runtime copy preflight でも、source と destination Workbench の probe path が effective Git ignore 対象であることを確認する。

* ignore されていない場合は fail closed
* `.gitignore` を copy command が自動編集しない
* Error は target で `spec-dock update` または branch update が必要であることを示す
* Global ignore で有効になっている場合は許可する
* Negation rule によって unignore される場合は拒否する

## 7. Path and symlink safety

### Scope and Workbench roots

次の component は symlink であってはならない。

* target worktree root から `spec-dock`
* `spec-dock/initiatives`
* resolved node path までの parent chain
* source `.workbench` root
* destination `.workbench` root

理由は、copy root 自体の symlink を許すと、source scope 外を read したり target scope 外へ write したりできるためである。

### Descendant symlinks

Scoped Workbench 内の symlink は除外しない。

* `lstat` で link object として読む
* directory symlink を traversal しない
* relative、absolute、broken symlink の target text をそのまま複製する
* target filesystem 上で link を再作成する
* link 先が Workbench 外でも、copy operation 自身は dereference しない

これは「symlinked content を選別しない」と containment を両立する最小設計である。

## 8. Copy preflight

Mutation 前に二段階 preflight を行う。

### Phase A — structural preflight

* source/target worktree resolution
* same-worktree detection
* source/target `spec-dock` existence
* scope ID uniqueness/kind
* scope containment
* source Workbench existence and directory type
* destination Workbench absent または directory
* Workbench root symlink rejection
* effective Git ignore check

### Phase B — tree-shape preflight

Source subtree を symlink-follow なしで走査し、destination の対応 entry を `lstat` する。

* directory-directory: compatible
* leaf-leaf: compatible、source replacement
* absent: compatible
* directory-leaf または leaf-directory: incompatible
* unsupported special entry: provisional human-decision policy に従い fail

Tree-shape failure 時には destination を一切 mutation しない。

## 9. Merge semantics

| Source       | Destination            | Result                     |
| ------------ | ---------------------- | -------------------------- |
| directory    | absent                 | directory を作成し再帰 copy      |
| directory    | directory              | 再帰 merge                   |
| regular file | absent                 | copy                       |
| regular file | regular file / symlink | source bytes で置換           |
| symlink      | absent                 | link を作成                   |
| symlink      | regular file / symlink | source link で置換            |
| leaf         | directory              | preflight error            |
| directory    | leaf                   | preflight error            |
| absent       | any                    | destination-only entry を保持 |

「leaf」は regular file または symlink を意味する。Special filesystem entry の handling は U-002 disposition に従う。

Directory tree の wholesale deletion は行わない。Content-aware merge、line merge、archive extraction、Git repository interpretationを行わない。

## 10. Mutation strategy and partial failure

### Per-entry behavior

* Destination directory は必要時に作る。
* Regular file overwrite は可能な限り destination sibling temporary file へ書き、同一 filesystem の replace で切り替える。
* Symlink overwrite も target object を follow せず置換する。
* Temporary entry は失敗時に best-effort cleanup する。
* Source metadata の owner、ACL、xattr は authority としない。

### Overall atomicity

Tree 全体を transaction 化しない。Shadow tree を作って destination `.workbench` 全体と swap すると、destination-only file preservation と競合し、実装も複雑になるためである。

I/O failure 時:

* 即時停止
* exit code nonzero
* `partial=true`
* completed/created/overwritten counts
* failed relative path
* destination は部分更新され得る
* rollback、copy-back、manifest replay は行わない
* 原因修正後の同一 command 再実行を recovery path とする

Concurrent source/destination writer に対する lock は導入しない。Last-writer behavior と filesystem error が residual risk となる。

## 11. Error model

既存 `WorktreeCommandError` と同様の structured expected-error pattern を採る。

Candidate error categories:

| Code                         | Condition                        | Mutation         |
| ---------------------------- | -------------------------------- | ---------------- |
| `source_worktree_unresolved` | Current path が Git record と一致しない | none             |
| `target_not_found`           | Target 0件                        | none             |
| `ambiguous_target`           | Target 複数                        | none             |
| `unsupported_branch_target`  | Branch-only selector             | none             |
| `same_worktree`              | Source と target が同一              | none             |
| `target_not_checkout`        | Bare/stale/missing target        | none             |
| `scope_not_found`            | Source または target scope 不在       | none             |
| `ambiguous_scope`            | Duplicate ID / invalid tree      | none             |
| `unsupported_scope_kind`     | ADR 等                            | none             |
| `source_workbench_not_found` | Source `.workbench/` 不在          | none             |
| `workbench_not_directory`    | Root が file 等                    | none             |
| `workbench_root_symlink`     | Root/parent symlink              | none             |
| `workbench_not_ignored`      | Git ignore invariant 不成立         | none             |
| `path_type_collision`        | file-directory collision         | none             |
| `unsupported_entry_type`     | U-002 対象                         | none             |
| `copy_io_failed`             | Mutation 中 I/O error             | possibly partial |

Argparse error は既存 CLI と同様 exit `2`、operational error は exit `1`、success は `0` とする。

## 12. Output and observability

### Text success

少なくとも次を表示する。

* `experimental`
* scope ID/kind
* source worktree absolute path
* target worktree absolute path
* source/destination Workbench path
* merge policy `recursive-source-wins`
* created / overwritten / symlink / preserved-destination counts
* `partial=false`

### JSON success

Candidate fields:

* `status: "ok"`
* `experimental: true`
* `command: "workbench.copy"`
* `scope`
* `source_worktree`
* `target_worktree`
* `source_workbench`
* `destination_workbench`
* `merge_policy`
* `created_entries`
* `overwritten_entries`
* `destination_only_preserved`
* `symlinks_copied`
* `partial: false`
* `warnings`

### JSON expected error

* `status: "error"`
* `experimental: true`
* `error.code`
* `error.message`
* `scope`
* `target`
* `candidates`
* `failed_relative_path`
* `partial`
* completed counts

Existing worktree JSON expected failures は stdout に structured error を返すため、この convention を維持する。

Output は file content、hash、secret detection result、全 file list を含めない。

## 13. Install and update propagation

1. Provider assets/runtime を変更する。
2. Hidden `.gitignore` package-data coverage を確認する。
3. Isolated `init` で new consumer を作る。
4. Root/scoped ignore behavior を検証する。
5. Existing consumer に root/scoped Workbench と stale runtime file を配置する。
6. Provider checkout/package から `update` を実行する。
7. Runtime と `.gitignore` が更新され、Workbench と initiatives が保持されることを確認する。
8. Dogfood mirror を update-generated state に揃える。
9. Provider/dogfood full-tree parity を確認する。

Dogfood-only implementation や provider/dogfood への手動二重編集は認めない。

## 14. Testing strategy

### Opaque traversal tests

* Workbench 内 fake `.meta.json` が node scan に入らない
* legacy `meta.json` detector が Workbench 内を見ない
* `validate`, `sync`, `deps` の checked-node count / output が不変
* source manifest に Workbench entry が入らない
* Root、Initiative、Epic、Issue の全 placement
* Deep nested `.workbench/.workbench/`
* Large Workbench でも scanner が descendant へ入らないことを probe で確認

### Ignore/install tests

* Fresh init の全 placement が `git check-ignore`
* Update 後も全 placementが ignored
* Existing Workbench bytes 保持
* Existing initiative/user file 保持
* Packaged wheel/local checkout 両経路
* Provider/dogfood asset parity

### Resolution tests

既存 `tests/cli_runtime/test_worktree.py` の fixture と semantics を拡張する。

* ID/path/basename target
* external linked target
* main checkout target
* branch-only reject
* ambiguous basename candidates
* stale/bare/missing path
* same target via ID/path/symlink alias
* source/target scope independent rename
* source/target scope missing
* duplicate ID / invalid target tree

### Merge tests

* Empty source
* Empty destination
* Deep directory
* binary、ZIP、`.env`
* nested `.git`
* relative/absolute/broken symlink
* source file overwrite
* destination-only preserve
* directory merge
* repeated execution
* file-directory collision and zero mutation
* permission failure
* disk-full/replace failure injection
* partial-result counts
* special entry test、platform capability に応じて skip または expected error

### Regression and quality gates

* Focused new tests
* Existing worktree/validate/sync/update test suites
* `uv run pytest`
* `make lint`

Current `make lint` runs `ruff check`、`ruff format --check`、`mypy` over `src/spec_dock` and `tests`.

## 15. Rejected alternatives

| Alternative                         | Rejection reason                                 |
| ----------------------------------- | ------------------------------------------------ |
| Root Workbench bulk copy            | Root は雑多で不要物を含む。Product owner が明示棄却              |
| Automatic copy on `worktree create` | 明示 user direction と no-sync boundary に反する        |
| Shared central Workbench store      | 第二の managed storage system になる                   |
| Session/manifest/catalog/TTL        | Low-friction disposable goal を壊す                 |
| Secret scan / allowlist / denylist  | Content interpretation を command 責務へ持ち込む         |
| Destination directory replacement   | Destination-only content を失う                     |
| Content-level merge                 | File semantics を解釈する必要がある                        |
| Backup/rollback transaction tree    | Manifest/state/complexityを追加する                   |
| Cross-repository target             | Existing same-repository worktree authority から逸脱 |
| Branch-name target                  | Existing target contract が明示拒否している               |
| Dogfood-only implementation         | Provider/dogfood drift を生む                       |
| `.gitignore` だけの対応                  | Runtime scanner が内容を解釈し続ける                       |
| Post-`rglob` filtering              | Descendant traversal 自体を止められない                   |

---

# Candidate plan — `plan.md`

## 1. Epic classification

* **Classification:** multi-Issue implementation Epic
* **Final quality Issue:** required
* **Recommended Issue count:** 3
* **Execution order:** W1 → W2 → W3
* **Issue nodes:** 未作成
* **Implementation readiness:** 未承認
* **Canonical start condition:** requirement/design/plan の fresh spec review pass と U-001/U-002 disposition

## 2. Dependency-ordered phases

| Phase | Candidate Issue                        | Main outcome                                     | Entry gate                     | Exit gate                                                           |
| ----- | -------------------------------------- | ------------------------------------------------ | ------------------------------ | ------------------------------------------------------------------- |
| P0    | Canonical alignment gate               | 親 conflict、special-entry policy、EAL adoption を確定 | Current clarification evidence | Human disposition、requirement review pass                           |
| P1    | W1 Opaque Workbench Foundation         | Ignore + scanner prune + regression foundation   | P0 pass                        | Fake metadata/source manifest/validate regressions pass             |
| P2    | W2 Scoped Copy Command                 | Explicit copy + resolver + merge + safety/output | W1 complete                    | Full copy/error/partial matrix pass                                 |
| P3    | W3 Installed Runtime And Final Quality | Update/package/dogfood/docs/full QA/mergeable PR | W1+W2 complete                 | Final spec/code review、full tests、provider parity、PR-ready evidence |

## 3. P0 — Authoring and governance gate

1. Clarification artifacts を report EAL に disposition する。
2. Parent Initiative の local-only wordingを human review へ提示する。
3. Special filesystem entries の扱いを human review へ提示する。
4. Candidate requirement を canonical `requirement.md` へ統合する。
5. Fresh requirement reviewer pass を得る。
6. Candidate design を統合し fresh design reviewer pass を得る。
7. Candidate plan を統合し fresh plan reviewer pass を得る。
8. Child Issue 作成は上記 pass 後に限る。

Epic report scaffold は delegated evidence の採否、reviewer verdict、blocking state を記録することを要求している。

## 4. P1 — W1 verification gate

必須 evidence:

* Managed `.gitignore` asset と installer fallback
* 全 supported placement の ignore test
* Default scanner callsite inventory artifact
* Node/legacy metadata scanner prune
* Source-manifest prune
* Validate/sync/deps/context regression
* Workbench 内 invalid/fake content が無視される証拠
* Provider source only implementation
* Focused pytest + static analysis

Gate failure 時は W2 を開始しない。Copy command が scanner safety より先に導入されると、copied fake metadata を target runtime が canonical content と誤認し得るためである。

## 5. P2 — W2 verification gate

必須 evidence:

* CLI help と experimental marker
* Existing worktree resolver semantics parity
* Source/current and target/same-repo proof
* Independent source/target scope resolution
* Root Workbench exclusion
* Ignore preflight
* Path containment and symlink-root guards
* Recursive merge
* Source-wins leaf replacement
* Destination-only preservation
* Type-collision zero-mutation failure
* Nested `.git` / binary / archive / `.env`
* Symlink non-follow behavior
* Same-worktree rejection
* Partial I/O result
* Text/JSON result and error tests
* No automatic sync/copy-back

Gate failure 時は W3 の final integration を開始しない。

## 6. P3 — W3 final quality and mergeable-PR gate

W3 は final quality Issue とする。

Dependencies:

* W3 depends on W1
* W3 depends on W2

W3 が所有するもの:

* Provider assets/runtime final synchronization
* Dogfood update-generated mirror
* Package/local checkout init/update smoke
* Existing Workbench preservation
* User-facing reference docs
* CLI help review
* Model/workflow guidanceにおける root manual-selection rule
* Full test suite
* `make lint`
* Provider/dogfood full-tree parity
* Manual scenario summary
* Fresh code review
* Fresh final spec review
* Epic report/EAL/AC closure
* Push と mergeable PR preparation

W3 は新しい product semantics を追加しない。W1/W2 で固定された contract の integration、repair、documentation、quality closure に限定する。

## 7. Provider / dogfood synchronization

推奨 sequence:

1. W1/W2 は provider source を変更する。
2. Focused provider tests を実行する。
3. Isolated target へ local package `init/update` を行う。
4. Dogfood mirror は installer/update 経路で反映する。
5. Provider と dogfood の全 runtime inventory parity を検証する。
6. Generated caches は比較対象外とする。
7. Drift があれば W3 内で修復し、手動二重実装として残さない。

既存 parity Issue は subset comparison では新規 file 漏れを見逃すため、全 inventory parity を要求している。

## 8. PR delivery policy

Reviewed Epic plan が採用した場合、W1/W2 は per-Issue PR を作らず、W3 へ PR delivery を relay する。

W1/W2 report には次を記録する。

* final quality Issue candidate/実 ID
* dependency edge
* no-per-Issue-PR rationale
* merge-prepared claim をしていないこと
* remaining final PR gate

W3 は deferred PR delivery を使用できず、Epic-level PR と merge preparation を所有する。これは current Epic plan scaffold の final quality policy と一致する。

---

# Issue decomposition

以下は evidence draft である。`iss-*` node や GitHub child Issue が存在するとは主張しない。

## W1 — Experimental Workbench Ignore And Opaque Traversal Foundation

### Objective

`.workbench/` を Git-ignored reserved subtree とし、SpecDock の全 default semantic discovery が内部を解釈しない基盤を作る。

### Scope

* Provider `.gitignore` asset
* Installer fallback
* Reserved opaque-path predicate / prunable walker
* `fs_repo.py` metadata scans
* legacy/runtime scanner path
* source-manifest discovery
* scanner callsite inventory と分類
* validate/sync/deps/context regression tests
* update preservation test

### Non-scope

* Workbench copy command
* Root Workbench helper
* Content filtering
* Catalog/manifest/TTL
* User-facing final documentation
* PR preparation

### Dependencies

* P0 human disposition and canonical spec-review pass

### Deliverables

* Provider-side ignore changes
* Provider-side traversal policy
* Scanner inventory artifact
* Focused unit/integration tests
* W1 implementation report
* W3 への deferred PR delivery evidence

### Acceptance criteria

1. Root、Initiative、Epic、Issue Workbench が ignored。
2. Default scanner は `.workbench` へ descend しない。
3. Fake metadata、ADR、dependency、source files が canonical outputへ入らない。
4. Explicit unrelated file operations の既存 contract を無差別に変更しない。
5. Existing Workbench content は update で保持される。
6. Provider source が唯一の implementation authority。

### Tests

* Node record loading
* Legacy metadata detection
* Validate/sync/deps
* Source manifest
* Git ignore matrix
* Init/update preservation
* Large/invalid Workbench subtree prune
* Existing CLI regression
* Static analysis

### Draft-requirement handoff

* **Parent trace:** E-RQ-001–005、E-RQ-015、E-RQ-017–018
* **Allowed local delta:** scanner inventoryに基づく最小 callsite修正
* **Forbidden changes:** copy command、Workbench schema、content validation
* **Acceptance seed:** E-AC-001、002、014、015
* **Constraints:** Result filteringではなく traversal pruning。Provider-only implementation。

---

## W2 — Experimental Scoped Workbench Copy And Source-Wins Merge

### Objective

Current worktree の一つの Initiative / Epic / Issue Workbench を、一つの same-repository target worktree へ explicit copy する layered runtime command を実装する。

### Scope

* `workbench copy` parser/registry
* Request/result/error contracts
* Existing worktree target semantics reuse
* Current-source resolution
* Independent source/target scope resolution
* Git ignore preflight
* Containment/symlink-root guards
* Recursive non-follow traversal
* Source-wins merge
* Destination-only preservation
* Type-collision preflight
* Partial-I/O reporting
* Text/JSON presentation
* Focused tests

### Non-scope

* Root Workbench copy
* Automatic worktree-create hook
* Cross-repository copy
* Content classification、secret scan、archive extraction
* Sync/copy-back
* Catalog、manifest、rollback database
* Final package rollout/PR

### Dependencies

* W1 complete

### Deliverables

* Provider command/application/port/infra/presentation changes
* Copy contract tests
* Error/output schema tests
* Manual test fixture
* W2 implementation report
* W3 deferred PR evidence

### Acceptance criteria

1. Source=current、scope=exactly one、target=exactly one。
2. Root Workbench は選択不可。
3. ID/path/basename target semantics は既存 worktree command と一致。
4. Same worktree、missing/ambiguous target、missing scope は mutation 前に fail。
5. Full scoped tree を content selection なしで copy。
6. Destination-only preserve、same-path leaf source wins。
7. File-directory collision は zero-mutation failure。
8. Symlink は follow せず link として copy。
9. Nested `.git` は ordinary subtree name として copy。
10. Partial failure は success にならない。
11. No automatic sync/copy-back。
12. Help/text/JSON は experimental。

### Tests

* Existing `test_worktree.py` resolver fixture reuse
* New candidate `test_workbench.py`
* All target selector forms
* External target
* Main target
* Same-worktree aliases
* Source/target renamed scope
* Root exclusion
* Empty/nonempty merge
* Binary/archive/`.env`/nested `.git`
* Symlink matrix
* Type collision
* Repeated run
* Permission/replace failure
* Partial count/output
* JSON expected errors

### Draft-requirement handoff

* **Parent trace:** E-RQ-006–014、E-RQ-016
* **Allowed local delta:** Exact error names、result-field naming、adapter granularity
* **Forbidden changes:** Root command、filtering、sync、destination wholesale replacement
* **Acceptance seed:** E-AC-003–013、016
* **Constraints:** Same-repository Git records only。No content logging。U-002 disposition mandatory。

---

## W3 — Installed Runtime, Dogfood Parity, Final Quality And Mergeable PR

### Objective

W1/W2 を installed consumer と dogfood surface へ配布し、full regression、documentation、review、Epic closure、mergeable PR を完成させる。

### Scope

* Provider/dogfood synchronization
* Package-data verification
* Fresh init smoke
* Existing target update smoke
* Existing Workbench preservation
* Full-tree runtime parity
* User-facing reference docs
* CLI help polish
* Root manual-selection guidance
* Experimental status documentation
* Full test suite and static analysis
* Manual scenario summary
* Code review / spec review repair loop
* Epic report EAL/OAL/AC closure
* PR preparation

### Non-scope

* 新 product semantics
* Copy algorithm redesign
* Root helper
* Secret scanning
* Additional promotion workflow
* General installer refactor
* Unrelated scanner refactor

### Dependencies

* W1 complete
* W2 complete

### Deliverables

* Installed runtime/assets
* Updated dogfood mirror
* Reference documentation
* Package/init/update evidence
* Full quality evidence
* Final reports and ledgers
* Mergeable Epic PR

### Acceptance criteria

1. Fresh package install で Workbench capability が利用可能。
2. Existing consumer update で runtime/ignore が更新される。
3. Existing root/scoped Workbench bytes が保持される。
4. Provider/dogfood runtime inventory が一致。
5. Generated cache は parity 対象外。
6. Full pytest と static analysis が pass。
7. Docs/help に experimental、root manual rule、no sync、no canonical authority が記載。
8. Final spec reviewer と code reviewer の blocking finding がない。
9. Epic E-AC coverage が report へ trace される。
10. Human approval前に merge-ready claim をしない。

### Tests and gates

* W1/W2 focused suites
* Existing worktree/validate/sync/update suites
* `uv run pytest`
* `make lint`
* Isolated wheel/local checkout smoke
* Provider/dogfood inventory diff
* `git check-ignore` placement matrix
* Manual worktree handoff scenario
* Final dirty-tree scope review
* Final spec/code review

### Draft-requirement handoff

* **Parent trace:** E-RQ-016–018、全 E-NFR、E-AC-015–017
* **Allowed local delta:** Documentation wording、test fixture details、repair-only changes
* **Forbidden changes:** New product decisions、new storage/catalog semantics
* **Acceptance seed:** 全 Epic AC closure
* **Constraints:** W3 owns final PR。W1/W2 の unreviewed semantic change を黙って吸収しない。

---

# Decision disposition

| ID    | Disposition          | Decision                                                          | Reasoning                                                          | Evidence                                                                               |
| ----- | -------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------------ | -------------------------------------------------------------------------------------- |
| D-001 | adopted              | Root Workbench は `spec-dock/.workbench/YYYY-MM-DD/`               | Pre-scope、messy、non-managed convention                             | `.../20260713t003208z-disc-workbench-clarification-synthesis-and-authoring-handoff.md` |
| D-002 | adopted              | Scoped Workbench は Initiative/Epic/Issue direct child             | Scope-local disposable context                                     | 同上                                                                                     |
| D-003 | adopted              | Git-ignored、local-only、disposable、non-canonical                   | Clarification の中心 product decision                                 | 同上                                                                                     |
| D-004 | adopted              | Session/manifest/TTL/catalog/delete blocker を持たない                 | 第二の management system を避ける                                         | 同上                                                                                     |
| D-005 | adopted              | Runtime-wide opaque subtree                                       | Scanner 誤解釈を防ぐ                                                     | 同上                                                                                     |
| D-006 | adopted              | Root の command copy は作らず、必要 file のみ手動選択                           | Root は不要物を多く含む                                                     | Root interview                                                                         |
| D-007 | adopted              | Scoped copy は current source + one scope ID + one target worktree | Explicit、minimal handoff                                           | Synthesis                                                                              |
| D-008 | adopted              | File type、extension、archive、nested `.git` で選別しない                  | Low-friction、content-opaque                                        | File-policy interview                                                                  |
| D-009 | adopted              | Destination-only preserve、same-path file source wins              | Product owner が Option A を選択                                       | Collision interview                                                                    |
| D-010 | adopted              | No sync / no copy-back                                            | One-time handoff boundary                                          | Synthesis                                                                              |
| D-011 | adopted              | Provider implementation、`init/update` 全 consumer 配布、experimental  | Dogfood-only lane を避ける                                             | Rollout interview                                                                      |
| D-012 | refined              | Target は existing ID/path/basename resolver semantics を使用         | Current architecture/test が既に contract を持つ                         | Worktree tests/docs                                                                    |
| D-013 | refined              | Target は managed-only でなく同一 repo の external linked worktree も許可   | Existing worktree family は external records も first-class に扱う      | Reference docs                                                                         |
| D-014 | refined              | Source/target scope は ID で独立解決                                    | Branch 間の slug/path drift に耐える。Current NodeRepository contract で可能 | Ports                                                                                  |
| D-015 | refined              | Workbench root symlink は拒否、descendant symlink は link として copy     | Containment と「symlink 除外なし」を両立                                     | Product decision は symlink exclusion を不採用                                              |
| D-016 | refined              | File-directory collision は mutation 前に fail                       | Source placementとdestination-only preservationを同時に満たせないため          | Clarification は Issue-local technical design として残した                                    |
| D-017 | refined              | Full transaction/rollback なし、partial state を明示                    | Manifest/backup systemを導入せず、失敗を隠さない                                | Collision artifact の test seed                                                         |
| D-018 | refined              | Runtime で destination effective-ignore を preflight                | Old target branch への accidental untracked copy を防ぐ                 | Git-ignore が product invariant                                                         |
| D-019 | rejected             | Root bulk copy、attach helper、automatic root transfer              | Product owner が明示棄却                                                | Root interview                                                                         |
| D-020 | rejected             | Content scanner、allow/deny list、secret scan                       | Adopted low-friction boundaryに反する                                  | File-policy interview                                                                  |
| D-021 | rejected             | Destination `.workbench` wholesale replacement                    | Destination-only preservationに反する                                  | Collision interview                                                                    |
| D-022 | rejected             | Dogfood-only duplicate implementation                             | Provider parityを壊す                                                 | Rollout interview                                                                      |
| D-023 | needs-human-decision | Parent Initiative の local-only wording                            | Literal wordingでは本 Epic と衝突                                        | Parent requirement/design                                                              |
| D-024 | needs-human-decision | FIFO/socket/device 等の special entry                               | Portable/safe complete copy を保証できず、literal no-type-filtering と緊張   | Special exclusions were explicitly not adopted                                         |
| D-025 | refined              | No ADR at this stage                                              | Experimentalで可逆、Epic-local contract。Hard-to-reverseではない            | Synthesis ADR triage                                                                   |

---

# Risks and failure modes

| Failure mode                                 | Required handling                             | Residual risk / verification                |
| -------------------------------------------- | --------------------------------------------- | ------------------------------------------- |
| Scope path が worktree 外を指す                   | Source/targetそれぞれ canonical containment check | Symlink/race を unit test                    |
| Scope parent または `.workbench` root が symlink | Preflight reject                              | Descendant symlink は link object として許可      |
| Descendant symlink が外部を指す                    | Follow せず link target text を copy             | Target上で link を開く操作は command scope外         |
| Same worktree を別 selector で指定                | Canonical identity comparisonで reject         | ID/path/basename/symlink alias tests        |
| Target worktree 不在                           | `target_not_found`、mutationなし                 | Git recordsがauthority                       |
| Basename ambiguous                           | candidates付き error                            | Existing worktree semantics parity          |
| Branch-only selector                         | reject                                        | Existing contract維持                         |
| Target record はあるが path missing/bare         | fail closed                                   | Stale Git metadataのrepairはscope外            |
| Source scope 不在                              | explicit error                                | Root Workbenchへのfallback禁止                  |
| Target scope 不在                              | explicit error、自動node作成なし                     | Target branchを更新する必要                        |
| Duplicate/ambiguous scope ID                 | tree-invalid / ambiguous error                | Invalid `.meta.json` の修復が必要                 |
| Target branchで scope slugが異なる                | IDで独立解決                                       | Relative path転写禁止                           |
| Target `.workbench` が Git ignored でない        | copy前に拒否                                      | Old branch/global ignore差異                  |
| Destination `.workbench` が regular file      | preflight reject                              | 自動削除しない                                     |
| File-directory collision                     | 全 mutation前に reject                           | Destination subtree保持                       |
| Permission/disk-full I/O failure             | nonzero、partial counts/path                   | Full rollbackなし                             |
| Sourceがcopy中に変更される                           | Stop/errorまたはobserved bytesをcopy              | Lockなし。再実行がrecovery                         |
| 複数copyが同時実行                                  | Filesystem last-writer/error                  | Concurrency guaranteeなし                     |
| Regular file overwrite中のprocess crash        | Temporary sibling + replace                   | Directory全体はnon-atomic                      |
| Special filesystem entry                     | Human disposition後、推奨は preflight error        | Platform差                                   |
| Scanner callsite漏れ                           | W1 inventory + fake canonical content tests   | Repository-wide `rglob` が散在                 |
| Result filterのみで内部を歩く                        | Prunable walkerを要求                            | Large/malicious Workbench test              |
| Installer fallbackのrule漏れ                    | Asset/fallback双方をtest                         | Hidden `.gitignore` package coverageを確認     |
| Provider/dogfood drift                       | Full inventory parity                         | Subset mapは新規fileを見逃す                       |
| Updateが Workbench を消す                        | Root/scoped preservation fixture              | Initiatives/unmanaged preservation contract |
| Nested `.git` が toolingを混乱させる                | Copy by design、docs warning                   | Content interpretationなし                    |
| `.env` / secret を複製する                        | Copy by design、help warning、contentをlogしない    | Secret scannerは明示 non-goal                  |
| Worktree remove で唯一のcopyが消える                 | Disposable contractをdocsに明記                   | Durable evidenceは `artifacts/` へ            |
| Root Workbenchを誤ってbulk copy                  | CLI routeを作らない                                | Manual filesystem操作までは禁止しない                 |
| Workbenchをreview evidenceと誤認                 | Authority boundaryをdocs/reportに記載             | EAL/canonical docs以外はadopted扱いしない           |
| Parent policy conflictを黙って解釈                 | Human approval gate                           | 未解決ならIssue creationを止める                     |

---

# Assumptions and insufficient evidence

## Assumptions

1. Candidate command spellingは `workbench copy --scope ... --to ...` とした。Clarification は command semantics を採用しているが、exact CLI spelling は採用済み事実ではない。
2. Target は同一 repository の全 linked worktreeを許可する案とした。これは既存 `worktree list/show/remove` が external worktree も扱う事実からの設計推論である。
3. Empty source Workbench は zero-entry success とする案とした。Clarification に明示回答はない。
4. Regular file bytes、directory structure、symlink targetを「complete content」と解釈した。Owner、ACL、xattr、device semanticsの fidelity は未定義である。
5. File-directory collisionは preflight failure とした。Clarification はこの点を technical design に残している。
6. Tree-wide rollback を導入しない。Adopted no-manifest/no-backup/minimal surface からの設計推論である。
7. Output field名と error code は候補であり、現在の repository API ではない。

## Insufficient evidence

1. GitHub connector で source code と docs は確認したが、local checkout で test、`git check-ignore`、package build、installer smoke は実行していない。
2. Repository-wide search で多数の `rglob` callsiteを確認したが、各 callsite が runtime default discovery か explicit user input かの全分類は未実施である。W1 の mandatory inventory とする。
3. Exact special-file behavior、Windows symlink privilege、metadata preservationについて current repository policyは見つからなかった。
4. Issue #246 report は stale runtime refresh、full parity、package smokeの tests が passしたと記載している。  しかし指定コミットの `tests/unit/infra/test_init_update.py` を connector で取得した応答では file body が露出しなかったため、その test implementation と現在の実行可能性は独立確認できていない。
5. Current Epic 00312 report の EAL は空であるため、clarification artifacts が canonical docsへ adopted 済みとは扱っていない。
6. 添付 `設計判断と提案.txt` は `ExceptionBase`、`UseCaseFailure`、`InternalFault` 等の exception/failure mapping 設計を扱う文書であり、Epic 00312 の Workbench、scanner、worktree、installer に関する repository evidence を含まないため、本提案の根拠から除外した。

## Canonical adoption boundary

この提案を canonical とするには、少なくとも次が必要である。

* Human による D-023 / D-024 disposition
* Clarification artifacts の report EAL 採用記録
* Candidate requirement/design/plan の段階的統合
* 各 phase の fresh spec-reviewer pass
* Human approval
* その後の child Issue 作成と dependency edge 設定

それ以前は、W1/W2/W3 は planning evidence であり、Issue node、execution-ready specification、approved implementation plan ではない。
