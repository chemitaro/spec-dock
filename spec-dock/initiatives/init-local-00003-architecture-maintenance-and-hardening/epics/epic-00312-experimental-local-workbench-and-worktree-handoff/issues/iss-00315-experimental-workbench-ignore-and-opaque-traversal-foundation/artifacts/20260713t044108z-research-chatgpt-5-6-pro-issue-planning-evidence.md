# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a545ef5-94f4-83ee-ab33-78bec6084663

## Prompt

Required repository connector context:
- @GitHub chemitaro/spec-dock
- Current branch: iss-00315-experimental-workbench-ignore-and-opaque-traversal-foundation
- Default branch: main
- MUST inspect this GitHub repository with the GitHub connector before answering.
- First inspect the current branch. If the current branch does not exist or cannot be opened, inspect the default branch instead.
- Hard failure condition: if the GitHub connector/app is unavailable, or if the repository, current branch, and default branch cannot be accessed, return immediately with exactly: repository access failed.
- Do not continue from attached files, prompt context, memory, or general knowledge when repository access fails.
- Attached files and prompt-provided context are supplementary only after repository access succeeds.

Use the attached brief. Inspect @GitHub chemitaro/spec-dock on the current branch and produce the requested Japanese Issue planning candidates. Evidence-only.

### File: ../../../../../private/tmp/codex-agent-work/501/session-20260712t154229z-specdock-chatgpt-first-storage-analysis-ac120a25/iss-00315-planning-prompt.md
Lines: 1-39
```md
 1 | # Issue 315 ChatGPT-first planning brief
 2 | 
 3 | Repository: `chemitaro/spec-dock`
 4 | Branch: `iss-00315-experimental-workbench-ignore-and-opaque-traversal-foundation`
 5 | Parent: Epic 00312, reviewed requirement/design/plan and accepted Artifact import ADR.
 6 | Input framing: requirement-heavy.
 7 | Authority: Your output is evidence-only. Do not claim canonical adoption, reviewer pass, execution-ready, Issue finish, or PR readiness.
 8 | 
 9 | ## Issue objective
10 | Plan only W1: Experimental Workbench Ignore And Opaque Traversal Foundation.
11 | 
12 | It must deliver:
13 | - Git-ignore for root, Initiative, Epic, Issue `.workbench/` placements.
14 | - Runtime-wide opaque boundary: default semantic discovery must not enumerate/read/interpret `.workbench/` descendants.
15 | - Inventory recursive discovery callsites and classify default semantic discovery vs explicit user operation vs generated-known-tree; do not blindly replace every `rglob`.
16 | - Exact `.workbench` file/dir must be rejected as authoring semantic source while ordinary filesystem operations remain allowed.
17 | - Scope delete/worktree remove must not gain a Workbench blocker.
18 | - `spec-dock update` preserves existing Workbench contents.
19 | - Provider assets/runtime are authority; dogfood is verification surface.
20 | - Copy command and Artifact import are out of scope.
21 | - Intermediate Issue: PR delivery is deferred to final Issue 319. Local completion still needs tests/reviews/commit/report evidence and explicit deferred PR gate.
22 | 
23 | ## Task
24 | Inspect the GitHub branch, parent Epic, current runtime/code/tests/docs, then produce Japanese candidates for canonical Issue:
25 | 1. `requirement.md`
26 | 2. strict-grade `design.md`
27 | 3. strict executable `plan.md`
28 | 
29 | The plan must satisfy current `workflow_issue.md`, `phase_plan_issue.md`, and `authoring/issue-plan.md`:
30 | - vertical behavior slices, one current step at a time;
31 | - Spec-Locked Closure Index;
32 | - each implementation step has planned contract, delegation contract, concrete test cases, report evidence destination, step closure, amendment trigger, reviewer mapping, commit candidate;
33 | - S90 docs impact resolution;
34 | - S99 final local quality with qa-reviewer, issue-wide code-reviewer, spec-reviewer;
35 | - deferred PR delivery gate to Issue 319;
36 | - exact commands and allowed/forbidden paths;
37 | - preserve dogfooding provider-source authority.
38 | 
39 | Identify current callsites/files/tests precisely. Return information_insufficient rather than inventing behavior.
```

## Answer

# 結論

GitHub connector で `chemitaro/spec-dock` の指定ブランチを確認し、Issue 315 の W1 に限定した日本語候補文書を作成しました。以下はすべて **evidence-only の未採用候補**です。canonical 採用、spec-reviewer 合格、実装開始可能、Issue 完了、PR 準備完了を示すものではありません。

指定ブランチの Issue 315 文書は現時点では汎用 scaffold／compose 待ちであり、Strict grade の assurance authorization も GitHub 上では確認できませんでした。そのため、今回の `design.md` と `plan.md` は **Strict-grade candidate** とし、実装前の S00 で `assurance classify`、canonical integration、fresh spec review を必須ゲートにしています。

## 生成物

* [Issue 315 requirement.md 候補](sandbox:/mnt/data/iss-00315-requirement-candidate.md)
* [Issue 315 strict-grade design.md 候補](sandbox:/mnt/data/iss-00315-design-strict-candidate.md)
* [Issue 315 strict executable plan.md 候補](sandbox:/mnt/data/iss-00315-plan-strict-candidate.md)
* [3 文書一括 ZIP](sandbox:/mnt/data/iss-00315-planning-candidates.zip)

ファイル整合性確認用 SHA-256:

```text
7ec032efdab7bbb9851f78c0537d6c72ca73587f68155d42f5a226136686698c  requirement
71afa460f0d00360be49761fc54e129f34f1f4e37d5ad78d9bd8f63afa265748  design
404ce1733bde73c66c59850c93921bd4d5f61bf68bc3b0be8bd8f8c4a918d59f  plan
4c159fc46569bb1aa6be0da42e23562d9bec52c6a67c82975e1f21166c8332e9  ZIP
```

# 根拠

## 1. Issue 範囲

親 Epic は W1 に、次の契約を割り当てています。

* root、Initiative、Epic、Issue 配下の `.workbench/` を Git-ignore する。
* default semantic discovery は `.workbench/` を見つけた時点で descend しない。
* recursive discovery callsite を分類し、すべての `rglob` を一律に置換しない。
* authoring source として指定された exact `.workbench` file/directory を拒否する。
* delete と worktree remove に Workbench blocker を設けない。
* update で既存 Workbench を保持する。
* provider assets/runtime を正本とし、dogfood は検証面とする。
* copy command と Artifact import は後続 Issue とする。

最終 PR delivery は W5 の Issue 319 に集約され、Issue 319 は Issue 315–318 に依存しています。したがって Issue 315 の S99 はローカル品質、review、commit、report evidence までを閉じ、PR の作成・更新・mergeability 判定は明示的に deferred としました。

## 2. 現行実装で確認した主要な semantic discovery callsite

| 分類                                | 現行 callsite                                                                  | 候補設計での処置                                                                              |
| --------------------------------- | ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| default semantic discovery        | `infra/fs_repo.py` の `.meta.json` / legacy `meta.json` 再帰探索                  | Workbench directory を descent 前に prune。exact `.workbench` file も候補から除外                |
| default semantic recovery         | installer `src/spec_dock/cli.py::_resolve_manifest_target_dir`               | 同じ component-exact prune semantics を installer 側で適用                                   |
| default semantic fallback         | `application/delete_node.py::_matching_target_directories`                   | canonical depth を維持した列挙、または pruned traversal に置換                                      |
| default semantic scope resolution | `application/delegated_authoring.py::_resolve_scope_dir`                     | wildcard recursive metadata discovery を pruned traversal に置換                          |
| authoring semantic discovery      | `domain/authoring_pack/source_manifest.py`                                   | exact Workbench source を安定 token で拒否し、directory manifest traversal も descent 前に prune |
| explicit operation                | node subtree delete、explicit directory state、ZIP/pack tree、template scaffold | 一律置換しない。明示操作または generated-known-tree として保持                                            |

`fs_repo.py` は現在 `initiatives` 以下を再帰探索して metadata を読み込みます。installer の active-state recovery にも独立した `.meta.json` 再帰探索があります。delete fallback と delegated-authoring scope resolution にも、共通 node reader を経由しない探索経路が存在します。

一方、template scaffolding、pack staging、ZIP contract、explicit diff-guard directory hashing は、利用者が明示した木または provider が把握する生成木です。これらまで opaque semantic discovery helper に機械的に置換しない方針としました。

## 3. source manifest は blocker だけでは閉じない

現在の source manifest は selected directory を `rglob("*")` し、ファイルを読み取って hash 化します。除外対象は Python cache 程度です。また、preflight は `source_path_blockers()` の結果を収集した後にも `build_source_manifest()` を呼びます。したがって exact Workbench source の blocker だけでは不十分で、manifest builder 自体にも defensive rejection／pruning が必要です。

候補では、既存の blocker 命名体系に沿う安定 token として、次を提案しています。

```text
unsafe_source_path:workbench:<original-source-path>
```

これは現行 token ではなく、Issue 315 の設計候補です。

## 4. Git-ignore と update

現行 provider `.gitignore` および installer fallback には `.workbench/` 規則がありません。installer は provider `.gitignore` を package data として配布し、存在しない場合にはコード内 fallback を使用します。したがって両方を更新対象にしています。

候補規則は次の一行です。

```gitignore
.workbench/
```

`spec-dock/.gitignore` からの非 anchor 規則として、root および `initiatives/**` 内の supported placement を再帰的に対象とする設計です。

installer update は `docs`、`templates`、`scripts`、`system` を managed directory とし、`initiatives/**` を managed replacement 対象にしていません。そのため update preservation は、新しい destructive production logic よりも、root/scoped Workbench に sentinel を置く回帰テストで閉じる可能性が高いと判断しました。

ただし、現在の `tests/unit/infra/test_init_update.py` は空ファイルでした。過去 report の記載だけを現行テストの存在証拠として扱わず、Issue 315 で新しい update preservation／provider-dogfood parity テストを追加する計画にしています。

# 候補文書の主要契約

## `requirement.md`

候補は以下を明示しています。

* exact component 名 `.workbench` のみを reserved boundary とする。
* `.workbench-notes`、`my.workbench` などは通常名として扱う。
* default semantic discovery は `.workbench/` の存在を結果から除くのではなく、内部へ descend しない。
* Workbench 内の malformed `.meta.json`、canonical ID に似た directory、ADR／artifact に似た Markdown が、sync、validate、deps、active/context、authoring source manifest に影響しない。
* Workbench 外の malformed metadata は従来どおり失敗させ、opaque 化を一般的な validation 緩和にしない。
* exact Workbench file/directory を authoring semantic source に指定した場合は、内容を読む前に拒否する。
* delete、worktree remove、通常の shell/file operation は Workbench の存在だけでは拒否しない。
* update 後も既存 bytes、nested files、destination-only contents を保持する。
* copy command、Artifact import、TTL、secret scan、promotion、catalog は非目標。

## `design.md`

Strict candidate では次の seam を提案しています。

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/opaque_paths.py
```

ここに exact component predicate と pruned traversal primitive を置きます。候補 invariant は次です。

```text
Path component == ".workbench"
```

```text
topdown traversal:
  directory entry が ".workbench" なら dirnames から除去
  その subtree の stat/read/parse/hash を行わない
```

installer `src/spec_dock/cli.py` は provider runtime asset を import する前提にせず、package-side の小さな同等 predicate／iterator を使用します。この重複は semantic duplication ではなく、installer と installed runtime の実行境界が異なるための実装配置候補です。

## `plan.md`

計画は one-current-step 方式で、次の順序です。

| Step | 垂直スライス                                                                                          |
| ---- | ----------------------------------------------------------------------------------------------- |
| S00  | assurance、canonical integration、recursive callsite inventory、baseline                           |
| S01  | provider `.gitignore` と installer fallback                                                      |
| S02  | node metadata discovery／graph opacity                                                           |
| S03  | installer recovery、delete fallback、delegated scope resolver                                     |
| S04  | authoring source rejection と source-manifest pruning                                            |
| S05  | scope delete／worktree remove の no-blocker characterization                                      |
| S06  | update preservation と provider→dogfood distribution                                             |
| S90  | docs impact resolution                                                                          |
| S99  | full tests、static analysis、QA、issue-wide code review、spec review、commit/report、deferred PR gate |

各 implementation step に以下を記載済みです。

* planned contract
* bounded delegation contract
* test ID、fixture、操作、期待結果、failure signal
* Red／Green／Refactor evidence destination
* step closure
* amendment trigger
* reviewer mapping
* commit candidate
* allowed paths／forbidden paths

Spec-Locked Closure Index は `CLOS-001`–`CLOS-012` として、要件、design、step、test、report evidence destination、reviewer、closure state を対応付けています。これは current Issue planning workflow が求める closure index、具体的 test schema、step-local delegation、S90、S99 を反映したものです。

# 仮定

1. `.workbench/` は `spec-dock/.gitignore` の一規則で、root と supported scoped placement の双方を ignore する。
2. reserved 判定は basename の substring ではなく、path component の完全一致とする。
3. Workbench の symlink／special entry の内容を default semantic discovery が調査する必要はない。boundary を directory entry 名で認識した時点で descend しない。
4. node metadata discovery を修正すれば、そこから構築される graph を利用する sync、validate、deps の主要経路にも opaque boundary が伝播する。ただし、共通 node reader を迂回する独立 resolver は S03 で別途修正する。node graph と downstream dependency resolution の現在の接続は確認できました。
5. dogfood runtime は手作業で別実装せず、provider 更新後にローカル installer/update 経路で生成・比較する。

# 不確実性

* GitHub connector の静的検索だけでは、文字列組み立て、subprocess 内の traversal、将来追加された callsite を完全に列挙したとは断定できません。そのため S00 で local `rg` と実装本文確認を行い、分類表を `report.md` に固定する契約にしています。
* Strict grade はユーザー要求に基づく候補です。canonical implementation 前に、実際の `assurance classify --stage requirement --issue iss-00315` の結果を確認する必要があります。
* update preservation は現行 managed-directory boundary から成立すると推定できますが、実際の wheel／installer-like update smoke は未実行です。
* Workbench の unreadable directory や特殊 filesystem entry が prune の手前で OS-level error を発生させないことは、GitHub 上のコード読解だけでは十分に確認できません。S02/S04 の sentinel テストで、descendant の read/stat が発生しないことを観測する設計です。
* `.workbench/` 内部にある ignored file が delegated-authoring の Git status ベース guard にどう現れるかは、この Issue の semantic-discovery 契約とは別の挙動です。Issue 315 では Workbench を authoring output surface にせず、既存 explicit diff-guard policy の全面変更は行いません。

# 未検証主張

以下は設計・計画候補であり、現行実装の事実ではありません。

* `opaque_paths.py` という module 名。
* `unsafe_source_path:workbench:*` という blocker token。
* 候補内の test function 名と fixture 名。
* `.workbench/` を追加した後の実際の Git ignore 結果。
* focused/full pytest、ruff、mypy、validate、sync の合格。
* provider/dogfood parity。
* qa-reviewer、code-reviewer、spec-reviewer の判定。
* commit 作成、Issue finish、Issue 319 への引き渡し。

参照取得は GitHub connector による 2026-07-13 JST 時点の観測であり、Codex 側での独立検証済みとは扱っていません。また、添付の `設計判断と提案.txt` は FastAPI／exception taxonomy に関する別件資料だったため、Issue 315 の根拠には採用していません。
