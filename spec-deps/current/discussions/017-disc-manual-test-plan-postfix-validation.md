---
種別: discussion
ID: "017"
タイトル: "issue-28 修正後の manual test 計画"
状態: "open"
作成者: "Codex CLI"
作成日: "2026-03-18"
関連: ["requirement.md", "design.md", "plan.md", "report.md"]
---

# issue-28 修正後の manual test 計画

## 目的
- `issue-28-runtime-regression-bugs` で修正した runtime 回帰が、実運用に近い複数 resource / 複数操作の組み合わせでも再発しないことを確認する。
- 通常操作、複数 resource を伴う日常利用、やや変則的だが実行可能な手順を混ぜて、潜在的な runtime bug を炙り出す。
- local-only と GitHub-linked の両経路で、create / validate / doctor / deps / active / import の整合を手動で確かめる。

## スコープ
- local workspace を使った multi-resource 操作
- GitHub test repository を使った live import / sync / active / deps の確認
- issue / epic / initiative を複数件作るシナリオ
- duplicate / stale / missing artifact / explicit target ambiguity の再発確認

## 非スコープ
- provider 実装の追加修正
- GitHub 以外の forge host
- NFS など特殊 filesystem の lock 検証

## 前提
- 現在ブランチ `fix/issue-28-runtime-regression-bugs` の実装・自動テストは完了済み
- 手動テスト成果物は `manual-tests/` 配下に記録する
- GitHub live test には専用の test repository が必要

## 手動テスト環境
- local workspace:
  - `manual-tests/workspaces/issue-28-postfix-manual/trial-local-2026-03-18/`
- GitHub live workspace:
  - `manual-tests/workspaces/issue-28-postfix-manual/trial-gh-2026-03-18/`
- report root:
  - `manual-tests/reports/2026-03-18-issue-28-postfix-manual/`

## ケース一覧

### MT-01 baseline local init
- 目的:
  - 新規 local repo で `spec-dock init` が正常に初期化され、active fallback と template 群が揃うことを確認する。
- 主観点:
  - init 成功
  - required artifact 初期状態
  - active fallback entrypoint

### MT-02 multi-resource local create
- 目的:
  - initiative 2 件以上、epic 3 件以上、issue 6 件以上を作り、ID 採番・配置・active 操作が安定することを確認する。
- 主観点:
  - duplicate id 非発生
  - issue / epic の親子関係
  - `active set/show`

### MT-03 discussion sequence stress
- 目的:
  - 同一 issue で doc/discussion を複数作成し、seq が連番で衝突しないことを確認する。
- 主観点:
  - duplicate seq 非発生
  - validate 成功
  - docs 追加後の report/plan 維持

### MT-04 local-only status and deps
- 目的:
  - GitHub 未連携 issue 群で `deps check`, `active set`, `sync --no-github` 相当の local-first 経路が整合することを確認する。
- 主観点:
  - local-only issue の readiness
  - freshness 表示
  - active 経路との一致

### MT-05 validate and doctor recovery
- 目的:
  - 実行可能な範囲で軽微な破損状態を作り、`validate` と `doctor` が期待どおりの guidance を返すことを確認する。
- 主観点:
  - missing artifact
  - broken meta
  - stale active pointer
  - duplicate seq / duplicate id の検知面

### MT-06 odd but plausible local flows
- 目的:
  - 実使用で起こりうる変則手順を混ぜ、順序依存の不具合を探る。
- 手順候補:
  - active 未設定のまま `deps check`
  - issue 作成直後に active 切替を連打
  - local-only issue と GitHub-linked issue を混在させた `active set`
  - plan/report を編集した後の `validate`

### MT-07 github live import and sync
- 目的:
  - 専用 test repository 上の issue を import し、current repo 判定、sync、deps、active が safe default で動くことを確認する。
- 主観点:
  - canonical URL import success
  - current repo identity 判定
  - sync 後 freshness / source

### MT-08 github target safety and explicit intent
- 目的:
  - wrong-repo URL と explicit target flag を使い、誤操作防止が働くことを確認する。
- 主観点:
  - foreign URL default fail
  - `--allow-foreign-url` opt-in success
  - `--id` / `--github-issue` / positional target の曖昧性 reject
  - `new issue --create-github-issue` の正常系

### MT-09 summary and residue check
- 目的:
  - 全ケースの残課題、再現ログ、未実施項目、追加修正候補を整理する。
- 主観点:
  - case verdict 集約
  - discovered issue の切り分け
  - 再実行要否

### MT-10 organic long-run operator session
- 目的:
  - 人間の coding agent が長時間にわたり initiative / epic / issue / discussion / deps / active / sync / import を行き来する実運用に近い手順を再現し、順序依存や状態遷移のほつれを探す。
- 想定する行動:
  - initiative を作成し、複数 epic を段階追加する
  - issue を複数並行で立て、active を頻繁に切り替える
  - 一部 issue は local-only のまま進め、一部は GitHub issue と連携する
  - 完了した issue を閉じた前提で次の issue / epic へ移動し、deps を継続的に増やす
  - discussion/doc を途中で追加し、validate / doctor / deps / sync を要所で挟む
  - URL import、explicit target flag、active fallback を混在させる
- 主観点:
  - 長い操作列のあとでも active / deps / status / freshness が破綻しない
  - local-only と GitHub-linked の混在で target 解釈が崩れない
  - validate / doctor が終盤でも実用的な診断を返す
  - 依存関係を増やした状態でも CLI 操作が一貫する

## 実施順
1. MT-01 で local workspace 初期化
2. MT-02 から MT-06 まで local-only / local mixed の確認
3. GitHub test repository 受領後に MT-07, MT-08 を実施
4. MT-10 で local / GitHub linked を混在させた長時間セッションを実施
5. MT-09 で summary を確定

## ログ契約
- `checklist.md`:
  - ケース一覧、前提、実施順、完了条件を記録する
- `execution-log.md`:
  - 各ケースごとに、日時、目的、事前状態、実行コマンド、期待結果、実結果、差分、判定、補足を残す
- `summary.md`:
  - overall verdict、発見事項、blocked / skipped、推奨 next action を残す

## GitHub test repository 要件
- 推奨 repository name:
  - `spec-dock-manual-test-issue-28-20260318`
- 受領済み URL:
  - `https://github.com/chemitaro/spec-dock-manual-test-issue-28-20260318`
- 必要条件:
  - 空の repository であること
  - 現在のユーザー認証で `git push` と `gh issue create/view` 相当ができること
  - URL を受領後、その repository を GitHub live workspace の `origin` として利用する

## 完了条件
- `MT-01` から `MT-10` までの各ケースに verdict がある
- GitHub live が実施可能なら `MT-07` `MT-08` `MT-10` の live 含みケースまで完了している
- `manual-tests/reports/2026-03-18-issue-28-postfix-manual/summary.md` に overall summary がある
