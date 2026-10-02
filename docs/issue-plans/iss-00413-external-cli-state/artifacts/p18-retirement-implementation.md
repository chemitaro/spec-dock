# P-18 Windows対応撤去の実装記録

2026-10-02 JST。基準はclean/push済み `dd90ca978fd711c32df7bbdf38aea516f62bbb1c`。P-18.2/P-18.3のsource/test checkpointであり、P-18全体、P-13、Code Review、FQの完了認定ではありません。P-16/P-17はhuman merge後です。

## 第三者ブリーフの採用

[GPT-5.6 Sol / Proブリーフ](p18-implementation-brief-dd90ca97.md)は22分31秒で完了、actual exit0。native metadataのmodel/thinking pickerは各verified=true、指定branch/full SHAのconnector照合を回答本文で確認。実装担当GPT-6.1 Sol / Maxと区別します。[元の回答bytes](p18-implementation-brief-dd90ca97-raw.json)はUTF-8原文とhashで保全し、readerでは末尾空白だけ整えました。

本文はR/D/Pを変更する第二正本ではありません。現物照合により次の実行補正を適用しました。

- unit Aのdomain限定で廃止予定のWindowsテストも不成立になるため、A/Bは収集・importを含めGreenで成立する一checkpointへまとめる。CIは別commit。
- 本文の `commit-codex -a -m ...` は使わない。最新の利用者提供AGENTS、`instruction-authorization.md` A1〜A6、`git-commit` に従い、生成は `commit-codex -a` 自身に委ねる。
- public `main` / domain境界で一件ずつRed→Greenを進める。private dispatcherの呼出し構造を判定条件にしない。
- P-07 Finish修正はこのsource diffに含めず、後続の別TDD/commitにする。current recordの限定scanは繰り返さない。

## source/testの実施範囲

`PhysicalIdentity` はposixと10進device/file_idのみ。work-target v1、Scope schema3、workspace protocol、Scope ID、記録tokenの形は不変です。単一business guardはutility後、installation/raw doctor/CI validate/通常context前に `UNSUPPORTED_PLATFORM` / exit3 / effects=[]を返します。初期化時のapplication/infra importもguard後へ移動し、fresh processでネイティブ依存のimport前に拒否します。

Win32 module、directory/JSON/mutex呼出し、専用三test、shared suiteのWindows専用部分を撤去。POSIX descriptor、nofollow、single-link、exact bytes、fsync/no-replace、Start-only flock、遅い観測済み解除は変更していません。Windows store未完成を表す古いskip文言は退役し、shared POSIX caseを保全しました。一般path/basename policyの `domain/artifacts.py` / `committed_workspace.py` は変更しません。

## TDDと検証

[全logとactual exit](p18-retirement-focused-evidence.json)に成功・失敗を別々に保存しています。

- 変更前のcharacterization: 63 passed / 1 Windows-only skipped、1.65秒、exit0。
- identity Red: Windows payloadをdomainが受理し `DID NOT RAISE`、exit1。POSIX限定後の同一testはexit0。
- OS guard Red: missing project解決へ到達しexit4。guard追加後の同一testはexit3と `UNSUPPORTED_PLATFORM`、test exit0。
- wheel Red: fresh wheelに `windows_handles.py` が含まれるためassertion failure、exit1。
- fresh-process追加検査で5 failures / 29 passed、exit1。guard前のmodule importからstdlib subprocessのfcntl importへ到達。依存importをguard後へ移して修正。
- 次の1 failure / 73 passedはtestが既存text headerを誤って禁止したharness assertion。既存rendererのheader契約へ合わせ、製品のtext rendererは変更しない。
- 最終focused: 74 passed、16.84秒、exit0。wheel/sdist、外部noneditable console、native POSIX別process、utility、保存/解除を含む。
- 影響する公開契約/Start/validate/native concurrent Start: 195 passed、56.10秒、exit0。
- `make lint`: Ruff check/format、mypyすべてpass、exit0。
- 通常collect-only: 1895 tests、exit0。collection exclusion/xfailを追加していません。

これらを通常fullや別OSのpassへ合算しません。Linux/macOS full、必要なPython3.10範囲、手動実console、fresh Code Review/FQは新候補SHAで後続実行します。source撤去後のWindows negative test文字列、既存の一般path防護、過去raw evidenceは削除対象ではありません。

## 残作業

Windows CI jobの別commit、provider docs/skills/static inventory、HTML/ZIP状態同期、OS別実検証は未完了。P-07のr12 P1も未修正。実dogfood metadata/active/controlは変更していません。この記録やブリーフ採用はSpecDock正式Startではありません。
