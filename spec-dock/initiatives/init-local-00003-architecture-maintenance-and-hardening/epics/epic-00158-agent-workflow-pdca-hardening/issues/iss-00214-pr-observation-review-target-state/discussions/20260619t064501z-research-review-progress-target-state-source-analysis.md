---
種別: research
ID: "20260619t064501z-research"
タイトル: "Review Progress Target State Source Analysis"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-06-19"
親: ["iss-00214"]
関連: []
authority: "synthesized"
derived_from:
  - "GitHub issue #214"
  - "spec-dock/active/context-pack.md"
  - "spec-dock/active/issue/requirement.md"
  - "spec-dock/active/epic/requirement.md"
  - "src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py"
  - ".agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py"
  - "src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md"
  - "tests/unit/infra/test_init_update.py"
reflected_to: []
---

# 20260619t064501z-research Review Progress Target State Source Analysis

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約、用語衝突、edge case など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は source-grounded research evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- 事実、推測、未検証事項、用語衝突、edge case、判断への含意を混ぜない。
- local context で解ける疑問は人間に聞かず、この artifact に source-grounding を残す。

## 調査目的 (必須)
- GitHub issue #214 の requirement / design / plan 具体化前に、`wait_pr_observation.sh` の progress line が `review=` に何を表示しているか、どの source が authority か、どの未確定判断だけをユーザーに聞く必要があるかを明らかにする。

## sources / 調査方法 (必須)
- 参照先:
  - `spec-dock/active/context-pack.md`
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/epic/requirement.md`
  - GitHub issue #214 body
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
  - `.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
  - `tests/unit/infra/test_init_update.py`
- 検証手順:
  - `./spec-dock/scripts/spec-dock issue start --id iss-00214`
  - `gh issue view 214 --json number,title,body,state,url,labels`
  - `rg -n "def progress_line|render_review|review_progress_counts|review=observing" ...`
  - `sed` で `review_progress_counts(...)`, `progress_line(...)`, 関連テスト、PR observation skill contract を確認。
- 実験条件:
  - 実装・canonical docs 具体化は未実施。
  - 調査対象は local worktree の current checkout。

## facts / 観測できた事実 (必須)
- `iss-00214` は `issue start` 済みで、active issue は `iss-00214`、親 epic は `epic-00158`。
- active issue の `requirement.md` / `design.md` / `plan.md` は import scaffold のままで、実質的な仕様情報は GitHub issue #214 body にある。
- GitHub issue #214 は、progress line の `review=observing` が監視対象である Codex review の状態ではなく、観測者側の状態を表示していることを問題としている。
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py` と `.agents/.../pr_observation_wait.py` は同じ問題箇所を持つ。
- `progress_line(...)` は `review_progress_counts(payload)["status"]` を `review_status` として取得した後、`phase == "wait" and not observation_complete` のとき `render_review = "observing"` で上書きしている。
- `review_progress_counts(...)` は `review.status` / `summary.review` を target state として返し、comments / threads / unresolved / requested count も集計する。
- `tests/unit/infra/test_init_update.py` には `phase=wait ci=passed review=observing` を期待するテストがあり、今回の仕様変更で更新対象になる。
- 既存テストには `review=unresolved`、`review=commented` と count 表示を確認するケースがあり、これらは壊してはいけない。
- `github-pr-observation/SKILL.md` は、`stderr` progress は非 authoritative、final JSON の `decision` / `decision_fingerprint` が authoritative と明記している。
- 同 skill は、通常 wait flow では caller / agent が手動 `@codex review` を投稿してはいけないこと、`wait_pr_observation.sh` が default `post-once` で固定 trigger を1回投稿することを明記している。

## inference / 推測 (必須)
- 事実から推測したこと:
  - 最小実装は provider-side `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py` の `progress_line(...)` を変更し、dogfooding mirror `.agents/...` へ反映する形になりそう。
  - `review=observing` の上書きを単純に削除すると、GitHub issue の主目的である target state 表示には近づく。
  - ただし `review.status="none"` かつ trigger metadata がある場合に `review=none` と出ると、operator-facing には「trigger 済みだが signal 待ち」という文脈が弱くなる可能性がある。
  - `observer=` や `wait=` の追加は、progress line の bounded key/value と optional field drop order への影響があるため、要求するなら design / tests で明示する必要がある。
- 推測の根拠:
  - GitHub issue #214 の実装ヒントは `render_review = "observing"` 上書きの廃止または別フィールド化を主な変更候補としている。
  - Existing skill contract は progress line を bounded summary として扱い、authoritative contract は final JSON に置いている。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - `review.status="none"` / `summary.review` / `codex_review.lifecycle.status` の全組み合わせで、既存 payload がどの状態値を持つか。
  - `trigger` metadata が `post-once` / `resume` / inferred / unknown の各ケースで progress line にどこまで反映可能か。
  - progress line の length cap と optional drop order に、`observer=` または `wait=` を追加しても問題ないか。
- 確認できない理由:
  - ここでは issue start と clarification 調査が目的で、実装・テスト設計はまだ開始していない。

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - `@codex review` trigger 済みだが、Codex review の completion / comment signal がまだない待機中状態を `review=` で何と表現するか。
- pressure-test question として切り出すべき候補:
  - `review=pending_signal` を標準名にするか、`review=none` / `review=triggered` / `review=no_completion_signal` など別名にするか。
- 質問せずに解決できた候補:
  - `review=observing` は避けるべき。GitHub issue #214 の問題文と受け入れ条件に明記されている。
  - final JSON の `decision` / `decision_fingerprint` contract は壊さない。skill contract と issue body に明記されている。
  - 手動 `@codex review` 投稿仕様、default `post-once`、snapshot read-only contract は非スコープ。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - `observing`: 現在の progress line では wait 中の observer state として使われているが、operator は `review=` を target review state と読んでしまう。
  - `pending`: 既存 payload / final status では non-terminal wait state として使われる。`review=pending` にすると「review target pending」なのか「whole wait pending」なのか曖昧になりうる。
  - `none`: target state としては正確な場合があるが、trigger 済みの文脈が progress line だけでは伝わりにくい。
- 既存 docs / code / tests / discussions での使われ方:
  - `review_completion_unknown` は、latency guards を満たした後の non-pass terminal-like review state として skill contract に記載されている。
  - `pending` / `timeout` / `human_gate` は final JSON status / decision path で既に使われている。
- 判断が必要な理由:
  - 状態名は user-facing progress line に出るため、operator の次行動と誤操作リスクに直接影響する。

## edge cases / 具体シナリオ (必須)
- edge case:
  - Trigger comment は投稿済み、CI は running、Codex review signal はまだゼロ。
  - CI は passed、Codex review completion signal はまだゼロ、latency guard 未満。
  - CI は passed、Codex review completion signal はまだゼロ、latency guard を満たして `review_completion_unknown` / `human_gate` へ進む。
  - Codex review が `unresolved` / `changes_requested` / `commented` になり、comments / threads / unresolved count を表示する。
  - Codex review が passed / approved 相当になり、final JSON は merge-prepared / passed path を示す。
- その edge case が requirement / design / plan に与える影響:
  - 待機中 signal ゼロの名称を決めないと、acceptance criteria と tests が曖昧になる。
  - `review_completion_unknown` との境界を誤ると、早すぎる human_gate や、逆に timeout の曖昧化につながる。

## implications / 判断への含意 (必須)
- Requirement では、`review=observing` を廃止し、`review=` は target state を表示することを受け入れ条件にする。
- Design では、`progress_line(...)` の target state derivation と、必要なら observer/wait state の別フィールド化を定義する。
- Plan では、existing `review=observing` expectation を failing test として更新し、待機中・unresolved・passed/approved の代表ケースを確認する。
- ADR は不要そう。これは public progress display contract の局所修正で、長期 architecture decision というより Issue-local design decision。

## リスク/制約 (任意)
- Progress line は非 authoritative だが、operator-facing で誤操作を誘発しうるため、表示名の clarity は重要。
- Provider-side source と dogfooding mirror の両方に影響する。
- Tests は `tests/unit/infra/test_init_update.py` に大きく集約されており、focused `-k` 実行が必要。

## 反映先 (任意)
- reflected_to:
  - `requirement.md` / `design.md` / `plan.md` authoring の input。
  - `report.md` Evidence Adoption Ledger / Spec Authoring Gate。

## 参考（References） (任意)
- GitHub issue #214: `PR observation progressのreview状態を監視対象基準で表示する`
- `20260619t064502z-interview-review-pending-state-naming.md`
