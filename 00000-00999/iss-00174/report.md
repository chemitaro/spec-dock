---
種別: 実装報告書（Issue）
ID: "iss-00174"
タイトル: "Refine PR Observation Two Stage Progress Output"
関連GitHub: ["#174"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-08"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00067", "init-local-00003"]
---

# iss-00174 Refine PR Observation Two Stage Progress Output — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

> `report.md` は観測証跡台帳（observed evidence ledger）の scaffold です。planned requirements、evidence destination、closure 条件は `plan.md` が持ち、この文書は実際の Red / Green / Refactor evidence、発見された tests、closure delta、reviewer status、commit/no-op evidence を記録する evidence slot です。workflow / compliance authority は skills、docs、accepted ADRs、reviewer gates に置きます。

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger / 必須）

`report.md` は実装中・文書更新中に発生した material な仕様解釈、判断、plan 逸脱、tradeoff、open question、promotion / follow-up を記録する audit trail でもある。worker の raw note や作業 transcript を貼る場所ではなく、orchestrator が source docs、diff、tests、reviewer output と照合して issue-level の canonical entry に統合する。

Material な判断がない場合もこの section は残し、次を明示する。

- No material interpretation changes.
- No decision entries.

Ledger entry は次の契約値を使う。

- `Status`: `open` / `resolved` / `superseded`
- `Type`: `interpretation` / `scope` / `implementation` / `compatibility` / `test-strategy` / `operation` / `deviation` / `follow-up`
- `Disposition`: `applied` / `rejected` / `promoted_to_design` / `promoted_to_adr` / `promoted_to_plan` / `converted_to_followup` / `deferred` / `no_action` / `superseded`

完了時の意味論（completion semantics）:
- issue completion 前に `Status=open` の entry を残してはならない。
- `Status=resolved` は `Disposition`、evidence、必要な follow-up を持つ。
- `Status=superseded` または `Disposition=superseded` は置換先 entry ID を持つ。
- `Disposition=promoted_to_design` / `promoted_to_adr` / `promoted_to_plan` は昇格先 artifact と evidence を持つ。
- `Disposition=converted_to_followup` は follow-up issue / discussion / ADR candidate の参照を持つ。
- `Disposition=deferred` は scope 外である理由、blocking でない根拠、revisit 条件を持つ。
- `Disposition=no_action` は issue-local な判断で追加対応不要である理由を持つ。将来も効く durable decision を `report.md` だけに閉じ込めてはならない。

Disposition ごとの必須証跡:
- `applied`: 変更した artifact / 実装証跡と、issue-local 適用で十分な理由。
- `rejected`: 却下した選択肢、理由、blocking impact が残らない根拠。
- `promoted_to_design` / `promoted_to_adr` / `promoted_to_plan`: 昇格先 artifact 参照と証跡。
- `converted_to_followup`: follow-up issue / discussion / ADR candidate 参照と blocking / non-blocking の分類。
- `deferred`: scope-out 理由、non-blocking の根拠、revisit 条件。
- `no_action`: 判断が issue-local で durable ではない理由。
- `superseded`: 置換先 entry ID と置換理由。

| 識別子（ID） | 状態（Status） | 種別（Type） | 起票元（Raised By） | 契機 / 差分（Gap） | 検討した選択肢 | 判断 / 解釈 | 根拠（Rationale） | 処置（Disposition） | 証跡（Evidence） | フォローアップ（Follow-up） |
|---|---|---|---|---|---|---|---|---|---|---|
| D-001 | resolved | scope | user / orchestrator | `iss-00170` の main PR は merge 済みだが、polling progress 表示はユーザー意図と異なるため後続 issue へ切り出された。 | A: `iss-00170` へ追加実装を戻す; B: 新 issue `iss-00174` で progress 表示改善として扱う | B を採用する。`iss-00174` は `github-pr-observation` wait wrapper の stderr progress 二段階表示、quiet reset semantics、focused tests を扱う follow-up issue とする。 | PR #173 / GitHub #170 は close 済みであり、追加改善は scope / review / delivery を分離した方が安全で追跡しやすい。 | applied | `requirement.md`; `discussions/20260608t024500z-research-progress-line-two-stage-status-analysis.md`; `discussions/20260608t030500z-disc-progress-line-two-stage-design-proposal.md` | none |
| D-002 | resolved | interpretation | user interview / orchestrator | progress line の `comments=N` が、PR 全体コメント、Codex authored 全件、trigger-window signal、unresolved thread のどれを指すかで要件が変わる。 | A: PR 全体コメント件数; B: Codex authored 全件; C: `@codex review` trigger 以後の今回の観測窓で捕捉した Codex review comments / review signals 件数 | C を採用する。古い PR 全体コメントや過去 unresolved thread は `comments=N` へ毎回積み上げない。 | ユーザー回答が Yes で確定済み。目的は「今回のレビューが 0 -> 1 -> 2 と進んでいる」ことを読むこと。 | applied | `discussions/20260608t025500z-interview-progress-review-comment-count.md`; `requirement.md` | design / plan で projection と tests を具体化する |
| D-003 | resolved | implementation | code-reviewer / spec-reviewer | 初回実装では `review_progress_counts` が `trigger_command` と `outside_trigger_window` だけを除外しており、`trigger_unknown` / timestamp unavailable / non-Codex signal が `comments=N` と quiet reset に混入し得た。 | A: 表示だけ `comments=N` を絞る; B: `comments=N` と semantic fingerprint の review signal projection を同じ current trigger-window Codex-authored signal に揃える | B を採用する。`trigger_command`、任意の `omitted_reason`、`codex_authored is not True`、対象外 `kind` は progress comments と fingerprint signal から除外する。 | `comments=N` の定義は「今回の観測窓で捕捉した Codex review comments / review signals」であり、表示だけでなく quiet reset も同じ意味論に揃える必要がある。 | applied | `/private/tmp/iss-00174-code-review-1.json`; `/private/tmp/iss-00174-spec-review-implementation-1.json`; `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`; `tests/unit/infra/test_init_update.py` | fresh code-reviewer / qa-reviewer / spec-reviewer pass を取得する |
| D-004 | resolved | test-strategy | GitHub Actions / dev-coder | PR 作成後の full provider suite で、新規 issue `.meta.json` が checked-in dogfooding meta snapshot に未登録だったため `test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json` が fail した。 | A: issue `.meta.json` を除外する; B: snapshot tuple と depends_on baseline へ `iss-00174` を追加する | B を採用する。新規 dogfooding issue は checked-in snapshot の一部なので、path set と `depends_on=[]` baseline に登録する。 | CI failure は今回追加した issue artifact 由来であり、実装挙動ではなく dogfooding snapshot 契約の更新漏れだった。 | applied | `gh run view 27118295527 --log-failed`; `tests/unit/infra/test_init_update.py`; `uv run pytest tests/unit/infra/test_init_update.py -k 'checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json or pr_observation_wait or pr_review or pr_observation' -q` -> `80 passed, 212 deselected` | amended commit / rerun PR checks |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | research / discussion | `requirement.md` | progress line の現状、目標二段階表示、quiet reset、テスト観点を要件へ昇格するための主要 evidence として十分。 | `discussions/20260608t024500z-research-progress-line-two-stage-status-analysis.md`; `requirement.md` | fresh `spec-reviewer` review |
| EAL-002 | adopted | interview | `requirement.md` | `comments=N` の定義はユーザー意図 blocker だったため、回答済み interview を要件の非交渉制約・受け入れ条件へ反映した。 | `discussions/20260608t025500z-interview-progress-review-comment-count.md`; `requirement.md` | fresh `spec-reviewer` review |
| EAL-003 | partially_adopted | discussion | `requirement.md` | design proposal / implementation plan draft は要件粒度に必要な範囲のみ採用し、projection structure や optional field drop order などの詳細は次の design / plan へ残した。 | `discussions/20260608t030500z-disc-progress-line-two-stage-design-proposal.md`; `discussions/20260608t031000z-disc-progress-line-two-stage-implementation-plan.md`; `requirement.md` | design authoring で再採用判断 |
| EAL-004 | adopted | system-architect discussion draft | `design.md` | system-architect draft は、既存 collector payload を増やさず wait wrapper 内 projection で二段階 progress / quiet reset / stdout boundary / provider-mirror parity を整理しており、approved requirement と整合する。 | `discussions/20260608t043253z-disc-system-architect-progress-line-two-stage-design.md`; `design.md` | fresh `spec-reviewer` review |
| EAL-005 | adopted | implementation-planner discussion draft | `plan.md` | implementation-planner draft は、approved design の dependency order を tests -> provider implementation -> fingerprint alignment -> mirror parity -> docs/final gates に分解し、closure ids、delegation、review gates、rollback / compatibility を実行契約へ落とし込んでいる。初回 plan review の P1 指摘は closure index / 具体テストケース / S02-S04 delegation contract の補強で解消済み。 | `discussions/20260608t044318z-disc-implementation-planner-progress-line-two-stage-plan.md`; `plan.md`; `/private/tmp/iss-00174-plan-spec-review-1.json`; `/private/tmp/iss-00174-plan-spec-review-2.json` | proceed to implementation execution |
| EAL-006 | adopted | dev-coder implementation + reviewer findings | source / tests / `report.md` | dev-coder 実装は approved plan の provider-first / mirror parity / focused regression 方針に従い、初回 code/spec reviewer の `comments=N` 境界指摘も追加修正で取り込んだ。 | `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`; `.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`; `tests/unit/infra/test_init_update.py`; `uv run pytest tests/unit/infra/test_init_update.py -k 'pr_observation_wait or pr_review or pr_observation' -q` -> `79 passed, 213 deselected` | fresh final reviewer gates |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | Primary objective is better long-running PR observation progress readability without changing stdout final JSON authority. | Secondary requirements include provider/mirror parity, no new GitHub API calls for progress only, and focused regression tests. | low | passed by fresh `spec-reviewer` (`/private/tmp/iss-00174-requirement-spec-review-2.json`) |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | active issue docs; parent epic requirement; progress research; answered interview; design proposal; implementation plan draft; provider wait script; tests grep | `comments=N` definition answered in `discussions/20260608t025500z-interview-progress-review-comment-count.md`; no new blocking user question | adopted into `requirement.md`; first review P2 findings fixed; requirement marked approved | passed (`/private/tmp/iss-00174-requirement-spec-review-2.json`, findings=[]) | no | promote to design authoring |
| design | approved requirement; system-architect discussion draft; current provider wait script; checks / review collectors; focused test surface in `tests/unit/infra/test_init_update.py` | no open question; `comments=N` already answered; collector changes are non-default fallback only | adopted into `design.md`; design marked approved after fresh reviewer pass | passed (`/private/tmp/iss-00174-design-spec-review-1.json`, findings=[]) | no | promote to plan authoring |
| plan | approved requirement/design; implementation-planner discussion draft; issue-plan authoring semantics; workflow_issue execution/reviewer/completion policy | no open question; amendment triggers are recorded for implementation-time discoveries | adopted into `plan.md`; first review P1 findings fixed; plan marked approved | passed (`/private/tmp/iss-00174-plan-spec-review-2.json`, findings=[]) | no | promote to implementation execution |

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）
- 委任 authoring の使用:
  - used / not used
- 未使用の場合:
  - manual authoring path / 委任ドラフトを昇格証跡として使っていない理由。
- lifecycle state（契約値）:
  - `requested`, `produced`, `integrated`, `partially_integrated`, `rejected`, `superseded`, `blocked`, `stale`
- 昇格不可 state:
  - `stale`, `rejected`, `superseded`, `blocked`
- 標準出力先:
  - 対象 scope の `discussions/` direct child にある flat Markdown
  - filename: `<ts>-<kind>-<slug>.md` または same-second collision 用 `<ts>-<nn>-<kind>-<slug>.md`
- 軽量 provenance:
  - `created_by_role`, `scope_id`, `source_paths`, `intended_targets`, `adoption_status: unreviewed`, `reflected_to: []`, `diff_guard_result`, fallback decision, report evidence destination, adoption ledger note
  - 互換 label: source artifacts, draft artifact path, status, integration result, rejected portions, blockers, reviewer result, promotion decision
- 禁止 self-claim:
  - `authority: accepted`, `adoption_status: adopted`, non-empty `reflected_to`, reviewer pass, phase completion, implementation readiness
- 禁止 wildcard token:
  - `*`, `grants.*`, `all`
- 標準必須にしない field:
  - task manifest hash, Permission Profile hash, session invocation hash, probe run id, session hash
- historical note:
  - 既存 `iss-00126` などの manifest/Profile/probe/session artifacts は grandfathered evidence として残し、削除・rename・validation failure 化しない。

| ロール（created_by_role） | 範囲（scope_id） | ドラフトパス（discussion draft path） | 参照元（source_paths） | 予定反映先（intended_targets） | 採用状態（adoption_status） | 反映先（reflected_to） | 差分ガード結果（diff_guard_result） | 統合結果 | 採用しなかった部分 | ブロッカー | レビュー結果（reviewer result） | 昇格判断（promotion decision） |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| system-architect | iss-00174 | `discussions/20260608t043253z-disc-system-architect-progress-line-two-stage-design.md` | `requirement.md`; progress research; interview; design proposal; implementation plan draft; provider wait script; snapshot / CI / review collectors; `tests/unit/infra/test_init_update.py` | `design.md`; `plan.md`; provider / mirror wait script; focused tests | integrated | `design.md`; `report.md` | passed (`git diff --check`) | projection boundary, two-stage rendering, quiet reset semantics, stdout/stderr boundary, provider/mirror parity, and test strategy were adopted into canonical design | none | none | passed (`/private/tmp/iss-00174-design-spec-review-1.json`, findings=[]) | design approved; promote to plan authoring |
| implementation-planner | iss-00174 | `discussions/20260608t044318z-disc-implementation-planner-progress-line-two-stage-plan.md` | approved `requirement.md`; approved `design.md`; `report.md`; system-architect draft; prior implementation plan draft; provider / mirror wait script; tests; issue-plan / workflow docs | `plan.md`; `report.md`; provider / mirror wait script; focused tests | integrated | `plan.md`; `report.md` | passed (`git diff --check -- <new discussion>`) | step slicing, closure index, delegation contracts, review gates, rollback/compatibility, docs impact, and final quality gate were adopted into canonical plan; first reviewer findings were incorporated before approval | none | none | passed (`/private/tmp/iss-00174-plan-spec-review-2.json`, findings=[]) | plan approved; promote to implementation execution |

### 委任ドラフトの失敗モード（Delegated Draft Failure Modes）
| 失敗モード | 期待される判定 | 許可される次アクション | レポート証跡の記録先（report evidence destination） | 昇格可否 |
|---|---|---|---|---|
| 同意なし（missing consent） | blocked / incomplete | 範囲付き同意を取得する、または手動 authoring に戻す | この section | ineligible |
| 前段 reviewer pass 不足 / stale（missing/stale previous reviewer pass） | blocked / incomplete | レビューゲートを再実行する（rerun reviewer gate） | レビューゲート証跡（Reviewer Gate Status / Final Spec Review Gate） | ineligible |
| 設計中の要件 gap（requirement gap during design） | blocked / incomplete | requirement phase へ戻す | 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger） | ineligible |
| 計画中の設計 gap（design gap during plan） | blocked / incomplete | design phase へ戻す | 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger） | ineligible |
| ロール利用不可（role unavailable） | blocked / manual path | 利用不可を記録し、妥当なら手動で続行する | この section | ineligible |
| 禁止行為の試行（forbidden action attempt） | rejected | ドラフトを破棄し incident を記録する | この section / decision ledger | ineligible |
| 古いドラフト（stale draft） | stale | 再生成または差分調整する | この section | ineligible |
| 置換済みドラフト（superseded draft） | superseded | 置換先ドラフトを参照する | この section | ineligible |
| 委任使用主張に対する証跡不足（missing draft evidence when delegated use is claimed） | incomplete | 証跡を追加する、または委任使用 claim を外す | この section | ineligible |
| reviewer 利用不可 / 拒否 / waiver / provisional（reviewer unavailable/denied/waived/provisional） | blocked / incomplete | fresh な passed reviewer を取得する、または昇格なしの risk acceptance を記録する | レビューゲート証跡（Reviewer Gate Status / Final Spec Review Gate） | ineligible |

## 実装サマリー (任意)
- `wait_pr_observation.sh` の stderr progress を二段階表示へ拡張し、CI 実行中は `checks=done/total ok/run/pend/fail`、review 観測中は current trigger-window Codex signal に基づく `comments=N` を出すようにした。
- quiet reset / stable 判定の semantic fingerprint も CI progress count と review progress projection に揃え、非 Codex signal、`trigger_unknown`、timestamp unavailable、古い review signal が progress と quiet reset を汚さないようにした。
- provider script と dogfooding mirror script は exact match に同期し、focused regression tests を追加・更新した。

## 実装記録（セッションログ） (必須)

### セッションログ（2026-06-08）

#### 対象
- Step: S01, S02, S03, S04, S90, S99
- AC/EC: AC-001..AC-010, EC-001..EC-008
- 計画上の出典（Planned source）:
  - `plan.md` section: 仕様固定クロージャ索引、S01-S04 実装ステップ、S90/S99 final gates
  - closure ids: cl-ci-detail, cl-ci-quiet, cl-ci-compact, cl-review-detail, cl-review-quiet, cl-review-human-gate, cl-progress-none, cl-boundary, cl-truncation, cl-zero-check, cl-skipped-neutral, cl-failed-compact, cl-old-thread-isolation, cl-trigger-unknown, cl-timeout-rendering, cl-raw-body-stability, cl-provider-mirror-parity, cl-bash-compat, cl-docs-impact, cl-final-quality

#### 実施内容
- dev-coder に S01-S04 の実装を委任した。
- provider `wait_pr_observation.sh` に CI / review progress projection と二段階 progress rendering を追加した。
- `semantic_fingerprint` に CI progress と review progress projection を含め、同じ coarse status でも job count / review count が進むと quiet がリセットされるようにした。
- 初回 code-reviewer / spec-reviewer 指摘を受け、review progress signal を `trigger_command` ではない、`omitted_reason` を持たない、`codex_authored is True`、かつ `pull_review` / `pull_review_comment` / `issue_comment` のみに限定した。
- provider script を `.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh` へ同期し、provider/mirror parity を確認した。
- focused regression tests に CI progress、terminal compact、human gate、review comments progression、non-Codex / trigger unknown / timestamp unavailable noise isolation、stderr/stdout boundary、line budget、`--progress none` を追加・更新した。

#### 実行コマンド / 結果
```bash
bash -n src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh
# passed

bash -n .agents/skills/github-pr-observation/scripts/wait_pr_observation.sh
# passed

diff -u src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh .agents/skills/github-pr-observation/scripts/wait_pr_observation.sh
# passed: empty diff

git diff --check
# passed

uv run pytest tests/unit/infra/test_init_update.py -k 'pr_observation_wait or pr_review or pr_observation' -q
# 79 passed, 213 deselected
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S01/S02 | Green | focused pytest で二段階 progress rendering を検証する | CI detailed / terminal compact / review detailed / human gate / progress none / boundary / truncation tests が pass | `uv run pytest tests/unit/infra/test_init_update.py -k 'pr_observation_wait or pr_review or pr_observation' -q` | pass | `79 passed, 213 deselected` |
| S03 | Green | quiet reset が CI / review progress count 変化で動き、body-only / old-noise では過剰に動かない | CI `latest_change_poll`、review `latest_change_poll`、non-Codex / omitted signal で `quiet=1/2` 継続を確認 | focused pytest | pass | code/spec reviewer 指摘後、fingerprint も progress projection に揃えた |
| S04 | Inspect | provider / mirror parity と Bash syntax | provider/mirror `bash -n` pass、`diff -u` empty | `bash -n`; `diff -u` | pass | mirror は provider と exact match |
| S90 | Inspect | docs impact を判断する | user-facing docs / README / workflow / skill text の更新不要、issue-local report のみ更新 | diff inspection | approved-no-op | script behavior と tests の issue-local 変更で完結 |
| S99 | Review | final reviewer gates | 初回 code/spec/QA fail 指摘は実装修正と report 更新で対応済み。fresh code-reviewer / qa-reviewer / spec-reviewer は pass。 | reviewer outputs + report | pass | `/private/tmp/iss-00174-code-review-2.json`; `/private/tmp/iss-00174-qa-review-2.json`; `/private/tmp/iss-00174-spec-review-implementation-3.json` |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S01/S02/S03 | `trigger_unknown` / timestamp unavailable / non-Codex post-trigger signal が `comments=N` と quiet reset に混入するリスク | code-reviewer / spec-reviewer | `review_progress_signal_items` を追加し、comments と fingerprint の signal projection を current trigger-window Codex-authored signal に限定。focused pytest fixture にノイズ poll を追加した。 | cl-review-detail, cl-review-quiet, cl-old-thread-isolation, cl-trigger-unknown | no | `tests/unit/infra/test_init_update.py`; focused pytest pass |
| S99 | 新規 dogfooding issue `.meta.json` が checked-in meta snapshot baseline に未登録となり full provider suite が fail するリスク | GitHub Actions / dev-coder | `_CHECKED_IN_DOGFOODING_META_JSON_PATHS` と `_CHECKED_IN_DOGFOODING_DEPENDS_ON_BY_META_PATH` に `iss-00174` を追加した。 | cl-final-quality | no | `uv run pytest tests/unit/infra/test_init_update.py -k 'checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json or pr_observation_wait or pr_review or pr_observation' -q` -> `80 passed, 212 deselected` |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S01/S02 | cl-ci-detail, cl-ci-compact, cl-review-detail, cl-review-human-gate, cl-progress-none, cl-boundary, cl-truncation, cl-zero-check, cl-skipped-neutral, cl-failed-compact, cl-old-thread-isolation, cl-trigger-unknown, cl-timeout-rendering | provider wait wrapper が二段階 progress と境界条件を満たす | focused pytest `79 passed, 213 deselected`; `bash -n` provider pass | pass | `comments=N` は current trigger-window Codex-authored signal のみ |
| S03 | cl-ci-quiet, cl-review-quiet, cl-raw-body-stability | semantic fingerprint / quiet reset が progress count 変化に追随し、不要な body/noise では過剰 reset しない | focused pytest pass。review noise poll で `comments=0` かつ `quiet=1/2` を確認 | pass | fingerprint の review signal は progress projection に合わせた |
| S04 | cl-provider-mirror-parity, cl-bash-compat | provider/mirror parity と shell syntax | `diff -u` empty; both `bash -n` pass | pass | shipped provider と dogfooding mirror を同期 |
| S90 | cl-docs-impact | docs impact が更新済みまたは approved-no-op | issue-local report 更新。public docs / templates / README / workflow / skill の変更は不要と判断 | approved-no-op | fresh spec-reviewer で確認予定 |
| S99 | cl-final-quality | final QA / code / spec reviewer が pass | code-reviewer pass、qa-reviewer pass、spec-reviewer pass。PR 作成後 CI failure の snapshot 更新漏れは dev-coder が修正し、focused regression + failing snapshot test を再実行済み。 | pass | `/private/tmp/iss-00174-code-review-2.json`; `/private/tmp/iss-00174-qa-review-2.json`; `/private/tmp/iss-00174-spec-review-implementation-3.json`; `80 passed, 212 deselected` |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| cl-ci-detail / cl-ci-quiet | S01/S02/S03 | yes | red-required | dev-coder が focused tests を追加 | focused pytest | pass | `checks=2/4` など detailed CI progress と `latest_change_poll` を確認 |
| cl-ci-compact / cl-skipped-neutral / cl-failed-compact | S01/S02 | yes | red-required | dev-coder が focused tests を追加 | focused pytest | pass | terminal passed は compact、failed は `fail=N` のみ |
| cl-review-detail / cl-review-quiet / cl-review-human-gate | S01/S02/S03 | yes | red-required | dev-coder が focused tests を追加 | focused pytest | pass | `comments=0 -> 1 -> 2`、human gate counts、quiet reset を確認 |
| cl-old-thread-isolation / cl-trigger-unknown | S01/S02/S03 | yes | red-required | 初回 reviewer 指摘で不足が判明 | focused pytest | pass | old / omitted / non-Codex noise は progress comments と fingerprint signal から除外 |
| cl-progress-none / cl-boundary / cl-truncation | S01/S02 | yes | red-required | dev-coder が focused tests を追加 | focused pytest | pass | stderr forbidden detail なし、stdout final JSON、line length <= 240 |
| cl-zero-check / cl-timeout-rendering / cl-raw-body-stability | S01/S02/S03 | yes | red-required / covered-existing | 既存 issue-75 系 wait wrapper tests と今回 focused run に含めて確認 | focused pytest | pass | `pr_observation_wait` selection に既存 coverage を含む |
| cl-provider-mirror-parity | S04 | yes | inspect-only | N/A | `diff -u ...` | pass | empty diff |
| cl-bash-compat | S04 | yes | inspect-only | N/A | `bash -n` both scripts | pass | syntax OK |
| cl-docs-impact | S90 | yes | inspect-only | N/A | diff inspection + report record | approved-no-op | public docs changeなし |
| cl-final-quality | S99 | yes | manual-required | N/A | final reviewer gates | pass | code / QA / spec reviewer pass |

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| cl-ci-detail | S01/S02 | focused pytest | pass | running CI detailed counters |
| cl-ci-quiet | S01/S03 | focused pytest | pass | CI count change resets quiet |
| cl-ci-compact | S01/S02 | focused pytest | pass | terminal passed compact |
| cl-review-detail | S01/S02 | focused pytest | pass | Codex current signal comments progression |
| cl-review-quiet | S01/S03 | focused pytest | pass | review progress signal change resets quiet |
| cl-review-human-gate | S01/S02 | focused pytest | pass | human gate preserves comments / threads / unresolved |
| cl-progress-none | S01/S02 | focused pytest | pass | stderr empty |
| cl-boundary | S01/S02 | focused pytest | pass | forbidden detail absent from stderr |
| cl-truncation | S01/S02 | focused pytest | pass | line budget and `limit=truncated` |
| cl-zero-check | S01/S02 | focused pytest | pass | existing zero-check wait tests included |
| cl-skipped-neutral | S01/S02 | focused pytest | pass | skipped / neutral counted as ok |
| cl-failed-compact | S01/S02 | focused pytest | pass | failed compact uses `fail=N` |
| cl-old-thread-isolation | S01/S02 | focused pytest | pass | old/non-current signals do not inflate comments |
| cl-trigger-unknown | S01/S02 | focused pytest | pass | `omitted_reason` noise excluded |
| cl-timeout-rendering | S01/S02 | focused pytest | pass | timeout rendering preserves final JSON |
| cl-raw-body-stability | S01/S03 | focused pytest | pass | raw body churn not primary quiet reset source |
| cl-provider-mirror-parity | S04 | `diff -u` | pass | empty diff |
| cl-bash-compat | S04 | `bash -n` provider/mirror | pass | syntax OK |
| cl-docs-impact | S90 | diff inspection / report | approved-no-op | no public docs impact |
| cl-final-quality | S99 | final reviewer gates | pass | code / QA / spec reviewer pass |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none | all | focused issue-174 / issue-75 wait wrapper tests | all planned closure ids | planned closure ids の範囲内で reviewer 指摘を実装・テスト補強した | no | yes |

#### ワークフロー委任同意の証跡（Workflow Delegation Consent）
`workflow_issue.md` is the policy source for workflow-scoped delegation consent. This report records observed consent, boundary, expiry, and denied / unavailable handling only.

| 同意元（consent source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可理由（denied / unavailable reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user instruction / explicit approval | `/Users/iwasawayuuta/.codex/worktrees/3b01/spec-dock` | iss-00174 | current session | dev-coder, code-reviewer, qa-reviewer, spec-reviewer | same repo, active issue, scoped source/test/docs work; no destructive action; no publishing until PR step | issue complete / session end / scope change / host policy conflict / user revocation | none | proceed to fresh reviewer gates |

#### 実装委任ゲート（Implementation Delegation Gate）
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records observed evidence only.

| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01-S04 | delegated | source/test implementation is outside main orchestrator direct-edit boundary and touches shipped provider plus dogfooding mirror | dev-coder | provider wait wrapper, mirror wait wrapper, focused tests | `requirement.md`; `design.md`; `plan.md` | `wait_pr_observation.sh` provider/mirror and focused tests | issue docs/report, unrelated source/docs/config, new GitHub API calls | `bash -n` both scripts; provider/mirror `diff -u`; `git diff --check`; focused pytest | design contradiction, stdout final JSON authority change, forbidden detail leakage | worker summary / changed files / verification / risks | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S01-S04 | dev-coder | Added two-stage progress projection/rendering, quiet reset alignment, current Codex review signal filtering, provider/mirror sync, and focused regression tests. | `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`; `.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`; `tests/unit/infra/test_init_update.py` | `bash -n` both -> pass; `diff -u` -> empty; `git diff --check` -> pass; focused pytest -> `79 passed, 213 deselected` | code-reviewer pass; qa-reviewer pass; spec-reviewer pass | none known | accepted for commit / PR |
| S99 | dev-coder | Updated checked-in dogfooding meta snapshot after PR CI exposed the new `iss-00174` `.meta.json` path was missing from the baseline. | `tests/unit/infra/test_init_update.py`; `spec-dock/active/issue/report.md` | `git diff --check` -> pass; focused pytest + failing snapshot test -> `80 passed, 212 deselected`; PR #175 rerun checks -> pass | CI rerun passed on PR #175 | none known | accepted for PR merge-prepared |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| S01-S04 | N/A | no risk acceptance needed | N/A | N/A | revert implementation commit / patch if reviewer fails | N/A | code-reviewer pass; qa-reviewer pass; spec-reviewer pass | none |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| requirement | requirement authoring gate | spec-reviewer | fresh after latest substantive change | passed | no | proceed to design authoring | `/private/tmp/iss-00174-requirement-spec-review-2.json`; findings=[]; previous P2 findings from `/private/tmp/iss-00174-requirement-spec-review-1.json` were fixed |
| design | design authoring gate | spec-reviewer | fresh after latest substantive change | passed | no | proceed to plan authoring | `/private/tmp/iss-00174-design-spec-review-1.json`; findings=[]; confidence=0.88 |
| plan | plan authoring gate | spec-reviewer | fresh after latest substantive change | passed | no | proceed to implementation execution | `/private/tmp/iss-00174-plan-spec-review-2.json`; findings=[]; confidence=0.91; previous P1 findings from `/private/tmp/iss-00174-plan-spec-review-1.json` were fixed |
| implementation | first code review | code-reviewer | before reviewer fixes | failed | no | fixed; rerun required | `/private/tmp/iss-00174-code-review-1.json`; required current Codex signal filtering and trigger_unknown/non-Codex tests |
| implementation | first QA review | qa-reviewer | before report completion | failed | no | report updated; rerun required | `/private/tmp/iss-00174-qa-review-1.json`; required report closure evidence and trigger_unknown wait-level evidence |
| implementation | first spec implementation review | spec-reviewer | before reviewer fixes/report completion | failed | no | fixed; rerun required | `/private/tmp/iss-00174-spec-review-implementation-1.json`; same comments=N/fingerprint/report blockers |
| implementation | final code review | code-reviewer | fresh after implementation and report update | passed | no | proceed to spec rerun | `/private/tmp/iss-00174-code-review-2.json`; findings=[]; focused pytest `79 passed, 213 deselected`; residual risks accepted |
| implementation | final QA review | qa-reviewer | fresh after implementation and report update | passed | no | proceed to spec rerun | `/private/tmp/iss-00174-qa-review-2.json`; findings=[]; no live GitHub integration required |
| implementation | second spec implementation review | spec-reviewer | after implementation/report update but before code/QA pass rows were reflected | failed | no | fixed; rerun completed | `/private/tmp/iss-00174-spec-review-implementation-2.json`; implementation/S90 sufficient, report self-reference rows pending |
| implementation | final spec implementation review | spec-reviewer | fresh after final report gate update | passed | no | proceed to commit / PR | `/private/tmp/iss-00174-spec-review-implementation-3.json`; findings=[]; confidence=0.89 |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S01-S04/S90/S99 | committed-and-pr-merge-prepared | provider/mirror wait script, focused tests, issue report | PR #175 head commit / GitHub PR state | worktree clean; PR checks pass | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh` - provider wait wrapper progress projection/rendering and fingerprint alignment.
- `.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh` - dogfooding mirror synced to provider.
- `tests/unit/infra/test_init_update.py` - focused regression tests for two-stage progress, boundary, quiet reset, and current Codex review signal filtering.
- `spec-dock/active/issue/report.md` - issue-local evidence ledger.

#### コミット
- PR #175: https://github.com/chemitaro/spec-dock/pull/175
- PR head: branch `iss-00174-refine-pr-observation-two-stage-progress-output`

#### メモ
- 初回 reviewer fail は実装品質ゲートとして有効に機能し、`comments=N` の意味論を implementation / tests / report へ反映済み。

---

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| docs / templates / README / workflow / skill / migration notes | no | N/A | public docs / templates / README / workflow / skill contract changesなし。issue-local `report.md` の証跡更新のみ必要。 | final spec review pass |

### 最終 QA ゲート（Final QA Gate）
| レビュアー（reviewer） | 範囲 | 統合テスト判断（integration test decision） | 証跡（evidence） | 結果（result） |
|---|---|---|---|---|
| qa-reviewer | whole issue obligation coverage | focused regression tests added; live GitHub integration not required | `/private/tmp/iss-00174-qa-review-2.json`; focused pytest `79 passed, 213 deselected`; report closure evidence updated after first QA fail | pass |

### 最終コードレビューゲート（Final Code Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| code-reviewer | issue-wide integrated diff | first review failed on `comments=N` projection and missing tests; fixed by `review_progress_signal_items` and focused noise tests | 1 | pass |

### 最終 spec review ゲート（Final Spec Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| spec-reviewer | requirement / design / plan / report / implementation / tests / docs alignment | first implementation review failed on `comments=N` projection and scaffold-only report; second review accepted implementation/S90 but failed report status and pending final rows; final review passed after report status and final rows were updated | 2 | pass |

### 最終 commit（Final Commit）
| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| this report after final spec pass | provider/mirror wait wrapper, focused tests, issue report | PR #175 / final response | PR #175 merge-prepared |

### PR delivery / merge-preparation gate
| PR | base | head | GitHub mergeability | checks | observation result | result |
|---|---|---|---|---|---|---|
| https://github.com/chemitaro/spec-dock/pull/175 | `main` | `iss-00174-refine-pr-observation-two-stage-progress-output` | `MERGEABLE` | `validate` x2 pass; `provider-tests` x2 pass | `overall_status=passed`; `recommended_next_action=merge_prepared` | pass |

## 遭遇した問題と解決 (任意)
- 問題: 初回実装では `comments=N` が non-Codex / `trigger_unknown` / timestamp unavailable signal を数え得た。
  - 解決: `review_progress_signal_items` を追加し、progress comments と fingerprint signal を current trigger-window Codex-authored signal に限定した。
- 問題: PR 作成後の full provider suite で、新規 issue `.meta.json` が dogfooding snapshot baseline に未登録だったため `test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json` が fail した。
  - 解決: `_CHECKED_IN_DOGFOODING_META_JSON_PATHS` と `_CHECKED_IN_DOGFOODING_DEPENDS_ON_BY_META_PATH` に `iss-00174` を追加し、該当 test と observation focused tests を再実行した。

## 学んだこと (任意)
- progress 表示の意味論と quiet reset の意味論は同じ projection を共有しないと、表示は正しくても wait loop の安定判定がノイズに反応する。

## 今後の推奨事項 (任意)
- PR #175 は merge-prepared まで確認済み。人間による merge 判断へ進める。

## 省略/例外メモ (必須)
- S90 は public docs / templates / README / workflow / skill 更新なしの approved-no-op とした。理由は、変更対象が既存 skill script の内部 progress behavior と focused tests であり、使用方法・CLI option・stdout JSON authority の公開契約を変更しないため。
