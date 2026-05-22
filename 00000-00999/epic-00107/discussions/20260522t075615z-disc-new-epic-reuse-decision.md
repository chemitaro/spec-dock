---
種別: disc
ID: "20260522t075615z-disc"
タイトル: "new epic reuse decision"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-05-22"
親: ["epic-00107"]
関連: []
authority: "synthesized"
derived_from: ["20260522t074811z-research"]
reflected_to: ["../requirement.md"]
---

# 20260522t075615z-disc new epic reuse decision

## 位置づけ
- 用途: 集まった情報をもとに、論点、評価軸、選択肢、合意点/未合意点を整理する。
- authority default: `proposed`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- 人間から回答を引き出し、回答欄や未回答事項を管理する場合は `interview` を使う。
- 生ログや未整理の思考は `scratch`、事実確認や外部根拠は `research`、長期判断の固定は `adr` に分ける。
- doc が大きくなりすぎたら、質問回答は `interview`、事実調査は `research`、raw capture は `scratch`、長期決定は `adr` へ分割する。

## 議題 (必須)
- `worktree` 作成 capability を既存 epic に追記するか、新しい epic `epic-00107 Worktree Provisioning` として扱うかを整理する。

## 背景 (必須)
- `init-local-00002` は feature expansion initiative であり、operator が日常的に使う command / workflow capability を価値単位で増やすことを目的にしている。
- 既存 `epic-00054` は GitHub issue close、local node delete、repo-local self-update を扱う lifecycle command expansion であり、Git linked worktree 作成や branch/path/bootstrap naming は scope に含めていない。
- 既存 `epic-00074` は host agent / config asset expansion であり、worktree 作成 command とは機能価値も影響範囲も異なる。
- 今回の user intent は、`spec-dock` 自身を複数変更の並行開発に対応させるため、worktree 作成 command を runtime command 群へ追加することである。
- worktree 作成は Git subprocess、path placement、branch naming、optional `make init` bootstrap、Codex-managed worktree との境界を含むため、既存 lifecycle / host asset epic に混ぜると設計の背骨が濁る。

## 選択肢 (必須)
- Option A:
  - 既存 `epic-00054 GitHub lifecycle command expansion` に追加する。
  - Pros:
    - command expansion という大枠には近い。
    - 既存 runtime command 追加の文脈を流用できる。
  - Cons:
    - `epic-00054` は close / delete / self-update の lifecycle gap を閉じる epic であり、parallel development workspace provisioning とは受け入れ条件が異なる。
    - worktree path / branch naming / bootstrap / Codex boundary を追加すると、完了済みまたは進行済みの lifecycle contract が膨らむ。
- Option B:
  - 新規 `epic-00107 Worktree Provisioning` として扱う。
  - Pros:
    - 並行開発用 worktree 作成 capability を、独立した operator value として requirement / design / plan へ落とせる。
    - Git worktree placement、naming、bootstrap、Codex-managed worktree との境界をこの epic の背骨として扱える。
    - 将来の worktree status / remove / dashboard は同じ capability area の future extension として整理しやすい。
  - Cons:
    - command expansion epic が増えるため、initiative plan 上では `epic-00054` との関係を明記する必要がある。

## 推奨案 (必須)
- Option B。
- worktree 作成は `spec-dock` の GitHub lifecycle 操作や host asset 配布とは別の operator capability であり、placement / naming / bootstrap / parallel development policy を一つの requirement として閉じる必要がある。
- 既存 epic へ追記すると scope と acceptance criteria が混ざるため、新規 epic として管理する方が `workflow_epic.md` の「設計の背骨」を保てる。

## 未決事項 (任意)
- なし。CLI shape は `spec-dock worktree create [LABEL]`、output は absolute path 主表示として requirement で確定済みである。

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - `requirement.md` は、worktree 作成 capability を `epic-00107` の scope として固定する。
  - `epic-00054` / `epic-00074` は関連既存 epic として調査済みだが、本 epic へ統合しない。
- 追加で作る discussion docs:
  - なし。
