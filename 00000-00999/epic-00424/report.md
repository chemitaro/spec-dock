---
種別: レポート（Epic）
ID: "epic-00424"
タイトル: "Centralize Specs On Canonical Branch And GitHub Issues"
関連GitHub: ["#424"]
最終更新: "2026-10-25"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["init-00423"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

仕様の正本を、構造は GitHub Issue（親子、依存、状態、題名、種類）に、中身は `spec-dock/canonical` ブランチ（カタログ）に集めた。利用者の5つのリポジトリ（spec-dock、input-devices、company-os、housing-lifecycle、taikyohiyou_project）をすべて canonical モード（宣言の版4）に移し、従来モード（版3、`.meta.json`）を撤去した SpecDock 0.5.0 にそろえた。

| 段階 | Issue | 結果 |
|---|---|---|
| 部品（I-1〜I-9、I-11、I-14〜I-16） | #428〜#436、#438、#455、#456、#460 | 0.3.0（2026-10-30、canonical モードと従来モードの共存） |
| spec-dock の切り替え（I-10） | #437 | PR #469（2026-10-30） |
| 0.4.1・0.4.2（I-12 の前後の改善） | #491、#493〜#495、#501 | 0.4.1（2026-11-01）、0.4.2（2026-11-02） |
| 残りの4つの切り替え（I-12） | #439 | input-devices#19、company-os#2、housing-lifecycle#239、taikyohiyou_project#2228（2026-11-01） |
| 従来モードの撤去（I-13） | #440 | PR #505、0.5.0（2026-11-02）。5つのリポジトリの配布資産を 0.5.0 に（input-devices#22、company-os#4、housing-lifecycle#242、taikyohiyou_project#2230） |

子の Issue は 23 件（完了 22、不採用 1：I-6 は I-5 に移した）。

## Verification

受け入れの条件（AC-01〜AC-20）の根拠は `.workbench/ac-evidence-20261102.md`（子の報告書の行を引いた表。読むだけの補助のエージェントが作り、統括が確かめた）。

| AC | 判定 | 根拠の要点 |
|---|---|---|
| AC-01 | 満たす | I-10 の PR #469 と I-12 の4つの切り替えの PR で、既定のブランチから仕様のツリーを外した |
| AC-02 | 満たす | I-3・I-9 の実機（macOS 33秒、Linux 36秒、Docker 60秒で別のクローンに届く）。別の PC は bare のリポジトリで代えた |
| AC-03 | 満たす | I-3・I-9 の実機で、別名ファイル1つ、競合のマーカー0 |
| AC-04 | 満たす | I-10（265 Scope、リンク502件、`verify` 不一致0）、I-12（4つのリポジトリの `verify` 一致と往復の記録） |
| AC-05 | 一部 | `adopt-worktree` のテスト（AC-435-11）と、I-10 の `spec-dashboard` の取り込み。取り込んだブランチの PR が仕様を含まずにマージされた実例はまだない（版3の worktree 2つは #514 で扱う） |
| AC-06 | 満たす | I-2 のテストと実機、I-9 |
| AC-07 | 一部 | Claude Code の1行は実機で確かめた（I-10）。Codex の1行は表示と文書だけで、実際のセッションでは未確認 → #515 の R-03 |
| AC-08 | 満たす | I-2 のテストと Linux の実機 |
| AC-09 | 満たす | I-5・I-14・I-16 のテスト、日本語の題名の運用 |
| AC-10 | 満たす | I-3 のテスト。運用の周期 6436 回で保留0（保留が要る削除は起きなかった） |
| AC-11 | 満たす | I-3 のテスト（bare のリポジトリへの強制 push） |
| AC-12 | 一部 | `canonical check` のテストと、本物の PR（#469、#505、4つの切り替えの PR）で検査が動いて成功した。仕様を含む PR が本物の GitHub で失敗と表示された実例はない（テストだけ） |
| AC-13 | 満たす | I-5 のテスト、I-9 の実機（2〜7秒で完了） |
| AC-14 | 満たす | I-9 の白紙のエージェントの試行（1回、合格） |
| AC-15 | 満たす | I-1〜I-9、I-14〜I-16 の各 Issue の回帰の確かめ。撤去の後は AC-20 |
| AC-16 | 満たす | 304 は本物の GitHub で確かめた（I-1）。2026-11-02 に、本物の GitHub で #515 の題名を変えると、21秒で `scope show` に出た（ダッシュボードは Issue を ID で示すので、題名は Epic 以上だけ出る。I-11 のテスト） |
| AC-17 | 満たす | I-11 のテスト、I-10 の実機（GitHub の題名で作り直された） |
| AC-18 | 満たす | I-3・I-9 の実機（OrbStack の systemd、Docker、マウントしたコンテナの `CANONICAL_FOREIGN_CHECKOUT`）。systemd のタイマーからの push の認証は AC の外で、#515 |
| AC-19 | 満たす | I-10・I-12 の予行演習、切り替え、運用の点検（`iss-00439/report.md`）。input-devices、company-os、housing-lifecycle は、切り替えの後の仕様の編集がまだない |
| AC-20 | 満たす | I-13 のコードの検索とテスト（`iss-00440/report.md`）。5つのリポジトリの配布資産が 0.5.0 になり、input-devices と company-os の main、taikyohiyou の PR で検査が 0.5.0 で通った（housing-lifecycle は I-12 の決定で PR の CI がなく、push の前の `canonical check` が通った） |

一部の3件（AC-05、AC-07、AC-12）は、どれも製品の動きの不足ではなく、本物の環境での実例が足りないもの。AC-07 の残りは #515 に移した。AC-05 と AC-12 は、テストで確かめた動きが、次に起きる実例（版3の worktree の扱い、仕様を含む誤った PR）で観測されるのを待つ。

### 未確認の事項の仕分け（2026-11-02）

`design.md` の「未確認の事項」の8件のうち、確かめたもの4件、閉じたもの2件、#515 に移したもの2件。詳しくは `design.md` の同じ節。親子の変更で Issue の `updated_at` が変わらないこと（30分ごとの取り直しが要ること）は、`iss-00437/report.md` に書いた。

## Residual Risks / Follow-ups

- **epic-00512（#512）**：I-13 で見つかった canonical の処理の不足（`iss-00440/report.md` の後続の候補）を #506〜#511 で直し、0.5.1 を5つのリポジトリに配り（#513）、移行の控えと版3の worktree を片付ける（#514）。
- **#515**：Linux の systemd のタイマーからの push、Linux の Codex のサンドボックスの `flock`、Codex の1行の実際のセッションでの確かめ。
- **次の Epic**：ダッシュボード（epic-00427、#427）と Orca との連携（#471）。
- 移行で分かったこと（各リポジトリ）：
  - 仕様のツリーの外から中を指すリンク（`content/`、`docs/` など）は、移行のスクリプトが書き換えない。I-12 で input-devices 17、housing-lifecycle 316、taikyohiyou 4 件を手で直した（#495 で README に書いた）。
  - 見本の `spec-dock-check.yml` は、ホストの runner で PR と push のたびに動く。費用の決まりのあるリポジトリ（housing-lifecycle）は手で合わせた（#494 で見本に注記）。
  - カタログが `.DS_Store` などの OS のファイルを保存した（#493 で直した）。
  - `installation update` が `.claude/skills/spec-dock*` の古い写しを外し、リンクがないと Claude Code から skill が見えなくなる（#496 で警告にした）。
  - ルートの `.gitignore` の `.workbench/` で、雛形の `.workbench/README.md` がコミットから漏れる（#497 で直した）。
  - GitHub への書き込みは1時間に500件までに抑え、二次のレート制限に当たらなかった。Scope が0件のリポジトリ（company-os）では、`verify` が比べるものがなく止まる。
