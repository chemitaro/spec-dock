---
種別: 要件定義書（Issue）
ID: "iss-00174"
タイトル: "Refine PR Observation Two Stage Progress Output"
関連GitHub: ["#174"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-08"
親: ["epic-00067", "init-local-00003"]
---

# iss-00174 Refine PR Observation Two Stage Progress Output — 要件定義（何を、なぜ行うか）

## 目的
- `github-pr-observation` の `wait_pr_observation.sh` が長時間 polling するとき、stderr progress を「進行中は詳細、完了後は圧縮」の二段階表示に改善する。
- AI agent と human が、stdout final JSON を待っている間も CI / review の進捗と quiet reset の意味を読み取れるようにする。
- stdout final JSON を唯一の authoritative result とする既存契約を維持しつつ、progress 表示だけを観測しやすくする。

## 背景・現状
- `iss-00170` では、PR monitoring を `pr-monitor` sub-agent から deterministic `github-pr-observation` skill / scripts へ置き換えた。
- その結果、`wait_pr_observation.sh` は poll ごとに snapshot JSON を取得し、semantic fingerprint と quiet window により stable observation を待つ構造になった。
- 現在の stderr progress は、概ね次の粗い状態だけを出す。
  - `poll`
  - `elapsed`
  - `remain`
  - `phase`
  - `ci`
  - `review`
  - `quiet`
  - `limit`
  - `final=stdout_json`
- 現行表示では、CI が `running` のまま `checks=1/4 -> 2/4 -> 3/4` と進む様子や、Codex review comments が `0 -> 1 -> 2` と増える様子が見えない。
- 現行 `semantic_fingerprint()` は review signal には比較的追従している一方、CI check count progress を quiet reset の意味論へ十分に含めていない可能性がある。
- この issue は、`iss-00170` の main deliverable をマージした後に切り出した follow-up であり、移送済み discussions を正本要件へ昇格する。

## 情報源
- `discussions/20260608t024500z-research-progress-line-two-stage-status-analysis.md`
- `discussions/20260608t025500z-interview-progress-review-comment-count.md`
- `discussions/20260608t030500z-disc-progress-line-two-stage-design-proposal.md`
- `discussions/20260608t031000z-disc-progress-line-two-stage-implementation-plan.md`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
- `.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
- `tests/unit/infra/test_init_update.py`
- 親 epic `epic-00067` の install-shaped asset / provider-mirror parity 要件

## 対象ユーザー / 利用シナリオ
- 主な利用者:
  - PR 作成後に `github-pr-observation` skill を使って GitHub PR の CI / review を待つ main orchestrator agent。
  - 長時間 polling 中の stderr progress を読む human maintainer。
- 代表シナリオ:
  - PR 作成後、orchestrator が `wait_pr_observation.sh --progress stderr-summary` を実行する。
  - CI が複数 check run を実行している間、progress line で `checks=done/total` と内訳が増える。
  - Codex review が走っている間、trigger-window の current Codex review comments / review signals count が `comments=0 -> 1 -> 2` と増える。
  - CI / review が安定した後は、progress line が compact status に畳まれ、最終判断は stdout final JSON で行われる。

## スコープ
- 必須:
  - `wait_pr_observation.sh` の stderr progress を二段階表示にする。
  - CI が進行中の間、check run の `done/total` と短い内訳を progress line に出す。
  - Review が観測中の間、`@codex review` trigger 以後に今回の観測窓で新しく捕捉した Codex review comments / review signals 件数を `comments=N` として progress line に出す。
  - CI check count progress と review comment / thread progress が quiet reset の意味論に反映されるようにする。
  - CI / review が完了または stable human gate に到達した後は、progress line を compact status へ圧縮する。
  - stdout final JSON と stderr progress の分離を維持する。
  - provider source と dogfooding mirror の `wait_pr_observation.sh` の parity を維持する。
  - focused regression tests で progress line、quiet reset、stdout/stderr boundary、provider/mirror parity を検証する。
- 禁止:
  - progress line に review body、URL、reviewer name、workflow name、job name、failed step detail、P1/P2 text interpretation を出さない。
  - progress 表示を final decision authority にしない。
  - arbitrary GitHub query、raw `gh` args、任意 URL fetch、または progress 専用の新しい GitHub API call を追加しない。
  - 文字数削減のために stdout final JSON の既存 authority / schema を削らない。
  - 旧 `pr-monitor` sub-agent や旧 Codex-only review skill を復活させない。
- 対象外:
  - `@codex review` command の投稿責務変更。
  - review body / CI failure detail の final JSON schema 拡張。
  - GitHub API から「今後 review comment が増えない」ことを確定する仕組み。
  - `github-pr-merge-preparer` や `github-pr-creator` の責務変更。

## 境界
- 常に行う:
  - stdout final JSON を唯一の authoritative result として扱う。
  - stderr progress は 1 poll 最大1行の bounded key/value current-state summary とする。
  - `--progress none` では progress line を出さない。
  - `--progress stderr-summary` では human / agent が進捗を読める範囲の current counts を出す。
  - source of truth は provider side の `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh` とし、dogfooding mirror へ同期する。
- 判断が必要:
  - progress line が長くなりすぎる場合、どの optional field を落として `limit=truncated` にするかは design / implementation plan で固定する。
  - Review compact 後に human gate 理由として残す最小 count は design で具体化する。
- 行わない:
  - progress line に本文や個別 item detail を流さない。
  - progress のために GitHub 取得範囲を広げない。
  - source / mirror の片側だけを更新しない。

## 非交渉制約
- stdout は parseable final JSON のまま維持し、stderr progress と混在させない。
- progress line は poll ごとに最大1行とし、通常は 240 chars 程度までに収める。
- `comments=N` は、ユーザー回答により「`@codex review` trigger 以後に今回の観測窓で新しく捕捉した Codex review comments / review signals の件数」と定義する。
- 古い PR 全体コメントや過去の unresolved thread は、progress の `comments=N` へ毎回積み上げない。
- CI の `checks=done/total` は、初期実装では GitHub check runs の terminal count / total を主 denominator とする。
- commit statuses / required-check rollup は CI status 判定と limitations に使い、必要が出るまで `checks=done/total` denominator へ混ぜない。
- Review の「完了」は GitHub API で絶対確定しようとせず、wait loop の `observation_complete` / stable 条件と current review status で表示粒度を切り替える。
- `limit=none` を通常値とし、optional fields を落とした場合だけ `limit=truncated` とする。現行の `limit=ok` は本 issue で整理対象とする。

## 前提
- `fetch_pr_observation_snapshot.sh`、checks collector、review collector は、progress 表示に必要な CI check run counts、review signals、threads、limitations を既に snapshot JSON に含められる。
- 本 issue の主変更対象は wait wrapper の progress projection、semantic fingerprint、stderr rendering、focused tests である。
- `tests/unit/infra/test_init_update.py` に既存 PR observation fixtures / fake `gh` harness があり、追加 regression を同じ近傍に置ける。
- `epic-00067` の contract により、installed agent-tooling assets は provider source と dogfooding mirror の両方を考慮する必要がある。

## 受け入れ条件
- AC-001:
  - アクター: main orchestrator agent
  - 前提: `wait_pr_observation.sh --progress stderr-summary` が CI running 中の snapshot を polling している
  - 操作: check runs が total 4、success 2、running 2 の payload を観測する
  - 期待結果: stderr progress line に `pr_obs` prefix、`ci=running`、`checks=2/4`、`ok=2`、`run=2`、`pend=0`、`fail=0` が含まれる
  - 観測点: focused pytest / stderr assertion
- AC-002:
  - アクター: main orchestrator agent
  - 前提: CI check runs が `checks=0/3 -> 1/3 -> 2/3 -> 3/3` と進む
  - 操作: wait loop が同じ coarse `ci=running` status のまま複数 poll する
  - 期待結果: check count progress が semantic fingerprint / quiet reset の対象になり、`latest_change_poll` と `quiet` が最後の count 変化を反映する
  - 観測点: focused pytest / final JSON `wait.latest_change_poll` / stderr `quiet`
- AC-003:
  - アクター: main orchestrator agent
  - 前提: CI が terminal success になっている
  - 操作: wait loop が completion / stable 判定へ進む
  - 期待結果: stderr progress line は `ci=passed` の compact 表示になり、通常の detailed `checks=` / `ok=` / `run=` fields を省略する
  - 観測点: focused pytest / stderr assertion
- AC-004:
  - アクター: main orchestrator agent
  - 前提: `@codex review` trigger 以後の current observation window で Codex review comments / review signals が `0 -> 1 -> 2` と増える
  - 操作: wait loop が review observing 中に複数 poll する
  - 期待結果: stderr progress line の `comments=N` が `0 -> 1 -> 2` と増え、古い PR 全体コメントや過去の unresolved thread は `comments=N` に含まれない
  - 観測点: focused pytest / stderr assertion / trigger-window fixture
- AC-005:
  - アクター: main orchestrator agent
  - 前提: review comment count または unresolved thread count が増減する
  - 操作: wait loop が次 poll を処理する
  - 期待結果: review progress change が semantic fingerprint / quiet reset の対象になり、no-change poll では quiet が伸びる
  - 観測点: focused pytest / final JSON `wait.latest_change_poll` / stderr `quiet`
- AC-006:
  - アクター: main orchestrator agent / human maintainer
  - 前提: review observation が stable human gate に到達し、status が `unresolved` または `changes_requested` である
  - 操作: wait loop が terminal / observation complete progress を出す
  - 期待結果: stderr progress line は compact status を中心にしつつ、human gate 理由として `comments=N` を必ず残す。thread state が human gate の根拠に含まれる場合は `threads=N` と `unresolved=N` も残す
  - 観測点: focused pytest / stderr assertion
- AC-007:
  - アクター: script caller
  - 前提: `--progress none` を指定する
  - 操作: wait script を実行する
  - 期待結果: stderr progress line は出ず、stdout final JSON は現行どおり parseable である
  - 観測点: focused pytest / stdout JSON parse / stderr empty assertion
- AC-008:
  - アクター: script caller
  - 前提: `--progress stderr-summary` を指定する
  - 操作: wait script を実行する
  - 期待結果: stdout は final JSON のみであり、stderr progress line に review body、URL、reviewer name、workflow name、job name、failed step detail が含まれない
  - 観測点: focused pytest / stdout-stderr boundary assertion
- AC-009:
  - アクター: maintainer
  - 前提: progress line に optional fields が多い payload を観測する
  - 操作: rendering が line length budget を超えそうになる
  - 期待結果: optional fields を落として `limit=truncated` を表示し、通常時は `limit=none` を表示する。単純な token途中 slice を通常経路にしない
  - 観測点: focused pytest / stderr length and `limit` assertion
- AC-010:
  - アクター: maintainer
  - 前提: provider source と dogfooding mirror の wait script が存在する
  - 操作: implementation 後に parity を確認する
  - 期待結果: `src/spec_dock/assets/install_root/.../wait_pr_observation.sh` と `.agents/.../wait_pr_observation.sh` が一致する
  - 観測点: `diff -u` / scaffold parity test

## 例外・エッジケース
- EC-001:
  - 条件: check runs が 0 件、または GitHub check metadata がまだ出揃っていない
  - 期待: 既存 zero-check grace / pending / limitation semantics を壊さず、progress は `ci=pending` または `ci=none` と短い counts を出す。false passed にしない
  - 観測点: focused pytest / existing zero-check regression
- EC-002:
  - 条件: check runs は skipped / neutral を含み、failed はない
  - 期待: GitHub 上 merge を妨げない terminal outcome は `done` / `ok` に含め、最終 CI status は existing pass semantics と整合する
  - 観測点: focused pytest / CI status assertion
- EC-003:
  - 条件: failed check run がある
  - 期待: compact 後は `ci=failed` と最小 `fail=N` を表示でき、workflow / job / failed step detail は final JSON に委ねる
  - 観測点: focused pytest / stderr assertion / final JSON failures assertion
- EC-004:
  - 条件: old unresolved thread が PR に存在するが、今回の trigger window 後に新規 Codex review comment はない
  - 期待: progress の `comments=N` は 0 のままにできる。final JSON の review status / human gate は既存 thread state に基づいて維持する
  - 観測点: focused pytest / trigger-window fixture
- EC-005:
  - 条件: trigger comment が不明、または trigger timestamp が取得できない
  - 期待: progress count は安全側に倒し、古い body / comments を新規 progress として数えない。limitation があれば `limits=N` などで示せる
  - 観測点: focused pytest / limitation assertion
- EC-006:
  - 条件: snapshot collection が deadline 近くで timeout する
  - 期待: 既存 latest-payload preservation と `snapshot_poll_timeout` limitation を壊さず、progress rendering が stdout final JSON を破壊しない
  - 観測点: existing timeout regression / focused pytest
- EC-007:
  - 条件: payload は変わらないが raw review body text だけが変わる
  - 期待: raw body text だけを semantic fingerprint / progress reset の主因にせず、既存 raw-body-only stability regression を維持する
  - 観測点: existing focused pytest
- EC-008:
  - 条件: progress line が line length budget を超えそうになる
  - 期待: optional fields を deterministic order で落とし、`limit=truncated` を出す。stdout final JSON には影響しない
  - 観測点: focused pytest

## 入力→出力例
- EX-001:
  - 入力: CI running、check runs total 4 / success 2 / running 2、review observing comments 0
  - 出力:
    ```text
    pr_obs poll=4 elapsed=120 remain=1680 phase=wait ci=running checks=2/4 ok=2 run=2 pend=0 fail=0 review=observing comments=0 quiet=30/90 stable=1/2 limit=none final=stdout_json
    ```
- EX-002:
  - 入力: CI running、review comments が2件に増加
  - 出力:
    ```text
    pr_obs poll=8 elapsed=240 remain=1560 phase=wait ci=running checks=3/4 ok=3 run=1 pend=0 fail=0 review=observing comments=2 threads=2 unresolved=2 quiet=0/90 stable=1/2 limit=none final=stdout_json
    ```
- EX-003:
  - 入力: CI passed、review none、observation stable
  - 出力:
    ```text
    pr_obs poll=12 elapsed=480 remain=1320 phase=terminal ci=passed review=none quiet=70/90 stable=3/2 limit=none final=stdout_json
    ```
- EX-004:
  - 入力: CI passed、review unresolved human gate
  - 出力:
    ```text
    pr_obs poll=14 elapsed=540 remain=1260 phase=terminal ci=passed review=unresolved comments=3 threads=2 unresolved=2 quiet=70/90 stable=3/2 limit=none final=stdout_json
    ```

## 用語
- `progress line`:
  - `wait_pr_observation.sh --progress stderr-summary` が poll ごとに stderr へ出す 1 行の current-state summary。
- `stdout final JSON`:
  - wait script が stdout へ最後に出す authoritative result。progress line はこれを代替しない。
- `two-stage progress`:
  - CI / review が進行中の間は count-based detail を出し、完了後または stable 後は compact status へ圧縮する表示方針。
- `comments=N`:
  - `@codex review` trigger 以後に今回の観測窓で新しく捕捉した Codex review comments / review signals の件数。
- `checks=done/total`:
  - 初期実装では GitHub check runs の terminal count / total。commit statuses / required-check rollup は別の status 判定に使う。
- `quiet reset`:
  - semantic fingerprint が変わったときに wait loop の quiet elapsed をリセットすること。

## 未確定事項
- なし。
  - 重要なユーザー意図 blocker だった `comments=N` の定義は、`discussions/20260608t025500z-interview-progress-review-comment-count.md` で回答済み。
  - 残る詳細は design / plan で具体化する低リスク実装方針であり、要件作成を止める質問ではない。
