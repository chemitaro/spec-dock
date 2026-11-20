---
種別: レポート（Epic）
ID: "epic-00672"
関連GitHub: ["#672"]
最終更新: "2026-11-20"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

- iss-00673（PR #677 → 0eee53b94）：`canonical status` の `data.tools.antigravity` と警告。Antigravity（`ANTIGRAVITY_AGENT`）の作業用の worktree で、`~/.gemini/antigravity-cli/settings.json` の `permissions.allow` に `read_file(<カタログ>)`・`write_file(<カタログ>)` がなければ1行を示す。deny・ask に判定できない規則があれば UNKNOWN。案内 `docs/canonical.md`。agy 1.5.12 で、規則がないと linked worktree からカタログへの書き込みが拒まれ、`allowNonWorkspaceAccess` や信頼済みの folder では代わりにならないことを確かめた。R-02（書けない動き方）は Antigravity にないので、配るスキルは変えていない。
- iss-00674（PR #678 → 6de140261）：ダッシュボードの種類の名前を orca-web の部品（`AGENT_ICONS[iconKey(t)].label`）から引く `agentTypeLabel`。
- iss-00675（PR #680 → 836d52501、タグ v0.9.10）：0.9.10 のリリース。
- 同じ版に入った別の Epic の直し：epic-00080 の iss-00676（PR #679 → a6000d8cd、本人の指摘と決定 B）『これから』でも指揮の線。
- orca-web 側は epic-00065（完了）：アイコンと名前、送信の照合と回答、モデルと推論の深さ。

## Verification

統括が 2026-11-20 に、タグ v0.9.10 から作った wheel をこの PC の道具の環境に入れ（`spec-dock --version` 0.9.10）、常駐のダッシュボード（自動で 0.9.10 に起動し直した）で確かめた：
- `/graph` の既定の『これから』で `specdockCmdAudit()` が links 4・arcs 1・boxOverlaps 0・edgeOverlaps 0、黄色の動く点線が出る（写しは統括の確かめ）。
- 作業用の worktree の `spec-dock canonical status --json` に `data.tools.antigravity`（needed true、configured false、足す1行）が出る。
- Antigravity のエージェントの名前は、iss-00674 の担当が orca-web 4ad7471 の常駐の実データで確かめた。
各 PR は最終品質ゲートの合格のコミット＝PR の先端、CI 成功を統括が確かめてマージした。

## Residual Risks / Follow-ups

- iss-00673 の P2（改行を含む deny・ask の規則を拾わない）は直していない（iss-00673 の report.md）。
- Antigravity の CLI は新しく、設定の場所や形が版で変わりうる。案内は agy 1.5.12 で確かめた。
- 各リポジトリの `installation update` は必須ではない（0.9.9〜0.9.0 の配布資産のままで動く）。手元の `docs/canonical.md` に Antigravity の案内を載せたいときに実行する。
- この PC の Antigravity で作業用の worktree からカタログに書くには、本人が `canonical status` の1行を `~/.gemini/antigravity-cli/settings.json` に足す必要がある（SpecDock は書き換えない）。
