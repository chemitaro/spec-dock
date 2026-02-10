# spec-dock Guide（旧版・参考）

> ⚠️ 注意（旧版）  
> このファイル（`spec-dock-guide-old.md`）は **旧版の参考**です。  
> 現行運用の正は `spec-dock/docs/README.md` / `spec-dock/docs/spec-dock-guide.md` / `spec-dock/docs/workflow-*.md` です。

このガイドは、spec-dock v2 の設計検討初期に作られた「運用ルールの叩き台」です。  
履歴的な背景の参照のために残していますが、**運用判断やコマンド例は現行と一致しない可能性があります**。

## 現行との差分（要点）

- `active set` は現行では `./spec-dock/scripts/spec-dock active set <target>` です
  - `target` は GitHub Issue番号（例: `123` / `#123` / issue URL）またはノードID（例: `iss-00123`）です
- Initiative/Epic/Issue の多層運用は `workflow-tree.md` を正とします
- ADR は「結論が出る前に叩き台を作る」運用です（`workflow-adr.md`）

## 旧版が強調していた原則（参考）

- 99.9%理解ルール（推測で進めない）
- TDD（Red → Green → Refactor）
- 仕様（requirement/design/plan）→ 実装 → 報告（report）を往復し、証拠を残す

## 参照先（現行）

1. `spec-dock/docs/README.md`（入口）
2. `spec-dock/docs/spec-dock-guide.md`（共通原則/チェックリスト）
3. `spec-dock/docs/workflow-issue.md`（Issueワークフロー）
4. `spec-dock/docs/workflow-tree.md`（ツリー運用）
5. `spec-dock/docs/workflow-adr.md`（ADR運用）

