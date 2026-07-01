---
種別: 設計書（Issue）
ID: "iss-00250"
タイトル: "Route Issue Draft Design And Plan Through Profile Templates"
関連GitHub: ["#250"]
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-30"
依存: ["requirement.md"]
親: ["epic-00224", "init-local-00003"]
Issue Grade: "strict"
authorized_profile: "standard"
manual_escalation: "strict"
---

# iss-00250 Route Issue Draft Design And Plan Through Profile Templates — Issue 設計書

## 1. 設計方針

この Issue は、Issue scope の `new doc draft-design` / `new doc draft-plan` を、`.assurance.json` の `authorized_profile` に対応する grade 別 profile template へ接続する。

Runtime classification は現時点で `authorized_profile=standard` を返しているが、変更対象は CLI / runtime / template / delegated authoring workflow の境界に触れる。そのため、この Issue の authoring と review は `20260630t111316z-adr Grade-Aware Issue Authoring Rules` に従い、manual escalation として strict 相当で扱う。

設計の中心は、`new doc` の discussion draft 生成を `assurance compose` と同じ profile template authority に揃えることである。`assurance compose` は canonical `design.md` / `plan.md` を更新する。一方、`new doc draft-design` / `draft-plan` は discussion draft だけを作る。両者の出力先は違うが、Issue design / plan の source template authority は同じでなければならない。

## 2. 採用する設計契約

- DES-001 `[N]`: Issue scope の `draft-design` は、valid な `.assurance.json` の `classification.authorized_profile` に対応する `templates/issue-profiles/<profile>/design.md` を source とする。
- DES-002 `[N]`: Issue scope の `draft-plan` は、valid な `.assurance.json` の `classification.authorized_profile` に対応する `templates/issue-profiles/<profile>/plan.md` を source とする。
- DES-003 `[N]`: profile selection は `authorized_profile` だけを使う。`lite_candidate`、frontmatter の `Issue Grade`、コマンド title、暗黙 default は profile selection authority にしない。
- DES-004 `[N]`: missing / invalid / stale `.assurance.json`、unsupported profile、missing template、non-file template、symlink escape、empty template は discussion file write 前に fail-closed とする。
- DES-005 `[N]`: Issue scope の `draft-requirement` は従来通り `templates/issue/requirement.md` を source とし、`.assurance.json` を要求しない。
- DES-006 `[N]`: Initiative / Epic scope の `draft-design` / `draft-plan` は従来通り `templates/{initiative,epic}/{design,plan}.md` を source とする。
- DES-007 `[N]`: `new doc draft-design` / `draft-plan` は canonical `design.md` / `plan.md` を変更しない。書き込み先は対象 scope の `discussions/` 直下の timestamped Markdown 1 件だけである。
- DES-008 `[N]`: generated discussion draft は canonical authority を自己主張しない。`authority: accepted`、`adoption_status: adopted`、non-empty `reflected_to`、reviewer pass、phase completion を設定しない。
- DES-009 `[P]`: profile template の path / text 読み込みは、`ArtifactStore` の validation logic を再利用または抽出して、`assurance compose` と `new doc` の filesystem guard を重複させない。

## 3. 現状設計と問題

現在の `create_node.py` は、`draft-design` / `draft-plan` を canonical artifact 名へ変換し、`spec-dock/templates/<scope_kind>/<artifact>.md` を読む。

| doc type | Issue scope の現 source | 問題 |
|---|---|---|
| `draft-requirement` | `templates/issue/requirement.md` | 問題なし。Issue requirement は共通 template でよい。 |
| `draft-design` | `templates/issue/design.md` | 現在は compose 前 placeholder であり、grade 別 design template ではない。 |
| `draft-plan` | `templates/issue/plan.md` | 現在は compose 前 placeholder であり、grade 別 plan template ではない。 |

さらに `_normalize_draft_discussion_text()` は `artifact_state: awaiting-assurance-compose` を削除し、薄い独自本文へ置き換える。そのため、出力は placeholder には見えないが、Standard / Strict / Critical の gate や review evidence を持たない draft になる。

## 4. 目標データフロー

### 4.1 成功フロー

```text
spec-dock new doc draft-design --issue iss-XXXXX
  -> scope node を issue として解決
  -> doc_type が draft-design / draft-plan か判定
  -> issue target を解決
  -> .assurance.json を verify
  -> contract.classification.authorized_profile を取得
  -> templates/issue-profiles/<profile>/<artifact>.md を検証付きで読む
  -> discussion doc 用 replacements を適用
  -> discussions/<timestamp>-draft-<artifact>-<slug>.md にだけ書き込む
```

### 4.2 失敗フロー

```text
spec-dock new doc draft-plan --issue iss-XXXXX
  -> .assurance.json verify が missing / invalid / stale
  -> RuntimeError
  -> no discussion file write
  -> operator に requirement concretization / assurance classify / compose or verify を促す
```

## 5. 責任分担

| モジュール | 現責務 | 変更後の責務 |
|---|---|---|
| `commands/new.py` | CLI 入力を `CreateDiscussionDocRequest` に変換する。 | 原則変更しない。 |
| `application/create_node.py` | scope 解決、template path 選択、discussion filename allocation、render/write を行う。 | Issue `draft-design` / `draft-plan` の profile-aware routing を orchestration する。 |
| `infra/assurance_store.py` | `.assurance.json` の read / schema / source binding / stale 判定を持つ。 | draft routing の contract verification authority として使う。 |
| `infra/artifact_store.py` | `issue-profiles/<profile>/<artifact>.md` の validation と body 読み込みを持つ。 | profile template の full text または reusable template source を提供する。 |
| `infra/template_scaffolder.py` | template の render / write を行う。 | 既存責務を維持する。 |
| `tests/cli_runtime/test_new.py` | `new doc` の CLI 挙動を固定する。 | Issue `draft-design` / `draft-plan` が profile template を使うことと fail-closed を固定する。 |

## 6. Interface / Contract Delta

| 対象 | 変更 |
|---|---|
| CLI success shape | 維持。成功時は従来通り `spec-dock: ok (new doc) ... path=...` を返す。 |
| CLI failure | Issue `draft-design` / `draft-plan` に valid contract がない場合は non-zero で失敗する。 |
| `CreateDiscussionDocRequest` | 変更しない想定。 |
| discussion filename | 維持。timestamp + doc type + slug の既存規約を使う。 |
| canonical artifacts | `new doc` では変更しない。 |
| profile selection | `.assurance.json` の `authorized_profile` を唯一の selection authority とする。 |

## 7. Failure / Edge Design

| Failure ID | 条件 | 期待判定 | 書き込み |
|---|---|---|---|
| FAIL-001 | `.assurance.json` missing | fail-closed | なし |
| FAIL-002 | `.assurance.json` invalid JSON / invalid schema | fail-closed | なし |
| FAIL-003 | source binding stale | fail-closed | なし |
| FAIL-004 | profile template missing / empty / non-file | fail-closed | なし |
| FAIL-005 | profile template symlink escape | fail-closed | なし |
| FAIL-006 | unsupported profile name | fail-closed | なし |
| FAIL-007 | `draft-requirement` without contract | success | discussion draft 1 件 |
| FAIL-008 | Initiative / Epic `draft-design` / `draft-plan` without contract | success | discussion draft 1 件 |

Failure message は、少なくとも対象 Issue、doc type、contract / template failure reason、次に実行すべき分類 / compose / verify の導線を含む。

## 8. 採用しない方針

| 方針 | 採用しない理由 |
|---|---|
| `templates/issue/design.md` / `plan.md` から薄い draft を作り続ける | Grade-aware authoring rules と矛盾し、delegated specialist が canonical compose 後と違う構造で作業する。 |
| `.assurance.json` missing 時に Standard template へ fallback する | `authorized_profile` authority と Lite automatic default 禁止に反する。 |
| `Issue Grade` frontmatter を profile selection authority にする | manual escalation と runtime authority を混同する。 |
| `unclassified` profile template を追加する | `draft-design` / `draft-plan` が分類後 artifact の draft であることを曖昧にする。分類前の論点整理は `disc` / `research` を使う。 |

## 9. 文書・テスト影響

- `tests/cli_runtime/test_new.py` の `test_new_doc_creates_draft_artifacts_from_scope_specific_templates` は、Issue `draft-design` / `draft-plan` だけ期待 source を更新する。
- classified Standard / Strict / Critical Issue の draft design / plan が profile 見出しを含む test を追加する。
- missing / invalid / stale `.assurance.json` で discussion file が作られない test を追加する。
- `src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md` の「canonical template を直接 source として render」は、Issue design / plan では profile template を source とするよう補正する。
- dogfooding mirror `spec-dock/docs/rules/issue/discussions.md` も provider asset と整合させる。

## 10. 検証への含意

| Design ID | 検証 |
|---|---|
| DES-001 | Standard / Strict / Critical の `draft-design` CLI tests。 |
| DES-002 | Standard / Strict / Critical の `draft-plan` CLI tests。 |
| DES-004 | missing / invalid / stale contract の no-write tests。 |
| DES-005 | Issue `draft-requirement` の既存 success test。 |
| DES-006 | Initiative / Epic draft design / plan の既存 success test。 |
| DES-009 | profile template validation guard の既存 compose tests と必要な unit / CLI tests。 |

Focused verification は次を基本とする。

```bash
uv run pytest tests/cli_runtime/test_new.py tests/cli_runtime/test_assurance_compose.py
```

## 11. Plan Handoff

実装計画では、次の順に閉じる。

1. 既存 `new doc draft-*` tests を読み、profile-aware Issue draft routing の Red を追加する。
2. contract verification と profile template source resolution を `create_node.py` へ導入する。
3. missing / invalid / stale contract の fail-closed と no-write を固定する。
4. provider docs と dogfooding docs を更新する。
5. focused CLI tests と必要な regression tests を実行する。

Stop / replan triggers:

- `.assurance.json` verification API が `create_node.py` から安全に利用できない。
- profile template validation を `assurance compose` と共有できず、filesystem guard が重複・不整合になる。
- existing discussion draft compatibility を壊す必要が出る。
- public CLI output shape の変更が必要になる。

## 12. 委任ドラフト採用

この設計は `system-architect` delegated draft `discussions/20260630t124012z-disc-system-architect-design-draft.md` を採用して main orchestrator が統合した。

採用した内容:

- Issue `draft-design` / `draft-plan` を `authorized_profile` profile template へ route する設計。
- missing / invalid / stale contract の fail-closed。
- `draft-requirement` と Initiative / Epic draft の既存挙動維持。
- tests / docs 更新方針。

採用しなかった内容:

- 新しい shipped role skill 追加に関する拡張は、この Issue の scope ではないため含めない。
