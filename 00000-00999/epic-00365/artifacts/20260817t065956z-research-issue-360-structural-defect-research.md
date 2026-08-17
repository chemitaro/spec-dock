---
種別: research
ID: "20260817t065956z-research"
タイトル: "Issue 360 Structural Defect Research"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-08-17"
親: ["epic-00365"]
template: "research"
authority: "evidence"
derived_from:
  - "iss-00360 requirement/design/plan/report and s95-full-regression-ledger.json"
  - "current provider source, dogfood projection, tests, CLI help, and Git history"
reflected_to: []
---

# 20260817t065956z-research Issue 360 Structural Defect Research

## Question

- Issue 360の実装と最終品質ゲートで発見された未解決問題は、既存のSpecDock構造欠陥と品質ゲート運用の欠陥のどちらに属するか。
- Issue 360を閉じるために直ちに修正する範囲と、Epic 00365で調査・再設計する範囲をどう分離するか。

## Source

- 調査対象は、同一repository内のIssue 360 evidence corpusとした。確認日は2026-08-17。
- Canonical / historical evidence:
  - `iss-00359`のRequirement、Design、Plan、Report
  - `iss-00360`のRequirement、Design、Plan、Report
  - `iss-00360/artifacts/s95-full-regression-ledger.json`
  - Initiative `init-local-00003`のRequirement、Design、Plan
- Provider / dogfood / runtime:
  - `src/spec_dock/cli.py`
  - `src/spec_dock/managed_distribution.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`
- Tests and command contracts:
  - `tests/cli_runtime/test_distribution_cutover.py`
  - `tests/unit/infra/test_init_update.py`
  - Current root / group / leaf `./spec-dock/scripts/spec-dock ... --help`
- このArtifactは上記を一つのIssue 360 evidence corpusとして読むsource-grounded investigationである。複数案の正式な採否比較は後続`disc`またはADRで扱う。

## Findings

### 1. 結論

Issue 360では、実在する重大な欠陥が多数検出・修正された。一方、終盤のレビュー非収束には、広大な状態機械を毎回再探索したこと、既存full-regression failureをIssue 360のmerge blockerと混同したこと、仕様上正しい回復動作をP1と誤判定したことも含まれる。

したがって、Epic 00365へ引き継ぐ問題は次の二群である。

1. Issue 360以前から存在するruntime / test architectureの構造欠陥
2. final-quality campaignの収束制御とevidence更新の欠陥

Issue 360を無期限に拡張して両群を全面改修するのはscope誤りである。Issue 360のchanged surfaceを閉じ、既存構造と品質ゲート運用の恒久対策をEpic 00365へ移すのが妥当である。

### 2. Distribution / installerの構造的複雑性

確認できた事実:

- `src/spec_dock/cli.py`は4,945行、top-level class / functionは147件である。
- `src/spec_dock/managed_distribution.py`は3,220行、top-level class / functionは95件である。
- distribution cut-overの主要test二本は、`test_distribution_cutover.py`が2,902行、`test_init_update.py`が今回の追記前でも8,000行を超える。
- runtime側は86個のPython moduleへ層分割されている一方、installer / distribution側は二つの巨大moduleへ、admission、inventory、ownership、plan、apply、retry marker、rollback / forward recovery、uninstall、diagnostic、CLI orchestrationが集中している。
- Issue 360 Reportには`Latest P1 repair candidate`が32段階記録されている。これは32件すべてが独立したproduction defectだったことを意味しないが、同一状態機械の別surfaceを後続reviewで発見し続けた事実を示す。
- `init`、`update`、`init --force`、`uninstall`が、fresh / recognized / retry / uninstall-retry、managed / user-owned / unknown、missing / identical / modified、symlink / hard-link / root-rebindを横断する。

評価:

- 局所修正の不足だけではない。多数のfilesystem identity helperとphase固有分岐を同じmodule群で組み合わせる構造が、レビュー範囲の把握、failure atomicityの証明、変更影響の限定を難しくしている。
- descriptor-bound / no-follow / identity-pinned mutationは必要であり、単純な`shutil`処理へ戻すべきではない。問題は安全性の強度ではなく、安全primitive・transaction state・product policy・CLI orchestrationの責務境界が浅いことである。

### 3. 実在した重大欠陥とレビューの価値

Issue 360のreview / repair historyで確認できる主要な真陽性は次である。

- Fresh initのapply markerとforward recovery不足
- preflight後のpath / root rebind、symlink / hard-link、directory walk不完全性に対するmutation直前再検証不足
- managed scaffold recursive copy / chmod / cleanupのpathname依存
- update / uninstall retry marker publication・identity・cleanupのfailure atomicity不足
- keep-specs / remove-specs / reinit境界、mode mismatch、same-bytes ownershipの契約不足
- obsolete legacy tests / assetsが物理退役後も残る問題
- full-regression failure比較がsetup / teardown / wrong checkoutを見逃し得るledger verifier問題

これらはreviewが過剰だったために作られた問題ではなく、実装とテストで再現・修正された欠陥である。前半のreview campaignは、重大欠陥を実際に炙り出した点で有効だった。

### 4. Review非収束と偽陽性

確認できた事実:

- 終盤のbounded reviewは、missing non-anchor scaffold directoryをrecognized update / `init --force`が回復できないというP1を報告した。
- 実装とfocused reproductionでは、`docs/templates/system`のようなnon-anchor directoryは回復し、runtime anchor欠損だけが設計どおりzero-write blockすることを確認した。
- この区別を固定する二つの回帰testが追加され、passしている。
- 同じreviewの`_assert_managed_path_identity`が`ctime_ns`を比較しないという指摘は、現行sourceでも確認できる。ただし当時の利用者policyではP2であり、Issue 360のclosure blockerではない。安全primitive統一時の調査候補としてEpic 00365へ移す。

評価:

- reviewのcoverage拡大は必要だったが、新規reviewerが毎回全体を再探索するとfinding identityと既決事項が安定せず、収束が遅くなる。
- 同一campaign session、stable finding ID、root-cause group、reviewed / unreviewed surface ledger、completion sweepを維持する必要がある。
- model findingはadvisoryであり、P0 / P1であっても、specと最小再現に反する場合はhuman adjudicationでrejectできなければならない。

### 5. Full regression baseline

確認できた事実:

- canonical S95 ledgerは26件のcall-phase failureを記録している。
- failureはdelete 1件、import / import application 9件、active / context-pack 11件、sync 2件、shell 1件、Workbench 1件など、Issue 360のdistribution changed surface外へ分布する。
- ledgerは固定点でも同じ26 node IDが失敗するため`approved-no-op`と分類し、Issue 360起因のcurrent-only failureは0件としている。
- これはIssue 360の差分回帰がない証拠にはなるが、repository全体がgreenである証拠にはならない。
- ledgerの`current_head_sha`とReportの最新証拠は現行branch tipより古く、evidence refreshの手作業負荷とdriftも残る。

評価:

- Issue 360のmerge / close判定と、SpecDock repository全体のzero-failure baseline回復を分離する必要がある。
- 26件を永久に`approved-no-op`として固定してはならない。Epic 00365で再現、root cause、owner、expected behaviorを確定し、削除・期待値更新・実装修正のいずれかで0件へ収束させる。
- PR fast gateとpost-merge full regressionの分離自体は時間効率上合理的だが、post-merge failureを次のmerge判断へ確実に戻す運用証拠が必要である。

### 6. Issue 360を閉じる条件とEpic 00365へ移す条件

Issue 360で閉じる対象:

- distribution cut-overのRequirement / Designで定義されたfresh / update / force / uninstall / migration contract
- focused distribution / archive integration / fast laneの成功
- Issue 360 changed surfaceにcurrent-only full-regression failureがないこと
- 終盤の偽P1を回帰testで棄却したhuman adjudication

Epic 00365へ移す対象:

- installer / distributionのdeep-module化とtransaction state machine再設計
- filesystem identity primitiveの単一化と`ctime_ns`を含む契約再評価
- 26件の既存full-regression failureのzero-baseline recovery
- active / import / sync / delete / Workbenchのfixture、contract、read modelの統合
- evidence ledgerの自動生成・current SHA binding・staleness検出
- final-quality campaignのstable finding / session reuse / human adjudication / stop budget

### 7. 推奨するIssue分割候補

1. Baseline characterization:
   - 26 failureを独立再現し、expected behavior、共通fixture、root cause group、ownerを確定する。
2. Distribution transaction boundary:
   - admission、ownership inventory、plan、apply、recovery、diagnosticを明示的なstate transitionへ分離する。
3. Descriptor-bound filesystem kernel:
   - no-follow open、identity snapshot、atomic publish、recursive copy / removeを単一deep moduleへ集約する。
4. Runtime read-model and fixture consolidation:
   - active / import / sync / delete / Workbenchが共有するrepository / GitHub viewを整理する。
5. Zero-failure regression recovery:
   - baseline 26件を順に解消し、full regressionを0 failureへ戻す。
6. Evidence and quality-gate convergence:
   - exact SHA evidence生成、staleness検出、stable finding ID、session reuse、bounded human escalationを統合する。

### 8. 非対象

- filesystem安全性を弱めるためのpathname-based shortcut
- Issue 360内での全面リアーキテクティング
- P2 / P3をIssue 360 closure blockerへ格上げすること
- PR mergeの自動化

## Reflection

- このArtifactはevidenceであり、Epic 00365の正式scope、受け入れ条件、Issue順序をまだ決定しない。
- Epic 00365を具体化するときは、上記Issue候補をそのまま採用せず、最初のbaseline characterizationでroot cause groupとdependency順を確定する。
- Issue 360のclosureでは、「repository全体がgreen」と主張せず、「Issue 360 changed surfaceに新規failureがなく、既存26件をEpic 00365へ明示移管した」と記録する。
