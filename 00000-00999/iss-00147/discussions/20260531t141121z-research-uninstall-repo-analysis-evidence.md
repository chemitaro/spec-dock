---
種別: research
ID: "20260531t141121z-research"
タイトル: "Uninstall repo analysis evidence"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-05-31"
親: ["iss-00147"]
関連: []
authority: "synthesized"
derived_from:
  - repo-analyst notification 019e7e57-f09b-7130-8a31-83b851a68d71
reflected_to:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/report.md
---

# 20260531t141121z-research Uninstall repo analysis evidence

## 調査目的
- `spec-dock uninstall` の要件定義に必要な、既存 installer / runtime / managed asset inventory / test surface / self-removal risk を source-grounded に整理する。
- repo-analyst sub-agent の read-only findings を、phase promotion で参照できる durable discussion evidence として固定する。

## sources / 調査方法
- 参照先:
  - `src/spec_dock/cli.py`
  - `src/spec_dock/assets/install_root/.agents/host-adapters/meta.json`
  - `src/spec_dock/assets/install_root/`
  - `src/spec_dock/assets/spec_dock/scripts/spec-dock`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/update.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`
  - `tests/test_init_update.py`
  - `tests/cli_runtime/test_update.py`
  - `tests/cli_runtime/test_runtime_shell_s11.py`
- 検証手順:
  - repo-analyst が read-only で source paths と implementation/test surface を確認。
  - orchestrator が requirement へ採用する事実だけをこの research に再記述。
- 実験条件:
  - code edit / command mutation は行っていない。

## facts / 観測できた事実
- installer CLI の正本は `src/spec_dock/cli.py` であり、現行 package entrypoint は `init` / `update` を持つ。
- installer は `spec-dock/` 内の managed scaffold directory と、repo root 側の `install_root` assets を target repo に同期する。
- `spec-dock/initiatives/**` は product/spec history として persistent data に近い扱いで、通常 update の managed overwrite 対象ではない。
- repo root 側の managed assets は `src/spec_dock/assets/install_root/` の recursive file inventory が正本である。
- `src/spec_dock/assets/install_root/.agents/host-adapters/meta.json` は `.codex/config.toml` を `bootstrap_only_exact_file_paths` として定義している。
- repo-local runtime `update` は repo 内で直接 installer logic を再実装せず、`uvx --no-cache --from git+https://github.com/chemitaro/spec-dock spec-dock update <target>` を呼ぶ thin wrapper pattern を採る。
- runtime command 追加の接点は `commands/<name>.py` の `command_specs()`、`cli/registry.py`、`cli/parser.py` である。
- repo-root `spec` shortcut は installer が作る SpecDock runtime shortcut であり、uninstall で扱うなら symlink target 確認が必要である。
- runtime entrypoint は `spec-dock/scripts/spec-dock` から runtime module を import して動くため、同一 process で runtime scaffold を削除する self-removal は platform / filesystem semantics により不安定化し得る。

## inference / 推測
- 事実から推測したこと:
  - uninstall の実処理は installer CLI 側へ置き、repo-local runtime command は update と同様に外部 installer invocation へ委譲する方が安全である。
  - uninstall inventory は installer の existing install_root plan builder と scaffold sync knowledge を再利用する設計が自然である。
  - tests は installer CLI integration と runtime wrapper tests に分ける必要がある。
- 推測の根拠:
  - 既存 `update` が runtime wrapper + installer implementation split を採用しているため。
  - repo-local runtime 自身が削除対象になり得るため。

## unverified / 未検証事項
- まだ確認していないこと:
  - 具体 implementation で既存 install plan helper をどこまで reuse できるか。
  - Windows filesystem semantics で runtime wrapper self-removal をどう扱うか。
- 確認できない理由:
  - requirement phase では HOW / platform-specific implementation を固定しないため。

## terminology conflicts / 用語衝突
- 衝突している用語:
  - `delete` と `uninstall`
- 既存 docs / code / tests / discussions での使われ方:
  - `delete` は local spec node / subtree deletion。
  - `uninstall` は target repo から SpecDock-managed development tooling / scaffold を取り外す repo-local operation。
- 判断が必要な理由:
  - `delete` の spec node cleanup と uninstall の repo-local tooling removal を混同すると、仕様履歴や repo root assets の削除境界が崩れる。

## edge cases / 具体シナリオ
- edge case:
  - repo-local runtime command が uninstall 実行中に削除される。
  - repo-root `spec` が user-created file または別 target の symlink である。
  - `.github/workflows/ci.yml` が SpecDock 由来から product CI として編集・流用されている。
- その edge case が requirement / design / plan に与える影響:
  - installer CLI direct retry path、shortcut target verification、product-reusable asset mismatch preservation を requirement に含める必要がある。

## implications / 判断への含意
- `requirement.md`:
  - repo-local wrapper + installer implementation を requirement として固定する。
  - repo-root `spec` shortcut は target match した場合だけ削除対象にする。
  - product-reusable managed assets は mismatch preserve にする。
- `design.md`:
  - installer CLI uninstall implementation と runtime wrapper subprocess invocation を分けて設計する。
  - removal inventory は managed scaffold / install_root / specs / generated state / shortcut を分類する。
- `plan.md`:
  - installer CLI tests、runtime wrapper tests、self-removal retry guidance、shortcut preservation tests を含める。

## リスク/制約
- self-removal を runtime process 内で完結させると partial failure recovery が弱くなる。
- current package asset と古い installed assets の comparison は version drift により mismatch が多くなり得る。
- unknown user-created paths は preserve を基本にしないと誤削除リスクが高い。

## 反映先
- reflected_to:
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/report.md`
