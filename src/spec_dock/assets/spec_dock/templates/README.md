# テンプレート一覧

各 scope は次の四文書を持ちます。

- `initiative/{requirement,design,plan,report}.md`
- `epic/{requirement,design,plan,report}.md`
- `issue/{requirement,design,plan,report}.md`

記入前に [Authoring Kit 概要](../docs/authoring/overview.md) を読み、各文書の役割は対応する Guide で確認します。
各テンプレートは対応する Guide を参照して記入する。

- [Requirement Guide](../docs/authoring/requirement.md)
- [Design Guide](../docs/authoring/design.md)
- [Issue Plan Guide](../docs/authoring/issue-plan.md)
- [Report Guide](../docs/authoring/report.md)

Current の Artifact template は次の六種です。

- `artifacts/{blank,research,interview,disc,decision-candidate,adr}.md`

用途と durable な反映先は [Artifact Guide](../docs/authoring/artifacts.md) を参照してください。

## CUE の Scope の雛形

canonical モード（宣言の版4）の `scope create` と `scope import github` は、上の `.md` の雛形ではなく、次の雛形から CUE の Scope を作ります（SpecDock 0.4.0 から）。

- `cue/initiative/{requirement.cue,design.cue,plan.cue,explanation.html,report.md}`
- `cue/epic/{requirement.cue,design.cue,plan.cue,explanation.html,report.md}`
- `cue/issue/{requirement.cue,design.cue,plan.cue,explanation.html,report.md}`

- `requirement.cue` の `{{ASSURANCE_LEVEL}}` と `{{ASSURANCE_REASON}}` は、作るときに必須の `--assurance <light|standard|strict|critical>` と `--assurance-reason <理由>` の値で置き換わります。理由は CUE の文字列の書き方に変えて入ります。
- `explanation.html` は `../design-system/explanation-skeleton.html` と同じバイトです。
- `cue/<種類>/` がない古い配布資産では、新しい CLI は GitHub に何も書かずに `SCOPE_TEMPLATES_OUTDATED` で止まります。`spec-dock installation update` で入れます。
- 書き方は [CUE Authoring Guide](../docs/authoring/cue.md) と [Explanation Guide](../docs/authoring/explanation.md) にあります。上の `.md` の雛形は、版3のリポジトリと前の版の CLI のために残しています。

## ID・token・更新単位

- テンプレート中の `<SCOPE_ID>`、`<INIT_ID>`、`<EPIC_ID>`、`<ISS_ID>` は、GitHubが発行した番号をkind prefix付きで表すCurrent Scope IDです。テンプレートが新しい番号を割り当てたり、UUIDやオフラインScopeを発行したりはしません。
- `artifact create` はCLIが解決した既存Scope IDを置換します。手作業でmetadataやIDを発行せず、create/importが返すIDとpathを使います。
- `spec-dock/.agent/work-target/target-<token>.json` のfile tokenは一件の直接記録用で、テンプレートへ代入するScope IDではありません。
- このtemplate treeはconsumer worktreeごとの静的資産です。provider側の正本をpackageへ収録し、明示したworktreeへ導入・更新します。installed Python runtimeはここへコピーされません。
