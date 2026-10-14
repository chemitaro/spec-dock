# SpecDock 共通CLI刷新後の調査・ローカル照合結果

調査日: 2026-10-06 JST。調査・提案のみ。製品source、正本文書、metadata、GitHub設定は変更していない。

## 結論

刷新後の修正候補は7件ある。主に現在の利用者へ見える文書・診断・補完の不整合であり、刷新全体のやり直しを要する根拠は確認していない。ChatGPTは7件をP2に分類した。今回の範囲でP0/P1は確定していないが、網羅的な無欠陥保証ではない。

`./spec` は現在の新規installationが自動生成するものではない。このrepositoryが追跡している既存の互換ショートカットであり、廃止候補にはできる。外部consoleへ委譲する配布shimとは別に判断する。通常の入口は `spec-dock` に揃える方針が適切。

共通skillのglobal化には利点がある。推奨は、当面のproject-local配置を維持しながら、将来の「globalな共通操作skill＋localなproject規則・仕様参照」を独立して検証すること。現在の2 skillをそのままglobalへ移すだけでは、版整合・同名衝突・Grill helperのpath問題が残る。

## 外部分析の来歴

- 使用skill: `chatgpt-use-strict`。Oracle 0.21.4、browser engine。
- 指定: `gpt-6-pro` / `pro`。OracleのUI観測: model `Latest`、effort `Pro`、双方verified。指定名と実際のUIラベルを区別する。
- session: `specdock-cli-refresh-audit-resumed`。約31分、exit 0、status completed。
- repository: `chemitaro/spec-dock`、branch `main`。
- full SHA: `0e7dc86841cb48d011270a1a2165cb6406ac0cea`。
- wrapperのlocal/live-upstream gate通過。ChatGPTの回答はGitHub connectorによるbranch-tip完全一致を明記。connector検証はskillの仕様上、回答内の申告でありwrapperからの機械的attestationではない。
- [ChatGPT回答原文](./chatgpt-report.md)／[会話](https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6ac46387-8628-83ee-9104-2bb0e6874e14)。原文はadvisoryであり、以下にローカル照合と未確認の境界を示す。
- 前回の添付送信前timeoutは英語UIへの復旧後に再開した。元の依頼の重複送信は行っていない。準備記録は `recovery.md`。

## 確認した修正候補

| ID | 問題と影響 | 根拠 | ローカル照合・最小対応 |
|---|---|---|---|
| SD-OPS-001 | 旧 `meta.json` を見つけた際、一律に `.meta.json` へrenameする案内が出る。既存の現行metadataとの同居時には手作業の上書きを誘発し得る。CLI自身が上書きする不具合ではない。 | [fs_repo.py:338](/Volumes/990p2t/workspace/tools/spec-dock/src/spec_dock/runtime/infra/fs_repo.py:338)、[現行の呼出元:126](/Volumes/990p2t/workspace/tools/spec-dock/src/spec_dock/runtime/application/direct_scope_publish.py:126) | 現行create/import経路からreaderを呼ぶことを確認。保全・内容比較・既存file確認を先に促す診断へ直す。未実施: 同居fixtureでの公開CLI再現。 |
| SD-OPS-002 | READMEのScope作成例が `--json` と必要な `--yes` を併記していない。そのままでは確認不足で失敗する。 | [README:21](/Volumes/990p2t/workspace/tools/spec-dock/README.md:21)、[確認guard:56](/Volumes/990p2t/workspace/tools/spec-dock/src/spec_dock/runtime/application/direct_scope_publish.py:56) | parserで `non_interactive=true, yes=false` を確認。guardが `CONFIRMATION_REQUIRED` を返す。許可済み作成例に `--yes` を追加する。実GitHub作成はしていない。 |
| SD-OPS-003 | 通常TARGETの説明にGitHub番号・URLを含めるが、通常selectorとimport refの文法は別。root文書の裸番号import例にもrepo指定がない。 | [CLI参照:3](/Volumes/990p2t/workspace/tools/spec-dock/src/spec_dock/assets/spec_dock/docs/reference_cli.md:3)、[GitHub説明:13](/Volumes/990p2t/workspace/tools/spec-dock/docs/github-issue-integration.md:13)、[selectors.py](/Volumes/990p2t/workspace/tools/spec-dock/src/spec_dock/runtime/domain/selectors.py) | 通常selectorのURL拒否、repo指定なし裸番号import拒否、repo指定付きimport受理を実関数で確認。文書を現在の契約に揃える。 |
| SD-OPS-004 | 「現行」Sync文書に生成物再構築、`--source cache`、journal診断の旧説明が残る。 | [sync-aggregation.md:3](/Volumes/990p2t/workspace/tools/spec-dock/docs/sync-aggregation.md:3) | parserでcache退役エラーを確認。現在のSyncは観測であり生成物保存ではない。providerの現行参照へ統一する。 |
| SD-OPS-005 | AGENTSに2026-10-03時点の「main等未移行・merge pending」が現行入口として残る。 | [AGENTS:10](/Volumes/990p2t/workspace/tools/spec-dock/AGENTS.md:10) | 現在HEADはPR #414のmerge commit、consumerのwriter宣言も新protocol。日時付き履歴と現状を分ける。他worktreeの実環境移行は未認定。 |
| SD-OPS-006 | Bash/Zsh/Fish補完が全leafに全共通optionを出し、実際には拒否される `--yes` や `--lock-timeout` を提示する。 | [候補生成:257](/Volumes/990p2t/workspace/tools/spec-dock/src/spec_dock/runtime/cli/options.py:257)、[parser制限:458](/Volumes/990p2t/workspace/tools/spec-dock/src/spec_dock/runtime/cli/options.py:458) | 3 shellの生成文字列でscope listへの両option提示を確認。scope list --yes、active show --lock-timeoutはparserがexit 2。leafごとに候補を絞る。実shell操作試験は未実施。 |
| SD-OPS-007 | GitHub Aboutが `uvx`、`.spec-dock/`、runtime不要・コピーfileのみという旧紹介のまま。 | [repository](https://github.com/chemitaro/spec-dock) のdescription | `gh api repos/chemitaro/spec-dock`で再確認。commit外のGitHub metadataなので、README変更とは別に更新する必要がある。今回は未変更。 |

補足: `docs/github-issue-integration.md` の「固定外部エンジン」も現行説明へ直す対象。既存local backendの互換読取・lifecycleが残ることと、新規local Scopeを作れることは別である。旧語句の全件置換はしない。

配布資産を修正する際は、providerを先に変更し、`static-inventory.json` の現在hash・既知旧hashを適切に更新する。fresh consumer確認と対象worktreeへの静的更新は別々に検証する。

## `./spec` と他のリンク

| 対象 | 現在の位置づけ | 推奨 |
|---|---|---|
| `spec-dock` | 外部installed console | 標準入口に統一する。 |
| `./spec` | mode 120000で追跡された `spec-dock/scripts/spec-dock` へのlink | 現行inventoryのcurrent/retiredいずれにもなく、新規生成されない。既存利用の互換方針を決め、必要ならこのrepoで段階廃止する。 |
| `./spec-dock/scripts/spec-dock` | PATHのconsoleへ委譲する現在の配布shim | rulesの案内・互換テストが利用している。root linkと同時に無条件削除しない。 |
| `spec-dock/active/` | このworktreeに残るignoredな旧投影 | 現在の選択正本ではない。確認済みの残存物として扱い、自動一括削除しない。 |
| Scopeの `artifacts/rules.md` 等 | 現在のScope作成でも生成する文書規則link | 現役。共通CLI化を理由に削除しない。 |

根拠: [static inventory loader](/Volumes/990p2t/workspace/tools/spec-dock/src/spec_dock/runtime/infra/static_assets.py:30)、[導入実装](/Volumes/990p2t/workspace/tools/spec-dock/src/spec_dock/runtime/application/direct_installation.py:56)、[既存linkの互換テスト](/Volumes/990p2t/workspace/tools/spec-dock/tests/integration/test_issue413_shim.py:136)、[rulesのshim案内](/Volumes/990p2t/workspace/tools/spec-dock/src/spec_dock/assets/spec_dock/docs/rules/issue/artifacts.md:27)。

## skill配置の判断

| 案 | 利点 | 主な課題 | 評価 |
|---|---|---|---|
| project-local | チーム・clone単位で同じ手順を共有できる | 共通内容の更新を各worktreeへ適用する必要がある。PATH上のCLI版まで固定されるわけではない | 現行方式として当面維持 |
| user-globalへ全面移行 | 複数projectの共通手順を一箇所で更新できる | 未導入者、CI、旧CLIとの互換性、同名local skill、projectごとの規則の扱い | 単純コピー移行は非推奨 |
| global共通skill＋local project情報 | 共通操作と各projectの規則・仕様を分離できる | 版互換の確認、導入案内、helper位置と対象rootの分離が必要 | 将来案の第一候補 |

Codex公式はuser scopeの `$HOME/.agents/skills` とrepo scopeをサポートし、同名skillは統合されず両方が候補になり得ると説明している。local優先を前提に二重配置しない。再利用skillの配布にはpluginも公式に案内されているが、SpecDockでの採用は未決である。[公式Build skills](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)

現在の通常skillはSKILL.mdのみで、global入口の限定実験に向く。Grillはrepo相対helper pathを使うため、実際に読み込んだskill directoryからhelperを解決し、対象repo rootを独立に固定する変更が必要になる。外部 `grilling` / `domain-modeling` の利用可能性や明示起動policyも維持する。

現行installerは一worktreeの静的配置を管理する。global skill導入機能はない。`.agents` を共通directoryへのsymlinkに置き換えて既存updateを使う方法は、installerのsymlink拒否境界と衝突する。

## 現在も維持すべき運用

1. 外部CLIの所在・版と、操作対象の絶対worktree rootを確認する。
2. package更新、worktreeの静的資産更新、writer宣言の移行を別操作として扱う。
3. 新規導入はinit。資産が既にあるcloneはinstallation showで確認してから必要なupdateを行う。
4. 直接対象はactive showで観測する。新しい対象の取得はwork start、閲覧だけならscope showと文書読取で足りる。
5. work finishとtest/review/commit/push/PR/mergeを別の完了証拠として扱う。
6. Syncは観測。旧dashboard・active投影が更新されることを期待しない。
7. 履歴資料は日時と当時のSHAを保ち、現在の操作入口へ旧手順を混ぜない。

## 推奨する後続作業

1. 現行の復旧案内・README実行例・selector説明・Sync文書を修正する（001〜004）。
2. AGENTSの時点整理とGitHub About更新を行う（005・007）。
3. 補完候補とparserの受付条件を揃える（006）。
4. root `./spec` と配布shimの互換・廃止方針を別々に決める。
5. 非到達の旧presentation等を関数単位で調査し、必要なreaderを巻き込まず整理する。
6. 配布済みskillのroot/nested CWD動作を確認し、通常skillからglobal＋local案を小さく検証する。

Issue/PRは未作成。上記は実装承認済みの計画ではなく、調査からの提案である。

## 実施した確認と限界

- 開始・終了時のmain/HEAD/clean statusを確認。Git変更・commit・pushなし。
- current inventoryの85資産はconsumerとhash一致。workspace.jsonはbytesの整形差があるが、schema=3 / writer=specdock.worktree-writer/v1で一致する。これは初期配置専用の宣言で、通常の静的同期差分と混同しない。
- 通常scope selector、import ref、retired cache、非適用option、3 shellの補完生成を現行provider関数で照合。
- GitHub Aboutをread-only APIで再確認。
- 限定テスト: `uv run pytest tests/integration/test_issue413_assets.py::test_init_places_only_static_assets_and_a_new_declaration_in_the_explicit_worktree tests/integration/test_issue413_artifact_skill.py -q` → **3 passed in 2.71s**。uvは開発用.venvを整備した。ユーザー共通installed consoleの更新ではない。
- full suite、新規wheelの配布検証、live GitHub create/close、全linked worktree移行、実hostでのGrill一連操作は未実施。
- ChatGPT原文の他agent providerに関する説明・uvの運用説明は今回すべてを独立再検証していない。本照合報告の推奨は、ローカル実装と上記Codex公式資料で確認できた範囲に限定する。

この報告はGit-ignored Workbenchの調査成果物で、SpecDockのcanonical Artifactや承認済み仕様ではない。
