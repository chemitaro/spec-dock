# iss-00354 S05 実装ブリーフ v2 — Identity Rebind Addendum v2

> **目的:** 元の `s05-orchestration-cli-cutover-v2-20260805.md` および既存の identity rebind addendum の scope、不変条件、allowlist、verification、停止条件を変更せず、S05 実装開始時の source identity だけを現在の named branch tip へ再結合する。
> **性質:** identity-only addendum。元 v2 brief または既存 addendum の再生成・改訂・置換ではなく、実装承認、review verdict、test PASS、assurance promotionでもない。
> **Binding state:** `ACTIVE`。以下の exact identity が維持される期間に限る。

## 1. Exact identity

| 項目                            | 値                                          |
| ----------------------------- | ------------------------------------------ |
| Repository                    | `chemitaro/spec-dock`                      |
| Named branch                  | `codex/iss-00354-chatgpt-context-contract` |
| Original v2 brief source HEAD | `a4e38bd00bf11dd7b2c125e6f33aef630c4cf332` |
| Previous bound baseline       | `dd780169f65bb923229e7f43c72c6ea744475d49` |
| Current source HEAD           | `ce7f933ff25e2edfc521d5e05cae995c8f967d69` |
| Named branch tip comparison   | `identical`                                |
| Ahead / behind                | `0 / 0`                                    |
| Default branch fallback       | 使用していない / 使用禁止                             |
| GitHub Connector 確認日          | `2026-08-05`                               |

GitHub Connector で named branch の存在を確認し、次の比較を行った。

```text
base:   ce7f933ff25e2edfc521d5e05cae995c8f967d69
head:   codex/iss-00354-chatgpt-context-contract
status: identical
ahead:  0
behind: 0
files:  0
```

したがって、確認時点の named branch tip は current source HEAD
`ce7f933ff25e2edfc521d5e05cae995c8f967d69` と完全一致する。default branch は参照していない。

## 2. Rebind proof

Previous bound baseline から current source HEAD までの GitHub 比較結果は次のとおりである。

```text
base:          dd780169f65bb923229e7f43c72c6ea744475d49
head:          ce7f933ff25e2edfc521d5e05cae995c8f967d69
status:        ahead
ahead / behind: 2 / 0
commits:       2
files changed: 2
```

変更ファイルは次の二件だけである。

| ファイル                                                                                  |            GitHub 差分 | 分類                                         |
| ------------------------------------------------------------------------------------- | -------------------: | ------------------------------------------ |
| `report.md`                                                                           | modified, `+11 / -1` | S05 v2 brief / rebind の evidence-only 記録整合 |
| `artifacts/implementation-briefs/s05-orchestration-cli-cutover-v2-rebind-20260805.md` |   added, `+238 / -0` | 前回 identity rebind addendum の保存            |

### 2.1 Current tip の report-only correction

Current source HEAD の commit は次である。

```text
ce7f933ff25e2edfc521d5e05cae995c8f967d69
docs(s05): EAL-033/034のreport追記を訂正
```

この commit が変更したファイルは `report.md` 一件だけであり、patch は次の二点に限定される。

1. 元 v2 implementation brief の採用記録である `EAL-033` を復元した。
2. `EAL-034` の previous source 表記を省略形 `a4e38bd...` から full SHA
   `a4e38bd00bf11dd7b2c125e6f33aef630c4cf332` へ訂正した。

復元された `EAL-033` と訂正後の `EAL-034` は、元 v2 brief と既存 rebind addendum を一組として current baseline へ引き継ぐという同一の S05 evidence chain を記録している。変更は report の採用台帳・artifact 記録・identity handoff・モデル証跡境界の整合に限られ、production、test、requirement、design、plan の意味変更を含まない。

### 2.2 既存 rebind addendum

既存 rebind addendum は、previous bound baseline 後の rebind evidence commit で新規追加された。Current tip の report-only correction commit はこの artifact を変更していない。

Current source HEAD における Git blob identity は次である。

```text
path:
artifacts/implementation-briefs/s05-orchestration-cli-cutover-v2-rebind-20260805.md

Git blob SHA:
cf57b5946e106e67bc4ebba428982f5f4d857dbb
```

したがって、既存 rebind addendum の本文、scope、不変条件、allowlist、verification、停止条件は、その追加時点から current tip まで変更されていない。

### 2.3 元 v2 brief

元 v2 brief は previous bound baseline と current source HEAD の両方で同一 Git blob を持つ。

```text
path:
artifacts/implementation-briefs/s05-orchestration-cli-cutover-v2-20260805.md

Git blob at dd780169f65bb923229e7f43c72c6ea744475d49:
b3b86ec0a06348613c2cf0928d70951da6c64b6c

Git blob at ce7f933ff25e2edfc521d5e05cae995c8f967d69:
b3b86ec0a06348613c2cf0928d70951da6c64b6c
```

元 v2 brief の本文および実装契約は byte identity の観点でも変更されていない。

## 3. Scope invariance

`dd780169f65bb923229e7f43c72c6ea744475d49` から
`ce7f933ff25e2edfc521d5e05cae995c8f967d69` の GitHub 比較には、前節の二ファイル以外は存在しない。

### 3.1 S05 production runtime

次の production write allowlist 対象に差分はない。

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue_planning.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py
```

したがって、旧 `--context-manifest` の hard cutover、`--provided-context-path`、create/review/revise wiring、prompt path ordering、identity・stale・publication semantics は未実装のままであり、この rebind によって変更されたとは扱わない。

### 3.2 S05 tests

次の test write allowlist 対象に差分はない。

```text
tests/unit/commands/test_issue_planning.py
tests/unit/application/test_issue_planning.py
tests/unit/application/test_issue_planning_prompt.py
tests/cli_runtime/test_chatgpt_cli.py
tests/integration/test_issue_planning_chatgpt_transport.py
tests/integration/test_issue_planning_e2e.py
```

TC-S05-001〜TC-S05-010、focused unit、CLI、transport、lifecycle、Ruff、Mypy、legacy zero-match、diff-scope verification は元 v2 brief のまま未実行である。

### 3.3 Canonical requirement / design / plan

次の canonical specifications に差分はない。

```text
requirement.md
design.md
plan.md
```

要件、設計判断、S05 execution card、production/test allowlist、verification contract、停止条件は変更されていない。

### 3.4 S03/S04 baseline

S03/S04 の次の範囲にも差分はない。

* path-only application contract と caller wiring。
* direct repeated `--file` transport。
* Review resource の identity contract。
* provider / projection runtime。
* no-inspection / no-materialization tests。
* transport / lifecycle integration tests。
* same-HEAD closure を構成する report 外の実装証跡。

S03/S04 の runtime/test/spec closure を再解釈または再開する変更ではない。

### 3.5 元 v2 brief と既存 rebind addendum

次は引き続き元 v2 brief および既存 rebind addendum のまま有効である。

* S05 hard-cutover scope。
* S03/S04 から継承する不変条件。
* production 3ファイル、test 6ファイルの write allowlist。
* domain、infra、CLI parser の read-only 境界。
* create、review、semantic revision、mechanical revision の各契約。
* path order、duplicate retention、lexical relative/absolute form、object identity。
* no-inspection / no-materialization 境界。
* TC-S05-001〜TC-S05-010。
* focused verification commands。
* P0/P1 相当の停止条件。
* fresh Red Team の read-only / defect-only 境界。

本 addendum v2 はこれらを追加、削除、緩和、一般化しない。

## 4. Identity substitution rule

本 addendum v2 が変更するのは current implementation identity だけである。

```text
Previous bound implementation baseline:
dd780169f65bb923229e7f43c72c6ea744475d49

Current implementation baseline:
ce7f933ff25e2edfc521d5e05cae995c8f967d69
```

次の identity は historical evidence として書き換えず保持する。

```text
Original v2 brief source:
a4e38bd00bf11dd7b2c125e6f33aef630c4cf332

Previous rebind baseline:
dd780169f65bb923229e7f43c72c6ea744475d49
```

実装開始時には、元 v2 brief または既存 rebind addendum にある「current baseline」「named branch tipとの一致確認」「worker diff起点」「concurrent drift検出基準」だけを、次へ置き換える。

```text
ce7f933ff25e2edfc521d5e05cae995c8f967d69
```

worker の implementation diff 監査起点は次とする。

```bash
git diff --name-only \
  ce7f933ff25e2edfc521d5e05cae995c8f967d69...HEAD
```

テスト、allowlist、期待結果、停止条件は変更しない。

## 5. Worker preconditions

S05 worker は実装または Red 作成前に、次をすべて確認しなければならない。

1. repository が `chemitaro/spec-dock` である。
2. named branch が `codex/iss-00354-chatgpt-context-contract` である。
3. named branch tip が `ce7f933ff25e2edfc521d5e05cae995c8f967d69` と完全一致する。
4. default branch fallback を使用していない。
5. current source HEAD 後に S05 production 3ファイルまたは test 6ファイルの先行変更がない。
6. canonical requirement/design/plan に先行変更がない。
7. S03/S04 path-only/direct-transport baseline に先行変更がない。
8. worker のローカル worktree が clean、または scope 外変更を安全に分離できる。
9. 元 v2 brief、既存 rebind addendum、本 addendum v2 を一組として使用する。
10. 実装差分を current source HEAD 起点で監査する。

GitHub Connector はローカル worktree の clean 状態を検証していない。これは worker 開始時の未検証 precondition である。

いずれかを満たさない場合、本 addendum v2 は stale であり、S05 実装を開始せず、状態を次とする。

```text
BLOCKED
```

新しい named branch tip に対する identity-only rebind を取得するまで進めてはならない。

## 6. Prohibitions

本 addendum v2 によって、次は許可されない。

* 元 v2 brief または既存 rebind addendum の再生成、書換え、短縮版への置換。
* canonical requirement/design/plan/report または `.assurance.json` の worker 変更。
* production/test allowlist の拡張。
* read-only domain、infra、CLI parser の変更。
* S06 以降の先行実装。
* thread binding、continuation、reusable Blue/Red state の追加。
* wrapper、API、alternate backend、retry loop、fallback の追加。
* inline/bytes fallback、input ZIP、copy、hash、tree inspection、generated manifest/prompt-pack の追加。
* Candidate/Review schema、public status/reason、output validator、publication semantics の変更。
* default branch、別 branch、添付だけの内容、ローカル記憶を exact GitHub identity の代替にすること。
* 本 addendum v2 だけを根拠とする実装完了、test PASS、fresh review PASS、Human adoption、assurance promotion、PR、merge、Issue close の主張。

## 7. Model evidence boundary

本 identity rebind では、新しいモデル実測証跡を生成していない。

既存記録から確認できる範囲は次に限定される。

```text
requested: gpt-5.6
target: GPT-5.6 Sol
verification: no
reasoning-effort evidence: なし
```

したがって、次を verified と記録してはならない。

* `GPT-5.6 Luna`。
* `Reasoning Effort Max`。
* Luna / Max の組合せ。
* model 自己申告だけに基づく resolved label。

S05 実装・検証・fresh review 後も、provider/browser 経路で実測できた値だけを記録する。Reasoning Effort の観測証拠がない場合、`Max verified` と主張しない。

## 8. Binding effect

本 addendum v2 の有効範囲は、named branch tip が次と一致している期間に限る。

```text
repository:
chemitaro/spec-dock

named branch:
codex/iss-00354-chatgpt-context-contract

current source HEAD:
ce7f933ff25e2edfc521d5e05cae995c8f967d69
```

この identity が維持される限り、S05 worker は元 v2 brief と既存 rebind addendum の scope、不変条件、allowlist、verification、停止条件を変更せず、`ce7f933ff25e2edfc521d5e05cae995c8f967d69` を implementation baseline として使用する。

branch tip の変化、runtime/test/spec drift、allowlist 外差分、既存 brief/addendum の内容変更、または default branch 依存が検出された時点で、本 binding は失効し、S05 実装は `BLOCKED` となる。
