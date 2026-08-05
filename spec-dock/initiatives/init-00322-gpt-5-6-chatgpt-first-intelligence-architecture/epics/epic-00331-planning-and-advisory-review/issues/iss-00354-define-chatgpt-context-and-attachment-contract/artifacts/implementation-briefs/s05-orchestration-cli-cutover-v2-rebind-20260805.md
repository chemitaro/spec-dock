# iss-00354 S05 実装ブリーフ v2 — Identity Rebind Addendum

> **目的:** `artifacts/implementation-briefs/s05-orchestration-cli-cutover-v2-20260805.md` の scope、不変条件、allowlist、verification、停止条件を変更せず、実装開始時の source identity だけを現在の named branch tip へ再結合する。
> **性質:** identity-only addendum。元の v2 brief の再生成、改訂、置換、実装承認、review verdict、assurance promotionではない。

## 1. Rebound identity

| 項目                                   | 値                                          |
| ------------------------------------ | ------------------------------------------ |
| Repository                           | `chemitaro/spec-dock`                      |
| Named branch                         | `codex/iss-00354-chatgpt-context-contract` |
| Previous brief source HEAD           | `a4e38bd00bf11dd7b2c125e6f33aef630c4cf332` |
| Current implementation baseline HEAD | `dd780169f65bb923229e7f43c72c6ea744475d49` |
| Named branch tip comparison          | `identical`                                |
| Ahead / behind                       | `0 / 0`                                    |
| Default branch fallback              | `0` / 使用禁止                                 |
| GitHub確認日                            | `2026-08-05`                               |

GitHub Connector で named branch の存在を確認し、`dd780169f65bb923229e7f43c72c6ea744475d49` と named branch tip を比較した結果は `identical`、ahead `0`、behind `0`、差分ファイル `0` である。default branch は参照していない。

元の v2 brief に記載された `a4e38bd00bf11dd7b2c125e6f33aef630c4cf332` は、**ブリーフ生成時の historical source identity** として保持する。S05 worker が実装開始時に使用する baseline は、この addendum により `dd780169f65bb923229e7f43c72c6ea744475d49` へ置き換わる。元のブリーフ本文を書き換えてはならない。

## 2. Rebind proof

GitHub Connector による比較結果は次のとおりである。

```text
base:   a4e38bd00bf11dd7b2c125e6f33aef630c4cf332
head:   dd780169f65bb923229e7f43c72c6ea744475d49
status: ahead
commits: 2
files changed: 3
```

変更ファイルは次の3件だけである。

| ファイル                                                                           |             GitHub差分 | 確認内容                                                                   |
| ------------------------------------------------------------------------------ | -------------------: | ---------------------------------------------------------------------- |
| `report.md`                                                                    | modified, `+11 / -0` | `EAL-033`、S05実装ブリーフv2の保存・identity・SHA・モデル境界、関連するartifact/evidence記録の追記 |
| `artifacts/implementation-briefs/s05-orchestration-cli-cutover-v2-20260805.md` |  added, `+1819 / -0` | `a4e38bd...` で生成済みの元v2 briefをrepository evidenceとして追加                  |
| `.assurance.json`                                                              |  modified, `+1 / -1` | `plan.md` のsource-binding SHA-256だけを現在値へ更新                             |

### 2.1 `report.md`

Previous HEAD の `report.md` は `EAL-032` までであり、S05 plan-review evidenceの後に直接 Final Quality Gate が続いていた。

Current HEAD では、次が追記されている。

* `EAL-033`。
* v2 brief の保存先、SHA-256、生成時 source HEAD。
* hard cutover、repeatable original-path forwarding、prompt ordering、no-inspection/no-materialization、各lane、focused verification、停止条件を具体化したというevidence。
* Luna / Maxを実測済みまたはverifiedと扱わない境界。
* S05実装ブリーフv2のartifact記録。

既存行の削除または置換はなく、GitHub差分は追加11行だけである。

### 2.2 `.assurance.json`

Current tip commit `dd780169f65bb923229e7f43c72c6ea744475d49` は `.assurance.json` だけを変更している。変更は `plan.md` のSHA-256を次のように更新したものに限定される。

```text
before: c04a6b7591a84f84840beebb1f9abcf81602571b177ffd8996ba79a29aeb778b
after:  6e5b8418b7ef98c15a895de90d2b4d49a209fc1e52b9b61cba010b769fec3b0e
```

`schema_version`、`policy_version`、`stage=requirement`、`status=provisional`、`mode=adaptive`、requirement/design binding、classification、risk facts、obligationsは変更されていない。assurance promotionは行われていない。

### 2.3 元の v2 brief

Current HEAD に保存された v2 brief は、次のidentityで保持される。

| 項目                   | 値                                                                              |
| -------------------- | ------------------------------------------------------------------------------ |
| Repository path      | `artifacts/implementation-briefs/s05-orchestration-cli-cutover-v2-20260805.md` |
| Recorded SHA-256     | `1bd1749dc1b460868e35326b7b9568d98bc43aaebddc33c9e6af62cc54b55eec`             |
| Git blob SHA         | `b3b86ec0a06348613c2cf0928d70951da6c64b6c`                                     |
| Original source HEAD | `a4e38bd00bf11dd7b2c125e6f33aef630c4cf332`                                     |
| Current binding      | 本addendumにより `dd780169f65bb923229e7f43c72c6ea744475d49`                        |

tip commit `dd780169...` は `.assurance.json` 以外を変更していないため、先行docs-only commitで追加されたv2 brief本文はtip commitでは変更されていない。元のartifactとreportに記録されたSHA-256も一致している。

## 3. Scope invariance

`a4e38bd...` から `dd780169...` のGitHub比較に上記3ファイル以外は存在しない。このため、次は変更されていない。

### 3.1 S05 production runtime

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue_planning.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py
```

### 3.2 S05 tests

```text
tests/unit/commands/test_issue_planning.py
tests/unit/application/test_issue_planning.py
tests/unit/application/test_issue_planning_prompt.py
tests/cli_runtime/test_chatgpt_cli.py
tests/integration/test_issue_planning_chatgpt_transport.py
tests/integration/test_issue_planning_e2e.py
```

### 3.3 Canonical specifications

```text
requirement.md
design.md
plan.md
```

Canonical requirement/design/planの本文、要件、設計判断、S05 execution card、allowlist、test contract、停止条件に差分はない。

### 3.4 Earlier implementation baseline

S03/S04のproduction runtime、Review resource、provider projection、unit/integration tests、same-HEAD closureを構成する実装にも差分はない。

### 3.5 v2 brief contract

次はすべて元のv2 briefのまま有効であり、本addendumは追加・削除・緩和を行わない。

* S05 hard-cutover scope。
* S03/S04から継承する20項目の不変条件。
* production 3ファイル、test 6ファイルのwrite allowlist。
* domain、infra、CLI parserのread-only境界。
* CLI、create、review、semantic revision、mechanical revisionの各契約。
* TC-S05-001〜TC-S05-010。
* focused unit、CLI、transport、lifecycle、Ruff、Mypy、legacy zero-match、diff-scope verification。
* identity、allowlist、requirement/design、S06境界、S03/S04 regression、lifecycle/outputの停止条件。

これらの現行本文はCurrent HEADのGitHub artifactでも維持されている。

## 4. Identity substitution rule

本addendumが変更するのはidentity parameterだけである。

```text
Previous brief authoring identity:
a4e38bd00bf11dd7b2c125e6f33aef630c4cf332

Current implementation baseline:
dd780169f65bb923229e7f43c72c6ea744475d49
```

元のv2 brief中で `a4e38bd...` が**生成履歴、reviewed input、過去の証跡**を表す箇所は historical recordとして読み替えず保持する。

元のv2 brief中で `a4e38bd...` が次を表す箇所だけは、実装開始時には `dd780169...` を用いる。

* named branch tipとの開始前一致確認。
* S05 implementation baseline。
* workerによるscope-diffの起点。
* resulting HEADとの変更ファイル監査。
* concurrent runtime/test driftの検出基準。

したがって、元の次のdiff-scope verificationはidentity parameterだけを置換する。

```bash
git diff --name-only \
  dd780169f65bb923229e7f43c72c6ea744475d49...HEAD
```

テスト群、allowlist、zero-match条件、期待結果、停止条件は変更しない。

## 5. Worker preconditions

S05 workerは、実装またはRed作成前に次をすべて確認しなければならない。

1. repositoryが `chemitaro/spec-dock` である。
2. named branchが `codex/iss-00354-chatgpt-context-contract` である。
3. named branch tipが `dd780169f65bb923229e7f43c72c6ea744475d49` と完全一致する。
4. default branch fallbackを使用していない。
5. current baseline後にS05 production 3ファイルまたはtest 6ファイルの先行変更がない。
6. S03/S04 path-only/direct-transport baselineに先行変更がない。
7. canonical requirement/design/planに先行変更がない。
8. workerのworktreeにscope外変更がある場合、それを安全に分離できる。
9. 元のv2 briefと本addendumを一組として使用する。
10. 実装差分を `dd780169...` 起点で監査する。

いずれかを満たさない場合、このaddendumはstaleであり、S05実装を開始せず `BLOCKED` とする。新しいexact HEADに対するidentity rebindが必要である。

## 6. Prohibitions

本addendumによって、次は許可されない。

* 元のv2 briefの再生成、書換え、要約版への置換。
* canonical requirement/design/plan/reportまたは`.assurance.json`のworker変更。
* original allowlistへのproduction/test path追加。
* read-only domain、infra、CLI parserの変更。
* S06以降の先行実装。
* thread binding、continuation、reusable Red/Blue stateの追加。
* wrapper、API、alternate backend、retry loop、fallbackの追加。
* inline/bytes fallback、input ZIP、copy、hash、tree inspection、generated manifest/prompt-packの追加。
* Candidate/Review schema、public status/reason、output validator、publication semanticsの変更。
* default branch、別branch、添付内容、ローカル記憶をGitHub exact identityの代替にすること。
* 本addendumだけを根拠とする実装完了、test PASS、fresh review PASS、Human adoption、assurance promotion、PR、merge、Issue closeの主張。

## 7. Model evidence boundary

要求モデルは元のv2 briefどおり次である。

```text
GPT-5.6 Luna
Reasoning Effort Max
```

確認済み証跡は次の範囲に限定される。

```text
requested: gpt-5.6
target: GPT-5.6 Sol
resolved-label evidence: independently verifiedではない
verification: no
reasoning-effort evidence: なし
```

したがって、次をverifiedと記録してはならない。

* `GPT-5.6 Luna`。
* `Reasoning Effort Max`。
* Luna / Max の組合せ。
* model自己申告だけに基づくresolved label。

実装・検証・fresh review後も、browser/provider経路で実測できた値だけを記録し、Reasoning Effortの観測証拠がない場合は `Max verified` と主張しない。

## 8. Binding effect

このaddendumの有効範囲は、named branch tipが次と一致している期間に限る。

```text
chemitaro/spec-dock
codex/iss-00354-chatgpt-context-contract
dd780169f65bb923229e7f43c72c6ea744475d49
```

このidentityが維持される限り、S05 workerは元のv2 briefのscope、不変条件、allowlist、verification、停止条件を変更せず、`dd780169f65bb923229e7f43c72c6ea744475d49` を実装baselineとして使用する。

branch tipの変化、runtime/test/spec drift、allowlist外差分、またはdefault branch依存が検出された時点で、本addendumによるidentity bindingは失効し、S05実装は `BLOCKED` となる。
