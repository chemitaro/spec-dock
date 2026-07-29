---
種別: 設計ドラフト（Issue）
ID: "iss-00342"
タイトル: "Pytest Opt-In Full Regression Draft Design"
Issue Grade: "standard"
状態: "draft"
作成者: "ChatGPT authoring candidate / main orchestrator preserved summary"
最終更新: "2026-07-28"
関連Requirement: ["requirement.md"]
関連Plan: ["plan.md"]
親: ["epic-00080", "init-00079"]
authority: "evidence_only"
adoption_status: "unreviewed"
reflected_to: []
---

# Pytest opt-in full regression — 設計ドラフト

## 証跡

- Detailed candidate: `specdock-authoring-pack/drafts/design.md`
- ZIP SHA-256: `511b81980c67da9d7e6b9290c20e59959e7d0835496aecee86f170bdc4402212`
- Source commit: `2513c943fee26de16d0c0371eafeaa5a484cfd43`

この文書はChatGPT詳細候補の採用判断用要約であり、正本ではない。

## 設計判断

### 選択と実行許可を分離する

- pytestの`-m`はitem selectionを担当する。
- `--run-full-regression`は長時間itemのbodyを実行してよいかを担当する。
- `-m full_regression`は選択だけを変更し、実行許可を与えない。

この分離により、通常コマンドを変えず、focused longの誤実行も防ぐ。

### hook責務

`tests/conftest.py`に次の責務を置く。

1. `pytest_addoption`
   - boolean option `--run-full-regression`を登録する。
2. marker registration
   - `fast`と`full_regression`をstrict markerとして登録する。
3. `pytest_itemcollected`
   - required-fast exact nodes、既存heavy prefix、明示markerから各itemを早期分類する。
   - exactly-one違反をcollection errorにする。
   - marker expression評価より前にdynamic markerが見えるようにする。
4. `pytest_collection_modifyitems`
   - flagなしの場合だけ、選択された`full_regression` itemへsession-local policy skipを追加する。
   - flagありの場合はpolicy skipを追加しない。
   - 既存skip/skipif/xfailを削除・変更しない。

stable reason:

```text
full regression test; rerun with --run-full-regression
```

### 分類契約

- `C`: collected items
- `F`: fast items
- `H`: full regression items

repository全体では`F ∩ H = ∅`、`F ∪ H = C`、`U = 0`、`H > 0`とrequired-fast exact subsetを専用verifierで確認する。

focused invocationでは収集subsetのexactly-oneだけを確認する。未収集のrequired-fast nodeやglobal `H > 0`を要求しない。

### pytest設定

`pyproject.toml`はmarker登録とstrictnessだけを持つ。default selectionを変える`addopts = -m fast`は置かない。

### CI topology

- `.github/workflows/provider-ci.yml`
  - `pull_request`のみ。
  - `make lint`と`uv run pytest`。
  - existing workflow/job identityを維持する。
- `.github/workflows/provider-full-regression.yml`
  - `main` pushと`workflow_dispatch`のみ。
  - `uv run pytest --run-full-regression`。
  - scheduleなし。
  - main pushはlatest SHAを残すconcurrency、manualは相互cancelしないgroup。
  - failureをswallowせず、event/SHA/count/duration/outcome/rerun情報をsummaryへ残す。

同一eventでfast/fullを重複実行しない。

## コマンド行列

| Command | Selection | Permission | Expected |
|---|---|---|---|
| `uv run pytest` | root `F ∪ H` | no | F body実行、selected Hはpolicy skip |
| `uv run pytest tests/unit` | unit subset | no | subset F実行、subset Hはpolicy skip |
| `uv run pytest <fast-node>` | focused F | no | pass/fail normally |
| `uv run pytest <heavy-node>` | focused H | no | stable reason付きskip、exit 0 |
| `uv run pytest -m full_regression` | H | no | selected Hをpolicy skip |
| `uv run pytest --run-full-regression <heavy-node>` | focused H | yes | bodyを実行 |
| `uv run pytest --run-full-regression -m full_regression` | H | yes | runnable Hを実行 |
| `uv run pytest --run-full-regression` | root `F ∪ H` | yes | policy skipなしのformal full |

## skip安全性

恒久的な`@pytest.mark.skip`を長時間分類に使わない。skipはstatic marker、skipif、module/import、imperative skip、plugin/platform policyなど複数の起源を持つため、full modeでskip markerをgenericに除去すると正当なskipまで壊す。

repository policyはflagなしsessionでのみ追加する。flagありsessionでは追加しない。この方式なら既存skipを「解除」する必要がない。

policy skipはcollection/importを止めない。したがってcollection failureやcollection timeは残り、この限界を文書化・characterization testで固定する。

## 変更境界

変更候補:

- `tests/conftest.py`
- `tests/unit/test_provider_test_lanes.py`
- `tests/unit/infra/test_init_update.py`
- `pyproject.toml`
- `.github/workflows/provider-ci.yml`
- `.github/workflows/provider-full-regression.yml`
- `README.md`
- `AGENTS.md`
- Issue `report.md`

原則変更しない:

- `Makefile`（既存`lint`のみ維持）
- `src/spec_dock/**`
- shipped assets / consumer workspace
- branch protection
- unrelated workflows

## 失敗・ロールバック

- flagなしでH bodyが実行される
- flagありでpolicy skipが残る
- legitimate skip/xfailが変わる
- dynamic markerが`-m`から見えない
- focused collectionがglobal invariantで失敗する
- check identityが変わる
- provider workflowがconsumerへshipされる

上記を検出した場合は停止する。ロールバックはPRのdirect commandを`uv run pytest --run-full-regression`へ戻し、post-merge workflowを無効化する。分類markerと検証testは診断資産として保持できる。
