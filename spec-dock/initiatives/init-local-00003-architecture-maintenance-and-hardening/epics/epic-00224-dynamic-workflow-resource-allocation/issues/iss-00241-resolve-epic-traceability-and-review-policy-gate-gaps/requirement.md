---
種別: 要件定義書（Issue）
ID: "iss-00241"
タイトル: "Resolve Epic Traceability And Review Policy Gate Gaps"
関連GitHub: ["#241"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-27"
親: ["epic-00224", "init-local-00003"]
---

# iss-00241 Resolve Epic Traceability And Review Policy Gate Gaps — 要件定義

## 目的
- Epic 00224 の実装後監査で判明した、accepted ADR / Epic 要件 / live discussion decision が個別 Issue 実装・skill 文面・Epic 正本・最終 report に完全反映されていない問題を修正する。
- Trusted base SHA review policy、`guidance <target>` stdout handoff、human-only projection、planning scaffold composition、Epic closure ledger を一つの corrective Issue として閉じる。
- Epic close / PR merge-prepared 前に、初期 Issue だけでなく corrective Issue も含めた traceability quality gate を成立させる。

## 背景・現状
- 現状の挙動:
  - `trigger_codex_review.sh` は base SHA policy が missing / invalid / oversized / unreadable の場合でも warning limitation を積み、bare `@codex review` body へ fallback して投稿し、success 扱いになり得る。
  - `github-pr-observation/SKILL.md` は、実装済みの deterministic multiline body ではなく「fixed body `@codex review`」を public write contract として説明している。
  - Epic 00224 の `requirement.md` / `design.md` / `plan.md` には、`iss-00238` で置換済みの `workflow next` と generated Runbook projection authority の語彙が残っている。
  - `iss-00239` は planning template composition の corrective Issue として存在するが、scaffold のままであり Epic close readiness を block している。
  - Epic `report.md` は completed issue / acceptance criteria / corrective issue / blocked gate の状態が混在し、現在の close readiness を一貫して示していない。
- 現状の課題:
  - Accepted ADR `Trusted Base SHA GitHub Review Policy` と逆の failure path が実装・テストで固定されている。
  - Skill、provider asset、dogfooding mirror、tests、Epic docs が同じ public contract を説明・検証していない。
  - Epic で確定した後続 decision が Issue-local report に閉じ、Epic 正本へ戻る final traceability gate が不足している。
  - 要件未確定 / assurance 未分類のまま design / plan scaffold が通常編集可能に見え、agent が classification / compose gate を飛ばすリスクが残っている。
- 情報源:
  - Epic audit: `discussions/20260627t025746z-research-epic-quality-gate-traceability-audit.md`
  - Spec reviewer: `discussions/20260627t030737z-disc-spec-reviewer-epic-traceability-gate.md`
  - Trusted policy ADR: `discussions/20260623t074444z-adr-trusted-base-sha-github-review-policy.md`
  - Fixed kernel ADR: `discussions/20260623t074441z-adr-fixed-skill-kernel-compiled-runbook-authority.md`
  - Issue 239 research: `issues/iss-00239-compose-issue-planning-templates-after-assurance-classification/discussions/20260624t113051z-research-assurance-compose-scaffold-analysis.md`
  - Issue 241 clarification: `discussions/20260627t031714z-research-clarification-before-requirement-authoring.md`
  - User-approved scope decision: `discussions/20260627t031736z-interview-corrective-issue-scope-confirmation.md`

## スコープ
- 必須:
  - Trusted base SHA review policy が利用不能な場合、review trigger は投稿せず human gate / fail-closed とする。
  - `github-pr-observation` skill の public write contract を fixed endpoint + runtime-composed deterministic body + human gate failure path に更新する。
  - Provider asset と dogfooding mirror の script / skill / tests を同じ contract へ揃える。
  - Epic 00224 の正本を、agent-facing authority は `./spec-dock/scripts/spec-dock guidance <target>` stdout、generated projection は human/debug-only という現在仕様へ更新する。
  - `iss-00239` の planning scaffold composition 問題を `iss-00241` に吸収し、`iss-00239` は superseded / closed として traceability 上も未解決扱いにしない。
  - Issue 作成直後の `design.md` / `plan.md` は通常 scaffold ではなく assurance compose 待ちの blocker placeholder とし、requirement capture / classification / compose を飛ばしにくくする。
  - Epic `report.md` を current closure ledger として再構成し、corrective Issue、blocked gate、reviewer verdict、remaining next action を一貫して示す。
  - Epic final quality gate に、E-RQ / E-AC / ADR / discussion decision から implementation / tests / docs / report evidence への横断 traceability audit を追加する。
- 禁止:
  - PR head 側の `.github/codex/review-policy.md` へ fallback しない。
  - Base policy が読めない状態で bare `@codex review` を投稿しない。
  - caller-provided review body、任意 endpoint、任意 policy path、raw `gh` args を許可しない。
  - `workflow next` を現在の agent-facing entrypoint として残さない。
  - generated Runbook projection を agent handoff authority として扱わない。
  - `iss-00239` を open scaffold のまま Epic close-ready としない。
  - 既存の substantive user content を assurance compose で自動上書きしない。
- 対象外:
  - Automatic Lite default の有効化。
  - Codex Action 本番移行。
  - 新しい live telemetry backend の追加。
  - PR blocker engine 全体の再設計。
  - Epic 初期 7 Issue の実装を全面的に作り直すこと。

## 境界
- 常に行う:
  - Provider source of truth を先に更新し、dogfooding mirror / tests / docs / report と整合させる。
  - Failure path は negative test で固定する。
  - Docs-only / skill-text-only の変更は inspection / spec-review evidence で閉じる。
  - Epic 正本更新は historical ADR を改ざんするのではなく、必要に応じて「superseded wording / current contract」を canonical docs と report に明記する。
- 判断済み:
  - `iss-00239` は `iss-00241` に吸収し、一つの corrective Issue として扱う。
  - review artifacts は Epic discussions に残し、Issue 241 では参照・採用する。
- 行わない:
  - 本 Issue で別の追跡 Issue をさらに作って scope を分散しない。ただし実装中に Epic 外の新規リスクが見つかった場合は report に follow-up 候補として記録する。

## 非交渉制約
- Accepted ADR と逆の success path を残してはならない。
- Provider asset / dogfooding mirror / installed skill text / tests は同じ public contract を共有する。
- `guidance <target>` stdout は agent-facing handoff authority、generated projection は non-canonical human/debug output とする。
- Base policy missing / invalid / oversized / unreadable / unreadable permission は fail-closed human gate とする。
- Requirement / design / plan / report は main orchestrator-owned canonical artifacts とし、discussion evidence は採用台帳を通して反映する。
- Final status は「comment zero」ではなく、verified blocker zero と traceability gate pass で判断する。

## 前提
- Active issue は `iss-00241`。
- `iss-00241` は GitHub issue `#241` に紐づく。
- `iss-00239` の scope 吸収はユーザー承認済み。
- 現在の runtime / skills は `guidance issue-planning` / `guidance issue-execution` を使う方針に移行済みである。
- Repo は dogfooding repo であり、implementation source of truth は `src/spec_dock/assets/...`、`spec-dock/` は dogfooding validation target である。

## 受け入れ条件
- AC-001: Trusted review policy failure は human gate になる
  - アクター: GitHub PR observation operator / agent。
  - 前提: Open PR があり、base SHA が取得できない、または base SHA 上の `.github/codex/review-policy.md` が missing / invalid / non-UTF-8 / oversized / unreadable。
  - 操作: review trigger helper を実行する。
  - 期待結果: PR issue comment は投稿されず、JSON は `success=false`、`overall_status=human_gate`、blocking limitation、policy failure reason、trigger skipped/blocked 相当を返す。
  - 観測点: provider / dogfooding trigger script tests、fake `gh` call log。
- AC-002: Valid base policy の deterministic multiline trigger は維持される
  - アクター: GitHub PR observation operator / agent。
  - 前提: base SHA 上に valid review policy があり、expected head SHA が一致する。
  - 操作: review trigger helper を実行する。
  - 期待結果: policy base SHA、policy hash、reviewed head SHA を含む deterministic multiline `@codex review` comment が 1 件だけ投稿される。
  - 観測点: fake GitHub contract test、trigger JSON、posted body。
- AC-003: Skill public contract が runtime behavior と一致する
  - アクター: 後続 agent。
  - 前提: `github-pr-observation/SKILL.md` を読む。
  - 操作: review trigger / observation workflow を実行する。
  - 期待結果: skill は fixed endpoint + runtime-composed deterministic body、caller-provided body 禁止、base policy failure human gate、手動 bare trigger 禁止を説明している。
  - 観測点: provider / dogfooding skill text inspection、unit text assertions。
- AC-004: Epic 正本は `guidance <target>` stdout handoff を現在仕様として示す
  - アクター: Issue planning / execution agent。
  - 前提: Epic 00224 の requirement / design / plan を読む。
  - 操作: workflow entrypoint を確認する。
  - 期待結果: current command は `./spec-dock/scripts/spec-dock guidance issue-planning` / `issue-execution` として説明され、`workflow next` は historical / superseded wording として扱われる。
  - 観測点: Epic docs inspection、skill text / runtime test parity。
- AC-005: Generated projection は human/debug-only として扱われる
  - アクター: Issue planning / execution agent。
  - 前提: guidance command が projection files を書く。
  - 操作: handoff authority を確認する。
  - 期待結果: agent は projection file を読みに行く必要がなく、stdout guidance を current handoff とする。projection write failure は guidance stdout success を失敗扱いにしない。
  - 観測点: Epic docs、runtime tests、presentation text。
- AC-006: Issue 作成直後の design / plan は assurance compose 待ち blocker になる
  - アクター: Issue authoring agent。
  - 前提: 新規 Issue を作成する。
  - 操作: `design.md` / `plan.md` を開く。
  - 期待結果: 通常 scaffold ではなく、requirement capture、assurance classify、assurance compose を要求する machine-readable placeholder が表示される。
  - 観測点: `spec-dock new issue` CLI tests、template inspection。
- AC-007: Assurance compose は placeholder を安全に materialize する
  - アクター: Issue authoring agent。
  - 前提: requirement が具体化され、assurance classification / contract が存在し、`design.md` / `plan.md` は placeholder 状態。
  - 操作: `assurance compose --artifact all` を実行する。
  - 期待結果: profile-aware design / plan scaffold が生成される。既に substantive content がある場合は上書きせず fail-closed または conflict とする。
  - 観測点: assurance compose tests、artifact content inspection。
- AC-008: `iss-00239` は `iss-00241` に supersede される
  - アクター: SpecDock operator。
  - 前提: `iss-00241` の requirement / design / plan が `iss-00239` scope を含む。
  - 操作: `iss-00239` の lifecycle / GitHub issue 状態と Epic report を確認する。
  - 期待結果: `iss-00239` は superseded / closed と記録され、Epic final gate では unresolved scaffold として残らない。
  - 観測点: SpecDock report / GitHub issue / Epic report。
- AC-009: Epic report は current close readiness を一貫して示す
  - アクター: Epic reviewer / downstream agent。
  - 前提: `iss-00241` の修正が完了している。
  - 操作: Epic `report.md` を読む。
  - 期待結果: completed / blocked / corrective issue status、E-RQ / E-AC evidence、reviewer verdict、remaining next action が矛盾なく記録される。
  - 観測点: Epic report inspection、spec-reviewer。
- AC-010: Epic traceability quality gate が追加される
  - アクター: Spec reviewer / Epic closer。
  - 前提: Epic close 前。
  - 操作: E-RQ / E-AC / accepted ADR / live discussion decisions を implementation / tests / docs / reports へ照合する。
  - 期待結果: failed / partial / needs-verification entry は 0、または explicit human gate / formal supersede として記録される。
  - 観測点: Epic plan/report traceability table、spec-reviewer pass。

## 例外・エッジケース
- EC-001: PR head に policy が追加されているが base branch にはない
  - 条件: PR head has `.github/codex/review-policy.md`、base SHA にはない。
  - 期待: head policy を使わず human gate。bare trigger も投稿しない。
  - 観測点: base/head fixture test。
- EC-002: base policy が大きすぎる
  - 条件: base policy が 32 KiB を超える。
  - 期待: human gate。POST なし。blocking limitation に oversized reason を含める。
  - 観測点: trigger test。
- EC-003: base policy が non-UTF-8 / unreadable
  - 条件: base policy fetch は成功するが decode / read validation に失敗する。
  - 期待: human gate。POST なし。head fallback なし。
  - 観測点: trigger test。
- EC-004: Issue 作成後に agent が placeholder design / plan を直接編集しようとする
  - 条件: `artifact_state: awaiting-assurance-compose` のまま design / plan に本文が追記される。
  - 期待: validate / guidance / compose のいずれかで未合成状態または conflict として検出し、通常 planning complete としない。
  - 観測点: validate / compose / workflow tests。
- EC-005: guidance stdout は成功するが projection write に失敗する
  - 条件: `.agent/runbooks` または `active/current-runbook.*` が書けない。
  - 期待: stdout guidance は agent handoff として利用可能。projection error は human/debug projection failure として表示し、authority failure にはしない。
  - 観測点: runtime presentation / runbook store tests。

## 用語
- Trusted base policy:
  - PR base SHA の fixed path `.github/codex/review-policy.md` から読む review policy。
- Deterministic review body:
  - caller が自由入力せず、runtime が trusted policy と PR metadata から合成する `@codex review` comment body。
- Human gate:
  - 自動 trigger / merge-prepared を進めず、人間判断または環境修復を要求する fail-closed 状態。
- Guidance:
  - `./spec-dock/scripts/spec-dock guidance <target>` が stdout に返す、現在状態に対する agent-facing handoff。
- Projection:
  - `.agent/runbooks/current-runbook.*` / `active/current-runbook.*` に生成される human/debug-only output。canonical authority でも agent handoff authority でもない。
- Placeholder scaffold:
  - Issue 作成直後の `design.md` / `plan.md` に置かれる、assurance compose 待ちを示す blocker content。
- Corrective integration Issue:
  - 初期 Issue 実装後に見つかった Epic-level gap を、一つの traceability / quality gate 修正として統合して閉じる Issue。

## 未確定事項
- なし。
