---
種別: 要件定義書（Issue）
ID: "iss-00247"
タイトル: "Move Assurance Compose Scaffold Sources To Profile Markdown Templates"
関連GitHub: ["#247"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-29"
親: ["epic-00224", "init-local-00003"]
---

# iss-00247 Move Assurance Compose Scaffold Sources To Profile Markdown Templates — 要件定義

## 0. 文書の位置づけ

この Issue は、Issue planning artifact の初期本文を実質手作業で組み立てる状態を解消し、Assurance Profile / Issue Grade に応じた deterministic Markdown template を provider-side asset として持たせる。

この文書は、実現する成果、制約、受け入れ条件、grade 判定材料を定義する。template loader、parser、write ordering、test implementation の詳細は `design.md` / `plan.md` に委譲する。

## 1. 目的

`assurance compose` が生成する Issue-level `design.md` / `plan.md` scaffold source を、JSON string body から provider-side Markdown template files へ移す。

同時に、GPT-5.5 Pro が作成した Issue Grade Template Pack を採用し、共通 `requirement.md` template と `lite` / `standard` / `strict` / `critical` 用 `design.md` / `plan.md` templates を provider assets として扱える状態にする。

これにより、Issue planning artifact の本文を Markdown として直接 review / preview / diff でき、agent が毎回手作業で設計書・実装計画書を組み立てる状態を終わらせる。

また、template の title / heading が英語中心だと、agent がその文脈に引っ張られて本文まで英語で作成するリスクがある。そのため、今回採用する template は title 行、見出し、小見出し、説明本文を日本語優先に補正する。

## 2. 背景・現状

現在の挙動:

- 新規 Issue の `design.md` / `plan.md` は `artifact_state: awaiting-assurance-compose` を持つ placeholder として作成される。
- `assurance classify --stage requirement` が Issue-local `.assurance.json` を作成する。
- `assurance compose --artifact design|plan|report|all` が `authorized_profile` に応じて managed sections を materialize する。
- profile 別 section の heading / body は `src/spec_dock/assets/spec_dock/templates/assurance/profile-sections.json` に JSON string として定義されている。
- 現行 composer は marker conflict、substantive content no-overwrite、dry-run、changed paths、source binding update、path / symlink guard を持つ。

問題:

- `design.md` / `plan.md` は Markdown artifact なのに、profile-specific scaffold prose の source が JSON string に閉じ込められている。
- 現在の generated section は薄すぎ、実際には orchestrator が手動で設計書・実装計画書を組み立てる状態になっている。
- profile / grade ごとの計画密度が artifact source として見えず、PR review、差分確認、template quality improvement が難しい。
- 今回ユーザーが提供した ZIP は、まさにこの問題を解消するための template pack である。

採用する外部素材:

- `/Users/iwasawayuuta/.codex/attachments/ed533576-0494-4554-8480-1ea2c23320e0/spec-dock-issue-grade-templates.zip`
- 展開確認先: `/private/tmp/spec-dock-issue-grade-templates/spec-dock-issue-grade-templates/`
- 含まれる主要ファイル:
  - `src/spec_dock/assets/spec_dock/templates/issue/requirement.md`
  - `src/spec_dock/assets/spec_dock/templates/issue-profiles/lite/design.md`
  - `src/spec_dock/assets/spec_dock/templates/issue-profiles/lite/plan.md`
  - `src/spec_dock/assets/spec_dock/templates/issue-profiles/standard/design.md`
  - `src/spec_dock/assets/spec_dock/templates/issue-profiles/standard/plan.md`
  - `src/spec_dock/assets/spec_dock/templates/issue-profiles/strict/design.md`
  - `src/spec_dock/assets/spec_dock/templates/issue-profiles/strict/plan.md`
  - `src/spec_dock/assets/spec_dock/templates/issue-profiles/critical/design.md`
  - `src/spec_dock/assets/spec_dock/templates/issue-profiles/critical/plan.md`
  - `docs/template-matrix.md`
  - `docs/final-review.md`

## 3. Issue Grade

この Issue 自体は `strict` として扱う。

理由:

- provider-side scaffold / template contract を変更する。
- `assurance compose` の source resolution と validation behavior に影響する。
- workflow / skill / agent planning の実用性に影響する。
- 既存 workspace と新規 installed scaffold の互換性を確認する必要がある。
- `critical` 条件である secret、privacy、destructive deletion、GitHub mutation、forward-only migration は含まない。

Assurance runtime note:

- 現行 `assurance classify` は requirement 内の structured risk facts をまだ抽出せず、unknown defaults から `authorized_profile=standard` を返す場合がある。
- この Issue の実行義務は、runtime の `authorized_profile=standard` を下限として扱いつつ、scaffold / template contract 変更であるため issue-local planning gate と reviewer gate を `strict` 相当に引き上げる。
- この手動引き上げは、runtime template selection authority を変更しない。実装後の compose selection は引き続き `.assurance.json` の `authorized_profile` だけを使う。

## 4. Actor / Trigger / 利用シナリオ

主な actor:

- `spec-dock` maintainer。
- `assurance compose` を使う agent / orchestrator。
- Issue planning artifact を review する `spec-reviewer`。
- provider-side template を更新する future maintainer。

代表シナリオ:

- Maintainer が `issue-profiles/strict/design.md` を Markdown として読み、template quality を review する。
- `authorized_profile=standard` の Issue で `assurance compose --artifact all` を実行すると、Standard 用 `design.md` / `plan.md` が materialize される。
- `lite_candidate=true` でも `authorized_profile=standard` なら Lite template は選ばれない。
- `report.md` は既存 evidence ledger template と managed-section compose behavior を維持する。

## 5. スコープ

In scope:

- GPT-provided template pack を provider-side source として採用する。
- 共通 `src/spec_dock/assets/spec_dock/templates/issue/requirement.md` を template pack の構造に更新する。
- `src/spec_dock/assets/spec_dock/templates/issue-profiles/{lite,standard,strict,critical}/design.md` を追加する。
- `src/spec_dock/assets/spec_dock/templates/issue-profiles/{lite,standard,strict,critical}/plan.md` を追加する。
- template の title 行、見出し、小見出し、説明本文は原則として日本語で作成する。
- 日本語だけでは正確性が落ちる専門語、既存用語、command 由来の名称は、日本語表現を先に置き、括弧内に英語名を併記する。
- `assurance compose` が `authorized_profile` と artifact kind に基づいて profile Markdown template を選べるようにする。
- `design.md` / `plan.md` の prose authority を `profile-sections.json` から Markdown template files へ移す。
- JSON manifest を残す場合は、prose body authority ではなく inventory / validation / section id metadata に限定する。
- `--artifact all` では `design` / `plan` は Markdown template source、`report` は既存 managed-section source という mixed-mode を許容する。
- provider asset と dogfooding workspace / installed scaffold の parity を検証する。

Out of scope:

- `report.md` evidence ledger の全面 redesign。
- `assurance classify` の profile 判定ロジック変更。
- 既存 materialized Issue artifact を自動 refresh / rewrite する command。
- Step Assurance、agent routing、context policy の別機能実装。
- GitHub mutation、network dependency、credential access。

Must not change:

- `authorized_profile` だけが template selection authority である。
- `lite_candidate` は template selection や obligation reduction に使わない。
- user-authored substantive content を silent overwrite しない。
- missing / invalid template は artifact / contract write 前に fail-closed する。
- dry-run は artifact / contract を書かない。
- provider-side `src/spec_dock/assets/spec_dock/...` を source of truth とする。

## 6. 要求される振る舞い

### BH-001: Provider-side grade template pack adoption

Provider assets に、共通 requirement template と profile 別 design / plan template が配置される。

### BH-002: Markdown template source selection

`assurance compose` は `design` / `plan` について、`authorized_profile` と artifact kind から Markdown template source を選択する。

### BH-003: JSON prose authority removal

`profile-sections.json` または後継 manifest は、`design` / `plan` の長文 prose body authority を持たない。

### BH-004: Report compatibility

`report.md` は現行 evidence ledger lifecycle と append-oriented managed-section compose behavior を維持する。

### BH-005: Fail-closed template validation

template missing、invalid marker、wrong root、unsupported profile、unsupported artifact は write 前に explicit error として止まる。

### BH-006: Existing safety semantics preservation

placeholder materialization、substantive content conflict、marker conflict、idempotence、downgrade safety、dry-run、changed paths、source binding update を維持する。

### BH-007: テンプレート本文と言語の日本語優先

Issue template の title、見出し、小見出し、説明本文は日本語を主言語にする。英語の専門名が必要な場合は、日本語表現を先に置き、括弧で英語名を補足する。

## 7. 受け入れ条件

### AC-001: Template pack files are provider assets

`src/spec_dock/assets/spec_dock/templates/issue/requirement.md` と `src/spec_dock/assets/spec_dock/templates/issue-profiles/{lite,standard,strict,critical}/{design,plan}.md` が provider-side asset として存在し、installer / update の対象になる。

### AC-002: design / plan prose source is Markdown

`assurance compose --artifact design|plan|all` が `design.md` / `plan.md` を materialize するとき、profile-specific prose は Markdown template files から来る。

### AC-003: profile selection uses authorized_profile only

`.assurance.json` が `authorized_profile=standard` かつ `lite_candidate=true` の場合でも、Standard template が選択され、Lite template は使われない。

### AC-004: requirement template is updated

新規 Issue scaffold の common `requirement.md` template は、Issue Grade 判定材料、observable outcome、scope、AC、constraints、risk facts を記録できる構造になる。

### AC-005: report behavior remains compatible

`assurance compose --artifact report` と `--artifact all` で、`report.md` は既存 managed-section compose behavior を維持する。

### AC-006: missing / invalid template fails before writes

required template が missing、unreadable、invalid、root 外、または marker conflict を含む場合、artifact と `.assurance.json` は変更されない。

### AC-007: placeholder materialization preserves frontmatter

unedited awaiting-compose placeholder に compose すると、`artifact_state` は除去され、Issue-specific frontmatter / metadata は保持され、選択された Markdown template body が入る。

### AC-008: substantive content is not overwritten

`design.md` / `plan.md` に substantive non-placeholder content がある場合、silent overwrite せず explicit conflict または no-op になる。

### AC-009: idempotence and downgrade safety remain

二回目 compose は unchanged になり、強い profile で追加済みの既存 managed sections は弱い profile compose で自動削除されない。

### AC-010: dry-run and changed_paths remain accurate

dry-run は intended changes を報告するが書かない。real compose は変更した artifact だけを `changed_paths` に出す。

### AC-011: planning source binding update remains correct

real compose が planning artifact を変更した場合のみ `.assurance.json` の planning source binding が更新される。

### AC-012: installed scaffold parity is tested

provider-side assets を install / update した target repo で、template files、placeholder flow、compose output が期待どおり確認できる。

### AC-013: テンプレート見出しと本文は日本語優先である

追加・更新される `requirement.md` と profile 別 `design.md` / `plan.md` templates は、title 行、見出し、小見出し、説明本文が日本語優先である。英語だけの見出しや、英語見出しに引っ張られた英語本文を残さない。必要な英語名は、日本語表現の後に括弧で併記する。

## 8. 例外・エッジケース

| ID | 条件 | 期待 |
|---|---|---|
| EC-001 | profile template file missing | write 前に fail-closed |
| EC-002 | profile template root 外参照 | write 前に fail-closed |
| EC-003 | unknown profile | unsupported profile として fail |
| EC-004 | template marker duplicate / unclosed / malformed / mismatched | fail-closed |
| EC-005 | target artifact has substantive content | silent overwrite しない |
| EC-006 | `--artifact all` で design は valid、plan は invalid | どの artifact も write しない |
| EC-007 | `lite_candidate=true` かつ `authorized_profile=standard` | Standard template を選ぶ |
| EC-008 | existing report compose tests | regression しない |

## 9. 制約

- CON-001: Provider-side assets are source of truth.
- CON-002: Runtime compose must be local and deterministic.
- CON-003: Template selection authority is `authorized_profile`.
- CON-004: Template files must be inspectable Markdown.
- CON-005: Prose authority for `design` / `plan` must not be duplicated in JSON.
- CON-006: `report.md` migration is deferred.
- CON-007: Existing user-authored artifact protection remains mandatory.
- CON-008: Template prose and headings は日本語優先である。英語だけの heading は、code identifiers、commands、file names、API names、または意味を損なわずに翻訳できない既存 product terms に限って許容する。

## 10. 依存関係

前提:

- Existing `assurance classify` / `.assurance.json` contract exists.
- Existing `assurance compose` placeholder and managed-section safety behavior exists.
- Existing installer / update tests cover provider asset copying.

影響対象:

- `src/spec_dock/assets/spec_dock/templates/issue/requirement.md`
- `src/spec_dock/assets/spec_dock/templates/issue/design.md`
- `src/spec_dock/assets/spec_dock/templates/issue/plan.md`
- `src/spec_dock/assets/spec_dock/templates/issue-profiles/**`
- `src/spec_dock/assets/spec_dock/templates/assurance/profile-sections.json`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/artifact_composer.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/artifact_store.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/assurance.py`
- Runtime / installer / CLI tests.

## 11. 設計判断の解決状況

Blocking open questions: none.

Resolved design decisions:

- Q-001: profile Markdown template は full body として読める source file とし、compose safety のため managed section marker validation / preservation を許容する。Design: DES-007。
- Q-002: `profile-sections.json` は `report.md` legacy managed-section source または metadata-only manifest とし、`design` / `plan` prose authority から外す。Design: DES-004。
- Q-003: `.assurance.json` の current source binding behavior は維持し、template source path / hash provenance はこの Issue の必須要件にしない。Design: DES-008。
- Q-004: template pack の common requirement template は provider-side `templates/issue/requirement.md` として採用する。Design: DES-001、Plan: S01。
- Q-005: template title / headings / prose は日本語優先とし、必要な英語名は日本語表現の後に括弧併記する。Design: DES-010、Plan: CLOS-009 / S01 / S90。

## 12. 完了条件

- AC-001 から AC-013 までが検証されている。
- `requirement.md` / `design.md` / `plan.md` が fresh `spec-reviewer` pass を持つ。
- `report.md` に template pack 採用、設計判断、実装証跡、reviewer gate が記録されている。
- 実装後に relevant unit / CLI / installer tests が pass している。
