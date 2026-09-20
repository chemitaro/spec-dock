---
種別: artifact
ID: "20260920t055027z-02"
タイトル: "Specification Adoption Receipt"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-09-20"
親: ["iss-00405"]
template: "blank"
authority: "evidence"
derived_from: []
reflected_to: []
---

# Issue #405 仕様採用記録

## 来歴

- ChatGPT会話: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6aaf4317-c7c8-83ee-91e2-1dffda7f2cf9
- Oracle session: `issue-405-cleanup-spec-authoring`。監査を行った同じ会話を継続。
- 指定: GPT-5.6 Sol / Pro。初回監査でmodel picker検証済み。今回followupはmodelを継承（再選択検証はskipped）、ProはUI verified。
- Strict expected/connector-observed SHA: `457faf31df8840d1f2fc87417d297dc318903fbe`。
- ChatGPT原本: [仕様ZIP](20260920t055018z--iss-00405-cleanup-spec-pack.zip)。SHA-256 `4daac99d84afafb4e0dcfe15c47d2da16b17cf639352ae588fe97cf8ecff0a77`。CRCと内部SHA256SUMS一致。
- 調査原本: [監査ZIP](20260920t045654z--epic-384-semantic-audit-final.zip)。

## 採用範囲

Issue直下のrequirement.md/design.md/plan.mdを完全置換し、HTML・実装handoff・source-symbol map・test dispositionをArtifactへ配置した。Product source/testは変更していない。親Epic文書の更新は後続実装計画に置いた。

## 原本からの採用時補正

1. Markdown補助ArtifactをSpecDock `new artifact blank`で作成した正式名へ対応させ、正規文書内リンクを置換。Artifact frontmatterを保持。
2. S1のRed-only checkpointを禁止し、S1〜S3のtest・production・必要検証をまとめたworking checkpointに変更。`git-commit` skill、Git一コマンド一call、認可境界を補足。
3. Luna handoffのshell wrapper付きidentity確認を、個別の `git config` readに変更。
4. HTMLのPlantUML rectangle labelに含まれていた実改行8か所をPlantUMLの `\n` 表記へ修正。描画契約・validatorは変更していない。
5. HTMLにもS1〜S3のcheckpoint境界を反映。

## 検証

- 既存test case 100件のpath/function/lineをlocal ASTと照合し不一致0。CSV全132行。
- canonical Markdownのlocal link切れ0。
- `./spec-dock/scripts/spec-dock validate`: PASS、nodes=237。
- `git diff --check`: PASS。
- HTML validator: 初回は2図中1図でPlantUML label syntax error。補正後2/2 inline SVG、zoom click/keyboard/bounds/focus trap/dismissal/focus restoration PASS。
- 今回は仕様作成でありProduct test/lint/build/CIや独立仕様reviewは未実施。前回のinstaller 11 passedはpre-implementationの限定証拠のみ。

## 状態

仕様候補draftを配置済み。Issue startは完了、実装未着手。canonical Plan S0の独立仕様reviewは残る。著者による自己点検やCodexの採用確認を独立review passとは扱わない。
HTMLのローカル納品は完了。追加のTailscale公開は自動承認レビューで拒否され、公開の明示承認待ち（ファイル納品の阻害条件ではない）。

- 最終整形: CSVのCRLFをLFへ正規化（行・値は不変）。採用済みZIPも配置内容から再生成し一致を確認。
