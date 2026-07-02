---
種別: draft-design
ID: "20260702t081010z-draft-design"
タイトル: "Epic Quality Gate Manual Tests And PR Delivery draft-design pre-start seed"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["iss-00276", "epic-00270"]
authority: "evidence"
not_canonical: true
scope_type: "issue"
scope_id: "iss-00276"
draft_lifecycle_state: "migrated_from_misplaced_canonical"
draft_origin: "pre_start_canonical_body_migration"
source_paths: ["old canonical design.md body before placeholder restore", "../requirement.md", "../report.md#EAL-00276-DESIGN", "../../../requirement.md", "../../../design.md", "../../../plan.md"]
intended_targets: ["design.md"]
adoption_status: "unreviewed"
reflected_to: []
---

# iss-00276 Epic Quality Gate Manual Tests And PR Delivery — draft-design pre-start seed

## 移行メモ

この artifact は、accepted ADR `20260702t074332z-adr-unified-draft-artifact-command-grade-role-policy.md` に従い、Issue Start 前に canonical `design.md` に置かれていたドラフト本文を Issue-local evidence として退避したものです。

- authority: evidence only（証跡のみ）
- canonical adoption: Issue Start 後に Issue Planning の EAL で adopted / partially_adopted / rejected / stale / blocked を判断する（このartifact単体では正本化しない）
- original source: placeholder復元前に canonical `design.md` に置かれていた旧本文
- specialist obligation: specialist output がない場合は原則 blocked。manual fallback は明示的 risk acceptance と追加 gate が必要

## 移行前本文

---
種別: 設計書ドラフト（Issue）
ID: "iss-00276"
タイトル: "Epic Quality Gate Manual Tests And PR Delivery"
関連GitHub: ["#276"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
依存: ["requirement.md"]
親: ["epic-00270", "init-local-00003"]
artifact_state: "draft-before-issue-start"
---

# iss-00276 Epic品質gate、手動テスト、PR delivery — 設計ドラフト

## ドラフト扱い
- この設計書は先行ドラフトであり、実行開始前に正規設計へ更新する。
- 前段 Issue の実際の変更、検証結果、未解決リスクを読んでから final gate の詳細を確定する。

## 設計方針
- この Issue は final integrator であり、新しい feature scope を増やす Issue ではない。
- Automated checks、manual checks、reviewer gates、PR readiness を `report.md` に統合して証跡化する。
- 1PR delivery を既定とし、分割が必要な場合は Epic plan amendment と fresh review を先に行う。
- Manual evidence は summary を report に残し、raw workspace / logs は commit しない。
- PR作成後の merge / closeout はユーザーの明示指示に従う。

## 変更対象候補
| 対象 | 変更意図 |
|---|---|
| `spec-dock/initiatives/.../epic-00270/report.md` | final evidence、validation、manual test、reviewer result、PR readiness を記録する。 |
| 前段で変更された provider assets / tests | final gate で見つかった in-scope repair のみ行う。 |
| PR metadata | scope / validation / risks / follow-up を説明する。 |
| tracked workspace | raw manual files が staged されていないことを確認する。 |

## 要件から設計への対応
| 要件 | 設計対応 |
|---|---|
| `I276-AC-001` | 前段 Issue reports と completion state を final gate の入力にする。 |
| `I276-AC-002` | automated checks / validate の結果を report に記録する。 |
| `I276-AC-003` | manual dogfooding summary を report に残し raw files を除外する。 |
| `I276-AC-004` | `spec-reviewer` で Epic fulfillment / 日本語ファーストを確認する。 |
| `I276-AC-005` | 必要に応じて `qa-reviewer` / `code-reviewer` を使う。 |
| `I276-AC-006` | PR description を開発記録として作成する。 |
| `I276-AC-007` | PR分割が必要なら plan amendment を先に行う。 |
| `I276-AC-008` | 日本語ファースト逸脱の最終確認を行う。 |

## 依存関係
- `iss-00271` から `iss-00275` の完了証跡に依存する。
- この Issue の後続は PR workflow であり、merge / closeout は別指示を待つ。

## 検証戦略
- 前段が実行した focused tests を再実行または確認する。
- Full baseline が現実的なら実行し、重い / 不適切な場合は理由と代替確認を report に残す。
- Manual dogfooding は、new templates / docs / skills / handoff readiness / Japanese-first guidance の read-through と必要な command smoke を対象にする。
- reviewer gate は failure を隠さず、repair loop と再検証を report に残す。

## 実行時に正規化する論点
- 実際に実行する test command の最小集合。
- PR作成前に必要な reviewer role と fallback。
- 1PR delivery が維持できるかどうか。
