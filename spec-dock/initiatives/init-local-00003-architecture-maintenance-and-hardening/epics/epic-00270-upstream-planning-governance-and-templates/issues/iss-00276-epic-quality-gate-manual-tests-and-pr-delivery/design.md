---
種別: 設計書（Issue）
ID: "iss-00276"
タイトル: "Epic Quality Gate Manual Tests And PR Delivery"
関連GitHub: ["#276"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
依存: ["requirement.md"]
親: ["epic-00270", "init-local-00003"]
---

# iss-00276 Epic品質gate、手動テスト、PR delivery — 設計

## 0. 文書の位置づけ
- この文書は `iss-00276` の正規設計である。
- Runtime `authorized_profile=standard` は compose template authority として扱う。ただし Issue 要件と Epic plan はこの Issue を `critical` final delivery gate として定義しているため、実行・レビュー・PR delivery の証跡義務は critical 相当に引き上げる。
- Pre-start の `draft-design` / `draft-plan` と specialist draft は evidence-only input であり、正本 authority、reviewer pass、execution readiness を単独では与えない。

## 1. 設計目的
- `iss-00271` から `iss-00275` の成果を統合し、Epic 全体の automated checks、manual dogfooding、reviewer gates、PR readiness を一つの最終品質gateとして閉じる。
- 新しい upstream planning policy や新機能を追加するのではなく、これまでの変更が Epic requirement / design / plan を満たしていることを証跡化する。
- 原則1PR delivery を維持し、PR 作成後は merge-prepared evidence を得る。ただし PR merge、GitHub Issue close、post-merge cleanup はこの Issue の暗黙作業に含めない。

## 2. 正本・根拠
| 種別 | パス・識別子 | この Issue への意味 |
|---|---|---|
| Issue requirement | `requirement.md` | `I276-AC-001..011` と `I276-EC-001..005` の正本。 |
| Epic requirement | `epic-00270/requirement.md` | `E-RQ-008..010`, `E-AC-006..008` を final gate で閉じる。 |
| Epic design | `epic-00270/design.md` | `D-007` one-PR delivery、`D-008` 日本語ファースト、`D-009` draft artifact / grade-aware role policy を継承する。 |
| Epic plan | `epic-00270/plan.md` | Slice 06 として final quality / PR delivery の責務を定義する。 |
| Epic report | `epic-00270/report.md` | EAL、前段 Issue 状態、E-AC 達成状況を更新する対象。 |
| 前段 reports | `iss-00271..iss-00275/report.md` | completion evidence、verification、reviewer gate、未解決 risk の入力。 |
| Pre-start draft artifacts | `artifacts/20260702t081010z-*`, `artifacts/20260702t081011z-*` | 旧 canonical body の退避 evidence。採用可否は report EAL に記録する。 |
| Specialist drafts | `artifacts/20260702t122432z-*` | 正規設計・計画の構造入力。最終 authority ではない。 |

## 3. 要件から設計への追跡
| 要件 | 設計ID | 設計上の扱い |
|---|---|---|
| `I276-AC-001` | `D276-001`, `D276-004` | 前段 Issue の完了 / defer / unresolved blocker を分類して report に記録する。 |
| `I276-AC-002` | `D276-002`, `D276-006` | automated checks と `validate` / `assurance verify` を実行し、結果を証跡化する。 |
| `I276-AC-003` | `D276-003`, `D276-005` | manual dogfooding / read-through summary を残し、raw manual files を commit しない。 |
| `I276-AC-004` | `D276-007`, `D276-010` | fresh `spec-reviewer` が Epic fulfillment と日本語ファースト authoring を確認する。 |
| `I276-AC-005` | `D276-007` | `qa-reviewer` と、必要に応じた `code-reviewer` で検証十分性と diff risk を確認する。 |
| `I276-AC-006` | `D276-008` | PR description に scope、背景、変更内容、影響範囲、検証、risk、follow-up を含める。 |
| `I276-AC-007` | `D276-008`, `D276-009` | 1PR が破綻する場合は PR 分割前に Epic plan amendment と fresh review に戻る。 |
| `I276-AC-008` | `D276-010` | canonical docs / artifacts の本文を日本語ファーストで確認する。 |
| `I276-AC-009` | `D276-001`, `D276-010` | 前段 completion evidence と pre-start draft migration 完了を確認する。 |
| `I276-AC-010` | `D276-010` | canonical Issue `design.md` / `plan.md` に misplaced draft body が戻っていないことを確認する。 |
| `I276-AC-011` | `D276-008`, `D276-011` | PR description で handoff-ready / execution-ready boundary、draft adoption、final validation を説明する。 |
| `I276-EC-001` | `D276-001`, `D276-009` | 前段未完了を理由なしで無視して PR を作らない。 |
| `I276-EC-002` | `D276-006`, `D276-007` | failing checks を隠して readiness を主張しない。 |
| `I276-EC-003` | `D276-003`, `D276-009` | final gate repair を超える新規 scope を導入しない。 |
| `I276-EC-004` | `D276-005` | raw manual workspace、temporary logs、local-only artifacts を staged / commit しない。 |
| `I276-EC-005` | `D276-011` | PR merge や GitHub Issue close を暗黙作業にしない。 |

## 4. 設計契約
| 設計ID | 固定度 | 設計契約 |
|---|---|---|
| `D276-001` | `[N]` | `iss-00276` は final integrator であり、前段 Issue の成果を分類して Epic delivery readiness を判定する。 |
| `D276-002` | `[N]` | automated verification は broad suite と SpecDock validation を含め、未実施の場合は理由と残リスクを report に残す。 |
| `D276-003` | `[N]` | 変更面は final gate repair、Issue / Epic report、PR metadata に限定する。新規 policy / feature scope は禁止する。 |
| `D276-004` | `[N]` | 前段 Issue reports、dependency state、recent commits を照合し、古い report 文言より current lifecycle evidence を優先する。 |
| `D276-005` | `[N]` | manual dogfooding は summary-only evidence とし、raw workspaces / logs / captures / temporary artifacts は commit しない。 |
| `D276-006` | `[N]` | failure、reviewer finding、observation blocker は隠さず report に記録し、in-scope repair 後に再検証する。 |
| `D276-007` | `[N]` | fresh `spec-reviewer`、`qa-reviewer`、必要時 `code-reviewer` を gate とする。worker output は reviewer pass の代替にしない。 |
| `D276-008` | `[N]` | PR は原則1PR。PR description は delivery record として scope、検証、risk、draft / readiness boundary を説明する。 |
| `D276-009` | `[N]` | 1PR delivery が破綻する場合は、PR split 前に Epic plan update と fresh review を行う。 |
| `D276-010` | `[N]` | 日本語ファーストと draft artifact boundary を final manual / reviewer gate に含める。 |
| `D276-011` | `[N]` | PR 作成後の observation / repair は `github-pr-merge-preparer` の境界で扱い、merge / closeout は行わない。 |

## 5. 許可変更面と禁止変更
| 区分 | 対象 | 扱い |
|---|---|---|
| 許可 | `iss-00276/design.md`, `plan.md`, `report.md` | 正規 planning、execution evidence、reviewer gate、PR readiness を記録する。 |
| 許可 | `epic-00270/report.md` | final E-AC status、manual summary、reviewer / PR readiness evidence を更新する。 |
| 条件付き許可 | provider assets、dogfooding mirror、tests | final gate で発見した in-scope repair のみ最小修正する。 |
| 許可 | PR title / body / metadata | delivery record として作成する。 |
| 禁止 | new upstream planning policy / new feature scope | Epic plan amendment と fresh review なしでは導入しない。 |
| 禁止 | raw manual workspaces、logs、captures、temporary files | staged / committed にしない。 |
| 禁止 | PR merge、GitHub Issue close | ユーザー明示指示があるまで行わない。 |

## 6. Evidence flow
```text
iss-00271..iss-00275 reports
  -> completion / blocker audit
  -> automated verification
  -> manual dogfooding summary
  -> reviewer gates and repair loop
  -> iss-00276/report.md
  -> epic-00270/report.md
  -> PR description
  -> PR observation / merge-preparer evidence
```

## 7. 検証戦略
- Automated:
  - `uv run pytest tests/unit`
  - `uv run pytest tests/cli_runtime`
  - 必要に応じた `uv run pytest`
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock assurance verify`
  - `git diff --check`
  - `git status --short`
- Manual:
  - Initiative / Epic templates、workflow docs、planning / execution skills、scope-layering reference の read-through。
  - `draft-before-issue-start` が canonical `design.md` / `plan.md` に戻っていないことの grep。
  - 日本語ファースト本文と識別子保持の境界確認。
- Reviewer:
  - `spec-reviewer`: Epic / Issue fulfillment、draft boundary、日本語ファースト、PR readiness。
  - `qa-reviewer`: automated / manual validation の十分性。
  - `code-reviewer`: material implementation diff がある場合の regression / scope leak review。
  - `github-pr-merge-preparer`: PR 作成後の CI / review / merge-prepared evidence。

## 8. 失敗時の扱い
- In-scope failure は最小 repair、該当 check 再実行、fresh re-review で閉じる。
- Scope expansion、PR split、new policy、destructive operation が必要な場合は停止し、Epic plan update / user decision / fresh review へ戻る。
- Reviewer 利用不可や observation limitation は pass とみなさず、risk / blocker / next action として report に残す。

## 9. PR boundary
- PR 作成は `iss-00276` の最終段階でのみ行う。
- PR description は、IssueごとのPRを作らずにバトンをつないだ理由、handoff-ready / execution-ready boundary、draft artifact adoption、final validation、manual summary、remaining risk を説明する。
- `merge-prepared` は PR observation と blocking finding / required CI の状態に基づく。PR merge は行わない。
