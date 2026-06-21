---
種別: disc
ID: "20260620t141318z-disc"
タイトル: "Doctor Tests Docs Migration"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-06-20"
親: ["iss-00222"]
関連: []
authority: "proposed"
derived_from:
  - "20260620t141316z-research-actions-only-pr-observation-viability-research.md"
  - "Deep Consultant risks/tests/doctor analysis 2026-06-20"
reflected_to:
  - "report.md Evidence Adoption Ledger"
---

# 20260620t141318z-disc Doctor Tests Docs Migration

## 位置づけ
- 用途: 集まった質問回答や調査をもとに、意思決定前の synthesis、選択肢、tradeoff、reflection proposal、ADR candidate triage、推奨反映先を整理する。
- authority default: `proposed`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は synthesis / reflection proposal / adoption target / ADR triage の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 人間から回答を引き出し、回答欄や未回答事項を管理する場合は `interview` を使う。
- 生ログや未整理の思考は `scratch`、事実確認や外部根拠は `research`、長期判断の固定は `adr` に分ける。
- この doc は proposal / synthesis であり、issue `report.md` の observed evidence ledger ではない。採否の最終証跡は canonical docs / ADR / `report.md` Evidence Adoption Ledger に昇格する。
- doc が大きくなりすぎたら、質問回答は `interview`、事実調査は `research`、raw capture は `scratch`、長期決定は `adr` へ分割する。

## 対象論点 (必須)
- 今回整理する論点:
  - Actions-only 方針を実装へ落とす際の doctor capability、テスト戦略、docs/skill migration。
- この synthesis が必要な理由:
  - 既存 runtime doctor と tests は旧設計の Checks/status/rollup capability を修復対象として固定しており、実装だけを変えると検証が旧仕様を再要求する。

## derived question sheets / research (必須)
- `interview`:
  - `20260620t140618z-interview-commit-statuses-policy-boundary.md`
- `research`:
  - `20260620t141316z-research-actions-only-pr-observation-viability-research.md`
- その他の根拠:
  - Deep Consultant risks/tests/doctor analysis。
  - Current tests:
    - `tests/cli_runtime/test_runtime_doctor_s04.py`
    - `tests/unit/infra/test_init_update.py`
  - Current runtime:
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/github_capability_cli.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/doctor.py`

## synthesis (必須)
- 合意済みのこと:
  - doctor core / gateway diagnostics は `check_runs_read`, `commit_statuses_read`, `status_check_rollup_read` を required capability として扱わない。
  - `actions_read` は PR observation CI 判定に必要な capability として扱う。
  - tests は forbidden call が発生したら失敗する形で書く。
  - historical discussions は書き換えず、current skill/docs/tests を新方針へ更新する。
- 未合意 / 未確定のこと:
  - Capability enum から旧 capability を削除するか、他用途互換のため残して doctor/PR observation から外すか。
  - provider-side と dogfooding mirror の更新同期手順。
- source-grounded に解決できたこと:
  - 現行 tests には旧仕様を固定するものが複数あるため、削除ではなく反転/置換が必要。
  - static scan は provider-side current assets を対象にし、historical `spec-dock/initiatives/**` は除外する必要がある。

## 選択肢 / tradeoff (必須)
- Option A: doctor/tests/docs を Actions-only contract に同期する（推奨）
  - Pros:
    - 実装・検証・運用文言が一致する。
    - future regression を fake-gh と static scan で防げる。
    - Checks/status permissions を修復対象から外せる。
  - Cons:
    - 既存 test の大きめの書き換えが必要。
    - status-only / external CI ユーザーへの migration note が必要。
- Option B: implementation だけ Actions-only にし、doctor/tests は最小修正に留める
  - Pros:
    - 初期差分は小さい。
  - Cons:
    - doctor が不要な permission を要求し続ける。
    - tests が旧 fallback を再導入する圧力になる。
    - skill/docs と実装が乖離する。

## reflection proposal (必須)
- canonical docs / workflow / template / skill guidance へ反映すべき候補:
  - doctor capability probe:
    - PR observation required capability は repo/PR metadata + Actions read。
    - Checks/status/rollup permission failure は repair inventory に載せない。
  - tests:
    - fake `gh` が `/check-runs`, `/status`, `statusCheckRollup`, `gh pr checks` を検出したら fail。
    - Actions green は pass、かつ `ci_coverage_limited_to_github_actions` を出さない。
    - zero Actions + green legacy check/status は pass しない。
    - jobs unavailable で check-runs fallback しない。
    - Actions API unavailable は unknown/human gate。
    - doctor は Actions read を要求し、Checks/statuses/status rollup を要求しない。
    - merge-preparer wording は「all required checks passed」と主張しない。
  - docs/skill:
    - “supplemental Checks/statuses/rollup” wording を削除する。
    - “Actions-only CI observation; external/non-Actions checks intentionally not observed” に更新する。
- まだ proposal に留める理由:
  - 実装フェーズで exact test names / assertion shape を既存 test structure に合わせて固定する必要がある。

## adoption target / 採用先候補 (必須)
- `requirement.md`:
  - Non-negotiable constraints and acceptance criteria。
- `design.md`:
  - doctor/capability design、test strategy、migration wording。
- `plan.md`:
  - step-by-step implementation and verification contract。
- `ADR`:
  - 不要。
- `report.md` Evidence Adoption Ledger:
  - EAL-DEEP-004。

## ADR triage / ADR candidate triage (必須)
- ADR candidate か:
  - no
- hard to reverse:
  - no
- surprising without context:
  - yes
- real tradeoff:
  - yes
- ADR 化しない場合の反映先:
  - `design.md` / `plan.md`

## 推奨案 (必須)
- Option A を採用する。Actions-only contract は runtime collector だけでなく doctor、tests、skill docs、merge-preparer wording まで同期しないと、旧 forbidden surface が regression として戻る。

## 推奨反映先 (必須)
- `requirement.md`:
  - Required capability は Actions read。Checks/statuses permissions は不要。
- `design.md`:
  - doctor capability update、test matrix、migration notes。
- `plan.md`:
  - S01 collector tests、S02 wait/snapshot tests、S03 doctor/tests/docs、S04 final scans。
- `ADR`:
  - なし。
- `report.md` Evidence Adoption Ledger:
  - EAL-DEEP-004。

## 未採用 / deferred 理由 (必須)
- 未採用:
  - Option B: implementation と validation contract が分裂する。
- deferred:
  - enum 削除 vs 非使用維持は design の compatibility section へ defer。

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - doctor capability migration。
  - test rewrite list。
  - docs/skill wording migration。
  - static scan scope。
- 追加で作る discussion docs:
  - なし。
