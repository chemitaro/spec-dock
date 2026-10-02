# Scope公開の事前判定を含む候補のmacOS全件検証

2026-10-02、clean <code>75ac57604f5b95f1c50a2e7214d711bc720fb0eb</code>、親6032621c、branch=codex/iss-00413-external-cli-stateを照合した。[Scope公開の事前判定](scope-publication-capability.md)と[Windows JSON読取](windows-json-read.md)を含む製品sourceの結果である。

## 実際の実行

    uv run pytest -q --tb=short -ra
    1900 passed, 4 skipped in 388.57s (0:06:28)
    exit 0

macOS arm64、実Python3.12.11、このcheckoutの.venvとsrc/spec_dock/のimport元を開始前に照合した。通常pytestを直接起動し、元sessionの実exit0を待った。独自runner、収集除外、policy skip、regression ledgerは用いていない。検査中はtracked sourceとdocsを変更せず、終了後も同HEAD・clean statusと製品source差分0を確認した。

元logはEpicのGit-ignored Workbench iss-00413-implementation/pytest-macos-full-scope-capability.log。関連287件や旧候補の結果へ合算しない。

4 skipは実Windows WAIT_ABANDONED、実Windows JSON/hardlink、実Windows親path置換、Linux O_TMPFILE能力試験。Windows/NTFSのnative成功を示すものではない。

| 製品source | SHA256 |
|---|---|
| src/spec_dock/runtime/infra/json_store.py | ba9850a8d31176d8c5b894d77aed6d93f696fb7f8175ccfb96f19fd3f0e2ae5b |
| src/spec_dock/runtime/infra/windows_handles.py | 75c9e3f6b50bde4a1fa3c544835a0a4862c8676e9651c5e612703ebe2d841bae |
| src/spec_dock/runtime/application/direct_scope_publish.py | cf193d6b5dc151a1622507e972fc0d224ca0bb59c18c56f55419d1075cd883f7 |

## 手動確認と未完了事項

同じ候補sourceの通常wheelを外部fresh venvへインストールし、[14回の個別手動操作](manual-console-75ac5760.md)も確認した。実Git、GitHub境界だけstateful fake ghを使用した。

Windows保存・各公開・process接続とnative受入、最新候補のCode Review StrictとFinal Quality Gate、人間merge後の実consumer切替・正式#413 import/Startは未完了。旧macOS比較不一致と旧runner不備の履歴を保持し、今回の成功で原因確定や過去結果の撤回を行わない。[全候補の検証証拠](implementation-acceptance-evidence.md)を参照する。
