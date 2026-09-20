---
種別: 要件定義書（Epic）
ID: "epic-00384"
タイトル: "固定ディレクトリ再配置と検証の簡素化"
状態: "approved"
最終更新: "2026-09-19"
---

# Epic #384 — 固定ディレクトリ再配置による簡素化

## 決定と正本

2026-09-19のユーザー指示により、Epic自体を再構成する。正本は本Requirement、Design、Plan、および[再構成20260919t021920z-adr-directory-replacement-reconstruction.md](artifacts/20260919t021920z-adr-directory-replacement-reconstruction.md)である。旧E384-QUAL-001、Wire v12、P02、rolling-wave追加契約、旧failure register、#392/#395の実装保証は履歴であり、今回の実装を拘束しない。旧レビュー合格を新仕様の合格証拠へ流用しない。

## 目的

データ領域には触れず、固定されたツールディレクトリを削除し、配布パッケージのディレクトリをそのままコピーする。個別ファイルの保持・差分マージ・所有権台帳を廃止する。実装、旧テスト、CIをこの小さい契約へ切り替える。

## 範囲と動作

- R1: 管理対象は `spec-dock/{docs,templates,system,scripts}` と `.agents/skills/{spec-dock,spec-dock-grill-with-docs}` の6ディレクトリ。内部のローカル変更・未知ファイルも交換時に削除する。
- R2: 上記以外の利用者データ・仕様・成果物・設定・無関係なスキルには書き込まない。ディレクトリ内部で「このファイルだけ残す」という判断を持たない。
- R3: 初回initは未導入の `spec-dock/` に初期スキャフォールド全体をコピーする。既存領域へinitする場合は明示した `--force` が必要で、その場合はupdateと同じ6ディレクトリ交換になる。
- R4: updateは6ディレクトリを順番に削除・コピーする。旧バージョン記録やmarkerの検査による移行ゲートは設けない。欠損した管理対象も同じ処理で再配置できる。
- R5: バージョン表示用の `spec-dock/spec-dock.version` は単純な版文字列と改行にする。全配置成功後にだけ書く。runtime起動を認証する状態機械に使わない。
- R6: uninstallは既定dry-run、`--apply` で6ディレクトリとバージョン記録だけを削除する。データの削除機能は持たない。`--remove-specs` は引き続き拒否する。
- R7: 配布元の必要ディレクトリ不足、配置先の危険なsymlink/非ディレクトリ、I/O失敗は非ゼロ終了で通知する。固定対象とその親を事前確認し、データへの誤書込みを防ぐ。敵対的な同一ユーザーの競合、対象内部の個別inode追跡は保証しない。
- R8: 更新中は関連コマンドを停止して利用する。複数ディレクトリの原子的交換、クラッシュ後の自動再開、ロールバック、並行更新は保証しない。update失敗時は外部installerで同じ更新を最初からやり直す。この再配置保証は6管理ディレクトリに限り、初回initでコピーする設定は補修しない。初回init自体が失敗した場合は、利用者が不完全な `spec-dock/` を別の場所へ移して保全し、空いた配置先へinitを再実行する。ツールが利用者データを自動削除する復旧は行わない。途中失敗を成功と報告しない。
- R9: 通常のruntime起動は配置されたPythonプログラムを起動するだけとし、provider digest/slot marker/共有leaseの確認を廃止する。データ操作自身の既存ロック・整合性検査は別責務として保持する。
- R10: GitHub workflowの自動配置・個別ファイルseed管理を廃止する。既存の利用者workflowは変更しない。初回の `.gitignore` はスキャフォールド全体のコピーに含め、updateでは触らない。

## 撤去する保証・機構

永続lifecycle state、cleanup token、completion receipt、candidate digest、exact-legacy fixture、native rename exchange、provider専用descriptor/lease/checkout認証、およびそれらだけを検証するテストを撤去する。CPU比率、実効quota認証、first-five/latest-twenty、専用campaign/history/fault catalogue/evidence schema、保持期間H、same-SHA再実行禁止を撤去する。

旧台帳・timing weights・sharder・既定policy skipを廃止する。新しい所有権pluginや独自評価CLIで置換しない。通常のpytest、lint、パッケージの基本動作で検証する。

## 受入条件

1. init/update後の6ディレクトリが配布元と一致し、削除された配布ファイルや導入先だけのファイルが残らない。
2. 更新・削除前後で非対象データの内容が変わらない。
3. 不完全な配布元と危険な配置先は変更前に拒否する。updateの途中コピー失敗は非ゼロになり、同じupdateの再実行で6管理ディレクトリの正常配置へ戻る。初回initの失敗は非ゼロで報告し、R8の別途保全・fresh init手順でやり直す。
4. 外部installerと導入されたruntimeが動作し、wheel/sdistに必要なファイルが含まれる。
5. 旧専用機構とそのconsumerが現行コード/CIに残らず、残す一般機能のテストとlintが通る。
6. Linux/macOSの基本ファイル操作を検証する。性能専用の合格条件は設けない。
7. 指定の独立コードレビューと最終品質確認を通したPRを提出する。マージは人間が行う。

## 履歴と非ゴール

#392/#395とPR #403の修正は既存履歴。#395のURL認証情報をエラーへ漏らさない性質など、残る機能の回帰は守る。Issue状態を勝手に変更しない。実装は既存#396で完結させる。通常の仕様管理・GitHub操作・worktree機能の廃止や、利用者データの移行・削除は今回の目的に含めない。
