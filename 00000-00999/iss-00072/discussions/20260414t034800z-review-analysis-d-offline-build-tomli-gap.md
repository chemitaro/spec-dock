# Review Analysis D: offline build backend contract に `tomli` が不足

- Source PR: `https://github.com/chemitaro/spec-dock/pull/73`
- Review source: Codex inline comment on `tests/test_init_update.py`
- Analyst mode: main analysis + consultant second opinion

## Finding

issue-69 の hermetic wheelhouse / offline build backend contract では `build==1.2.2` を vendoring しているが、Python 3.10 条件付き依存である `tomli>=1.1.0` を wheelhouse に含めていない。そのため `pip install --no-index` による fresh venv の build backend 準備が Python 3.10 で失敗しうる。

## Evidence

- `tests/test_init_update.py` の issue-69 backend requirements:
  - `build==1.2.2`
  - `packaging==24.2`
  - `pyproject_hooks==1.2.0`
  - `setuptools==75.8.0`
  - `wheel==0.45.1`
- 同 file の wheelhouse filenames に `tomli` がない
- wheel fixture `tests/fixtures/wheelhouse/build-1.2.2-py3-none-any.whl` の `METADATA` に:
  - `Requires-Dist: tomli >= 1.1.0; python_version < "3.11"`
- repo 自体の supported Python range は `>=3.10`

## Assessment

- Validity: `妥当`
- Response priority: `必須`
- Why:
  - hermetic/offline 契約の欠落は test fixture bug
  - Python 3.10 support を掲げたまま dependency gap を残すのは整合しない

## Options

### Option 1: `tomli` を requirements と wheelhouse filenames に追加し、wheel も vendor する

- Pros:
  - 最小変更で contract を満たせる
  - Python 3.10 support を維持できる
  - hermetic/offline test の目的と整合する
- Cons:
  - fixture 更新が必要

### Option 2: Python 3.10 support をやめる

- Pros:
  - `tomli` gap 自体は消える
- Cons:
  - product compatibility policy を変える大きな変更になる
  - issue scope を超える

### Option 3: offline/hermetic 前提を緩めて network 依存にする

- Pros:
  - fixture 管理は減る
- Cons:
  - issue-69 の設計意図に反する
  - reproducibility が落ちる

## Best Response

`Option 1` が最善。

推奨内容:

- requirements fixture に `tomli` を追加する
- wheelhouse filenames contract に `tomli` を追加する
- 対応する wheel fixture を vendor する
- Python 3.10 fresh venv + `--no-index` の経路を実際に再検証する

## Decision

- Classification: `対応必須`
- Action requirement: `must fix in this PR before merge`

## Notes

consultant 評価でも D は B と並ぶ最優先事項。これは style 指摘ではなく、hermetic packaging contract の欠落と判断できる。
