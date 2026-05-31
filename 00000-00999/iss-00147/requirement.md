---
種別: 要件定義書（Issue）
ID: "iss-00147"
タイトル: "SpecDock uninstall command"
関連GitHub: ["#147"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-05-31"
親: ["epic-00054", "init-local-00002"]
---

# iss-00147 SpecDock uninstall command — 要件定義（何を、なぜ行うか）

## 目的
- `spec-dock` 導入済み repo から、開発用の SpecDock agent / skill / tooling を安全に取り除ける repo-local uninstall capability を追加する。
- 開発完了後、second brain / LLM wiki のように agent や skill 自体がプロダクト運用のノイズになり得る repo で、SpecDock 由来の開発支援設定を整理できるようにする。
- 実行環境の Python package / global CLI / uvx cache を削除するのではなく、target repo 内に配置された SpecDock-managed artifacts の removal を扱う。

## 背景・現状
- 現状の挙動:
  - installer entrypoint は `spec-dock init [path]` と `spec-dock update [path]` により、target repo に `spec-dock/` scaffold と agent / skill assets を導入・更新する。
  - repo-local runtime command には installer update を呼び出す `./spec-dock/scripts/spec-dock update` がある。
  - local spec node deletion は既存の `delete` command が扱うが、repo から SpecDock の開発用 tooling 全体を取り外す command はない。
- 現状の課題:
  - 開発完了後の product repo に、`.agents/skills/**`、`.codex/agents/**`、`.github/agents/**` などの開発用 agent / skill assets が残り続ける。
  - sub-agent や skill の稼働が product behavior の一部になる repo では、SpecDock の開発用 agent / skill が discovery や運用判断のノイズになる。
  - 仕様履歴を残して再開発可能性を保ちたい repo と、使い捨てで履歴ごと消したい repo の両方があり、仕様履歴削除を暗黙 default にできない。
  - `.codex/config.toml` など user edit が入り得る bootstrap-only file や、product repo に流用された CI / config / prompt / rule を誤削除するリスクがある。
- 情報源:
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/epic/design.md`
  - `src/spec_dock/cli.py`
  - `src/spec_dock/assets/install_root/.agents/host-adapters/meta.json`
  - `src/spec_dock/assets/install_root/`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/update.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/delete.py`
  - `tests/test_init_update.py`
  - `tests/cli_runtime/test_update.py`
  - `tests/cli_runtime/test_delete.py`
  - `discussions/20260531t133315z-interview-uninstall-command-scope.md`
  - `discussions/20260531t133616z-interview-uninstall-removal-boundary.md`
  - `discussions/20260531t134004z-interview-uninstall-user-owned-asset-boundary.md`
  - `discussions/20260531t134206z-interview-uninstall-command-surface.md`
  - `discussions/20260531t134650z-interview-uninstall-managed-asset-mismatch.md`
  - `discussions/20260531t135206z-interview-uninstall-empty-directory-cleanup.md`

## 対象ユーザー / 利用シナリオ
- 主な利用者:
  - SpecDock を使って product development を進めた後、repo から開発用 agent / skill / tooling を整理したい maintainer。
  - sub-agent / skill configuration が product behavior の一部になる repo の maintainer。
- 代表シナリオ:
  - 開発完了後、`./spec-dock/scripts/spec-dock uninstall` を実行し、SpecDock の agent / skill noise を target repo から取り除く。
  - 将来の開発再開や機能追加に備えて仕様履歴を残したまま uninstall する。
  - 使い捨て tool や今後の機能追加を想定しない repo で、仕様履歴を含めて SpecDock workspace を削除する。
  - repo-local runtime が削除された後や uninstall が途中失敗した後、外側の `spec-dock uninstall [path]` で再実行 / 復旧する。

## スコープ
- 必須:
  - installer CLI に `spec-dock uninstall [path]` を追加する。
  - repo-local runtime command に `./spec-dock/scripts/spec-dock uninstall` を追加し、installer CLI の uninstall implementation を呼び出す。
  - uninstall は標準で dry-run / plan 表示を提供し、実削除時は仕様履歴を残すか削除するかの明示選択を必須にする。
  - `--keep-specs` 相当の mode では、開発再開に必要な `spec-dock/initiatives/**` の仕様履歴を残す。
  - `--remove-specs` 相当の mode では、使い捨て repo / 完全 cleanup のために仕様履歴を削除対象に含める。
  - `.agents/skills/**`、`.codex/agents/**`、`.github/agents/**` のような agent / skill assets は uninstall の core removal target とし、content mismatch があっても削除する。
  - repo-root `spec` shortcut は、SpecDock runtime script へ向く symlink の場合に削除対象にする。
  - bootstrap-only / user-owned になり得る file は、現在の shipped asset と内容が完全一致する場合だけ自動削除し、差分がある場合は preserve + manual review にする。
  - CI / config / prompt / rule など product repo へ流用されやすい managed assets は、現在の shipped asset と内容が完全一致する場合だけ自動削除し、差分がある場合は preserve + manual review にする。
  - 削除対象 file の removal 後、既定の上限 root 内で空になった directory だけを bounded cleanup する。
  - dry-run / execution result で、削除予定 / 削除済み、preserve された manual review 対象、削除された empty directory を operator が追えるようにする。
  - 途中失敗時は、削除済み、未削除、preserved、failed を区別した summary と non-zero exit status を返す。
  - uninstall 後に再実行しても、存在しない managed artifact を no-op / already removed として扱い、安全に現状を report できる。
- 禁止:
  - Python package / global CLI / uvx cache / pip environment の削除を自動実行しない。
  - 仕様履歴を暗黙 default で削除しない。
  - bootstrap-only / user-owned になり得る差分あり file を自動削除しない。
  - CI / config / prompt / rule など product reuse 可能な差分あり file を自動削除しない。
  - preserved file、user-authored file、content mismatch で残した file がある directory を削除しない。
  - `.agents`、`.codex`、`.github`、`spec-dock` など既定の cleanup boundary root を越えて directory cleanup しない。
  - repo root、`.git`、target repo の親 directory、unknown unmanaged paths を削除しない。
- 対象外:
  - GitHub issue close / delete。
  - spec node 単体の local delete command の再設計。
  - package manager 別の environment uninstall automation。
  - legacy workspace の自動 migration。
  - product repo 固有の agent / skill / CI 設定の意味解釈。

## 境界
- 常に行う:
  - target repo 内の SpecDock-managed artifacts を inventory 化し、dry-run / execution result に removal plan を表示する。
  - agent / skill assets は primary objective の removal target として扱う。
  - specs handling は実削除時に explicit mode selection を要求する。
  - user edit protection と agent / skill noise removal の主従を明確にする。
  - uninstall 後も、必要なら installer CLI から再 install / update して開発再開できる前提を守る。
- 判断が必要:
  - 新しい managed asset category を追加した場合、それが agent / skill noise として content mismatch でも削除すべきものか、product reuse 可能 asset として mismatch preserve すべきものか。
  - 将来 package/environment uninstall guidance を docs に追加するか。
- 行わない:
  - repo 外の user environment を変更しない。
  - hidden / unknown / unmanaged files を convenience で削除しない。
  - dry-run だけで destructive operation を暗黙実行しない。

## 非交渉制約
- destructive operation は explicit mode と operator-visible plan を持つ。
- agent / skill noise removal は primary objective とし、差分あり agent / skill assets も削除対象にする。
- user-authored / product-reused file の誤削除を避けるため、bootstrap-only と product-reusable managed assets は content mismatch 時に preserve する。
- specs deletion は explicit choice とし、開発再開可能性を失う操作であることを operator に示す。
- uninstall は additive command として導入し、既存 `init` / `update` / `delete` / `sync` / `validate` の契約を壊さない。
- remote GitHub state は変更しない。

## 前提
- target repo は `spec-dock init` または `spec-dock update` により SpecDock assets が配置された managed repo である。
- current shipped assets と target files の content comparison が可能である。
- content comparison は、実行中の installer package が持つ shipped asset を基準にする。
- content comparison が判定不能な場合は、agent / skill core removal target を除いて preserve + manual review に倒す。
- repo-local runtime wrapper が消えた後でも、installer CLI `spec-dock uninstall [path]` から再実行できる。
- cleanup boundary roots は design で明示され、root を越えた directory cleanup は行わない。

## 削除対象分類

| path / category | 所有境界 | match required | mismatch 時の扱い | specs mode 依存 | report behavior |
|---|---|---:|---|---|---|
| `.agents/skills/**` | SpecDock-managed agent / skill | no | delete | none | removed / already removed |
| `.codex/agents/**` | SpecDock-managed agent | no | delete | none | removed / already removed |
| `.github/agents/**` | SpecDock-managed agent | no | delete | none | removed / already removed |
| `.agents/host-adapters/meta.json` | SpecDock-managed metadata | yes | preserve + manual review | none | preserved: content mismatch |
| `.codex/config.toml` | bootstrap-only / user-owned candidate | yes | preserve + manual review | none | preserved: content mismatch |
| `.codex/prompts/**` | product-reusable managed prompt | yes | preserve + manual review | none | preserved: content mismatch |
| `.codex/rules/**` | product-reusable managed rule | yes | preserve + manual review | none | preserved: content mismatch |
| `.codex/AGENTS.md` | product-reusable managed guidance | yes | preserve + manual review | none | preserved: content mismatch |
| `.github/workflows/**` | product-reusable managed CI | yes | preserve + manual review | none | preserved: content mismatch |
| `spec` repo-root shortcut | SpecDock-managed shortcut if symlink points to `spec-dock/scripts/spec-dock` | target match | preserve if not matching SpecDock shortcut | none | removed / preserved: not spec-dock shortcut |
| `spec-dock/docs/**`, `spec-dock/templates/**`, `spec-dock/system/**`, `spec-dock/scripts/**`, `spec-dock/spec-dock.version` | SpecDock runtime / scaffold | yes | preserve + manual review | none | removed or preserved reason |
| `spec-dock/active/**`, `spec-dock/.agent/**` | generated active / state | no | delete when removable | remove with workspace cleanup; keep only if preserving specs requires a coherent resume state by design | removed / skipped with reason |
| `spec-dock/initiatives/**` | specs / product development history | no | depends on explicit mode | `--keep-specs`: preserve; `--remove-specs`: delete | preserved: keep-specs / removed: remove-specs |
| unknown files under `.agents`, `.codex`, `.github`, `spec-dock` | unmanaged / user-authored candidate | no automatic ownership | preserve | none | preserved: unmanaged |

- agent / skill assets の mismatch deletion は、SpecDock-managed known paths に限る。unknown user-created agent / skill files は unmanaged として preserve する。
- product-reusable managed assets は、content match する場合だけ自動削除する。content mismatch、symlink / file type mismatch、permission / comparison error など判定不能な場合は preserve + manual review とする。
- repo-root `spec` は symlink target が SpecDock runtime shortcut と確認できる場合だけ削除する。通常 file、directory、または別 target の symlink は preserve + manual review とする。
- exact flag names and output wording は design phase で既存 CLI style に合わせて固定する。

## 受け入れ条件
- AC-001:
  - アクター:
    - maintainer
  - 前提:
    - SpecDock-managed agent / skill assets を持つ target repo がある。
  - 操作:
    - `./spec-dock/scripts/spec-dock uninstall` または `spec-dock uninstall <target>` で dry-run / plan 表示を実行する。
  - 期待結果:
    - 削除予定 files、preserve 予定 files、manual review 対象、empty directory cleanup plan が表示される。
    - dry-run では filesystem mutation が発生しない。
  - 観測点:
    - CLI output
    - filesystem assertions
- AC-002:
  - アクター:
    - maintainer
  - 前提:
    - target repo に `spec-dock/initiatives/**` の仕様履歴がある。
  - 操作:
    - 実削除を要求するが、specs handling mode を指定しない。
  - 期待結果:
    - command は fail-fast し、`--keep-specs` / `--remove-specs` 相当の明示選択を要求する。
    - 仕様履歴も agent / skill assets も削除されない。
  - 観測点:
    - exit status
    - CLI error
    - filesystem assertions
- AC-003:
  - アクター:
    - maintainer
  - 前提:
    - target repo に SpecDock-managed agent / skill assets と仕様履歴がある。
  - 操作:
    - `--keep-specs` 相当の mode で uninstall を実行する。
  - 期待結果:
    - agent / skill assets は content mismatch の有無にかかわらず削除される。
    - `spec-dock/initiatives/**` は残る。
    - repo-local runtime / scaffold / managed assets は、mode と category rule に従って削除または preserve される。
    - 空になった managed directories は boundary root 内で cleanup される。
  - 観測点:
    - filesystem assertions
    - CLI result summary
- AC-004:
  - アクター:
    - maintainer
  - 前提:
    - target repo に SpecDock-managed assets と仕様履歴がある。
  - 操作:
    - `--remove-specs` 相当の mode で uninstall を実行する。
  - 期待結果:
    - agent / skill assets と仕様履歴が削除対象になる。
    - deletion plan / result は仕様履歴削除を明示する。
    - cleanup boundary root を越えた directory deletion は行われない。
  - 観測点:
    - filesystem assertions
    - CLI result summary
- AC-005:
  - アクター:
    - maintainer
  - 前提:
    - `.codex/config.toml` など bootstrap-only file が shipped asset と完全一致する。
  - 操作:
    - uninstall を実行する。
  - 期待結果:
    - 当該 file は自動削除対象になる。
  - 観測点:
    - filesystem assertions
    - result summary
- AC-006:
  - アクター:
    - maintainer
  - 前提:
    - bootstrap-only file または product-reusable managed asset が shipped asset と異なる内容を持つ。
  - 操作:
    - uninstall を実行する。
  - 期待結果:
    - 当該 file は自動削除されず、manual review 対象として result に表示される。
  - 観測点:
    - filesystem assertions
    - result summary
- AC-007:
  - アクター:
    - maintainer
  - 前提:
    - known SpecDock-managed agent / skill path の file が shipped asset と異なる内容を持つ。
  - 操作:
    - uninstall を実行する。
  - 期待結果:
    - 当該 agent / skill asset は削除される。
    - unknown user-created agent / skill file は削除されず、unmanaged preserve として表示される。
  - 観測点:
    - filesystem assertions
    - result summary
- AC-008:
  - アクター:
    - maintainer
  - 前提:
    - repo-local runtime command が存在する。
  - 操作:
    - `./spec-dock/scripts/spec-dock uninstall` を実行する。
  - 期待結果:
    - repo-local command は installer `spec-dock uninstall <target>` implementation を呼び出す。
    - repo-local runtime が削除対象になっても、operator は installer CLI から再実行 / 復旧できる案内を得る。
  - 観測点:
    - runtime command test
    - subprocess args assertion
    - CLI output
- AC-009:
  - アクター:
    - maintainer
  - 前提:
    - uninstall 対象の一部が既に削除済み、または前回実行が途中で失敗している。
  - 操作:
    - installer CLI `spec-dock uninstall <target>` で再実行する。
  - 期待結果:
    - command は既に存在しない managed artifacts を no-op / already removed として扱う。
    - 削除済み、未削除、preserved、failed が区別された summary が返る。
    - 再実行できない destructive error にならない。
  - 観測点:
    - filesystem assertions
    - CLI result summary
    - exit status
- AC-010:
  - アクター:
    - maintainer
    - agent
  - 前提:
    - agent または自動化が uninstall の dry-run plan / apply result を機械的に解釈する必要がある。
  - 操作:
    - installer CLI または repo-local runtime command で `--json` を付けて uninstall を実行する。
  - 期待結果:
    - command は human-readable summary ではなく、machine-readable な JSON object を stdout に返す。
    - JSON は dry-run plan と apply result の両方を表現できる。
    - JSON は削除予定 / 削除済み / 既に削除済み / 保持 / 失敗 / 空 directory cleanup / guidance を agent が判別できる構造を持つ。
    - `--json` は runtime wrapper から installer CLI へ forwarding される。
  - 観測点:
    - JSON parse assertion
    - schema/key assertion
    - runtime subprocess args assertion
    - exit status

## 例外・エッジケース
- EC-001:
  - 条件:
    - target repo に `spec-dock/` が存在しない、または managed repo と判定できない。
  - 期待:
    - command は fail-fast し、`spec-dock init` / target path の確認を案内する。
  - 観測点:
    - exit status
    - CLI error
- EC-002:
  - 条件:
    - dry-run mode。
  - 期待:
    - CLI output は removal plan を表示するが、file / directory を変更しない。
  - 観測点:
    - filesystem snapshot comparison
- EC-003:
  - 条件:
    - preserved file がある directory が cleanup candidate になる。
  - 期待:
    - directory は削除されない。
  - 観測点:
    - filesystem assertions
- EC-004:
  - 条件:
    - cleanup traversal が `.agents`、`.codex`、`.github`、`spec-dock` などの boundary root に到達する。
  - 期待:
    - boundary root を越えて parent directory を削除しない。
  - 観測点:
    - filesystem assertions
- EC-005:
  - 条件:
    - uninstall 途中で repo-local runtime wrapper が削除済みになった後に再実行が必要になる。
  - 期待:
    - installer CLI `spec-dock uninstall <target>` から再実行できる。
  - 観測点:
    - installer CLI test / docs inspection
- EC-006:
  - 条件:
    - shipped asset との content comparison が file type mismatch、symlink、permission error、または読み取り失敗で判定不能になる。
  - 期待:
    - agent / skill core removal target を除き、対象 file は preserve + manual review として扱う。
    - result summary に判定不能理由が表示される。
  - 観測点:
    - filesystem assertions
    - CLI result summary
- EC-007:
  - 条件:
    - repo-root `spec` が通常 file、directory、または SpecDock runtime 以外を指す symlink である。
  - 期待:
    - command は `spec` を自動削除せず、manual review 対象として表示する。
  - 観測点:
    - filesystem assertions
    - CLI result summary
- EC-008:
  - 条件:
    - `--json` が指定された command で failed removals、inventory/comparison/apply error、または preserved manual-review item が発生する。
  - 期待:
    - command は parse 可能な JSON object を stdout に返し、status / summary / actions / guidance / errors によって agent が次アクションを判定できる。
    - human-readable 補足は JSON stdout に混在しない。
  - 観測点:
    - JSON parse assertion
    - stdout/stderr separation
    - exit status

## 入力→出力例
- EX-001:
  - 入力:
    - `./spec-dock/scripts/spec-dock uninstall --dry-run`
  - 出力:
    - removed candidates、preserved manual review、required specs mode guidance を含む plan。
- EX-002:
  - 入力:
    - `./spec-dock/scripts/spec-dock uninstall --apply --keep-specs`
  - 出力:
    - agent / skill assets removal、spec history preservation、bounded empty directory cleanup の result summary。
- EX-003:
  - 入力:
    - `spec-dock uninstall /path/to/repo --apply --remove-specs`
  - 出力:
    - target repo の SpecDock artifacts と specs removal の result summary。
- EX-004:
  - 入力:
    - `spec-dock uninstall /path/to/repo --json`
  - 出力:
    - agent が parse 可能な dry-run plan JSON。
- EX-005:
  - 入力:
    - `spec-dock uninstall /path/to/repo --apply --keep-specs --json`
  - 出力:
    - agent が parse 可能な apply result JSON。

## 用語（ドメイン語彙）
- repo-local uninstall:
  - target repo 内に導入された SpecDock-managed artifacts を取り外す操作。Python package / global CLI の削除は含まない。
- repo-root shortcut:
  - target repo root の `spec` symlink。SpecDock runtime script へ向く場合のみ SpecDock-managed shortcut として扱う。
- specs:
  - `spec-dock/initiatives/**` に蓄積された仕様履歴と開発再開のための canonical project history。
- agent / skill assets:
  - `.agents/skills/**`、`.codex/agents/**`、`.github/agents/**` など、agent discovery / sub-agent 稼働に影響する開発用 assets。
- product-reusable assets:
  - `.github/workflows/ci.yml`、`.codex/prompts/**`、`.codex/rules/**` など、SpecDock 由来でも product repo 側で編集・流用され得る assets。
- bootstrap-only / user-owned file:
  - installer が初回作成するが、以後の update では user edit を尊重する file。現時点の代表例は `.codex/config.toml`。
- bounded empty-dir cleanup:
  - 削除対象 file の親 directory から上に向かって空 directory を削除するが、既定の boundary root を越えない cleanup。

## 未確定事項
- none.

## 解決済み質問
- Q-001:
  - 質問:
    - `--apply` / `--yes` / `--keep-specs` / `--remove-specs` などの具体的な flag 名をどうするか。
  - 回答:
    - design phase で `--apply`、`--keep-specs`、`--remove-specs`、`--json` として固定した。
  - 影響範囲:
    - CLI help
    - tests
    - docs
