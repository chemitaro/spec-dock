---
種別: 要件ドラフト（Issue）
ID: "iss-00342"
タイトル: "Pytest Opt-In Full Regression Draft Requirement"
状態: "draft"
作成者: "ChatGPT authoring candidate / main orchestrator preserved summary"
最終更新: "2026-07-28"
親: ["epic-00080", "init-00079"]
authority: "evidence_only"
adoption_status: "unreviewed"
reflected_to: []
---

# Pytest opt-in full regression — 要件ドラフト

## 証跡

- ChatGPT conversation: `iss00342-pytest-opt-in-authoring`
- GitHub source branch: `codex/iss-00342-pytest-opt-in-planning`
- GitHub source commit: `2513c943fee26de16d0c0371eafeaa5a484cfd43`
- Source manifest hash: `f40f3dac04774c04df9a0d3fb015d59a2f250f246b5e2a9403c17139fcd14577`
- ZIP: `iss-00342-pytest-opt-in-full-regression-authoring-pack.zip`
- ZIP SHA-256: `511b81980c67da9d7e6b9290c20e59959e7d0835496aecee86f170bdc4402212`
- Pack tree digest: `466409f6203f455be53a483b5a36ac712542406a9b8106f6689739f4f392d6e1`
- Detailed candidate: `specdock-authoring-pack/drafts/requirement.md` in the ZIP

この文書は詳細候補の採用判断用要約であり、正本ではない。正本反映は Evidence Adoption Ledger、main orchestratorによる再記述、fresh reviewerを必要とする。

## 目的

通常開発とPull Requestの待ち時間を短縮しつつ、長時間の完全回帰テストを削除せず、明示実行と`main` merge後の事後検証に残す。

## 必須要件

1. 通常開発者とエージェントは、ラッパーを必要とせず通常のpytestコマンドを使う。

   ```bash
   uv run pytest
   uv run pytest tests/unit
   uv run pytest path/to/test.py::test_name
   ```

2. 長時間テストを含む完全回帰は、pytest-nativeな明示フラグでのみ許可する。

   ```bash
   uv run pytest --run-full-regression
   uv run pytest --run-full-regression -m full_regression
   uv run pytest --run-full-regression path/to/long_test.py::test_name
   ```

3. `--run-full-regression`がない場合、選択された`full_regression` itemはstable reason付きでpolicy skipされ、test bodyを実行しない。
4. `-m full_regression`だけでは実行許可にならず、選択された長時間itemはpolicy skipされる。
5. `--run-full-regression`がある場合はrepository policy skipを追加しない。既存の`skip`、`skipif`、`xfail`、import/platform条件は削除・上書きしない。
6. 全itemを`fast`または`full_regression`のちょうど一方へ分類し、未分類、重複分類、required-fast nodeの長時間分類をfail-closedで検出する。
7. focused invocationは収集されたsubsetだけのlocal invariantを検査し、repository全体の`H > 0`やrequired-fast全集合を要求しない。
8. repository全体の分類完全性は専用verifierで検証する。
9. default pytest configに`addopts = -m fast`を設定しない。
10. Make targetや独自ラッパーを通常実行の必須インターフェースにしない。

## CIイベント契約

| Event | Fast merge gate | Full regression |
|---|---:|---:|
| `pull_request` | yes | no |
| non-`main` push | no | no |
| `main` push | no | yes |
| `workflow_dispatch` | no | yes |
| `schedule` | no | no |

- PRでは既存の`Provider CI` / `provider-tests` identityを維持する。
- `main` pushとmanual fullは`uv run pytest --run-full-regression`を直接実行する。
- post-merge fullの失敗は既存mergeを遡及blockせず、修復対象として可視化する。
- schedule/cron、automatic merge、automatic rollbackは追加しない。

## 完全回帰の意味

formal fullはun-narrowed root commandで`fast ∪ full_regression`を選択し、repository policy skipが0である状態を指す。環境上正当なskipやxfailを強制解除して、全test bodyを無条件実行することは意味しない。

## 受け入れ条件

- bare root、`tests/unit`、focused fastが通常コマンドで動作し、長時間test bodyを実行しない。
- focused long without flagはexit 0、stable skip reason、body未実行である。
- focused long with flagはrepository policy skipなしでbodyを実行する。
- `-m full_regression` aloneは長時間testを実行しない。
- root fullはpolicy skip 0で、分類上の全集合を選択する。
- full flagが既存skip/skipif/xfail outcomeを変更しない。
- PR/main/manual/non-main/scheduleのevent matrixが自動テストで固定される。
- provider-only workflowがconsumer scaffoldへshipされない。
- READMEとAGENTSに通常・完全回帰・focused・incident/rollbackのコマンドを明記する。
- 同一stateのpaired measurementで通常経路がfullより短く、通常経路の長時間body実行数が0である。

## 非対象

- 長時間テスト自体の削除、assertion弱体化、恒久的skip化
- test directoryの全面再編
- xdist、sharding、remote cache、新規dependency
- schedule/cron
- public CLI/API/schema、migration、product dataの変更
- provider-only workflowのinstalled assetsへの追加
