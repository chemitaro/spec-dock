---
種別: discussion
ID: "018"
タイトル: "issue-28 再修正後の comprehensive manual rerun 計画"
状態: "closed"
作成者: "Codex CLI"
作成日: "2026-03-18"
関連: ["requirement.md", "design.md", "plan.md", "report.md", "discussions/017-disc-manual-test-plan-postfix-validation.md"]
---

# issue-28 再修正後の comprehensive manual rerun 計画

## 目的
- `foreign URL + --allow-foreign-url` 修正後に、blocking defect が live 条件で解消していることを再確認する。
- 修正の副作用として、same-repo import、local-only flows、active / deps / sync / doctor / validate の周辺契約が崩れていないことを網羅的に確認する。
- 人間の coding agent が長時間・多操作・多 resource で実際に行いそうな作業列を再現し、局所テストでは出にくい順序依存・状態遷移・複合条件の bug を炙り出す。

## 今回ラウンドで前回から強化する点
- `MT-08` 相当の foreign import 境界だけでなく、same-repo / foreign / local-only の 3 系統を同一ラウンドで繰り返し往復する。
- GitHub live 側で issue close / reopen / newly created / imported / local-only coexistence を混在させる。
- organic session を「長い 1 本の流れ」と「途中で validate/doctor/deps を挟む checkpoint」の両方で記録する。
- 生成物 runtime の help 差分観測（`sev-3`）は再観測するが、主目的は runtime behavior の網羅確認とする。

## スコープ
- fresh local workspace での multi-resource 操作
- fresh GitHub test repository での live import / sync / deps / active / GitHub issue lifecycle 確認
- initiative / epic / issue / discussion / deps / active / sync / import / validate / doctor の横断操作
- foreign URL / same-repo URL / numeric target / explicit target flag の混在確認

## 非スコープ
- provider 実装の追加変更
- GitHub 以外の forge host
- 特殊 filesystem や CI 上の分散 lock 検証

## fresh GitHub repository を使う理由
- 前回 test repo には既存 issue と import 履歴が残っており、same-repo / foreign / close-reopen の観測が history 依存になりやすい。
- 今回は副作用確認と organic rerun を主目的にするため、クリーンな issue 番号列と empty repo から始めたほうが evidence の切り分けが明確になる。
- 結論:
  - 今回は fresh GitHub test repository を新規に 1 つ用意するのが望ましい。

## 推奨 GitHub test repository
- repository name:
  - `spec-dock-manual-rerun-issue-28-20260318`
- 必要条件:
  - 空 repository
  - 現在の認証で `git push` と `gh issue create/view/edit/close/reopen` が可能
  - 今回ラウンド専用に使う

## 手動テスト環境
- local workspace:
  - `manual-tests/workspaces/issue-28-manual-rerun/trial-local-2026-03-18/`
- GitHub live workspace:
  - `manual-tests/workspaces/issue-28-manual-rerun/trial-gh-2026-03-18/`
- report root:
  - `manual-tests/reports/2026-03-18-issue-28-manual-rerun/`

## ケース一覧

### RT-01 baseline fresh init and scaffold parity
- 目的:
  - fresh local repo で `spec-dock init` / generated runtime / provider runtime の基本状態を確認する。
- 主観点:
  - init 成功
  - active fallback / required artifact 初期状態
  - help surface 差分の再観測

### RT-02 broad local create matrix
- 目的:
  - initiative 2 件以上、epic 4 件以上、issue 8 件以上を作成し、複数 lineage の create / active / deps を確認する。
- 主観点:
  - duplicate id 非発生
  - 親子関係の整合
  - active 切替の安定性

### RT-03 discussion and artifact churn
- 目的:
  - 複数 issue に対して doc/discussion を連続追加し、途中で requirement / design / plan / report 編集と validate を挟む。
- 主観点:
  - duplicate seq 非発生
  - required artifact 契約維持
  - validate 継続成功

### RT-04 deps topology growth
- 目的:
  - issue 間 dependency を段階的に増やし、blocked / ready / done の変化と active 操作への影響を見る。
- 主観点:
  - deps check の安定性
  - local-only readiness
  - force/non-force active paths

### RT-05 recovery and odd local states
- 目的:
  - 軽微な missing artifact / broken meta / stale active pointer を意図的に作り、doctor/validate で recoverability を確認する。
- 主観点:
  - detectability
  - guidance の実用性
  - recovery 後の通常操作復帰

### RT-06 github live same-repo flows
- 目的:
  - fresh GitHub repo 上で gh issue を複数作成し、same-repo URL import / sync / deps / active / close-reopen を確認する。
- 主観点:
  - same-repo import success
  - sync freshness / source
  - close/reopen 反映

### RT-07 github live foreign-url safety
- 目的:
  - foreign URL default fail と `--allow-foreign-url` success を live で再確認し、副作用として same-repo path が壊れていないことを確かめる。
- 主観点:
  - repository mismatch fail
  - `--allow-foreign-url` success
  - same-repo no-regression

### RT-08 explicit target and ambiguity stress
- 目的:
  - `--id` / `--github-issue` / positional / URL target / invalid input を交互に使い、曖昧性 reject と正常系を確認する。
- 主観点:
  - explicit target surface の一貫性
  - invalid input reject
  - mixed mode confusion の不在

### RT-09 organic long-run operator session
- 目的:
  - local-only issue と GitHub-linked issue を混在させ、initiative/epic/issue を跨いで長時間の連続作業を行う。
- 想定する流れ:
  - initiative A/B を作る
  - epic を段階追加し、issue を並行作成する
  - 一部 issue は import、一部は local-only で起票する
  - deps を増やしながら active を切り替える
  - 途中で close/reopen、sync、doctor、validate、discussion 追加を挟む
  - 完了済み issue から別 issue / 別 epic へ移る
- 主観点:
  - 長い作業列でも active / deps / status / freshness が破綻しない
  - local / github / foreign import の混在で target 解釈が崩れない
  - 終盤でも validate / doctor が使える

### RT-10 summary and residue check
- 目的:
  - 全ケースの verdict、発見事項、継続観測事項、follow-up 候補を整理する。

## 実施順
1. RT-01 で fresh init / preflight
2. RT-02 から RT-05 まで local broad sweep
3. fresh GitHub repository 受領後に RT-06 から RT-08 を実施
4. RT-09 で local/GitHub を跨ぐ organic long-run session を実施
5. RT-10 で summary を確定

## ログ契約
- `checklist.md`:
  - ケース、前提、順序、完了条件
- `execution-log.md`:
  - 時刻、目的、precondition、command、expected、actual、diff、checks、verdict、evidence
- `summary.md`:
  - overall verdict、resolved findings、new findings、residual risks、next actions

## 完了条件
- `RT-01` から `RT-10` まで verdict がある
- fresh GitHub repository を用いた live cases `RT-06` `RT-07` `RT-08` `RT-09` が完了している
- `manual-tests/reports/2026-03-18-issue-28-manual-rerun/summary.md` に overall summary がある
