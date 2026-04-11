---
種別: 要件定義書（Issue）
ID: "iss-00063"
タイトル: "Final regression parity and cutover closure"
関連GitHub: ["#63"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-04-11"
親: ["epic-00059", "init-local-00003"]
---

# iss-00063 Final regression parity and cutover closure — 要件定義（WHAT / WHY）

## 目的
- `iss-00062` が固定した hard cutover judgment を前提として、epic `epic-00059` の最終回帰、parity confirmation、spec review、close summary を T4 closure owner として完了する。
- `E-AC-005` と epic final close review を、T3/T4 の ownership を崩さず reviewer が追跡できる evidence bundle と report record で閉じる。
- deliverable は final regression suite、parity confirmation、T3 evidence bundle review / packaging、T4 issue `report.md` final parity/spec review record、epic `report.md` close summary である。

## 背景・現状
- 現状の挙動:
  - epic `plan.md` では hard cutover judgment と entry 条件の primary owner を T3 issue `iss-00062` に固定している。
  - T4 issue `iss-00063` は、T3 judgment fixed 後の final regression / parity confirmation / close review を担当する closure tranche と定義されている。
  - T3 issue `report.md` は cutover readiness / judgment の正本であり、T4 はその証跡を review / package したうえで final closure record を作る役割を持つ。
- 現状の課題:
  - `iss-00063` の issue docs は T4 closure owner 向けの骨格までは埋まっているが、`iss-00062/report.md` の実測証跡に追従した review-only inherited regression suite と、T3 report metadata/status の前提ギャップがまだ固定されていない。
  - final regression / parity confirmation / spec review の責務分界が曖昧なままだと、T3 judgment を再判定したり、逆に E-AC-005 の final close evidence が不足したまま epic close を主張したりする危険がある。
  - `final regression suite` の正本、`same dependency graph` の判定方法、epic `report.md` を更新できる step が曖昧なままだと、reviewer が T3/T4 の owner split を追えない。
- 再現手順:
  1. epic `requirement.md` / `design.md` / `plan.md` を確認する。
  2. `iss-00063` 配下の `requirement.md` / `design.md` / `plan.md` を確認する。
  3. T4 closure owner の deliverable、review boundary、report 更新責務が issue-level に具体化されていないことを確認する。
- 観測点:
  - Docs:
    - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/requirement.md`
    - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/design.md`
    - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/plan.md`
    - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00062-downstream-parity-and-cutover-readiness/report.md`
    - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00063-final-regression-parity-and-cutover-closure/requirement.md`
    - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00063-final-regression-parity-and-cutover-closure/design.md`
    - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00063-final-regression-parity-and-cutover-closure/plan.md`
    - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00063-final-regression-parity-and-cutover-closure/report.md`
    - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/report.md`
  - Command:
    - `./spec-dock/scripts/spec-dock validate`
    - `./spec-dock/scripts/spec-dock sync`
    - 必要時 `./spec-dock/scripts/spec-dock active set <target-id>`
  - Evidence:
    - T3 cutover judgment record
    - final regression suite result
    - parity confirmation result
- 情報源:
  - epic `requirement.md` / `design.md` / `plan.md`
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/docs/phase_plan_issue.md`
  - `iss-00062/report.md`

## 対象ユーザー / 利用シナリオ
- 主な利用者:
  - epic maintainer
  - T4 closure owner
  - final spec reviewer
- 代表シナリオ:
  - reviewer が T3 と T4 の責務分離を保ったまま、epic close を判断する。
  - maintainer が final regression / parity confirmation / report close summary を一続きの close-out flow として実行する。

## スコープ
- MUST:
  - T3 で固定済みの hard cutover judgment を入力として受け取り、再判定しない。
  - final regression suite の正本、構成コマンド/テスト、pass 条件、記録先を固定する。
  - `same dependency graph` の比較表現、`set-active` / `sync` / `validate` から採る観測値、mismatch 判定条件を fixed contract として固定する。
  - T3 evidence bundle の review 観点、欠落時の扱い、T4 側での packaging 先を固定する。
  - T4 issue `report.md` に final parity/spec review record を残す。
  - epic `report.md` に close summary を反映する責務を固定し、更新可能 step を S04 のみに限定する。
  - `iss-00062/report.md` 完成前は T4 close-out execution を blocker として扱う。
- MUST NOT:
  - T3 cutover judgment の owner を T4 に移さない。
  - T3 entry 条件の実施自体を T4 でやり直したことにしない。
  - source code や runtime contract の変更を本 issue の責務に含めない。
  - T3 evidence に欠落や矛盾がある場合、ad hoc に runtime fallback や追加実装で埋め合わせしない。
- OUT OF SCOPE:
  - `.meta.json` schema や `deps add/remove` contract の再設計。
  - hard cutover readiness の再承認。
  - 新しい mutation feature や validation rule の追加。

## 境界
- Always:
  - T3 は cutover readiness/judgment owner、T4 は final closure ownerという分担を維持する。
  - T4 の primary deliverable は evidence review / packaging / report close-out である。
  - final regression / parity confirmation の結果は、必ず issue `report.md` の session record と final summary に残す。
  - epic close claim は T4 issue `report.md` と epic `report.md` の両方から追える形にする。
  - epic `report.md` を更新してよいのは、T3 evidence bundle review と T4 parity/spec review が揃った S04 close reporting のみとする。
- Ask:
  - T3 evidence bundle に欠落、矛盾、再現不能な command result がある場合は blocker として reviewer 判断へ escalate する。
  - final regression で product gap が見つかった場合は、epic close ではなく follow-up issue 判断へ escalate する。
- Never:
  - T3 judgment を「T4 で pass したから成立」と読み替えない。
  - report 未更新のまま `complete` や epic close summary を主張しない。
  - spec review 未通過の evidence bundle を final close record として確定しない。

## 非交渉制約
- `E-AC-005` の final closure owner は T4 であり、T4 issue `report.md` が primary evidence record になる。
- T3 issue `report.md` は hard cutover judgment の primary evidence のままとする。
- final regression / parity confirmation の required command では `./spec-dock/scripts/spec-dock validate` を成功させる。
- final regression suite の正本は本 issue spec とし、追加/削除を ad hoc に決めない。
- `same dependency graph` は `.meta.json` SoT 由来の正規化 `issue_depends_on_map` を比較基準とし、順序差だけでは pass/fail を変えない。
- same-snapshot parity は checked-in `.meta.json` graph snapshot と rerun-required command 観測の整合を要求する。手順外の repo mutation は禁止するが、rerun-required command 自身が生成する `spec-dock/.agent/**` / `dashboard.md` / `*.puml` 更新や、`sync` 自身が branch matching により active target を current branch issue へ復元する副作用は、`.meta.json` / canonical tuple 集合が不変で command exit が success の場合に限り expected output として許容する。
- epic `report.md` の更新は S04 close reporting だけで許可し、S02/S90 では更新しない。
- epic close summary は T4 issue `report.md` と矛盾してはならない。
- 新たな uppercase path を作らない。

## 前提
- `iss-00062/report.md` が template / placeholder ではなく、hard cutover judgment、docs 更新、dogfooding checked-in data manual fix、`validate` / `sync` evidence を実値で記録している。
- T4 が S02 へ進むには、`iss-00062/report.md` の本文 evidence と frontmatter/status が 完了状態（frontmatter `状態: "approved"` + 本文 evidence complete） として整合している必要がある。status mismatch が残る間は T4 は S01 の blocker 記録までしか行わず、S02 以降へ進まない。
- T4 は T3 judgment fixed 後の repo state を対象に close-out を行う。
- 必要な product change が残っていれば、その時点で本 issue は `blocked` または `未完了` であり close 不可である。

## 固定契約
- final regression suite contract:
  - 正本:
    - 本 issue `requirement.md` の AC-001 と TERM-002。実行時の詳細記録先は T4 issue `report.md` の final regression section とする。
  - suite item:
    - review-only inherited targeted regression:
      - `python -m unittest tests.cli_runtime.test_delete tests.cli_runtime.test_runtime_delete_s13 tests.cli_runtime.test_active tests.cli_runtime.test_sync tests.cli_runtime.test_validate -v`
      - `python -m unittest tests.cli_runtime.test_active tests.cli_runtime.test_sync tests.cli_runtime.test_validate tests.cli_runtime.test_runtime_active_s06 tests.cli_runtime.test_runtime_deps_s04 tests.cli_runtime.test_runtime_validate_s02 -v`
      - `python -m unittest tests.test_init_update.TestInitUpdate.test_init_creates_expected_structure tests.test_init_update.TestInitUpdate.test_init_does_not_seed_legacy_node_deps_json_templates tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_mirror_templates_match_provider_assets tests.test_init_update.TestInitUpdate.test_reference_sync_doc_matches_bundled_asset tests.test_init_update.TestInitUpdate.test_reference_deps_doc_matches_bundled_asset tests.test_init_update.TestInitUpdate.test_workflow_issue_doc_matches_bundled_asset tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_subprocess_numeric_deps_overlap_parity tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_subprocess_scoped_deps_ref_parity tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_subprocess_numeric_deps_ref_foreign_only_fail_closed_parity -v`
      - `python -m unittest -v tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_mirror_match_provider_assets tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_subprocess_validate_and_sync_on_cutover_snapshot tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_subprocess_deps_mutation_on_cutover_snapshot tests.test_init_update.TestInitUpdate.test_init_creates_expected_structure tests.test_init_update.TestInitUpdate.test_init_does_not_seed_legacy_node_deps_json_templates tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_mirror_templates_match_provider_assets`
    - rerun-required final commands:
      - `./spec-dock/scripts/spec-dock sync`
      - `./spec-dock/scripts/spec-dock validate`
      - `./spec-dock/scripts/spec-dock active set <target-id>` ただし `<target-id>` は `iss-00062/report.md` に active parity の観測対象として記録済みの id を使う。id が記録されていなければ blocker とする。
  - review substitution scope:
    - T3 で pass 済みの targeted regression は `iss-00062/report.md` の command line、exit code、pass verdict、対象 test 名が揃っている場合に限り、T4 では review-only evidence として扱う。rerun gate には含めない。
    - `python -m unittest tests.cli_runtime.test_runtime_active_s06 tests.cli_runtime.test_runtime_deps_s04 -v` は `iss-00062/report.md` S02 の flaky-check subset であり、fixed inherited suite には含めない。T4 では supplemental evidence としてのみ参照できる。
    - T4 では `sync` / `validate` / 必要時 `active set` の final command evidence を review だけで代替してはならない。
  - pass 条件:
    - review-only inherited targeted regression がすべて `iss-00062/report.md` から追える。
    - rerun-required final commands が現在の repo state で pass し、T4 issue `report.md` に command line、exit code、result summary が残る。
    - fail / mismatch / evidence 欠落が 1 件でもあれば suite verdict は `pass` にしない。
- same dependency graph contract:
  - graph 表現:
    - `.meta.json` SoT から導く正規化 `issue_depends_on_map` を基準とし、比較時は `issue_id -> depends_on_id` の sorted unique tuple 集合として扱う。
  - command ごとの観測値:
    - `active set <target-id>`:
      - `target_id`
      - `ready` / `blocked` verdict
      - `blocker_ids` の sorted list
    - `sync`:
      - rendered edge tuple 集合
      - artifact / stdout が示す dependency error の有無
    - `validate`:
      - exit code
      - validation error edge の有無
      - pass / fail verdict
  - mismatch 判定:
    - command 間で edge tuple が欠落/追加/重複している。
    - `active set` の `blocker_ids` が同じ graph snapshot から導かれる依存集合と一致しない。
    - `sync` または `validate` が、他 command が参照していない edge/error を示す。
    - 同一 repo snapshot で採った観測として説明できない。
    - ただし rerun-required command 自身が生成する `spec-dock/.agent/**` / `dashboard.md` / `*.puml` 更新や、`sync` が `matched id in branch: <current-issue>` を理由に active target を current branch issue へ復元しただけで、`.meta.json` / canonical tuple 集合が不変なら mismatch とは扱わない。

## 受け入れ条件
- AC-001:
  - Actor:
    - T4 closure owner / reviewer
  - Given:
    - T3 issue `report.md` に hard cutover judgment evidence があり、`iss-00062/report.md` 完了状態（frontmatter `状態: "approved"` + 本文 evidence complete） が確認できる
  - When:
    - T4 が fixed final regression suite を実行または review し、その対象、結果、判定を issue `report.md` に記録する
  - Then:
    - final regression suite の正本が本 issue spec にあること、suite item ごとの review-only / rerun-required 区分が reviewer に追える
    - final regression suite が pass したこと、または fail / block の理由が reviewer に追える
    - T4 が T3 judgment を再判定していないことが明記される
  - 観測点:
    - T4 issue `report.md`
    - `iss-00062/report.md`
    - regression command / test result
- AC-002:
  - Actor:
    - T4 closure owner / reviewer
  - Given:
    - T3 judgment fixed 後の repo state
  - When:
    - `set-active` / `sync` / `validate` の最終確認を parity confirmation として実施し、fixed graph contract に従って同一 dependency graph を観測する
  - Then:
    - downstream command が同一 graph を扱っていることを、正規化 `issue_depends_on_map` と command ごとの観測値比較で説明できる
    - `./spec-dock/scripts/spec-dock validate` の成功結果が issue `report.md` に残る
  - 観測点:
    - `active set` の `target_id` / `ready|blocked` / `blocker_ids`
    - `sync` の rendered edge tuple summary
    - `validate` の exit code / validation error summary
    - issue `report.md` の parity section
    - `sync` の active restore reason（branch matching による復元が起きた場合）
- AC-003:
  - Actor:
    - T4 closure owner / reviewer
  - Given:
    - T3 issue `report.md` が hard cutover judgment の正本である
  - When:
    - T4 が T3 evidence bundle を review し、required evidence の有無、参照先、close への持ち上げ方を package する
  - Then:
    - T3 evidence bundle の review 結果が T4 issue `report.md` から追える
    - evidence 欠落時は `blocked` または `未完了` と next action が記録される
  - 観測点:
    - T4 issue `report.md`
    - T3 issue `report.md`
- AC-004:
  - Actor:
    - final spec reviewer / epic maintainer
  - Given:
    - final regression、parity confirmation、T3 evidence bundle review が揃っている
  - When:
    - S04 でのみ T4 issue `report.md` に final parity/spec review record を作成し、epic `report.md` に close summary を反映する
  - Then:
    - `E-AC-005` の close evidence が T4 issue `report.md` で追える
    - epic `report.md` には close summary だけが転記され、T3/T4 ownership conflict がない
    - epic final close review の verdict が追跡できる
  - 観測点:
    - T4 issue `report.md`
    - epic `report.md`

## 例外・エッジケース
- EC-001:
  - 条件:
    - T3 issue `report.md` に required evidence の参照先不足または command 結果欠落がある
  - 期待:
    - T4 は不足箇所を明記して `blocked` または `未完了` とし、T3 judgment 自体を rewrite しない
  - 観測点:
    - T4 issue `report.md` の blocker / next action 記録
- EC-002:
  - 条件:
    - final regression または parity confirmation で drift / mismatch が見つかる
  - 期待:
    - epic close summary は更新せず、差分内容と follow-up 要否を T4 issue `report.md` に記録する
  - 観測点:
    - command result
    - issue `report.md`
- EC-003:
  - 条件:
    - T4 issue `report.md` と epic `report.md` の close claim が不整合
  - 期待:
    - epic close は不成立として扱い、spec review で fail にする
  - 観測点:
    - review verdict
    - 両 report の記述差分
- EC-004:
  - 条件:
    - `iss-00062/report.md` が incomplete、frontmatter/status と本文 evidence が 完了状態（frontmatter `状態: "approved"` + 本文 evidence complete） として整合しない、または final regression suite の review-only inherited item を追跡できない
  - 期待:
    - T4 は S04 へ進まず `blocked` と next action を記録し、epic `report.md` を更新しない
  - 観測点:
    - T4 issue `report.md`
    - `iss-00062/report.md`

## 入力→出力例
- EX-001:
  - Input:
    - T3 issue `report.md`
    - final regression suite result
    - `validate` / `sync` / `set-active` summary
  - Output:
    - T4 issue `report.md` final parity/spec review record
    - epic `report.md` close summary

## 用語（ドメイン語彙）
- TERM-001:
  - T3 evidence bundle:
    - `iss-00062/report.md` に集約された hard cutover judgment、docs 更新、manual fix、`validate` / `sync` evidence 一式。
- TERM-002:
  - final regression suite:
    - T4 で最終 close 前に確認する固定 regression test / command 群。review-only inherited targeted regression 4 件と rerun-required final command 2-3 件で構成し、T3 judgment を再判定せず close readiness だけを再確認する。
- TERM-003:
  - parity confirmation:
    - `set-active` / `sync` / `validate` が、`.meta.json` SoT 由来の正規化 `issue_depends_on_map` を同じ graph 表現として観測していることの最終確認。
- TERM-004:
  - close summary:
    - epic `report.md` に記録する短い close-out 要約。詳細 evidence の正本は issue `report.md` に置く。

## 未確定事項
- 現時点ではなし。
