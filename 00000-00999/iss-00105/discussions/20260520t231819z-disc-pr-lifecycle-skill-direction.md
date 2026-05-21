---
種別: disc
ID: "20260520t231819z-disc"
タイトル: "PR Lifecycle Skill Direction"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-05-20"
親: ["iss-00105"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260520t231819z-disc PR Lifecycle Skill Direction

## 位置づけ
- 用途: 集まった情報をもとに、論点、評価軸、選択肢、合意点/未合意点を整理する。
- authority default: `proposed`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- 人間から回答を引き出し、回答欄や未回答事項を管理する場合は `interview` を使う。
- 生ログや未整理の思考は `scratch`、事実確認や外部根拠は `research`、長期判断の固定は `adr` に分ける。
- doc が大きくなりすぎたら、質問回答は `interview`、事実調査は `research`、raw capture は `scratch`、長期決定は `adr` へ分割する。

## 議題 (必須)
- `iss-00105` で作成する skill の方針を、要件定義書へ落とせる粒度まで決める。
- 具体的には、skill 名、責務境界、既存 skill / agent との関係、PR lifecycle consent、merge-ready 定義、human gate、実装範囲を決める。

## 背景 (必須)
- ユーザーは、作業完了後に毎回「PR 作成、PR monitor 監視、CI / review 指摘の分析、修正、push、再監視、merge-ready までの反復」を口頭で指示している。
- 既存 `github-pr-creator` は push / PR 作成 / issue linkage / `pr-monitor` handoff までを持つが、failure / review feedback の修正 loop は持たない。
- 既存 `pr-monitor` は read-only agent で、checks/statuses と Codex review を bounded timeout 付きで見る。修正・push・再監視の orchestration owner ではない。
- `issue finish` は spec-dock lifecycle closure であり、commit / push / PR / merge / review completion を保証しない。したがって、今回の能力は runtime command ではなく post-implementation delivery workflow skill として扱う。
- Provider source-of-truth は `src/spec_dock/assets/install_root/`。dogfooding root の `.agents/`, `.codex/`, `.github/` は mirror / parity 対象。
- GitHub CLI / Docs から、merge-ready 判定には `mergeable`、`mergeStateStatus`、`reviewDecision`、`statusCheckRollup`、`gh pr checks`、required checks などの複数情報を使う必要がある。
- Push / PR create / re-push は external publishing / credentialed write を伴うため、通常の issue-scoped reviewer / specialist delegation consent とは別の `PR Lifecycle Consent` が必要。

## 選択肢 (必須)
- Option A: `github-pr-creator` を拡張して lifecycle まで持たせる
  - Pros:
    - 既存 PR 作成 entrypoint をそのまま使える。
    - skill 数は増えない。
  - Cons:
    - PR creation leaf skill が CI triage / review feedback / fix loop / merge-ready 判定まで抱え、責務が太くなる。
    - `pr-monitor` との関係が曖昧になりやすい。
    - 既存の bounded PR creation use case に余計な重さが入る。
- Option B: 新しい上位 coordinator skill `github-pr-lifecycle` を作る
  - Pros:
    - PR 作成、監視、分類、修正委譲、再 push、再監視、merge-ready 判定を state machine として表現できる。
    - `github-pr-creator` と `pr-monitor` を置き換えず、既存資産を leaf / monitor として再利用できる。
    - PR lifecycle consent、human gate、retry 上限、merge-ready 定義を独立した durable contract にできる。
    - spec-dock 以外の GitHub repo でも使える名前でありつつ、spec-dock repo では active issue docs / report を読む契約を入れられる。
  - Cons:
    - 新しい shipped skill と tests / asset inventory 更新が必要。
    - 既存 `github-pr-creator` との使い分けを明記しないと entrypoint が増えて迷う。
- Option C: 新しい上位 coordinator skill `spec-dock-pr-lifecycle` を作る
  - Pros:
    - active issue docs / report を読むことが名前から分かりやすい。
    - spec-dock dogfooding workflow に強く寄せられる。
  - Cons:
    - GitHub PR lifecycle 汎用 skill としては狭く見える。
    - 既存 `github-pr-creator` / `github-codex-pr-review-comments` の命名系から外れる。
- Option D: 新しい outcome-focused skill `github-pr-merge-ready` を作る
  - Pros:
    - 目標が merge-ready であることが明確。
    - PR 作成後の monitor / fix loop に焦点を当てやすい。
  - Cons:
    - PR 作成前から始まる lifecycle 全体を少し狭く表現する。
    - `merge-ready` が「merge 実行」まで含むと誤解される可能性がある。

## 推奨案 (必須)
- Option B の「新しい上位 coordinator skill」を採用し、skill 名は追加分析に基づいて `github-pr-merge-preparer` を推奨する。
- 理由:
  - 実態は PR 作成 skill でも monitor agent でもなく、PR を人間が merge できる状態まで準備する coordinator である。
  - 既存 `github-pr-creator` を creation leaf として残し、`pr-monitor` を read-only watcher として残せる。
  - `lifecycle` は抽象的で、ユーザーが求める「PR を仕上げる」目的を名前だけでは伝えにくい。
  - `merge-ready` は待機状態に見えるため、能動的に整える `merge-preparer` の方が意図に近い。
  - `github-pr-merge-preparer` は merge 自体を実行せず、merge に向けて準備する skill であることを表現できる。
- 推奨 state machine:
  - `prepare -> create-or-find-pr -> monitor -> classify -> analyze-or-delegate-fix -> verify -> commit-and-push -> monitor-again -> merge-ready-or-human-gate`
- 推奨 responsibility model:
  - `github-pr-lifecycle`: state machine owner / consent boundary / routing / final merge-ready判定。
  - `github-pr-creator`: PR 作成 leaf。base/head diff、issue linkage、title/body draft、push / create。
  - `pr-monitor`: read-only observation。checks/statuses、reviewDecision、Codex review、mergeability signal。
  - `dev-coder`: code / runtime / tests / scaffold behavior の修正。
  - `doc-writer`: docs / templates / skills / workflow text の修正。
  - `consultant`: 複雑な CI failure、曖昧な review comment、設計 tradeoff の分析。
  - main orchestrator: spec-dock issue の `report.md` / decision ledger 統合。
- Merge / auto-merge / branch delete / issue close / admin override はこの skill の自律範囲から外し、別 human gate とする。
- Skill invocation は一段階 consent として扱い、PR 作成から bounded fix / re-push / re-monitor / merge-prepared 報告まで都度確認なしに進める。
- Fix loop 上限は default total 3 cycles、または同一 failure class 2 回で human gate にする案を維持する。

## 未決事項 (任意)
- Q-001: skill 名を何にするか。
  - 回答済み:
    - 抽象的な `lifecycle` や、待機状態に見える `merge-ready` より、PR をマージ可能な状態まで持っていく目的が分かる名前がよい。
  - 追加分析:
    - `20260521t000352z-disc-pr-completion-skill-naming.md`
  - 現時点の推奨:
    - `github-pr-merge-preparer`
- Q-002: PR lifecycle consent は二段階にするか。
  - 回答済み:
    - 二段階ではなく一段階。
    - PR 作成で止まらず、都度ユーザー確認なしにマージ可能な状態まで持っていくことが skill の価値。
  - 反映方針:
    - skill invocation は PR 作成、監視、bounded fix / commit / re-push / re-monitor までの一連の consent として扱う。
    - ただし merge / auto-merge / branch delete / issue close / admin override は consent 外の別 human gate。
- Q-003: merge / auto-merge を今回完全 out of scope にするか。
  - 回答済み:
    - 完全 out of scope。
    - merge は人間ユーザーが行う。skill は merge 可能な状態まで整え、報告する。
- Q-004: merge-ready 判定で non-required check failure を blocker にするか。
  - 推奨: 原則 blocker。ただし explicit waiver 可能。
  - 詳細シート:
    - `20260521t000352z-02-interview-non-required-check-policy.md`
- Q-005: unresolved review thread state を扱うため、固定 read-only GraphQL wrapper または GitHub connector 利用を要求するか。
  - 現 REST wrapper は Codex comments の取得には十分だが、unresolved / resolved thread state は弱い。
  - 詳細シート:
    - `20260521t000352z-01-interview-review-thread-state-policy.md`
- Q-006: PR 作成 default は draft-first か、local final gates pass 後なら ready PR か。
  - 詳細シート:
    - `20260521t000352z-03-interview-pr-draft-ready-and-base-resolution-policy.md`
- Q-007: base 解決で `branch.<current>.gh-merge-base` を尊重するか。
  - 推奨: GitHub CLI と揃えて尊重し、必ず表示する。
  - 詳細シート:
    - `20260521t000352z-03-interview-pr-draft-ready-and-base-resolution-policy.md`

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - ユーザー確認後、`requirement.md` に `github-pr-lifecycle` の目的、scope、consent、state machine、human gate、merge-ready 定義、AC を反映する。
  - `design.md` では role routing table、state transition、failure classification、asset / tests impact、`pr-monitor` output 拡張有無を設計する。
  - `plan.md` では shared skill 追加、existing skill updates、pr-monitor output update、mirror parity、tests、review gates を step 化する。
- 追加で作る discussion docs:
  - ユーザー回答が必要な事項は `interview` doc へ分離する。
