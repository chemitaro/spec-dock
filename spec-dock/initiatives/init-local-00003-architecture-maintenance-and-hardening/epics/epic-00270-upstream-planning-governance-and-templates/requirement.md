---
種別: 要件定義書（Epic）
ID: "epic-00270"
タイトル: "Upstream Planning Governance And Templates"
関連GitHub: ["#270"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["init-local-00003"]
---

# epic-00270 Upstream Planning Governance And Templates — 要件定義

## 目的（Initiative との紐づき）
- Initiative 目標:
  - `spec-dock` の architecture maintenance / governance / hardening を継続的に扱うため、上流 planning から下流 Issue execution までの仕様作成品質を安定させる。
- この Epic が提供する能力:
  - Initiative / Epic authoring を、source-grounded clarification、scope ownership、artifact adoption、Issue slicing、handoff readiness、fresh reviewer gate を通じて、実装可能な downstream Issue へ接続できるようにする。
  - Phase 1 で強化済みの Issue grade / TDD planning と、Phase 2 で強化済みの `artifacts/` evidence surface に、上流 Initiative / Epic planning を接続する。
  - 日本語運用では、要件定義書、設計書、計画書、report、artifacts の本文を日本語ファーストで作成できるようにする。

## ユースケース
- 正常系:
  - maintainer が新しい Initiative / Epic を作成し、既存 docs / code / ADR / artifacts を調査したうえで、必要な user-intent gap だけを一問ずつ確認できる。
  - agent が Initiative / Epic requirement / design / plan を作成し、raw evidence を canonical authority と誤認せず、採用判断を `report.md` に残せる。
  - agent が日本語運用の文脈では、要件定義書、設計書、計画書、report、artifacts の本文を日本語ファーストで作成できる。
  - Epic plan が downstream Issue に、parent requirement / design trace、responsibility boundary、suggested grade、dependencies、verification expectation を渡せる。
  - Epic execution coordinator が Issue を実行へ流す前に handoff package の構造欠落を blocking として止め、意味的な十分性は reviewer finding として扱える。
- 例外 / 運用シナリオ:
  - 既存6 Issue では独立レビュー性、責務境界、検証可能性、PR delivery が破綻する場合は、計画を更新して Issue を追加または再分割できる。
  - 1PR delivery が現実的でなくなった場合だけ、証跡を残して PR 分割を再検討する。
  - code / docs / history から解ける疑問はユーザーへ質問せず、調査 artifact に外部化する。

## エピック要件
- E-RQ-001: Initiative / Epic template upgrade
  - Initiative templates は strategic planning / Epic handoff を扱い、Issue-level implementation detail や TDD cycles を持ち込まない。
  - Epic templates は capability / model envelope、cross-Issue constraints、design slice catalog、Issue handoff package、suggested Issue grade を扱う。
- E-RQ-002: source-grounded clarification workflow
  - planning skills / workflow docs は `spec-dock-clarification` による source-grounded grill loop を利用し、local sources で解けることをユーザーへ質問しない。
  - 重要質問は `interview` artifact として一問ずつ記録し、採用判断を同じ artifact と `report.md` に残す。
- E-RQ-003: artifact-to-canonical authority flow
  - `artifacts/` は working evidence surface とし、raw research / interview / disc / delegated draft は canonical authority ではない。
  - 採用された知識は canonical docs、accepted ADR、または `report.md` Evidence Adoption Ledger / Spec Authoring Gate へ反映する。
- E-RQ-004: architecture-neutral / architecture-aware authoring
  - templates と skills は DDD / EDA を標準前提にしない。
  - existing architecture / design policy が明確な場合はそれに合わせ、未定義の場合は Initiative layer で明確化する。
- E-RQ-005: scope layering and reference publication
  - Initiative / Epic / Issue responsibility model は provider-side reference `docs/authoring/scope-layering.md` に集約し、workflow docs / skills / templates は薄くリンクする。
- E-RQ-006: Epic-to-Issue slicing and handoff
  - Epic plan は provisional 6 Issue baseline を基本にしつつ、必要に応じた controlled re-slicing を許容する。
  - downstream Issue へ parent trace、allowed local delta、forbidden parent boundary changes、acceptance seed、constraints、expected evidence、suggested grade、dependencies、escalation triggers、relevant artifacts を渡す。
- E-RQ-007: handoff inspection and execution readiness
  - Epic execution handoff inspection は medium strictness とする。
  - machine-checkable な構造欠落は blocking fail、意味的品質は reviewer finding とする。
- E-RQ-008: quality and delivery gate
  - final quality Issue は automated checks、manual tests、fresh reviewer gates、review repair、PR readiness を統合して扱う。
  - Epic は原則1PRで delivery し、IssueごとのPR分割は計画しない。
- E-RQ-009: Japanese-first spec and artifact authoring
  - 日本語運用では、requirement / design / plan / report / artifacts の本文を日本語ファーストで作成する。
  - ファイルパス、コマンド、コード識別子、SpecDock の固定用語、外部固有名詞は原文を保持してよい。
  - templates、skills、workflow docs、reviewer guidance、smoke tests は、英語混在を放置せず、日本語ファースト authoring を誘導・確認できるようにする。
- E-RQ-010: Issue-local draft artifact boundary and grade-aware role policy
  - Issue Start 前の Issue design / plan seed は、canonical `design.md` / `plan.md` ではなく Issue-local `draft-design` / `draft-plan` artifact に置く。
  - Canonical Issue `design.md` / `plan.md` は、Issue Planning で `assurance compose` されるまで `artifact_state: awaiting-assurance-compose` placeholder として保持する。
  - Draft artifact 作成 surface は `new artifact draft-design --issue <issue-id>` と `new artifact draft-plan --issue <issue-id>` に統一し、actor別、specialist別、深さ別 command は作らない。
  - system-architect / implementation-planner の関与は、Issue grade に応じた workflow / skill / EAL / reviewer gate で管理する。
  - `assurance compose` は canonical compose 専用であり、pre-start draft artifact 作成に使わない。
  - `compose-draft`、`issue prepare`、`epic prepare-issues` は初期実装必須 surface にしない。将来追加する場合も thin wrapper に限定する。

## エピック受け入れ条件
- E-AC-001: Initiative template readiness
  - 前提: 新しい Initiative scaffold / template を作成または確認する。
  - 操作: requirement / design / plan template を読む。
  - 期待結果: strategic purpose、capability landscape、source-of-truth、Epic handoff、artifact adoption、reviewer gate が表現できる。
  - 観測点: template snapshot、unit test、manual scenario summary。
- E-AC-002: Epic template readiness
  - 前提: 新しい Epic scaffold / template を作成または確認する。
  - 操作: requirement / design / plan template を読む。
  - 期待結果: capability / model envelope、design slice catalog、Issue handoff、suggested grade、dependencies、final quality gate が表現できる。
  - 観測点: template snapshot、unit test、manual scenario summary。
- E-AC-003: planning skills and workflow alignment
  - 前提: Initiative / Epic planning skills と workflow docs を確認する。
  - 操作: source-grounded clarification から requirement / design / plan authoring、fresh reviewer gate、handoff までの導線を追う。
  - 期待結果: skills / docs が raw artifacts を canonical authority とせず、`report.md` adoption evidence を要求する。
  - 観測点: docs diff、reviewer result、利用可能な targeted tests。
- E-AC-004: Epic execution handoff readiness
  - 前提: downstream Issue list / readiness contract を持つ planned Epic が存在する。
  - 操作: Epic execution entrypoint の handoff inspection behavior を確認する。
  - 期待結果: missing canonical docs / reviewer pass / Issue readiness contract / executable step structure / required verification / reviewer focus は blocking になり、semantic quality は reviewer finding になる。
  - 観測点: unit / CLI runtime tests、または smoke scenario evidence。
- E-AC-005: upstream planning validation
  - 前提: updated templates and skills が利用可能である。
  - 操作: `validate`、関連する unit / CLI runtime tests、manual dogfooding scenarios を実行する。
  - 期待結果: existing Issue grade / TDD workflow と矛盾せず、新しい upstream planning path が downstream Issue planning へ接続できる。
  - 観測点: test output と report / artifacts の manual test summary。
- E-AC-006: delivery readiness
  - 前提: implementation Issues が完了している、または証跡付きで意図的に skip されている。
  - 操作: final quality gate と PR readiness check を実行する。
  - 期待結果: raw manual-test files が commit されず、PR scope / validation / manual-test / follow-up が説明される。
  - 観測点: final report ledger と PR preparation evidence。
- E-AC-007: Japanese-first authoring readiness
  - 前提: updated templates / skills / workflow docs / artifact guidance が利用可能である。
  - 操作: 新規または更新された requirement / design / plan / report / artifacts の作成導線を確認する。
  - 期待結果: 説明文、判断理由、受け入れ条件、設計説明、計画説明、artifact本文が日本語ファーストになり、許容される英語は識別子・固定語・外部固有名詞に限定される。
  - 観測点: template snapshot、docs diff、skill read-through、smoke test、reviewer result。
- E-AC-008: pre-start Issue draft migration readiness
  - 前提: `iss-00271` から `iss-00276` の canonical `design.md` / `plan.md` に pre-start draft body が存在する。
  - 操作: 各 draft body を Issue-local `draft-design` / `draft-plan` artifact へ移し、canonical `design.md` / `plan.md` を awaiting-assurance-compose placeholder に戻す。
  - 期待結果: 未開始 Issue の canonical `design.md` / `plan.md` は本文入り draft ではなくなり、Issue-local draft artifacts は evidence-only として report EAL に記録される。
  - 観測点: artifact path index、Issue report EAL、Epic report EAL、fresh `spec-reviewer` result、`rg` / `validate` 結果。

## スコープ
- 必須:
  - provider-side scaffold assets 配下の Initiative / Epic templates。
  - Initiative / Epic authoring と Epic execution handoff の planning skills / workflow docs。
  - scope-layering reference と、workflow / docs / skills / templates からの thin links。
  - 日本語ファースト authoring 方針を templates、skills、workflow docs、artifacts guidance、reviewer checks に反映すること。
  - template structure、artifact authority、reviewer gates、handoff readiness を扱う tests / smoke checks。
  - scaffold-affecting changes がある場合の local dogfooding workspace inspection / validation。
- 禁止:
  - raw V3 planning pack prose を canonical docs に全文貼り付けること。
  - `artifacts/` を canonical authority として扱うこと。
  - DDD / EDA を SpecDock の標準前提にすること。
  - 日本語運用の canonical docs / artifacts に、説明文としての英語本文を混在させたままにすること。
  - decision-only Issue を execution-ready として作ること。
  - Issue Start 前に canonical Issue `design.md` / `plan.md` へ pre-start draft body を置くこと。
  - actor / specialist / depth 別の draft artifact command を作ること。
  - `assurance compose` を Issue-local draft artifact 作成に流用すること。
  - Issue grade templates を直接 redesign すること。ただし compatibility fix は許容する。
- 対象外:
  - multi-repo / multi-tracker strategy。
  - user-facing product feature expansion。
  - runtime dependency algorithm redesign。
  - PR merge / auto-merge / GitHub issue close automation。

## 境界
- 常に行う:
  - user interview の前に source-grounded investigation を行う。
  - user judgment が必要な場合は、essential question を一問ずつ確認する。
  - decisions / constraints / Issue slicing / handoff の adoption evidence を `report.md` に残す。
  - downstream handoff の前に fresh reviewer gates を通す。
  - 日本語運用では、canonical docs / artifacts の本文を日本語ファーストにする。
- 判断が必要:
  - 6 Issue baseline の re-slicing。
  - 1PR delivery が破綻する場合の PR boundary。
  - prototype / high-fidelity evidence が必要な design question の扱い。
  - 技術識別子として英語を残すか、説明文として日本語化するかの境界。
- 行わない:
  - chat context only の知識を canonical docs の根拠にしない。
  - agent が user-intent blocker を代理判断しない。
  - Epic execution skill を semantic reviewer にしない。
  - コマンド名、ファイルパス、コード識別子を無理に日本語化しない。

## 非機能要件
- 信頼性 / 一貫性:
  - planning workflow は、missing / stale reviewer pass、unresolved Spec Authoring Gate、missing handoff contract、raw artifact authority leaks に対して fail closed する。
- 運用:
  - documentation は discoverable に保つ。
  - high-detail references は、各 template へ重複させず、1つの provider-side reference または scope-local artifacts に置く。
- 可読性:
  - 日本語運用では canonical docs / artifacts の本文を日本語ファーストにし、技術識別子と説明文の境界を明確にする。
- 互換性:
  - existing Issue grade / TDD planning behavior は Issue-level execution の source of truth として維持する。
- セキュリティ:
  - secrets、tokens、local-only artifacts は導入しない。
  - manual test workspaces は untracked のままにする。

## 依存 / 影響範囲
- 影響する component:
  - `src/spec_dock/assets/spec_dock/templates/{initiative,epic}/`
  - `src/spec_dock/assets/spec_dock/docs/`
  - `src/spec_dock/assets/install_root/.agents/skills/`
  - runtime guidance または validation が必要な場合の `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`
  - installer / scaffold / runtime validation のための `tests/`
  - confirmation のための local dogfooding `spec-dock/`
- 外部依存:
  - 実装に必要な外部依存はない。
  - final delivery では GitHub / PR delivery evidence を利用する可能性がある。
- 互換性:
  - updated scaffold を受け取る existing managed repos は、DDD / EDA adoption を要求されずに improved templates / docs を受け取れる。

## 未確定事項
- なし:
  - clarification interviews と accepted ADRs により、現時点で design / plan authoring 前に必要な Epic-level product decisions は解決済みである。
