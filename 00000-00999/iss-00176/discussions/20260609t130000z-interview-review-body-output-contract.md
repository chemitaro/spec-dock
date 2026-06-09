# Interview: Codex review body output contract

- 作成日: 2026-06-09
- 対象: `iss-00176 GitHub PR observation should trigger and wait for Codex review completion`
- 種別: answered interview
- 状態: answered

## 背景

`requirement.md` では、`wait_pr_observation.sh` の final `stdout` JSON を authoritative result とし、`--out` は optional debug / audit artifact として扱う方針が確定している。

また、`resume` mode では reviews / review comments / review threads の fetched counts / IDs、selected IDs、boundary-before exclusion evidence を検証可能にすることも要件化された。

一方で、Codex review の本文をどこまで final `stdout` JSON に含めるかは、要件上まだ明確ではない。

関連する既存情報:

- `requirement.md`
  - stdout final JSON は authority。
  - `--out` は authority ではない。
  - selected review output を含める。
  - reviews / review comments / review threads の collection summary を検証可能にする。
- 現行 script contract
  - `fetch_pr_review_snapshot.sh` には `--body-mode none|trigger-window-truncated|trigger-window-full|out-only` がある。
  - `trigger-window-full` は stdout JSON が大きくなり得る。
  - `out-only` は本文を artifact 側に逃がせるが、final stdout JSON だけを読むエージェントにとって review 本文の authority が弱くなる。
- これまでのユーザー意図
  - GitHub API を追加で叩かず、スクリプトの実行結果から Codex review 本文を読めることを重視していた。
  - 一方で、長い stdout JSON はコンテキスト圧迫や取り回しの悪さを生む可能性がある。

## 確認したいこと

`wait_pr_observation.sh` の final `stdout` JSON には、trigger boundary 以降に選択された Codex review 本文を、原則として全文含めるべきですか。

## 選択肢

### A. stdout に選択済み review 本文を全文含める（推奨）

- final `stdout` JSON だけで、メインエージェントが review 内容を読み、修正要否を判断できる。
- `--out` は copy / raw / audit 用に残せるが、authority は stdout に保てる。
- 長い review では stdout JSON が大きくなる。
- 実装では body cap / item cap を設けず、Codex review output の完全性を優先する必要がある。

### B. stdout は要約・ID・counts までにし、本文全文は `--out` artifact に置く

- stdout は小さく安定する。
- ただし、エージェントが最終 JSON だけで review 本文を読めず、追加 artifact read が必要になる。
- `--out` の authority 境界が曖昧になりやすい。

### C. stdout は既定で truncated、必要時だけ full body mode

- 既定の出力サイズを抑えつつ、必要時に全文取得できる。
- ただし、通常 workflow でエージェントが全文を読み損ねる可能性が残る。
- mode 選択を実行エージェントに委ねる分、非決定性が増える。

## 推奨

推奨は **A. stdout に選択済み review 本文を全文含める**。

理由:

- この issue の目的は、メインエージェントが GitHub を追加探索せず、script contract から PR observation と Codex review output を判断できるようにすることにある。
- final `stdout` JSON を authority とする既存方針と最も整合する。
- `--out` は raw evidence / debug / audit copy として残せるが、本文の唯一の所在にはしない方がよい。

## 回答欄

- ユーザー回答:
  - はい。final `stdout` JSON に選択済み Codex review 本文を全文含める。
  - エージェントが GitHub CLI / GitHub API を用いて後から review 本文を取得しようとすると、全件コメント取得によるノイズ、または `gh api` による変更可能な API 利用リスクに直面する。
  - そのため、危険な追加 API 操作やノイズの多い全件取得を避け、スクリプトの標準出力 JSON テキストから必要な review 情報だけを取得できることが望ましい。
- 採用判断:
  - 採用: A. stdout に選択済み review 本文を全文含める。
  - `--out` は raw / debug / audit 用として残せるが、review 本文の唯一の所在にはしない。
- 反映先:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md` Evidence Adoption Ledger / Spec Authoring Gate
