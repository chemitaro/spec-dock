---
種別: 要件定義書（Issue）
ID: "iss-00344"
タイトル: "Workbench Shell Scaffolding"
関連GitHub: ["#344"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-29"
親: ["epic-00343", "init-local-00002"]
---

# iss-00344 Workbench Shell Scaffolding — Issue 要件定義

## 0. 文書の位置づけ

この文書は、fresh な SpecDock root と今後作成される Initiative、Epic、Issue に optional Workbench shell を提供するための、観測可能な成果、境界、受け入れ条件を定義する。

実装方法、変更ファイル、テスト実行順序は `design.md` と `plan.md` で扱う。generic single-file Artifact import は `iss-00345`、candidate wheel を使った統合 E2E、dogfood projection、full regression、Epic 全体の最終レビューと PR 送達は `iss-00346` の責務とする。

## 1. 目的と観測可能な成果

### 1.1 目的

fresh な SpecDock root、および今後新規作成される Initiative、Epic、Issue に、利用方法と権限境界を説明する tracked `.workbench/README.md` を含む optional Workbench shell を提供する。

Workbench は一時的、worktree-local、破棄可能、non-canonical であり、README 以外の内容は Git 管理外とする。既存 root および既存 node への backfill は行わない。

### 1.2 完了後に観測できること

1. fresh target で `spec-dock init` を実行すると、`spec-dock/.workbench/README.md` が生成される。
2. 今後新規作成する Initiative、Epic、Issue の各 node 直下に `.workbench/README.md` が生成される。
3. root と3種類の node の README は byte-identical である。
4. 各 `.workbench/README.md` は Git tracking 対象になり、同じ `.workbench/` 内のその他の entry は深さや形式によらず ignore される。
5. tracked README は通常の Git checkout により別 worktree へ現れる。
6. ignored な作業ファイルは checkout だけでは別 worktree へ移らず、必要な場合だけ明示的な `workbench copy` で移せる。
7. source tree、wheel、sdist、installed package resources のすべてに4つの Workbench README asset が収録される。
8. shipped docs が Workbench shell、Git 境界、manual copy、evidence-only authority を一貫して説明する。

### 1.3 完了後に観測できてはいけないこと

- 既存 root または既存 node への自動 backfill。
- Workbench または README の不在を理由とする validation error。
- `.workbench/README.md` 以外の Workbench 内容の Git 追跡。
- automatic copy、watch、sync、copy-back。
- README または Workbench 内容を node、Artifact、ADR、dependency、authoring source として解釈する挙動。
- `.workbench/.gitkeep` の生成。
- `iss-00345` が所有する generic import 実装。
- `iss-00346` が所有する dogfood projection、full regression、PR 作成または merge。

### 1.4 この Issue の種類

- [x] 新規振る舞いの追加
- [x] 既存振る舞いの変更
- [x] 仕様・文書の明確化
- [x] テンプレート変更
- [x] CLI / script 挙動変更
- [x] migration / compatibility を伴う変更
- [x] セキュリティ・プライバシー / authorization に関係する変更

## 2. 背景と現状

現行 provider scaffold は Workbench 全体を `.gitignore` で除外しており、利用方法を説明する tracked file を生成しない。fresh root や新規 node で `.workbench/README.md` を自動生成する契約もない。

そのため、利用者や model は Workbench の用途、Git 境界、Artifact への明示 import、canonical adoption との違いを Workbench 自体から確認できない。また、空 directory を Git に残すための `.gitkeep` は利用規約を伝えず、本件の目的に適合しない。

一方で、既存の Workbench は optional、ignored、semantic に opaque であり、`workbench copy` は明示的な one-shot operation として存在する。この互換境界は維持する必要がある。

### 2.1 根拠

- 親 Epic:
  - `../../requirement.md`
  - `../../design.md`
  - `../../plan.md`
- ChatGPT authoring evidence:
  - `artifacts/20260728t153458z-chatgpt-output-chatgpt-issue-00344-planning-candidate.md`
- provider source:
  - `src/spec_dock/cli.py`
  - `src/spec_dock/assets/spec_dock/templates/`
  - `src/spec_dock/assets/spec_dock/.gitignore`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`
- packaging:
  - `pyproject.toml`
- relevant tests:
  - `tests/unit/infra/test_init_update.py`
  - `tests/unit/infra/test_runtime_fs_repo_workbench_opacity.py`
  - `tests/cli_runtime/test_runtime_new_doc_s09.py`
  - `tests/cli_runtime/test_workbench.py`

## 3. 親スコープと継承条件

### 3.1 親 Initiative

- Initiative: `init-local-00002`
- 継承する制約:
  - provider source は `src/spec_dock/` に置く。
  - `spec-dock/` は dogfooding projection であり、一次実装 authority にしない。
  - Artifact と canonical specification の authority を混同しない。

### 3.2 親 Epic

- Epic: `epic-00343`
- 継承する要件:
  - `E-RQ-001`: fresh root shell
  - `E-RQ-002`: future node shell
  - `E-RQ-003`: tracked README / ignored contents
  - `E-RQ-004`: optional presence
  - `E-RQ-005`: no-backfill
  - `E-RQ-006`: semantic opacity / disposable
  - `E-RQ-007`: manual copy only
  - `E-RQ-023`: Workbench copy compatibility
  - `E-RQ-024`: provider / distribution parity の Issue-local 部分
  - `E-RQ-025`: shell / copy に関する documentation

### 3.3 この Issue で再定義しないもの

- generic arbitrary-file Artifact import の CLI、source guard、filename、publication、privacy 契約。
- `artifact import chatgpt-output` の既存契約。
- Artifact naming grammar と root Artifact target。
- Workbench retention、TTL、session model。
- Workbench copy の automatic lifecycle。
- canonical adoption workflow。
- Epic の Issue 分割と dependency 方向。
- PR Delivery Gate と Merge Preparation Gate の最終所有者。

## 4. 関係者と代表シナリオ

| 関係者 | 役割 | この Issue との関係 |
|---|---|---|
| SpecDock 利用者 | root または node を作成して Workbench を利用する | README から用途と境界を確認する |
| 開発 agent / model | 一時作業ファイルを扱う | README を operator guidance として参照する |
| installer CLI | fresh root を生成する | root Workbench shell を fresh-init-only で配置する |
| repo-local runtime | Initiative / Epic / Issue を生成する | node template から Workbench shell を配置する |
| Git | tracked file を checkout する | README のみを materialize し、他の内容を ignore する |
| package consumer | wheel / sdist を利用する | provider asset を installed resources から取得する |
| reviewer | 要件・実装・証跡を確認する | no-backfill、opacity、package parity を判定する |

### SC-344-001 Fresh root

- 前提: target に `spec-dock` path が存在しない。
- 操作: `spec-dock init <target>` を実行する。
- 期待結果:
  - `spec-dock/.workbench/README.md` が生成される。
  - README は Git tracking 候補になる。
  - Workbench のその他の entry は ignore される。

### SC-344-002 Future node

- 前提: Issue 344 の provider template が導入されている。
- 操作: Initiative、Epic、Issue のいずれかを新規作成する。
- 期待結果:
  - 新しい node だけに `.workbench/README.md` が生成される。
  - create plan、command result、filesystem の path 集合が一致する。
  - existing ancestor と sibling は変更されない。

### SC-344-003 Existing workspace update

- 前提: root と既存 node に `.workbench/README.md` がない。
- 操作: `spec-dock update` または existing workspace の更新経路を実行する。
- 期待結果:
  - managed templates、docs、runtime、ignore 契約は更新される。
  - existing root / node には README を生成しない。
  - 更新後に新規作成した node には README を生成する。

### SC-344-004 Linked worktree

- 前提: README が commit され、source worktree に ignored な作業ファイルがある。
- 操作:
  1. Git linked worktree を作成する。
  2. 必要な場合だけ `workbench copy` を実行する。
- 期待結果:
  - README は通常 checkout で新 worktree へ現れる。
  - ignored な作業ファイルは checkout だけでは現れない。
  - 明示 copy 後にだけ ignored な作業ファイルが移る。
  - automatic sync または copy-back は発生しない。

### SC-344-005 Semantic opacity

- 前提: Workbench 内に README、fake metadata、ADR-like Markdown、binary、invalid UTF-8 がある。
- 操作: validate、sync、dependency check、default discovery を実行する。
- 期待結果:
  - Workbench subtree の内容は意味解釈されない。
  - Workbench 内容を理由とする node、ADR、dependency、authoring source の増減や decode error が発生しない。

## 5. 対象範囲

### 5.1 In scope

- fresh-init-only root Workbench shell。
- future Initiative / Epic / Issue Workbench shell。
- 4つの byte-identical な provider README asset。
- README の guidance contract。
- README-only Git tracking 契約。
- installer fallback `.gitignore` との一致。
- existing root / node no-backfill。
- optional presence と semantic opacity。
- existing `workbench copy` の focused compatibility。
- package-data include / exclude の調整。
- source、wheel、sdist、installed resource の exact README inventory。
- provider-first docs。
- Issue-local focused tests と evidence destination。
- `iss-00346` への deferred PR delivery record。

### 5.2 Out of scope

- `spec-dock artifact import file` の実装。
- root または node Artifact destination の実装。
- arbitrary-file source validation、publication、naming、privacy。
- existing root / node の migration または backfill command。
- Workbench automatic copy、watch、sync、copy-back。
- Workbench content classifier、retention、expiration、cleanup。
- Workbench を canonical source にする変更。
- candidate wheel を使った full end-to-end product verification。
- dogfood `spec-dock/**` への正式 projection。
- full test suite closure。
- Epic-wide final QA / code / spec review。
- push、PR 作成、merge preparation、merge。

### 5.3 変更しないもの

- existing `workbench copy` の source-wins、destination-only preserve、one-shot という公開挙動。
- existing Workbench 内の user content、bytes、names、mtime。
- existing root / node の files。
- `validate`、`sync`、dependency、active context の semantic input。
- node ID、metadata、dependency topology。
- Artifact または ADR の既存 contract。
- Git worktree lifecycle と GitHub Issue state。

## 6. 要件

### I344-RQ-001 Fresh root shell

`spec-dock` が存在しない target への fresh init は、root に `.workbench/README.md` を生成しなければならない。

- 空 placeholder または `.gitkeep` を代替として生成してはならない。
- root Workbench または README が後から削除されても workspace は valid でなければならない。

### I344-RQ-002 Future node shell

今後新規作成される Initiative、Epic、Issue には、各 node 直下の `.workbench/README.md` を生成しなければならない。

- create plan、command result、filesystem で README path が一致しなければならない。
- node 作成を契機として ancestor または sibling へ README を追加してはならない。

### I344-RQ-003 README guidance

root と各 node kind の README は byte-identical とし、少なくとも次を明示しなければならない。

1. Workbench は一時的、worktree-local、disposable、non-canonical である。
2. Git tracking を意図する Workbench file は `README.md` だけである。
3. その他の Workbench file は Git に ignore される。
4. 保存価値のある file は対象 scope の `artifacts/` へ `spec-dock artifact import file` で明示 import する。
5. Workbench file は自動 copy / sync されず、必要な場合だけ manual `workbench copy` を使う。
6. Git ignore は security boundary ではなく、禁止された secret を保存してはならない。
7. file の明示指定または import は read / import authorization に限られ、import 結果は evidence-only である。canonical adoption には別の reviewed workflow が必要である。
8. tracked README は通常の Git checkout で別 worktree へ現れ、manual copy が必要なのは ignored な作業ファイルである。
9. 人間、model、tool は README を含む Workbench content を canonical input として扱ってはならない。

### I344-RQ-004 README-only tracking

各 scope の `.workbench/README.md` だけを Git tracking 可能とし、同じ Workbench 内のその他の entry を ignore しなければならない。

- file の深さ、extension、encoding、content によって例外を作ってはならない。
- nested `README.md` と case variant `readme.md` を tracking 対象にしてはならない。
- `.workbench-notes` など near-name directory へ Workbench 用 ignore rule を適用してはならない。

### I344-RQ-005 Optional presence and no-backfill

Workbench と README の存在は validity 要件ではない。

- existing root / node へ README を追加してはならない。
- update、existing workspace への init / update、validate、sync、active 切替、Artifact / ADR 作成を backfill 契機にしてはならない。
- future node 作成時も新規 node 以外へ README を追加してはならない。
- existing Workbench の entry、bytes、names、mtime を変更してはならない。

### I344-RQ-006 Semantic opacity and disposability

Workbench subtree は default semantic discovery から除外され続けなければならない。

- README を node metadata、Artifact、ADR、dependency、authoring source または canonical guidance source として解釈してはならない。
- Workbench の削除または worktree 破棄は SpecDock validity を損なってはならない。
- README は operator guidance であって workflow authority ではない。

### I344-RQ-007 Git checkout and manual copy positioning

tracked README は通常の Git checkout で他 worktree へ materialize されなければならない。

- linked worktree 作成だけで ignored work file を移行してはならない。
- manual `workbench copy` は ignored work file を必要時に移すための明示的 one-shot operation とする。
- automatic hook、watch、sync、copy-back を追加してはならない。
- existing `workbench copy` の ignored content に対する公開挙動を壊してはならない。

### I344-RQ-008 Provider and distribution parity

4つの Workbench README asset は provider source tree、built wheel、built sdist、installed package resources の全 surface へ収録されなければならない。

template README の package inventory は次の exact allowlist とする。

- existing `templates/README.md`
- root Workbench README
- Initiative Workbench README
- Epic Workbench README
- Issue Workbench README

allowlist 外の nested template README を意図せず配布してはならない。

### I344-RQ-009 Compatibility

existing workspace の validity、Workbench の optional 性、semantic opacity、explicit `workbench copy` command surface、one-shot / noncanonical / disposable / no-sync 契約、existing user content、provider-first source-of-record 境界を維持しなければならない。

### I344-RQ-010 Documentation

shipped provider docs は fresh root / future node shell、existing scope no-backfill、optional presence、README-only tracking、ignored / disposable / noncanonical content、Git checkout と manual copy の役割分担、no automatic sync、Git ignore は security boundary ではないこと、explicit import は evidence-only であることを一貫して説明しなければならない。

generic import の実装は `iss-00345` の責務であることも明記する。

## 7. 受け入れ条件

| ID | 対応要件 | 受け入れ条件 |
|---|---|---|
| `AC-344-001` | `I344-RQ-001` | fresh init で root `.workbench/README.md` が生成され、existing init / update では backfill されない |
| `AC-344-002` | `I344-RQ-002` | 新規 Initiative / Epic / Issue の各 node にだけ README が生成され、create plan / result / filesystem が一致する |
| `AC-344-003` | `I344-RQ-003` | 4 README が byte-identical で9つの guidance element を含む |
| `AC-344-004` | `I344-RQ-004` | top-level README だけが trackable で、nested / case variant / other payload は ignore される |
| `AC-344-005` | `I344-RQ-005` | update、既存操作、新規 child 作成で existing root / ancestor / sibling が変更されない |
| `AC-344-006` | `I344-RQ-006` | README、fake metadata、ADR-like file、binary、invalid UTF-8 が semantic discovery と validation 結果を変えない |
| `AC-344-007` | `I344-RQ-007` | linked worktree には README が checkout され、ignored file は manual copy 後にだけ現れ、README bytes は変わらない |
| `AC-344-008` | `I344-RQ-008` | source / wheel / sdist / installed inventory が exact allowlist と一致し、4 README bytes が一致する |
| `AC-344-009` | `I344-RQ-009` | current `workbench copy` と existing workspace の focused regression が通る |
| `AC-344-010` | `I344-RQ-010` | shipped docs が shell、Git、copy、security、authority、Issue 境界を矛盾なく説明する |

## 8. 例外・境界条件

- target の `spec-dock` が file、directory、または symlink として既に存在する場合は fresh root とみなさない。
- fresh / existing 判定は installer mutation より前に固定する。
- pre-existing empty `spec-dock` directory も existing root とみなし backfill しない。
- existing user-created `.workbench/README.md` を update で上書きしない。
- Workbench README の削除は validation failure としない。
- directory symlink / descendant symlink は Workbench copy の既存 security rule に従い、本 Issue で緩和しない。
- binary、invalid UTF-8、large file、nested directory の有無は semantic discovery に影響しない。
- package backend の hidden directory 処理は build artifact と installed resource で実測する。

## 9. 非機能要件

### 9.1 互換性

- schema migration を追加しない。
- existing root / node を書き換えない。
- Workbench の有無に依存しない既存 command の成功条件を維持する。

### 9.2 セキュリティとプライバシー

- Git ignore を secret 保護手段として説明しない。
- README 以外の Workbench content を Git へ露出させない。
- Workbench content の semantic parse、network upload、automatic import を追加しない。

### 9.3 可観測性

- init / create の result path と実 filesystem path が一致する。
- package inventory と byte parity を machine-verifiable にする。
- focused test、build、review 結果を Issue report に記録できる。

### 9.4 性能

- README 追加による create plan は固定4 asset 以下の増分である。
- Workbench subtree の再帰 semantic scan を追加しない。

## 10. リスク信号

| ID | リスク信号 | 必須対応 |
|---|---|---|
| `RS-344-001` | existing root / node に README が追加された | blocking regression として修正し再レビューする |
| `RS-344-002` | README 以外の Workbench content が Git status に現れた | ignore 契約を修正し、nested / case variant test を追加する |
| `RS-344-003` | Workbench 内容が discovery / validation 結果を変えた | semantic opacity 回帰として修正する |
| `RS-344-004` | source にはあるが wheel / sdist / installed resource にない | package-data を修正し全 surface を再検証する |
| `RS-344-005` | README を得るために manual copy が必要と説明された | Git checkout と manual copy の役割分担を修正する |
| `RS-344-006` | Issue 345 / 346 の責務を実装または完了主張した | scope を戻し parent dependency に defer する |

## 11. 完了条件

- `AC-344-001` から `AC-344-010` がすべて Issue-local evidence で満たされる。
- requirement、design、plan が fresh `spec-reviewer` の pass を得る。
- focused implementation / QA / code / spec review gate が pass する。
- Issue report に実行済みの証跡、未実施事項、`iss-00346` への deferred delivery record が記録される。
- `iss-00346 -> iss-00344` dependency が維持される。
- 本 Issue では PR-ready、merge-ready、Issue finish、Epic completion を主張しない。

## 12. 仮定と未確定事項

- README の exact wording はこの Issue の design で固定するが、9つの guidance element は変更しない。
- `workbench copy` は opaque whole-tree merge の既存実装を維持し、README 専用 filter は追加しない。
- `pyproject.toml` の broad nested README exclusion は exact distribution allowlist と両立するよう design で解決する。
- hidden `.workbench/README.md` の wheel / sdist 収録挙動は `uv build` 実測まで未検証である。
- manual copy による README mtime 変化は公開契約にしない。公開互換性は content no-diff で判定する。
