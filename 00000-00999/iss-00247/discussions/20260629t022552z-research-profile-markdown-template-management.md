---
種別: research
ID: "20260629t022552z-research-profile-markdown-template-management"
タイトル: "Issue profile 別 design / plan template 管理方式の分析"
作成者: "Codex"
作成日: "2026-06-29"
対象: ["iss-00247", "assurance compose", "issue templates"]
状態: "draft"
---

# Issue profile 別 design / plan template 管理方式の分析

## 目的

`lite` / `standard` / `strict` / `critical` の Issue Quality Profile に応じて、`design.md` と `plan.md` の scaffold / template をどのように管理するべきかを分析する。

特に、現行の `profile-sections.json` と Python code による動的 section 合成が、将来のテンプレート変更・レビュー・dogfooding 運用に対して適切かを検討する。

この research は `iss-00244` の実装完了直後に発見した設計課題を、follow-up issue `iss-00247` の初期分析として移管したものである。

## 調査対象

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/artifact_composer.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/assurance.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/artifact_store.py`
- `src/spec_dock/assets/spec_dock/templates/assurance/profile-sections.json`
- `src/spec_dock/assets/spec_dock/templates/issue/design.md`
- `src/spec_dock/assets/spec_dock/templates/issue/plan.md`
- `tests/cli_runtime/test_assurance_compose.py`
- `tests/cli_runtime/test_new.py`
- `spec-dock/active/issue/requirement.md`
- `spec-dock/active/issue/design.md`
- `spec-dock/active/issue/plan.md`

## 現状

新規 Issue の `design.md` / `plan.md` は、実体テンプレートではなく `artifact_state: awaiting-assurance-compose` を持つ placeholder として作成される。

その後、`assurance classify --stage requirement` によって Issue-local `.assurance.json` が作成され、`assurance compose --artifact all` が `authorized_profile` に応じた planning section を `design.md` / `plan.md` / `report.md` に合成する。

profile 別の scaffold 本文は `src/spec_dock/assets/spec_dock/templates/assurance/profile-sections.json` に JSON string として定義されている。たとえば `standard.plan` は `plan.step-contract` を参照し、`strict.plan` は `plan.step-contract` と `plan.strict-review` を参照する。

`artifact_composer.py` は managed marker を scan し、足りない section だけを append する。placeholder の場合は `artifact_state: awaiting-assurance-compose` を除去し、`状態: "draft"` を `状態: "approved"` に変換する。すでに実質的な本文がある場合や marker conflict がある場合は fail-closed する。

既存 test は次を固定している。

- 新規 Issue の `design.md` / `plan.md` は compose 待ち placeholder になる。
- compose 後は managed section が materialize される。
- 二回目の compose は `unchanged` になる。
- substantive content や marker conflict がある場合は上書きしない。
- `lite_candidate` だけでは Lite 権限にしない。

## 問題意識

現行方式は machine-readable で一見きれいだが、profile 別の design / plan scaffold は本質的に人間と agent が読む Markdown 文書である。

今後、次のような変更は高い確率で発生する。

- Lite の template をもっと軽くする。
- Standard の `plan.md` に標準的な step closure table を追加する。
- Strict / Critical に reviewer gate、rollback、evidence ledger、manual test obligation を追加する。
- 日本語の説明、表、チェックリスト、サンプル section を調整する。

このとき、Markdown prose が JSON string に埋まっていると、編集・preview・レビュー・差分確認が難しくなる。profile 別の完成形を見るには、`profiles` の section id list と `sections` の body を頭の中で合成する必要がある。

これは、SpecDock が dogfooding している「agent が source of truth を読みやすくする」という方向と緊張する。

## 外部分析

### Deep Consultant の分析

Deep Consultant は、長期的には `authorized_profile` に応じて profile / artifact 別の Markdown body template を読む方式へ寄せることを推奨した。

一方で、`design.md` / `plan.md` を丸ごと無条件に上書きする方式は非推奨であり、現行の `managed-section` / idempotency / fail-closed / source binding 更新の安全機構は維持するべきだと判断した。

scope 判断としては、`iss-00244` はすでに plan-centric hard cutover、`.assurance.json` rename、PR observation repair を含み大きいため、JSON manifest から Markdown template への全面移行は follow-up issue に分けるのが安全、という見解だった。

短期的に `iss-00244` で行うべきことは、現行 `profile-sections.json` の scaffold を必要最小限厚くして AC-005 / AC-006 を満たすことだとされた。

### ChatGPT GPT-5.5 Pro Extended の分析

ChatGPT は `Markdown-template-first hybrid` を推奨した。

具体的には、profile-specific な `design.md` / `plan.md` scaffold body を `profile-sections.json` から明示的な Markdown files に移し、Python には小さな selector / index layer だけを残す案である。

ChatGPT も、現行の fail-closed materialization、安全な placeholder 判定、dry-run、changed path reporting は維持するべきだとした。

scope 判断は Deep Consultant と少し異なり、`iss-00244` がまだ merge 前なら、現在の placeholder + compose behavior を導入している issue 内で design / plan の template-file shift まで入れる価値がある、という見解だった。ただし、profile wording の高度化、`report.md` parity、既存 scaffold refresh command は follow-up とするべきだとされた。

## 選択肢比較

### 選択肢 A: 現行 JSON section manifest を継続する

利点:

- section reuse がしやすい。
- `standard` に section を足して `strict` / `critical` を構成する additive model は表現しやすい。
- machine-readable なため、unknown section、wrong artifact、marker conflict を検出しやすい。
- 既存実装と test contract がすでに揃っており、短期変更コストは低い。

欠点:

- Markdown scaffold が JSON string に閉じ込められ、編集・preview・PR review が悪い。
- profile 別の完成形が見えない。
- human / agent-facing artifact の source が Markdown ではなく JSON であるため、dogfooding 上の見通しが悪い。
- template を厚くするほど escaped newline や body string が読みづらくなる。
- `artifact_kinds` のように manifest と Python 側の authority が二重化しやすい。

評価:

短い invariant section や append-only report evidence には許容できる。しかし、`design.md` / `plan.md` の主 scaffold source として長期運用するには保守性が低い。

### 選択肢 B: profile / artifact 別 Markdown file を丸ごと copy する

利点:

- `standard/plan.md`、`strict/design.md` のように、profile 別完成形をそのまま読める。
- Markdown の表、チェックリスト、見出し、日本語説明を自然に編集できる。
- PR diff が普通の Markdown diff になる。
- agent-facing artifact と template source の形式が一致する。

欠点:

- 共通 section が profile 間で重複し、文言 drift が起き得る。
- full-file replacement にすると Issue-specific frontmatter を壊しやすい。
- 既存の「実質本文がある場合は上書きしない」「既存 managed section を preserve する」安全性を壊しやすい。
- profile 再分類後に自動上書きすると、agent / human が書いた design / plan を破壊し得る。

評価:

単純だが、丸ごと copy / replace は危険である。特に `design.md` / `plan.md` は compose 後に human / agent が編集する一次文書になるため、再 compose による上書きは避けるべきである。

### 選択肢 C: Markdown-template-first hybrid

概要:

- `templates/issue/design.md` / `templates/issue/plan.md` は現行の pre-classification placeholder として残す。
- profile 別 Markdown body template を追加する。
- `assurance compose` は `authorized_profile` と artifact kind に応じて Markdown body template を読み込む。
- Python は profile 解決、template path 解決、placeholder 判定、frontmatter preserve、safe write、dry-run、source binding 更新に責務を限定する。
- full overwrite はしない。
- substantive content / marker conflict / stale source binding は現行と同じく fail-closed する。

候補 layout:

```text
src/spec_dock/assets/spec_dock/templates/
  issue/
    design.md
    plan.md
  assurance/
    profiles/
      lite/
        design.md
        plan.md
      standard/
        design.md
        plan.md
      strict/
        design.md
        plan.md
      critical/
        design.md
        plan.md
```

必要なら、prose を持たない小さな index だけを置く。

```text
src/spec_dock/assets/spec_dock/templates/assurance/profile-templates.json
```

ただし、profile と artifact の組み合わせが 4 x 2 程度であれば、`profiles/{profile}/{artifact}.md` という convention-only でも足りる。

評価:

この案が最もバランスがよい。ユーザーが懸念している template 編集性を満たしつつ、現行実装が持つ fail-closed / idempotency / source binding の安全性を維持できる。

## 推奨方針

採用すべき長期方針は `Markdown-template-first hybrid` である。

理由:

- `design.md` / `plan.md` は user / agent-facing の Markdown artifact であり、その scaffold source も Markdown である方が自然である。
- Profile 別 template は将来頻繁に調整される可能性が高く、JSON string に prose を閉じ込めると変更コストが増える。
- profile 数と artifact 数は少なく、Markdown file の重複は許容範囲である。
- ただし full replacement は危険なので、現行の placeholder guard、substantive content fail-closed、source binding、dry-run / changed paths reporting は維持する。
- dynamic composition の責務を「template prose の合成」ではなく「どの template を安全に materialize するか」に縮小できる。

## 推奨する target behavior

`assurance compose --artifact design|plan|all` は次のように振る舞う。

1. `.assurance.json` を verify し、`authorized_profile` を取得する。
2. 対象 artifact が unedited awaiting-compose placeholder か確認する。
3. `templates/assurance/profiles/{authorized_profile}/{artifact}.md` を読む。
4. 既存 frontmatter から `artifact_state: awaiting-assurance-compose` を削除し、現行 contract に従って state を更新する。
5. profile Markdown body template を materialize する。
6. `.assurance.json` の planning source binding を更新する。
7. すでに substantive content がある場合は、silent overwrite せず invalid / conflict を返す。

二回目以降の compose は、すでに materialized 済みで変更不要なら `unchanged` とするか、あるいは `already_materialized` として no-op にする。profile 再分類による自動差し替えは行わない。

## iss-00247 で取り組む理由

`iss-00244` はすでに merge 済みであり、`assurance compose` の現行挙動も一度 main に入っている。したがって、この research の対象は `iss-00247` で独立して扱う。

判断は二段階に分ける。

### 設計判断としては独立 issue 化が妥当

この変更は `artifact_composer.py`、`artifact_store.py`、templates、CLI tests、profile matrix tests にまたがる。`iss-00244` はすでに複数の追加修正を含んでおり、さらに template storage model 変更まで入れると scope が膨らむ。

したがって、`iss-00247` として分離して扱うのが安全である。

### ただし、今後 JSON body を厚くするなら先に切り替えるべき

今後 `profile-sections.json` の design / plan scaffold を大幅に厚くするなら、その前に Markdown template 化した方がよい。厚い JSON scaffold を作ってから移行すると、同じ template 設計を二度行うことになる。

このため、本 research の推奨は次である。

- `iss-00247` では、Markdown-template-first hybrid への移行を主題として扱う。
- `profile-sections.json` の design / plan prose を増やす前に、template source を Markdown file へ移す。
- `report.md` の扱いは、design / plan と同時に移すか、append-oriented artifact として managed-section を一時維持するかを planning で決める。

## follow-up issue 案

作成済み Issue:

`iss-00247 Move Assurance Compose Scaffold Sources To Profile Markdown Templates`

目的:

`assurance compose` の profile 別 `design.md` / `plan.md` scaffold source を JSON string body から Markdown template files へ移し、profile 別 planning template の編集性・レビュー容易性・dogfooding 適合性を高める。

最小 acceptance:

- `templates/assurance/profiles/{lite,standard,strict,critical}/{design,plan}.md` が provider asset として存在する。
- `assurance compose` は `authorized_profile` と artifact kind に応じて Markdown template を選択する。
- `lite_candidate` は template 選択 authority にならない。
- 既存の placeholder guard、substantive content fail-closed、marker conflict guard、dry-run、changed path reporting、source binding update は維持される。
- `standard` / `strict` / `critical` の output 差分を profile matrix tests で固定する。
- `design.md` / `plan.md` の prose は `profile-sections.json` に残さない。

追加検証:

- 全 profile に `design.md` / `plan.md` template が存在する。
- missing template は write 前に fail-closed する。
- existing frontmatter の ID、title、GitHub、parent、dependency が維持される。
- `<ISS_ID>` / `<ISS_TITLE>` のような placeholder が最終 artifact に残らない。
- 二回目 compose は no-op。
- materialized 後の profile 再分類は silent overwrite しない。

## report.md について

Deep Consultant と ChatGPT の両方で、`report.md` は扱いを分ける余地があるとされた。

`report.md` は execution 後の evidence ledger であり、design / plan より append-oriented である。したがって、短期的には現行 managed-section 方式を残してもよい。

ただし、profile 別 report scaffold も人間が編集したくなるなら、同じ Markdown template layout に移す価値はある。これは follow-up issue の scope 決定時に再検討する。

## リスク

- Markdown template 化で profile 間の重複が増え、共通文言 drift が起きる。
  - 対策: profile matrix tests と review checklist で固定する。
- full-file copy を採用すると frontmatter や human edits を壊す。
  - 対策: body template + frontmatter preserve を基本にする。
- profile 再分類後に compose を再実行したとき、silent overwrite が起きる。
  - 対策: materialized artifact は自動差し替えしない。明示的な refresh / reset command は別 issue で扱う。
- JSON manifest を残したまま Markdown template も導入すると authority が二重化する。
  - 対策: design / plan prose は Markdown template に一本化し、manifest を使う場合も path index のみにする。

## 最終判断

長期のベストプラクティスは、profile / artifact 別 Markdown template file を source of truth とする `Markdown-template-first hybrid` である。

`iss-00244` はすでに merge 済みであるため、この設計課題は `iss-00247` で分離して扱う。`iss-00247` の planning では、まず design / plan の profile scaffold source を Markdown template file に移すことを中心に要件化する。

この判断を変える条件は、`report.md` も同時に Markdown template 化する必要が明確になった場合である。その場合は、design / plan だけでなく report も含めた profile template layout を planning で再検討する。
