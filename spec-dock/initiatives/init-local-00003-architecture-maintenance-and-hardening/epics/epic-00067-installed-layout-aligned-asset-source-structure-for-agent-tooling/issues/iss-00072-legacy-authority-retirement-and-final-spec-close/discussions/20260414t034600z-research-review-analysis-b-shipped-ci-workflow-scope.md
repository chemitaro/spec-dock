# Review Analysis B: shipped CI workflow が repo 固有前提を持っている

- Source PR: `https://github.com/chemitaro/spec-dock/pull/73`
- Review source: Copilot inline comment on `src/spec_dock/assets/install_root/.github/workflows/ci.yml`
- Analyst mode: main analysis + consultant second opinion

## Finding

`install_root` 配下の `.github/workflows/ci.yml` は installer により managed repo へ配布される current asset であるにもかかわらず、workflow 内容が `python -m pip install .` と `python -m unittest -v tests/test_cli.py` を前提としており、spec-dock provider repo 固有の構造を一般 managed repo に仮定している。

## Evidence

- `AGENTS.md` では `src/spec_dock/assets/install_root/` を installed agent-tooling assets の current authority と明記している
- `src/spec_dock/assets/install_root/.github/workflows/ci.yml` の current 内容:
  - `python -m pip install .`
  - `python -m unittest -v tests/test_cli.py`
- 一般 managed repo は:
  - Python package root を持たない可能性がある
  - `tests/test_cli.py` を持たない可能性が高い
  - provider repo と同一の CI surface を持つ保証がない

## Assessment

- Validity: `妥当`
- Response priority: `必須`
- Why:
  - 配布 asset が配布先で壊れるのは shipped contract violation
  - review の指摘は product surface に直結しており、hygiene ではなく実害カテゴリ

## Options

### Option 1: この workflow を repo 固有のまま維持し、条件分岐で managed repo では実行しない

- Pros:
  - provider repo 向け CI を流用できる
- Cons:
  - 配布 asset としての意味が薄い
  - 条件判定の根拠が複雑になる
  - managed repo 向け contract が曖昧なまま残る

### Option 2: `install_root` から workflow を外す

- Pros:
  - managed repo に壊れた workflow を配らない
- Cons:
  - managed repo 向け baseline CI がなくなる
  - product の shipped automation surface が後退する

### Option 3: managed repo 向け generic workflow に置換する

- Pros:
  - 配布 contract と整合する
  - repo 非依存の baseline health check を提供できる
  - `spec-dock` の product value と一致する
- Cons:
  - workflow 設計をやり直す必要がある

## Best Response

`Option 3` が最善。

推奨内容:

- managed repo 向け workflow の基準コマンドを `./spec-dock/scripts/spec-dock validate` に置く
- 必要なら最小 smoke として local-only な `sync` 系を検討する
- `--github` のような認証や外部状態に依存する step は baseline workflow から外す
- provider repo 固有の package/test CI は provider repo 側 workflow に分離する

## Decision

- Classification: `対応必須`
- Action requirement: `must fix in this PR before merge`

## Notes

consultant 評価でも B は最優先の 1 つとされており、install_root 配布 contract と矛盾するため、反論余地は小さい。
