---
種別: 要件定義書（Issue）
ID: "iss-00229"
タイトル: "Compose Profile Aware Planning Artifacts"
関連GitHub: ["#229"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
親: ["epic-00224", "init-local-00003"]
---

# iss-00229 Compose Profile Aware Planning Artifacts — 要件定義（何を、なぜ行うか）

## 目的
- Provisional / approved Assurance Contract に応じて、Issue の `design.md` / `plan.md` / `report.md` に必要な profile-aware planning sections を安全に合成する。
- Planning artifact の source binding が古くなった場合に、agent が古い Assurance に基づいて execution handoff へ進まないようにする。

## 背景・現状
- I01 で issue-local tracked `assurance.json` と `authorized_profile` / `lite_candidate` の分類基盤を導入した。
- I02 で `workflow status` / `workflow next` と fixed Skill kernel を導入し、`authorized_profile` を obligation authority として扱うようにした。
- しかし現時点では、Assurance Profile に応じて canonical planning artifacts へ必要 section を作る仕組みがなく、agent が毎回 template や長い workflow docs から必要 section を推測する必要がある。
- `assurance.json` は planning source artifacts の hash に binding されるが、requirement / design / plan の substantive change 後に古い contract のまま compose や実行へ進むことを防ぐ end-to-end gate が不足している。

## スコープ
- 必須:
  - Profile preset / fragment manifest を provider asset として定義する。
  - `design.md` / `plan.md` / `report.md` 用の managed profile sections を合成する。
  - Pristine scaffold には必要 section を full materialize できる。
  - 既存 substantive body は自動上書きしない。
  - 同じ input で二度 compose しても tracked diff を出さない。
  - `assurance.json` の source binding と現在の `requirement.md` / `design.md` / `plan.md` hash の不一致を stale として検出する。
  - stale / invalid / missing authority では compose と execution Runbook が実装開始を許可しない。
  - Provider source と dogfooding mirror の parity を維持する。
- 禁止:
  - Step worker routing、agent reasoning effort、context packet policy を実装しない。
  - GitHub PR review trigger / blocker policy を変更しない。
  - downgrade 時に既存 section を自動削除しない。
  - generated Runbook / projection を canonical authority として扱わない。
- 対象外:
  - Automatic Lite default の有効化。
  - 既存全 Issue の bulk backfill。
  - Cross-provider agent context transfer。

## 非交渉制約
- `authorized_profile` だけが planning artifact obligation の authority である。`lite_candidate` だけで section を削減してはならない。
- Escalation は単調追加である。強い profile から弱い profile への downgrade は自動 section deletion を行わない。
- Generated / managed section は stable markers を持つが、canonical source of truth は tracked `assurance.json`、canonical docs、accepted ADR、source binding である。
- Fragment manifest / composer / stale checker は typed boundary を持ち、Ruff / MyPy baseline を満たす。

## 前提
- `iss-00227` の Assurance Contract / classification runtime が完了している。
- `iss-00228` の state-aware Runbook / fixed Skill kernel / generated projection store が完了している。
- Epic ADR `Adaptive Assurance Contract Lite Authorization And Monotonic Escalation` により、Standard default、explicit Lite authorization、`authorized_profile` authority が固定済みである。

## 受け入れ条件
- AC-001 profile-aware materialization:
  - アクター: agent
  - 前提: active Issue に valid `assurance.json` があり、`authorized_profile` が `lite` / `standard` / `strict` / `critical` のいずれかである。
  - 操作: planning artifact compose command を実行する。
  - 期待結果: profile preset に応じた managed sections が `design.md` / `plan.md` / `report.md` へ追加される。
  - 観測点: composed artifact content、command JSON / text output、golden fixture。
- AC-002 idempotence:
  - アクター: agent
  - 前提: AC-001 の compose が一度成功済みである。
  - 操作: 同じ input で compose を再実行する。
  - 期待結果: `git status --short` に追加 diff が出ない。
  - 観測点: CLI runtime test、artifact diff。
- AC-003 no-overwrite:
  - アクター: agent
  - 前提: managed marker 内または近接 section に人間 / agent が substantive content を書いている。
  - 操作: compose を実行する。
  - 期待結果: substantive body は自動上書きされず、missing managed section の追加または preserve notice に留まる。
  - 観測点: fixture before/after、composer result warnings。
- AC-004 stale source binding:
  - アクター: agent
  - 前提: valid `assurance.json` 作成後に `requirement.md` / `design.md` / `plan.md` のいずれかが substantive change している。
  - 操作: `assurance compose`、`assurance verify`、または `workflow next issue-execution` を実行する。
  - 期待結果: source binding stale として invalid / blocked 扱いになり、compose output と execution handoff を許可しない。
  - 観測点: command exit code / JSON reason、stale artifact details、Runbook state / stop condition。
- AC-005 downgrade no deletion:
  - アクター: agent
  - 前提: より強い profile 用 section が既に存在し、その後より弱い profile contract で compose する。
  - 操作: compose を実行する。
  - 期待結果: 既存 section は削除されず、必要なら stale / escalation notice を追加する。
  - 観測点: before/after artifact、composer warnings。
- AC-006 provider / mirror parity:
  - アクター: maintainer
  - 前提: provider asset 変更後。
  - 操作: `uv run python -m spec_dock.cli update .` と parity diff を実行する。
  - 期待結果: provider templates / runtime と dogfooding mirror が一致する。
  - 観測点: parity diff no output、SpecDock validate。

## 例外・エッジケース
- EC-001 missing assurance:
  - 条件: active Issue に `assurance.json` がない。
  - 期待: compose は fail-closed し、`assurance classify --stage requirement` を案内する。
  - 観測点: command output / non-zero or blocked status。
- EC-002 invalid assurance:
  - 条件: `assurance.json` が JSON / schema / source binding 不整合で invalid。
  - 期待: compose と execution Runbook は obligation を減らさず、stale artifact を示して repair / reclassify を案内する。
  - 観測点: `assurance verify`、`workflow next`。
- EC-003 marker conflict:
  - 条件: artifact に壊れた managed marker、重複 marker、または閉じていない marker がある。
  - 期待: composer は対象 artifact を自動破壊せず、conflict を報告して停止する。
  - 観測点: composer result warnings/errors、artifact unchanged。

## 入力→出力例
- EX-001 standard profile:
  - 入力: `authorized_profile=standard` の `assurance.json` と pristine `design.md` / `plan.md` / `report.md`。
  - 出力: Standard profile の planning sections、step contract reminders、review gate sections が stable markers 付きで追加される。
- EX-002 explicit Lite profile:
  - 入力: explicit opt-in と evidence gate により `authorized_profile=lite` になった `assurance.json` と pristine artifacts。
  - 出力: Lite profile の planning sections が追加される。`lite_candidate=true` だけで Lite sections にはならない。
- EX-003 stale source:
  - 入力: `assurance.json` の source hash と現在の `requirement.md` / `design.md` / `plan.md` hash のいずれかが異なる。
  - 出力: `assurance compose` と `assurance verify` は invalid / stale reason を返し、`workflow next issue-execution` は execution-ready を返さない。

## 用語
- Profile preset:
  - `authorized_profile` ごとに planning artifact へ必要な section fragments を定義する policy。
- Managed section:
  - composer が stable marker で管理する Markdown section。手動編集された substantive body は自動上書きしない。
- Source binding stale:
  - `assurance.json` に保存された artifact hash が現在の canonical artifact と一致しない状態。

## 未確定事項
- なし。
