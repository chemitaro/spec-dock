---
種別: decision-candidate
ID: "20260713t023439z-decision-candidate"
タイトル: "ChatGPT Output Artifact Import Contract"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
親: ["epic-00312"]
関連: ["epic-00259"]
scope: "epic"
scope_id: "epic-00312"
created_at: "2026-07-13T02:34:39Z"
created_by: "iwasawayuuta"
status: "proposed"
authority: "user-proposed"
adoption_status: "unreviewed"
derived_from: []
reflected_to: []
---

# ChatGPT Output Artifact Import Contract

## 問題
- ChatGPT First運用では、ChatGPTが作成した人間向け完成レポートをCodexがcanonical docsへ要約・再構成する際、原文の構造、説明、可読性、洞察が失われ得る。
- Codexの要約版だけを永続化すると、後から採否を再評価するevidenceと詳細説明への参照先が失われる。

## 提案する能力
- Existing `new artifact` と別に、完成済みfileを内容不変でArtifactへcopyする `artifact import` を追加する。
- MVP artifact typeは `chatgpt-output`。
- MVP inputは単一Markdown file。
- Workbenchはdownload、内容確認、比較、選別、一時保管、加工前作業の場所として維持する。

## Candidate CLI
```sh
spec-dock artifact import chatgpt-output \
  --epic epic-00312 \
  --file .workbench/chatgpt-workbench-analysis.md \
  --title "Workbench architecture analysis"
```

## Candidate destination
```text
artifacts/
└── 20260713t130000z-chatgpt-output-workbench-architecture-analysis.md
```

## 内容不変契約
1. File bodyを変更しない。
2. Frontmatterを挿入しない。
3. Artifact templateを適用しない。
4. Markdownを整形しない。
5. 改行code/character encodingを意図的に変換しない。
6. Codexによる要約・再構成を行わない。
7. Artifact規則に合うdestination filenameだけを新しく生成する。
8. Source fileへtimestamp/type/slug prefixを付けた名前でcopyする。
9. Same destination nameが存在する場合はoverwriteせず、existing collision suffix ruleに従う。
10. Import前後のSHA-256一致を検証する。
11. Imported Artifactはevidence-onlyで、canonical authorityにはならない。
12. Canonical docsへの採否・反映先はEvidence Adoption Ledgerで管理する。

## Copy / failure contract
- Moveではなくcopyする。Workbench sourceは残す。
- Temporary destinationへcopyし、hash一致後にformal Artifact pathへ配置する。
- Sourceを自動削除しない。
- Failure時もsourceを失わない。
- Collision時はexisting suffix contractを使い、existing Artifactをoverwriteしない。

## MVP scope / future boundary
- MVP: single Markdown file、`chatgpt-output` type、Initiative/Epic/Issue scope、byte-preserving copy/hash verification。
- Future only after observed need: PDF、image、ZIP、multi-file bundle、directory import、`captures/` / RawCaptureBundle。

## ChatGPT First operation principle candidate
> ChatGPT出力が人間向けの完成レポートとして有用な場合、Codexはcanonical documentへ再記述する前に、その原文を `chatgpt-output` Artifactとしてimportする。原文を保存せず、Codexが作成した要約版だけを永続化してはならない。

- Canonical docsは採用された規範的requirement/design/planを記述し、詳細説明はimport済みChatGPT原文Artifactへlinkできる。

## Adoption questions
- Epic 00312にWorkbench-to-Artifact promotion boundaryとして統合するか。
- Epic 00259のArtifact filename/type/template/collision/authority contractにどの変更が必要か。
- `workflow_spec_authoring.md` / `workflow_chatgpt_authoring_pack.md` / ChatGPT-first skillsへ、import-before-rewriteをmandatoryにする範囲。
- Existing raw ZIP quarantine/authoring packと、single-file byte-preserving importの責務境界。
- 既存3-Issue案を拡張するか、Artifact importを独立implementation Issueにしてfinal quality Issueを後段へ維持するか。

## Adoption boundary
- このfileはuser-proposed evidenceであり、canonical requirement/design/planやaccepted ADRではない。
- GitHub-synced ChatGPT 5.6 Pro analysis、local repository inspection、fresh phase reviewerを経てEAL dispositionする。
