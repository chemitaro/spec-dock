---
種別: 要件定義書（Issue）
ID: "iss-00372"
タイトル: "Distribution Hard Cutover And Parity"
関連GitHub: ["#372"]
状態: "planned"
最終更新: "2026-08-30"
親: ["epic-00365", "init-local-00003"]
---

# iss-00372 Distribution Hard Cutover And Parity — 要件定義

詳細: [Requirement Guide](../../../../../../docs/authoring/requirement.md)

## 目的

Issue `iss-00368`〜`iss-00371` で受理・実装された distribution contract を変更せず、D5 final cutover owner として、現在の production distribution path が一つの managed distribution authority に収束していること、残存する dead legacy execution seam が再到達不能ではなく物理的にも除去されていること、provider source・checked-in dogfooding・wheel・sdist・installed package・fresh consumer・Linux・macOS が同じ candidate SHA の contract を満たすことを確定する。

本 Issue の完了は、新しい distribution semantics の設計ではない。D1〜D4 の accepted product semantics、public CLI/JSON compatibility、data-preservation boundary、forward-only recovery authority を保持したまま、integration、absence、package、platform、test、documentation の最終 parity evidence を完成させることである。

## 現在の前提

実装前 baseline は commit `e8b885fcb98e63e6c2e5f32245f8d65345157d1f` である。この baseline では、fresh/recognized/deprovision/purge の public mutation は `src/spec_dock/managed_distribution.py` の typed service boundary へ到達している。一方、`src/spec_dock/cli.py` には current public route から参照されない旧 managed-file writer helper と、その helper のための private filesystem-kernel import/test seam が残存している。また provider PR CI は Ubuntu のみで、macOS の required distribution parity evidence は workflow に固定されていない。

この baseline 記述は Issue 372 の変更対象を識別するためのものであり、D1〜D4 の contract を再定義するものではない。

## 用語

- **managed distribution authority**: ownership assessment、executable plan、descriptor-bound filesystem mutation、guard/journal transition、typed process result を所有する `managed_distribution.py` の責務境界。
- **public intent**: fresh provisioning、recognized `update` / `init --force` reconciliation、managed distribution deprovision、explicit spec-history purge。
- **current forward guard**: `spec-dock/.distribution-retry.json` の schema 2 form。intent ごとの forward-only purpose を持ち、current implementation が journal と組み合わせて書き込む active recovery evidence。
- **legacy distribution retry payload**: 同じ `spec-dock/.distribution-retry.json` pathname に存在し得る schema 1 `distribution-rerun` payload。安全条件を満たす場合だけ current guard/journal へ一方向移行する migration input。
- **legacy uninstall marker**: `spec-dock/.uninstall-retry.json`。current implementation では新規 writer authority を持たず、自動変換せず、manual/fail-closed recovery 判定のために読む legacy evidence。
- **ordinary fast lane**: repository policy により `full_regression` nodes を skip する通常の `uv run pytest`。
- **focused full-regression shard**: heavy node を明示的に実行する `--run-full-regression --full-regression-shard` lane。
- **Full Regression verifier**: Issue 368 の current `verify-full-regression.py` と ledger による post-merge/current-candidate verification contract。
- **candidate SHA `C`**: PR head branch の full commit SHA。`pull_request` event では `github.event.pull_request.head.sha` を authority とし、D5 focused job はその SHA を明示 checkoutして runner 内の `git rev-parse HEAD` と一致させる。default checkoutの merge ref SHAである `github.sha` は `C` ではない。

## 観測可能な要件

| ID | 要件 |
|---|---|
| I372-R01 | D1〜D4 で受理済みの fresh、recognized reconciliation、deprovision、purge の intent/authority/postcondition/recovery semanticsを変更しない。Issue 372 は新 command、flag、public JSON schema、new destructive authority を追加しない。 |
| I372-R02 | 全 public distribution mutation は managed distribution authority を経由する。CLI は command parsing、target/package resolution、admission/serialization coordination、typed service dispatch、public rendering、exit mapping の adapter であり、managed asset の独立 writer、recursive mutation owner、journal/guard transition owner、staging cleanup ownerにならない。literal に一つの generic Python functionへ統合することは要件ではなく、intent-specific entrypointが同一 authority/kernel/journal/result boundaryを共有すればよい。 |
| I372-R03 | baselineで public call graph から到達不能な CLI-owned legacy managed-file writer/helper subgraph と、それを維持するためだけの private kernel import/test seamを production source から除去する。`managed_distribution.py` 内で現役の `_rename_distribution_no_replace` その他 descriptor-bound kernel primitive は legacy とみなさず維持する。 |
| I372-R04 | recovery metadata は pathname 名だけで legacy/current を判定しない。schema 2 `.distribution-retry.json` forward guard と `.distribution-journal.json` は current writer authorityとして維持し、schema 1 `.distribution-retry.json` は既存 contractに従う migration-only input、`.uninstall-retry.json` は reader-only legacy evidenceとして扱う。cross-intent、cross-authority、root/plan/protocol/package/evidence mismatch は追加 mutation 前に fail closed し、authority を推測昇格しない。 |
| I372-R05 | `init`、fresh/recognized `init --force`、fresh/recognized `update`、`uninstall` default/`--keep-specs`、`uninstall --remove-specs` の既存 command/flag、dry-run/apply、text、JSON schema version 1、one-object JSON、status、action projection、retry guidance、exit mapping、sanitization を保持する。unknown/modified/user-owned/Workbench/spec-history preservation は各 accepted intent contractどおり維持する。 |
| I372-R06 | provider source、checked-in dogfooding projection、wheel、sdist、installed package resources、fresh consumer output が、current package mappingに従って path inventory、regular-file bytes、required mode/executable bit、symlink target（存在する surface のみ）、managed manifest/protocol asset、stale-legacy absence で一致する。wheel/sdist は stale build output や generated Python cache を再収録しない。 |
| I372-R07 | Linux と macOS の両方で、同一 candidate SHA から、distribution filesystem safety、guard/journal forward recovery、root/parent rebind、symlink/hardlink/unknown preservation、no-replace publication、fresh package consumer を含む focused gate が成功する。通常 runner に必要 capability がない場合は target write 前に既存の stable fail-closed diagnostic で停止し、silent fallback や weaker mutation に切り替えない。 |
| I372-R08 | repository の current test-lane policy を維持する。ordinary `uv run pytest` は fast lane、heavy focused verification は `--run-full-regression --full-regression-shard`、global Full Regression は current verifier/ledger contract、post-merge workflow は `.github/workflows/provider-full-regression.yml` の current verifier routeとして区別する。historical failure count、historical duration、600秒等を新しい固定 acceptance value にしない。 |
| I372-R09 | root README、shipped/dogfooding migration/recovery guidance、およびそれらの provider projection は current guard/journal semanticsを正確に説明する。特に同一 `.distribution-retry.json` pathname の schema 1 legacy input と schema 2 current forward guardを混同せず、`.uninstall-retry.json` が自動変換されないこと、code rollback と forward recovery が別概念であることを明示する。完了済み Issue 368〜371 を未完了の将来 owner/compatibility route のように説明する stale wording は current product behavior の説明へ置き換える。 |
| I372-R10 | final implementation evidence は一つの candidate SHA に source、package artifact、Linux/macOS CI、focused tests、ordinary fast lane、Full Regression verifier、docs を束縛する。Implementation Completion、Strict Review Pass、Human PR Merge Gate、`issue finish` は互いに代替しない独立 gateとして扱う。 |

## スコープ

### 対象

- `src/spec_dock/cli.py` に残る dead distribution writer/helper/test seam の最小除去
- CLI → managed distribution authority の structural/call-route absence verification
- `src/spec_dock/managed_distribution.py` の current recovery authority と migration-only reader 境界の固定
- `tests/unit/infra/test_managed_distribution.py`、`tests/cli_runtime/test_distribution_cutover.py`、`tests/unit/infra/test_init_update.py`、`tests/integration/test_epic_00343_distribution.py` の D5 regression/parity coverage
- `src/spec_dock/assets/**`、checked-in `spec-dock/**`、package/build configuration の parity
- `.github/workflows/provider-ci.yml` における Linux/macOS focused provider evidence
- `.github/workflows/provider-full-regression.yml` と current verifier/ledger contract の維持確認
- `README.md`、`spec-dock/docs/README.md`、`spec-dock/docs/migration.md` と対応 provider asset projection の recovery/docs parity
- candidate SHA に束縛し、candidate commitを変更しない PR/check/CI artifact上の final verification receiptと、freeze前に完成したIssue report

### 対象外

- Issue 368〜371 の accepted behavior の再設計
- `DistributionProcessResult` public schema の version change
- new operation/action/product feature
- automatic whole-operation rollback
- generic transaction framework
- Windows support
- unrelated Full Regression failure の修復
- automatic GitHub Issue creationやIssue lifecycle変更
- broad module split、line-count reduction、style-only refactor
- `.meta.json`、node ID/title/path、dependency metadata の手編集
- Human PR merge の自動化

## Fail-closed boundary

### D5 で修正してよい final integration/parity gap

次は D5 owner の範囲で最小変更する。

- public production routeから到達不能であることを確認できた CLI legacy writer/helper/import/test seam
- package source/projection/build artifact の drift
- provider-only CI の macOS evidence gap
- existing accepted semanticsを誤って説明する README/migration wording
- D5 absence/parity を固定する test coverage 不足

### predecessor owner decisionへ戻す blocker

次のいずれかが current implementation の再調査で判明した場合、D5 で独自 semanticsを決めず実装を停止する。

1. D1〜D4 のいずれかの public route が、現在も managed distribution authority 外の executable writer/mutator を実行する。
2. `.uninstall-retry.json` に current production writer/resume authority が存在する。
3. cross-intent recovery を安全に解決するために、accepted intent/authority/postcondition を変更する必要がある。
4. public compatibility を守るには command/flag/JSON schema/exit semantics の owner decision が必要になる。
5. macOS を supported gate とするために、fail-closed capability boundaryでは足りず destructive semantics自体を変更する必要がある。
6. package parityを成立させるために current canonical/projection ownership contractを変更する必要がある。

単なる dead code、dead test seam、docs drift、CI gap、package projection drift は上記 blocker ではなく D5 の実装対象である。

## 受け入れ条件

| AC | 条件 | 対応要件 |
|---|---|---|
| I372-AC01 | current public commands の runtime spy/characterization が、それぞれ current intent-specific `execute_*_distribution()` entrypointを選択し、managed distribution authority外の managed-file writerを通らない。 | R01, R02, R05 |
| I372-AC02 | `cli.py` の baseline dead writer/helper subgraph と、そのためだけの `_rename_distribution_no_replace` / `_swap_regular_distribution_target_if_bound` / `_remove_distribution_target_if_bound` direct dependency が除去され、再導入を検出する structural test がある。current `managed_distribution.py` kernel primitive は維持される。 | R02, R03 |
| I372-AC03 | schema 2 `.distribution-retry.json` current guard writer、`.distribution-journal.json` writer、schema 1 migration、`.uninstall-retry.json` reader-only/manual behavior が regression testで区別され、cross-intent mismatch は write 0/manual/fail-closed contractを保持する。 | R04 |
| I372-AC04 | public parser/flag/dry-run/apply/text/JSON/exit/retry behavior の既存 characterization が greenで、new public surfaceがない。 | R01, R05 |
| I372-AC05 | provider/dogfood parity testが greenで、wheel/sdist package manifestが provider asset manifestと bytes/modes を含め一致し、installed/fresh consumerが same content contractを満たす。 | R06 |
| I372-AC06 | wheel と sdist からの isolated consumer で、fresh provisioning と recognized refresh に加え、D5が対象とする deprovision/purge routeの少なくとも public dispatch・preservation境界が packaged runtime から検証される。checkout source fallback はない。 | R05, R06 |
| I372-AC07 | provider CI の focused D5 job が Linux/macOS の両方で `github.event.pull_request.head.sha == C` を明示 checkoutし、各 runner の `git rev-parse HEAD == C` を検証したうえで required checksが green。default PR merge refの `github.sha` を `C` とみなさず、macOS jobを `continue-on-error` 等の best-effort にしない。 | R07, R10 |
| I372-AC08 | `make lint` と ordinary `uv run pytest` が green。heavy focused suites は `--run-full-regression --full-regression-shard` で明示実行され、lane policyを迂回しない。 | R08 |
| I372-AC09 | final candidate SHA に対し current `verify-full-regression.py` が current ledger contractを満たす。合否は verifier result/signature contractで判定し、過去の27 failuresや特定秒数を universal fixed gateにしない。 | R08, R10 |
| I372-AC10 | README/migration/recovery wording と provider projection が source/testsの current guard/journal semanticsに一致し、dogfood/provider parity testが green。 | R09 |
| I372-AC11 | tracked `report.md` は `C` freeze前に実装要約と検証方法まで完成させる。`C` 確定後の final evidence receiptはcandidate commitを変えないPR本文、GitHub check summary、CI artifactに candidate SHA `C`、PR head SHA、各 CI runner の checked-out HEAD、OS/runner、Python version、focused commands、package artifact digests、Full Regression verifier resultを対応付ける。remediationまたはtracked report変更で `C` が変わった場合は stale evidenceを final扱いしない。 | R07, R08, R10 |
| I372-AC12 | Implementation Completion、Strict Review Pass、Human PR Merge Gate、`issue finish` が別々に記録され、前者の不足を後者で代用しない。 | R10 |

## 完了時の非回帰保証

Issue 372 の変更後も次を維持する。

- unknown/modified/user-owned contentを pathname heuristicsだけで削除しない。
- keep/deprovision と remove/purge の authorityを相互昇格しない。
- active forward guard/journalを旧 installerへ rollback して復旧しない。compatible current/newer packageによる forward recoveryを優先する。
- journal/guard mismatch時に自動修復、marker deletion、推測 retryを行わない。
- JSON は一つの object とし、repository外 absolute pathやsource content等の既存 sanitization boundaryを弱めない。
- package surfaceだけを手修正して provider/dogfood/source driftを隠さない。
- Linux/macOS差を silent fallback によって隠さない。

## 2026-08-30 収束Addendum（既実施M1〜M5を変更しない）

本節は既存要件と実施済み成果を遡及変更しない。Step 10で発見されたrepository quality-policy blockerを解消し、同じD5目的へ収束するための追加条件だけを定める。

| ID | 追加要件 |
|---|---|
| I372-R11 | Issue `iss-00382` がaccepted ADRに従うrepository-level Full Regression lifecycle/successor authorityを実装し、人間mergeされるまでIssue 372のfinal Full Regression判定を停止する。Issue 372内にbaseline exception、failure test復活、historical row削除を実装しない。 |
| I372-R12 | Issue 382 merge後、Issue 372のproduction semanticsを追加変更せず、新しいfinal candidate SHAへordinary/focused/package/Linux/macOS/Full Regression/Strict evidenceを再束縛する。旧candidateまたはIssue 368 artifact verifierのreceiptをfinal evidenceへ流用しない。 |

| AC | 追加受け入れ条件 | 対応要件 |
|---|---|---|
| I372-AC13 | Issue 382のexact merged implementationがrepository-level canonical verifierを提供し、retained-skill successorをcollected・executed・passed・not-skippedとして証明し、他のactive baseline rowを維持する。 | R11 |
| I372-AC14 | Issue 382 merge後に形成したIssue 372 candidateについて、accepted canonical verifier、same-SHA evidence、Strict reviewがgreenであり、Implementation Completion、human merge、`issue finish`が別々に記録される。 | R12 |
