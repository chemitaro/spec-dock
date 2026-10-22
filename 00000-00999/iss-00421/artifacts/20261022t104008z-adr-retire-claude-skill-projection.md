---
種別: ADR（Architecture Decision Record）
ID: "20261022t104008z-adr"
タイトル: "Retire the Claude Code skill projection"
状態: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-10-22"
親: ["iss-00421"]
authority: "accepted"
accepted_authority: "accepted ADR"
accepted_at: "2026-10-22"
accepted_by: "iwasawayuuta"
mirror_eligible: true
derived_from: []
reflected_to: ["../requirement.md", "../design.md", "../plan.md"]
---

# 20261022t104008z-adr Retire the Claude Code skill projection

architecture / contract / migration の判断候補を記録します。明示的に `accepted` となった ADR だけが durable authority になり得ます。original は `artifacts/` に残り、legacy `discussions/` も accepted ADR の mirror source として扱えます。

## Context

- 判断が必要な背景と制約:
  - accepted ADR `20261014t072234z-adr`（iss-00418）の Decision 2・3 により、`installation init/update` は同梱スキル `spec-dock`・`spec-dock-grill-with-docs` を `.agents/skills/<name>/` と `.claude/skills/<name>/` の両方へ、同じバイト列の通常ファイルとして投影している。管理 slot は4つ（`.agents` 側2つ、`.claude` 側2つ）である。
  - Claude Code は `.agents/skills` を読まない。そのため `.claude` 側の投影は、Claude Code にスキルを見せるためだけに存在する。
  - 2026-10-22、product owner（iwasawayuuta）が次のとおり決定した（原文）。
    - 「スペックドック側を修正して、…クロードコード側にスキルを配置しないようにする。共通スキルのみを作成するようにする。で、このスペックドックの共通、クロードコードへのスキルの取り込みは、このクロードコード側のフック及びスキル側に、委ねるようにするのが良い」
    - 「スペックドックは個人用です。シンプルな記述で良いです。」
  - Claude Code 側の取り込みは、ユーザーレベルの SessionStart フックと手動同期スキルが同じスクリプトで行う（`~/.claude` リポジトリで別に実装する）。契約は次のとおり。
    - リポジトリルートの `.agents/skills/<name>/` ごとに、`.claude/skills/<name>` → `../../.agents/skills/<name>` の相対シンボリックリンクを作る。リンクは Git で管理する（コミットは利用者かエージェントが行う）。
    - 正しいリンクがあれば何もしない。ファイルを含む実体ディレクトリには触れない。ファイルを1つも含まない実体ディレクトリは、リンクに置き換える。リンク先が消えた管理リンクは削除する。
    - `git config claude.linkAgentsSkills false` でリポジトリ単位に無効化できる。
  - ADR `20261014t072234z-adr` の「撤退条件と手順」は、インベントリからエントリを消すだけでは撤退にならず、retired inventory と retired allowlist の拡張で既知のファイルを除去する手順を定めている。
  - 現行の installer は、親チェーンに symlink があると fail-closed で停止する（`verify_existing_parent`）。そのため、`.claude/skills/<slot>` をリンクにした worktree では、`.claude` 側の管理ファイルを検査する update・uninstall が停止する。

## Decision

2026-10-22 に、product owner（iwasawayuuta）がこの ADR の accepted 化を承認した（Orca coordinator 経由の確認）。以下を決定とする。

1. **`.claude` へのスキル投影をやめる。** `installation init/update` は、同梱スキルを `.agents/skills/<name>/` にだけ配置する。`.claude/` 配下には何も作らない。管理 slot は `.agents/skills/spec-dock` と `.agents/skills/spec-dock-grill-with-docs` の2つに戻る。
2. **Claude Code への取り込みは Claude Code 側に委ねる。** spec-dock は `.claude/skills/<name>` のリンクを作成・検査・削除しない。取り込みは Context に記した Claude Code 側の契約で行う。
3. **既存の `.claude` 側のコピーは、ADR `20261014t072234z-adr` の撤退手順で退役させる。**
   - `.claude` 側の4エントリを current inventory から retired inventory へ移し、各パスに実際に配布したハッシュを登録する。
   - `package_retired_assets()` の allowlist を、`.claude/skills/spec-dock/` と `.claude/skills/spec-dock-grill-with-docs/` の2つの固定 slot に限って拡張する。
   - 通常の `installation update --backup-dir ABS --yes`（と uninstall）で、既知のハッシュのファイルだけをバックアップしてから除去する。未知の改変は従来どおり手動マージを求めて停止する。
   - 共有の親（`.claude/`、`.claude/skills/`）、slot ディレクトリ、利用者のファイルと設定は保持する。除去後に空のディレクトリが残ってよい（Claude Code 側がリンクに置き換える）。
4. **リンク経由の slot は管理外とする。** 退役対象の slot について、`.claude`、`.claude/skills`、`.claude/skills/<slot>` のいずれかがシンボリックリンク（リンク先がないものを含む）であれば、その slot は spec-dock の管理外とする。init / update / show / uninstall はそのリンクをたどらず、リンクとリンク先を変更・削除せず、そのリンクを理由に停止しない。
   - それ以外の異常な形（通常ファイルの `.claude`、実体の slot 内にあるファイル単位の symlink、hard link、特殊ファイル）は、従来どおり fail-closed で停止する。
5. **改訂する過去の判断**（部分的な supersede）:
   - ADR `20261014t072234z-adr` の Decision 2（`.claude/skills/<name>/` への投影）と Decision 3（4 slot の管理）。管理対象は `.agents` 側の2 slot に戻す。
   - 同 ADR の Decision 7 のうち、ADR `20260831t005139z-adr` Decision 6 の slot を4つへ拡張した部分。同 Decision 6 の「`.agents/skills` の2 slot に限定する」記述に戻る。
   - 同 ADR の Decision 1（正本は一つ）、Decision 4（インベントリ契約）、Decision 5（ホスト中立のスキル本文）は維持する。Decision 6 の「symlink による投影を採らない」も、installer の方針として維持する（リンクは installer ではなく Claude Code 側が作る）。

## Options

- 検討した選択肢と trade-off:
  - **A: 現状維持（`.claude` へのコピー）**
    - 同じ内容を2か所に持ち、ハッシュとインベントリを二重に保守する。
    - product owner がやめると決定した。
  - **B: spec-dock 自身が `.claude/skills/<name>` のリンクを作る**
    - installer にリンクの inventory・backup・uninstall 契約を新設する必要があり、親チェーンの symlink を拒否する現行設計と衝突する。
    - product owner は、取り込みを Claude Code 側に委ねると決定した。
  - **C（採択）: `.claude` 投影を退役させ、取り込みを Claude Code 側のフックとスキルに委ねる**
    - spec-dock は `.agents` 側だけを管理する。Claude Code 側の契約は、リポジトリごとのスキルを一般的に扱える。
  - **D: インベントリから `.claude` のエントリを消すだけ**
    - 既存環境のコピーが管理外のまま残り、Claude Code 側のスクリプトもファイル入りのディレクトリには触れないため、リンクに置き換わらない。撤退として不十分である。

## Consequences

- 影響、移行、または見直し条件:
  - **移行**: `.claude` 側のコピーを持つ worktree は、外部パッケージを更新した後、通常の `installation update --backup-dir ABS --yes` を実行すると、既知のコピーがバックアップされてから除去される。空になったディレクトリは、Claude Code 側のスクリプトがリンクに置き換える。
  - **順序の自由**: 先にリンクを作った worktree でも update は失敗しない（Decision 4）。リンクを作る前に update した worktree では、空のディレクトリが残る。
  - **Claude Code 側がない環境**: Claude Code 側のフックやスキルがなければ、Claude Code から SpecDock のスキルは見えない。個人用のため許容する。
  - **リンクの再現性**: リンクを Git にコミットしても、`core.symlinks=false` の clone では通常ファイルになり、探索が壊れる。個人用のため許容する。
  - **show の表示**: `installation show` は current inventory だけを表示するため、`.claude` 側を表示しない。retired のファイルが残っていても表示しない（既存の retired 資産と同じ）。
  - **uninstall**: `.agents` 側の管理ファイルを除去する。`.claude` 側のリンクは残り、リンク先がなくなる。その削除は Claude Code 側のスクリプトが行う。
  - **旧 CLI**: `.claude` 投影を含む版（main の `99f304c8`〜`4d25a8b4` からビルドしたもの。2026-10-22 時点でユーザーのツール環境にある 0.2.4 は `4d25a8b4` のビルド）は、リンク入りの worktree で `.claude` 側を `unsafe` と表示し、update を親チェーンの symlink で停止する。パッケージを更新してから使う。
  - **見直し条件**: Claude Code が `.agents/skills` を正式に読むようになった場合、Claude Code 側の取り込み自体が不要になる。spec-dock 側の変更は要らない。

## References

- 根拠と反映先:
  - 改訂対象: `../../iss-00418-claude-code-skill-discovery/artifacts/20261014t072234z-adr-project-skill-projections-for-codex-and-claude-code.md`（Decision 2・3・7）
  - 間接的な改訂対象: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/artifacts/20260831t005139z-adr-disposable-provider-roots-and-fixed-skill-slots.md`（Decision 6。2 slot の限定に戻る）
  - 根拠: 2026-10-22 の product owner の決定（Context に原文を記録）
  - 反映先: 同 Issue の `requirement.md`・`design.md`・`plan.md`、`AGENTS.md`、`README.md`、同梱の `spec-dock` SKILL.md、`src/spec_dock/assets/spec_dock/docs/authoring/overview.md`
