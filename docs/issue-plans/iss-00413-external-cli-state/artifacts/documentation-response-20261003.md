## GitHub検証結果

- **Repository:** `chemitaro/spec-dock`
- **Branch:** `codex/iss-00413-external-cli-state`
- **検証済みtip:** `8606e132327066d56567556e336e4bc1ae6a0b17`
- **Expected SHA:** `8606e132327066d56567556e336e4bc1ae6a0b17`
- GitHub connectorで対象branchを直接検索し、同branchをbase/headとするcommit比較から取得したfull SHAが完全一致することを確認しました。

## 主な修正内容

- provider開発source、外部tool環境のinstalled package、worktree単位のconsumer静的資産、ignoredな直接作業記録を明確に分離。
- Scope IDをGitHub番号とし、work-targetのfile token、UUID、オフラインScopeと区別。
- `active set`による新規取得例を廃止し、取得を`work start`へ統一。
- `create.lock`、shared lease、legacy active link、read-only permission gateなどの旧説明を現行実装へ更新。
- root Artifactの文法を`artifact import file PATH --scope @root`とCurrent v2 envelope/effectsへ更新。
- Issue 413のR/D/Pと説明HTMLを、検証済みSHAの既存証拠、0805 worktree限定適用、他worktree・正式Start・人間merge・publication未完了という現在状態へ更新。
- 旧SHA、旧試験、Windows検討、過去の実施記録はraw historyとして保持。
- PlantUML契約v2、4件の埋込source、`@plantuml/core@1.2026.6`、render/zoom JS、style boilerplateは元HTMLと同一のまま保持。
- `analysis.md`には、差し替え後の`static-inventory.json` hash更新、`known_old_sha256`追記、Current CLIによるconsumer反映、pack manifest/ZIP再生成の後続処理を記載。

## 全文差し替えファイル

**Root:** `README.md`、`AGENTS.md`

**Provider skill:**
`src/spec_dock/assets/install_root/.agents/skills/spec-dock/SKILL.md`

**Authoring・rules:**
`src/spec_dock/assets/spec_dock/docs/authoring/overview.md`
`src/spec_dock/assets/spec_dock/docs/rules/root/artifacts.md`
`src/spec_dock/assets/spec_dock/docs/rules/{initiative,epic,issue}/{artifacts,discussions}.md`

**System・templates:**
`src/spec_dock/assets/spec_dock/system/README.md`
`src/spec_dock/assets/spec_dock/system/.runtime/README.md`
`src/spec_dock/assets/spec_dock/system/active-none/README.md`
`src/spec_dock/assets/spec_dock/system/active-none/{initiative,epic,issue}/README.md`
`src/spec_dock/assets/spec_dock/templates/README.md`

**Issue 413:**
`docs/issue-plans/iss-00413-external-cli-state/{requirement.md,design.md,plan.md,explanation.html}`

ZIPには合計22件の全文置換ファイルと、`analysis.md`、`manifest.json`、`unchanged-documents.md`を単一root `specdock-413-documentation-replacements/` 配下に収録しています。既存の`8606e132`合格証拠は保持し、この文書差し替えに対する新規Final Quality Gate認定は付与していません。

**ZIP SHA-256:** `d2e2d3305fc2cdd7212c75b86730a1a4268c2e23d1bae88194ba3269e5e80f9f`

specdock-413-documentation-replacements.zip[specdock-413-documentation-replacements.zip をダウンロード](sandbox:/mnt/data/specdock-413-documentation-replacements.zip)
