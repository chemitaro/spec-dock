# Blue Team 実装ブリーフ — S03/S04 direct transport P1

**結論:** production は変更せず、`tests/unit/infra/test_issue_planning_chatgpt.py` の既存 direct-transport テストだけを強化する。現行 runtime は attachment operand を `str()` のまま repeated `--file` へ渡し、Oracle 実行に `cwd=repo_root` を設定済みである。

## identity

* Repository: `chemitaro/spec-dock`
* Named branch: `codex/iss-00354-chatgpt-context-contract`
* Source HEAD: `91781cf507f979b02ba3ceb0a0610f2815114ec8`
* GitHub connector で branch の存在、および branch と source HEAD が `identical`（ahead/behind 0）であることを確認済み。default branch fallback は未使用・禁止。
* Fresh Red Team v3 の `P0=0 / P1=1 / FAIL` は依頼本文を正本とする。

## allowlist

* 変更可能: `tests/unit/infra/test_issue_planning_chatgpt.py` のみ。
* 対象: `test_direct_file_operands_preserve_order_and_do_not_materialize_pack` の拡張。
* 維持する許可:

  * Oracle session からの output artifact 読み取り。
  * output-only staging、ZIP snapshot、hash 計算。
  * 現行の `issue_planning_oracle_artifact`、`issue_planning_contracts`、テスト用 `_artifact` に対する output-side hash 例外。
* input operand に対する read/open/tree/copy/ZIP/hash/materialization は引き続き全禁止。

## テストケース

1. `repo_root = tmp_path / "repo"` を明示し、guard 導入前に次を準備する。

   * absolute static directory
   * absolute external `Candidate.zip`
   * lexical repository-relative source path

2. 上記3 operand を `SynthesizedPlanningPrompt.attachment_paths` に設定し、**dataclass の構築確認だけで終わらせず**、`invoke_issue_planning_chatgpt(repo_root=repo_root, ...)` へ実際に渡す。現状は direct transport テストの operand がすべて absolute で、relative-path テストは infra を呼び出していない。

3. guard 対象へ次の両表現を同時登録する。

   * lexical relative operand
   * `repo_root / relative_operand`

   両方を `Path.read_*`、`open`、`stat/resolve`、`iterdir/glob/rglob/scandir/listdir`、`shutil.copy* / move`、`ZipFile`、input-side `sha256` の禁止対象にする。

4. `fake_run` は `(argv, kwargs["cwd"])` を記録し、次を assert する。

   * `--file` operand は指定順かつ完全一致。
   * relative source の argv 要素は relative 文字列のままで、absolute path に変換されていない。
   * preflight と submit を含む全 Oracle subprocess call の `cwd == repo_root`。
   * input archive/copy/hash call count はすべて `0`。
   * prompt pack その他の input materialization が存在しない。

## 検証

```bash
uv run pytest tests/unit/infra/test_issue_planning_chatgpt.py \
  -q -k direct_file_operands_preserve_order_and_do_not_materialize_pack

uv run pytest tests/unit/infra/test_issue_planning_chatgpt.py -q
uv run ruff check tests/unit/infra/test_issue_planning_chatgpt.py
```

追加確認:

```bash
git diff --name-only 91781cf507f979b02ba3ceb0a0610f2815114ec8
```

出力は `tests/unit/infra/test_issue_planning_chatgpt.py` のみでなければならない。

## 完了条件

* mixed absolute/relative operand が実際の infra invocation を通る。
* relative argv の lexical identity と `cwd=repo_root` が同一テストで固定される。
* relative operand と `repo_root/relative` の両方に no-inspection/no-materialization guard が効く。
* focused test、対象ファイル全体、Ruff が成功する。
* Blue Team 修正は test-only diff。S03/S04 closure は後続 Fresh Red Team が `P0/P1=0` を確認するまで保留する。

## 非目標

* production runtime、provider/projection、resource の変更。
* requirement/design/plan、S05以降の変更。
* output-only artifact staging/hash policy の変更。
* default branch fallback。
* GPT-5.6 Luna / Max の性能・可用性・実測結果に関する主張。これらは未確認。

添付の別設計文書は、本 P1 修正の判断根拠には使用していない。
