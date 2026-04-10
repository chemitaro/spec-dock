---
種別: 要件定義書（Issue）
ID: "iss-00060"
タイトル: "Meta json dependency schema and reader alignment"
関連GitHub: ["#60"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-04-10"
親: ["epic-00059", "init-local-00003"]
---

# iss-00060 Meta json dependency schema and reader alignment — 要件定義（WHAT / WHY）

## 目的
- `epic-00059` の T1 foundation として、dependency metadata の canonical storage を node 直下の `.meta.json` に固定し、`infra/deps_reader.py` の read contract をその境界へ揃える。
- 後続の mutation / downstream parity / hard cutover judgment が依拠する最小契約として、schema、reader の fail-closed 条件、hard cutover boundary note、unit test の観測点を先に固定する。

## 背景・現状
- 現状の挙動:
  - `infra/deps_reader.py` は各 node directory の `deps.json` を読み、`depends_on` を解決して `DepsTopologyLoadResult.issue_depends_on_map` を構築している。
  - `infra/fs_repo.py` の `.meta.json` contract は node identity / GitHub linkage を管理するが、dependency field はまだ持たない。
  - provider-side 正本である `src/spec_dock/assets/spec_dock/docs/reference_deps.md` と、dogfooding 側 copy である `spec-dock/docs/reference_deps.md`、および `tests/cli_runtime/test_deps.py`、`tests/cli_runtime/test_sync.py`、`tests/cli_runtime/test_active.py`、`tests/test_init_update.py` も `deps.json` を前提にしている。
- 現状の課題:
  - epic requirement は `.meta.json` を唯一の SoT として要求しているが、reader と docs/test の正本がまだ `deps.json` 側にある。
  - mutation command を先に導入すると、write path と read path の正本がずれたままになる。
  - downstream command（`sync` / `active set` / `validate` / `delete`）は `DepsTopologyLoadResult` に依存しているため、T1 で read contract を固定しないと後続 tranche の責務分離が崩れる。
- 再現手順:
  1. `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/deps_reader.py` を確認する。
  2. `src/spec_dock/assets/spec_dock/docs/reference_deps.md`、`spec-dock/docs/reference_deps.md`、dependency 系 test を確認する。
  3. dependency の SoT が `deps.json` に残っており、`.meta.json` と reader contract が未整列であることを確認する。
- 観測点:
  - Runtime:
    - `infra/deps_reader.py`
    - `infra/contracts.py`
  - Metadata:
    - node 直下の `.meta.json`
    - node 直下の `deps.json`
  - Docs:
    - `src/spec_dock/assets/spec_dock/docs/reference_deps.md`
    - `spec-dock/docs/reference_deps.md`
  - Tests:
    - `tests/cli_runtime/test_deps.py`
    - `tests/cli_runtime/test_sync.py`
    - `tests/cli_runtime/test_active.py`
    - `tests/test_init_update.py`
- 情報源:
  - `epic-00059` requirement / design / plan
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/docs/phase_requirement.md`
  - `src/spec_dock/assets/spec_dock/docs/reference_deps.md`
  - `spec-dock/docs/reference_deps.md`
  - 現行 runtime / docs / tests

## 対象ユーザー / 利用シナリオ（必要時）
- 主な利用者:
  - dependency schema を実装・保守する maintainer
  - T2/T3/T4 の reviewer / implementer
- 代表シナリオ:
  - maintainer が `.meta.json` に dependency を保存する writer 実装へ進む前に、read 側の canonical schema と failure boundary を確認したい。
  - reviewer が「この issue は T1 foundation だけを閉じ、mutation や cutover evidence までは持たない」ことを spec 上で確認したい。

## スコープ
- MUST:
  - `.meta.json` に追加する dependency field の shape、既定値、許容 ref grammar を issue レベルで固定する。
  - `infra/deps_reader.py` が `.meta.json` を唯一の read source とする contract を固定する。
  - `DepsTopologyLoadResult.issue_depends_on_map` / `warnings` の downstream surface を維持する。
  - provider-side dependency docs 更新を mandatory とし、`src/spec_dock/assets/spec_dock/docs/reference_deps.md` を正本更新対象、`spec-dock/docs/reference_deps.md` を secondary verification 対象として扱う。
  - hard cutover boundary note を残し、legacy `deps.json` manual fix と dogfooding `validate` / `sync` evidence の owner が `iss-00062` であることを明示する。
  - schema / reader / boundary note を unit tests で観測できるようにする。
- MUST NOT:
  - `deps add` / `deps remove` の command contract をこの issue で導入しない。
  - `delete` / `sync` / `active set` / `validate` の parity fix や dogfooding checked-in data manual fix をこの issue で閉じない。
  - `deps.json` dual-read や fallback migration path を導入しない。
- OUT OF SCOPE:
  - dependency mutation write API
  - delete scrub / downstream parity
  - hard cutover judgment の実施・固定
  - final regression / close review

## 境界
- Always:
  - canonical storage は node 直下の `.meta.json` に置く。
  - reader contract は `.meta.json` だけを読み、旧 `deps.json` を SoT に戻さない。
  - downstream 互換のため、T1 では `DepsTopologyLoadResult` の shape を変えない。
  - architecture hardening として、曖昧な silent fallback より fail-closed / 明示 note を優先する。
- Ask:
  - `.meta.json` の dependency field 名と raw value grammar は design で具体化して固定する。
  - `deps_reader.py` の helper 抽出や test 配置は、既存 runtime test layout に合わせて最小差分で決める。
- Never:
  - storage 境界変更と mutation command 導入を同一 issue に混ぜない。
  - downstream parity 未完了のまま「cutover 完了」と表現しない。

## 非交渉制約
- `.meta.json` SoT と read contract の確定が本 issue の完了条件である。
- raw dependency ref grammar は current contract を不必要に広げず、`deps.json` 時代の既存 shorthand 解決ロジックを踏襲する。
- T1 では schema / reader / tests / boundary note のみに責務を絞り、T2/T3/T4 の owner を侵食しない。
- rollback は issue diff revert 前提とし、temporary compatibility mode は持たない。

## 前提
- `epic-00059` が `.meta.json` 単一 SoT と hard cutover only を採択している。
- 現行 runtime は `deps.json` を参照しているため、T1 では reader 契約の整列が最優先である。
- dogfooding checked-in data manual fix と dogfooding `validate` / `sync` evidence bundle は `iss-00062`（T3 integration）が owner であり、T1 completion gate には含めない。

## 受け入れ条件
- AC-001:
  - Actor:
    - maintainer / reviewer
  - Given:
    - node metadata が `.meta.json` で管理されている
  - When:
    - dependency schema を確認する
  - Then:
    - `.meta.json` に node 単位の `depends_on` field が定義され、field absence は `[]` と同義で扱う contract が明記されている
    - `depends_on` の raw value grammar は、current `deps.json` contract と同じ shorthand（node id / GitHub issue number / scoped ref / canonical issue URL）に限定される
    - storage 追加先が `.meta.json` であり、`deps.json` ではないこと、かつ `src/spec_dock/assets/spec_dock/docs/reference_deps.md` が正本更新対象、`spec-dock/docs/reference_deps.md` が secondary verification 対象であることが docs / spec / test で一致する
  - 観測点:
    - issue `design.md`
    - `src/spec_dock/assets/spec_dock/docs/reference_deps.md`
    - `spec-dock/docs/reference_deps.md`（secondary verification）
    - schema-focused unit tests
- AC-002:
  - Actor:
    - maintainer / reviewer
  - Given:
    - `infra/deps_reader.py` が graph と node metadata を読む
  - When:
    - `load_issue_depends_on_map` を実行する
  - Then:
    - reader は `.meta.json` だけを読み、`DepsTopologyLoadResult.issue_depends_on_map` と `warnings` の既存 surface を維持する
    - shorthand 解決、issue-level direct edge への compile、dedupe、deterministic sort、descendant/self 由来の invalid dependency reject、`deps_ref_expanded_to_empty` warning が current contract どおり観測できる
    - cycle detection や downstream parity の責務を reader に混ぜず、既存 downstream contract を壊さない
  - 観測点:
    - `infra/deps_reader.py`
    - reader-focused unit tests
    - downstream contract smoke assertions
- AC-003:
  - Actor:
    - maintainer / reviewer
  - Given:
    - hard cutover judgment はまだ T3 で固定されていない
  - When:
    - 本 issue の boundary note を確認する
  - Then:
    - T1 が確定するのは `.meta.json` schema と reader contract までであり、legacy `deps.json` checked-in data manual fix、dogfooding `validate` / `sync` evidence、final cutover judgment は `iss-00062` の責務であって T1 completion gate ではないことが明記されている
    - no dual-read / no auto-migration / rollback-by-revert の原則が issue spec で追える
  - 観測点:
    - issue `requirement.md`
    - issue `design.md`
    - issue `plan.md`

## 例外・エッジケース
- EC-001:
  - 条件:
    - `.meta.json` に `depends_on` field が存在しない
  - 期待:
    - dependency 未設定として `[]` を返し、schema default が一意に解釈される
  - 観測点:
    - reader-focused unit tests
- EC-002:
  - 条件:
    - `depends_on` に bool / object / unsupported string が混在する
  - 期待:
    - reader は fail-closed error で拒否し、曖昧に normalize しない
  - 観測点:
    - schema validation unit tests
- EC-003:
  - 条件:
    - node shorthand の展開結果が 0 issue になる
  - 期待:
    - hard error ではなく `deps_ref_expanded_to_empty` warning を返し、current downstream surface を維持する
  - 観測点:
    - reader-focused unit tests
- EC-004:
  - 条件:
    - repo に legacy `deps.json` がまだ残っている
  - 期待:
    - T1 spec はこれを reader fallback の根拠にせず、manual fix と dogfooding `validate` / `sync` evidence owner が `iss-00062` であることを boundary note に固定する
  - 観測点:
    - issue spec

## 入力→出力例（必要時）
- EX-001:
  - Input:
    - issue node の `.meta.json` に `"depends_on": ["iss-00123", 456, "owner/repo#789"]` がある
  - Output:
    - reader は canonical issue id の direct dependency map に compile し、dedupe 済み `issue_depends_on_map` を返す
- EX-002:
  - Input:
    - initiative / epic node の `.meta.json` に shorthand dependency がある
  - Output:
    - reader は現在の compile contract を維持し、配下 issue 群に展開した `issue_depends_on_map` を返す

## 用語（ドメイン語彙）
- TERM-001:
  - hard cutover boundary note:
    - T1 で固定する storage / read 原則と、`iss-00062` が担う manual fix / dogfooding `validate` / `sync` evidence owner / judgment timing を切り分けて記述する note
- TERM-002:
  - reader contract:
    - `infra/deps_reader.py` がどの file を読み、どのエラー / warning / compiled output を返すかという境界
- TERM-003:
  - direct issue edge:
    - initiative / epic / issue shorthand を解決したあと、issue -> issue に還元された canonical dependency edge

## 未確定事項
- なし:
  - field 名、default、raw value grammar、T1/T3 の owner boundary は本 issue で固定する
