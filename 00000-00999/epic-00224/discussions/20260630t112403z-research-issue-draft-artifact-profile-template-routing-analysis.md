---
種別: research
ID: "20260630t112403z-research"
タイトル: "Issue Draft Artifact Profile Template Routing Analysis"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-06-30"
親: ["epic-00224"]
関連:
  - "iss-00247"
  - "20260630t111316z-adr"
authority: "synthesized"
derived_from:
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/assurance.py"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/artifact_store.py"
  - "src/spec_dock/assets/spec_dock/templates/issue/design.md"
  - "src/spec_dock/assets/spec_dock/templates/issue/plan.md"
  - "src/spec_dock/assets/spec_dock/templates/issue-profiles/{lite,standard,strict,critical}/{design,plan}.md"
  - "spec-dock/docs/rules/issue/discussions.md"
  - "spec-dock/docs/phase_design.md"
  - "tests/cli_runtime/test_new.py"
  - "tests/cli_runtime/test_assurance_compose.py"
  - "consultant analysis: Huygens"
reflected_to: []
---

# 20260630t112403z-research Issue Draft Artifact Profile Template Routing Analysis

## 位置づけ
この artifact は、`spec-dock new doc draft-requirement|draft-design|draft-plan` が、Issue #247 で導入した grade 別 Issue design / plan template pack と整合しているかを調査した report である。

結論として、`new doc draft-*` コマンド自体は機能している。しかし Issue scope の `draft-design` / `draft-plan` は、`templates/issue-profiles/<profile>/{design,plan}.md` を使っていない。現行実装は `templates/issue/{design,plan}.md` の compose 前 placeholder を読み、placeholder marker を削ったうえで薄い独自本文へ正規化している。

これは、Issue #247 後の grade-aware authoring 方針、および `20260630t111316z-adr Grade-Aware Issue Authoring Rules` と不整合である。

## 調査目的

- `new doc draft-design` / `new doc draft-plan` が現在も機能しているか。
- それらが Issue の `authorized_profile` に応じた grade-specific template を使っているか。
- 使っていない場合、どのコード経路が原因か。
- 後続 Issue としてどのような修正を行うべきか。

## 調査方法

- `rg` で `draft-requirement` / `draft-design` / `draft-plan` / `issue-profiles` / `assurance compose` の参照を検索した。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py` の `new doc` 実装を確認した。
- `assurance compose` の grade profile template 読み込み経路を確認した。
- provider-side template と dogfooding docs / tests の記述を確認した。
- Consultant `Huygens` に read-only 分析を依頼し、ローカル調査と突き合わせた。

## 観測できた事実

### F-001: `new doc draft-*` の doc type は現在も存在する

`CreateDiscussionDocRequest.doc_type` には `draft-requirement` / `draft-design` / `draft-plan` が含まれている。

`spec-dock new doc --help` でも、discussion doc type として `draft-requirement`、`draft-design`、`draft-plan` が表示される。

### F-002: draft doc は canonical scope template を直接 source としている

`create_node.py` は draft doc type を canonical artifact 名へ変換する。

```text
_DRAFT_TARGET_BY_DOC_TYPE = {
    "draft-requirement": "requirement",
    "draft-design": "design",
    "draft-plan": "plan",
}
```

根拠: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py:52-55`

template path の解決は次の通りである。

```text
return specdock_dir / "templates" / scope_kind / f"{target}.md"
```

根拠: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py:1222-1226`

つまり Issue scope の `draft-design` は `spec-dock/templates/issue/design.md`、`draft-plan` は `spec-dock/templates/issue/plan.md` を読む。`issue-profiles/<profile>` は参照しない。

### F-003: Issue の canonical design / plan template は compose 前 placeholder である

provider-side `templates/issue/design.md` / `templates/issue/plan.md` は、`artifact_state: awaiting-assurance-compose` を持ち、「このファイルはまだ合成されていません」と明記している。

これらは手動 authoring の開始点ではなく、`assurance classify --stage requirement` と `assurance compose --artifact all` を促す placeholder である。

根拠:

- `src/spec_dock/assets/spec_dock/templates/issue/design.md`
- `src/spec_dock/assets/spec_dock/templates/issue/plan.md`
- `spec-dock/docs/phase_design.md`

### F-004: draft 生成は placeholder を grade template に置き換えず、薄い独自本文へ正規化している

`_normalize_draft_discussion_text()` は `artifact_state: awaiting-assurance-compose` を見つけると、その marker を削除し、`draft-design` / `draft-plan` を独自の最小本文へ差し替える。

`draft-design` は `## 目的・制約` と `## 採用方針 / トレードオフ` だけを持つ。

`draft-plan` は `## 計画（Issue と実施順序）` と `## 検証` だけを持つ。

根拠: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py:1229-1257`

これは `lite / standard / strict / critical` の profile template materialization ではない。

### F-005: `assurance compose` は grade-specific template を正しく使う別経路を持つ

`ArtifactStore.load_profile_artifact_template()` は `spec-dock/templates/issue-profiles/<profile>/<artifact>.md` を読む。

根拠: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/artifact_store.py:72-96`

`compose_assurance()` は `.assurance.json` の `contract.classification.authorized_profile.value` を使い、design / plan の profile template を読み込む。

根拠: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/assurance.py:116-138`

`tests/cli_runtime/test_assurance_compose.py` は、`assurance compose` 後に Standard design / plan template が materialize されることを確認している。

### F-006: 既存テストは draft doc の旧挙動を期待している

`tests/cli_runtime/test_new.py` は `new doc draft-design --issue` の source を `templates/issue/design.md` として期待している。

根拠: `tests/cli_runtime/test_new.py` の `test_new_doc_creates_draft_artifacts_from_scope_specific_templates`

したがって現行テストは、Issue draft が grade-specific template と接続されていない問題を検出しない。むしろ旧挙動を固定している。

## Consultant 所見

Consultant `Huygens` の read-only 分析も、次の点でローカル調査と一致した。

- `new doc draft-design` / `draft-plan` は機械的には動作する。
- Issue scope では `templates/issue/design.md` / `templates/issue/plan.md` を入口にしており、`templates/issue-profiles/{lite,standard,strict,critical}` を使っていない。
- `_normalize_draft_discussion_text()` により placeholder 感だけが消え、profile 非対応の薄い draft が「それらしく」見える。
- classified Issue の draft design / plan は、`authorized_profile` に基づく profile template を使うべきである。
- unclassified / missing `.assurance.json` の挙動は明示的に固定すべきである。

## 推測 / 判断

### I-001: ユーザー懸念は妥当である

要件定義書 draft は `templates/issue/requirement.md` を source としてよい。一方で Issue design / plan は、Issue #247 以後は `templates/issue/{design,plan}.md` が compose 前 placeholder に変わっている。

したがって、`new doc draft-design` / `new doc draft-plan` がこの placeholder を source とする現行挙動は、grade-aware template pack 導入後の期待とずれている。

### I-002: 失敗は「placeholder がそのまま出る」よりも紛らわしい

実装上は placeholder marker を削除し、簡易本文に置き換えるため、出力は完全な placeholder には見えない。

しかし内容は `standard` / `strict` / `critical` template の見出し、gate、review evidence、commit / validation gate を含まない。よって delegated specialist がこの draft を使うと、canonical compose 後の設計書 / 実装計画書構造とズレる。

### I-003: この問題は G1/G2/G3 の前提不備として扱うべきである

`20260630t111316z-adr` では、grade-aware authoring rules を Epic 上流設計として固定した。`new doc draft-design` / `draft-plan` が grade-specific template を使わないままだと、delegated specialist role routing と evidence gate が古い薄い draft に引きずられる。

よって、この修正は G1 / G2 / G3 のどこかに吸収するより、R0 後または G1 の一部として明示的な sub-scope にするべきである。

## 影響

| 対象 | 影響 |
|---|---|
| Delegated design authoring | `system-architect` が grade-specific design template ではなく薄い draft を使う可能性がある。 |
| Delegated plan authoring | `implementation-planner` が Standard / Strict / Critical の milestone / behavior / validation / safety gate を持たない draft から計画する可能性がある。 |
| Spec reviewer | reviewer が grade-specific template 構造ではなく薄い draft を review する可能性がある。 |
| Tests | `test_new.py` が旧 source template を期待しており、profile 非対応を固定している。 |
| Docs | `rules/issue/discussions.md` の「canonical template を直接 source として render」が、Issue design / plan については現行方針と衝突している。 |

## 修正方針候補

### Option A: Issue `draft-design` / `draft-plan` を `.assurance.json` の `authorized_profile` に基づく profile template から生成する

- 内容:
  - Issue scope の `draft-design` / `draft-plan` だけ特別扱いする。
  - `.assurance.json` を読み、`authorized_profile` を取得する。
  - `templates/issue-profiles/<authorized_profile>/{design,plan}.md` を source として render する。
- 良い点:
  - canonical compose 後の artifact と同じ grade template 構造を delegated draft に使える。
  - `20260630t111316z-adr` の grade-aware authoring rules と整合する。
- 注意点:
  - 未分類 Issue では draft 生成の扱いを決める必要がある。

### Option B: 未分類 Issue では `draft-design` / `draft-plan` を fail-closed にする

- 内容:
  - `.assurance.json` がない、または invalid / stale の場合は draft 生成を拒否し、先に `assurance classify --stage requirement` と `assurance compose --artifact all` を促す。
- 良い点:
  - 古い placeholder / 薄い draft で設計・計画を始める事故を避けられる。
- 注意点:
  - 初期構想段階の free-form discussion draft を作りたい場合は `disc` / `research` を使う必要がある。

### Option C: 未分類用の explicit unclassified draft template を別に用意する

- 内容:
  - profile template ではないことが明確な `unclassified` draft template を追加する。
  - ただし design / plan の正式 draft ではなく、classification 前の論点整理として扱う。
- 良い点:
  - early thinking の置き場を残せる。
- 注意点:
  - `draft-design` / `draft-plan` という名前と混ざるため、誤用リスクがある。

## 推奨

推奨は Option A + Option B である。

- classified Issue:
  - `draft-design` / `draft-plan` は `authorized_profile` に対応する `templates/issue-profiles/<profile>/{design,plan}.md` を使う。
- unclassified / invalid / stale Issue:
  - `draft-design` / `draft-plan` は fail-closed にし、先に requirement concretization、classification、compose を求める。
- requirement draft:
  - `draft-requirement` は従来通り `templates/issue/requirement.md` を source としてよい。
- free-form thinking:
  - classification 前の設計論点整理は `disc` / `research` を使う。

## テスト観点

- classified standard Issue で `new doc draft-design --issue <id>` が `Issue 設計書（Standard）` を含む。
- classified standard Issue で `new doc draft-plan --issue <id>` が `Issue 実装計画書（Standard / TDD）` と Standard 固有 section を含む。
- strict / critical の `.assurance.json` fixture で、それぞれの profile template が使われる。
- missing `.assurance.json` の Issue で `draft-design` / `draft-plan` が fail-closed になる。
- stale / invalid `.assurance.json` の Issue で `draft-design` / `draft-plan` が fail-closed になる。
- initiative / epic の `draft-design` / `draft-plan` は従来通り scope canonical template を source としてよい。
- `draft-requirement` は Issue でも従来通り common requirement template を使う。
- `tests/cli_runtime/test_new.py` の旧期待値 `templates/issue/design.md` / `templates/issue/plan.md` は、Issue design / plan について更新する。

## 未検証事項

- 実際に `new doc draft-design --issue` を dogfooding issue に対して実行する確認は行っていない。理由は不要な discussion artifact を増やさないため。
- ただし、該当コード経路と既存テストにより、Issue draft design / plan が `issue-profiles` を参照しないことは確認できている。

## 反映先候補

- Epic #224 `requirement.md`:
  - Grade-aware authoring rules の acceptance criteria に、discussion draft design / plan も profile template を使うことを追加する。
- Epic #224 `design.md`:
  - Grade-Aware Authoring Router に `new doc draft-design` / `draft-plan` の profile-aware template routing を追加する。
- Epic #224 `plan.md`:
  - G1 または新規 sub-scope として `new doc draft-design/draft-plan profile routing` を明示する。
- 実装 Issue:
  - R0 後、G1 の一部、または G1 の前段小 Issue として扱う。
