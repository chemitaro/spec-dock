---
種別: ADR（Architecture Decision Record）
ID: "20261014t072234z-adr"
タイトル: "Project skill projections for Codex and Claude Code"
状態: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-10-14"
親: ["iss-00418"]
authority: "accepted"
accepted_authority: "accepted ADR"
accepted_at: "2026-10-14"
accepted_by: "iwasawayuuta"
mirror_eligible: true
derived_from: ["20261014t071357z-research", "20261014t071419z--chatgpt-strict-claude-skill-distribution-analysis.md"]
reflected_to: ["../requirement.md", "../design.md", "../plan.md"]
---

# 20261014t072234z-adr Project skill projections for Codex and Claude Code

architecture / contract / migration の判断候補を記録します。明示的に `accepted` となった ADR だけが durable authority になり得ます。original は `artifacts/` に残り、legacy `discussions/` も accepted ADR の mirror source として扱えます。

## Context

- 判断が必要な背景と制約:
  - `spec-dock installation init/update` は、同梱スキル `spec-dock`・`spec-dock-grill-with-docs` を対象 worktree の `.agents/skills/<name>/` にだけ配置する。
  - 2026-10-14 時点の公式文書では、Codex のリポジトリ内探索先は `.agents/skills`（cwd から repository root までの各階層）である。Claude Code のプロジェクト探索先は `.claude/skills`（起動ディレクトリから repository root まで。linked worktree では worktree root で停止）であり、`.agents/skills` を読まない。そのため、SpecDock を導入しても Claude Code からはスキルが見えない（この dogfooding repo でも観測済み）。
  - epic-00074（draft）の E-RQ-003 は「shared skills は `.agents/skills/` に集約し、host 固有ディレクトリへ重複配置しない」と定めた。同 Epic は Claude Code などの追加 host を OUT OF SCOPE としていた。
  - accepted ADR `20260831t005139z-adr` の Decision 6 は、managed skill を `.agents/skills/spec-dock` と `.agents/skills/spec-dock-grill-with-docs` の2つの固定 slot に限定し、`.agents/skills` 親全体を所有しないと定めた。
  - 現行の静的インストール契約（Issue 413、AC-413-37）は、明示した1つの worktree の既知の静的資産だけを、ファイル単位のインベントリ（path・source・sha256・mode・known_old_sha256）で管理する。未知の改変は手動マージを要求して fail-closed で停止する。
  - 協業者、Claude Code on the web、CI 上のエージェントなどは、リポジトリにコミットされた内容しか参照できない。
  - スキル本文は、外部 CLI の使い方に加えて、worktree ごとの静的スキャフォールド（`spec-dock/docs`・`templates`・`system`）のレイアウトにも依存している。

## Decision

2026-10-14 に、product owner（iwasawayuuta）が Option A1 を受理した。以下を決定とする。

1. **正本は一つにする。** スキルの著作・保守上の正本は `src/spec_dock/assets/install_root/.agents/skills/<name>/` だけとする。provider 側に `.claude` 用のコピーは作らない。
2. **ホストのプロジェクト探索先へ投影する。** 同じ正本を、次の2つの配置先へ同じバイト列の通常ファイルとして投影する。
   - `.agents/skills/<name>/`（Codex ほか、`.agents/skills` を読むホスト）
   - `.claude/skills/<name>/`（Claude Code）
3. **管理単位は固定 slot 内のインベントリファイルだけにする。** 管理対象は次の4つの固定 slot 内で、インベントリに列挙したファイルだけとする。
   - `.agents/skills/spec-dock`
   - `.agents/skills/spec-dock-grill-with-docs`
   - `.claude/skills/spec-dock`
   - `.claude/skills/spec-dock-grill-with-docs`

   `.agents/`・`.agents/skills/`・`.claude/`・`.claude/skills/` は共有の親とし、所有も削除もしない。`.claude/settings.json`、`.claude/settings.local.json`、他のスキル、hooks、agents などのホスト設定は管理しない。
4. **既存の静的インストール契約をそのまま使う。** 両投影とも Issue 413 のファイル単位インベントリで管理し、init / update / uninstall / show の既存の fail-closed 契約、バックアップ要求、partial 報告に従う。`known_old_sha256` は配置先ごとの配布履歴とし、新設の `.claude` 側は空から始める。本 ADR は slot の所有証明方式（ADR `20260831t005139z-adr` が想定した owner marker など）を再決定しない。
5. **スキル本文はホスト中立の1種類にする。** 両投影の内容は同一に保ち、ホスト別に分岐させない。ホスト固有の起動制御は、同じパッケージ内に共存させる（Codex 用の `agents/openai.yaml`、Claude Code 用の frontmatter `disable-model-invocation`）。同梱 helper は、読み込まれたスキルディレクトリを基準に解決する。シェルの現在ディレクトリや他の探索先、`$HOME` から探して代用しない。
6. **採らない方式**: グローバル導入（`$HOME` への配置）、Claude Code プラグイン、symlink による投影、ホスト検出による配布先の切り替え、ホスト設定の自動編集。
7. **改訂する過去の判断**（部分的な supersede）:
   - epic-00074 E-RQ-003 と、それに対応する happy path・境界の記述のうち、「host 固有ディレクトリへ重複配置しない」という配置制約。単一の正本、拡張可能性、未知の利用者ファイルの保持、runtime protocol をホスト側へ再実装しない境界は維持する。過去の OUT OF SCOPE は、当時の判断として書き換えない。
   - ADR `20260831t005139z-adr` Decision 6 のうち、managed skill の slot を `.agents/skills` 配下の2つに限定する記述。上記3の4 slot へ拡張する。共有の親を所有しないこと、無関係なスキルを常に保持することは維持する。

## Options

- 検討した選択肢と trade-off:
  - **A1（採択候補）: プロジェクトへの二重投影（コピー）**
    - 両ホストの標準探索先に置ける。
    - 両投影と静的スキャフォールドを、同じ update・同じ PR で扱える。
    - リポジトリにコミットすれば、協業者とクラウドのエージェントにも届く。
    - 既存のインベントリ機構（ハッシュ判定、バックアップ、partial 報告）をそのまま使える。
    - Windows の `core.symlinks=false` でも配置が壊れない。
  - **A2: プロジェクトへの symlink 投影**
    - Claude Code は skill エントリの symlink を公式にサポートする。
    - しかし、インストーラの「親チェーンとファイルの symlink を拒否する」設計と衝突し、リンクの inventory・backup・uninstall 契約を新設する必要がある。
    - `core.symlinks=false` の clone では、リンクが小さな通常ファイルになって探索が壊れる。
  - **B: グローバル導入（`~/.agents/skills`・`~/.claude/skills`）**
    - `$HOME` を書き換える別契約が必要になる。wheel には post-install hook がないため、明示コマンドと更新のたびの再実行が要る。
    - 複数のリポジトリ・ブランチが一つの版を共有するため、worktree の静的資産と版がずれやすい。
    - Claude Code では personal のスキルが project のスキルより優先されるため、プロジェクト側の版を隠す危険がある。
    - リポジトリしか見えない協業者・クラウドには届かない。
  - **C: Claude Code プラグイン**
    - CLI と別の版管理経路が増え、呼び出し名が `/plugin:skill` に名前空間化される。
    - 協業者ごとにインストールが必要で、クラウドセッションはローカル設定のプラグインを読まない。
  - **D: 製品を変えず、利用者側で回避する（`--add-dir`、手動 symlink、`CLAUDE.md` から参照など）**
    - 製品としての問題が残り、手動同期のずれが起きる（ローカルの `~/.claude/skills` 手動同期で、既に取りこぼしを観測している）。

## Consequences

- 影響、移行、または見直し条件:
  - **利用者への影響**:
    - 既存利用者は、外部パッケージを更新した後、対象 worktree で通常の `installation update --backup-dir ABS --yes` を実行すると、`.claude` 側を `installation.create` として受け取る。
    - init は、管理対象の4 slot 内に既存ファイルがあれば、内容が同じでも拒否する。
  - **所有権の限界**: 同じパスに同じバイト列があると、利用者の手動コピーか SpecDock の配布物かを区別できない。update で current として受け入れたファイルは、uninstall で削除対象になる。
  - **一致の保証範囲**: 両投影の一致は、パッケージ生成時と update 成功時に保証する。update はファイルごとの順次公開なので、途中で失敗すると片方の投影だけが新しくなり得る。その場合は既存の partial 報告と、新しい明示操作で収束させる。
  - **ホスト側の挙動はインストーラの保証外**:
    - Claude Code は同名の personal スキルを project より優先する。
    - v2.1.277 以降の linked worktree は、ルートに `.claude/skills` がなければ main checkout のスキルを読む。
    - Desktop app から開始した worktree セッションは、main checkout 側の設定を読む。

    そのため、`installation show` が current でも、実際のセッションがそのコピーを選ぶとは限らない。uninstall 後に空の `.claude/skills` が残ると、main checkout へのフォールバックも抑止される。uninstall の保証は「対象 worktree にある、自ら管理するファイルの除去」までとする。
  - **保守コスト**:
    - スキルのファイルを変更すると、インベントリの2エントリ（`.agents` 側と `.claude` 側）の sha256 を同時に更新する。
    - `known_old_sha256` は配置先ごとに管理する。
    - 投影の対応関係はテストで固定する。
  - **撤退条件と手順**: Claude Code が `.agents/skills` を正式に読むようになった場合に、`.claude` 投影の廃止を検討する。
    - 前提として、サポートする最小バージョンで次を確認する: `.agents` からの発見、grill の明示起動制御、helper の位置解決、移行期間中の重複ロードと優先順位。
    - 撤退の手順:
      1. 廃止条件と移行期間を文書化する。
      2. `.claude` の各管理ファイルを current inventory から retired inventory へ移し、そのパスに実際に配布したハッシュを登録する。
      3. `package_retired_assets()` の allowlist を、`.claude/skills/spec-dock/` と `.claude/skills/spec-dock-grill-with-docs/` の固定 slot に限って拡張する。
      4. 通常の `installation update` で、バックアップと `--yes` の下で既知のファイルだけを除去する。未知の改変、利用者設定、共有の親は保持する。

      インベントリからエントリを消すだけでは撤退にならない。既存環境のファイルが管理外のまま残る。
  - **その他の見直し条件**:
    - スキルが worktree の静的スキャフォールドから独立し、複数リポジトリで一つの版を共有してよくなった場合は、B・C を再評価する。
    - symlink を確実に再現できる環境だけが対象になり、リンクの安全な lifecycle 契約が整い、コピーの負担が実際に問題になった場合は、A2 を再評価する。
    - 第3のホストが既存の探索先を共有しない場合は、同じ正本から投影先を追加できる。その追加は、新しい判断として記録する。

## References

- 根拠と反映先:
  - 調査: `20261014t071357z-research-claude-code-skill-discovery-investigation.md`（同 Issue の Artifact）
  - 外部分析: `20261014t071419z--chatgpt-strict-claude-skill-distribution-analysis.md`（同 Issue の Artifact。ChatGPT Strict、`main@0e7dc868`）
  - 改訂対象: `spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00074-multi-host-agent-and-config-asset-expansion/requirement.md`（E-RQ-003）
  - 部分改訂対象: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/artifacts/20260831t005139z-adr-disposable-provider-roots-and-fixed-skill-slots.md`（Decision 6）
  - 維持する契約: `docs/issue-plans/iss-00413-external-cli-state/requirement.md`（AC-413-37）
  - 公式文書（2026-10-14 確認）: https://code.claude.com/docs/en/skills 、https://code.claude.com/docs/en/worktrees 、https://code.claude.com/docs/en/plugins 、https://learn.chatgpt.com/docs/build-skills
  - 反映先: 同 Issue の `requirement.md`・`design.md`・`plan.md`
