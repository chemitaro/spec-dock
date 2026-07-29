
# Issue #344 delivery-boundary amendment analysis

## 結論

**現行 canonical contract のままでは、Issue #344 を mergeable PR まで進めてはならない。**
ただし、機能スコープを広げる必要はない。最小修正は、**Issue #344 の delivery boundary だけを変更し、Issue-local PR に不可欠な dogfood projection、既定 PR test lane、PR 作成・観測・merge preparation を Issue #344 へ移す**ことである。

Issue #344 は、次の条件付きで自身の ready PR を所有できる。

1. Issue #344 の `requirement.md`、`design.md`、`plan.md` と親 Epic `plan.md` を先に整合させる。
2. Issue #344 固有の provider 変更だけを checked-in dogfood mirror へ provider-first で projection する。
3. PR-triggered `Provider CI` と同一の `make lint`、`uv run pytest` をローカルで pass させる。
4. Issue-wide の fresh QA/code/spec review 後に ready PR を作成し、最終 head SHA に対する Actions、PR review、thread、merge-conflict、branch-protection 状態を観測する。
5. PR 作成後は branch を Issue #344 の blocker repair 以外で変更せず、Issue #345/#346 の実装を同じ PR head に積まない。
6. merge、auto-merge、branch deletion、Issue finish は行わない。

これは、添付 brief が求める「Issue #344 の全実装 step 完遂と mergeable PR 作成」を満たすための delivery-topology amendment であり、generic import、candidate-wheel consumer E2E、Epic-wide integration を Issue #344 に吸収する提案ではない。

| 判断項目                             | 推奨判断                                                                                                                            |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Issue #344 が自身の ready PR を所有できるか | **できる。ただし canonical amendment が先**                                                                                              |
| Issue #344 へ移す deferred 項目       | Issue固有のdogfood projection、default PR lane、PR作成・観測・merge preparation                                                            |
| checked-in dogfood projection    | **必須**                                                                                                                          |
| Issue #346 に残す項目                 | candidate-wheel consumer E2E、integrated consumer/dogfood、opt-in full regression、cross-feature repair、Epic-wide review、残余Epic PR |
| S99                              | PR delivery と external observation を含むよう変更。ただし projection 実装は新設 S95 で先に閉じる                                                      |
| 親 Epic plan                      | **実装再開前に amendment 必須**                                                                                                         |
| dependency metadata              | **変更不要**。`iss-00346 -> iss-00344, iss-00345` を維持                                                                                |
| 現時点の実行可否                         | **planning amendment と fresh spec-review が完了するまで blocked**                                                                      |

---

## 1. Repository facts observed

### 1.1 Source identity

2026年7月29日時点で GitHub connector から以下を確認した。

* Repository `chemitaro/spec-dock` はアクセス可能で、default branch は `main`。
* Branch `iss-00344-workbench-shell-scaffolding` は取得可能で、head は指定どおり `cc17c25530f8778b52b006b878c780dafeccf57f`。
* 同 commit は S01 の fresh implementation review PASS と evidence-only closure を記録する commit である。
* GitHub compare は branch が `main` より **39 commits ahead、0 commits behind**、merge base が current `main` の `72424ca0ef99cfbe2d2f73c63483633a446ad5a5` であると返した。
* branch を head とする既存 PR は connector 検索では見つからなかった。
* exact head に紐づく pull-request-triggered workflow run はまだ存在しない。

現在の branch diff は Issue #344 の実装だけではなく、Epic #343 の planning baseline、Issue #345/#346 の node scaffold、関連 planning evidence も含む。これは sibling implementation の吸収ではないが、PR body と final review では明示する必要がある。

### 1.2 Current Issue #344 contract

Issue #344 requirement は、generic file import を Issue #345、candidate-wheel E2E、dogfood projection、full regression、Epic-wide review、PR delivery を Issue #346 の責務としている。さらに「Issue #346 が所有する dogfood projection、full regression、PR 作成または merge」を Issue #344 の完了後に観測されてはならないものとしている。

同 requirement の scope section も、以下を明示的に out-of-scope としている。

* candidate-wheel full E2E
* dogfood `spec-dock/**` projection
* full test suite closure
* Epic-wide final review
* push、PR creation、merge preparation、merge

一方で、通常の `spec-dock update` による managed assets 更新自体は許可されている。

Issue completion 条件も、PR-ready、merge-ready、Issue finish、Epic completion を主張しないよう要求している。

Issue design では dogfood `spec-dock/**` を primary implementation にせず、Issue #346 が projection を扱うと定めている。また sibling handoff でも、candidate-wheel E2E、dogfood projection、full regression、Epic-wide review、PR delivery を Issue #346 に割り当てている。

Issue plan の計画タグは現在、次のとおりである。

```text
per_issue_pr: false
delivery_owner: iss-00346
```

本文も candidate-wheel consumer E2E、dogfood projection、full regression、PR delivery は Issue #346 が所有し、merge と Issue finish を Issue #344 の自動実行範囲外としている。

### 1.3 S01 state and known red suite

S01 report は、focused tests、Ruff、format、diff check、および fresh code review PASS を記録している。一方、default fast suite は次の結果だった。

```text
670 passed, 2042 skipped, 2 failed
```

失敗 node は以下である。

```text
tests/unit/infra/test_init_update.py::TestInitUpdate::
  test_checked_in_dogfooding_mirror_docs_match_provider_assets

tests/unit/infra/test_init_update.py::TestInitUpdate::
  test_checked_in_dogfooding_mirror_templates_match_provider_assets
```

report は当時、この2件を Issue #346 への deferred dogfood projection と分類していた。これは旧 plan 下では妥当な S01 判定だったが、Issue #344 自身が PR を作るという最新 instruction の下では delivery gate に残せない。

S01 の implementation review 自体は PASS で、scope creep なし、finding 0 と記録されている。したがって、今回必要なのは S01 implementation のやり直しではなく、**後続 delivery step の追加と旧 defer 判断の supersession** である。

### 1.4 Why the two failures are merge blockers

この2つの parity test は、偶然 default lane に入っているのではない。repository の test-lane contract は両 node を `REQUIRED_FAST_NODE_IDS` に明示している。したがって、skip、marker変更、full-regression lane への移動は契約回避にあたる。

`pyproject.toml` も、`fast` を development と pull request の default provider lane、`full_regression` を default lane から除外する long-running lane と定義している。

PR-triggered GitHub Actions の `Provider CI` は、次だけを実行する。

```text
make lint
uv run pytest
```

一方、`uv run pytest --run-full-regression` は `main` push または manual dispatch の別 workflow で、PR trigger ではない。

したがって、次の区別が必要である。

| Test lane                                         | Issue #344 amendment後の所有 |
| ------------------------------------------------- | ------------------------ |
| `uv run pytest` default PR lane                   | **Issue #344 に移す**       |
| `uv run pytest --run-full-regression` opt-in lane | **Issue #346 に残す**       |

### 1.5 Provider and checked-in dogfood divergence

Provider `.gitignore` は既に新しい3-rule contract を持つ。

```gitignore
**/.workbench/*
!**/.workbench/README.md
**/.workbench/README.md/**
```

Checked-in dogfood の `spec-dock/.gitignore` は、依然として `.workbench/` 全体を ignore する旧契約である。

Provider には root / Initiative / Epic / Issue 用の canonical Workbench README asset があり、README-only tracking、noncanonical authority、secret 非保存、manual copy、explicit Artifact import を説明している。

Parity test は次を要求している。

* `spec-dock/.gitignore` と provider `.gitignore` の byte equality

* checked-in `spec-dock/templates` と provider templates の **全 inventory equality**

* 各 template file の content equality

### 1.6 Provider-first projection path

Installer `update` は provider の managed `docs/templates/scripts/system` を checked-in target へ同期し、provider `.gitignore` をコピーする。`spec-dock/initiatives/**` は永続領域として削除・置換しない。また root Workbench README の生成は fresh install のみなので、existing dogfood root への backfill は行わない。

CLI contract は `spec-dock update [path]` を正式に公開しており、project script も `spec-dock = "spec_dock.cli:main"` と定義されている。

したがって、projection は dogfood 側の手編集ではなく、原則として次で行うべきである。

```bash
uv run spec-dock update .
```

ただし、この command は全 managed surface を同期するため、**実行後 diff を exact allowlist で検査し、Issue #344 と無関係な drift が出た場合は commit せず停止する**必要がある。

### 1.7 Parent Epic and Issue #346

親 Epic plan は、Candidate 1/2 を local milestone まで閉じて per-Issue PR を作らず、Candidate 3 が dogfood、candidate wheel、full regression、Epic-wide reviews、push、PR delivery、merge preparation を一括所有すると定めている。

Issue #346 の dependency metadata は現在、次の2 edge を保持している。

```json
"depends_on": [
  "iss-00344",
  "iss-00345"
]
```

Issue #346 の local requirement はまだ具体化済み canonical contract ではなく、placeholder を残す scaffold 状態である。したがって、現時点での Issue #346 scope authority は親 Epic plan である。

---

## 2. Contradiction analysis

最新 instruction と canonical contract の衝突は、単一文書ではなく4層に存在する。

| Layer             | Current claim                             | Latest instructionとの衝突                              |
| ----------------- | ----------------------------------------- | --------------------------------------------------- |
| Issue requirement | dogfood/full regression/PR は #346         | #344 自身が PR-ready になるには dogfood/default lane/PR が必要 |
| Issue design      | dogfood projection は #346                 | provider/dogfood parity failure を #344 PR に残せない     |
| Issue plan        | `per_issue_pr:false`, owner #346、S99はPR禁止 | 明示的に PR 作成を求められている                                  |
| Parent Epic plan  | Candidate1/2はPRなし、Candidate3が唯一のPR owner  | per-Issue PR topology へ変更が必要                        |

この矛盾を report だけで上書きしてはならない。report は実行証跡であり、normative scope を再定義する場所ではない。

また、default suite の2 failure を残したまま ready PR を作ることもできない。PR-triggered workflow 自体が `uv run pytest` を実行し、対象2 node は required-fast として固定されているためである。

一方、これを理由に Issue #346 全体を Issue #344 へ移す必要もない。PR mergeability に必要なのは次の限定された delivery items だけである。

1. Issue #344 によって変更された provider managed assets の checked-in projection。
2. PR default lane の全 pass。
3. Issue-local PR 作成、CI/review observation、merge preparation。

candidate-wheel consumer E2E、external-file import、cross-feature integration、opt-in full regression、Epic aggregate review は、現在の2 failure と Issue #344 PR mergeability の直接原因ではない。

---

## 3. Recommended minimal amendment

### 3.1 Ownership split after amendment

| Responsibility                                          |           Issue #344 |                                    Issue #346 |
| ------------------------------------------------------- | -------------------: | --------------------------------------------: |
| Workbench shell provider implementation                 |              primary |                       integrated verification |
| Issue #344 provider docs                                |              primary |                             integrated parity |
| Issue #344 changed assetsのchecked-in dogfood projection |          **primary** | later integrated re-projection / verification |
| `make lint` + default `uv run pytest`                   | **PR closure owner** |                        final integrated rerun |
| Issue #344 ready PR                                     |            **owner** |                                     not owner |
| candidate-wheel consumer E2E                            |                   no |                                     **owner** |
| fresh / pre-feature updated consumer matrix             |                   no |                                     **owner** |
| generic single-file import                              |                   no |             integration only; primary is #345 |
| manual external-file root/node scenario                 |                   no |                                     **owner** |
| `uv run pytest --run-full-regression`                   |                   no |                                     **owner** |
| cross-feature integration repairs                       |                   no |                                     **owner** |
| Epic-wide E-RQ/E-AC closure map                         |                   no |                                     **owner** |
| Epic base/head aggregate QA/code/spec/decision review   |                   no |                                     **owner** |
| remaining Epic integration PR                           |                   no |                                     **owner** |
| merge                                                   |           human only |                                    human only |

### 3.2 Mandatory items moved into Issue #344

#### A. Checked-in dogfood projection

S90 後に、Issue #344 が変更した provider assets を checked-in dogfood mirror へ projection する。

対象は、実際の provider diff に対応する exact mirror に限定する。

* `spec-dock/.gitignore`
* `spec-dock/templates/{root,initiative,epic,issue}/.workbench/README.md`
* S90 で変更された provider docs に対応する checked-in docs
* S90 で変更された `templates/README.md` の mirror

`spec-dock update .` が上記以外を変更した場合は、以下のどちらかに分類する。

* 既存 provider/dogfood drift の必須修復: planning amendment に追加して fresh review
* Issue #344 と無関係な drift: commitせず defer

`spec-dock/initiatives/**`、existing root/node Workbench、Workbench payload、Issue #345/#346 implementation は変更禁止である。

#### B. Default PR lane

以下を Issue #344 の final local gate とする。

```bash
make lint
uv run pytest
```

`make lint` は repository CI と同じく Ruff check、Ruff format check、Mypy を実行する。

#### C. PR creation and observation

Issue #344 は次を所有する。

* branch push
* ready PR creation
* base `main`
* head `iss-00344-workbench-shell-scaffolding`
* `Closes #344`
* `Refs #343`
* latest head SHA の Actions/review/thread/merge-state observation
* blocking repair loop
* merge preparation
* human merge前停止

PR creator contract も、PR作成後に URL、number、base、head、latest SHA を返し、observation または merge-preparer へ続けることを要求している。

### 3.3 Items remaining deferred to Issue #346

以下は Issue #344 に移さない。

1. `artifact import file` と generic import の機能実装。
2. Candidate wheel を temporary consumer repo に install する integrated CLI E2E。
3. Pre-feature existing consumer update/no-backfill と post-update future node matrix。
4. External filesystem source、privacy sentinel、unsupported capability を含む manual generic-import scenario。
5. Issue #345 と組み合わせた integrated dogfood projection。
6. `uv run pytest --run-full-regression`。
7. Candidate 1/2/3 全体の Epic-base-to-final-head aggregate review。
8. E-RQ-001〜025 / E-AC-001〜020 の Epic closure map。
9. Issue #345 と integration repairs を含む残余 Epic PR。
10. Epic completion と人間 merge。

Issue #346 は「Issue #344 の dogfood projection を一度も行っていない状態」を前提にしなくなるが、**Issue #345 後の integrated provider/dogfood parity を再検証する責務**は維持する。

---

## 4. Exact canonical sections and claims to change

### 4.1 Issue #344 `requirement.md`

| Section            | Required amendment                                                                                                           |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| `0. 文書の位置づけ`       | #346 への一括 defer を、Issue-local PR と Epic-integrated delivery に分割                                                              |
| `1.2 完了後に観測できること`  | checked-in projection、default PR lane pass、open ready PR を追加                                                                 |
| `1.3 観測できてはいけないこと` | dogfood projection/PRの全面禁止を削除し、Issue #344固有projectionだけ許可。generic import、opt-in full regression、Epic-wide review、mergeは禁止のまま |
| `3.3 再定義しないもの`     | 「PR final owner」を固定対象から外し、親Epic amendmentに従う                                                                                 |
| `5.1 In scope`     | provider-first dogfood projection、default PR lane、PR delivery/observationを追加                                                 |
| `5.2 Out of scope` | `dogfood spec-dock/**` と `PR creation/merge preparation` の全面除外を狭める                                                           |
| `10. リスク信号`        | `RS-344-006` を「#346 scopeを吸収した場合」に限定し、approved local projection/PRは違反ではないとする                                                 |
| `11. 完了条件`         | deferred PR record/no-PR-ready claimを、ready PR + merge-prepared evidenceへ置換                                                  |
| `11. 完了条件`         | merge、auto-merge、Issue finish、Epic completionは引き続き禁止                                                                         |

追加する requirement claim は、概ね次の形がよい。

> Issue #344 は、自身の provider changes と shipped docs を checked-in dogfood mirror へ provider-first に projection し、default PR lane を green にしたうえで、`main` 向け ready PR の作成と merge-preparation evidence を所有する。candidate-wheel consumer E2E、generic import integration、opt-in full regression、Epic-wide review、および merge は所有しない。

### 4.2 Issue #344 `design.md`

新しい設計 decision を1件追加する。

#### `DES-344-010 Issue-local projection and PR boundary`

設計要点:

* provider source remains authoritative。
* projection は `spec-dock update` による managed mirror sync。
* dogfood file の手編集を正規経路にしない。
* projection は S90 後に一度行う。
* existing root/node Workbench を backfill しない。
* `spec-dock/initiatives/**` を projection mutation に含めない。
* default PR lane と actual PR observation を Issue-local closure に含める。
* candidate-wheel consumer E2E と integrated dogfood は #346 に残す。

既存 section の変更:

| Section               | Required amendment                                                                           |
| --------------------- | -------------------------------------------------------------------------------------------- |
| `9. 変更責任とファイル境界`      | dogfood rowを「Issue #344 changed managed assetsのprojectionはS95、integrated projectionは#346」に変更 |
| `10. 検証設計`            | projection parity closureを追加                                                                 |
| `12. sibling handoff` | #346のPR ownershipを「remaining Epic integration PR」に変更                                         |
| `12. sibling handoff` | default laneと#344 PRはhandoff対象外、既に#344が閉じることを明記                                              |

### 4.3 Issue #344 `plan.md`

計画タグは次のように変更する。

```text
per_issue_pr: true
issue_pr_delivery_owner: iss-00344
epic_integration_delivery_owner: iss-00346
provider_first: true
```

単一の `delivery_owner` を残す場合、Issue PR と Epic PR のどちらを指すか曖昧になるため、分割 field が望ましい。

変更対象:

| Section                    | Required amendment                                              |
| -------------------------- | --------------------------------------------------------------- |
| 計画タグ                       | 上記 ownership split                                              |
| `0. 文書の位置づけ`               | local dogfood/default lane/PRを#344へ移す                           |
| `1. Plan Readiness`        | delivery amendmentへのfresh spec-reviewを新開始条件にする                  |
| `2. 実装戦略`                  | S95を追加                                                          |
| milestone/dependency table | `S90 -> S95 -> S99`                                             |
| must-not-have              | PR全面禁止をmerge/finish禁止へ狭める                                       |
| closure index              | `TC-344-011` と delivery gateを追加                                 |
| S90                        | provider docsまで。dogfood projectionはS95へhandoff                  |
| S99                        | PR delivery、observation、repair loop、external Result Approvalへ変更 |
| verification ladder        | default laneを#344、opt-in full regressionを#346に分離                |
| stop rules                 | PR branch freezeとsibling implementation禁止を追加                    |
| Final Exit Contract        | ready PR/merge-prepared evidenceを必須化                            |
| Follow-up                  | #346 handoffをintegrated responsibilitiesだけに縮小                   |

### 4.4 Issue #344 `report.md`

過去の S01 evidence は書き換えない。旧 plan 下で「2 failuresは#346 defer」と判断した事実は履歴として保持する。

追加するもの:

* 最新 user instruction の Decision Ledger entry。
* 本 analysis の EAL disposition。
* S01 の old defer を supersede する current delivery decision。
* amendment review SHA と verdict。
* S95 worker evidence、projection diff inventory、tests。
* authorization boundary に PR creation/observation を追加。
* merge、auto-merge、Issue finish、sibling implementation は authorization 外のまま。
* final local head、closure head、clean check。
* PR URL/number/base/head/head SHA。
* external observation status、Actions run/job IDs、review completion、thread state、mergeability。
* repair iteration があれば headごとの履歴。

### 4.5 Parent Epic `plan.md`

親 plan amendment は必須である。現行 plan が per-Issue PR を明示的に禁止し、Candidate 3 を唯一の PR delivery owner としているため、Issue docs だけの変更では矛盾が残る。

変更対象:

| Parent section            | Required amendment                                                                            |
| ------------------------- | --------------------------------------------------------------------------------------------- |
| `1. 目的と分割方針`              | Candidate1がIssue-local PRを持てる例外を追加                                                            |
| Candidate 1               | dogfood projection、default lane、Issue-local PRをdeliverableへ追加                                 |
| Candidate 3               | #344 PRのexclusive ownershipを削除し、remaining Epic integration PRへ変更                              |
| `5. Dependency / tranche` | Candidate1だけper-Issue PR exception。Candidate2は従来どおりlocal-only                                 |
| `5. Dependency / tranche` | #344 PR branch freezeとhuman merge後の#345 branch admissionを明記                                   |
| `6. G2`                   | Candidate1のPR delivery gateを追加                                                                |
| `6. G3/G4`                | integrated candidate-wheel/dogfood/full regression/Epic reviewは維持                             |
| `8. Rollout`              | #344 PR → human merge → #345 → #346 の安全なbranch topologyへ変更                                    |
| `9. Final exit`           | 最終Epic evidenceはoriginal Epic baseからfinal headまでをaggregate reviewし、#344の先行PRもevidence mapに含める |

特に、Issue #344 が main へ先に merge された後、Issue #346 の PR diff だけを見ると Issue #344 の変更が含まれない。そのため、Epic-wide review は引き続き **original Epic base から final integrated head までの aggregate commit range** を対象にしなければならない。

### 4.6 Issue #346 docs and dependency metadata

Issue #346 の local docs は placeholder scaffold であるため、Issue #344 実装再開前に具体化する必要はない。将来の Issue #346 planning 時に、amended parent plan と merged Issue #344 state を current source として取り込む。

Dependency metadata は変更しない。

```text
iss-00346 -> iss-00344
iss-00346 -> iss-00345
```

新しい `iss-00345 -> iss-00344` edge も追加しない。Candidate1/2 に product dependency はなく、今回必要なのは branch/PR sequencing gate であって機能依存ではない。これを dependency edge にすると意味を過剰に強める。

---

## 5. Updated step, closure, and handoff boundaries

## 5.1 Amendment gate before resuming implementation

S02 を再開する前に、次を完了する。

1. Issue requirement amendment。
2. Issue design amendment。
3. Issue plan amendment。
4. Parent Epic plan amendment。
5. report に decision/EAL dispositionを記録。
6. canonical amendment candidate commit を push。
7. exact SHA に対する fresh `spec-reviewer` PASS。
8. review evidence-only closure commit。
9. clean check と Result Approval。

S01 の implementation closure は維持する。S01 の当時の review を無効化する必要はない。

## 5.2 Existing implementation sequence

```text
S01 committed/PASS
  -> amendment gate
  -> S02 opacity/copy compatibility
  -> S03 distribution/package evidence
  -> S90 provider docs
  -> S95 checked-in projection/default PR lane
  -> S99 final review/PR delivery/observation
```

S02、S03、S90 の機能 scope と既存 closure IDs は変更しない。

## 5.3 New S95 — Checked-in Dogfood Projection and PR-lane Green

### Dependency

* S90 Result Approval 後のみ開始。
* S90 前に projection すると、S90 docs の再projectionが必要になり二重作業になるため禁止。

### Owner

* Projection operation と diff guard: `dev-coder`
* Canonical report integration: main orchestrator
* Fresh review: `code-reviewer`
* Final aggregate quality判断: S99 `qa-reviewer`

### Operation

```bash
uv run spec-dock update .
```

### Allowed changes

* Issue #344 の current provider diff に exact 対応する checked-in managed mirrors。
* 主に:

  * `spec-dock/.gitignore`
  * four Workbench README template mirrors
  * S90 changed docs mirrors
  * S90 changed `templates/README.md` mirror

### Forbidden changes

* `spec-dock/initiatives/**`
* existing root/node `.workbench` content
* Workbench payload
* generic import
* `workbench copy` production logic
* candidate-wheel consumer logic
* Issue #345/#346 implementation
* unrelated agent/skill/runtime drift

### Proposed closure

#### `TC-344-011 — Provider-first checked-in projection parity`

Close conditions:

1. projection command succeeds。
2. every changed dogfood path corresponds to an Issue #344 changed provider asset。
3. docs parity test passes。
4. template inventory/content parity test passes。
5. existing root/node no-backfill remains pass。
6. `spec-dock/initiatives/**` has no S95 mutation。
7. default `uv run pytest` has zero failure。
8. `make lint` passes。
9. fresh code review has no blocking/major finding。

#### Evidence IDs

* `EVD-012`: projection command、before/after path inventory、allowed-path disposition、parity/no-backfill tests。
* `EVD-013`: local PR lane、final review SHA、PR observation。

## 5.4 Revised S99 — Final Issue Quality and PR Delivery

S99 は review-only/local handoff から、**Issue-wide final quality + actual PR delivery + observation gate** へ変更する。

### Required order

```text
S95 Result Approval
  -> issue-wide local verification
  -> final pre-PR report integration
  -> review_target_sha commit/push
  -> fresh QA/code/spec reviews
  -> blocking findings repair and fresh re-review
  -> evidence-only final closure commit
  -> clean check
  -> push exact closure_head_sha
  -> create ready PR
  -> observe exact PR head
  -> repair/re-push/re-observe if needed
  -> github-mergeable / merge-prepared evidence
  -> S99 Result Approval
  -> stop before merge
```

### Non-circular evidence boundary

PR Actions と review observation は commit 後にしか得られないため、branch内 report に最終結果を自己参照的に書き戻してはならない。

最終 observation は、次の external evidence destination に置く。

* PR metadata / review / Actions
* GitHub Issue comment
* final orchestrator response
* external delivery ledger

PR observation 後に report へ書き戻すため branch を変更した場合、その commit が新しい PR head となるため、CI/review observation をすべてやり直す。

### Branch freeze

ready PR 作成後に許可される branch mutation は、次だけである。

* required Actions failure
* P0/P1 review finding
* visible merge conflict
* required branch-protection blocker
* amendmentで許可されたIssue #344 scope内修正

Issue #345/#346 の作業を同じ PR head に追加してはならない。

---

## 6. Final Exit Contract after amendment

Issue #344 は、次をすべて満たした場合だけ delivery complete candidate とする。

1. Existing `TC-344-001`〜`TC-344-010` が pass。
2. New `TC-344-011` が pass。
3. S01/S02/S03/S90/S95 が `committed` または evidence-qualified `approved-no-op`。
4. Issue #344 changed provider assets と checked-in dogfood mirrors が一致。
5. `make lint` が pass。
6. default `uv run pytest` が zero failure。
7. canonical validate/sync evidence が pass。
8. final local working tree が clean。
9. `origin/main` が final head の ancestor である。main が進んだ場合は integration 後に全 gate を再実行。
10. issue-wide fresh QA review が pass。
11. issue-wide fresh code review が pass。
12. requirement/design/plan/report/implementation/tests/docs を対象とする fresh spec review が pass。
13. ready PR が open。
14. base は `main`。
15. head branch は `iss-00344-workbench-shell-scaffolding`。
16. observed PR head SHA が final pushed SHA と一致。
17. `Provider CI / provider-tests` が成功。
18. current-head review に unresolved P0/P1 がない。
19. changes-requested review、unresolved blocking thread、merge conflict がない。
20. required checks、required reviews、conversation-resolution rule が確認されている。
21. `merge-prepared: yes` が成立。
22. GitHub platform requirementsも確認できた場合だけ `github-mergeable: yes` とする。
23. PR body は `Closes #344` と `Refs #343` を含み、Issue #345/#346をcloseしない。
24. merge、auto-merge、branch deletion、Issue close、`spec-dock issue finish` を行っていない。
25. candidate-wheel consumer E2E、opt-in full regression、generic import integration、Epic-wide reviewは未実施事項として #346 handoff に残る。

PR observation skill 自体も、最新 head、required Actions、blocking review、merge conflict、thread状態を merge-prepared predicate とし、platform requirements未確認時の `github-mergeable` claim を禁止している。

---

## 7. Exact tests and review gates

## 7.1 Existing focused gates

既存 plan の S02/S03/S90 focused gates はそのまま実行する。

代表 command:

```bash
uv run pytest tests/unit/infra/test_runtime_fs_repo_workbench_opacity.py
uv run pytest tests/cli_runtime/test_workbench.py

uv run pytest tests/unit/infra/test_init_update.py
uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_344_dual_distribution_paths_preserve_exact_workbench_readme_allowlist
uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_344_dual_distribution_paths_prune_disallowed_nested_readmes
```

S90 は provider docs の exact semantic assertion、Ruff check/format、fresh spec review を維持する。

## 7.2 S95 projection verification

```bash
git status --short

uv run spec-dock update .

git diff --name-only
git diff --check

uv run pytest -q -ra \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_mirror_docs_match_provider_assets \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_mirror_templates_match_provider_assets

uv run pytest -q -ra --run-full-regression \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_and_force_init_do_not_backfill_workbench_readme
```

補足:

* 最後の `--run-full-regression` は full suite 実行ではなく、focused heavy test node を policy skip させず実行するための opt-in である。
* `git diff --name-only` の結果は exact allowlist と比較する。
* `spec-dock/initiatives/**`、existing `.workbench`、unrelated managed assets が含まれた場合は S95 を close しない。

## 7.3 Issue-wide local PR-equivalent gate

GitHub `Provider CI` と同じ command を必須にする。

```bash
make lint
uv run pytest
```

加えて、SpecDock canonical health と Git state を確認する。

```bash
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync --no-github

git diff --check
git status --short

git fetch origin main
git merge-base --is-ancestor origin/main HEAD
```

期待値:

* `make lint`: pass
* `uv run pytest`: zero failure
* validate/sync: pass
* `git diff --check`: no output
* `git status --short`: empty
* `merge-base --is-ancestor`: exit 0

`uv run pytest --run-full-regression` 全 suite は Issue #344 closure には要求せず、Issue #346 に残す。

## 7.4 Fresh review gates

| Gate                  | Scope                                                      | Passing condition                |
| --------------------- | ---------------------------------------------------------- | -------------------------------- |
| Amendment spec review | Issue requirement/design/plan + parent Epic plan           | contradiction 0、scope transferなし |
| S95 code review       | projection diff、update path、no-backfill、test evidence      | blocking/major 0                 |
| Final QA review       | all Issue obligations、test quality、negative coverage       | pass                             |
| Final code review     | Epic planning baselineを含むIssue #344 aggregate branch diff  | blocking/major 0                 |
| Final spec review     | requirement/design/plan/report/source/tests/docs alignment | pass                             |
| PR observation review | exact PR head、Codex/current review boundary                | P0/P1 0、completion observed      |

既存 branch diff に Epic planning baseline と sibling scaffolds が含まれるため、final code/spec review はそれらも確認し、sibling implementation が混入していないことを明示する。

## 7.5 PR creation evidence

PR作成前に、次を記録する。

* selected base: `main`
* base resolution source
* current branch
* local final SHA
* clean status
* main ancestor check
* no existing PR
* diff stat/name inventory
* Issue #344 completion claim
* Issue #345/#346 non-completion claim

作成 command の canonical pattern:

```bash
gh pr create \
  --base main \
  --head iss-00344-workbench-shell-scaffolding \
  --title "<Japanese Issue #344 title>" \
  --body-file <reviewed-pr-body>
```

PR body には最低限、次を含める。

```text
Closes #344
Refs #343
```

Issue #345/#346 は `Closes` しない。

## 7.6 PR observation evidence

通常 flow:

```bash
./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh \
  --repo chemitaro/spec-dock \
  --pr <pr-number> \
  --head-sha <final-head-sha>
```

この script は head validation、Actions observation、deterministic Codex review request、review/thread collection を行い、stdout のJSONを authority とする。

必須 observation fields:

* PR URL / number
* open state
* ready / draft state
* base branch
* head branch
* latest head SHA
* observed head SHA
* Actions workflow run/job
* `Provider CI` terminal status
* current review completion signal
* P0/P1 inventory
* P2/P3 residual findings
* changes-requested state
* unresolved current thread count
* merge conflict / merge state
* branch-protection and required-review state
* observation limitations
* `merge-prepared`
* `github-mergeable` claim eligibility

PR head が変わった場合、旧 observation は stale とし、新しい SHA へ再実行する。

---

## 8. Updated handoff topology

最小で安全な branch topology は次である。

```text
Issue #344 branch
  -> Issue #344 ready PR
  -> human merge to main
  -> Issue #345 starts from updated main
  -> Issue #345 local milestone
  -> Issue #346 integrates #344 + #345
  -> remaining Epic integration PR
  -> human merge
```

Issue #344 PR が open のまま同 branch で Issue #345 を開始すると、PR head が #345 implementation を吸収し、Issue-local PR boundary が崩れる。

Stacked PR を採用する方法もあるが、base/head topology、review range、merge order、rebase repairが複雑になり、今回の「smallest amendment」には適さない。明示的な別 amendment がない限り、Issue #345 admission は Issue #344 の human merge 後とする。

これは product dependency ではなく delivery sequencing なので、dependency metadata は変更しない。

---

## 9. Risks

### R-1: Provider update may project unrelated drift

`spec-dock update .` は全 managed tree を同期する。current parity が既に別箇所でずれていれば、Issue #344 と無関係なファイルも変更される可能性がある。

**Mitigation:** clean S90 closure SHA から実行し、post-update path inventory を exact allowlist と照合する。外れた path は自動採用しない。

### R-2: Current branch PR is wider than implementation-only diff

branch は Epic planning baseline と sibling issue scaffoldsも含む。

**Mitigation:** PR body、code review、spec reviewで区別する。Issue #345/#346 の files は node/planning scaffold であり、implementation completionではないと記録する。

### R-3: Main can advance after local green

現時点では behind 0 だが、PR作成までに `main` が進む可能性がある。

**Mitigation:** final push直前とPR observation時に base ancestryを再確認する。integration commit/rebase後は、local gates、fresh reviews、observationを新SHAでやり直す。

### R-4: “merge-prepared” and GitHub “mergeable” are different

Local testsとreviewがpassしても、branch protection、required review、conversation resolutionが未確認ならGitHub mergeabilityを断定できない。

**Mitigation:** observer resultに加えて、GitHub platform requirementsを確認する。観測権限不足は human gate とし、mergeableを主張しない。

### R-5: S01 historical record becomes misleading if overwritten

S01 reviewは旧plan下でdogfood failure deferを妥当と判断した。

**Mitigation:** historical rowは保持し、新しい delivery amendment が後続closureで supersede したと追記する。

### R-6: Epic-wide review can lose Issue #344 after separate merge

Issue #346 PR diffがupdated main基準になると、先にmergeされたIssue #344はPR diffに現れない。

**Mitigation:** Epic final reviewのrangeをoriginal Epic baseからfinal integrated headまで固定し、先行PR SHA/merge commitをevidence mapへ含める。

---

## 10. Rejected alternatives

### A. Issue #346 全体を Issue #344 へ吸収する

却下。generic import、candidate-wheel consumer E2E、external-file/privacy scenarios、Epic-wide closureは、Issue #344 PRの2 parity failureを閉じるために不要である。

### B. Known 2 failures を残して ready PR を作る

却下。PR-triggered `Provider CI` が同じ `uv run pytest` を実行するため、ready/mergeable claimと両立しない。

### C. Parity tests を skip または full-regression laneへ移す

却下。両 node は `REQUIRED_FAST_NODE_IDS` である。テスト分類を変えるのは不具合修正ではなく契約弱化である。

### D. Dogfood filesを手作業でcopyする

却下。provider-first authorityを壊し、S90 docsやfull template inventoryの同期漏れを起こしやすい。

### E. Issue #344 で opt-in full regression と candidate-wheel consumer E2E まで行う

却下。PR workflowが要求しておらず、Issue #346 の integrated distribution scopeを先取りする。

### F. Parent Epic planを変更せず、user instructionを一時overrideとして扱う

却下。parent planがper-Issue PRを明示的に禁止しているため、canonical contradictionとstale review evidenceが残る。

### G. `iss-00345 -> iss-00344` dependency を追加する

却下。Candidate1/2の機能依存はなく、必要なのはbranch admission ruleである。

### H. Issue #344 PR open中に同branchへIssue #345を追加する

却下。Issue #344 PRがsibling implementationを吸収し、今回の目的に反する。

### I. Current branch historyをrewriteし、Issue #344 commitsだけをcherry-pickする

原則却下。Epic planning baselineとIssue node metadataが前提であり、history surgeryは最小修正ではない。final reviewerが本当に無関係な実装混入を確認した場合だけ別判断とする。

---

## 11. Assumptions, uncertainty, and unverified claims

* 本分析は GitHub connector で source/docs/tests を読んだもので、ローカル command を独立実行していない。
* `670 passed, 2042 skipped, 2 failed` は canonical report の観測結果であり、本分析内で再実行した結果ではない。
* S90 実装後の exact provider diff はまだ存在しないため、S95 の final dogfood allowlist は S90 closure SHA の実差分から確定する必要がある。
* Branch protection、required review、conversation resolution の最終状態は、PR作成後の actual platform observation が必要である。
* 現時点では PR-triggered workflow run がないため、CI passは未観測である。
* Issue #346 local requirement/design/plan はまだ具体化済み sourceではない。親 Epic plan amendment後に fresh planningが必要である。
* 本文は advisory evidence であり、canonical docsのamendment、review、approval、PR creation、merge preparationを完了したとは主張しない。

---

## 12. Final `spec-reviewer` checklist

### Source and amendment identity

* [ ] Repository は `chemitaro/spec-dock`。
* [ ] Branch は `iss-00344-workbench-shell-scaffolding`。
* [ ] Amendment source base は `cc17c25530f8778b52b006b878c780dafeccf57f` または、その正当な後継SHA。
* [ ] `main` との ancestry を amendment review時に再確認した。
* [ ] Issue requirement/design/plan と parent Epic plan を同じ amendment boundaryで確認した。

### Scope discipline

* [ ] Issue #344 は Workbench shell scopeのまま。
* [ ] Generic single-file Artifact importを追加していない。
* [ ] `workbench copy` production semanticsを変更していない。
* [ ] Candidate-wheel consumer E2EをIssue #344へ移していない。
* [ ] Opt-in full regressionをIssue #344 closureへ移していない。
* [ ] Epic-wide review/closureをIssue #344で主張していない。
* [ ] Dogfood projectionはIssue #344 changed provider assetsに限定されている。
* [ ] Existing root/node Workbenchをbackfillしていない。
* [ ] `spec-dock/initiatives/**` をprojection operationで変更していない。

### Canonical consistency

* [ ] Requirementのdogfood/PR全面禁止がnarrow exceptionへ変更されている。
* [ ] Designにprovider-first projection boundaryが追加されている。
* [ ] Plan tagがper-Issue PR ownershipを表す。
* [ ] Issue PR ownerとEpic integration PR ownerが区別されている。
* [ ] Parent Epic planの「Candidate1/2はPRなし」がIssue #344 exceptionへ変更されている。
* [ ] Issue #346 のintegrated responsibilitiesが失われていない。
* [ ] Dependency metadataを変更しない理由が記録されている。
* [ ] Historical S01 review evidenceを改ざんせず、superseding decisionを追加している。

### Step and closure quality

* [ ] S95がS90後、S99前に置かれている。
* [ ] S95 allowed/forbidden pathsがexact。
* [ ] `TC-344-011` または同等のprojection closureがある。
* [ ] Projection diff inventoryがevidenceとして残る。
* [ ] Required-fast parity testsをskip/reclassifyしていない。
* [ ] Default `uv run pytest` がzero failure。
* [ ] `make lint` がpass。
* [ ] validate/sync/diff-check/clean checkがpass。
* [ ] S95にfresh code reviewがある。
* [ ] S99にfresh QA/code/spec reviewがある。

### PR delivery and observation

* [ ] PR baseは`main`。
* [ ] PR headはIssue #344 branch。
* [ ] PR is open and ready。
* [ ] PR bodyに`Closes #344`と`Refs #343`がある。
* [ ] Issue #345/#346をcloseしていない。
* [ ] Observed head SHAがlatest pushed SHAと一致する。
* [ ] `Provider CI / provider-tests` が成功している。
* [ ] Current-head review completionが観測されている。
* [ ] Unresolved P0/P1がない。
* [ ] Changes-requested reviewがない。
* [ ] Blocking unresolved threadがない。
* [ ] Visible merge conflictがない。
* [ ] Required checks/reviews/conversation-resolutionが確認されている。
* [ ] Platform要件未確認時に`github-mergeable`を主張していない。
* [ ] Push後は毎回new SHAでre-observeしている。
* [ ] BranchへIssue #345/#346 implementationを追加していない。
* [ ] merge、auto-merge、branch deletion、Issue finishを行っていない。

### Final promotion decision

* [ ] 以上がすべて満たされるまでは amendment または PR readiness を `PASS` にしない。
* [ ] Canonical amendmentへのfresh `spec-reviewer` PASS後だけS02以降を再開する。
* [ ] PR delivery完了後はhuman merge前で停止する。
