# Start保存原語確認を含む候補のmacOS全件検証

2026-10-02、clean `2b2be5e227ddf4d067da083bba15a8ec23d21367`、親578f27e3、branch=codex/iss-00413-external-cli-stateを照合した。[Startの保存原語確認](start-publication-capability.md)を含む製品sourceの結果である。

## 実際の実行

    uv run pytest -q --tb=short -ra
    1916 passed, 4 skipped in 434.98s (0:07:14)
    exit 0

macOS 27.0.1 arm64、実Python3.12.11、checkoutの.venvとsrc/spec_dock/のimport元を開始前と終了後に照合した。通常pytestを直接起動し、元session65514の実exit0まで待った。独自runner、収集除外、policy skip、regression ledgerは用いていない。検査中はtracked source/docsを変更せず、終了後も同HEAD・clean status・製品source hash不変を確認した。

元logはEpicのGit-ignored Workbench `iss-00413-implementation/pytest-macos-full-2b2be5e2.log`。log SHA256は `ad28c1d958c750d2852400c09c238bd05117fa8c00f316d145ae9d6128b2424f`。関連266件や過去候補の結果へ合算しない。

4 skipは実Windows WAIT_ABANDONED、Linux O_TMPFILE能力試験、実Windows JSON/hardlink、実Windows親path置換。Windows/NTFSのnative成功を示すものではない。

| 製品source | SHA256 |
|---|---|
| src/spec_dock/runtime/application/work_start.py | a2cb777b07888d2cd5934a949acb6d26043944f099b47260bb3c06a5b385ad6d |
| src/spec_dock/runtime/infra/json_store.py | ba9850a8d31176d8c5b894d77aed6d93f696fb7f8175ccfb96f19fd3f0e2ae5b |
| src/spec_dock/runtime/infra/windows_handles.py | 75c9e3f6b50bde4a1fa3c544835a0a4862c8676e9651c5e612703ebe2d841bae |

## 手動確認と未完了事項

同じ製品sourceの通常wheelを外部fresh venvへインストールし、[14回の個別手動操作](manual-console-2b2be5e2.md)も確認した。実Git、GitHub境界だけstateful fake ghを使用した。

Windows保存・各公開・process接続とnative受入、現在候補のCode Review Strict/Final Quality Gate、人間merge後の実consumer切替・正式#413 import/Startは未完了。先行候補の[1900件の全件](macos-full-75ac5760.md)、旧macOS比較不一致・旧runner不備の記録を保持し、今回の成功を過去結果の撤回や全OS認定へ変換しない。
