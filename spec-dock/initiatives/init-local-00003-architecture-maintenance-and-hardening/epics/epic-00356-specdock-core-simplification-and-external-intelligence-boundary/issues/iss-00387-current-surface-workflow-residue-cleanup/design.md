---
種別: 設計書（Issue）
ID: "iss-00387"
タイトル: "Current Surface Workflow Residue Cleanup"
関連GitHub: ["#387"]
状態: "draft"
最終更新: "2026-08-31"
依存: ["requirement.md"]
親: ["epic-00356", "init-local-00003"]
---

# iss-00387 Current Surface Workflow Residue Cleanup — 設計

詳細: [Design Guide](../../../../../../docs/authoring/design.md)

## 1. 設計目標

新しい仕組みを追加せず、Current surfaceを親Epic #356の採用済み契約へ収束させる。

1. Current textは旧workflow authorityを提示しない。
2. `active set`のpublic behaviorとinternal request shapeをselection-onlyに一致させる。
3. provider sourceを正本とし、dogfood projectionとのparityを維持する。
4. Historical evidenceとEpic #384所有surfaceを変更対象から隔離する。
5. drift guardは明示的なCurrent inventoryだけを検査し、全repository scanをproduction化しない。

## 2. Current / Target

| Surface | Current | Target |
|---|---|---|
| active-none report | 旧role、phase、reviewer、Profile、EAL、Promotion schemaを含む | active未設定・編集禁止・canonical pathだけを示す |
| root README | `active set --checkout`とEAL必須を案内 | selection-only、`issue start`、canonical rewriteを案内 |
| Authoring overview | Issue #359完了前の未来形 | 現在の二skillを現在形で案内 |
| active command args | parserにない旧flagのdefault値を内部へ運ぶ | targetと表示文字列だけを運ぶ |
| SetActiveRequest | targetのほかcheckout/GitHub/force系fieldを持つ | targetだけを持つ |
| set_active use case | `checkout=True`ならGit操作可能 | active stateのselection/writeだけを行う |
| issue start | helperでcheckout後、旧shape requestを生成 | helperでcheckout後、target-only requestを生成 |
| package config | stale mypy overrideとphantom glob | live inventoryだけを列挙 |
| drift guard | Current path coverageが不足 | explicit Current inventory + Historical exclusion |

## 3. Authorityとprojection

### 3.1 Source of truth

- shipped docs/system/runtimeの正本は`src/spec_dock/assets/spec_dock/**`である。
- `spec-dock/**`はdogfood projectionである。
- root `README.md`と`pyproject.toml`はprovider repository固有の正本であり、projection pairを持たない。
- 本IssueのR/D/Pは履歴領域内であるが、本Issue自身のcanonical authorityとして通常どおり更新する。

### 3.2 更新順序

1. provider sourceを変更する。
2. 既存の同期経路またはbyte-exact copyで対応projectionを更新する。
3. `cmp`または既存parity testで一致を確認する。
4. projection側だけの修正で差分を隠さない。

### 3.3 Placeholder content contract

三scopeのreportは同じ意味を持ち、scope名とcanonical pathだけを変える。

```markdown
# No active <Scope>

現在 active な <Scope> はありません。
このファイルは active 未設定時の placeholder であり、編集対象ではありません。
実際の Report は `<canonical-node-path>/report.md` にあります。
```

exact wordingは既存の日本語primary contractに合わせてtestで一元化してよい。ただし新しいtemplate engineは作らない。

## 4. Active selectionの責務境界

### 4.1 Public command

`active set`の公開入力は現状どおり次の三形式である。

- positional target
- `--id`
- `--github-issue`

ここでいうGitHub issue numberはlocal linkageを解決するselectorであり、GitHub network accessの許可ではない。新しいflagやaliasを追加しない。

### 4.2 Command contract

```text
ActiveSetArgs
  target_ref: TargetRef
  target_display: str

SetActiveRequest
  target: TargetRef
```

`_active_set_args()`はparser結果からこの二fieldだけを構築し、`_run_active_set()`はtargetだけをuse caseへ渡す。

### 4.3 Application contract

`set_active()`の責務は次に限定する。

1. node recordsを読みgraphを構築する。
2. target nodeを解決する。
3. active chainを選択する。
4. manifest/context packを生成する。
5. rollback付きactive writeを行う。
6. `ActiveSetResult(branch=None, ...)`を返す。

`set_active()`はGit gateway、GitHub、dependency evaluation、unfinished guardを呼ばない。

### 4.4 Issue start contract

`issue start`は既存順序を維持する。

```text
unfinished active guard
  -> dependency readiness
  -> checkout_active_target()
  -> set_active(SetActiveRequest(target=...))
  -> sync
```

`checkout_active_target()`はこのIssueで変更しない。active request縮小は、checkout helperの削除や移動ではない。

### 4.5 Compatibility

- public help、target resolution、rendered result、exit codeは変更しない。
- `ActiveSetResult.branch`は既存result shape維持のため残し、`active set`では常に`None`とする。
- repository内のdirect `SetActiveRequest` call siteはcompile/testで全てtarget-onlyへ更新する。
- repository外のPython internal importはpublic stability保証の対象としない。新しいdeprecated wrapperは作らない。

## 5. Current-facing drift guard

### 5.1 Explicit inventory

test-only inventoryは次を列挙する。

- root `README.md`
- provider/dogfood active-none report 3 pair
- provider/dogfood Authoring overview
- `ActiveSetArgs`/`SetActiveRequest` field shape
- public CLI help/negative behavior

### 5.2 Semantic assertions

raw word countではなく、surfaceごとのrequired/forbidden assertionを使う。

- README: `issue start`とselection-only説明が必要、`active set --checkout`とEAL必須説明は禁止。
- active-none: exact minimal contentが必要、旧schema heading/fieldは禁止。
- overview: 二skill pathが必要、Issue #359未来形は禁止。
- contracts: dataclass field tupleをexact matchする。
- behavior: fail-fast fake portで`set_active()`がGit/GitHub/depsを呼ばないことを示す。

### 5.3 Historical exclusion

次をCurrent inventoryへ入れない。

- `spec-dock/initiatives/**`（本Issue自身のdocs validationを除く）
- `docs/authoring/historical.md`
- `tests/fixtures/authoring_kit/existing_issue/**`
- migration-only wording
- removed-route negative test
- Epic #384 canonical docs

detector自体はsynthetic textに旧phraseを入れるmutation testで検証できる。Historical file本文を書き換えてtestを通さない。

## 6. Package/test hygiene

### 6.1 pyproject

削除候補を二entryへ限定する。

- mypy override: `tests.cli_runtime.test_delegated_authoring`
- package-data: `assets/install_root/.codex/**`

`.agents/**`と`.github/**`はcurrent installed assetのため保持する。clean wheel/sdistの実inventoryで削除の安全性を確認する。

### 6.2 Definition-only constants

候補ごとに次を満たす場合だけ削除する。

1. `rg`で定義以外の参照がない。
2. AST上の`Load`がない。
3. string/dynamic discoveryに使われない。
4. focused test、lint、collectionが成功する。

proofが成立しない候補は残し、理由をReportに記載する。このcleanupを理由に一般dead-code sweepを行わない。

## 7. Epic #384との境界

本IssueはCurrent contentと内部selection seamをcleanにし、Epic #384が扱うdistribution/test redesignの入力を単純化するだけである。次には触れない。

- managed asset ownership/manifestの置換
- fixed skill slot marker
- journal/checkpoint/recovery
- legacy identity catalog
- uninstall/purge semantics
- Full Regression shard/ledger/timing/provider workflow
- provider test portfolioの削減・統合

package buildとcurrent full-regression verifierは非回帰確認として実行するが、その構成やpolicyを変更しない。

## 8. Data、failure、recovery

### 8.1 Data migration

不要。node metadata、consumer user data、Historical document、schema、distribution stateを変更しない。

### 8.2 Failure handling

| Failure | 処置 |
|---|---|
| provider/dogfood不一致 | provider sourceを確認し再同期する |
| active setがGit portを呼ぶ | request contractionを未完了とし、application testから修正する |
| issue start regression | public `active set --checkout`を復活させず、call site/orderingをforward-fixする |
| live `.codex` assetを発見 | phantom判定を撤回しpackage config削除を止める |
| Historical false positive | Historicalを直さずCurrent inventoryを修正する |
| Epic #384 file変更が必要 | 本Issueから除外しEpic #384へhandoffする |
| Full Regression failure | ledger/timing/shardを変更せず原因diffを修正する |

### 8.3 Rollback

変更をdocs/placeholder、active request、package hygieneの小さいcommit境界に分ける。data migrationがないため各境界を独立revertできる。旧workflow schemaや`active set --checkout`をfallbackとして再導入しない。

## 9. Testability

| 設計観測点 | Test surface |
|---|---|
| placeholder/README/overview | `tests/unit/infra/test_authoring_kit_assets.py`、init/update parity test |
| request field shape/selection-only | `tests/unit/application/test_set_active.py`、`tests/cli_runtime/test_storage_core_cli.py` |
| issue start ordering | `tests/cli_runtime/test_issue_lifecycle.py` |
| package config/archive | `tests/unit/infra/test_init_update.py`、clean `uv build` |
| source/projection parity | existing `cmp`/parity assertions |
| overall non-regression | ordinary `uv run pytest`、current verifier、fresh init、`spec-dock validate` |
| no-touch boundary | implementation baselineからのpath diff audit |

## 10. 代替案と却下理由

| 案 | 判断 | 理由 |
|---|---|---|
| docsだけ直す | 却下 | internal checkout capabilityとrequest driftが残る |
| internal seamだけ直す | 却下 | Current利用者への誤案内が残る |
| repository-wide旧語彙ban | 却下 | Historical evidenceとmigration説明を破壊する |
| `checkout_active_target()`も削除 | 却下 | `issue start`のCurrent behaviorを壊す |
| Epic #384と同時実装 | 却下 | owner、failure boundary、review範囲が混ざる |
| compatibility wrapper/feature flag | 却下 | public surfaceは既に削除済みで、複雑性を再導入する |
| 本設計の限定cleanup | 採用 | Current contractを一つのIssueで最小に収束できる |

## 11. 要件対応

| 要件 | 設計 |
|---|---|
| R01〜R04, R08 | §3、§5 |
| R05 | §4 |
| R06 | §6 |
| R07 | §5 |
| N01〜N05 | §3〜§8 |
| AC01〜AC15 | §9とPlanのverification matrix |
