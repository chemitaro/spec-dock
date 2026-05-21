---
種別: disc
ID: "20260521t000352z-disc"
タイトル: "PR Completion Skill Naming"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-05-21"
親: ["iss-00105"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260521t000352z-disc PR Completion Skill Naming

## 位置づけ
- 用途: 集まった情報をもとに、論点、評価軸、選択肢、合意点/未合意点を整理する。
- authority default: `proposed`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- 人間から回答を引き出し、回答欄や未回答事項を管理する場合は `interview` を使う。
- 生ログや未整理の思考は `scratch`、事実確認や外部根拠は `research`、長期判断の固定は `adr` に分ける。
- doc が大きくなりすぎたら、質問回答は `interview`、事実調査は `research`、raw capture は `scratch`、長期決定は `adr` へ分割する。

## 議題 (必須)
- PR 作成後に CI / review / 修正 / 再 push / 再監視を回し、人間が merge できる状態まで PR を整える skill の名前を決める。
- `lifecycle` のような抽象名や、`merge-ready` のような待機状態に見える名前ではなく、「何をする skill か」が分かる名前を選ぶ。

## 背景 (必須)
- ユーザー回答:
  - 抽象的な lifecycle より、PR をマージできる状態まで持っていく目的が伝わる名前がよい。
  - `merge-ready` は「マージ待ち」に見えるため、skill が何をするのかを明確にしたい。
  - この skill は merge しない。人間が merge できる状態まで整え、報告する。
- 命名制約:
  - shipped skill 名なので lowercase kebab-case にする。
  - 既存 `github-pr-creator`、`github-codex-pr-review-comments` と近い命名体系に置くと discovery しやすい。
  - `spec-dock-*` にすると spec-dock 専用感が強くなるが、実体は GitHub PR の仕上げ workflow である。
- 責務:
  - PR を作成するだけでは終わらない。
  - PR を観測し、失敗や review 指摘を分類し、必要な修正を委譲し、push し直し、再監視し、人間が merge 判断できる状態まで整える。

## 選択肢 (必須)
- Option A: `github-pr-merge-preparer`
  - Pros:
    - 「merge する」のではなく「merge に向けて準備する」ことが名前から読める。
    - `preparer` は作業動詞に近く、待機状態ではなく能動的に整える skill だと伝わる。
    - GitHub PR 向けであることが明確。
    - `github-pr-creator` の上位/後続として自然。
  - Cons:
    - 少し長い。
    - `preparer` がやや英語として硬い。
- Option B: `github-pr-finisher`
  - Pros:
    - ユーザーの「PR を仕上げる」に近い。
    - 短く覚えやすい。
  - Cons:
    - `finish` が merge / close / issue finish まで含むように誤解される可能性がある。
    - spec-dock の `issue finish` と語感が衝突する。
- Option C: `github-pr-completion`
  - Pros:
    - PR 作成後の完了まで扱うことは伝わる。
  - Cons:
    - 名詞であり、何を能動的に行う skill かが少し弱い。
    - completion が merge / close を含むように読まれ得る。
- Option D: `github-pr-stabilizer`
  - Pros:
    - CI failure / review 指摘を潰して安定化させる意味がある。
  - Cons:
    - PR 作成や issue linkage を含む lifecycle 前半が名前から抜ける。
    - 何をもって stable とするかが曖昧。
- Option E: `github-pr-lifecycle`
  - Pros:
    - PR 作成から再監視まで状態遷移全体を表せる。
  - Cons:
    - ユーザー指摘どおり抽象的。
    - 「PR をマージできる状態まで持っていく」という目的が弱い。

## 推奨案 (必須)
- 推奨: `github-pr-merge-preparer`
- 理由:
  - 「PR を merge する」のではなく「人間が merge できるように準備する」ことを名前で表現できる。
  - `merge-ready` のような静的状態名ではなく、準備する skill という能動的な意味を持つ。
  - `github-pr-creator` と並べたときに、`creator` は作成、`merge-preparer` は merge 可能化、という役割分担が分かる。
  - auto-merge / merge execution を out of scope にする方針と矛盾しない。
- Description 案:
  - `Create or find a GitHub pull request, monitor checks and reviews, delegate bounded fixes, re-push, and prepare the PR for human merge without performing the merge.`
- 日本語説明案:
  - GitHub Pull Request を作成または検出し、CI / review の完了待ち、失敗分析、修正委譲、再 push、再監視を繰り返して、人間が merge できる状態まで整える。merge 自体は行わない。

## 未決事項 (任意)
- `github-pr-merge-preparer` で進めてよいか。
- `github-pr-finisher` の方が「仕上げる」に近く感じる場合、`finish` が merge / close を含む誤解を許容できるか。
- skill file path は推奨名に合わせて `.agents/skills/github-pr-merge-preparer/SKILL.md` とする想定。

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - `requirement.md` の目的、scope、用語、acceptance criteria に `github-pr-merge-preparer` を反映する。
  - `design.md` で既存 `github-pr-creator` / `pr-monitor` との責務分担を名前に合わせて整理する。
  - `plan.md` で provider install_root、dogfooding mirror、tests に新 skill path を入れる。
- 追加で作る discussion docs:
  - なし。
