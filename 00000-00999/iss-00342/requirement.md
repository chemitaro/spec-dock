---
種別: 要件定義書（Issue）
ID: "iss-00342"
タイトル: "Reduce Unit Test And Provider CI Runtime"
関連GitHub: ["#342"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-28"
親: ["epic-00080", "init-00079"]
---

# iss-00342 Reduce Unit Test And Provider CI Runtime — Issue 要件定義

## 0. 文書の位置づけ

この文書は、通常開発とPull Request（PR）のクリティカルパスから長時間の完全回帰を分離しつつ、完全なテスト集合を明示手動実行と`main`更新後の事後検知に残すための成果、制約、受け入れ条件を定義する。

実装方式、pytest selector、GitHub Actionsのjob構造、変更ファイル、TDD順序は`design.md`と`plan.md`で定義する。

## 1. 概要

### 1.1 目的

- 通常開発で使う既定テストとPRのmerge gateを、30〜40分かかる完全回帰から切り離す。
- 長時間テストを削除せず、開発者が意図的に実行できる完全回帰と、`main`へのmerge後に実行される完全回帰として保持する。
- 速度改善を理由に、provider / dogfooding parityや代表的CLI contractをmerge前検証から消失させない。

### 1.2 観測可能な成果

- 通常開発の既定テストは高速レーンだけを実行し、完全回帰に分類された長時間テストを実行しない。
- PRでは既存の`provider-tests` check identityを維持した高速レーンだけがmerge blockerになる。
- 完全回帰は明示的なローカル手動コマンドとGitHubの手動実行から起動できる。
- `main`へのpushでは、既に完了したmergeを遡ってblockしない独立した完全回帰が起動する。
- schedule / cron triggerは存在しない。
- 高速レーンと完全回帰の集合関係、event routing、代表的contract、性能値が自動テストまたは再現可能な証跡で確認できる。

### 1.3 このIssueの種類

- [x] 既存振る舞いの変更
- [x] 既存振る舞いの不具合修正
- [x] CLI / script 挙動変更
- [x] workflow / skill / agent導線の変更
- [x] 仕様・文書の明確化
- [ ] 新機能追加
- [ ] migration / compatibility を伴うproduct data変更

## 2. 背景・現状

### 2.1 現在の状態

- full collectionは2,696 testsである。
- `tests/unit`は1,209 testsで、観測実行は`1 failed, 1207 passed, 1 skipped in 380.19s`だった。
- `tests/unit/infra/test_init_update.py`を除くunit実行は`655 passed, 1 skipped in 5.45s`であり、unit elapsedの約98%が同ファイルに集中している。
- `tests/cli_runtime`は`1194 passed, 75 skipped in 1228.31s`で、約20分28秒を要した。
- Provider CIの成功runではpytest stepが2,249.64秒、全jobは約37〜38分を要した。
- 直近100件のProvider CIは中央値38.1分、最大40.9分で、同一SHAの`push`と`pull_request`が重複完走したgroupも確認された。
- `.github/workflows/provider-ci.yml`は`push`と`pull_request`の双方で、単一の`provider-tests` jobから`uv run pytest`を実行する。
- deployment / CD workflowは確認されていないため、このIssueでいうCI/CD問題の対象はProvider CIとローカルテストである。

### 2.2 現在の問題

- 小さな変更でも、通常開発またはPR feedbackのために完全回帰の終了を待つ必要がある。
- 長時間テストがmerge blockerであるため、検証の完全性と開発速度を同一のクリティカルパスでしか扱えない。
- `push`と`pull_request`の両方が同一SHAの完全回帰を起動し、待ち時間とcomputeを重複させ得る。
- 現行の一括コマンドでは「毎回必要な高速検証」と「意図的または事後に行う完全回帰」の契約が明示されていない。

### 2.3 根拠・情報源

- 上位要件:
  - `init-00079/requirement.md`
  - `epic-00080/requirement.md`
- 既存方針:
  - `iss-00160-reduce-test-runtime-followup/discussions/20260605t075347z-01-adr-test-suite-boundary-and-fixture-strategy.md`
  - `iss-00167-migrate-tests-to-pytest/requirement.md`
  - `iss-00167-migrate-tests-to-pytest/report.md`
- Issue-local evidence:
  - `artifacts/20260728t015759z-research-unit-test-and-provider-ci-runtime-investigation.md`
  - `artifacts/20260728t015759z-01-interview-full-regression-merge-gate-policy.md`
  - `artifacts/20260728t025412z-adr-separate-fast-merge-gate-and-full-regression-execution.md`
- ChatGPT-first evidence:
  - `oracle:iss00342-test-ci-planning`
  - ZIP SHA-256: `f300cbff69ce241e85462fd5a37fcf2ff7beacad77d8b1d40c133749783e1e01`
  - pack review / stage: pass、authority=`evidence_only`、adoption=`partially_adopted`
- 現行実装:
  - `.github/workflows/provider-ci.yml`
  - `pyproject.toml`
  - `Makefile`
  - `README.md`
  - `tests/cli_runtime/harness.py`
  - `tests/unit/infra/test_init_update.py`

## 3. 親スコープと継承条件

### 3.1 親Initiative

- Initiative ID: `init-00079`
- 継承する制約:
  - repo内で再現・検証可能なprovider-local問題に閉じる。
  - external consumer固有のpipeline変更を含めない。
  - provider-side source of truthとdogfooding mirrorの関係を崩さない。

### 3.2 親Epic

- Epic ID: `epic-00080`
- 対応する要件:
  - `E-RQ-001`: repo-local actionable bug
  - `E-RQ-002`: single actionable bugまたはtightly coupled contract bug
  - `E-RQ-004`: requirement / design / planとresearch evidenceを持つ
- このIssueは、ローカル既定テストとProvider CIの長時間化を同じtest-lane policyの問題として扱う。

### 3.3 再定義してはいけないもの

- local subprocess、filesystem、tempdir、local git、stub `gh`を外部integrationへ再分類しない。
- 遅いテストを`tests/integration`へ移すだけの見かけ上の高速化を行わない。
- CLI subprocess coverageは高シグナルなcontract smokeに限定し、business logicは適切なlower layerで検証する既存方針を維持する。
- 実GitHub、remote git、network、authをroutine local laneへ持ち込まない。
- product runtime behaviorをテスト性能のために変更しない。

## 4. 関係者・Trigger・代表シナリオ

### 4.1 主な関係者

| Actor | 役割 | このIssueとの関係 |
|---|---|---|
| contributor | 通常開発とPR作成 | 高速な既定feedbackを利用する |
| maintainer | merge判断とpost-merge障害対応 | fast checkをmerge gateにし、full failureを事後対応する |
| GitHub Actions | Provider CI実行 | eventに応じてfastまたはfullを起動する |
| test maintainer | lane分類とcontract保守 | 全集合の欠落、smoke、性能を維持する |

### 4.2 Trigger

- ローカル既定テストコマンド
- 明示的なローカル完全回帰コマンド
- GitHub `pull_request`
- `main` branchへの`push`
- GitHub `workflow_dispatch`

`schedule` / `cron`はtriggerに含めない。

### 4.3 代表シナリオ

#### SC-001: 通常開発

- Given: contributorがローカルで通常のテストを行う。
- When: bare/default pytest commandまたはdocumented fast commandを実行する。
- Then: fast laneのみを実行し、full-regression分類の長時間テストは実行しない。

#### SC-002: PR merge gate

- Given: PRが作成または更新される。
- When: Provider CIが`pull_request`で起動する。
- Then: lint、fast tests、代表的provider / dogfooding parityとCLI smokeを実行し、完全回帰は起動しない。

#### SC-003: 意図的な完全回帰

- Given: contributorまたはmaintainerが完全回帰を必要とする。
- When: documented local full commandまたは`workflow_dispatch`を実行する。
- Then:fast laneを含む論理的な全テスト集合を実行する。

#### SC-004: `main` merge後の事後検知

- Given: PRが`main`へmergeされ、`main` push eventが発生する。
- When: post-merge full regression workflowが起動する。
- Then: 完全回帰をバックグラウンドで実行し、結果をmerge後の事後検知として可視化する。

#### SC-005: post-merge full failure

- Given: `main`の完全回帰が失敗する。
- When: maintainerがGitHub Actions結果を確認する。
- Then: failing SHA、test、log、再実行コマンドを特定できる。
- And: 既に行われたmergeを遡ってblockしたとは扱わない。

## 5. スコープ

### 5.1 対象範囲

- fast default laneとfull regression laneの明示的なtest contract。
- bare/default pytest pathをfastにする設定または同等の仕組み。
- 明示ローカルfull commandとGitHub manual full trigger。
- PRではfastのみ、`main` pushではfullのみを保証するProvider CI event routing。
- 既存`provider-tests` check identityの維持。
- heavy test集合、fast test集合、full test集合の機械的な完全性検証。
- fast laneに残す代表的CLI contractとprovider / dogfooding parity obligation。
- workflow routing、selector、collection、performance、failure visibilityの回帰テスト。
- README、AGENTS、Makefile、pytest configuration、workflowのコマンド契約整合。

### 5.2 対象外

- schedule / cronによる定期実行。
- 長時間テスト自体の全面的な高速化。
- pytest-xdist、動的sharding、remote cache、恒久metrics serviceの導入。
- test taxonomy全体の再編またはintegrationへの単純移動。
- release / deployment automation。
- external consumer repositoryのpipeline変更。
- branch protection設定をcredentialed APIで直接変更する作業。
- full regression failureからGitHub Issueを自動起票する仕組み。

### 5.3 変更してはいけないもの

- 完全回帰で実行可能な既存test obligationを説明なく削除しない。
- broad skip / xfail、assertion弱体化、test deletionで性能条件を満たさない。
- full laneにlive external accessを新たに導入しない。
- `main` merge後のfull failureをPR merge失敗として扱わない。
- schedule非採用というaccepted policyを実装都合で変更しない。

### 5.4 判断境界

| 項目 | 扱い | 根拠 |
|---|---|---|
| fast/full分離 | 含める | accepted ADR |
| `main` post-merge full | 含める | user-approved |
| manual local / GitHub full | 含める | user-approved |
| schedule / cron | 除外 | user-approved |
| exact heavy/smoke node inventory | design / implementationで確定 | durationとcontract evidenceが必要 |
| required check名 | `provider-tests`維持を既定 | branch protection APIは403で未観測 |
| full suite内部最適化 | 必須条件に必要な場合だけ | lane分離が主要目的 |

## 6. 要求される振る舞い

### BH-001: 既定はfast

- Given: 明示的なfull opt-inがない。
- When: contributorまたはCIが既定テストcommandを実行する。
- Then: full-regression分類の長時間testを実行しない。
- And: fast test failureは通常どおりnonzeroで終了する。

### BH-002: fullは明示opt-in

- Given: documented full commandまたはfull workflow triggerが選択される。
- When: test collectionを行う。
- Then: fastとheavyを含む論理的な全test集合を選択する。
- And: default selectorによるheavy除外を確実に解除する。

### BH-003: PRはfastのみ

- Given: GitHub eventが`pull_request`である。
- When: Provider CIが起動する。
- Then: `provider-tests`はfast contractを実行する。
- And: full regression jobは起動しない。

### BH-004: `main` pushはpost-merge full

- Given: GitHub eventが`push`でrefが`refs/heads/main`である。
- When: Provider CIまたは独立full workflowが起動する。
- Then: full regressionを実行する。
- And: PR required checkとしてmerge前に待機させない。

### BH-005: manual full

- Given: maintainerが`workflow_dispatch`またはdocumented local full commandを選ぶ。
- When: 実行する。
- Then: `main` pushと同じfull regression contractを実行する。

### BH-006: scheduleを持たない

- Given: workflow定義を検査する。
- When: Provider test workflowのtriggerを列挙する。
- Then: `schedule` / cron entryは存在しない。

### BH-007: full failureを可視化する

- Given: post-merge full regressionが失敗する。
- When: run resultを確認する。
- Then: failing SHA、failed test、job log、手動再実行経路を確認できる。
- And: failureはactionableなpost-merge signalとして残る。

## 7. 受け入れ条件

### AC-001: default test pathは長時間testを実行しない

- bare/default pytest command、`tests/unit`の通常command、documented fast commandのいずれでも、full-regression分類されたtest itemの実行数が0である。
- selectorの誤りでfull-regression testが実行された場合は回帰テストが失敗する。

### AC-002: manual fullは全集合を実行する

- `make test-provider-full`またはdesignで定める同等のstable commandが存在する。
- full commandのcollected item ID集合は、fast集合とheavy集合のunionに一致する。
- fast集合とheavy集合のintersectionは空である。
- selector対象外となるtest itemが0である。

### AC-003: PR routing

- `pull_request`では`provider-tests`がfast commandを実行する。
- PRではfull commandまたはfull jobを実行しない。
- `provider-tests`のworkflow/job check identityを維持し、required checkが意図せず消失しない。

### AC-004: `main` post-merge routing

- `main`へのpushでfull commandが1回起動する。
- 同じeventでPR用full regressionを重複実行しない。
- full resultはGitHub Actions上でSHA、status、duration、test summaryを確認できる。

### AC-005: manual routingとschedule非採用

- `workflow_dispatch`からfull commandを起動できる。
- workflow YAMLに`schedule` triggerがない。
- local full commandがREADMEまたは同等のcontributor-facing docsに記載される。

### AC-006: merge前の最低contract

- fast laneはlintと短時間testsだけでなく、少なくとも次を検証する:
  - provider / installed dogfooding parityの代表例
  - CLI bootstrap / entrypoint
  - success時のexit codeと代表output
  - failure時のexit codeと代表error output
  - provider-side source of truthからconsumer-side artifactへ反映される代表contract
- exact node inventoryと選定理由をmachine-readableまたはreview可能な形で固定する。

### AC-007: coverage weakeningを行わない

- before / afterのfull collection item ID差分を記録する。
- test削除、skip / xfail増加、assertion削除がある場合は個別に理由とreplacement evidenceを持つ。
- 性能達成だけを理由にしたunexplained deltaは0件である。

### AC-008: 性能

- 同一checkout・Python・cache条件でlocal fastとlocal fullを3組実行し、各組でfast elapsedがfull elapsedより短い。
- local fastではfull-regression分類されたtest itemの実行数が0であり、短縮が単なる計測揺れではなくlane分離によることをitem IDとdurationで示す。
- PRの`provider-tests` jobは、queue timeを除くstarted-to-completed elapsedを3回記録し、各runが変更前のProvider CI中央値38.1分より短い。
- full regressionにはPR latency thresholdを課さない。実測durationをreportへ記録し、merge blockerでないことを成功条件とする。
- 性能計測のtest count、skip count、SHA、Python version、cache条件を併記する。
- local fast 120秒以内とPR fast 10分以内はdesign / implementationで評価する非blocking targetであり、owner承認済みhard thresholdまたはp95とは扱わない。

### AC-009: event routing regression test

次のtruth tableを自動テストまたは同等のdeterministic inspectionで固定する。

| Event | Fast merge gate | Full regression |
|---|---:|---:|
| `pull_request` | yes | no |
| non-`main` `push` | no | no |
| `main` `push` | no | yes |
| `workflow_dispatch` | no | yes |
| `schedule` | no | no |

full regressionはfast test集合を内包するため、`main` pushと`workflow_dispatch`で別のfast jobを重複実行しない。

### AC-010: post-merge failure operation

- full jobの名称、確認場所、local再実行command、failure ownerをdocsに記載する。
- post-merge failureはvisibleなfailed runとして残り、原因修正またはrerunまで追跡できる。
- 自動rollback、自動Issue作成、既存mergeの遡及blockは要求しない。

### AC-011: rollback

- fast selector漏れ、required check欠落、許容不能なescapeが確認された場合、PR jobをfull regressionへ戻せる。
- rollback後もmanual full commandと計測証跡を削除しない。
- rollback手順をdesignとdocsに記載する。

## 8. 例外・エッジケース

- heavy markerまたは同等selectorが0件になった場合は、成功扱いせず分類contract failureとする。
- full commandがdefault除外設定を引き継ぎ、heavy testを実行しない場合は失敗とする。
- 新規testがfast/heavyのどちらにも分類されない場合は、collection completeness guardで失敗する。
- representative smokeが遅くなった場合、無言で外さず、代替contract evidenceと選定理由をreviewする。
- `main`への連続pushでfull runをcancelする場合、最新SHAに対するfull runが必ず1件残る。
- fork PRでもrequired fast checkが欠落しないことをworkflow contractで確認する。
- branch protectionの現物を取得できない場合、既存`provider-tests` identityを変更しない。
- flaky testはlane変更だけで隠さず、full failureとして可視化し、必要なら別Issueへ切り出す。

## 9. 外部コマンド契約

最低限、次の利用者向けcontractを提供する。正確なflagやmarker名はdesignで定める。

| 用途 | 必須entrypoint | 意味 |
|---|---|---|
| 通常開発 | bare/default pytest path | fast lane |
| 明示fast | `make test-provider-fast`または同等 | CIと同じfast contract |
| 明示full | `make test-provider-full`または同等 | 全test集合 |
| GitHub manual | `workflow_dispatch` | local fullと同じfull contract |

command名、README、workflowの実行内容が乖離してはならない。

## 10. 非機能要求

### 10.1 互換性

- Python 3.10+方針を維持し、Provider CIのPython 3.11を別判断なしに変更しない。
- test directory layoutとpublic test IDsを不必要に変更しない。
- `provider-tests` check identityを維持する。

### 10.2 可観測性

- fast/fullのrun name、SHA、event、duration、counts、failureをGitHub Actionsまたはreportで確認できる。
- selector completenessとsmoke inventoryをlocal commandで再現できる。

### 10.3 性能

- performance authorityはAC-008とする。
- full regression自体の30〜40分を本Issueだけで短縮することは必須ではない。
- 主要成果はPRと通常開発のcritical path短縮である。

### 10.4 セキュリティ・隔離

- workflow permissionsを拡張しない。
- test実行にsecretやlive external credentialを追加しない。
- mutable repository / temp targetをtest間で共有して高速化しない。

## 11. 制約

### CON-001: accepted policy

`artifacts/20260728t025412z-adr-separate-fast-merge-gate-and-full-regression-execution.md`をtest-lane policyのauthorityとする。

### CON-002: source of truth

workflowやshipped test contractを変更する場合、provider-side source of truthを先に変更し、dogfooding側は検証対象として扱う。

### CON-003: no schedule

schedule / cronの導入はscope expansionであり、このIssueでは禁止する。

### CON-004: no silent weakening

速度改善はtest deletion、broad skip / xfail、assertion弱体化、integrationへの単純移動で達成してはならない。

## 12. 依存関係

- 実装前提:
  - accepted ADRとanswered interview
  - requirement / design / planのfresh `spec-reviewer` pass
  - authorized profile `standard`のassurance classification / composed Standard templates
  - test omission / workflow routingは`strict`相当のreview focusとして扱うが、authoring profile自体を`strict`へ変更しない
- 外部依存:
  - GitHub Actions
  - branch protectionはread-only確認できれば利用するが、取得不能でもjob identity維持で進める
- blocker:
  - 現時点でowner判断の未回答事項なし

## 13. Grade判定材料

### 13.1 推奨Grade

- assurance authorized profile: `standard`
- pre-classification review focus: `strict`相当のtest omission / workflow routing確認

### 13.2 理由

- product data、migration、security / privacy、external credential、不可逆変更を伴わず、既存PR full gateへ戻せるため`standard`とする。
- 一方でmerge protectionとpost-merge detection policyを変更し、pytest selector、workflow event routing、Makefile、docs、test inventoryが連動する。
- selector漏れは検証義務を静かに弱め得るため、Standardのspecialist evidence、fresh spec review、collection completeness、rollbackを省略しない。
- branch protection現物が403で未観測であり、compatibilityをjob identityで保守的に扱う。

### 13.3 Risk facts

- external communication: なし
- persistent product data mutation: なし
- irreversible migration: なし
- security / privacy change: なし
- operational policy change: あり
- rollback path: あり
- test omission risk: 高

### 13.4 Grade引き上げ条件

- workflow permission拡張、credentialed branch protection変更、release gate変更、external consumer workflow変更が必要になった場合はscopeを再確認する。

## 14. Designへの引き渡し

designで必ず定める:

- fast/heavy/fullの集合モデルとselector contract
- bare/default pytestをfastにし、full opt-inで除外を確実に解除する方式
- representative CLI / parity smokeの選定規則と初期inventory
- Provider CIのworkflow/job構造とevent truth table
- `provider-tests` check identityの維持方法
- main pushのfull concurrencyとlatest-SHA保証
- post-merge failure visibility、owner、rerun、rollback
- collection completeness、skip delta、workflow routing、性能の検証方式

## 15. Planへの引き渡し

planで分解する:

1. baselineとtest item集合の固定
2. selector / markerのRed test
3. fast/full local command contract
4. representative smoke inventory
5. workflow event routingのRed test
6. PR fastと`main` / manual fullの実装
7. docs整合
8. focused / fast / full / workflow / performance verification
9. rollback確認とfresh reviews

各stepはAC / edge caseとclosure IDで対応付ける。

## 16. docs / artifacts影響

- 更新対象:
  - `README.md`
  - `AGENTS.md`のtest command記述（必要な場合）
  - `.github/workflows/provider-ci.yml`または独立full workflow
  - `Makefile`
  - `pyproject.toml`
  - test lane inventoryまたは同等の保守文書
- Issue-local evidence:
  - research
  - answered interview
  - accepted ADR
  - ChatGPT ZIP review/stage evidence
  - `report.md`のEAL、authoring gate、実装証跡

## 17. 用語

- **fast default lane**: PR merge gateと通常開発の既定経路で実行する短時間の検証集合。
- **full regression lane**: fastとheavyを含む論理的な全test集合。
- **heavy / full-regression test**: defaultでは実行せず、明示fullまたは`main` post-mergeで実行する長時間test。
- **post-merge detection**: merge完了後の`main` SHAに対するfull resultで回帰を検出すること。
- **check identity**: branch protectionが参照し得るworkflow / job由来のstatus名。

## 18. 未確定事項

- owner判断が必要な未確定事項: なし。
- designでsource-groundedに確定する事項:
  - exact selector mechanism
  - initial heavy item inventory
  - initial representative smoke item inventory
  - workflowを単一fileで分けるか複数fileに分けるか

これらはaccepted policyを変更せず、performanceとcompatibilityを満たす最小設計を選ぶ。

## 19. 要件承認チェック

- [x] 問題、目的、actor、triggerを定義した
- [x] scope / non-scope / must-not-changeを定義した
- [x] fast / manual full / main post-merge / no scheduleを定義した
- [x] measurable acceptance criteriaを定義した
- [x] full collection completenessとcoverage weakening guardを定義した
- [x] parent scopeと既存ADRをtraceした
- [x] ChatGPT evidenceの採否を`report.md`に記録した
- [x] fresh `spec-reviewer` passを取得した
- [x] assurance classification / composeを完了した

## 20. 変更履歴

| 日付 | 変更 | 根拠 |
|---|---|---|
| 2026-07-28 | 初版 | local investigation、user interview、accepted ADR、ChatGPT-first evidence reconciliation |
