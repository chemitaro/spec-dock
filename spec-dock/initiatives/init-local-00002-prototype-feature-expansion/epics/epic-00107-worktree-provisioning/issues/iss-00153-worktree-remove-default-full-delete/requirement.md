---
種別: 要件定義書（Issue）
ID: "iss-00153"
タイトル: "Default Full Delete For Worktree Remove"
関連GitHub: ["#153"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-02"
親: ["epic-00107", "init-local-00002"]
---

# iss-00153 Default Full Delete For Worktree Remove — 要件定義（何を、なぜ行うか）

## 目的
- `spec-dock worktree remove <target>` を、追加 option なしで dirty / untracked file を含む linked worktree まで完全削除できる command にする。
- 現行の「通常削除は失敗し、完全削除には `--force` が必要」という UX を改め、日常的な worktree cleanup を一手少なく安全に完了できるようにする。
- 既存の hard blocker と branch retention は維持し、削除対象の拡大ではなく削除強度の default を変更する。

## 背景・現状
- 現状の挙動:
  - `worktree remove <target>` は Git の通常 `worktree remove` を実行する。
  - dirty / untracked / locked state などで Git が通常 remove を拒否した場合、SpecDock は error を返し、filesystem cleanup を行わない。
  - `worktree remove <target> --force` は Git force removal を使い、成功後に resolved target path の target-only filesystem cleanup を行う。
  - 成功時も関連 local branch は削除せず、JSON の `branch_deleted` は `false` のままである。
- 現状の課題:
  - worktree cleanup の利用者は、未追跡ファイルを残すか完全削除するかを command invocation 時に明示する必要がある。
  - ユーザー意図としては完全削除が通常の cleanup であり、未追跡ファイルを残す挙動を default にする必要がない。
  - `--force` を付け忘れると dirty / untracked file がある worktree の削除が失敗し、cleanup 手順が止まる。
- 再現手順:
  1. `spec-dock worktree create dirty` などで linked worktree を作成する。
  2. 作成した worktree に Git 管理外ファイルを追加する。
  3. `spec-dock worktree remove dirty --json` を実行する。
  4. 現行では `git_worktree_remove_failed` が返り、worktree directory が残る。
- 観測点:
  - CLI:
    - `worktree remove` の text / JSON output、exit code、help text。
  - Filesystem:
    - resolved target path が削除されるか。
  - Git:
    - Git worktree record が削除されるか。
    - 関連 branch が残るか。
- 情報源:
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/epic/plan.md`
  - `spec-dock/docs/reference_worktree.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/worktree.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py`
  - `tests/cli_runtime/test_worktree.py`
  - `discussions/20260602t062811z-interview-worktree-remove-force-compatibility-question.md`

## 対象ユーザー / 利用シナリオ（必要時）
- 主な利用者:
  - SpecDock maintainer。
  - SpecDock を使って長命 linked worktree を並行開発・検証に使う agent / operator。
- 代表シナリオ:
  - 完了済み worktree に `.codex-log` や一時ファイルなど Git 管理外の residue が残っている状態で、operator が `worktree remove <target>` だけを実行して cleanup を完了する。
  - 既存 script や agent 手順が引き続き `worktree remove <target> --force` を指定しても、互換入力として受け付けられ、同じ完全削除 contract を満たす。

## スコープ
- 必須:
  - `worktree remove <target>` の default を完全削除に変更する。
  - dirty / untracked file を含む linked worktree でも、hard blocker がなければ option なしで削除できるようにする。
  - `--force` は後方互換のため受け付ける。ただし完全削除 default と同じ削除強度を表し、新しい強度選択や必須 option として扱わない。
  - `worktree remove` の text / JSON output、help、provider docs、dogfooding docs、runtime tests を新しい contract に合わせる。
  - Git worktree record の削除、resolved target path の target-only cleanup、`branch_deleted=false` を確認可能にする。
- 禁止:
  - main checkout、current checkout、bare worktree、missing path、record missing、containment guard を bypass しない。
  - branch deletion を行わない。
  - parent directory、central root、namespace directory、repo root を cleanup 対象にしない。
  - `worktree status`、`prune`、`repair`、orphan directory cleanup、Codex-managed worktree lifecycle cleanup をこの issue に含めない。
- 対象外:
  - `worktree create` / `list` / `show` の機能追加。
  - SpecDock node delete / uninstall の削除 mode 変更。
  - GitHub issue / PR / branch lifecycle の cleanup。

## 境界
- 常に行う:
  - `worktree remove <target>` は hard blocker がない linked worktree に対して完全削除 default として振る舞う。
  - 削除は Git-first とし、Git worktree remove 成功後だけ resolved target path の target-only filesystem cleanup を行う。
  - `--force` 指定時も default と同じ成功条件・失敗条件・出力契約を満たす。
  - 成功 JSON では `removed_record=true`、`removed_directory=true`、`branch_deleted=false` を維持する。
- 判断が必要:
  - locked worktree など Git がさらに強い force depth や別処理を要求するケースで、既存 adapter の force depth で対応できない場合は design phase で失敗契約を明確化する。
  - CLI help / docs で `--force` を deprecated compatibility option として明記するか、互換入力として短く記すかは design phase で決める。
- 行わない:
  - 未追跡ファイルを残す alternative mode はこの issue では追加しない。
  - `--keep-untracked` や `--preserve-untracked` のような新 option は追加しない。

## 非交渉制約
- Provider-side source of truth は `src/spec_dock/assets/spec_dock/...` とし、dogfooding workspace `spec-dock/...` は検証・反映対象として扱う。
- Runtime layered architecture を維持し、command / application / infra / presentation の既存責務を崩さない。
- Worktree removal tests は temp Git repo / temp worktree root を使い、live checkout の worktree を作成・削除しない。
- Existing `--force` invocation を壊さない。

## 前提
- 親 Epic `epic-00107` は `worktree list` / `show` / `remove` を agent-first command として提供する範囲を承認済みである。
- `worktree remove` は Git worktree records に存在する linked worktree を対象にする。
- `unmanaged` は削除可否 blocker ではなく classification diagnostic である。
- User interview で Option B を採用済みであり、`--force` は互換入力として維持する。

## 受け入れ条件
- AC-001:
  - アクター:
    - SpecDock maintainer。
  - 前提:
    - temp Git repo に linked worktree `untracked` が存在する。
    - `untracked` worktree には Git 管理外ファイルが存在する。
    - 対象 worktree は main / current / bare / missing / record missing / containment violation ではない。
  - 操作:
    - `spec-dock worktree remove untracked --json` を実行する。
  - 期待結果:
    - command は exit code `0` で成功する。
    - Git worktree record が削除される。
    - resolved target path が削除される。
    - JSON は `removed_record=true`、`removed_directory=true`、`branch_deleted=false` を返す。
    - 関連 branch は残る。
  - 観測点:
    - runtime test。
    - `git worktree list --porcelain`。
    - filesystem assertion。
- AC-002:
  - アクター:
    - SpecDock maintainer。
  - 前提:
    - temp Git repo に linked worktree `modified` が存在する。
    - `modified` worktree には tracked file の未コミット変更が存在する。
    - 対象 worktree は main / current / bare / missing / record missing / containment violation ではない。
  - 操作:
    - `spec-dock worktree remove modified --json` を実行する。
  - 期待結果:
    - command は exit code `0` で成功する。
    - Git worktree record が削除される。
    - resolved target path が削除される。
    - JSON は `removed_record=true`、`removed_directory=true`、`branch_deleted=false` を返す。
    - 関連 branch は残る。
  - 観測点:
    - runtime test。
    - `git worktree list --porcelain`。
    - filesystem assertion。
- AC-003:
  - アクター:
    - 既存 script / agent 手順。
  - 前提:
    - AC-001 または AC-002 と同等の dirty linked worktree が存在する。
  - 操作:
    - `spec-dock worktree remove <target> --force --json` を実行する。
  - 期待結果:
    - `--force` は互換入力として受け付けられる。
    - default remove と同じ成功条件・削除結果・branch retention を満たす。
  - 観測点:
    - runtime test。
- AC-004:
  - アクター:
    - SpecDock maintainer。
  - 前提:
    - target が main checkout、current checkout、bare worktree、missing path、record missing、または containment guard violation のいずれかである。
  - 操作:
    - `spec-dock worktree remove <target>` を実行する。
  - 期待結果:
    - 完全削除 default でも削除は拒否される。
    - Git worktree remove は hard blocker の前に実行されない。
    - `--force` 指定時も同じ hard blocker を bypass しない。
  - 観測点:
    - existing or updated hard blocker runtime tests。
- AC-005:
  - アクター:
    - SpecDock maintainer。
  - 前提:
    - Provider docs、dogfooding docs、CLI help、runtime tests を確認できる。
  - 操作:
    - `worktree remove` の command contract を確認する。
  - 期待結果:
    - docs / help は、引数なし remove が完全削除 default であることを示す。
    - docs / help は、`--force` が完全削除を有効にする必須 option ではなく互換入力であることを矛盾なく示す。
  - 観測点:
    - docs inspection。
    - CLI help assertion or inspection。

## 例外・エッジケース
- EC-001:
  - 条件:
    - target が locked worktree で、Git が既存 force depth でも removal を拒否する。
  - 期待:
    - command は Git error を隠さず失敗として返す。
    - filesystem cleanup は実行されない。
    - design phase で locked worktree の扱いを既存 adapter の限界として明文化する。
  - 観測点:
    - existing locked worktree test or guarded skip。
- EC-002:
  - 条件:
    - Git worktree remove は成功したが、resolved target path の cleanup が permission / race / unsupported type で失敗する。
  - 期待:
    - Git record removal と filesystem cleanup の結果を区別できる error / evidence を維持する。
    - parent directory や namespace directory の cleanup へ拡大しない。
  - 観測点:
    - existing cleanup failure tests or design-phase test mapping。
- EC-003:
  - 条件:
    - target が unmanaged linked worktree である。
  - 期待:
    - unmanaged は diagnostic として出力されるが、削除可否 blocker にはならない。
    - 完全削除 default と branch retention は managed worktree と同じ contract を満たす。
  - 観測点:
    - existing external worktree remove tests。

## 入力→出力例（必要時）
- EX-001:
  - 入力:
    - `spec-dock worktree remove dirty --json`
  - 出力:
    - `status=ok`、`removed_record=true`、`removed_directory=true`、`branch_deleted=false` を含む JSON。
- EX-002:
  - 入力:
    - `spec-dock worktree remove dirty --force --json`
  - 出力:
    - EX-001 と同じ削除 contract を満たす JSON。

## 用語（ドメイン語彙）
- TERM-001:
  - 完全削除 default:
    - `worktree remove <target>` が追加 option なしで Git force removal 相当の削除強度を使い、Git worktree record と resolved target path を削除する command contract。
- TERM-002:
  - hard blocker:
    - main checkout、current checkout、bare worktree、missing path、record missing、containment guard など、完全削除 default でも bypass してはならない削除拒否条件。
- TERM-003:
  - 互換入力:
    - 既存 script / agent 手順を壊さないために受け付けるが、新しい挙動を選ぶためには不要な option。今回の `--force` が該当する。

## 未確定事項
- なし。
