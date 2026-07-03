---
種別: 実装計画書（Issue）
ID: "iss-00274"
タイトル: "Update Epic Execution Handoff And Issue Readiness Workflow"
関連GitHub: ["#274"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
依存: ["requirement.md", "design.md"]
親: ["epic-00270", "init-local-00003"]
---

# iss-00274 Epic execution handoff と Issue readiness workflow 更新 — Issue 実装計画

## 文書の位置づけ
- この文書は `iss-00274` の正規 Issue 実装計画書である。
- 承認済みの要件・設計を、Red / characterization / implementation / verification / review / finish の順で実行可能な手順へ落とす。
- 実行中の観測結果、逸脱、判断、検証証跡は `report.md` に記録する。
- この Issue では PR を作成しない。最終PRは `iss-00276` で作成する。

## 実装戦略
- まず現行 skill / docs の不足を characterization する。
- runtime behavior 変更が必要かどうかを早期に判定する。
- 中心変更は provider-side skill / workflow docs の最小更新とする。
- dogfooding copy は、実際の active entrypoint と provider asset の drift を避けるため、この Issue で同期対象に含める。
- fresh `spec-reviewer` を通すまでは execution-ready と扱わない。

## 許可変更面
| 種別 | パス | 変更方針 |
|---|---|---|
| provider skill | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md` | Epic execution readiness guidance を更新する。 |
| dogfooding skill | `.agents/skills/spec-dock-epic-execution/SKILL.md` | provider skill と同内容に同期する。 |
| workflow docs | `src/spec_dock/assets/spec_dock/docs/workflow_epic.md` | Epic planning handoff と Epic execution lifecycle の接続を補強する。 |
| workflow docs | `src/spec_dock/assets/spec_dock/docs/workflow_issue.md` | Issue Planning / execution-ready への参照と draft adoption 境界を補強する。 |
| authoring docs | `src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md` | 必要時のみ薄いリンク・文言補強を行う。 |
| runtime / tests | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`, `tests/cli_runtime/`, `tests/unit/` | S02 で不足が確認された場合だけ focused change を追加する。 |
| Issue docs | `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00270-upstream-planning-governance-and-templates/issues/iss-00274-update-epic-execution-handoff-and-issue-readiness-workflow/` | planning / execution evidence を記録する。 |

## 禁止変更
| 対象 | 禁止理由 | 必要になった場合 |
|---|---|---|
| actor / specialist / depth 別 draft command | accepted ADR に反する。command は authorship を保証できない。 | 停止し、Epic / ADR レベルで再判断する。 |
| `assurance compose` の draft artifact 作成化 | canonical compose と evidence artifact creation の境界が崩れる。 | 停止し、再設計する。 |
| dependency algorithm / Issue grade template の大規模再設計 | この Issue の範囲を超える。 | 後続Issueまたは新Issueへ分離する。 |
| credentialed GitHub mutation / PR creation / PR merge | final delivery は `iss-00276` の責務。 | `iss-00276` まで待つ。 |
| raw artifact を canonical authority とする変更 | scope-layering と EAL の前提に反する。 | reviewer blocker として止める。 |

## マイルストーン
| ID | 成果 | 関連Step | 主なClosure |
|---|---|---|---|
| M0 | 現行不足とRed代替証跡を固定する。 | S01 | `I274-AC-001..009` |
| M1 | docs / skills-only で足りるか runtime change が必要か判定する。 | S02 | `I274-AC-007..009`, `I274-EC-004` |
| M2 | Epic execution skill と workflow docs を更新する。 | S03-S04 | `I274-AC-001..009` |
| M3 | grep / read-through / focused tests / validate で closure を確認する。 | S05-S06 | all AC / EC |
| M4 | fresh reviewer gate を通す。 | S07 | `I274-EC-001..003` |
| M5 | report evidence を閉じ、PRなしで `issue finish` する。 | S08 | `I274-AC-005`, `I274-EC-004` |

## Closure Index
| Closure | 要件 | 設計ID | 検証 |
|---|---|---|---|
| `C274-001` | `I274-AC-001` | `D274-001` | skill / workflow read-through、grep、reviewer。 |
| `C274-002` | `I274-AC-002` | `D274-002` | structural blocker list の存在確認、reviewer。 |
| `C274-003` | `I274-AC-003`, `I274-EC-001`, `I274-EC-003` | `D274-003` | semantic reviewer 非代替と reviewer finding 境界の確認。 |
| `C274-004` | `I274-AC-004`, `I274-EC-002` | `D274-004` | raw artifact authority / decision-only ready 禁止の確認。 |
| `C274-005` | `I274-AC-005`, `I274-EC-004` | `D274-005`, `D274-011` | no per-Issue PR と `iss-00276` final delivery の確認。 |
| `C274-006` | `I274-AC-006` | `D274-006` | 日本語ファースト guidance の確認。 |
| `C274-007` | `I274-AC-007`, `I274-AC-008` | `D274-008`, `D274-010` | `new artifact draft-*` / `assurance compose` 境界の確認。 |
| `C274-008` | `I274-AC-009` | `D274-009`, `D274-010` | handoff-ready / execution-ready と specialist obligation の確認。 |

## 実装ステップ

以下の `S01..S08` を、この Issue の実行可能な workflow contract とする。

### S01 Red / characterization baseline
- 種別: `characterization-first` / `inspect-only`。
- 目的: 現行 `spec-dock-epic-execution` skill / workflow docs が、Issue handoff package、structural blocker / reviewer finding split、draft artifact primitive、handoff-ready / execution-ready split を十分に案内しているか確認する。
- 期待される不足:
  - 必須語彙または禁止導線が不足している。
  - no per-Issue PR / `iss-00276` final delivery の説明が曖昧である。
- コマンド:
  - `rg -n "handoff-ready|execution-ready|structural blocker|reviewer finding|draft-plan|draft-design|iss-00276|issue finish" src/spec_dock/assets/spec_dock/docs src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md .agents/skills/spec-dock-epic-execution/SKILL.md`
- 証跡: `report.md` の Step Evidence に不足と判断を記録する。

### S02 Runtime change 要否判定
- 目的: docs / skills-only で閉じられるか、runtime behavior / tests が必要かを決める。
- docs / skills-only とする条件:
  - 既存 `new artifact draft-design` / `draft-plan` が Issue-local artifact 作成 surface として存在する。
  - この Issue の要求が command behavior ではなく workflow / skill guidance で満たせる。
- runtime change を追加する条件:
  - `new artifact draft-*` が canonical docs を変更してしまう。
  - Issue-local `artifacts/` に作れない。
  - `assurance compose` との境界を runtime が誤誘導している。
  - no-write fail-closed が必要な箇所で実装不足が確認される。
- 証跡: 採用した path、選ばなかった path、必要な検証レベルを `report.md` に記録する。

### S03 Epic execution skill 更新
- 担当: `doc-writer` に委譲する。
- 対象:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md`
  - `.agents/skills/spec-dock-epic-execution/SKILL.md`
- 変更内容:
  - first-read input に reviewer-gated Epic docs と Issue handoff package を追加する。
  - structural blocker と reviewer finding を分ける。
  - missing / stale reviewer pass、missing executable plan structure、missing delegation contract、missing verification、missing reviewer focus、unresolved blocking report entries を fail-closed として扱う。
  - raw artifact authority leak、decision-only execution-ready、semantic reviewer 代替を禁止する。
  - no per-Issue PR / `iss-00276` final PR delivery を明示する。
  - 日本語ファースト authoring を execution / readiness 中の docs / report / artifacts に適用する。

### S04 Workflow docs 更新
- 担当: `doc-writer` に委譲する。
- 対象:
  - `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - 必要時のみ `src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md`
- 変更内容:
  - Epic execution lifecycle に handoff inspection と Issue readiness structural gate を置く。
  - `new artifact draft-design --issue <issue-id>` / `new artifact draft-plan --issue <issue-id>` を pre-start Issue handoff artifact primitive として明記する。
  - `assurance compose` は canonical compose 専用であり、draft artifact 作成 command ではないことを残す。
  - actor / specialist / depth 別 draft command を増やさない。

### S05 Docs / skills consistency verification
- コマンド:
  - `rg -n "structural blocker|reviewer finding|handoff-ready|execution-ready|draft-design|draft-plan|assurance compose|iss-00276|issue finish" src/spec_dock/assets/spec_dock/docs src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md .agents/skills/spec-dock-epic-execution/SKILL.md`
  - `rg -n "semantic reviewer|spec-reviewer|raw artifact|decision-only|日本語ファースト" src/spec_dock/assets/spec_dock/docs src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md .agents/skills/spec-dock-epic-execution/SKILL.md`
  - `./spec-dock/scripts/spec-dock validate`
- 証跡: `C274-001..008` と対応させて `report.md` に残す。

### S06 Conditional runtime / test verification
- S02 で runtime change required と判断した場合だけ実施する。
- 担当: `dev-coder` に委譲する。
- 対象:
  - focused runtime code under `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`
  - focused tests under `tests/cli_runtime/` or `tests/unit/`
- コマンド候補:
  - `uv run pytest tests/cli_runtime`
  - `uv run pytest <focused-test-path>`
  - `./spec-dock/scripts/spec-dock validate`
- S02 で docs / skills-only と判断した場合は、実施しない理由を `report.md` に記録する。

### S07 Fresh review gate
- docs / skills-only diff:
  - fresh `spec-reviewer` を通す。
- runtime / tests diff がある場合:
  - `code-reviewer` と `qa-reviewer` を追加し、workflow contract が変わった場合は `spec-reviewer` も再実行する。
- reviewer focus:
  - lifecycle / authority correctness。
  - structural blocker と reviewer finding の分離。
  - `spec-reviewer` 非代替。
  - draft artifact primitive と canonical non-mutation。
  - no per-Issue PR / `iss-00276` final delivery。
  - 日本語ファースト guidance。

### S08 Finish / handoff
- 前提:
  - `C274-001..008` が閉じている。
  - fresh reviewer gate が `passed`。
  - `./spec-dock/scripts/spec-dock validate` が成功している、または失敗理由と次アクションが明確である。
  - 作業ツリーに意図しない差分がない。
- コマンド:
  - `git status --short`
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock issue finish`
- 後続:
  - `iss-00275` に、changed paths、S02 scope decision、grep/read-through結果、validate結果、reviewer verdict、closure index result を渡す。

## レビュー前完了条件
- canonical `design.md` / `plan.md` が template-only ではなく、要件・ADR・specialist drafts を統合している。
- `report.md` の EAL に pre-start seed、system-architect draft、implementation-planner draft の採用判断がある。
- `assurance verify`、`validate`、`git diff --check` が成功している。
- fresh `spec-reviewer` に渡す reviewer focus が明示されている。

## 最終完了条件
- `I274-AC-001..009` と `I274-EC-001..004` が evidence 付きで閉じている。
- S02 の docs / skills-only または runtime-required 判定が記録されている。
- 必要な reviewer gate が fresh `passed` である。
- この Issue で PR を作っていない。
- `issue finish` が成功し、後続 `iss-00275` へ引き渡せる。
