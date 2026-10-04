# Windows JSON読取を含む候補のmacOS全件検証

2026-10-02、clean `6032621c2bd68ab9051b8929dd17d536a4114ad7`、親 `9a97f758c9948aa638ab40c3ed34f8565c09d81c`、branch `codex/iss-00413-external-cli-state` を照合し、通常の全件pytestを直接実行した。独自runner、収集除外、policy skip、regression ledgerは使用していない。

## 実際の実行

```text
uv run pytest -q --tb=short -ra
1876 passed, 4 skipped in 366.99s (0:06:06)
exit 0
```

macOS arm64、実Python 3.12.11、当該checkoutのvenvと `src/spec_dock/` import元を開始前に照合した。元sessionを完了まで待ち、終了後もHEADとclean statusを確認した。元logはEpicのignored Workbench `iss-00413-implementation/pytest-macos-full-6032621c.log`。関連58件の結果へ合算していない。

4 skipは実WindowsのWAIT_ABANDONED、実Windows JSON/hardlink、実Windows親path置換、Linux O_TMPFILE能力の確認である。Windows/NTFS成功を示す結果ではない。

候補内のSHA256は `json_store.py` = `6b6b80ed3272f650bf4cc4069bbb626335b4b152993d06b2910315fd69273053`、`windows_handles.py` = `75c9e3f6b50bde4a1fa3c544835a0a4862c8676e9651c5e612703ebe2d841bae`。[JSON読取の実装範囲](windows-json-read.md)を含む全件証拠である。

## 後続候補と区別すること

この全件後に[Scope公開の原語確認](scope-publication-capability.md)を追加したため、後続sourceの全件結果へ流用しない。Linux全件と手動consoleは8a70a8b3の証拠を保持する。旧macOS比較不一致の原因確定、Windows保存・process/native受入、現在候補のCode Review StrictとFinal Quality Gateの合格は、引き続き必要である。
