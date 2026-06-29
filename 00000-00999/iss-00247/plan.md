---
種別: 実装計画書（Issue）
ID: "iss-00247"
タイトル: "Move Assurance Compose Scaffold Sources To Profile Markdown Templates"
関連GitHub: ["#247"]
Issue Grade: "strict"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-29"
依存: ["requirement.md", "design.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00247 Move Assurance Compose Scaffold Sources To Profile Markdown Templates — 実装計画書（Strict / Spec-Locked TDD）

## 0. 文書の位置づけ

この計画書は、承認済みの `requirement.md` と `design.md` を、実行可能な milestone、closure index、検証ゲート、`report.md` への証跡記録先へ変換する。

実装中の観測結果、Red / Green / Refactor 証跡、逸脱、追加判断、review 結果は `report.md` に記録する。この文書は予定された実行契約であり、実績台帳ではない。

## 1. 計画開始条件

| Artifact | 状態 | 確認事項 |
|---|---|---|
| `requirement.md` | approved | AC-001〜AC-013、BH-001〜BH-007、strict grade の根拠がある |
| `design.md` | approved | DES-001〜DES-010、互換性、失敗時の扱い、実装計画への引き渡しがある |
| `report.md` | approved | authoring / adoption / execution evidence の記録先がある |
| Template pack | inspected | common requirement と profile 別 design / plan templates が存在する |
| Parent Epic | inspected | dynamic workflow resource allocation の文脈を確認済み |
| `.assurance.json` | valid, `authorized_profile=standard` | runtime の選択権限は standard のまま、issue-local execution gate は手動で strict 相当に引き上げる |

実装開始前のブロッカー:

- fresh `spec-reviewer` pass が必要である。
- 実装中に template pack を採用するには要件意味論の変更が必要だと判明した場合、実装を止めて authoring へ戻る。
- 手動で引き上げた strict planning grade を runtime compose の template selection input に使ってはならない。

## 2. 実装戦略

この Issue では Spec-Locked TDD を採用する。Spec-Locked とは、承認済みの要件、設計契約、互換性方針、検証契約を、実装都合で暗黙に変更しないことを意味する。

実行順:

1. 既存 composer / installer behavior を characterization する。
2. template assets と asset presence tests を追加する。
3. Markdown template source を domain / infra に導入し、既存安全契約を維持する。
4. application / infra loader と mixed-mode compose を接続する。
5. installer / dogfooding parity と docs / skill impact を検証する。
6. 完了前に reviewer gates を通す。

実行は承認済み step を 1 つずつ進める。各 step は割り当てられた closure IDs を閉じてから次へ進む。

## 3. スコープと変更面

許可する変更:

| 種別 | Path / 対象 | 許可する変更 | Design |
|---|---|---|---|
| templates | `src/spec_dock/assets/spec_dock/templates/issue/requirement.md` | common requirement template の更新 | DES-001 |
| templates | `src/spec_dock/assets/spec_dock/templates/issue-profiles/**` | profile 別 design / plan templates の追加 | DES-001 |
| templates | issue templates 全般 | title、見出し、小見出し、説明本文の日本語優先補正 | DES-010 |
| templates | `src/spec_dock/assets/spec_dock/templates/assurance/profile-sections.json` | design / plan prose authority の除去。必要なら report 用 legacy source を維持 | DES-004 |
| runtime domain | `.../domain/artifact_composer.py` | template source model、validation、compose behavior | DES-002, DES-005, DES-007 |
| runtime infra | `.../infra/artifact_store.py` | profile template loader | DES-002 |
| runtime application | `.../application/assurance.py` | mixed-mode preflight と result handling。必要な場合のみ | DES-005, DES-008 |
| tests | `tests/unit/**`, `tests/cli_runtime/**` | behavior、contract、installer parity tests | all |
| docs / skills | relevant docs / skill assets | 実装により workflow guidance の古さが明確になった場合のみ | DES-009 |
| dogfooding | `spec-dock/templates/**` | validation target / generated scaffold parity。必要な場合のみ | DES-009 |

禁止する変更:

- 既存 Issue の `design.md` / `plan.md` を無条件に full-file overwrite すること。
- `lite_candidate` を理由に Lite template を選択すること。
- runtime に network access を導入すること。
- GitHub mutation を行うこと。
- `report.md` evidence lifecycle を redesign すること。
- 関係のない広範な refactor を行うこと。

## 4. 仕様固定クロージャ一覧

| Closure ID | Requirement | Design | 閉じる内容 | 検証レベル | Report Evidence |
|---|---|---|---|---|---|
| CLOS-001 | AC-001, AC-004 | DES-001 | provider template pack files が期待 layout に存在する | asset inspection + installer test | `report.md` Step Evidence |
| CLOS-002 | AC-002, AC-003 | DES-002, DES-003 | compose が `authorized_profile` で profile Markdown template を選択する | domain + CLI tests | `report.md` Step Evidence |
| CLOS-003 | AC-005 | DES-004 | `report.md` compose behavior が互換維持される | regression tests | `report.md` Step Evidence |
| CLOS-004 | AC-006 | DES-005 | missing / invalid template が write 前に fail-closed する | unit / application tests | `report.md` Step Evidence |
| CLOS-005 | AC-007, AC-008, AC-009 | DES-006, DES-007 | placeholder safety、no-overwrite、idempotence、downgrade safety が維持される | domain tests | `report.md` Step Evidence |
| CLOS-006 | AC-010, AC-011 | DES-008 | dry-run、changed_paths、source binding update が正しく維持される | application + CLI tests | `report.md` Step Evidence |
| CLOS-007 | AC-012 | DES-009 | installed scaffold / dogfooding parity が検証される | installer / manual inspection | `report.md` Step Evidence |
| CLOS-008 | all | DES-009 | docs / skill impact が解消または明示的に deferred される | docs inspection + spec-reviewer | `report.md` S90 |
| CLOS-009 | AC-013 | DES-010 | 追加・更新 template の title / heading / prose が日本語優先である | template inspection + reviewer | `report.md` Step Evidence |

## 5. 振る舞いバックログ

| Behavior ID | Milestone | 振る舞い / 保証 | Closure | 依存 | 優先度 |
|---|---|---|---|---|---|
| B-001 | M0 | 変更前に既存 composer behavior を characterization する | CLOS-003, CLOS-005, CLOS-006 | none | high |
| B-002 | M1 | template pack files が provider assets に入る | CLOS-001 | B-001 | high |
| B-003 | M2 | domain composer が profile Markdown templates から design / plan を materialize できる | CLOS-002, CLOS-005 | B-002 | high |
| B-004 | M3 | template validation errors が write 前に fail-closed する | CLOS-004 | B-003 | high |
| B-005 | M4 | `--artifact all` が design/plan Markdown + report legacy の mixed-mode で動作する | CLOS-003, CLOS-006 | B-003 | high |
| B-006 | M5 | install / update / dogfooding scaffold が新しい templates を公開する | CLOS-007 | B-002, B-005 | high |
| B-007 | M90 | docs / skill impact が処理される | CLOS-008 | B-005 | medium |
| B-008 | M1 | template title / heading / prose が日本語優先に補正される | CLOS-009 | B-002 | high |

## 6. マイルストーンと実装ステップ

### S00: ベースライン characterization

担当: repo-analyst または dev-coder。

予定された義務:

- 実装変更前に、compose、report legacy sections、placeholder guards、source binding、installer asset copying の現在の挙動を確定する。
- この step 単体では requirement を閉じない。CLOS-003、CLOS-005、CLOS-006 の前提証跡を提供する。

Red / 代替証跡:

- Red 代替は characterization-only とする。
- 現在の focused tests がすでに pass する場合は、intentional Red ではなく baseline coverage として記録する。
- 編集前に既存テストが fail した場合は停止し、existing regression Red として分類する。

Green 検証:

- `uv run pytest tests/unit/domain/test_artifact_composer.py`
- `uv run pytest tests/unit/application/test_assurance.py`
- `profile-sections.json` を点検し、現在どの sections が design / plan / report prose の source になっているか記録する。

Refactor ガード:

- S00 では実装 refactor を行わない。
- この step で許可する production file edit は report evidence の記録のみ。

Report 記録先:

- `report.md` の session log、TDD evidence table、Discovered Tests、Closure Coverage。

計画修正トリガー:

- baseline behavior が `design.md` DES-004〜DES-008 と異なる場合、S01 へ進む前に停止して `design.md` を更新する。

Closure IDs（クロージャID）:

- CLOS-003、CLOS-005、CLOS-006 の baseline evidence に寄与する。

具体作業:

- 現行 `artifact_composer.py`、`artifact_store.py`、`assurance.py`、`profile-sections.json` を確認する。
- compose behavior を覆う focused existing tests を実行または特定する。
- baseline behavior と、更新が必要なテスト期待値を記録する。

### S01: provider template assets の追加

担当: dev-coder。

予定された義務:

- ユーザー提供 template pack を provider assets に採用し、実際の Issue directory 内には profile-specific canonical files を増やさない。
- 採用する template の title、見出し、小見出し、説明本文を日本語優先へ補正する。
- provider または installed scaffold に必須 template files がない場合に失敗する test を追加または更新する。

Red / 代替証跡:

- 推奨 Red: asset presence / installer assertion を追加し、files 追加前に fail することを確認する。
- 代替: expectation 更新後に既存 installer snapshot test が missing files で fail する場合、それを Red として記録できる。

Green 検証:

- `rg --files src/spec_dock/assets/spec_dock/templates/issue-profiles`
- 実装差分に応じた focused installer / scaffold pytest。候補は `tests/unit/infra/test_init_update.py` または近傍 scaffold tests。
- 採用後の `templates/issue/requirement.md` が汎用 placeholder-only 構造のままではないことを点検する。
- 採用後の template title、見出し、小見出し、説明本文が日本語優先であり、必要な英語名が括弧併記になっていることを点検する。

Refactor ガード:

- asset tests を表現するための小さな path constant 以外では、S01 で runtime compose logic を編集しない。
- active Issue directories 配下に profile template files を追加しない。

Report 記録先:

- `report.md` の Step Evidence、Test Contract Closure、CLOS-001 の Closure Coverage。

計画修正トリガー:

- ZIP templates に path / metadata adaptation または日本語優先補正を超える意味論的 rewrite が必要な場合、停止して requirement scope 変更要否を記録する。

Closure IDs（クロージャID）:

- CLOS-001、CLOS-009。

具体作業:

- ZIP の common `requirement.md` を provider `templates/issue/requirement.md` へ copy / adapt する。
- `templates/issue-profiles/{lite,standard,strict,critical}/{design,plan}.md` を追加する。
- template pack 由来の英語 title / heading / prose を、日本語優先の title / heading / prose へ補正する。
- 実際の Issue directories は単一 artifact set のまま維持し、profile files を増やさない。
- asset presence / install-update assertions を追加する。

### S02: profile 別 Markdown template source の domain / infra 導入

担当: dev-coder。

予定された義務:

- `design` / `plan` compose が profile Markdown template files を使うようにしつつ、`authorized_profile` selection authority と report legacy compose を維持する。
- `design` / `plan` の長文 prose body authority を JSON manifest から除去するか、metadata-only にする。

Red / 代替証跡:

- Red: profile Markdown body content が composed `design` / `plan` に入ることを期待する domain test が、loader 実装前に fail する。
- Red: `authorized_profile=standard` かつ `lite_candidate=true` の test が、Lite を選ぶ実装なら fail する。
- Red: `profile-sections.json` が `design` / `plan` prose bodies を authority としてまだ含む場合、inspection または test が fail する。

Green 検証:

- `uv run pytest tests/unit/domain/test_artifact_composer.py`
- 4 profiles と 2 artifacts を覆う追加 focused domain tests。
- report sections が利用可能なまま残っていることを点検する。

Refactor ガード:

- 新しい domain API は小さく、既存 layer に沿わせる。
- infra file loading を application orchestration に押し込まない。
- この step では `assurance classify` の profile decision logic を変更しない。

Report 記録先:

- `report.md` の Step Evidence、Discovered Tests、CLOS-002 / CLOS-003 の Closure Coverage。

計画修正トリガー:

- Markdown template files で idempotence / downgrade semantics を維持できない場合、停止して `design.md` へ戻る。

Closure IDs（クロージャID）:

- CLOS-002、CLOS-003。

具体作業:

- design / plan profile Markdown files 用の template loader model を追加する。
- `authorized_profile` selection semantics を維持する。
- `design` / `plan` prose body authority を JSON manifest から除去するか、report-only / metadata-only manifest に変える。
- `report` legacy path を維持する。

### S03: fail-closed validation と atomic compose

担当: dev-coder。

予定された義務:

- 最初の write 前に、全 target artifacts と selected templates を検証する。
- `--artifact all` でいずれか 1 artifact が fail した場合、すべての artifacts と `.assurance.json` が unchanged のままであることを保証する。

Red / 代替証跡:

- Red: missing template test が validation support 実装前に fail する。
- Red: invalid marker template test が template marker validation 実装前に fail する。
- Red: mixed-mode `--artifact all` partial failure test が write-before-fail behavior を露出する。

Green 検証:

- fail 時に artifact texts と contract writes が unchanged であることを assert する focused unit / application tests。
- 既存 marker conflict tests が green のまま。
- template loader が新しい path behavior を追加する場合、path / symlink guard tests が green のまま、または拡張されている。

Refactor ガード:

- error reasons は明示的にし、既存 result structure から見えるようにする。
- preflight ordering で十分な場合、広範な transaction machinery を導入しない。

Report 記録先:

- `report.md` の Step Evidence、Test Contract Closure、CLOS-004 / CLOS-005 の Closure Coverage。

計画修正トリガー:

- 現在の store interfaces で atomicity を保証できない場合、停止して design / application contract を更新してから続行する。

Closure IDs（クロージャID）:

- CLOS-004、CLOS-005。

具体作業:

- selected template が存在し、allowed root 配下にあり、non-empty であり、managed markers を使う場合は marker が valid であることを検証する。
- `--artifact all` で invalid artifact がある場合、どの artifact も write しない。
- path / symlink / substantive content guards を維持する。

### S04: application result contract と source binding

担当: dev-coder。

予定された義務:

- Markdown template source migration 後も、公開 `assurance compose` result semantics を維持する。
- dry-run、changed_paths、error reporting、source binding behavior を監査可能なまま保つ。

Red / 代替証跡:

- Red: dry-run が変更予定を報告しつつ files を変更しないことを期待する application / CLI test が、接続実装前に fail する。
- Red: `.assurance.json` が dry-run で更新される、または real write 後に更新されない場合に source binding test が fail する。
- 既存 changed_paths test がすでに十分精密なら、covered-existing evidence として扱える。

Green 検証:

- `uv run pytest tests/unit/application/test_assurance.py`
- `assurance compose --artifact design`、`--artifact plan`、`--artifact all` の focused CLI runtime tests。
- template failure 時の JSON output に changed paths と errors が見えることを確認する。

Refactor ガード:

- requirement / design を更新しない限り、command output contract を後方互換に保つ。
- network や external state を追加しない。

Report 記録先:

- `report.md` の Step Evidence、Test Contract Closure、CLOS-006 の Closure Coverage。

計画修正トリガー:

- output shape の変更が必要になった場合、停止して AC-010 / AC-011 と design result contract を更新する。

Closure IDs（クロージャID）:

- CLOS-006。

具体作業:

- dry-run behavior を維持する。
- changed_paths reporting を維持する。
- real writes 後にのみ planning source binding を更新する。
- errors が JSON / CLI output から確認できるようにする。

### S05: provider / dogfooding / installed parity

担当: dev-coder。実装後に qa-reviewer が確認する。

予定された義務:

- provider assets、dogfooding scaffold、installed target repos が同じ template structure と compose behavior を公開していることを証明する。

Red / 代替証跡:

- Red: target repo 内の `issue-profiles/<profile>/<artifact>.md` を期待する installer / update test が、asset copying 更新前に fail する。
- 代替: asset copying が generic で、assets 追加後にしか test を置けない場合、inspect-only Red alternative として理由を記録する。

Green 検証:

- focused installer / update pytest。
- dogfooding scaffold を refresh する場合、`rg --files spec-dock/templates | rg 'issue-profiles/(lite|standard|strict|critical)/(design|plan)\\.md'` で構造を確認する。
- 必要に応じて temp target で controlled manual compose を行い、before / after paths を `report.md` に記録する。

Refactor ガード:

- parity validation の一部として active dogfooding issue artifacts を rewrite しない。
- user-authored dogfooding data を削除しない。

Report 記録先:

- `report.md` の Step Evidence、CLOS-007 の Closure Coverage、Final QA Gate input。

計画修正トリガー:

- dogfooding refresh が user-authored files を上書きする可能性がある場合、停止して明示承認を得るか、非破壊 inspection を選ぶ。

Closure IDs（クロージャID）:

- CLOS-007。

具体作業:

- initialized target repo に profile templates が含まれることを確認する。
- scaffold update が必要な場合、dogfooding workspace template structure を確認する。
- controlled target で `assurance compose` が selected profile template を materialize できることを確認する。

### S90: docs / skill impact resolution

担当: non-issue docs の編集が必要な場合は doc-writer。main orchestrator は issue-local decisions の記録だけを直接行う。

予定された義務:

- 新しい template model によって生じる docs / skill changes を解消または明示的に defer する。
- templates 導入後も future agents が手動 design / plan authoring に戻されないことを確認する。
- template 言語方針が docs / skill guidance と衝突しないことを確認する。

Red / 代替証跡:

- Red 代替: docs inspection で stale guidance を特定し、doc edits 前に具体 path を記録する。
- docs edits が不要な場合は、点検した paths と no-op rationale を記録する。

Green 検証:

- `design.md` section 9 に listed された workflow / authoring docs を点検する。
- docs / skill guidance が英語 title / heading を標準として誘導していないことを点検する。
- doc-writer が docs を編集した場合、`git diff --check` と fresh `spec-reviewer` を実行する。

Refactor ガード:

- main orchestrator は non-issue permanent docs を直接編集しない。
- doc-writer task は docs / skill assets の範囲に限定する。

Report 記録先:

- `report.md` の Final Quality Gate S90 row と CLOS-008 / CLOS-009 の Closure Coverage。

計画修正トリガー:

- docs がこの plan と衝突する workflow conflict を示した場合、停止して `requirement.md` / `design.md` / `plan.md` を更新する。

Closure IDs（クロージャID）:

- CLOS-008、CLOS-009。

具体作業:

- workflow docs と issue-planning skill expectations を点検する。
- templates 導入後も current guidance が agent を手動 design / plan authoring に戻す場合のみ、docs / skills を更新する。
- current guidance が template title / heading / prose の英語優先を誘導する場合は、doc-writer へ修正を委任する。
- deferred docs がある場合、non-blocking rationale と follow-up を記録する。

### S99: final quality gate

担当: orchestrator が reviewers を調整する。

予定された義務:

- `issue finish` / PR preparation の前に、すべての closure IDs が coverage を持ち、review gates が pass し、未解決 blocker が残っていないことを確認する。

Red / 代替証跡:

- この step では intentional Red は不要である。
- reviewer finding が fail の場合、それを blocking Red として扱い、該当 step へ戻す。

Green 検証:

- `qa-reviewer` が CLOS-001〜CLOS-009 の coverage を確認する。
- `code-reviewer` が統合された runtime / template / test diff を確認する。
- `spec-reviewer` が最終的な requirement / design / plan / report alignment を確認する。
- `git diff --check`。
- 前 step で定義された relevant pytest lanes。

Refactor ガード:

- S99 では、reviewer-requested fixes を具体 step へ戻す場合を除き、新しい実装変更を行わない。

Report 記録先:

- `report.md` の Final QA Gate、Final Code Review Gate、Final Spec Review Gate、Final Commit。

計画修正トリガー:

- final review が新しい scope または design obligations を見つけた場合、authoring に戻って fresh review を再実行する。

Closure IDs（クロージャID）:

- CLOS-001〜CLOS-009 の完了を確認する。

## 7. report 証跡マッピング

implementation report は次を記録する。

- baseline commands と結果を session log に記録する。
- 各 step の Red / Green / Refactor evidence を、該当する場合に記録する。
- Template pack adoption を Evidence Adoption Ledger に記録する。
- requirement / design / plan の変更判断を Spec Interpretation / Decision Ledger に記録する。
- review gates を Final Quality Gate に記録する。
- CLOS-001〜CLOS-009 の closure coverage を記録する。

## 8. 停止 / エスカレーション規則

即時停止条件:

- template を採用するには Issue requirement の意味を変更する必要がある。
- substantive user content を上書きしないと runtime が成立しない。
- `lite_candidate` が selection logic に現れる。
- design / plan templates を成立させるために `report.md` migration が必要になる。
- すべての candidates を検証する前に partial write が発生する。
- security / credential / destructive / GitHub mutation risk が現れる。

停止した場合は `report.md` を更新し、implementation を続ける前に requirement または design authoring へ戻る。

## 9. 承認チェックリスト

- [x] Requirement has fresh `spec-reviewer` pass.
- [x] Design has fresh `spec-reviewer` pass.
- [x] Plan has fresh `spec-reviewer` pass.
- [x] No blocking open question remains.
- [x] Execution remains one approved step at a time.
- [x] Reviewer gates and report evidence destinations are clear.
