---
種別: 計画書（Epic）
ID: "epic-00059"
タイトル: "Dependency metadata unification and command mutation"
関連GitHub: ["#59"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-04-10"
依存: ["requirement.md", "design.md"]
親: ["init-local-00003"]
---

# epic-00059 Dependency metadata unification and command mutation — 計画（Issues / Order）

## この計画で閉じる E-RQ / E-AC
- E-RQ:
  - E-RQ-001, E-RQ-002, E-RQ-003, E-RQ-004
- E-AC:
  - E-AC-001, E-AC-002, E-AC-003, E-AC-004, E-AC-005

## Issue 分割方針
- slicing principle:
  - architecture boundary 変更を先に固定し、次に command mutation、最後に downstream parity と docs/test を閉じる。
  - `deps add` の duplicate-edge semantics は mutation tranche で固定し、current graph validation を先行させたうえで downstream parity へ曖昧さを持ち込まない。
- exceptions:
  - hard cutover judgment は T3 完了時に固定し、entry 条件の実施・充足も T3 で完了させる。T4 は final evidence packaging/review に限定する。

## Issue 一覧（順序 / tranche 付き）
- iss-00060-meta-json-dependency-schema-and-reader-alignment:
  - 目的:
    - `.meta.json` dependency schema と `infra/deps_reader.py` の read contract を確定する。
  - deliverable:
    - schema 定義、reader 実装、provider-side dependency docs（`src/spec_dock/assets/spec_dock/docs/reference_deps.md`）正本更新、hard cutover boundary note、unit tests。
  - tranche:
    - T1 foundation
  - closes:
    - E-RQ-001, E-AC-001
  - depends on:
    - なし
- iss-00061-dependency-mutation-command-contract:
  - 目的:
    - `deps add/remove` を導入し fail-closed validation を mutation path に組み込む。
  - deliverable:
    - parser/handler/application/domain/infra write path、CLI response/error contract、current graph validation 優先の duplicate-edge non-dup invariant、integration tests。
  - tranche:
    - T2 mutation
  - closes:
    - E-RQ-002, E-RQ-003, E-AC-002
  - depends on:
    - iss-00060-meta-json-dependency-schema-and-reader-alignment
- iss-00062-downstream-parity-and-cutover-readiness:
  - 目的:
    - delete/sync/active/validate の依存解釈を `.meta.json` SoT に統一し、hard cutover entry 条件を実施・充足・記録したうえで judgment を固定する。
  - deliverable:
    - `application/delete_node.py` scrub、`application/{set_active,sync_state,validate_tree}.py` parity、cutover boundary tests、dogfooding checked-in data manual fix 実施、`./spec-dock/scripts/spec-dock validate` / `sync` evidence、cutover evidence contract、hard cutover judgment primary owner record（T3 issue `report.md`）。
  - tranche:
    - T3 integration
  - closes:
    - E-RQ-004, E-AC-003, E-AC-004
  - depends on:
    - iss-00061-dependency-mutation-command-contract
- iss-00063-final-regression-parity-and-cutover-closure:
  - 目的:
    - T3 で固定済みの cutover judgment を前提に、final regression / parity confirmation / spec review / close summary を完了する。
  - deliverable:
    - final regression suite、parity confirmation、T3 evidence bundle の review / packaging、T4 issue `report.md` final parity/spec review record、epic `report.md` close summary。
  - tranche:
    - T4 closure
  - closes:
    - E-AC-005, epic final close review
  - depends on:
    - iss-00062-downstream-parity-and-cutover-readiness

## cutover evidence ownership
- T3 integration owner（`iss-00062-downstream-parity-and-cutover-readiness`）:
  - hard cutover judgment と E-AC-003 readiness verdict の primary owner。
  - 自身の `report.md` に dogfooding checked-in data manual fix 完了 path/scope、targeted regression summary、`./spec-dock/scripts/spec-dock validate` / `sync` の command line・exit code・結果要約、judgment verdict を残す。
  - provider-side dependency docs 正本更新は T1（`iss-00060`）の差分を正本として参照する。
- T4 closure owner（`iss-00063-final-regression-parity-and-cutover-closure`）:
  - E-AC-005 final closure と final parity / final spec review の primary owner。
  - 自身の `report.md` に final regression summary、T3 evidence bundle review 結果、必要な parity reconfirmation、final spec review verdict を残し、epic `report.md` には close summary だけを反映する。

## 統合チェックポイント
- G1 decomposition review:
  - schema/read contract と command contract の責務分離が明確か。
- G2 integration readiness:
  - mutation 導入後も delete/sync/active/validate が同一 graph を観測し、T3 で hard cutover judgment を固定できるか。
  - `deps add` 実行前に current graph validation が走り、不整合時は fail-closed error になり、正常時だけ既存 edge が `result=unchanged` の success/no-op として扱われるか。
- G3 rollout/docs impact:
  - provider-side dependency docs 正本更新が T1 で完了し、hard cutover 手順、manual fix、`validate` / `sync` evidence contract が T3 で実施・反映され、T3/T4 issue `report.md` と epic `report.md` の owner/shape が明示されているか。
- G9 final epic spec review:
  - E-AC すべてに test と実測証跡があるか。

## 品質ゲート
- test / observability / migration / docs:
  - unit + integration + cutover boundary regression を必須。
  - error code と fail-closed 挙動を snapshot で固定。
  - `deps add` は current graph validation failure を error で固定し、その後に duplicate-edge の `result=unchanged` と non-dup invariant を integration で固定する。
  - dogfooding workspace で checked-in data manual fix 後の `./spec-dock/scripts/spec-dock validate` / `sync` を T3 で成功させ、T4 は最終回帰として再確認のみ行う。
  - T3/T4 の `report.md` に最低 evidence bundle が揃っていることを close 条件にする。

## ロールアウト / docs impact
- rollout order:
  - schema/reader + provider-side dependency docs 正本更新 -> mutation command -> downstream parity + dogfooding manual fix / evidence -> final review。
- contract / docs refresh:
  - T1（`iss-00060`）で provider-side dependency reference docs 正本を更新する。
  - T3（`iss-00062`）で dogfooding checked-in data manual fix と `validate` / `sync` evidence、cutover judgment を記録する。

## Issue readiness contract
- Issue に要求する最低条件:
  - changed boundary（SoT/persistence/validation）を明記。
  - test 追加点と回帰点を明記。
  - rollback 観点を明記。

## final exit contract
- E-AC closure:
  - E-AC-001..005 がテストと dogfooding 実測で成立する。
  - E-AC-003 は T3 issue `report.md` の cutover judgment evidence bundle、E-AC-005 は T3 judgment fixed 後の T4 issue `report.md` と epic `report.md` close summary で reviewer が追跡できる。
- integration / rollout complete:
  - `deps` mutation と downstream command が同一 SoT を使用する。
  - `deps add` は current graph が不正なら fail-closed error、正常なら duplicate-edge を success/no-op として収束させ、storage 上の重複を発生させない。
- docs impact resolved:
  - initiative/epic/issue docs と runtime docs が同期されている。

## 依存 / ブロッカー
- D-001:
  - resolved:
    - dogfooding manual fix は checked-in data に限定し、cutover entry 条件は docs 更新 + manual fix + `validate` / `sync` evidence に固定し、T3 で実施する。
- D-002:
  - resolved:
    - command UX は remove not-found を error に固定した。

## 未確定事項
- 現時点ではなし。
