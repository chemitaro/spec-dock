---
種別: disc
ID: "20260818t030454z-disc"
タイトル: "Epic 365 Distribution Reconciliation Authoring Brief"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-08-18"
親: ["epic-00365"]
template: "disc"
authority: "evidence"
derived_from:
  - "20260817t065956z-research-issue-360-structural-defect-research.md"
  - "20260817t065956z-guide-issue-360-structural-problems.html"
reflected_to: []
---

# 20260818t030454z-disc Epic 365 Distribution Reconciliation Authoring Brief

Epic 365 の要件・設計・計画と Issue 分割を作成するために、Issue 360 からの引継ぎ、現行実装の観測、利用者インタビュー、外部分析を一つの authoring brief に統合する。この Artifact は evidence であり、durable authority は今後差し替える canonical `requirement.md`、`design.md`、`plan.md`、および明示的に accepted となった ADR に置く。

## Inputs

- 対象 scope:
  - Initiative: `init-local-00003` Architecture Maintenance and Hardening
  - Epic: `epic-00365`
  - GitHub Issue: `chemitaro/spec-dock#365`
  - 既存 node path: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00365-specdock-structural-integrity-rearchitecture-and-regression-baseline-recovery/`
  - 計画上の採用タイトル: `SpecDock Distribution Reconciliation and Recovery Architecture`
  - node ID と既存 path は維持する。`.meta.json` は CLI 管理対象であり、rename/update command が存在しないため手編集しない。
  - child Issue nodes:
    - `iss-00368` / GitHub `#368` / `recognized-workspace-reconciliation`
    - `iss-00369` / GitHub `#369` / `fresh-distribution-provisioning`
    - `iss-00370` / GitHub `#370` / `managed-distribution-deprovision`
    - `iss-00371` / GitHub `#371` / `explicit-spec-history-purge`
    - `iss-00372` / GitHub `#372` / `distribution-hard-cutover-and-parity`
  - accepted ADR destination: `artifacts/20260818t031610z-adr-unified-distribution-reconciliation-and-forward-recovery.md`
  - authoritative HTML destination: `artifacts/20260818t031610z-guide-epic-365-distribution-reconciliation.html`
- repository snapshot:
  - 調査開始時の local/GitHub `main` 一致 SHA: `081fde0d333520173255ad710aa66d727b475ec2`
  - authoring branch: `codex/epic-365-distribution-reconciliation-planning`
  - Strict consult は、この Artifact を commit/push した後の branch tip を改めて exact-SHA 検証する。上記開始時 SHA を Strict の代替根拠にしない。
- canonical source set:
  - 親 Initiative の `requirement.md`、`design.md`、`plan.md`
  - Epic 365 の現行 `requirement.md`、`design.md`、`plan.md`、`report.md`、`.meta.json`
  - Epic 356 と Issue 360 の canonical docs と direct-child Artifacts
  - `README.md`、`AGENTS.md`、`pyproject.toml`、`Makefile`
  - `src/spec_dock/cli.py`、`src/spec_dock/managed_distribution.py`、`src/spec_dock/assets/`
  - `tests/unit/infra/test_init_update.py`、`tests/unit/infra/test_managed_distribution.py`、関連する runtime / integration tests
  - `spec-dock/docs/authoring/`、`spec-dock/templates/{epic,issue,artifacts}/`
- 既存 Epic 365 evidence:
  - `20260817t065956z-research-issue-360-structural-defect-research.md`
  - `20260817t065956z-guide-issue-360-structural-problems.html`
- 外部分析:
  - ChatGPT-Use による GPT-5.6 分析を advisory evidence として使用した。
  - GitHub connector が `chemitaro/spec-dock` の `main` tip を調査開始時 SHA と一致確認した。
  - 外部分析の提案は、そのまま authority とせず、local code、tests、canonical docs、利用者判断に照合した。
- 利用者インタビュー:
  - Q1〜Q18 はすべて推奨 Option A を採用した。
  - Q19 で共有理解を明示承認し、canonical authoring、Issue slice 作成、必要な ADR、ChatGPT-Use Strict、生成 ZIP の byte-for-byte 採用、日本語 HTML の作成と Tailscale 配信まで承認した。

### 2026-08-18 Strict review refinement

- 現行 `main()` は fresh target に対する `init`、`init --force`、`update` をすべて fresh provisioning へ送る。public compatibility を維持するため、D1 は recognized target の `update` / `init --force`、D2 は fresh target の3 entrypointすべてを owner とする。
- authority non-expansion は mutation resume の exact-authority match として具体化する。lower-authority invocation は read-only inspection と diagnostic だけを許可し、journal checkpoint を進めない。
- D3 は default/`--keep-specs` dry-run と keep-specs apply、D4 は `--remove-specs` dry-run/apply を owner とする。
- current desired content と safe regular single-link identityを証明できるmode-only driftはjournaled repairとし、証明不能またはunsafeなmode driftだけをblockする。
- D5はlegacy seamを削除するcleanup ownerではなくabsence gateである。production executable seam/writerの残存はD1〜D4のowner exit未達として差し戻す。
- この refinement は Q1〜Q19 の採用判断や five fixed Issue slices を変更せず、現行 public behavior と canonical contract の曖昧さだけを解消する。

## Synthesis

### 1. 結論

Epic 365 は、曖昧な「structural integrity」全般ではなく、SpecDock の managed distribution lifecycle を一つの照合・実行・回復契約へ統合する。Full Regression baseline recovery は兄弟 Epic 候補へ分離し、AI model / browser session / iterative review orchestration は Epic 356 で確立した External Intelligence 境界の外側に維持する。

Epic の一貫した成果は次の関数として表現できる。

```text
Desired Managed Assets
+ Historical Ownership Evidence
+ Workspace Observation
+ Explicit Operation Intent
  -> read-only Workspace Assessment
  -> Executable Mutation Plan
  -> descriptor-bound execution with Operation Journal
  -> typed postcondition outcome or fail-closed recovery state
```

### 2. 現行実装で確認した構造問題

- `src/spec_dock/cli.py` は約 4,945 行で、argument parsing だけでなく root lock、scaffold copy/remove、retry marker、install orchestration、uninstall identity/action/plan/apply/post-verify/diagnostics を抱える。
- `src/spec_dock/managed_distribution.py` は約 3,220 行で、admission、catalog、historical evidence、workspace observation、classification、plan、apply、staging ownership、error を抱える。
- `managed_distribution.py` には `DistributionOperation = Literal["fresh", "update", "init-force", "uninstall"]` と共通 `DistributionAction` / `DistributionPlan` がある一方、`cli.py` は別の `_UninstallAction`、`_build_uninstall_plan()`、`_apply_uninstall_plan()` を持つ。
- update/init-force 系は `.distribution-retry.json`、uninstall 系は `.uninstall-retry.json` を使い、回復 protocol が二重化している。
- `cli.py` が `managed_distribution.py` の private `_rename_distribution_no_replace` を import しており、layer boundary が反転している。
- `apply_distribution_plan()` は `scaffold_applier` callback と `allow_blocked_scaffold_paths` を受け取り、共通 plan の外側に第二の mutation engine を接続できる。
- 現行 README は、`update` と `init --force` が共通 classifier を使うこと、unknown / modified / symlink / hardlink / root-rebound を preserve-and-block すること、uninstall が全 action の ownership 検証後だけ mutation することを公開契約としている。
- installer CLI の公開 surface は `init [--force] [path]`、`update [path]`、`uninstall [--apply] [--keep-specs|--remove-specs] [--json] [path]` である。
- filesystem safety は `dir_fd`、`O_NOFOLLOW`、directory descriptor、`fcntl.flock` など POSIX capability に依存する。CI は Ubuntu のみだが、実装には Linux と Darwin の分岐があり、利用者の実行環境には macOS が含まれる。

### 3. Epic scope

#### 対象

- fresh `init`
- `update`
- `init --force`
- managed distribution の解除（現行 `uninstall --keep-specs` 相当）
- 明示的権限による spec history の purge（現行 `uninstall --remove-specs` 相当）
- すべての intent に共通する ownership assessment、action grammar、filesystem mutation、journal、postcondition、diagnostics
- provider checkout、dogfooding workspace、wheel、sdist、fresh consumer の契約 parity
- Linux と macOS の検証可能な契約

#### 非対象

- Full Regression の失敗修復、waiver 解消、baseline burn-down
- AI model、browser session、反復 review campaign、人間の adjudication の orchestration
- Distribution 以外の runtime 全般の再設計
- 汎用 filesystem transaction framework
- Operation 全体を元に戻す原子的 rollback 保証
- Windows 対応
- 行数削減そのもの
- 新しい公開 CLI command / flag の追加
- private Python API の互換保証
- legacy marker schema の恒久的維持

### 4. 採用語彙

| 用語 | 意味 | 混同してはいけない対象 |
|---|---|---|
| Desired Managed Asset | 現在の package contract が配置・更新・削除を管理する対象 | 過去 version の asset、利用者所有 content |
| Ownership Evidence | current / historical package が対象を所有したと証明する情報 | 現在観測した filesystem 状態 |
| Workspace Observation | operation 開始時に descriptor-relative に観測した対象の状態 | 変更許可、desired state |
| Operation Eligibility | root、marker/journal、package、intent の組合せが assessment を開始できる条件 | asset ごとの ownership classification |
| Workspace Assessment | desired/evidence/observation/intent から disposition と blocker を作る read-only 結果 | 実行可能 plan、mutation |
| Executable Mutation Plan | blocker がなく、root/intent/contract/digest に束縛された action 集合 | assessment の途中結果 |
| Operation Journal | 部分実行を forward recovery する durable protocol | best-effort retry hint、全体 rollback log |
| Managed Content Root | distribution contract が管理する境界 root | root 内の unknown content を自動所有する権限 |
| Distribution Deprovision | tooling / generated state / owned managed assets を外す intent | spec history purge |
| Spec History Purge | 明示的な追加権限に基づき spec history を削除する intent | deprovision の暗黙的副作用 |

Identity は一つの汎用 tuple に潰さない。少なくとも directory binding identity、directory mutation snapshot、regular-file content identity、symlink identity を区別する。directory の child mutation は directory ctime を変え得るため、ctime をすべての identity に無条件で含めてはならない。

### 5. Target architecture

```text
CLI Adapter
  -> Distribution Operation Service
       -> Distribution Contract
       -> Workspace Assessment
       -> Journaled Executor
            -> Descriptor-bound Filesystem Kernel
```

#### CLI Adapter

- command / flag / path を parse する。
- application outcome を human text、既存 JSON contract、exit code へ写像する。
- ownership policy、filesystem recursion、journal transition、staging cleanup を持たない。

#### Distribution Operation Service

- explicit intent と package contract を受け取る。
- eligibility、assessment、plan、journaled execution、postcondition verification を順序付ける。
- operation ごとの第二 action grammar を作らない。

#### Distribution Contract

- Desired Managed Assets、Historical Ownership Evidence、Managed Content Roots、intent policy、preservation policy、postconditions を提供する。
- package version と journal protocol compatibility を明示する。

#### Workspace Assessment

- read-only で observation と ownership disposition を作る。
- blocker が一件でもあれば executable plan を発行しない。
- unknown content を pathname や parent directory だけで owned と推測しない。

#### Journaled Executor

- root identity、intent、contract/protocol version、plan digest、checkpoint、staging lease を Operation Journal に束縛する。
- checkpoint は単調に進み、partial failure では journal を保持する。
- same plan を再構成でき、journal protocol との互換性を明示した同一または新しい package だけ resume を許可する。
- downgrade、root change、intent change、plan mismatch、authority expansion は mutation 前に拒否する。
- postcondition 成功後にだけ journal を完了・除去する。

#### Descriptor-bound Filesystem Kernel

- root binding、parent-chain open、type-specific observation、no-replace publish、atomic replacement、exact unlink、recursive copy/remove、chmod、staging cleanup を唯一の実装として提供する。
- すべての mutation は root descriptor と検証済み relative path を通す。
- CLI や operation service に独自の recursive copy/remove、marker writer、rename shortcut を残さない。

### 6. Cross-Issue invariants

1. 全公開 intent は一つの operation model、action grammar、filesystem kernel、journal protocol、typed outcome を使う。
2. eligibility、assessment、plan construction は副作用を持たない。
3. blocker が一件でもあれば operation 全体を最初の write より前に停止する。safe subset の部分適用はしない。
4. unknown / modified / user-owned content は、明示的な purge authority の対象でない限り保持する。
5. retry/resume は元の authority を超えない。別 intent や purge への昇格を許可しない。
6. root、parent chain、target、staging entry は descriptor-relative に再検証する。
7. deprovision と purge は同じ engine を使うが、別 intent・別権限・別 postcondition を持つ。
8. public CLI、flag、安全性、利用者所有 data、既存 JSON の意味を維持する。
9. private API と internal journal schema は公開互換対象にしない。
10. legacy marker は exact conversion が証明できる場合だけ新 journal へ変換し、それ以外は fail closed とする。
11. code rollback と operation recovery を分ける。new journal 作成前は code rollback 可能だが、作成後は同一または互換 newer package による forward recovery を正規経路とする。
12. Windows は capability gate で write 前に停止し、Linux / macOS は同じ contract を満たす証拠を要求する。

### 7. 必須シナリオ

| ID | 条件 | 期待結果 |
|---|---|---|
| SC-FRESH-01 | fresh target、衝突なし | 全 Desired Managed Assets を作成し、postconditions を満たす |
| SC-FRESH-02 | parent/target collision または不明な parent state | write 0 件で typed blocker |
| SC-UPDATE-01 | current identity match | 必要な asset を adopt/upgrade/prune し、user content を保持 |
| SC-UPDATE-02 | historical ownership match | explicit historical evidence に基づき upgrade/prune |
| SC-UPDATE-03 | unknown/modified target | operation 全体を write 前に停止 |
| SC-UPDATE-04 | symlink/hardlink/parent symlink/root rebind | external mutation を起こさず停止 |
| SC-DEPROVISION-01 | owned tooling/generated/managed assets、keep specs | managed distribution を解除し、spec history と unknown content を保持 |
| SC-PURGE-01 | explicit purge authority | spec history を削除し、権限外 unknown content を保持 |
| SC-PURGE-02 | purge authority なし | spec history を削除せず write 前に停止 |
| SC-JOURNAL-01 | partial failure、same root/intent/plan、compatible package | checkpoint から再照合し、収束する |
| SC-JOURNAL-02 | root/intent/plan/protocol mismatch | write 前に停止し、journal と staging を推測変更しない |
| SC-JOURNAL-03 | retry で権限拡大を要求 | 拒否する |
| SC-LEGACY-01 | legacy marker を exact に解釈可能 | one-way conversion または明示的 compatibility adapter で回復 |
| SC-LEGACY-02 | malformed/dual/ambiguous marker | write 前に停止し、manual recovery guidance を返す |
| SC-PLATFORM-01 | Linux | 全 safety / failure matrix を満たす |
| SC-PLATFORM-02 | macOS | 全 safety / failure matrix を満たす |
| SC-PLATFORM-03 | Windows / required capability 不足 | write 前に stable diagnostic で停止 |

### 8. Issue slices と依存方向

#### D1 `iss-00368` Recognized Workspace Reconciliation

- `update` と `init --force` を新 engine へ移す最初の完全な vertical slice。
- Distribution Contract、Workspace Assessment、共通 action grammar、Descriptor-bound Filesystem Kernel、Operation Journal、typed diagnostics を、この利用者 flow を完了できる最小範囲で成立させる。
- 対象 flow の legacy path は同じ Issue 内で削除する。

#### D2 `iss-00369` Fresh Distribution Provisioning

- fresh `init` を D1 の engine へ移す。
- fresh-only collision / creation / postcondition を追加し、別 scaffold mutation engine を残さない。
- dependency: D1。

#### D3 `iss-00370` Managed Distribution Deprovision

- current `uninstall --keep-specs` 相当を共通 grammar/kernel/journal へ移す。
- spec history と unknown content の preservation を end-to-end で証明する。
- dependency: D2。

#### D4 `iss-00371` Explicit Spec History Purge

- current `uninstall --remove-specs` 相当を別 intent / 別 authority として同じ engine へ移す。
- retry で deprovision から purge へ昇格できないことを証明する。
- dependency: D3。

#### D5 `iss-00372` Distribution Hard Cutover And Parity

- 旧 `_UninstallAction`、旧 plan/apply、独自 recursive mutation、二重 marker writer、private rename import、fallback seam がD1〜D4で物理的に除去済みであることをabsence gateで検証する。残存するproduction seamはowner Issueへ戻す。
- provider checkout、dogfood、wheel、sdist、fresh consumer、Linux、macOS の parity と migration/recovery docs を確認する。
- dependency: D1〜D4。
- 親 Initiative の T3 までに全 public operation を hard cutover し、T4 は証拠収集と completion confirmation だけにする。

すべての Issue は一つの end-to-end value を持つ vertical slice とする。Contract、Kernel、Journal のような未接続 horizontal foundation だけを先に作る Issue 分割は採用しない。各 Issue の `plan.md` は public contract、migration、recovery の影響から原則 `strict` Planning Level とし、不可逆 data loss / incident response 条件が見つかった場合だけ同じ Plan 内で `critical` を再評価する。

### 9. Epic acceptance / exit

- 全 public intent が新 operation service を通り、第二 action grammar がない。
- `cli.py` は parse、asset location、dispatch、render、exit mapping に限定され、ownership policy、filesystem recursion、journal transition を持たない。
- mutation は一つの descriptor-bound kernel に集約される。
- legacy scaffold/uninstall mutation helper、二重 retry writer、private rename import が存在しないことを dependency / import / symbol tests で確認できる。
- ownership / preservation matrix が missing、identical current、historical、wrong mode、unknown modified/user-owned、symlink、hardlink、parent symlink、root rebind、generated state、spec history、unknown sibling を覆う。
- failure / resume matrix が preflight write-zero、partial journal retention、same-root same-plan convergence、mismatch block、preserved surfaces unchanged を覆う。
- public CLI / flag と既存 JSON semantic contract が維持される。
- provider、dogfood、wheel、sdist、fresh consumer の同一 contract を確認する。
- Linux と macOS の検証証拠を残す。CI 導入方法は Plan で具体化するが、どちらかを best-effort に落とさない。
- affected fast tests と対象 full-regression tests が成功し、この Epic が新しい full-regression failure を追加しない。
- general refactor、line count、naming cleanup を理由に Epic を延長しない。
- D1〜D4 の public flows が T3 までに hard cutover し、D5/T4 は legacy seam absence と parity evidence を確定する。

### 10. Full Regression sibling Epic handoff

Epic 365 は baseline recovery を実装しないが、Issue 360 の evidence を失わないため次の handoff contract を残す。

- exact current SHA で `uv run pytest --run-full-regression` を再計測する。
- 既存 Artifact の 26 件は旧 SHA における historical seed であり、current count と断定しない。
- `approved-no-op` は change attribution であり、health waiver ではない。
- failure ledger は stable ID、phase、first/latest SHA、command、expected/actual、root cause、owner、disposition、closure evidence、waiver expiry を持つ。
- production fix、test fix、obsolete test retirement のいずれかで各 failure を閉じる。
- exit は exact candidate/main SHA で failure 0、期限付き waiver 0、stale ledger 0 とする。
- sibling Epic node の作成は今回の task に含めない。

### 11. Strict authoring assignment

ChatGPT-Use Strict は configured GitHub upstream の exact branch tip を connector で検証してから、repository code、tests、canonical docs、この Artifact、既存 Epic 365 evidence を統合する。ChatGPT-5.6 Pro を使用し、別 branch、default branch、attachment-only analysis、古い conversation memory を根拠にしない。

要求する成果物は一つの ZIP とし、次の構造を最低限含める。

```text
epic-00365-distribution-reconciliation-planning-pack/
├── MANIFEST.md
├── epic/
│   ├── requirement.md
│   ├── design.md
│   └── plan.md
├── issues/
│   ├── iss-00368-recognized-workspace-reconciliation/
│   │   ├── requirement.md
│   │   ├── design.md
│   │   └── plan.md
│   ├── iss-00369-fresh-distribution-provisioning/
│   │   ├── requirement.md
│   │   ├── design.md
│   │   └── plan.md
│   ├── iss-00370-managed-distribution-deprovision/
│   │   ├── requirement.md
│   │   ├── design.md
│   │   └── plan.md
│   ├── iss-00371-explicit-spec-history-purge/
│   │   ├── requirement.md
│   │   ├── design.md
│   │   └── plan.md
│   └── iss-00372-distribution-hard-cutover-and-parity/
│       ├── requirement.md
│       ├── design.md
│       └── plan.md
├── adr/
│   └── 20260818t031610z-adr-unified-distribution-reconciliation-and-forward-recovery.md
└── explanation/
    └── 20260818t031610z-guide-epic-365-distribution-reconciliation.html
```

`MANIFEST.md` は、採用タイトル、上記5 Issueのactual ID / GitHub number / title / slug / dependency、各source fileとexact destination、ADR acceptance、HTML authoritative destinationを明記する。Issue nodeはすでにSpecDock CLIで作成済みであり、ChatGPTは別ID、別title、別slug、追加Issueを生成しない。Markdown本文は日本語とし、code identifier、command、path、schema fieldは原文を維持する。

Epic / Issue canonical Markdown は現在の対応 template と Authoring Kit の責務分離を守る。Epic front matter はactual Epic ID `epic-00365`、GitHub Issue `365`、parent `init-local-00003` を使う。Issue front matter は作成済みscaffoldに記録されたactual Issue ID `iss-00368`〜`iss-00372`、GitHub `#368`〜`#372`、parent `epic-00365` / `init-local-00003`、actual titleを使う。placeholder、架空番号、後処理tokenを残さず、そのままdestination file全体と差し替えられるcomplete fileを生成する。

ただし利用者は「ChatGPT が作成した file をそのまま採用し、既存 template file を編集ではなく差し替える」ことを要求している。したがって最優先の成果物形式は、Issue ID に依存しない完全な destination file を生成し、作成後 scaffold の metadata 値を壊さず byte-for-byte replace できる方式である。exact adoption が不可能な format conflict を発見した場合は、ZIP生成前に回答内で blocker と安全な解決案を示し、推測で placeholder を残さない。

ADR は `20260818t031610z-adr-unified-distribution-reconciliation-and-forward-recovery.md` の1件だけを完成させる。Current ADR templateに従い、Q4〜Q7、Q10〜Q12、Q16〜Q18で利用者承認済みの単一operation model、pre-write fail-closed、journaled forward recovery、deprovision/purge authority separation、vertical hard cutoverを記録する。`ID: "20260818t031610z-adr"`、`タイトル: "Unified Distribution Reconciliation And Forward Recovery"`、`状態: "accepted"`、`authority: "accepted"`、`accepted_authority: "accepted ADR"`、`accepted_at: "2026-08-18"`、`accepted_by: "iwasawayuuta"`、`mirror_eligible: true` を使う。追加ADRや重複した設計説明は作らない。

日本語 HTML は `japanese-explanatory-html` の `explanatory-document.html` contract v2 を基礎にし、`@plantuml/core@1.2026.6` の pinned browser rendering、editable inline PlantUML source、shared accessible zoom modal、diagnostic SVG rejection を保持する。資料単体で背景、用語、責務、正常 flow、failure/recovery、Issue rollout、検証、非対象を理解できるようにする。図の題名・表示語・関係名は日本語にし、実 code identifier は原文を維持する。PlantUML Server、Kroki、remote include、pre-rendered image を使わない。

生成 ZIP は ChatGPT の回答本文の Markdown code block ではなく、実ファイルとしてダウンロード可能にする。ZIP内に symlink、absolute path、`..` path、secret、credential、repository metadata を含めない。Codex は展開前に archive member を検査し、各 source の SHA-256 を記録し、destination との byte equality を確認する。

### 12. Strict analysis で追加確認する事実

- current branch exact SHA における installer/distribution の private call graph と重複 mutation surface。
- public JSON consumer / test contract と、互換性を壊さず typed outcome を導入する境界。
- legacy `.distribution-retry.json` / `.uninstall-retry.json` を exact conversion できる最小情報と、変換不能条件。
- Linux / macOS の syscall/capability 差と、両 platform の acceptance evidence を得る実行経路。
- D1 が horizontal foundation へ崩れず end-to-end flow として完結する最小 boundary。
- Issue 間 dependency を strict linear にする必要がある箇所と、D5 前に並行可能な検証作業。
- current canonical template と「生成 file を byte-for-byte replace」の両立方法。
- ADR が本当に必要な decision と、Epic design に留める説明の境界。

## Options and trade-offs

### 採用済み判断

| Decision | 採用 | 棄却した主な選択肢 | 理由 |
|---|---|---|---|
| Epic portfolio boundary | Distribution reconciliation に限定 | Distribution + regression + AI review を一 Epic に統合 | exit と変更 surface が異なり、親 Initiative の single coherent contract に反する |
| Full Regression health | sibling Epic で failure/waiver 0 | approved-no-op を health waiver として残す | attribution と repository health を分離するため |
| External Intelligence | Epic 356 boundary を維持 | model/session orchestration を product に戻す | deterministic storage contract と probabilistic operation を分離するため |
| Public compatibility | CLI/flag/data/JSON semantics を維持 | private API/marker schema まで凍結、または public break | 利用者契約を守りつつ内部二重化を除去するため |
| Recovery | journaled forward recovery | whole-operation rollback、二 marker の整理だけ | filesystem 全体の rollback を誤って保証しないため |
| Deprovision/Purge | 同じ engine の別 intent/authority | flag 差だけ、purge 廃止 | user-owned spec history の削除権限を明示するため |
| Cutover | vertical slice ごとに旧 path を同時削除 | 長期 dual mode、一括 big bang | 二重経路を残さず Issue 単位で code rollback 可能にするため |
| Platform | Linux + macOS required、Windows non-goal | Linux only、Windows inclusion | current implementationと実利用を覆い、Epic拡張を抑えるため |
| Architecture | Adapter / Service / Assessment+Executor / Kernel | CLI coordinator維持、汎用framework | policy、orchestration、mechanism を分離するため |
| Ambiguous ownership | operation全体をwrite前にblock | safe subset適用、force overwrite | recovery state と data-loss risk を増やさないため |
| Issue slicing | D1〜D5 vertical slices | horizontal foundations、一 Issue | 各 Issue が observable end-to-end value を持つため |
| Structural exit | dependency/absence/matrix/parity evidence | line-count target、既存testsのみ | 責務分離と旧 seam 除去を直接検証するため |
| Journal compatibility | same-plan compatible newer packageを許可 | exact same package only、latest package無条件 | forward fix と fail-closed recovery を両立するため |

### 主要 trade-off

- public CLI を維持するため、内部 action model を一度に美しく置換するより、vertical flow ごとの compatibility adapter が一時的に必要になる。ただし各 Issue の終了時に対象 legacy path を削除し、D5 まで adapter を永久化しない。
- operation 全体を pre-write block するため、部分的に更新できる case でも可用性より安全性を優先する。診断は action 単位に詳しく返してよいが、mutation authority は発行しない。
- Linux と macOS を required とするため platform evidence のコストは増えるが、POSIX と総称して未検証差異を隠さない。
- newer package recovery を許可するため journal protocol compatibility と plan digest が必要になるが、開始 version の bug で永続的に回復不能になることを避けられる。
- accepted ADR を増やしすぎると canonical design と重複するため、cross-Issue で長く独立参照する decision だけに限定する。

## Reflection

### canonical への反映方針

- Epic `requirement.md`:
  - coherent outcome、public behavior、scope/non-scope、observable acceptance、platform/data-preservation constraints を正本化する。
- Epic `design.md`:
  - target architecture、domain vocabulary、cross-Issue invariants、identity distinction、journal protocol、compatibility/migration、testability を正本化する。
- Epic `plan.md`:
  - D1〜D5 の vertical slice、dependency、T3 hard cutover、T4 evidence、cross-Issue verification、rollback/forward recovery、sibling handoff を正本化する。
- Issue docs:
  - 親契約を言い換えず、各 end-to-end flow の acceptance、担当 architecture seam、実装順、negative tests、migration、exit を具体化する。
- ADR:
  - cross-Issue で独立した durable decision がある場合だけ accepted record として作成する。Epic design で十分な説明を重複させない。
- HTML:
  - canonical authority ではなく、人間向けの説明資料として Epic direct-child `artifacts/` に置く。canonical docs と矛盾した場合は canonical docs を優先し、HTMLを更新する。

### 書き込みと採用の手順

1. SpecDock CLIで5 Issue node、dependency、ADR scaffoldを作成し、公式HTML template v2をauthoritative destinationへ配置する。
2. このArtifactをactual ID/pathへ更新し、scaffold一式をvalidate、commit、pushしてStrictがGitHub connectorで読めるexact branch tipにする。
3. ChatGPT-Use Strictでactual ID入りZIPを生成する。
4. archive member、path、file type、size、secret riskを検査する。
5. `MANIFEST.md` のIssue ID/title/slug/dependencyとexact destinationを照合する。
6. ZIP内のcanonical Markdown、ADR、HTMLを、対応する既存scaffold/destinationへ編集せず差し替える。
7. source/destination SHA-256 equalityを記録する。
8. SpecDock validation、document role、dependency projection、Git diff、byte equalityを確認する。
9. HTML browser validationを通し、authoritative fileをTailscaleへpublishする。
10. 最終状態をcommit/pushし、Issue ID、path、validation、URL、unpublish commandを報告する。

### 完了時に残してはならない曖昧さ

- Epic 365 と Full Regression sibling Epic の責務混在。
- deprovision と purge の権限混在。
- assessment と executable plan の混在。
- code rollback と operation forward recovery の混在。
- directory binding identity と child mutation snapshot の混在。
- public compatibility と private implementation preservation の混在。
- Artifact / HTML / external answer を canonical authority と誤認する状態。
- ChatGPT生成fileを人手で意味変更して「そのまま採用」と呼ぶ状態。
