# Python 3.10互換性の検証記録

## 対象と環境

対象は `460d6d3990313a77174c6c74ac9eac2939645ae2` に、下記のtest fixture二行の修正だけを適用した候補。production変更、test削除、skip/収集除外の追加はない。P-12中の予備検証であり、P-13、fresh Strict、Final Quality Gate、最終手動確認の完了ではない。

- macOS/Darwinの実Python 3.10.15、package version 0.2.4。
- provider外の一時venvを `UV_PROJECT_ENVIRONMENT` で指定し、`sys.version_info`、`sys.prefix`、provider import元がこのcheckoutの `src/spec_dock` であることを実行前に照合した。
- `uv run --locked --no-env-file --no-python-downloads --python <verified-python3.10> python <runner> <isolated-venv> 3.10` で、通常pytestの全件を選択した。独自sharder/ledger/policy skipは使わない。
- checkoutのvolumeがAPFSであることはmount出力で確認済み。一時fixtureのfilesystem種別やLinux/Windowsをこの結果だけで認定しない。

## 初回の失敗と切り分け

初回全件は **1864 passed / 2 failed / 1 skipped、380.34秒、exit1**。元logは保持する。

1. `test_atomic_json_killed_after_exchange_retains_old_and_blocks_retry` は、確認用runnerのtop-level `pytest.main` がmultiprocessingのspawn子processでも実行されたため、queue待機で停止した。runnerに `if __name__ == '__main__'` を設けた。製品sourceの修正やkill境界の緩和はない。
2. `test_linux_explicit_import_uses_anonymous_staging_without_visible_probe_or_unlink` は、Python 3.10の `Path.stat` が保持するaccessorのため、`os.stat` の差替えでは模擬 `/proc/self/fd` に届かなかった。実Python 3.10の `Path.stat` sourceを確認した。模擬の差替え先と元関数を、製品が呼ぶ `Path.stat` に揃えた。anonymous stage、bytes、可視probeなし、unlinkなし、durability→commitの順序を検査する既存assertionは全て維持した。

runnerだけを直したfocused再実行は **1 passed / 1 failed、0.14秒、exit1**。上記2の失敗はこの条件でも再現した。これは検証harness/fixtureの互換性補正であり、新しい製品機能のRed→Greenとして数えない。

## 修正後の実測

| 検証 | 結果 |
|---|---|
| Python 3.10、atomic JSONとbinary publisherの二suite | 56 passed / 1 skipped、0.30秒、exit0 |
| 既定Python 3.12、同じ二suite | 56 passed / 1 skipped、0.21秒、exit0 |
| Python 3.10、通常全pytest | **1866 passed / 1 skipped、365.74秒、exit0** |
| 全source/tests Ruff check / format | 成功、311 files |
| `MYPYPATH=src` の変更test限定mypy | 成功、1 file。通常full lintの代替にしない |
| `git diff --check` | 成功 |

唯一のskipは既存 `test_binary_artifact_publisher.py` の **Linux O_TMPFILE capability test**。DarwinでLinux原語を実行した証拠にしない。実Linux、Python 3.11、Windows native/NTFS、通常full lint、fresh Strict、最終手動確認は別途未完了。実consumer、metadata、直接record、live GitHubは変更していない。

元logsは既存Epic Workbenchの `iss-00413-implementation/pytest-python310-460d6d39.log`、`pytest-python310-failure-isolation.log`、`pytest-python310-publication-green.log`、`pytest-python312-publication-green.log`、`pytest-python310-corrected-full.log` に保持する。
