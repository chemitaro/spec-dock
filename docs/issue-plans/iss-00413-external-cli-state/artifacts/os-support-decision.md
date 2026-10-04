# Issue #413 対応OS決定記録

- 対象: GitHub Issue #413 / external CLI state
- 決定日: 2026-10-02 JST
- authority: 利用者の最新人間決定（OS範囲について最上位）
- 検証対象: `chemitaro/spec-dock` / `codex/iss-00413-external-cli-state` / `121228c6fca1fd016e7bccef009902396112ba43`
- 記録種別: 追加決定。既存 `user-decisions.md` と `interview-worktree-start.md` は上書きしない
- 著述モデル: GPT-5.6 Sol / Pro

## 決定

1. Windowsに対応する必要はありません。
2. 対応するOSはLinuxおよびmacOSです。
3. 撤回対象は、Issue #413で直前に追加されたWindows対応の要求・設計・実装・test・CI受入義務です。
4. Issue #413全体の目的、すなわち通常の外部CLI、Git管理領域への独自control/台帳/cache/daemonを置かないこと、worktreeごとの最小直接状態、Start-only排他は撤回しません。
5. Windowsを止める代替として、新しいlock file、PID/mkdir lock、registry、cache、daemon、ACL変更、別store、広範なOS抽象化を追加しません。

## 維持する確定事項

Initiative/Epic/Issueの三階層、GitHub必須の新規ID、UUID廃止、同じcloneのmain/linkedだけ、一worktree一直接対象、Startのbranch作成・checkout、重複確認から直接記録までの短い排他、通常編集/Finish/Sync等への包括lockなし、FinishのGitHub closed/completed、Finish後も同branch、自動rollbackなし、Git原文・partial/unknown保持、Syncの複数選択観測、独自 `.git` control/台帳/cache/daemonなし、新規work releaseなしを維持します。

## authorityの適用

- 旧R/D/Pや旧Implementation BriefにWindows minimal adapter、native/NTFS/store受入が書かれていても、本決定が優先します。
- 旧Windows調査、commit、test、CI、測定は履歴・raw evidenceとして保全しますが、Windowsを完成させる根拠にはしません。
- 未回答のOS判断として扱わず、Windows完成案を提案しません。

## 作業境界

本決定の反映はP-18として正本へ登録します。P-18実装は、更新済み正本を通常pushし、独立ChatGPT Implementation Brief Strictで対象SHA・file/symbol・command・停止条件を具体化した後に開始します。この記録、plan登録、brief作成はSpecDock正式Startの成功ではありません。P-16実consumer切替とP-17正式import/Startはhuman merge後の別手順です。
