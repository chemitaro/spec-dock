# active set の non-canonical `git@.../issues/<n>` target 受理バグ報告

## 目的
- `iss-00052` の背景となった問題を、次セッションの実装担当者が迷わず再現・切り分け・修正できるように、事実と観測結果を具体的に残す。
- 今回の問題が `manual test harness` の環境不足ではなく、`active set` の target parsing / fail-closed 契約の product gap であることを明確化する。

## 結論
- `./spec-dock/scripts/spec-dock active set git@github.com:chemitaro/spec-dock-completion-guard-current-20260407/issues/1` が **受理されてしまう**。
- これは、現在の契約と観測済みの他ケースに照らすと **fail-closed で拒否されるべき入力** である。
- 同じ manual test では、`import issue` に対する non-canonical target や foreign canonical URL は適切に拒否されているため、問題は `active set` 側の parsing / validation path に限定される可能性が高い。

## 背景
- `iss-00051` の manual test では、completion gate 文言修正後の host-native shim / delegated workflow を再検証した。
- current repo 側の Codex delegated flow は、goal-level prompt だけで active issue set、docs 4 点の issue-specific content、`validate` / `sync --github` / review evidence を満たし、completion-quality を通過した。
- その一方で、negative-path / fail-closed 確認の中で `active set` が non-canonical `git@.../issues/<n>` を通してしまう挙動が観測された。

## 参照資料
- 実行ログ:
  - `manual-tests/workspaces/2026-04-07-iss-00051-completion-guard-real-manual/trial-gh-current/repo/reports/2026-04-07-iss-00051-completion-guard-real-manual/execution-log.md`
- サマリ:
  - `manual-tests/workspaces/2026-04-07-iss-00051-completion-guard-real-manual/trial-gh-current/repo/reports/2026-04-07-iss-00051-completion-guard-real-manual/summary.md`
- 補助コンテキスト:
  - `spec-dock/active/issue/report.md`
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/docs/reference_github.md`

## 観測した事実

### 1. current repo delegated flow 自体は成立している
- manual test の current repo trial では、Codex host-native shim が discovery / delegation entrypoint として機能した。
- delegated orchestrator は、goal-level prompt だけで次を実施した。
  - `manual-test-plan.md` / `manual-test-checklist.md` / `operator-brief.md` 読み込み
  - spec-dock hub skill / issue-execution skill の使用
  - `./spec-dock/scripts/spec-dock active show`
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync --github`
  - `./spec-dock/scripts/spec-dock deps check --github-issue 1 --github`
- active issue は `init-00002 / epic-00003 / iss-00001` で整合し、`spec-dock/active/issue/{requirement,design,plan,report}.md` も issue-specific content を持っていた。
- したがって、今回の問題は「manual test 全体が成立していない」ことではなく、specific negative-path bug である。

### 2. fail-closed が期待通り動いたケース
次のケースは拒否された。

```bash
./spec-dock/scripts/spec-dock import issue \
  https://github.com/chemitaro/spec-dock-completion-guard-foreign-20260407/issues/1 \
  --title 'foreign completion guard manual runtime seed' \
  --epic epic-00003
```

- 結果: foreign single-repo identity 制約で拒否

```bash
./spec-dock/scripts/spec-dock import issue \
  git@github.com:chemitaro/spec-dock-completion-guard-current-20260407/issues/1 \
  --title 'non canonical current issue' \
  --epic epic-00003
```

- 結果: invalid target / canonical URL required で拒否

```bash
./spec-dock/scripts/spec-dock active set https://example.com/not-github/issues/1
```

- 結果: invalid target で拒否

```bash
./spec-dock/scripts/spec-dock active set not-a-real-target-999999
```

- 結果: invalid target で拒否

### 3. 問題の再現コマンド
次のコマンドは **拒否されず受理された**。

```bash
./spec-dock/scripts/spec-dock active set \
  git@github.com:chemitaro/spec-dock-completion-guard-current-20260407/issues/1
```

観測結果:
- `target=github#1` として解釈され、成功扱いになった
- active issue 自体はたまたま既存の `iss-00001` に残ったが、入力 validation としては通してはいけないはずの target が受理された

## 期待挙動
- `active set` は URL-like target を扱うとき、**canonical GitHub issue URL** のみを受理するべき。
- `git@github.com:owner/repo/issues/1` のような SCP-style / ssh-like 表現は、`issue` target としては canonical ではないため **fail-closed で拒否** するべき。
- 少なくとも、`import issue` が拒否するものを `active set` が受理してはならない。

## 実際の挙動
- `import issue` は non-canonical `git@.../issues/<n>` を拒否する。
- `active set` は同種の non-canonical target を `github#1` 相当として受理してしまう。
- この不整合により、documented contract / fail-closed policy / command parity が崩れている。

## 問題の性質
- 分類: `product gap`
- 理由:
  - 環境 blocker では再現しない deterministic behavior である
  - 同一セッション内で他の malformed target は拒否されている
  - `import issue` と `active set` の間で validation contract がずれている

## 影響
- オーケストレーターや subagent が non-canonical `git@.../issues/<n>` を誤って組み立てた場合でも、`active set` が成功扱いになってしまう
- fail-closed を前提にした manual test / workflow contract / docs と実装がずれる
- 将来的に repo identity / foreign URL guard / parsing のバグが隠れる温床になる

## 推定される原因候補
- `active set` の target parsing が、canonical URL validation より前に broad な GitHub issue shorthand 解釈へ流れている可能性
- `git@github.com:owner/repo/issues/1` を、URL-like string ではなく `github#1` に近い shorthand として拾っている可能性
- `import issue` と `active set` で parser / validator が共通化されておらず、判定ルールが drift している可能性

## 次セッションの実装担当者向けに期待する調査
1. `active set` の target parsing / validation path を特定する
2. `import issue` が non-canonical target を拒否する path と比較し、差分を明確化する
3. `git@github.com:owner/repo/issues/<n>` を canonical issue URL と見なさない guard を追加する
4. 次の parity を回帰テスト化する
   - `import issue` rejects non-canonical `git@.../issues/<n>`
   - `active set` also rejects non-canonical `git@.../issues/<n>`
   - canonical `https://github.com/<owner>/<repo>/issues/<n>` remains accepted where appropriate

## 修正後の受け入れイメージ
- `active set git@github.com:.../issues/<n>` は invalid target として fail-closed する
- `active set` と `import issue` の malformed-target handling が揃う
- manual test の negative-path 結果と docs 契約が一致する

## 引き継ぎメモ
- 今回の issue は、manual test 全体の blocked 解消 issue ではない
- 主対象は **active set の non-canonical git target 受理バグ** である
- Copilot runtime blocker や current checkout installer proof blocker は別論点として扱う
- current repo Codex delegated flow / docs 4 点 completion / foreign canonical import fail-closed は、今回の bug の再現とは別にすでに観測済みである
