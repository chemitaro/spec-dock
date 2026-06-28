---
種別: リサーチ
ID: "20260628t052300z-research"
タイトル: "Issue-local assurance contract を .assurance.json へ改名する分析"
状態: "draft"
作成者: "codex"
作成日: "2026-06-28"
親: ["iss-00244", "epic-00224"]
参照:
  - "../requirement.md"
  - "../design.md"
  - "../plan.md"
---

# Issue-local assurance contract を .assurance.json へ改名する分析

## 要約

`assurance.json` は Issue の品質プロファイル、source binding、stale detection、workflow readiness のための machine-readable contract である。これは requirement / design / plan / report のように agent が直接編集・読解する一次文書ではなく、runtime が管理する metadata に近い。

したがって、Issue directory の可視的な文書群から一段下げ、`.meta.json` に近い扱いとして `.assurance.json` へ改名するのが望ましい。

この変更は単なる文書表記の修正ではない。現行 runtime / tests / docs / dogfooding artifacts が `assurance.json` を前提にしているため、canonical path の変更、旧 path の扱い、既存 fixture / dogfooding artifact の rename、CLI help / docs の更新を一貫して行う必要がある。

## 現状

### Runtime

- provider authority:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/assurance_store.py`
  - `read_contract()` / `_contract_write_path()` が `target.issue_dir / "assurance.json"` を使う。
- dogfooding installed copy:
  - `spec-dock/scripts/spec_dock_runtime/infra/assurance_store.py`
  - 同じく `assurance.json` を使う。
- CLI help:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/assurance.py`
  - `spec-dock/scripts/spec_dock_runtime/commands/assurance.py`
  - `--dry-run` help が `writing assurance.json` と説明している。
  - `cli/parser.py` も `write assurance.json` と説明している。

### Tests

- `tests/cli_runtime/test_assurance.py`
- `tests/cli_runtime/test_assurance_compose.py`
- `tests/cli_runtime/test_workflow.py`
- `tests/cli_runtime/test_workflow_context_routing.py`
- `tests/unit/infra/test_assurance_store.py`
- `tests/unit/application/test_assurance.py`

上記に `assurance.json` fixture / assertion が存在する。

### Dogfooding artifacts

Epic `epic-00224` 配下には少なくとも次の Issue-local `assurance.json` が存在する。

- `iss-00228-compile-state-aware-workflow-runbooks-and-fixed-skill-kernels/assurance.json`
- `iss-00229-compose-profile-aware-planning-artifacts/assurance.json`
- `iss-00230-compile-step-assurance-agent-routing-and-context-policy/assurance.json`
- `iss-00231-inject-trusted-base-branch-codex-review-policy/assurance.json`
- `iss-00232-enforce-blocker-centric-pr-repair-and-rereview/assurance.json`
- `iss-00233-roll-out-adaptive-workflow-with-legacy-compatibility-and-telemetry/assurance.json`
- `iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/assurance.json`

### Documentation

Epic / Issue docs には `assurance.json` という名称が広く残っている。過去の完了 Issue / discussion の歴史的記録は、原則として書き換え対象ではない。

## 問題

### P1: Agent-facing document surface に metadata file が混ざる

Issue directory では `requirement.md`、`design.md`、`plan.md`、`report.md` が agent / human が直接読む canonical document である。一方 `assurance.json` は runtime が管理する contract であり、agent が自由に編集すべき一次文書ではない。

可視的な `assurance.json` という名前は、agent が requirement / design / plan と同列の編集対象と誤認する余地を残す。

### P2: `.meta.json` との扱いが揃っていない

SpecDock では machine-readable metadata を dotfile 的に扱う設計がある。Assurance contract も性質としては metadata / contract に近く、`.assurance.json` の方が位置づけを表現しやすい。

### P2: rename は runtime / test / existing artifacts の一貫性が必要

Store path だけを変えると既存 dogfooding Issue が missing contract になり、workflow readiness / validation が変わる。Tests だけを変えると runtime と docs が drift する。したがって、canonical path、旧 path の扱い、既存 artifact migration を同じ追加作業で閉じる必要がある。

## 理想形

- Canonical assurance contract path は Issue-local `.assurance.json` とする。
- Runtime は `.assurance.json` を read/write/verify の authority とする。
- `assurance classify` は non-dry-run 時に `.assurance.json` を作成する。
- `assurance show` / `assurance verify` / guidance / compose / workflow readiness は `.assurance.json` を参照する。
- `assurance.json` は新規 write しない。
- 既存 `assurance.json` は移行対象とし、dogfooding workspace 内の canonical artifacts は `.assurance.json` へ rename する。
- 旧 `assurance.json` が残っている場合の扱いは明示する。
  - 推奨: `.assurance.json` がなく `assurance.json` だけがある場合は `legacy_assurance_contract_path` として migration-required / invalid 相当の diagnostics を返し、current authority として silently accept しない。
  - 理由: 旧 path を silently read すると、改名後も agent / user が古い path を使い続けるため、rename の意味が弱くなる。
- Historical discussions / completed Issue docs は必要最小限の参照に留め、実装時に広範な過去文書 rewrites はしない。

## 選択肢

### Option A: hard cutover

- `.assurance.json` のみを canonical とする。
- `assurance.json` は read/write しない。
- 既存 dogfooding artifacts は rename する。
- Pros:
  - authority が明確。
  - agent が旧 path を使い続ける余地が小さい。
  - Issue 244 の hard cutover 方針と合う。
- Cons:
  - 既存 checkout に旧 file が残ると migration が必要。
- 判断:
  - 採用する。ただし diagnostics は親切にする。

### Option B: compatibility read fallback

- `.assurance.json` がなければ `assurance.json` を読む。
- Pros:
  - 既存 Issue が壊れにくい。
- Cons:
  - 旧 path が authority として生き続ける。
  - hidden metadata 化の目的が弱くなる。
- 判断:
  - 今回は採用しない。

### Option C: dual write

- `.assurance.json` と `assurance.json` の両方を書く。
- Pros:
  - migration 期間の互換性は高い。
- Cons:
  - authority が二重化し、drift risk が増える。
  - agent-facing surface から `assurance.json` が消えない。
- 判断:
  - 採用しない。

## 修正方針

### Runtime

- `AssuranceStore` の canonical contract filename を `.assurance.json` に変更する。
- `read_contract()` / `write_contract()` / `ensure_contract_writable()` / `_contract_write_path()` を `.assurance.json` に寄せる。
- `.assurance.json` が missing で `assurance.json` が存在する場合は、legacy path diagnostics を返す。
  - 実装名例:
    - status: `invalid` または `missing`
    - reason: `legacy_assurance_contract_path`
    - details: `rename assurance.json to .assurance.json`
  - どちらの status にするかは実装時に tests と既存 missing semantics を見て確定する。
- Symlink / outside issue guard は `.assurance.json` に対して維持する。

### CLI / presentation / docs

- CLI help の `assurance.json` 表記を `.assurance.json` に変更する。
- Current docs / issue planning docs / workflow docs の active contract 表記を `.assurance.json` に変更する。
- Historical discussions / completed issue records は、必要がなければ変更しない。

### Tests

- Existing tests の path fixture を `.assurance.json` に変更する。
- New tests:
  - classify writes `.assurance.json` and not `assurance.json`
  - show/verify reads `.assurance.json`
  - malformed `.assurance.json` fails invalid
  - missing `.assurance.json` with legacy `assurance.json` returns migration diagnostics
  - symlink guard applies to `.assurance.json`
  - dogfooding issue artifacts no longer include `assurance.json`

### Dogfooding artifacts

- Active / relevant Issue-local `assurance.json` を `.assurance.json` に rename する。
- `rg --files --hidden spec-dock | rg '(^|/)assurance\\.json$'` で current dogfooding workspace に旧 path が残らないことを確認する。
- 過去文書内の文字列 `assurance.json` は歴史的文脈として残し得るが、current authority docs / tests / runtime は `.assurance.json` に揃える。

## 受け入れ条件案

- AC-HA-001: Runtime read/write canonical path is `.assurance.json`.
- AC-HA-002: `assurance classify --stage requirement` creates `.assurance.json` and does not create `assurance.json`.
- AC-HA-003: `assurance show` / `assurance verify` use `.assurance.json`.
- AC-HA-004: Existing dogfooding Issue-local `assurance.json` artifacts are renamed to `.assurance.json`.
- AC-HA-005: Legacy `assurance.json` alone is not silently accepted as current authority and returns explicit migration diagnostics.
- AC-HA-006: CLI help / current docs / skill-facing guidance refer to `.assurance.json`.
- AC-HA-007: Focused tests and validation pass.

## リスクと緩和

- リスク: Existing Issue が missing contract 扱いになる。
  - 緩和: dogfooding artifacts を rename し、legacy path diagnostics を追加する。
- リスク: Historical docs の大量置換で意図しない履歴改変が起きる。
  - 緩和: current authority docs / runtime / tests に限定し、historical discussion は原則変更しない。
- リスク: Dotfile が `rg --files` の default から漏れる。
  - 緩和: tests / inspection では `rg --files --hidden` を使う。
- リスク: `.assurance.json` を agent が全く見なくなり、source binding stale の理由が分かりにくくなる。
  - 緩和: CLI output / guidance では contract path を明示し、必要な diagnostics は表示する。

## 結論

この Issue の追加作業として、Issue-local assurance contract の canonical path を `assurance.json` から `.assurance.json` へ hard cutover する。

旧 `assurance.json` は新規 write せず、current authority として silently accept しない。Dogfooding workspace の既存 contract artifacts は `.assurance.json` へ rename し、runtime / tests / current docs / CLI help を `.assurance.json` に揃える。
