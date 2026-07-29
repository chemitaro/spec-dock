---
種別: ADR（Architecture Decision Record）
ID: "20260728t105349z-03-adr"
タイトル: "Use Direct Pytest Commands With Explicit Full Regression Opt-In"
状態: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-07-28"
親: ["iss-00342"]
authority: "accepted"
accepted_authority: "accepted ADR"
accepted_at: "2026-07-28"
accepted_by: "iwasawayuuta"
mirror_eligible: true
derived_from:
  - "user clarification on 2026-07-28"
  - "artifacts/20260728t025412z-adr-separate-fast-merge-gate-and-full-regression-execution.md"
  - "artifacts/20260728t090735z-chatgpt-output-pytest-opt-in-full-regression-review.md"
  - "ChatGPT authoring ZIP SHA-256 511b81980c67da9d7e6b9290c20e59959e7d0835496aecee86f170bdc4402212"
reflected_to:
  - "requirement.md"
  - "design.md"
  - "plan.md"
  - "report.md"
---

# direct pytestと明示的full-regression opt-inを採用する

## ADR化基準

- hard to reverse: yes。通常開発、AI agent、CIの共通コマンド契約を変更する。
- surprising without context: yes。bare pytestで収集された長時間itemがpolicy skipになる。
- real tradeoff: yes。単純なmarker selectionよりhookは増えるが、通常インターフェースと誤実行防止を両立する。
- ADRとして残す理由: 既存Option Aのevent routingを維持しつつ、旧command-selectionをdurableに置換するため。

## Decision

既存accepted ADRが定める高速PR gate、manual full、`main` merge後full、scheduleなしのevent routingを維持する。その上でcommand-selectionを次のようにrefineする。

### 通常コマンド

```bash
uv run pytest
uv run pytest tests/unit
uv run pytest path/to/test.py::test_name
```

### 明示的な完全回帰

```bash
uv run pytest --run-full-regression
uv run pytest --run-full-regression -m full_regression
uv run pytest --run-full-regression path/to/long_test.py::test_name
```

- `--run-full-regression`をpytest-native optionとして登録する。
- 全itemを`fast`または`full_regression`へ排他的・完全に分類する。
- flagなしではselected `full_regression` itemへsession-local policy skipを追加する。
- flagありではrepository policy skipを追加しない。
- `-m full_regression`だけでは実行許可にならない。
- 既存のskip、skipif、xfailを削除・上書きしない。
- default `addopts = -m fast`を使わない。
- Make wrapperや独自scriptを通常実行の必須interfaceにしない。

## Context

旧設計はdefault `-m fast`と`make test-provider-fast/full`をstable facadeにする前提だった。しかしowner intentは、通常作業では特別なscriptを意識せずstandard pytest commandを使い、長時間testを実行するときだけspecial operationを要求することである。

marker expressionはselectionを表すが、実行許可を表さない。default `-m fast`はCLIの`-m full_regression`でoverrideでき、focused longはdeselection/no-testsになり得る。このためselectionとpermissionを別mechanismにする。

## Options

### default `addopts = -m fast` — rejected

- ordinary outputは静かだが、`-m full_regression`がownerの意図しないopt-inになる。
- focused longがreason付きskipではなくdeselectionになる。
- configured selectionとCLI overrideの理解が必要になる。

### permanent `@pytest.mark.skip` — rejected

- formal fullでもskipが残る。
- generic unskipはlegitimate skip/skipif/import/platform policyを壊し得る。

### environment-variable `skipif` — rejected

- shell stateとtruthy parsingを新しいinterfaceにする。
- `pytest --help`からdiscoverできず、focused commandだけではpermission stateが分からない。

### pytest option controlled conditional policy skip — accepted

- ordinary pytest commandを変更しない。
- special operationがhelpに現れる。
- focused longはreason付きskip、exit 0になる。
- selectionとpermissionを直交させられる。
- existing skipを解除する必要がない。

## Consequences

良い点:

- 新メンバーとAI agentは通常どおりpytestを実行できる。
- 長時間testを意図せずbody実行することを防げる。
- focused longを実行しなかった理由と再実行方法が明確になる。
- CIとlocalが同じdirect commandを使える。

制約:

- long itemはflagなしでもcollect/importされるため、collection cost/failureは残る。
- bare pytestのsummaryにpolicy skipが現れる。
- hook orderとdynamic marker visibilityを契約テストで固定する必要がある。
- full regressionだけが検出する不具合はmerge後に判明し得る。

## CI routing

| Event | Fast | Full |
|---|---:|---:|
| `pull_request` | yes | no |
| non-`main` push | no | no |
| `main` push | no | yes |
| `workflow_dispatch` | no | yes |
| `schedule` | no | no |

PRは`uv run pytest`、main/manual fullは`uv run pytest --run-full-regression`を直接実行する。既存check identityを維持し、post-merge failureは事後検知として扱う。

## Rollback

誤分類、policy leakage、legitimate skipの変化、または許容できないpost-merge回帰を検出した場合、PR commandを`uv run pytest --run-full-regression`へ戻し、post-merge full workflowを無効化できる。分類markerと検証testは診断用に保持する。

## References

- `artifacts/20260728t025412z-adr-separate-fast-merge-gate-and-full-regression-execution.md`
- `artifacts/20260728t090735z-chatgpt-output-pytest-opt-in-full-regression-review.md`
- `artifacts/20260728t105349z-draft-requirement-pytest-opt-in-full-regression-draft-requirement.md`
- `artifacts/20260728t105349z-01-draft-design-pytest-opt-in-full-regression-draft-design.md`
- `artifacts/20260728t105349z-02-draft-plan-pytest-opt-in-full-regression-draft-plan.md`
