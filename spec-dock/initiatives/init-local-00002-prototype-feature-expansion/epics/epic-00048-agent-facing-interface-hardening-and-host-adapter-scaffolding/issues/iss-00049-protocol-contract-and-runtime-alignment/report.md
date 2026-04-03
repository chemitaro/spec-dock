# iss-00049 report

## 2026-04-03 spec authoring
- 実施内容:
  - requirement/design/plan を current-future vs full-history contract 前提で具体化した。
  - host adapter 実装は issue-00050 へ分離し、本 issue は protocol/runtime/docs/tests alignment に限定した。

## 2026-04-03 spec review
- review scope:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - epic-00048 `requirement.md` / `design.md` / `plan.md` との整合
- checklist:
  - requirement:
    - scope / out-of-scope / AC / EC / 非交渉制約が観測可能であること
  - design:
    - 既存実装理解、契約、変更範囲、verification mapping が揃っていること
  - plan:
    - step 粒度、review gate、docs impact、final exit contract が揃っていること
- findings:
  - none
- verdict:
  - pass
- note:
  - `projection` / `source` metadata を採用決定として fixed point 化した

## 2026-04-03 SG1 re-review
- 実行コマンド:
  - `git --no-pager diff -- spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00048-agent-facing-interface-hardening-and-host-adapter-scaffolding/issues/iss-00049-protocol-contract-and-runtime-alignment/requirement.md spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00048-agent-facing-interface-hardening-and-host-adapter-scaffolding/issues/iss-00049-protocol-contract-and-runtime-alignment/design.md spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00048-agent-facing-interface-hardening-and-host-adapter-scaffolding/issues/iss-00049-protocol-contract-and-runtime-alignment/plan.md spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00048-agent-facing-interface-hardening-and-host-adapter-scaffolding/plan.md`
- review scope:
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/plan.md`
  - `spec-dock/active/epic/plan.md`
  - `spec-dock/docs/workflow_issue.md`
- 初回 reviewer verdict:
  - fail
- blocking findings:
  - iss-00049 と iss-00050 の docs parity / final review 責務境界が issue/epic 間で食い違っていた
  - artifact ごとの top-level `projection` / `source` contract が曖昧で、`deps-issues.json` provenance `source` と per-node issue status `source` semantics の境界が明示されていなかった
- 修正内容:
  - iss-00049 は protocol contract surface の runtime/provider-doc/dogfooding-doc/test parity を担当し、issue-00050 は adapter scaffold 残件と final epic parity/review を担当するよう issue/epic plan を整合させた
  - `index.json` / `index-all.json` / `deps-issues.json` の artifact ごとの top-level metadata contract を requirement/design/plan で明文化した
  - `index.json` / `index-all.json` には new top-level `source` を追加しないこと、`deps-issues.json` は provenance `source` を持ち、既存 per-node issue status `source` semantics は維持することを固定した
  - EC-001 の active-none placeholder 証跡と EC-002 の fail-closed placeholder/provenance 証跡を step gate に明記した
- 再 review verdict:
  - pass
- reviewer result:
  - `review_status: pass`
  - reason:
    - issue-00049 / issue-00050 の scope split と artifact metadata contract が docs 上で固定され、P0/P1 spec ambiguity が解消された
- 想定外と対処:
  - 既存 report には SG1 pass とだけ残っていたが、reviewer の blocking findings を後追いで回収したため fixed point の根拠が不足していた
  - stage commit 前に spec docs を是正し、re-review を通してから report を追記する形で収束させた
- refactor:
  - なし
