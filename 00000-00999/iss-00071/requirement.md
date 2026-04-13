---
種別: 要件定義書（Issue）
ID: "iss-00071"
タイトル: "Verification dogfooding and update parity"
関連GitHub: ["#71"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-04-13"
親: ["epic-00067", "init-local-00003"]
---

# iss-00071 Verification dogfooding and update parity — 要件定義（WHAT / WHY）

## 目的
- `iss-00069` の package parity と `iss-00070` の installer cutover をまとめて最終検証し、epic の `E-AC-002` と `E-AC-003` を閉じる。
- checked-in dogfooding workspace、runtime `validate/sync`、isolated installed package surface の 3 面で、install-shaped contract が同じ結果へ収束する状態を確定する。

## 背景・現状
- 現状の挙動:
  - installer 側には managed sync / cleanup の contract test があり、runtime 側には `validate` / `sync` の command contract test がある。
  - dogfooding checked-in state は `tests/test_init_update.py` の mirror map と subprocess parity tests で検証されている。
  - package-installed 系の自動検証は build artifact parity が中心で、site-packages 実体からの final cutover parity は issue-70 handoff 後にまとめて閉じる前提である。
- 現状の課題:
  - `iss-00069` と `iss-00070` がそれぞれ prerequisite を閉じても、local checkout / installed package / checked-in dogfooding state が同じ contract を示す最終証跡はまだ分散している。
  - runtime `validate` / `sync` の preflight、`sync --force` degraded path、missing artifact fail-fast、dogfooding snapshot parity を install-shaped layout 前提で揃えて読む contract が未固定である。
  - checked-in `.agents`、`.codex`、`.github`、`.github/workflows` と provider-side `install_root` の同期結果を、final verification tranche として明示する必要がある。
- 再現手順:
  1. `iss-00069` / `iss-00070` 完了後の checkout で `python -m unittest tests/test_init_update.py` を確認する。
  2. runtime command tests と checked-in dogfooding parity tests を確認する。
- 観測点:
  - Filesystem:
    - checked-in `.agents/`
    - checked-in `.codex/`
    - checked-in `.github/`
    - checked-in `spec-dock/`
  - CLI:
    - `./spec-dock/scripts/spec-dock validate`
    - `./spec-dock/scripts/spec-dock sync`
    - `./spec-dock/scripts/spec-dock sync --github`
  - Tests:
    - `tests/test_init_update.py`
    - `tests/test_cli.py`
    - `tests/cli_runtime/`
    - `tests/presentation_runtime/`
  - Installed package:
    - isolated non-editable package-installed `spec-dock`
- 情報源:
  - `tests/test_init_update.py`
  - `tests/test_cli.py`
  - `tests/cli_runtime/test_validate.py`
  - `tests/cli_runtime/test_sync.py`
  - `tests/presentation_runtime/test_runtime_sync_s07.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/...`
  - `iss-00069` docs
  - `iss-00070` docs
  - `epic-00067` docs

## 対象ユーザー / 利用シナリオ（必要時）
- 主な利用者:
  - maintainer / reviewer
  - dogfooding repo を使って release readiness を確認する contributor
- 代表シナリオ:
  - maintainer が provider-side assets を更新したあと、checked-in dogfooding state を再同期して runtime `validate/sync` と installed-package smoke まで一括で確認する。
  - reviewer が final verification evidence を見て、local checkout だけでなく installed package と checked-in state でも install-shaped contract が一致していることを確認する。

## スコープ
- MUST:
  - `E-AC-002` と `E-AC-003` を閉じる verification evidence を揃える。
  - local checkout runtime、isolated installed package、checked-in dogfooding workspace の 3 面で install-shaped contract が一致することを確認する。
  - runtime `validate` / `sync` / `sync --github` の command surface が install-shaped contract と矛盾しないことを確認する。
  - missing artifact fail-fast と `sync --force` degraded path を install-shaped layout 前提で再確認する。
  - checked-in `.agents` / `.codex` / `.github` / `.github/workflows` の parity と `spec-dock update` 後の convergence を確認する。
- MUST NOT:
  - installer source discovery や managed ownership の主契約を再設計しない。
  - package inclusion / built artifact parity の主契約を作り直さない。
  - legacy authority retirement 自体をこの issue で閉じない。
- OUT OF SCOPE:
  - `codex_skills` source tree の物理削除
  - epic / issue docs の final cleanup
  - Claude Code 拡張

## 境界
- Always:
  - this issue は verification / dogfooding / parity evidence を閉じる tranche であり、new source-of-truth は作らない。
  - runtime command verification は checked-in dogfooding workspace に対する事実確認であり、installer contract 自体の owner は `iss-00070` に残る。
  - installed package verification は `iss-00069` と `iss-00070` で確立した isolated surface をそのまま使う。
- Ask:
  - verification surface を増やす必要が出るのは、epic acceptance を閉じるのに不足がある場合だけ。
- Never:
  - final verification を local checkout のみで済ませない。
  - checked-in dogfooding drift を「issue-72 で直すから」で放置しない。
  - `sync --force` degraded path を silent success と誤読しない。

## 非交渉制約
- `epic-00067` の `E-AC-002` と `E-AC-003` の closure owner はこの issue である。
- verification は少なくとも次の 3 系統を含まなければならない。
  - checkout-based installer/runtime regression
  - isolated installed package cutover smoke
  - checked-in dogfooding workspace parity
- runtime command surface の primary evidence は `validate` / `sync` / `sync --github` の command contract とその subprocess tests とする。
- `sync --force` は preflight failure を degraded で継続する既存 contract を維持し、その warning / degraded surface が install-shaped layout でも崩れないことを確認する。
- missing artifact / invalid runtime prerequisite は `validate` / `sync` の fail-fast surface で継続して検出できなければならない。
- checked-in dogfooding parity は provider-side `install_root` authoritative assets と checked-in consumer-side agent-tooling files、および runtime fixture として使う checked-in `spec-dock/` scaffold が `spec-dock update` 後に収束することを要求する。
- issue-70 report の `handoff-validation-evidence` はこの issue の verification input として消費できなければならない。
- evidence は最終的に issue-71 report に集約し、少なくとも `tests/test_init_update.py`、runtime command tests、installed package smoke、`validate` / `sync` command execution の結果を辿れること。
- isolated installed package verification は `iss-00069` と同じく non-editable isolated install を使い、checkout fallback / `PYTHONPATH` / current working directory からの source tree fallback を禁止する。
- `sync --github` の closure evidence は hermetic runtime subprocess tests と fixture-driven stdout/stderr assertions を primary とし、手動コマンド実行は補助証跡に留める。

## 前提
- `iss-00069` が package parity を pass している。
- `iss-00070` が installer cutover / managed ownership を pass している。
- dogfooding repo の checked-in `.agents` / `.codex` / `.github` / `spec-dock/` は update 対象として存在する。

## 受け入れ条件
- AC-001:
  - Actor:
    - reviewer
  - Given:
    - `iss-00069` と `iss-00070` の handoff evidence が揃っている
  - When:
    - final verification suite を review する
  - Then:
    - `E-AC-002` / `E-AC-003` を閉じる evidence owner が this issue に集約されている
    - package parity prerequisite と installer cutover prerequisite がどの verification で消費されたか追跡できる
    - issue-71 report から checkout / installed package / checked-in dogfooding の 3 面 evidence を辿れる
  - 観測点:
    - issue-69 report
    - issue-70 report
    - issue-71 report

- AC-002:
  - Actor:
    - maintainer
  - Given:
    - local checkout で provider-side source と checked-in dogfooding workspace が存在する
  - When:
    - targeted regression suite と `spec-dock update` を実行する
  - Then:
    - `.agents`、`.codex`、`.github`、`.github/workflows` は provider-side `install_root` contract に再収束する
    - checked-in `spec-dock/` scaffold は runtime command verification を行う fixture surface として update 後に整合した状態へ収束する
    - checked-in dogfooding parity tests は pass する
    - user-authored unmanaged path が parity recovery の中で誤って prune されない
  - 観測点:
    - `tests/test_init_update.py`
    - checked-in filesystem assertions

- AC-003:
  - Actor:
    - maintainer
  - Given:
    - checked-in dogfooding workspace で runtime command surface を使える
  - When:
    - `./spec-dock/scripts/spec-dock validate`、`./spec-dock/scripts/spec-dock sync`、`./spec-dock/scripts/spec-dock sync --github` を実行する
  - Then:
    - install-shaped layout 前提でも各 command は fixture-driven subprocess tests 上で成功し、expected artifact / output contract を満たす
    - `validate` と `sync` は required artifact preflight を通る
    - `sync --github` でも hermetic test fixture 上で install-shaped contract と矛盾しない
  - 観測点:
    - runtime subprocess tests
    - command stdout / stderr assertions
    - generated artifact assertions

- AC-004:
  - Actor:
    - maintainer
  - Given:
    - runtime prerequisite を壊した fixture と `sync --force` fixture を用意する
  - When:
    - runtime tests を実行する
  - Then:
    - missing artifact / invalid prerequisite は `validate` / `sync` で fail-fast になる
    - `sync --force` は degraded path と warning surface を維持する
    - install-shaped contract への切替によって fail-fast / degraded semantics が変質しない
  - 観測点:
    - `tests/cli_runtime/test_validate.py`
    - `tests/cli_runtime/test_sync.py`
    - `tests/presentation_runtime/test_runtime_sync_s07.py`

- AC-005:
  - Actor:
    - maintainer
  - Given:
    - `iss-00069` / `iss-00070` が用意した isolated installed package surface があり、non-editable install で checkout fallback / `PYTHONPATH` / current working directory からの source tree fallback を使えない
  - When:
    - package-installed `spec-dock init` / `update` の final smoke を実行する
  - Then:
    - checkout fallback なしで cutover 後の current managed reflection が成立する
    - installed package surface の verification 結果は checkout-based verification と矛盾しない
    - package-installed smoke evidence は issue-71 report に集約される
  - 観測点:
    - isolated installed package smoke
    - target filesystem assertions
    - issue report evidence

## 例外・エッジケース
- EC-001:
  - 条件:
    - checked-in dogfooding workspace が古い mirror state を持つ
  - 期待:
    - `spec-dock update` 後に parity tests が green へ収束する
    - drift は report に before/after として残る
  - 観測点:
    - checked-in parity regression
    - issue report evidence

- EC-002:
  - 条件:
    - `sync --force` により degraded success を通す
  - 期待:
    - degraded warning surface は維持される
    - final verification では degraded path と normal success path を混同しない
  - 観測点:
    - runtime sync force tests
    - CLI text assertions

## 用語（ドメイン語彙）
- TERM-001:
  - final verification:
    - issue-69 / issue-70 prerequisite を消費し、epic acceptance を閉じるための checkout / installed package / checked-in dogfooding の総合検証。
- TERM-002:
  - checked-in dogfooding parity:
    - repo root に commit 対象として存在する `.agents` / `.codex` / `.github` / `spec-dock/` が provider-side source-of-truth と一致している状態。

## 未確定事項
- なし:
  - verification surfaces、closure owner、report evidence 集約方針はこの issue で固定する。
