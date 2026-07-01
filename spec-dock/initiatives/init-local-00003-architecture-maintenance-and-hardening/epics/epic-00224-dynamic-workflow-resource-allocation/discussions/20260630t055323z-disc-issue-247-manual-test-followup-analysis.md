---
種別: disc
ID: "20260630t055323z-disc"
タイトル: "Issue 247 Manual Test Follow-up Analysis"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-06-30"
親: ["epic-00224"]
関連: ["iss-00247", "#247", "manual-tests/iss-00247-profile-template-compose-20260630/summary.md"]
authority: "proposed"
derived_from: [
  "/Users/iwasawayuuta/.codex/attachments/6b3778a9-7196-4a6b-937b-37cff2fe54fe/pasted-text.txt",
  "manual-tests/iss-00247-profile-template-compose-20260630/summary.md",
  "ChatGPT 5.5 Pro consultation: epic224 grade template readiness analysis",
  "deep-consultant consultation: Banach"
]
reflected_to: []
---

# 20260630t055323z-disc Issue 247 Manual Test Follow-up Analysis

## 位置づけ

この artifact は、Issue #247 / PR #248 で導入した grade 別 Issue テンプレート群と、その後の手動テストで発見した readiness 判定不備を、既存 `epic-00224 Dynamic Workflow Resource Allocation` の中でどのように修正・再計画するべきかを整理するための discussion である。

結論は proposal であり、この文書単体は canonical authority ではない。採用する場合は、`epic-00224` の `requirement.md` / `design.md` / `plan.md`、必要なら ADR、後続 Issue の `report.md` Evidence Adoption Ledger へ反映する。

## 対象論点 (必須)

- 今回整理する論点:
  - Issue #247 の grade template pack 導入後、Epic #224 の旧 `Adaptive artifact composition` / `Compose Profile-Aware Planning Artifacts` をどのように読み替えるべきか。
  - 手動テストで再現した F-001〜F-004 を、Epic #224 の中でどの順序・粒度で修正すべきか。
  - `assurance classify`、`assurance compose`、`workflow status`、`guidance issue-execution` の責務境界を、実運用で未完成仕様書を execution-ready にしない形へどう再定義するか。
  - provider asset と dogfooding workspace の同期、skills/docs/guidance、回帰テスト、manual validation をどの work package に切るべきか。
- この synthesis が必要な理由:
  - Issue #247 の成果は template pack 導入としては前進したが、手動テストでは `workflow status` が未完成 artifact を `ready` と判定する false positive が見つかった。
  - Epic #224 はもともと「policy fragment から planning artifact sections を合成する」設計を含んでおり、現在の「grade-specific Markdown template pack を選択・materialize する」方針と表現がずれている。
  - readiness gate は Issue execution の安全境界であり、ここを曖昧にしたまま docs / skills / template を整備しても、agent が未完成 plan から実装を開始する可能性が残る。

## derived question sheets / research (必須)

- `interview`:
  - なし。
- `research`:
  - Issue #247 / PR #248 手動テスト報告サマリー: `manual-tests/iss-00247-profile-template-compose-20260630/summary.md`
  - ChatGPT 5.5 Pro レポート: `/Users/iwasawayuuta/.codex/attachments/6b3778a9-7196-4a6b-937b-37cff2fe54fe/pasted-text.txt`
  - Epic #224 canonical docs: `requirement.md` / `design.md` / `plan.md`
  - Runtime 実装確認: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py`
  - Requirement readiness 実装確認: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/workflow_state.py`
- その他の根拠:
  - ChatGPT 5.5 Pro consultation: `epic224 grade template readiness analysis`
  - deep-consultant consultation: `Banach`

## synthesis (必須)

- 合意済みのこと:
  - 新規 Initiative は作らず、`init-local-00003 Architecture Maintenance and Hardening` 配下の既存 `epic-00224` を amendment する。
  - Issue #247 の grade-specific template pack は破棄せず、`authorized_profile` に基づく deterministic template materialization として活かす。
  - ただし、`assurance compose` 成功を execution readiness と同一視してはならない。
  - 手動テスト F-001〜F-004 は、template content の見た目の問題ではなく、runtime readiness contract の false positive / false negative として扱う。
  - false negative より false positive が危険である。判定不能・未完成・placeholder 残存は `ready` ではなく blocked / capture / scaffold に寄せる。
- 未合意 / 未確定のこと:
  - Epic #224 の既存 `E-RQ-006` を完全に rename するか、変更履歴で supersede しつつ本文を再定義するか。
  - `assurance compose` をどこまで authoring の主経路に残すか。短期的には materialization helper として残すが、長期的に `new issue` 時点で selected template を直接生成するかは別判断が必要。
  - `authorized_profile` と人間が指定した Issue authoring grade / execution grade の関係をどこまで同一概念に寄せるか。
- source-grounded に解決できたこと:
  - Epic #224 requirement の `E-RQ-006` は現在も `design / plan / report の必要 sections を policy fragment から合成する` と書いているため、Issue #247 の Markdown template pack 方針と表現がずれている。
  - Epic #224 plan の `I03 — Compose Profile-Aware Planning Artifacts` は `Fragment source / preset manifests` や `design / plan / report composer` を成果物としており、grade template pack 選択・readiness validation を主語にした再定義が必要である。
  - `workflow.py` の plan 判定は `validation gate` を executable marker に含め、marker があれば `executable` へ進み得るため、F-002 と整合する。
  - `workflow.py` の table placeholder 判定は cell 全体が generated placeholder token である場合に寄っており、`SAFE-\`CLOS-...\`` のような composite placeholder を見落とすため、F-001 と整合する。
  - `workflow.py` の design frontmatter scaffold marker には `template` / `placeholder` が含まれており、正当な title に `template` が含まれると scaffold 扱いになり得るため、F-004 と整合する。
  - `workflow_state.py` の requirement placeholder 判定は古い sentinel 中心であり、`REQ-XXX` / `CON-...` を包括的に拾う contract になっていないため、F-003 と整合する。

## 選択肢 / tradeoff (必須)

- Option A: 新規 Initiative / 新規 Epic を作って #247 後続を分離する
  - Pros:
    - 既存 Epic #224 の古い記述を大きく触らずに済む。
    - template pack / docs / tests だけを独立したテーマとして扱いやすい。
  - Cons:
    - #224 の `Assurance Contract`、`Runbook`、`Artifact composition`、`workflow guidance` と責務が重複する。
    - readiness false positive は #224 の execution safety 境界そのものなので、別 Epic に逃がすと authority が分裂する。
    - 手動テストで見つかった問題が「template pack の後始末」に見えてしまい、runtime gate の P1 問題として扱いにくくなる。
- Option B: 既存 Epic #224 を amendment し、最初に readiness contract を閉じる
  - Pros:
    - #224 の既存責務と一致する。
    - `E-RQ-006` / `I03` を grade template pack 方針へ自然に更新できる。
    - 未完成 artifact を execution-ready にしない安全境界を、runtime / docs / skills / tests まで一貫して直せる。
  - Cons:
    - 既存 Epic docs の変更量は増える。
    - 過去の `compose` 中心記述と新方針の supersession を丁寧に記録しないと、後続 agent が旧文脈へ戻るリスクがある。
- Option C: Runtime には小さな regex patch だけを入れ、docs / skills は後回しにする
  - Pros:
    - F-001〜F-004 の表面的な再現は短期で潰せる。
    - PR サイズは小さくしやすい。
  - Cons:
    - template / readiness / executable plan の共通契約がないままになる。
    - 次の template 変更で別の placeholder 表現を取りこぼす可能性が高い。
    - `assurance compose` と `workflow status` の責務境界が曖昧なまま残る。

推奨は Option B である。必要に応じて Option C 相当の最小 hotfix を WP-224-B に含めるが、単発 regex 修正ではなく `Artifact Readiness Contract` の入口として扱う。

## reflection proposal (必須)

- canonical docs / workflow / template / skill guidance へ反映すべき候補:
  - `E-RQ-006` を `Grade Template Pack Selection And Artifact Readiness Contract` 相当に再定義する。
  - `I03` を `Compose Profile-Aware Planning Artifacts` から、`Select Grade-Specific Authoring Templates And Enforce Readiness` 相当に再定義する。
  - `assurance classify` は profile authorization と source binding の authority、`assurance compose` は selected template materialization / diagnostic、`workflow status` と `guidance issue-execution` は execution readiness の最終 preflight と明記する。
  - `workflow status` は未解決 placeholder、見出しだけの plan、実行単位を欠く plan を `ready` にしない。
  - `guidance issue-planning` / `guidance issue-execution` と issue planning / execution skills は、template materialized と approved/executable/readiness を分けて説明する。
  - Standard 以上の template 品質ゲート、commit 候補、M99 static analysis / lint / tests は template content として維持するが、それらの見出しだけで executable plan とみなさない。
- まだ proposal に留める理由:
  - この文書は分析レポートであり、canonical Epic docs の直接 amendment ではない。
  - #247 の post-merge 手動テストは FAIL だが、修正 Issue の切り方と既存 #229 / #247 の historical closure の扱いは、人間の採用判断が必要である。
  - `authorized_profile` と issue authoring grade / execution grade の関係は、今後の設計判断として明示的に決める必要がある。

## adoption target / 採用先候補 (必須)

- `requirement.md`:
  - `変更履歴` に Issue #247 / PR #248 後の grade template pack 方針と manual FAIL を追記する。
  - `E-RQ-006` を「policy fragment 合成」ではなく「authorized profile に基づく grade-specific template pack selection と artifact readiness contract」へ改定する。
  - `Templates は scaffold であり compliance authority ではない` を維持しつつ、execution readiness は runtime preflight が fail-closed で判断すると明記する。
- `design.md`:
  - コンポーネント図内の `Artifact Composer` を、profile Markdown template materializer / diagnostic helper と readiness validator に分ける。
  - `Workflow State Resolver` / `Guidance Compiler` / `Artifact Readiness Validator` の責務境界を明記する。
  - placeholder registry、frontmatter 判定範囲、executable plan predicate、positive/negative readiness examples を設計契約に含める。
- `plan.md`:
  - `I03` の目的・成果物・受け入れ条件を grade template pack + readiness validation へ変更する。
  - 手動テスト F-001〜F-004 を閉じる corrective slice を先行 work package として追加する。
  - 後続 docs/skills/template parity/manual validation を別 slice に分ける。
- `ADR`:
  - ADR 候補あり。旧 dynamic fragment composition を supersede し、grade template pack selection + fail-closed readiness contract を長期判断として固定する場合は ADR 化する。
- `report.md` Evidence Adoption Ledger:
  - Issue #247 post-merge manual test の FAIL と F-001〜F-004 を evidence として記録する。
  - 後続修正後は、同じ manual test harness の再実行結果と CLI/unit tests の pass を evidence として採用する。

## ADR triage / ADR candidate triage (必須)

- ADR candidate か:
  - yes
- hard to reverse:
  - yes
- surprising without context:
  - yes
- real tradeoff:
  - yes
- ADR 化しない場合の反映先:
  - `requirement.md` / `design.md` / `plan.md`

理由: `policy fragment から動的に section を合成する` 旧表現を、`authorized_profile に基づく static Markdown template pack selection + fail-closed readiness validation` へ置換する判断は、runtime contract、skills、docs、tests、dogfooding workflow に跨る。後続 agent が旧 `compose` 主経路へ戻らないよう、ADR または Epic requirement の amendment history で固定する価値がある。

## 推奨案 (必須)

現時点の推奨案は、既存 `epic-00224` 内に correction tranche を追加し、次の順序で進めることである。

1. `epic-00224` の方針 amendment を行う。
2. `workflow readiness` の false positive / false negative を最優先で修正する。
3. その上で grade template pack resolution / compose contract を整理する。
4. docs / skills / runtime guidance を同じ語彙へ揃える。
5. manual test harness と CLI/unit regression で F-001〜F-004 と positive ready path を固定する。

理由は、手動テストで発見した問題の本質が template pack の表層ではなく、`workflow status` / `guidance issue-execution` の safety boundary にあるためである。未完成 artifact を `ready` とする false positive は、Issue execution を誤って開始させる P1 相当の運用リスクであり、docs の追記や template 文言修正だけでは閉じられない。

### 推奨 Work Packages

#### WP-224-A — Amend Epic Direction For Grade Template Authoring

- 目的:
  - #247 / #248 により、Epic #224 の `E-RQ-006` / `I03` が旧 dynamic fragment composition から grade template pack selection へ変化したことを canonical docs に反映する。
- 受け入れ条件:
  - `requirement.md` の `E-RQ-006` が grade-specific template selection と readiness contract を扱う。
  - `plan.md` の `I03` が fragment manifests 中心ではなく、template pack resolution / materialization / readiness validation 中心に改定される。
  - `assurance compose` は helper / diagnostic / materialization として位置づけられ、execution readiness authority ではないと明記される。

#### WP-224-B — Enforce Issue Artifact Readiness Preflight

- 目的:
  - 手動テスト F-001〜F-004 を修正し、未完成 artifact を `ready` にしない。
- 受け入れ条件:
  - `SAFE-\`CLOS-...\`` / `SAFE-\`B-...\`` など、table/list cell の一部に含まれる composite placeholder が検出される。
  - `REQ-XXX` / `CON-...` / `B-...` / `CLOS-...` / `SAFE-...` / `...` など、template placeholder registry が requirement/design/plan readiness と共有される。
  - `## Validation Gate` や M99 品質ゲート見出しだけでは executable plan と判定しない。
  - plan readiness は、実装ステップ、振る舞い backlog、TDD cycle、closure contract などの実行可能な作業単位を要求する。
  - frontmatter title に `template` / `placeholder` という語があるだけでは design を scaffold 扱いしない。
  - placeholder を除去した positive standard path は `ready` のまま維持される。

#### WP-224-C — Define Deterministic Grade Template Pack Resolution And Compose Contract

- 目的:
  - `authorized_profile` に基づく template pack 選択、materialization、fallback、diagnostic を runtime contract として固定する。
- 受け入れ条件:
  - common requirement template と `issue-profiles/{lite,standard,strict,critical}/{design,plan}.md` の provider asset layout が source of truth として明記される。
  - Issue-local directory に全 profile templates が誤ってコピーされない。
  - unknown / unavailable profile は fail-fast diagnostic を返す。
  - provider asset と dogfooding mirror の整合確認手順がある。

#### WP-224-D — Align Runtime Guidance, Skills, And Docs With Grade Authoring

- 目的:
  - issue planning / execution の agent guidance を、grade template materialization と readiness gate の二段階に揃える。
- 受け入れ条件:
  - skill は fixed kernel として `guidance <target>` を実行し、blocked 時に停止する。
  - docs は `template materialized`、`reviewer approved`、`workflow ready`、`may_execute_approved_plan=true` を混同しない。
  - Standard 以上の static analysis / lint / tests / report / commit gate は、PR 後 CI で初めて基礎失敗を見つける前提ではなく、ローカル最終品質ゲートとして説明される。

#### WP-224-E — Add Readiness, Template, And Dogfooding Validation Evidence

- 目的:
  - 手動テストで見つかった regression を自動テストと manual evidence に固定する。
- 受け入れ条件:
  - F-001〜F-004 の negative tests が CLI runtime / domain tests に入る。
  - positive ready path が regression として残る。
  - `uvx --from . spec-dock init <trial-repo>` 相当の installer smoke で provider scaffold が確認される。
  - `manual-tests/iss-00247-profile-template-compose-20260630` の再実行結果が PASS に更新される、または後続 manual test artifact が作成される。

#### WP-224-F — Rollout Closure Without Automatic Lite Default

- 目的:
  - grade template pack と readiness gate を導入しても、automatic Lite default は有効化しないという既存 Epic 方針を維持する。
- 受け入れ条件:
  - Standard が新規 adaptive Issue の authoritative default として維持される。
  - Lite は `lite_candidate` / `lite_authorized` の区別を維持し、automatic Lite default は別 ADR / policy version bump / rollout evidence なしに有効化されない。

## 推奨反映先 (必須)
- `requirement.md`:
  - `変更履歴` に 2026-06-30 の #247 post-merge manual validation と readiness correction 方針を追記する。
  - `E-RQ-006` を改定する。
- `design.md`:
  - component responsibility と PlantUML を更新し、`Artifact Composer` / `Template Materializer` / `Artifact Readiness Validator` を分ける。
  - placeholder registry と executable plan predicate の設計契約を追加する。
- `plan.md`:
  - `I03` の scope を改定し、WP-224-B 相当の corrective slice を先行させる。
  - F-001〜F-004 と positive ready path を validation matrix に入れる。
- `ADR`:
  - 旧 dynamic fragment composition を supersede する判断を長期固定するなら ADR 化する。
- `report.md` Evidence Adoption Ledger:
  - 手動テスト FAIL、consultation、後続修正の verification evidence を採用する。

## 具体的な修正候補

### Runtime / Domain

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py`
  - `_classify_plan_text` から `validation gate` 単独の executable 判定を外す、または quality gate marker と executable work marker を別分類にする。
  - `_has_placeholder_table_rows` / `_has_placeholder_list_items` を、cell 全体一致だけでなく token containment / composite placeholder に対応させる。
  - `_classify_design_text` の frontmatter scaffold marker から generic な `template` / `placeholder` 単語一致を外し、`artifact_state: awaiting-assurance-compose` や明示 sentinel へ狭める。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/workflow_state.py`
  - `classify_requirement_text` の placeholder markers を template pack の ID 体系に合わせて拡張する。
  - 可能なら placeholder detection を application/domain で重複させず、共通 helper / contract に寄せる。

### Tests

- `tests/cli_runtime/test_workflow.py`
  - plan table cell に `SAFE-\`CLOS-...\`` が残る場合は `ready` ではない。
  - `## Validation Gate` だけの plan は `ready` ではない。
  - positive filled standard artifacts は `ready` のまま。
- `tests/unit/domain/test_workflow_state.py`
  - requirement に `REQ-XXX` / `CON-...` が残る場合は `scaffold`。
- `tests/unit/infra/test_init_update.py` または scaffold asset test
  - provider template pack layout と dogfooding mirror parity を確認する。

### Docs / Skills

- `src/spec_dock/assets/spec_dock/docs/phase_design.md`
  - `assurance compose` は profile template materialization の補助であり、authoring completion / execution readiness ではないことを明記する。
- `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md`
  - `Validation Gate` / `M99` は品質ゲートであり、実装単位の代替ではないことを明記する。
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
  - requirement -> classify -> materialize selected template -> fill substantive design/plan -> reviewer/guidance gate の順序を維持する。
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
  - `may_execute_approved_plan=true` 以外では停止する既存方針を維持し、template materialized だけでは実装開始しないことを強める。

## 修正順序

1. Epic #224 amendment artifact / ADR candidate を作る。
2. Readiness false positive の runtime tests を red として追加する。
3. Runtime / domain placeholder and executable plan classifier を修正する。
4. Positive ready path と F-001〜F-004 の regression を通す。
5. Docs / skills の語彙を揃える。
6. Provider asset / dogfooding mirror parity と manual test rerun を確認する。
7. Epic #224 `requirement.md` / `design.md` / `plan.md` へ採用済み evidence として反映する。

## 未解決質問

- `assurance compose` を今後も必須の authoring materialization step にするか、それとも `new issue` 時点で selected grade templates を直接 canonical `design.md` / `plan.md` に配置するか。
- `authorized_profile` と人間が「この Issue は strict で計画する」と判断した authoring grade を、同じ概念に統合するか、別メタデータとして扱うか。
- Placeholder detection は Markdown text heuristic に留めるか、template pack 側に `placeholder registry` / schema / structured marker を持たせるか。
- Epic #224 の過去完了扱い Issue / report で `E-AC pass` とした箇所を、manual FAIL を受けて correction pending としてどう追記するか。

## 結論

Issue #247 の成果は、grade template pack を provider assets として採用し、`assurance compose` が profile Markdown template を materialize できるようにした点で有効である。一方で、手動テストは `workflow status` / `guidance issue-execution` の readiness contract がまだ安全に閉じていないことを示した。

したがって、次の実装は template pack の追加改善より前に、Epic #224 内の `Artifact Readiness Contract` を先に固定し、F-001〜F-004 を regression として閉じるべきである。その後に docs / skills / template selection / dogfooding validation を揃えるのが、今回の Epic 単位で最も安全な修正順序である。

## 未採用 / deferred 理由 (必須)
- 未採用:
  - 新規 Initiative 化は採用しない。今回の問題は #224 の workflow / artifact / guidance authority に直結しており、別 Initiative にすると責務が分裂する。
  - docs だけの修正は採用しない。runtime readiness の false positive が残るため、実運用上の安全境界を閉じられない。
  - `template` という語を全面禁止する修正は採用しない。F-004 のように正当な title / prose を誤って scaffold 扱いするため、検出範囲を narrow にする。
- deferred:
  - `assurance compose` を完全に廃止するかどうかは deferred。現時点では selected profile template materialization と diagnostic helper として残す。
  - automatic Lite default の有効化は deferred。既存 Epic 方針どおり、別 ADR / policy version bump / rollout evidence なしには進めない。
  - discussions -> artifacts rename や設計レイヤー全面再整理は deferred。今回のスコープは #224 内の grade template authoring と readiness correction に限定する。

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - `requirement.md`: #247 / manual FAIL の amendment history と、改定版 `E-RQ-006`。
  - `design.md`: template materializer / readiness validator / workflow state resolver の責務境界。
  - `plan.md`: WP-224-A〜F、特に WP-224-B の先行化と F-001〜F-004 regression。
  - `ADR`: 旧 dynamic fragment composition を grade template pack selection + fail-closed readiness contract へ supersede する判断を固定する場合に作成する。
- 追加で作る discussion docs:
  - 追加 discussion は現時点では不要。次は canonical docs amendment または ADR candidate の作成へ進む。
