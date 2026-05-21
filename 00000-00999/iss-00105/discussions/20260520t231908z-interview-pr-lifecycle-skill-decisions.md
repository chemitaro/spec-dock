---
種別: interview
ID: "20260520t231908z-interview"
タイトル: "PR Lifecycle Skill Decisions"
状態: "draft | answered | archived"
作成者: "iwasawayuuta"
最終更新: "2026-05-20"
親: ["iss-00105"]
関連: []
authority: "raw"
derived_from: []
reflected_to: []
---

# 20260520t231908z-interview PR Lifecycle Skill Decisions

## 位置づけ
- 用途: 人間から目的、制約、期待、判断基準、未決事項を引き出し、回答を記録する。
- authority default: `raw`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- 技術的に調べられることは先に docs / code / tests / ADR / discussions / primary source を確認する。
- trivial な yes/no は、重要な判断、後続反映、回答証跡が必要なら `interview` を使い、そうでなければ issue comment や `scratch` で足りる。
- 回答から論点整理が必要になったら `disc`、追加調査が必要になったら `research`、長期判断が固まったら `adr` を新規作成する。

## ヒアリング概要 (必須)
- 対象者:
  - iwasawayuuta
- 回答が必要な理由:
  - `iss-00105` の要件定義前に、PR lifecycle skill の自律範囲、名前、外部書き込み許可、人間確認 gate を固定するため。
  - 技術調査では「新しい上位 coordinator skill が必要」という点は収束したが、運用ポリシーはユーザー判断が必要。
- 反映予定先:
  - `requirement.md`:
    - skill 名、scope / non-scope、PR lifecycle consent、merge-ready 定義、acceptance criteria。
  - `design.md`:
    - state machine、role routing、human gate、retry / timeout、review thread handling。
  - `plan.md`:
    - implementation steps、tests、review gates。
  - `adr`:
    - 必要なら、PR lifecycle consent や auto-merge exclusion を長期判断として分離する。

## 質問ブロック（必要な数だけ繰り返す） (必須)

### 質問 1
- 質問主題:
  - 新 skill 名
- 回答してほしいこと:
  - 新しい shared skill の名前を `github-pr-lifecycle` にしてよいか。
- なぜ質問するのか:
  - 要件、実装 path、tests、skill discovery の基準になるため。
- 背景:
  - consultant は `spec-dock-pr-lifecycle`、repo-analyst は `github-pr-merge-ready`、deep-consultant は `github-pr-lifecycle` を推奨した。
- 詳細説明:
  - `github-pr-lifecycle` は PR 作成から merge-ready までの lifecycle 全体を表し、既存 `github-pr-creator` / `github-codex-pr-review-comments` の命名系にも合う。
  - `spec-dock-pr-lifecycle` は spec-dock issue docs / report 読取を強調できるが、GitHub PR lifecycle 汎用 skill としては狭い。
  - `github-pr-merge-ready` は outcome が明確だが、PR 作成前から始まる state machine 全体より「最後の状態」に寄る。
- 事前分析:
  - 確認済みの docs / code / tests / ADR / discussions / primary source:
    - `20260520t231224z-research-pr-lifecycle-skill-analysis.md`
    - `20260520t231819z-disc-pr-lifecycle-skill-direction.md`
    - `src/spec_dock/assets/install_root/.agents/skills/github-pr-creator/SKILL.md`
    - `src/spec_dock/assets/install_root/.codex/agents/pr-monitor.toml`
  - まだ人間判断が必要な理由:
    - skill 名は user-facing entrypoint であり、一度 shipped asset として入れると rename cost がある。
- 回答案:
  - A:
    - `github-pr-lifecycle`
  - B:
    - `spec-dock-pr-lifecycle`
  - C:
    - `github-pr-merge-ready`
- 選択肢比較:
  - 評価軸:
    - 再利用性、既存命名との整合、目的の明確さ、rename cost。
- メリット:
  - A:
    - 汎用性と lifecycle 全体の表現が両立する。
  - B:
    - spec-dock issue/report 読取が名前から分かる。
  - C:
    - merge-ready という到達状態が分かりやすい。
- デメリット:
  - A:
    - spec-dock 固有の docs/report 読取が名前からは弱い。
  - B:
    - GitHub PR lifecycle 汎用 skill として狭く見える。
  - C:
    - lifecycle 全体より outcome に寄る。
- リスク:
  - 名前が曖昧だと、`github-pr-creator` との使い分けが後続 agent に伝わりにくい。
- ベストプラクティス分析:
  - coordinator skill は entrypoint から責務が分かり、leaf skill と区別できる名前がよい。
- 推奨案:
  - A: `github-pr-lifecycle`
- 未回答時の影響:
  - requirement の用語と file path を固定できない。
- 回答欄:
  - 回答済み:
    - `github-pr-lifecycle` や `merge-ready` ではなく、PR をマージ可能な状態まで「仕上げる」目的が明確に伝わる名前にする。
    - 抽象的な lifecycle より、何をする skill なのかが分かる名前を再検討する。
- 回答後フォローアップ:
  - 反映先:
    - `requirement.md`
    - `design.md`
    - `plan.md`
  - 追加で作る discussion docs:
    - `20260521t000352z-disc-pr-completion-skill-naming.md`

### 質問 2
- 質問主題:
  - PR lifecycle consent の段階
- 回答してほしいこと:
  - `create PR` 指示は push / PR create まで許可し、`autonomous lifecycle` 指示は bounded fix / commit / re-push / re-monitor まで許可する、という二段階 consent にしてよいか。
- なぜ質問するのか:
  - push / PR create / re-push は external publishing / credentialed write であり、通常の issue delegation consent より強い許可境界が必要なため。
- 背景:
  - `workflow_issue.md` の workflow-scoped delegation consent は reviewer / read-only specialist を対象にし、external publishing や credentialed access は許可しない。
- 回答案:
  - A:
    - 二段階 consent にする。
  - B:
    - PR lifecycle skill 起動時に毎回、許可操作を明示列挙して確認する。
- 推奨案:
  - A。普段の「PRを作成してmerge-readyまで整えて」は Tier 2 として扱え、危険操作は別 gate にできる。
- 回答欄:
  - 回答済み:
    - 二段階ではなく一段階にする。
    - この skill の価値は、PR 作成で止まらず、都度ユーザー確認なしにマージ可能な状態まで持っていくこと。
    - ただし merge 自体は行わない。

### 質問 3
- 質問主題:
  - Merge / auto-merge の扱い
- 回答してほしいこと:
  - 今回は merge / auto-merge / branch delete / issue close / admin override を完全に out of scope にしてよいか。
- なぜ質問するのか:
  - ユーザーの要望は「merge できる状態に整える」までであり、実際の merge はより強い権限・不可逆性・GitHub 設定に関わるため。
- 背景:
  - GitHub Docs では auto-merge の有効化に write permission が必要で、branch protection / required checks / required reviews と絡む。
- 回答案:
  - A:
    - 完全 out of scope。merge-ready 報告まで。
  - B:
    - auto-merge 有効化だけは明示要求時に scope に含める。
- 推奨案:
  - A。
- 回答欄:
  - 回答済み:
    - 完全 out of scope。
    - この skill は merge しない。merge 権限を持たず、人間ユーザーが merge する。
    - skill は「どんな状態になったら merge できるか」を確認し、そこまで整えたら報告する。

### 質問 4
- 質問主題:
  - merge-ready 判定における non-required check failure
- 回答してほしいこと:
  - non-required check failure も原則 blocker とし、ユーザーの明示 waiver がある場合だけ merge-ready 扱いにしてよいか。
- なぜ質問するのか:
  - GitHub required checks だけを見れば protected branch には merge できても、品質上は non-required failure が残る場合があるため。
- 回答案:
  - A:
    - non-required failure も blocker。明示 waiver で例外化。
  - B:
    - required checks のみ blocker。non-required failure は residual risk として報告。
- 推奨案:
  - A。
- 回答欄:
  - 詳細シートへ分離:
    - `20260521t000352z-02-interview-non-required-check-policy.md`

### 質問 5
- 質問主題:
  - Review thread state の取得範囲
- 回答してほしいこと:
  - unresolved review thread state を扱うため、将来または本 issue で固定 read-only GraphQL wrapper / GitHub connector 利用を要求するか。
- なぜ質問するのか:
  - 現行 REST wrapper は issue comments / inline review comments / review bodies を取得できるが、thread の resolved / unresolved 状態は弱い。
- 回答案:
  - A:
    - 今回は現行 REST wrapper を前提にし、unresolved state は limitation として扱う。
  - B:
    - 本 issue で fixed read-only thread-state wrapper を追加または requirement に含める。
  - C:
    - GitHub plugin connector の thread-aware skill を前提にする。
- 推奨案:
  - A または B。最小実装なら A、merge-ready 厳密性を優先するなら B。
- 回答欄:
  - 詳細シートへ分離:
    - `20260521t000352z-01-interview-review-thread-state-policy.md`

### 質問 6
- 質問主題:
  - PR default state
- 回答してほしいこと:
  - PR 作成時の default を draft-first にするか、local final gates pass 後なら ready PR を許可するか。
- 回答案:
  - A:
    - draft-first。merge-ready 到達時に ready 化は別 human gate。
  - B:
    - local final gates pass 後なら ready PR 作成。
- 推奨案:
  - B。既存 `github-pr-creator` は draft default ではなく、ユーザーの意図と diff / issue completion に応じて作成する設計に近い。ただし lifecycle skill は ready/draft を必ず報告する。
- 回答欄:
  - 詳細シートへ分離:
    - `20260521t000352z-03-interview-pr-draft-ready-and-base-resolution-policy.md`

### 質問 7
- 質問主題:
  - base branch 解決
- 回答してほしいこと:
  - `branch.<current>.gh-merge-base` を GitHub CLI と同様に尊重し、選択した base を必ず表示する方針でよいか。
- 背景:
  - GitHub CLI manual では、`--base` 未指定時に current branch の `gh-merge-base` config、なければ repository default branch を使う。
- 回答案:
  - A:
    - 尊重する。
  - B:
    - user-specified base と repository default のみ使う。
- 推奨案:
  - A。
- 回答欄:
  - 詳細シートへ分離:
    - `20260521t000352z-03-interview-pr-draft-ready-and-base-resolution-policy.md`
