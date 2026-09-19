---
種別: 設計書（Issue）
ID: "iss-00396"
タイトル: "固定ディレクトリ再配置への実装切替"
状態: "approved"
最終更新: "2026-09-19"
---

# Issue #396 — 設計

## 構成

installerを `cli.py`（引数・出力）と小さい配置処理へ分ける。配置処理はパッケージ内assetsを読み、固定の6パスに `shutil.rmtree` と `shutil.copytree` を適用する。ファイル別のmanifest/marker/保持リストを作らない。配布元はビルド成果物のディレクトリ構造を保つ。

## 更新の手順

1. ターゲットを絶対パスとして解決し、管理対象の親と6ディレクトリがsymlinkや不適切な種類でないことを確認する。
2. 配布元6ディレクトリが存在することを、削除を始める前に確認する。配布元を含む場所への自己上書きも拒否する。
3. 各対象が存在すれば丸ごと削除し、配布元から丸ごとコピーする。対象内部の古いファイルも残さない。
4. すべて成功した後、単純なバージョン記録を書く。

初回initのみ未導入のspec-dockスキャフォールド全体をコピーする。既存ターゲットのforce-initは通常updateと同じ処理にする。updateはデータ/設定seedを作成しない。配置元のPythonキャッシュはビルド成果物へ含めず、ローカルソース実行時にも配布対象から除く。

## 失敗と運用

途中失敗では混在状態が残り得る。利用者データは触らない。エラーを返し、外部installerのupdateをもう一度行う。途中状態の記録、旧版バックアップ、cleanup token、候補認証、自動復旧は作らない。通常のコマンドと更新の同時実行は運用上禁止する。

## runtimeとの境界

起動スクリプトはruntimeをimportしてdispatchする。更新/uninstallは外部installerに引き渡す。provider状態認証と共有leaseを削除する。Git操作に付加されたprovider世代の認証も外すが、Git操作自身の既存clean check、固定ref、安全なworktree対象判定は維持する。機能的に無関係なデータ操作ロックを撤去しない。

## テストとCI

置き換え契約は少数の一時ディレクトリ試験で確認する。旧provider_lifecycle専用suiteと生成器、専用regression ledger/sharderを撤去する。通常のruntime機能テストは保持する。CIの既存required job名を可能な範囲で維持し、`uv run pytest` と `make lint` を直接実行する。macOSはinstaller/runtime起動などの差分確認へ絞る。独自の履歴DB・qualification serviceは作らない。CI所要時間は通常ログで観察する。

## 文書の整合

旧Wire/qualification artifactは履歴として残し、現行R/D/Pから権威を外す。古いIssue #392/#395の受入を再演しない。provider側docsを更新後、同じinstallerを使ってdogfoodのツールだけを同期する。データ領域の内容比較を行う。
