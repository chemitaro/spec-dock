---

種別: 実装補助文書（Issue）
ID: "iss-00359"
タイトル: "Issue 359 Implementation Companion"
関連GitHub: ["#359"]
状態: "draft"
作成者: "ChatGPT-use-strict / main orchestrator"
最終更新: "2026-08-12"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00356", "init-local-00003"]
---
# Issue 359 Implementation Companion

## 最初に読むもの

1. `requirement.md` — scope、受け入れ条件、対象外の正本
2. `design.md` — skill責務、CLI分類、write boundary、materialization境界の正本
3. `plan.md` — 対象ファイル、実装順序、test、完了条件の正本

## Baseline

* Repository: `chemitaro/spec-dock`
* Branch: `iss-00359-replace-managed-workflow-skills-with-specdock-skills`
* Commit: `8e10f255b3377bf879b459380f563729522e22b2`

このcommitと異なる状態では、Current CLI、path、inventory、installer mappingを再確認してから着手する。

## 実装の中心

作るskillは次の二つである。

* `spec-dock`
* `spec-dock-grill-with-docs`

providerを先に実装し、dogfoodへbyte-identicalに反映する。

grillは`--initiative`、`--epic`、`--issue`のいずれか一つの明示selectorを必須とし、active scopeへfallbackしない。

grill成功時に許される永続差分は、対象scopeの新規Artifact Markdown一件だけである。`grilling`と`domain-modeling`はoperator-ownedであり、repositoryへ直接書き込ませない。

## Provider assetの境界

`install_root`へ追加した二つのprovider `SKILL.md`は、Currentの全file mappingによってinit / update copyとuninstall inventoryから認識される。

Issue #359ではこれをadditive skill asset materializationとして扱う。

次は変更しない。

* `_MANAGED_SKILL_NAMES`
* `_LEGACY_MANAGED_SKILL_NAMES`
* installer logic
* obsolete inventory
* 旧skill prune

Target inventory cutoverとconsumer migrationはIssue #360の責務である。

## 最初の変更対象

```text
src/spec_dock/assets/install_root/.agents/skills/spec-dock/SKILL.md
src/spec_dock/assets/install_root/.agents/skills/spec-dock-grill-with-docs/SKILL.md
src/spec_dock/assets/spec_dock/docs/README.md
src/spec_dock/assets/install_root/.codex/config.toml
tests/unit/infra/test_init_update.py
tests/cli_runtime/test_new.py
```

その後、provider内容を対応するdogfood pathへ反映する。

## CLI確認

* bare `doctor`: execute-read-only
* external GitHub diagnostic: present-only

```text
./spec-dock/scripts/spec-dock doctor \
  --github-repo <owner/repo> \
  --github-pr <pull-request-number> \
  --github-head-sha <head-sha> \
  [--github-extended]
```

`doctor --github`は使用しない。

## 最初の検証

```text
uv run pytest tests/unit/infra/test_init_update.py -q
uv run pytest tests/cli_runtime/test_new.py -q
uv run pytest tests/cli_runtime/test_storage_core_cli.py -q
uv run pytest tests/unit/infra/test_artifact_templates.py -q
```

## 停止条件

次が必要になった場合は実装を拡張せず、R/D/Pへ戻る。

* Runtimeの変更
* installer logicまたはmanaged inventory定数の変更
* 旧skillの物理削除
* fresh / update / uninstall consumer matrix
* Current CLIに存在しないcommand
* grillでのactive target fallback
* 新しいhost metadata file
* canonical文書の自動変更
* external skillによるrepository write
* 二件目のArtifact
* Issue #360のTarget inventory、distribution、migration、publication設計
* P2 / P3を根拠とする追加要件
