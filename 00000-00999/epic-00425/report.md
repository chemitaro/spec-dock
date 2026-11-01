---
種別: レポート（Epic）
ID: "epic-00425"
タイトル: "Build Html Spec Dashboard And Cue Documents"
関連GitHub: ["#425"]
最終更新: "2026-11-01"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["init-00423"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

I-1〜I-6 の実装と 0.4.0 の公開、I-7 の spec-dock での導入まで終えた（2026-11-01）。

| Issue | PR | マージのコミット |
|---|---|---|
| I-1 #472 CUE の型 v1 | #480 | `2cf4e961a` |
| I-4 #475 デザインシステム | #479 | `056f070f0` |
| I-2 #473 `scope check`・`work finish`・`scope show`・`workspace validate`/`doctor` | #483 | `418c1f87b` |
| I-5 #476 `render_scope_html` と `scope render` | #484 | `411261e59` |
| I-3 #474 `--assurance` 付きの雛形 | #485 | `d53b24d64` |
| I-6 #477 文書、スキル、0.4.0 | #486 | `7f3cf7d3c`（タグ `v0.4.0`） |
| I-7 の試しの Issue #487 | #488 | `c43aadd5b` |

### I-7 spec-dock での導入（AC-14）

- 2026-11-01、利用者の承認で、利用者の PC に `cue` 0.17.1（Homebrew）と SpecDock 0.4.0（タグ `v0.4.0` から作った wheel、`uv tool install --force`）を入れた。spec-dock（版4）と company-os（版3）で `workspace validate` が通る。
- spec-dock の配布資産は、各 PR が dogfood の写しを更新していたので、`installation update --dry-run` で差分がなかった（PR は作らない）。
- 今の `.md` の雛形は外さなかった。0.4.0 でも版3のリポジトリの `scope create` が使うので、epic-00424 の I-13（0.5.0）で外す（2026-11-01 に利用者が決めた。要件の R-H3、設計、計画、epic-00424 の計画・設計・要件を直した）。
- 実際の Issue #487（iss-00487、Polish CUE Authoring Guides And Leaf Help、light）を、0.4.0 の `scope create issue --assurance light` で CUE の雛形から作り、作業担当（opus / medium）が CUE の仕様で書き、仕様のレビュー、実装、コードのレビュー、最終品質ゲート、PR #488 まで回した。マージの後、統括が 0.4.0 の `work finish`（説明資料と CUE の検査を含む）で閉じた。詳しい記録は `iss-00487/report.md` の「CUE の仕様の試し」。

### 試しで分かったこと（`iss-00487/report.md` の要約）

- 書きやすさ：雛形のコメントと `cue.md` で迷わず書け、最初の `scope check` が通った。番号のキーと参照（`realizes`、`verifies`、`satisfies`）のつながりを検査に任せられ、仕様を書いて検査を通すまで約15分と、同じ規模の Markdown より短く感じた。計画の台帳、`execution`、説明資料の雛形の印の警告も役に立った。
- 書きにくさ：`status` を書く位置が自由で、同じ値が2つ入っても CUE は黙ってまとめる。既定値のある列挙の打ち間違いで、既定値との「conflicting values」の行が先に出て紛らわしい。`CUE_INVALID` の `hint` だけ英語。`scope render` の HTML は、デザインシステムを `file://` の絶対の道筋で読むので、別の機械では崩れる。

## Verification

- I-1〜I-6、#487：各 Issue の `report.md` に、仕様のレビュー、コードのレビュー、最終品質ゲート（`make lint`、`uv run pytest`）、PR の CI の結果がある。
- I-7：本物のカタログでの `scope create`（GitHub への作成、親への sub-issue、CUE の雛形）、`scope check iss-00487`（誤り0、警告0）、`scope render`、`work finish iss-00487`（Issue を閉じた）を、0.4.0 で確かめた。

## Residual Risks / Follow-ups

- 試しの改善の提案（`iss-00487/report.md`。優先度順）：(高) 既定値のある列挙の誤りの文の整理、(中) `CUE_INVALID` の `hint` の日本語化、(中) 雛形の手順の例で `status` を前に置く、(低) light でテストが1つもないことの情報、(低) `scope render` のデザインシステムの埋め込み・相対の道筋。まだ Issue にしていない。
- #487 の FQG-001（P3）：`-y` を help 用に argparse へ登録したため、`-yy` が誤りでなく受理になる（`--yes` の効果は付かない。安全側）。
- 未確認：祖先の `cue.mod` の評価への影響、`cue` の新しい版での誤りの文の形、`scope render` の `vendor_base` を渡した描画とブラウザーでの目視。
- `.md` の雛形の削除は epic-00424 の I-13 に移した。ほかの4つのリポジトリの `installation update` は、利用者の判断（epic-00424 の I-12 で 0.4.0 以上に上がる）。
