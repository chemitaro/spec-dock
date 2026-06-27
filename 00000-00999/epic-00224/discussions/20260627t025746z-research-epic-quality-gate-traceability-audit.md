---
種別: リサーチ
ID: "20260627t025746z-research"
タイトル: "Epic 00224 要件・ADR・議論の実装反映監査"
状態: "draft"
作成者: "codex"
最終更新: "2026-06-27"
親: ["epic-00224"]
scope:
  - "Epic requirement/design/plan"
  - "accepted ADRs"
  - "Issue reports"
  - "provider assets"
  - "dogfooding mirror"
  - "tests"
---

# Epic 00224 要件・ADR・議論の実装反映監査

## 結論

現時点の Epic 品質ゲートは、個別 Issue のテスト・レビューを通している一方で、Epic で確定した要件、ADR、議論上の生きた決定を横断的に再照合する仕組みが不足している。

今回確認された `@codex review` trigger の問題は、その具体例である。Epic requirement と accepted ADR は「base SHA の review policy が missing / invalid / oversized / unreadable の場合は human gate」と定義しているが、現行実装とテストは「fixed default `@codex review` へ fallback し、success 扱いする」挙動を固定している。

この状態では、PR head に policy file が追加されていても base branch に未導入であれば、trusted policy なしの bare `@codex review` が投稿される。これは expected rollout behavior ではなく、ADR の fail-closed policy と衝突する。

## 監査対象

- Epic 正本:
  - `requirement.md`
  - `design.md`
  - `plan.md`
- Accepted ADR:
  - `20260623t074441z-adr-fixed-skill-kernel-compiled-runbook-authority.md`
  - `20260623t074442z-adr-step-assurance-resource-allocation-agent-context-routing.md`
  - `20260623t074443z-adr-adaptive-assurance-lite-authorization-monotonic-escalation.md`
  - `20260623t074444z-adr-trusted-base-sha-github-review-policy.md`
  - `20260623t074447z-adr-blocker-centric-pr-risk-closure-rereview.md`
- 実装・skill・テスト:
  - `.agents/skills/github-pr-observation/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - `.agents/skills/github-pr-observation/scripts/trigger_codex_review.sh`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/trigger_codex_review.sh`
  - `tests/unit/infra/test_init_update.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**`
  - `spec-dock/scripts/spec_dock_runtime/**`

## 重要な確認結果

### QG-001: Trusted base SHA review policy の fail-closed が未実装

- 状態: failed
- 重大度: P0 / merge-prepared blocker
- 対応先候補: 既存 PR 内の修正、または追加 Issue
- 根拠:
  - Epic requirement は、final delivery で PR base SHA 上の review policy を読み、policy hash と reviewed head SHA を含む `@codex review` comment を投稿するとしている。
  - Epic requirement は、Review policy を PR base SHA から取得できない場合、外部 review 必須 workflow では human gate とするとしている。
  - ADR `Trusted Base SHA GitHub Review Policy` は、base policy が missing / invalid / oversized / unreadable の場合は human gate とし、head policy へ fallback しないと明記している。
  - 現行 `trigger_codex_review.sh` は missing / too_large / invalid / base_sha_missing で warning limitation を積み、fixed default body へ fallback して POST を継続する。
  - `tests/unit/infra/test_init_update.py` は missing / invalid / non-UTF-8 / too-large の各 case で `body=@codex review` 投稿と `success is True` を期待している。
- 必要な修正:
  - base SHA が取得できない、または base policy が missing / invalid / oversized / unreadable の場合は、trigger comment を投稿しない。
  - helper JSON は `success=false`、`overall_status=human_gate`、`trigger.action=skipped` または `blocked`、`review_policy.status=<reason>`、`limitations[].severity=blocking` を返す。
  - head policy fallback は追加しない。
  - tests は fallback success 期待を fail-closed / human gate 期待へ反転する。
  - provider asset と dogfooding mirror の script を同期する。

### QG-002: github-pr-observation skill 文面が旧 write contract のまま

- 状態: failed
- 重大度: P1
- 根拠:
  - dogfooding mirror と provider asset の `github-pr-observation/SKILL.md` は、許可 write を「fixed body `@codex review`」と説明している。
  - 実装済みの正常系は multiline body を生成し、`Trusted review policy:`、policy source、policy hash、reviewed head SHA を含める。
  - skill 文面は multiline deterministic body と trusted base policy failure の human gate を operator に伝えていない。
- 必要な修正:
  - skill の write contract を「fixed endpoint + deterministic body」に更新する。
  - body は caller-provided ではなく runtime が base policy と metadata から合成すると明記する。
  - base policy failure は trigger write ではなく human gate と明記する。
  - 「手動で `@codex review` を投稿しない」ルールは維持するが、理由を trusted policy evidence と紐付ける。

### QG-003: Epic 正本に `workflow next` の旧語彙が残っている

- 状態: failed
- 重大度: P1
- 根拠:
  - `iss-00238` の分析・実装では、Skill が second-stage workflow file を見に行くのではなく、`spec-dock guidance <target>` stdout を毎回取得する設計へ変更した。
  - しかし Epic requirement の E-RQ-001 / E-RQ-004 と plan の G2 には `workflow next` が current entrypoint として残っている。
  - 実装と active skill は `guidance issue-planning` / `guidance issue-execution` を使うため、Epic 正本が後続 agent に stale instruction を与え得る。
- 必要な修正:
  - Epic requirement / plan / relevant ADR の表現を `guidance <target>` に更新する。
  - `workflow next` が historical name である場合は、明示的に superseded とする。
  - Issue #238 report の決定を Epic-level decision / plan quality gate へ反映する。

### QG-004: human-only projection の位置付けは実装済みだが Epic 正本への再反映が不足

- 状態: partial
- 重大度: P2
- 根拠:
  - `iss-00238` では generated projection は human/debug output であり、agent handoff authority ではないという設計に更新されている。
  - `spec-dock-issue-planning` skill には projection を authority として読まない指示が入っている。
  - 一方、Epic requirement の E-RQ-005 は Runbook を `.agent/` と `active/` generated state へ保存することを前提にし、agent が stdout を primary handoff とする現行決定を十分に表現していない。
- 必要な修正:
  - Epic 正本で「stdout guidance が agent handoff authority」「projection は human/debug only」と明文化する。
  - projection write failure は non-blocking、context packet write failure は fail-closed、という差異を E-RQ / E-AC / quality gate に反映する。

### QG-005: Issue planning template composition の後続 Issue 化はできているが Epic trace は未統合

- 状態: partial
- 重大度: P2
- 根拠:
  - `iss-00239` は、Issue 作成時に requirement template のみを置き、classification / assurance 後に design / plan scaffold を合成する問題を扱う follow-up として作成されている。
  - これは Epic の「Adaptive artifact composition」と「model が assurance compose を飛ばさない」安全設計に関係するが、Epic requirement / plan の final quality gate には follow-up trace として明確に統合されていない。
- 必要な修正:
  - `iss-00239` を Epic 00224 の quality gate traceability table に追加する。
  - 初期 7 issue の範囲外に追加された corrective issue が、どの E-RQ / E-AC / discussion decision を補完するかを Epic report または discussion に記録する。

### QG-006: Step gate 判定の修正は実装済みだが、Epic-wide regression gate として未定義

- 状態: partial
- 重大度: P2
- 根拠:
  - PR review repair で、S90/S99 routing、full step approval before skip、context-packet failure guidance、draft requirement frontmatter などが修正された。
  - これらは Issue #238 の PR review で発見された Epic workflow safety gap であり、個別テストは追加されている。
  - ただし Epic の最終品質ゲートには「全 issue report の Sxx step closure が Step Contract Closure / Reviewer Gate Status / Step Commit Gate の三点で成立していること」を横断検証する gate が明文化されていない。
- 必要な修正:
  - Epic final gate に `issue report step closure audit` を追加する。
  - Step skip は full closure evidence または explicit approved-no-op がある場合だけ許可することを Epic-level invariant として記録する。

### QG-007: Context routing / clean-room / bounded return は実装証跡があるが外部 reviewer 実運用の証跡が薄い

- 状態: partial
- 重大度: P2
- 根拠:
  - `iss-00230` と `iss-00238` で context packet、reviewer clean-room、bounded return contract に関するテストと runtime output がある。
  - 一方で、実際の sub-agent / reviewer 実行が常に compiled context packet を参照しているか、operator が手動で文脈を過剰投入していないかを Epic-wide に検査する gate はない。
- 必要な修正:
  - Issue report に `Context Contract Used` / `Packet hash` / `Excluded author narrative` / `Returned payload boundary` を記録する table を追加する。
  - Epic close 前に各 issue の report から reviewer / consultant / worker context evidence を横断抽出する。

### QG-008: Auto-Lite readiness / efficiency evidence は成果物確認が必要

- 状態: needs-verification
- 重大度: P2
- 根拠:
  - Epic requirement は automatic Lite default を有効化せず、future adoption gates、telemetry、efficiency evidence を残すことを求めている。
  - 実装 Issue #233 がこの範囲を持つが、今回の監査では auto-lite readiness report の中身、metrics missing summary、automatic_lite_default_enabled=false の実証までは再確認していない。
- 必要な確認:
  - `iss-00233` の report と生成 artifact を確認する。
  - runtime / CLI に automatic Lite default が有効化されていないことを targeted test で確認する。

## E-RQ / E-AC 横断チェックリスト

| ID | 期待 | 現状判定 | 主な証跡 | 不足 / 次アクション |
|---|---|---:|---|---|
| E-RQ-001 | State-derived workflow entrypoint | partial | `guidance` command 実装、workflow tests | Epic 正本の `workflow next` 表現を更新 |
| E-RQ-002 | Assurance Contract | pass-needs-final-audit | `assurance.json` schema / tests / issue reports | final audit で provider/mirror parity を確認 |
| E-RQ-003 | Deterministic classification | pass-needs-final-audit | classification tests / reports | automatic Lite disabled を再確認 |
| E-RQ-004 | Fixed Skill kernel | partial | issue planning/execution skill は `guidance` 化済み | Epic 正本の stale wording 更新 |
| E-RQ-005 | Compiled Runbook | partial | runbook projection tests / stale projection tests | stdout authority vs projection human-only を Epic に反映 |
| E-RQ-006 | Adaptive artifact composition | partial | issue #229 / #239 | #239 trace を Epic quality gate に統合 |
| E-RQ-007 | Step Assurance | partial | workflow context routing tests | Sxx closure audit gate を追加 |
| E-RQ-008 | Context policy | partial | context packet tests / skill guidance | 実 sub-agent 使用証跡の横断 audit が必要 |
| E-RQ-009 | Trusted GitHub Codex review policy | failed | trigger helper / tests / skill | missing/invalid/oversized/unreadable を human gate に修正 |
| E-RQ-010 | Blocker-centric review closure | pass-needs-final-audit | PR blocker tests / observation semantics | real PR observation result と carryover thread handling を final audit |
| E-RQ-011 | Re-review and stagnation | pass-needs-final-audit | observation wait / repair loop tests | automation-stalled evidence を final audit |
| E-RQ-012 | Compatibility and rollout | pass-needs-final-audit | strict-legacy tests | existing issue path の manual smoke を確認 |
| E-RQ-013 | Observability | partial | reports / generated evidence | metrics missing summary と event projection を確認 |
| E-RQ-014 | Auto-Lite readiness | needs-verification | issue #233 expected | readiness report の存在・内容確認 |
| E-RQ-015〜021 | Context routing policy family | partial | issue #230 / context packet tests | clean-room 実運用証跡と return contract audit を追加 |
| E-AC-009 | Trusted review trigger | partial | valid policy 正常系 test | policy failure human gate tests が必要 |
| E-AC-010 | Untrusted policy rejection | pass-needs-final-audit | base SHA fetch / head policy non-use | missing base policy の fail-closed を追加 |
| E-AC-013 | Automation stalled | needs-verification | issue #233 expected | final report / tests を再確認 |
| E-AC-015 | Auto-Lite readiness without default enablement | needs-verification | issue #233 expected | generated report と runtime default を再確認 |
| E-AC-016 | Efficiency evidence | needs-verification | issue #233 expected | benchmark / missing metrics summary を確認 |
| E-AC-017〜021 | Context compilation / independence / minimization | partial | runtime tests | actual agent handoff evidence の横断 audit が必要 |

## 具体的な修正タスク案

### Fix A: Trusted review policy failure を fail-closed にする

- 対象:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/trigger_codex_review.sh`
  - `.agents/skills/github-pr-observation/scripts/trigger_codex_review.sh`
  - `tests/unit/infra/test_init_update.py`
- 期待:
  - base SHA missing / policy missing / policy invalid / policy non-UTF-8 / policy oversized では POST しない。
  - JSON は human gate を返す。
  - `review_policy.source` は `base_sha` または `fixed_default` のままでもよいが、`trigger.action` は `none` / `blocked` / `skipped` とし、`success=false` にする。

### Fix B: github-pr-observation skill contract を deterministic body へ更新

- 対象:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - `.agents/skills/github-pr-observation/SKILL.md`
- 期待:
  - fixed endpoint + deterministic runtime-composed body に更新。
  - valid base policy 時の multiline body を説明。
  - base policy failure は human gate であり bare trigger fallback しないと説明。

### Fix C: Epic 正本の stale workflow wording を修正

- 対象:
  - Epic `requirement.md`
  - Epic `design.md`
  - Epic `plan.md`
  - 必要なら accepted ADR の追記 discussion
- 期待:
  - `workflow next` を current command として書かない。
  - `guidance <target>` stdout が agent handoff authority、projection は human/debug only とする。
  - Issue #238 の決定を Epic quality gate に昇格する。

### Fix D: Epic close 前の traceability quality gate を追加

- 対象:
  - Epic `plan.md` または `report.md`
  - この discussion の follow-up
- 期待:
  - `E-RQ / E-AC / ADR / live discussion decision -> issue -> implementation -> test -> report evidence` の表を持つ。
  - corrective issue #237 / #238 / #239 を初期 7 issue と同じ quality gate に含める。
  - final PR 前に failed / partial / needs-verification を 0 または明示 human gate にする。

## 推奨する Epic 完了前ゲート

Epic 00224 を close / merge-prepared とする前に、以下を必須にする。

1. Accepted ADR の各 Decision bullet に対し、provider implementation、dogfooding mirror、tests、skill/docs の反映有無を表で確認する。
2. Epic requirement の E-RQ-001〜021 と E-AC-001〜021 に対し、実装ファイル、テスト、Issue report evidence を最低 1 つずつ紐付ける。
3. 「failed」または「逆仕様を固定するテスト」がある場合、PR review trigger を実行せず、human gate / repair issue に入る。
4. 追加 corrective issue は、Epic plan の initial issue list 外であっても final quality gate に含める。
5. Skill 文面、provider asset、dogfooding mirror、tests の 4 点が同じ public contract を説明・検証していることを確認する。

## 現時点の判定

- Epic close readiness: not ready
- PR merge-prepared readiness: blocked
- 主 blocker:
  - `E-RQ-009` / ADR trusted base policy の fail-closed 未実装。
  - `github-pr-observation` skill contract の stale wording。
  - Epic 正本に `workflow next` / projection authority 前提の stale wording が残っている。
- 次の推奨アクション:
  - Fix A / B を同一修正として実装し、focused tests を red/green で反転する。
  - Fix C / D を docs/spec quality gate として反映し、Epic-level traceability audit を再実行する。
