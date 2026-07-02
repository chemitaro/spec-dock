---
種別: 計画書（Epic）
ID: "epic-00270"
タイトル: "Upstream Planning Governance And Templates"
関連GitHub: ["#270"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
依存: ["requirement.md", "design.md"]
親: ["init-local-00003"]
---

# epic-00270 Upstream Planning Governance And Templates — 計画

## この計画で閉じる E-RQ / E-AC
- E-RQ:
  - E-RQ-001: Slice 01 と Slice 02 で Initiative / Epic templates を更新する。
  - E-RQ-002: Slice 03 で planning skills と workflow docs を、source-grounded clarification と reviewer-gated authoring に合わせる。
  - E-RQ-003: Slice 03 と Slice 05 で artifact-to-canonical authority flow と report evidence gate を維持・検証する。
  - E-RQ-004: Slice 01、Slice 02、Slice 05 で architecture-neutral / architecture-aware template authoring を反映・検証する。
  - E-RQ-005: Slice 03 で scope-layering provider reference と thin links を追加し、Slice 05 で discoverability と drift control を検証する。
  - E-RQ-006: Slice 02 で Epic-to-Issue slicing と handoff fields を定義し、Slice 04 で Epic execution が handoff を消費できるようにする。
  - E-RQ-007: Slice 04 で Option B handoff inspection を反映し、Slice 05 で structural fail と reviewer finding の分離を検証する。
  - E-RQ-008: Slice 06 で final automated / manual quality gates、review repair、one-PR delivery readiness を扱う。
  - E-RQ-009: Slice 01、Slice 02、Slice 03、Slice 04、Slice 05、Slice 06 で日本語ファーストの spec / artifact authoring を反映・検証する。
  - E-RQ-010: Slice 03 で workflow / skill guidance、Slice 04 で draft artifact primitive と readiness workflow、Slice 05 / Slice 06 で検証と最終確認を扱う。
- E-AC:
  - E-AC-001: Slice 01 で対応し、Slice 05 と Slice 06 で検証する。
  - E-AC-002: Slice 02 で対応し、Slice 05 と Slice 06 で検証する。
  - E-AC-003: Slice 03 で対応し、Slice 05 と Slice 06 で検証する。
  - E-AC-004: Slice 04 で対応し、Slice 05 と Slice 06 で検証する。
  - E-AC-005: Slice 05 と Slice 06 で対応する。
  - E-AC-006: Slice 06 で対応する。
  - E-AC-007: Slice 01、Slice 02、Slice 03、Slice 04 で反映し、Slice 05 と Slice 06 で検証する。
  - E-AC-008: planning correction で既存 Issue docs を移行し、Slice 04 / Slice 05 / Slice 06 で将来の workflow / command / validation として固定する。

## 課題分割方針
- 基本方針:
  - V3 の6 Issueを provisional baseline とする。
  - Slice 01-05 は `strict`、Slice 06 は `critical` を suggested grade とする。
  - actual Issue scaffold は `iss-00271` から `iss-00276` として作成済みである。
  - 各 Issue の正規 `requirement.md` は先行作成済みである。
  - Issue Start 前の design / plan seed は canonical `design.md` / `plan.md` ではなく、Issue-local `draft-design` / `draft-plan` artifact として保持する。
  - Canonical Issue `design.md` / `plan.md` は、Issue Planning の `assurance compose` と fresh reviewer gate まで `artifact_state: awaiting-assurance-compose` placeholder とする。
- 分割原則:
  - Issue は、1つの coherent observable outcome を持つ。
  - decision-only container を execution-ready Issue にしない。
  - parent Epic requirement / design の境界を Issue plan で再定義しない。
  - template / docs / skills / tests の変更は、reviewable boundary と verification boundary が一致するように切る。
- 再分割gate:
  - 追加 Issue / 再分割は推奨しない。
  - 既存6 Issueでは独立レビュー性、責務境界、検証可能性、PR delivery が明確に悪化する場合だけ許可する。
  - 追加 Issue / 再分割を行う場合は、理由、影響、baselineとの差分、dependency / order、grade、handoff package を `plan.md` に反映し、fresh `spec-reviewer` gate を通す。
  - re-slicing evidence は `report.md` Evidence Adoption Ledger / Spec Authoring Gate に記録する。
- pre-start draft correction gate:
  - `iss-00271` から `iss-00276` の canonical `design.md` / `plan.md` に置かれていた pre-start draft body は、Issue-local `draft-design` / `draft-plan` artifacts へ移す。
  - canonical Issue `design.md` / `plan.md` は awaiting-assurance-compose placeholder に戻す。
  - 各 Issue `report.md` に migration EAL と Grade Specialist Evidence Gate を記録する。
  - Epic `report.md` の EAL-021 / EAL-022 は historical batch planning evidence と現在の authority boundary に合わせて再分類する。
  - 移行後に `rg` / `validate` / fresh `spec-reviewer` を実行し、planning set の整合性を確認する。
- PR 方針:
  - Epic delivery は原則1PR。
  - IssueごとのPR分割は通常方針に入れない。
  - `iss-00271` から `iss-00275` は、それぞれ実装・検証後に `issue finish` し、次Issueを `issue start` するリレー方式で進める。
  - PR readiness / PR creation は `iss-00276` だけが扱う。
  - 1PRが reviewability / delivery risk の面で破綻すると判断できる場合だけ、証跡を残して PR boundary を再検討する。

## 課題一覧
以下の6件を actual SpecDock Issue として作成済みである。要件定義書は正本であり、設計書と実装計画書の seed は Issue-local draft artifacts に置く。各Issueの canonical `design.md` / `plan.md` は、Issue開始後に改めて `assurance compose` し、fresh reviewer gate を通して正規化する。

| Slice | Issue | 予定タイトル | Suggested grade | Tranche | 目的 | 主に閉じるもの | 依存 |
|---|---|---|---|---|---|---|---|
| 01 | `iss-00271` / #271 | Initiative 要件・設計・計画 templates の再設計 | `strict` | T1 templates | Initiative templates を strategic planning と Epic handoff の surface にする | E-RQ-001, E-RQ-004, E-RQ-009, E-AC-001, E-AC-007 | batch Issue planning gate |
| 02 | `iss-00272` / #272 | Epic 要件・設計・計画 templates の再設計 | `strict` | T1 templates | Epic templates を target model、design slice、Issue handoff、suggested grade の surface にする | E-RQ-001, E-RQ-004, E-RQ-006, E-RQ-009, E-AC-002, E-AC-007 | `iss-00271` |
| 03 | `iss-00273` / #273 | Scope-layering reference と planning guidance の更新 | `strict` | T2 guidance | scope-layering reference を作成し、workflow docs、phase docs、skills、更新済み templates へ thin links と draft artifact handoff guidance を追加する | E-RQ-002, E-RQ-003, E-RQ-005, E-RQ-009, E-RQ-010, E-AC-003, E-AC-007, E-AC-008 | `iss-00272` |
| 04 | `iss-00274` / #274 | Epic execution handoff と Issue readiness workflow の更新 | `strict` | T2 execution readiness | Epic execution が downstream Issue readiness を調整し、Option B handoff inspection、unified draft artifact primitive、日本語ファーストguidanceを適用できるようにする | E-RQ-006, E-RQ-007, E-RQ-009, E-RQ-010, E-AC-004, E-AC-007, E-AC-008 | `iss-00273` |
| 05 | `iss-00275` / #275 | Upstream planning smoke tests と template validation の追加 | `strict` | T3 validation | templates、skills、workflow docs、scope-layering links、artifact authority、draft artifact boundary、handoff readiness、日本語ファースト authoring を検証する | E-RQ-003, E-RQ-004, E-RQ-005, E-RQ-007, E-RQ-009, E-RQ-010, E-AC-005, E-AC-007, E-AC-008 | `iss-00274` |
| 06 | `iss-00276` / #276 | Epic quality gate、manual tests、PR delivery | `critical` | T4 final delivery | Epic全体の automated / manual quality gates、pre-start draft migration確認、review repair、mergeable PR readiness を扱う | E-RQ-008, E-RQ-009, E-RQ-010, E-AC-006, E-AC-007, E-AC-008 | `iss-00275` |

## Issueリレー依存
| 先に完了するIssue | 後続Issue | バトン |
|---|---|---|
| `iss-00271` | `iss-00272` | Initiative / Epic 共通の scope 語彙と日本語ファースト guidance |
| `iss-00272` | `iss-00273` | Epic handoff package fields と template link 導線 |
| `iss-00273` | `iss-00274` | scope-layering reference、artifact authority、planning guidance |
| `iss-00274` | `iss-00275` | structural blocker / reviewer finding 分離と readiness guidance |
| `iss-00275` | `iss-00276` | focused tests / smoke / validation evidence |

## Issue引き継ぎパッケージ

### Slice 01 / `iss-00271`: Initiative 要件・設計・計画テンプレートの再設計
- parent trace:
  - E-RQ-001, E-RQ-004, E-RQ-009, E-AC-001, E-AC-007
  - design decisions: D-001, D-002, D-003, D-005, D-008
  - ADRs: architecture-neutral template policy、scope-layering reference publication、complete-understanding before canonical authoring、Japanese-first spec authoring policy
- 許可される local delta:
  - provider-side Initiative requirement / design / plan templates を更新し、strategic purpose、capability landscape、source-of-truth ownership、artifact adoption、reviewer gates、Epic handoff を表現できるようにする。
  - 日本語運用では、template本文が日本語ファーストになるよう guidance を追加する。
  - Slice 03 が `authoring/scope-layering.md` 作成後に final thin links を追加できるよう、link target / wording を準備する。
- 禁止される parent boundary change:
  - Issue grade templates を再設計しない。
  - Initiative templates に Issue-level TDD cycles、private class / file design、implementation sequencing を持ち込まない。
  - DDD / EDA を必須にしない。
  - `authoring/scope-layering.md` への dangling link を作らない。final link insertion は Slice 03 の責務とする。
- acceptance seed:
  - 新しい Initiative scaffold が、downstream implementation detail を強制せずに strategic planning と Epic handoff を表現できる。
  - templates が `artifacts/`、evidence adoption、日本語ファースト authoring、fresh reviewer gate expectations を含む。
- model / contract / lifecycle constraints:
  - Initiative は strategic change、capability landscape、context / source-of-truth、strategic invariants、transition architecture、Epic handoff を持つ。
  - Initiative は Issue implementation structure を持たない。
- expected evidence:
  - template diff、focused tests または snapshot checks、manual scaffold read-through summary。
- suggested grade:
  - `strict`
- dependencies / blockers:
  - batch Issue planning gate に依存する。`iss-00272` と語彙を合わせる。
- reviewer focus:
  - `spec-reviewer` は scope-layering、template authority、日本語ファースト authoring を確認する。
  - docs / template smoke coverage は Slice 05 で確認する。
- escalation triggers:
  - accepted ADRs を超える新しい global planning policy が必要になった場合、Epic design へ戻す、または新しい ADR candidate を作る。
- relevant artifacts:
  - `20260702t020503z-disc-phase3-initiative-epic-template-model.md`
  - `20260702t024118z-adr-architecture-neutral-template-authoring-policy.md`
  - `20260702t022907z-adr-scope-layering-reference-publication-surface.md`
  - `20260702t025127z-adr-complete-understanding-before-canonical-authoring.md`
  - `20260702t040113z-adr-japanese-first-spec-authoring-policy.md`

### Slice 02 / `iss-00272`: Epic 要件・設計・計画テンプレートの再設計
- parent trace:
  - E-RQ-001, E-RQ-004, E-RQ-006, E-RQ-009, E-AC-002, E-AC-007
  - design decisions: D-001, D-002, D-003, D-004, D-005, D-008
  - ADRs: architecture-neutral template policy、scope-layering reference publication、complete-understanding before canonical authoring、Japanese-first spec authoring policy
- 許可される local delta:
  - provider-side Epic requirement / design / plan templates を更新し、capability / model envelope、lifecycle、cross-Issue invariants、design slice catalog、Issue handoff package、suggested grade、dependencies、final quality gate を表現できるようにする。
  - 日本語運用では、Epic requirement / design / plan の本文が日本語ファーストになるよう guidance を追加する。
- 禁止される parent boundary change:
  - Issue-level implementation steps や TDD cadence を Epic templates へ移動しない。
  - decision-only Issue pattern を作らない。
  - Issue grade / TDD workflow authority を置き換えない。
- acceptance seed:
  - 新しい Epic scaffold が、parent trace、allowed local delta、forbidden parent changes、acceptance seed、expected evidence、suggested grade、dependencies、escalation triggers を含む concrete Issue handoff package を作れる。
  - 日本語運用で作成される Epic docs が、説明文としての英語混在を避ける。
- model / contract / lifecycle constraints:
  - Epic は cross-Issue model envelope と handoff を持つ。
  - Issues は local behavior deltas を持つ。
- expected evidence:
  - template diff、focused tests または snapshot checks、manual Epic scaffold read-through summary。
- suggested grade:
  - `strict`
- dependencies / blockers:
  - `iss-00271` の完了と語彙整合に依存する。
- reviewer focus:
  - `spec-reviewer` は scope ownership、artifact authority、handoff completeness、日本語ファースト authoring を確認する。
  - smoke coverage は Slice 05 で確認する。
- escalation triggers:
  - Epic template work が Issue grade template contract の変更を必要とする場合、停止して Epic design / plan へ戻す。
- relevant artifacts:
  - `20260702t020503z-disc-phase3-initiative-epic-template-model.md`
  - `20260702t020503z-02-disc-phase3-issue-slicing-handoff-model.md`
  - `20260702t024118z-adr-architecture-neutral-template-authoring-policy.md`
  - `20260702t022907z-adr-scope-layering-reference-publication-surface.md`
  - `20260702t025127z-adr-complete-understanding-before-canonical-authoring.md`
  - `20260702t040113z-adr-japanese-first-spec-authoring-policy.md`

### Slice 03 / `iss-00273`: Scope-layering reference と計画ガイダンスの更新
- parent trace:
  - E-RQ-002, E-RQ-003, E-RQ-005, E-RQ-009, E-RQ-010, E-AC-003, E-AC-007, E-AC-008
  - design decisions: D-001, D-003, D-005, D-008, D-009
  - ADRs: scope-layering reference publication、complete-understanding before canonical authoring、Japanese-first spec authoring policy、unified draft artifact command and grade role policy
- 許可される local delta:
  - `docs/authoring/scope-layering.md` を single provider-side reference として追加する。
  - Initiative / Epic planning skills と workflow / phase docs を、thin links、source-grounded clarification、evidence adoption、fresh reviewer gates、日本語ファースト authoring に合わせて更新する。
  - reference 作成後、`iss-00271` と `iss-00272` で準備した wording を使い、Initiative / Epic templates から `authoring/scope-layering.md` への final thin links を追加する。
  - artifact guidance で、interview / research / disc artifacts の本文を日本語ファーストにする方針を示す。
  - Epic planning handoff guidance に、Issue-local `draft-design` / `draft-plan` path index と、pre-start canonical Issue `design.md` / `plan.md` を本文入りdraftにしない境界を追加する。
- 禁止される parent boundary change:
  - full responsibility table を各 template / doc / skill に重複させない。
  - ADRs を日常的な operational reference surface にしない。
  - canonical single-writer authority や fresh reviewer gates を弱めない。
  - `iss-00271` / `iss-00272` が明示した follow-up 以外の template content を、thin reference links を超えて変更しない。
  - `assurance compose` を draft artifact 作成 command として説明しない。
- acceptance seed:
  - planning skills が `artifacts -> requirement -> review -> design -> review -> plan -> review -> handoff` の流れを案内する。
  - 新しい working evidence は `artifacts/` を指し、legacy `discussions/` は preservation input として扱う。
  - 日本語運用では、skills / docs が日本語の canonical docs / artifacts 作成を促す。
  - EpicからIssueへ渡す pre-start seed は、canonical `design.md` / `plan.md` ではなく Issue-local draft artifact として参照される。
- model / contract / lifecycle constraints:
  - workflow docs は lifecycle authority に留まる。
  - `scope-layering.md` は narrow scope / decision-routing reference とする。
- expected evidence:
  - docs / skills diff、link checks または grep checks、`validate`、reviewer evidence。
- suggested grade:
  - `strict`
- dependencies / blockers:
  - `iss-00271` / `iss-00272` の template vocabulary と accepted ADRs に依存する。
  - reference 作成と final thin links を同じ slice で扱うことで dangling template links を避ける。
- reviewer focus:
  - `spec-reviewer` は discoverability、authority table の重複回避、artifact authority leak、日本語ファースト authoring guidance を確認する。
- escalation triggers:
  - docs が guidance / readiness wording を超える runtime command behavior change を必要とする場合、`iss-00274` と調整する、または follow-up を作る。
- relevant artifacts:
  - `20260702t022907z-adr-scope-layering-reference-publication-surface.md`
  - `20260702t024118z-adr-architecture-neutral-template-authoring-policy.md`
  - `20260702t025127z-adr-complete-understanding-before-canonical-authoring.md`
  - `20260702t025127z-01-research-grill-with-docs-research.md`
  - `20260702t040113z-adr-japanese-first-spec-authoring-policy.md`
  - `20260702t074332z-adr-unified-draft-artifact-command-grade-role-policy.md`

### Slice 04 / `iss-00274`: Epic execution handoff と Issue準備完了workflowの更新
- parent trace:
  - E-RQ-006, E-RQ-007, E-RQ-009, E-RQ-010, E-AC-004, E-AC-007, E-AC-008
  - design decisions: D-005, D-006, D-008, D-009
  - interview / ADR: handoff inspection Option B、unified draft artifact command and grade role policy
- 許可される local delta:
  - Epic execution skill / workflow guidance を更新し、reviewer-gated Epic planning outputs を消費し、Issue start / execution routing の前に structural handoff readiness を確認する。
  - structural blockers と reviewer findings の違いを明確にする。
  - execution / readiness guidance でも、日本語運用では日本語ファースト authoring を維持するよう明示する。
  - `new artifact draft-design --issue <issue-id>` / `new artifact draft-plan --issue <issue-id>` を、Issue Start 前にも Issue-local draft artifact を作る統一 primitive として強化する。
  - `assurance compose` は canonical `design.md` / `plan.md` を作る command として保持し、draft artifact 作成には使わない。
  - handoff-ready と execution-ready を分離し、draft artifact の存在だけで Strict / Critical Issue を execution-ready にしない。
  - grade別の system-architect / implementation-planner obligation を workflow / skill / EAL / reviewer gate で管理する。
- 禁止される parent boundary change:
  - Epic execution を semantic reviewer にしない。
  - Issue planning、Issue execution、dependency checks、fresh reviewer gates を bypass しない。
  - GitHub mutation、PR merge、Issue close を行わない。
  - actor / specialist / depth 別の draft artifact command を増やさない。
  - pre-start draft artifact 作成のために canonical Issue `design.md` / `plan.md` を変更しない。
- acceptance seed:
  - missing canonical docs、stale / missing reviewer pass、missing Issue readiness contract、missing executable plan structure、unresolved EAL / Spec Authoring Gate、raw artifact authority leak、decision-only Issue treated ready は blocking になる。
  - weak but present semantic content は reviewer finding になる。
  - `new artifact draft-design` / `draft-plan` は Issue-local artifact を生成し、canonical Issue `design.md` / `plan.md` を non-mutation に保つ。
  - missing / invalid / stale assurance metadata は fail-closed になり、artifact existence だけで readiness を進めない。
- model / contract / lifecycle constraints:
  - Epic execution は coordinator / structural gate であり、semantic spec sufficiency は `spec-reviewer` が担う。
- expected evidence:
  - skill / workflow diff、振る舞い変更がある場合の focused tests、smoke read-through。
- suggested grade:
  - `strict`
- dependencies / blockers:
  - `iss-00272` の handoff fields に依存し、`iss-00273` と wording を調整する。
- reviewer focus:
  - `spec-reviewer` は lifecycle / authority correctness と日本語ファースト guidance の反映を確認する。
  - command behavior が変わる場合だけ runtime tests を追加する。
- escalation triggers:
  - readiness を skill / workflow guidance ではなく runtime command validation にする必要がある場合、Epic design に戻って implementation scope を更新する。
- relevant artifacts:
  - `20260702t030615z-interview-phase3-handoff-package-inspection-strength.md`
  - `20260702t020503z-02-disc-phase3-issue-slicing-handoff-model.md`
  - `20260702t025127z-adr-complete-understanding-before-canonical-authoring.md`
  - `20260702t040113z-adr-japanese-first-spec-authoring-policy.md`
  - `20260702t074332z-adr-unified-draft-artifact-command-grade-role-policy.md`

### Slice 05 / `iss-00275`: Upstream planningスモークテストとテンプレート検証の追加
- parent trace:
  - E-RQ-003, E-RQ-004, E-RQ-005, E-RQ-007, E-RQ-009, E-RQ-010, E-AC-005, E-AC-007, E-AC-008
  - design decisions: D-001, D-002, D-003, D-005, D-006, D-008, D-009
- 許可される local delta:
  - updated templates、scope-layering links、artifact authority、architecture-neutral wording、handoff package fields、Option B structural blocker / finding split、日本語ファースト authoring guidance、draft artifact boundary を対象に focused tests / smoke checks を追加する。
  - canonical Issue `design.md` / `plan.md` に pre-start draft body marker が残らないこと、Issue-local draft artifact path index が report / handoff に存在することを確認する。
  - `new artifact draft-design` / `draft-plan` の canonical non-mutation、missing / invalid / stale assurance fail-closed、Strict / Critical readiness gate を検証する。
- 禁止される parent boundary change:
  - brittle semantic judgments を machine-only checks として固定しない。
  - DDD / EDA terms を mandatory sections にしない。
  - raw manual-test workspaces を inspect / commit しない。
  - 技術識別子まで日本語化する machine check を入れない。
  - draft artifact の存在だけをもって Issue execution-ready と判定する check を入れない。
- acceptance seed:
  - tests / smoke checks が、missing scope-layering reference、duplicated full responsibility table、raw artifact canonical authority language、decision-only Issue ready language、missing handoff fields、mandatory DDD / EDA-only template expectation、日本語ファースト guidance の欠落、pre-start canonical draft body、draft artifact path index 欠落を検出できる。
- model / contract / lifecycle constraints:
  - machine checks は構造を扱う。
  - semantic sufficiency と自然言語品質の最終判断は reviewer が担う。
- expected evidence:
  - test diff、test command output、`validate`、必要に応じた `sync`、manual scenario summary。
- suggested grade:
  - `strict`
- dependencies / blockers:
  - `iss-00271` から `iss-00274` に依存する。
- reviewer focus:
  - `spec-reviewer` は smoke coverage relevance、false-positive risk、日本語ファースト authoring の確認粒度を確認する。
- escalation triggers:
  - tests が missing requirements または design contradictions を明らかにした場合、先へ進まず Epic design / plan に戻す。
- relevant artifacts:
  - `20260702t023036z-interview-phase3-scope-layering-review-strictness.md`
  - `20260702t020503z-03-disc-phase3-quality-delivery-gate-model.md`
  - `20260702t022907z-adr-scope-layering-reference-publication-surface.md`
  - `20260702t024118z-adr-architecture-neutral-template-authoring-policy.md`
  - `20260702t025127z-adr-complete-understanding-before-canonical-authoring.md`
  - `20260702t040113z-adr-japanese-first-spec-authoring-policy.md`
  - `20260702t074332z-adr-unified-draft-artifact-command-grade-role-policy.md`

### Slice 06 / `iss-00276`: Epic品質gate、手動テスト、PR delivery
- parent trace:
  - E-RQ-008, E-RQ-009, E-RQ-010, E-AC-006, E-AC-007, E-AC-008
  - design decisions: D-007, D-008, D-009、および final quality / test strategy に関わるすべての判断
  - delivery interview: one PR default
- 許可される local delta:
  - Epic-wide automated checks、manual tests、dogfooding inspection、review repair loop、final report updates、PR readiness preparation を実行する。
  - final gates で見つかった in-scope issues を修正する。
  - final report / PR description で、日本語ファースト authoring の確認結果を記録する。
  - final gates で、pre-start draft migration が完了し、canonical Issue `design.md` / `plan.md` に本文入り draft が戻っていないことを確認する。
  - PR description で、Issue-local draft artifacts と canonical compose / review boundary を説明する。
- 禁止される parent boundary change:
  - gate repairs を超える新機能 scope を導入しない。
  - planning に戻すべき新しい Initiative / Epic planning policy を作らない。
  - raw manual-test workspaces、fixtures、logs、captures、evidence files を commit しない。
  - 明示許可なしに PR merge や credentialed external mutation を行わない。
  - final quality gate の都合で、未開始 Issue の canonical `design.md` / `plan.md` を本文入り draft に戻さない。
- acceptance seed:
  - automated / manual gates が完了している、または failure が理由と次アクション付きで記録されている。
  - reviewer feedback が修正され、再検証されている。
  - PR description が scope、validation、manual tests、follow-ups を説明している。
  - raw manual-test files が staged されていない。
  - 日本語運用の canonical docs / artifacts が、識別子を除き日本語ファーストになっている。
  - Issue-local draft artifacts は evidence-only として残り、canonical Issue `design.md` / `plan.md` は Issue Planning の compose / review を経る。
- model / contract / lifecycle constraints:
  - final delivery は、integrated Epic diff を原則1PRとして検証する。
- expected evidence:
  - test outputs、manual scenario summary、dogfooding inspection notes、final `report.md` updates、PR readiness evidence。
- suggested grade:
  - `critical`
- dependencies / blockers:
  - `iss-00271` から `iss-00275` に依存する。
- reviewer focus:
  - `qa-reviewer` は test adequacy を確認する。
  - implementation diff が大きい場合は `code-reviewer` を使う。
  - `spec-reviewer` は requirement / design / plan fulfillment と日本語ファースト authoring を確認する。
- escalation triggers:
  - 1PR delivery が現実的でなくなった場合、証跡を記録し、`plan.md` を更新し、PR strategy 変更前に fresh reviewer gate を再実行する。
- relevant artifacts:
  - `20260702t015343z-interview-phase3-delivery-pr-boundary.md`
  - `20260702t020503z-03-disc-phase3-quality-delivery-gate-model.md`
  - `20260702t025127z-adr-complete-understanding-before-canonical-authoring.md`
  - `20260702t040113z-adr-japanese-first-spec-authoring-policy.md`
  - `20260702t074332z-adr-unified-draft-artifact-command-grade-role-policy.md`

## 共通 handoff package 項目
各 downstream Issue には次を渡す。
- parent Initiative ID と Epic ID
- 適用される parent requirement ID
- 適用される parent design ID
- Issue purpose と1つの observable outcome
- allowed local delta
- forbidden parent boundary changes
- acceptance criteria seed
- model / contract / lifecycle constraints
- expected evidence type
- suggested Issue grade
- dependencies and blockers
- required verification level
- reviewer focus
- escalation triggers
- relevant artifacts and accepted ADRs
- canonical Issue requirement state
- canonical Issue design state
- canonical Issue plan state
- Issue-local `draft-design` / `draft-plan` artifact paths
- draft artifact adoption state
- grade-specific specialist obligation
- handoff-ready / execution-ready distinction

## Option B検査方針
- blocking fail:
  - 必要な canonical requirement / design / plan が欠けている。
  - 必要な fresh `spec-reviewer` pass が欠けている、または stale である。
  - Issue readiness contract が欠けている。
  - Issue plan に executable step、delegation contract、required verification、reviewer focus が欠けている。
  - unresolved Spec Authoring Gate、または blocking / stale Evidence Adoption Ledger entry が残っている。
  - raw artifact を canonical authority として扱っている。
  - decision-only Issue を execution-ready として扱っている。
- reviewer finding / warning:
  - acceptance criteria は存在するが意味的に弱い可能性がある。
  - test strategy は存在するが範囲が不足している可能性がある。
  - target files は明示されているが妥当性に疑問がある。
  - artifact reference は存在するが根拠説明を強める余地がある。
  - 日本語ファースト guidance は存在するが、文面の徹底度に改善余地がある。
- 境界:
  - Epic execution は coordinator / structural gate であり、semantic reviewer を置き換えない。

## 統合チェックポイント
- G0 canonical plan readiness:
  - `requirement.md`、`design.md`、`plan.md` が downstream Issue planning に十分具体化されている。
  - actual Issue scaffold と Issue planning docs が Epic handoff と矛盾せず、fresh `spec-reviewer` pass に提示できる。
- G1 template boundary review:
  - Initiative / Epic templates が architecture-neutral / architecture-aware wording を使う。
  - templates が DDD / EDA、private implementation design、Issue-level TDD cycles を強制しない。
- G2 scope-layering and authority review:
  - `docs/authoring/scope-layering.md` が single provider-side reusable reference として存在する。
  - workflow docs / phase docs / skills / templates は full responsibility model を重複させず薄くリンクする。
  - raw artifacts は canonical authority として扱われない。
- G3 handoff readiness review:
  - Epic plan と Epic execution guidance が handoff package fields、suggested grades、dependencies、verification expectations、Option B inspection policy を含む。
  - Issue-local draft artifacts は evidence-only として path index に記録され、canonical Issue `design.md` / `plan.md` は `assurance compose` まで placeholder である。
  - handoff-ready と execution-ready が区別され、Strict / Critical は specialist obligation と fresh reviewer gate を要求する。
- G4 日本語ファースト authoring review:
  - requirement / design / plan / report / artifacts guidance が、日本語運用で本文を日本語ファーストにすることを示す。
  - 許容される英語は、識別子、コマンド、固定語、外部固有名詞に限定される。
- G5 integrated smoke matrix:
  - template shape、planning skill wording、workflow links、artifact guidance、execution handoff、日本語ファースト guidance をまとめて確認する。
  - `new artifact draft-design` / `draft-plan`、canonical non-mutation、pre-start draft body absence、draft artifact path index、stale assurance fail-closed を確認する。
- G9 final quality / PR readiness:
  - `iss-00276` が `iss-00271` から `iss-00275` の完了または明示的 defer、automated / manual gates、review repairs、one-PR delivery readiness を確認する。

## 品質ゲート
- suggested automated gates:
  - `uv run pytest tests/unit`
  - `uv run pytest tests/cli_runtime`
  - `make lint`
  - `uv run pytest`
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync`
- command policy:
  - repository で利用可能な既存 command を使う。
  - command が利用不可、不適切、または unrelated baseline reason で失敗する場合は、command、exit / result、理由、次アクションを `report.md` に記録する。
- scope-layering structural fail checks:
  - provider docs が local artifact paths を provider authority として使っていないこと。
  - `authoring/scope-layering.md` への required inbound links が存在すること。
  - full responsibility table が templates / docs / skills に重複していないこと。
  - templates が長い scope table を埋め込んでいないこと。
  - decision-only Issues が execution-ready と説明されていないこと。
  - raw artifacts が canonical authority と説明されていないこと。
- 日本語ファースト checks:
  - 新規・更新 templates / skills / docs / artifact guidance が、日本語運用で日本語本文を促していること。
  - file paths、commands、code identifiers、SpecDock fixed terms、external proper nouns は原文保持を許容していること。
  - 説明文が英語本文のまま残る場合は reviewer finding とし、template / skill guidance の欠落なら blocking とする。

## 手動テスト
- setup:
  - local trial workspaces は `manual-tests/` のみを使う。
  - SpecDock state が必要な場合、trial directory 内に独立した Git repository を初期化する。
  - parent repository の git history、index、active SpecDock state を test data として使わない。
  - raw manual-test workspaces、fixtures、logs、captures、evidence files を commit しない。
  - 有用な証跡は `report.md` または scope-local artifact に要約する。
- minimum scenarios:
  1. 新しい Initiative scaffold が updated Initiative templates を使う。
  2. 新しい Epic scaffold が updated Epic templates を使う。
  3. Initiative templates が Issue-level TDD cycles を含まない。
  4. Epic templates が Issue handoff と suggested grade fields を含む。
  5. Initiative planning skill が `artifacts -> requirement -> review -> design -> review -> plan -> review -> Epic handoff` を案内する。
  6. Epic planning skill が `artifacts -> requirement -> review -> design -> review -> plan -> review -> Issue handoff` を案内する。
  7. Epic execution skill が handoff / execution coordinator として読める。
  8. `artifacts/` が新しい working artifacts の推奨先になっている。
  9. legacy `discussions/` が primary new working artifact destination として推奨されていない。
  10. 日本語運用で作成される requirement / design / plan / report / artifacts の本文が日本語ファーストになる。
  11. generated / dogfooding docs が validate / sync 後も coherent である。

## 課題準備完了条件
- actual downstream Issues は作成済みである。実行へ進める前に満たすこと:
  - canonical `requirement.md`、`design.md`、`plan.md` が fresh reviewer-gated adoption 済みである、または明示的な non-promotion state が記録されている。
  - provisional six-Issue baseline が、採用済み flexibility gate なしに変更されていない。
  - `report.md` EAL に、planning / handoff に影響する unresolved `blocked` または `stale` entry がない。
- 各 Issue が ready と言える条件:
  - 1つの coherent observable outcome がある。
  - 適用される E-RQ / E-AC links が分かっている。
  - parent requirement / design constraints が分かっている。
  - allowed local delta と forbidden parent changes が明示されている。
  - suggested grade が分かっている。
  - dependencies と blockers が列挙されている。
  - required verification と reviewer focus が列挙されている。
  - relevant artifacts / ADRs がリンクされている。
  - major open questions が解消されている、または明示的に scope 外にされている。

## 最終delivery Issue
- `iss-00276` は意図的に `critical` quality / delivery Issue とする。
- `iss-00276` が持つもの:
  - Epic全体の検証
  - 自動チェック
  - 利用可能な static analysis
  - SpecDock validate / sync evidence
  - 手動テスト
  - dogfooding workspace inspection
  - provider と dogfooding mirror の差分確認
  - documentation / template / skill consistency review
  - 日本語ファースト authoring review
  - review feedback repair loop
  - final report evidence
  - PR readiness checklist
  - active environment で許可される場合の PR creation
- `iss-00276` が持たないもの:
  - gates で見つかった修正を超える新機能scope
  - 新しい Initiative / Epic planning decisions
  - 破壊的操作
  - 明示許可のない credentialed external mutation
  - 明示許可のない PR merge

## 最終完了条件
- `iss-00271` から `iss-00276` が完了している、または defer が明示的な証跡と main orchestrator の受容を持つ。
- Initiative / Epic templates が provider-side scaffold assets で更新されている。
- planning / execution skills と docs が、更新後の templates と accepted ADRs に整合している。
- 日本語運用の requirement / design / plan / report / artifacts 作成導線が、日本語ファースト authoring を促す。
- automated checks が通っている、または failure が許容理由と follow-up 付きで記録されている。
- manual tests が実行され、要約されている。
- raw manual-test files が commit されていない。
- dogfooding mirror impact が確認されている。
- reviewer comments が修正され、影響する checks が再実行されている。
- PR description が scope、validation、manual tests、follow-ups を含む。
- PR は review / merge ready である。merge は明示許可なしに行わない。

## 依存 / ブロッカー
- D-001:
  - `iss-00271` から `iss-00276` の batch Issue planning docs を実行入力として扱う前に、fresh `spec-reviewer` pass が必要である。
- D-002:
  - actual Issue IDs は `iss-00271` から `iss-00276` として確定済みである。再分割する場合はこの plan と dependency chain を更新し、fresh review を通す。
- D-003:
  - generated readiness projections を証跡として使う前に `./spec-dock/scripts/spec-dock sync` を実行する。

## 未確定事項
- なし:
  - 既存 interviews と accepted ADRs により、Issue slicing、PR boundary、canonical detail、scope-layering publication、architecture-neutral template policy、complete understanding policy、Option B handoff inspection policy、日本語ファースト authoring policy は解決済みである。
