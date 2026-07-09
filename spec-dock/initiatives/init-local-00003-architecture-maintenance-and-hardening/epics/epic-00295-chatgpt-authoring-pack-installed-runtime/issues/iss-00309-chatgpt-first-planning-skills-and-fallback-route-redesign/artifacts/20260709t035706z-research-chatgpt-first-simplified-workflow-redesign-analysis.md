---
種別: research
ID: "20260709t035706z-research"
タイトル: "ChatGPT First Simplified Workflow Redesign Analysis"
状態: "draft | completed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-07-09"
親: ["iss-00309"]
関連: []
authority: "synthesized"
derived_from: []
reflected_to: []
---

# 20260709t035706z-research ChatGPT First Simplified Workflow Redesign Analysis

## 調査目的 (必須)
- ChatGPT-first planning workflow を、旧 manual planning の grade / specialist / phase mechanics からどこまで切り離せるかを分析する。
- ChatGPT に渡すべき情報、Codex/main orchestrator が保持すべき責務、スキル・ドキュメント・スクリプト・prompt template の具体設計を整理する。
- 3段階の ChatGPT GPT-5.5 Pro Extended 分析を evidence として保存し、後続実装の input にする。

## sources / 調査方法 (必須)
- 参照先:
  - ChatGPT session `specdock-chatgpt-first-simplified-workflow-2`
  - ChatGPT follow-up session `specdock-chatgpt-first-file-level`
  - ChatGPT follow-up session `specdock-chatgpt-first-template-wording`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-*-planning-manual/SKILL.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_chatgpt_authoring_pack.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_initiative.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/backend_invoke.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/pack_prepare.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/prompt_pack_contract.py`
  - `spec-dock/active/issue/artifacts/20260709t010505z-research-chatgpt-use-direct-vs-specdock-script-route-analysis.md`
- 検証手順:
  - Stage 1: 大枠の方向性、複数案比較、推奨設計を ChatGPT に分析させた。
  - Stage 2: 推奨設計を前提に、変更対象ファイル、受け入れ条件、テスト案を follow-up で具体化させた。
  - Stage 3: prompt template と Codex-facing skill instruction の具体文言案を follow-up で作成させた。
  - Oracle 0.15.2 と新 manual-login profile `/Users/iwasawayuuta/.oracle/browser-profile-recovery-20260709` で ChatGPT route の smoke test を通した。
- 実験条件:
  - `chatgpt-use` wrapper に `--browser-manual-login-profile-dir /Users/iwasawayuuta/.oracle/browser-profile-recovery-20260709` を追加して実行した。
  - Stage 1 は 22 files / 約 93k tokens の bundle で実行した。
  - Stage 2 / Stage 3 は browser follow-up session として実行した。

## facts / 観測できた事実 (必須)
- ChatGPT は、ユーザーの単純化仮説を「大筋で正しいが、無条件に単純化すると危険」と評価した。
- 推奨案は `Simple ChatGPT-first authoring UX + evidence-only adoption kernel + staged script hardening` である。
- ChatGPT-facing workflow からは、旧 manual planning の token-saving 目的だった grade / specialist / phase-by-phase mechanics を中心から外すべきとされた。
- Codex/main orchestrator 側には、EAL 採否、canonical rewrite、fresh `spec-reviewer`、human approval、Issue grade、manual fallback 条件を残すべきとされた。
- Issue grade は Initiative / Epic の broad planning から外し、formal Issue planning / execution planning の grade recommendation / template selection / quality gate selection に残す方針が推奨された。
- ChatGPT が十分な情報を得られない場合、ZIP/tree を無理に生成せず `information_insufficient` を返す contract が推奨された。
- Prompt template は Python 文字列ではなく、provider-side Markdown assets として追加する方針が推奨された。
- Script は planning authority ではなく、preflight / prompt rendering / backend invocation / artifact materialization validation / pack review / staging diagnostics に限定すべきとされた。
- `backend_call_pass`、`artifact_materialized_pass`、`pack_review_pass`、`candidate_validation_pass`、`adoption_ready_for_orchestrator_review` を分離することが推奨された。
- `backend_invoke.py` の backend return code 0 は artifact materialization success と同一視すべきではないとされた。

## alternatives / 比較案
| 案 | 内容 | 評価 |
|---|---|---|
| A | Heavy SpecDock script-first route | 安全だが ChatGPT reasoning UX が硬くなり、直実行ルートの良さを活かしにくい。 |
| B | Direct `chatgpt-use` route を実質標準化 | 出力品質は高いが、private wrapper path / browser profile を product contract にできない。 |
| C | Thin ChatGPT-first templates + evidence-only kernel | 推奨。単純さ、品質、安全性、既存 architecture fit のバランスが最良。 |
| D | Fully automated authoring pipeline | authority boundary を壊しやすく、現段階では危険。 |
| E | Old manual workflow as co-primary route | recovery には強いが、旧 token-saving 前提を温存しすぎる。 |

## recommended design / 推奨設計
- ChatGPT-facing layer は、rich context、repository / branch context、evidence mode、desired output tree、authority constraints、information-insufficient escape hatch を渡す薄い authoring UX にする。
- ChatGPT には内部の作り方を過剰に指定せず、タスクの重さに応じて自由に深く考えさせる。
- Codex/main orchestrator は、source selection、sync/local-context 判定、ChatGPT invocation、artifact inspection、EAL、canonical rewrite、fresh reviewer、human approval を所有する。
- Manual route は hard / unrecoverable ChatGPT failure + explicit human approval の emergency backup として残す。

## workflow by scope / scope別ワークフロー
### Initiative Planning
- ChatGPT に Initiative `requirement` / `design` / `plan` candidates、bounded Epic boundaries、optional ADR candidates、EAL candidates を求める。
- Epic specs / Issue specs は完成させない。
- Issue grade は中心にしない。
- 不足情報があれば `information_insufficient` とし、clarification へ戻す。

### Epic Planning
- ChatGPT に Epic `requirement` / `design` / `plan` candidates、Issue slices、dependency order、Issue-local draft requirement/design/plan、final quality / PR delivery Issue policy、path index を求める。
- Child Issue canonical docs は finalize しない。
- Multi-Issue implementation Epic には final quality / PR delivery Issue を要求する。例外は single-Issue / docs-only / no-op / accepted exception のみ。
- Grade signals は advisory。formal `authorized_profile` ではない。

### Issue Planning
- `zero-base` / `requirement-first` は `issue-planning` template を使う。
- `draft-adoption` は `issue-draft-adoption` template を使う。
- ChatGPT は grade を recommend できるが `authorized_profile` selection や `.assurance.json` mutation を claim しない。
- Draft claims は `adopt` / `partially_adopt` / `reject` / `stale` / `blocked` に分類する。

## grade policy / grade方針
- Grade を Initiative / Epic broad planning の中心から外す。
- Grade は formal Issue planning / execution planning に残す。
- ChatGPT の役割は `recommended_grade: lite | standard | strict | critical` と rationale / confidence / why_not_lower / escalation triggers / missing facts を返すこと。
- Lite は default ではない。unknown / ambiguous な scope、impact、risk、reviewer obligation は Standard 以上に倒す。
- Runtime / scaffold / workflow / template profile / installed asset 影響は通常 Strict 以上を検討する。

## information-insufficient contract
ChatGPT が安全に仕様書を生成できない場合、ZIP/tree を作らず次のような evidence-only response を返す:

```yaml
status: information_insufficient
authority: evidence_only
adoption_status: unreviewed
bundle_generation_not_promotion: true
scope: initiative | epic | issue | issue-draft-adoption
evidence_mode: github-synced | local-context | unknown
can_produce_zip: false
reason_codes:
  - ambiguous_scope
  - missing_user_intent
  - missing_acceptance_criteria
  - missing_parent_scope
  - missing_current_repo_state
  - missing_draft_provenance
  - missing_dependency_state
  - unresolved_report_ledger
  - conflicting_sources
  - stale_github_sync
  - unsafe_or_secret_context
blocking_questions:
  - question: "..."
    why_needed: "..."
safe_partial_findings:
  - finding: "..."
not_claimed:
  - canonical adoption
  - reviewer pass
  - execution-ready
  - PR-ready
```

## concrete file targets / 具体的な変更対象
### Skills
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md`
  - prompt template relationship を追加する。
  - `backend_call_pass` と `artifact_materialized_pass` の分離を明記する。
  - `information_insufficient` の扱いを追加する。
- `spec-dock-initiative-planning/SKILL.md`
  - `initiative-planning` template 使用を明記する。
  - Epic boundaries は candidate であり finalized Epic specs ではないと明記する。
- `spec-dock-epic-planning/SKILL.md`
  - `epic-planning` template 使用、Issue draft evidence、final quality Issue policy、non-authoritative grade signals を明記する。
- `spec-dock-issue-planning/SKILL.md`
  - `issue-planning` / `issue-draft-adoption` template の使い分けを明記する。
  - grade recommendation checklist を追加する。
- `spec-dock-*-planning-manual/SKILL.md`
  - 基本維持。manual は co-primary ではなく emergency backup として残す。

### Docs / Templates
- `src/spec_dock/assets/spec_dock/docs/workflow_chatgpt_authoring_pack.md`
  - prompt template set、information-insufficient outcome、status separation、backend/wrapper boundary を追加する。
- `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
  - ChatGPT-first の単純化と grade の formal Issue planning への限定を整理する。
- `src/spec_dock/assets/spec_dock/docs/workflow_initiative.md`
  - Initiative ChatGPT output shape を追加する。
- `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`
  - Epic ChatGPT output shape、Issue drafts、final quality Issue policy を追加する。
- `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - issue planning modes、draft adoption、information-insufficient routing を追加する。
- `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
  - grade recommendation checklist を追加する。
- `src/spec_dock/assets/spec_dock/templates/epic/plan.md`
  - `suggested grade` を non-authoritative `grade signals / downstream planning hints` に置き換える。

### New prompt assets
```text
src/spec_dock/assets/spec_dock/system/chatgpt-authoring/prompts/
  shared/base.md
  initiative-planning.md
  epic-planning.md
  issue-planning.md
  issue-draft-adoption.md
```

### Runtime / Scripts
- `prompt_pack_contract.py`
  - `issue-draft-adoption` mode を追加する。
  - forbidden claims に `merge-ready`、`Issue finish`、`Epic completion` を追加する。
  - prompt template path constants を追加する。
- `pack_prepare.py`
  - Python hardcoded prompt ではなく Markdown template render に切り替える。
  - mode-specific prompt を生成する。
  - `information_insufficient` contract を prompt に含める。
- `backend_invoke.py`
  - `backend_call_status` と `artifact_materialization_status` を分離する。
  - return code 0 のみでは local ZIP/tree availability を claim しない。
- `pack_review.py`
  - local materialized artifact validation step として docs/rendering 上の位置づけを明確にする。

### Tests
- `tests/cli_runtime/test_chatgpt_prompt_templates.py`
- `tests/cli_runtime/test_authoring_pack_prepare_templates.py`
- `tests/cli_runtime/test_authoring_backend_invoke_status_semantics.py`
- `tests/cli_runtime/test_authoring_pack_review_materialization.py`
- `tests/cli_runtime/test_chatgpt_first_skill_contracts.py`
- `tests/cli_runtime/test_chatgpt_docs_contracts.py`
- `tests/cli_runtime/test_installed_chatgpt_authoring_assets.py`

## prompt template wording / prompt文言骨子
Stage 3 では、次の実装転用可能な文言案が提示された:
- `shared/base.md`
  - evidence-only authority boundary
  - `github-synced` / `local-context`
  - source discipline
  - reasoning depth
  - output root `specdock-authoring-pack/`
  - information-insufficient fallback
  - forbidden authority claims / forbidden payloads
- `initiative-planning.md`
  - Initiative R/D/P candidates、Epic boundaries、optional ADR candidates
  - Epic specs / Issue specs を finalize しない
- `epic-planning.md`
  - Epic R/D/P candidates、Issue slices、dependency order、Issue drafts、final quality issue policy
  - child Issue canonical docs を finalize しない
- `issue-planning.md`
  - zero-base / requirement-first
  - Issue R/D/P candidates、grade recommendation、reviewer focus
- `issue-draft-adoption.md`
  - draft claim disposition、current-state drift、issue-local repair、epic repair triggers

## risks / リスク
- ChatGPT output を canonical と誤解するリスク。
- `backend invoke pass` を artifact materialization success と誤解するリスク。
- Prompt templates が再び重くなり、旧 manual workflow を再導入するリスク。
- `information_insufficient` が無視され、曖昧なまま仕様書が生成されるリスク。
- Grade が早期 decomposition を過剰に縛るリスク。

## implications / 判断への含意 (必須)
- この Epic の次実装は、旧 skill に ChatGPT 利用を追記するよりも、primary ChatGPT-first skill / prompt template / authoring scripts の責務分離を明確にする方向がよい。
- まず prompt template provider assets と docs/skills の責務整理を行い、その後に script の status semantics と artifact materialization validation を強めるのが安全。
- Manual route は廃止せず、human-approved emergency backup として維持する。
- Issue grade は正式 Issue planning でのみ重視し、Initiative / Epic の ChatGPT authoring では advisory risk signal に留める。

## unverified / 未検証事項 (必須)
- ChatGPT の提案は code patch ではない。実装時には current parser / test tree / installed asset copy behavior を再確認する必要がある。
- `authoring artifact collect` を今実装するか、`pack review --input <local ZIP/tree>` を当面の materialization validation とするかは実装判断が必要。
- Prompt template の実際の exact wording は、Stage 3 の出力をベースにしつつ、repo style とテスト容易性に合わせて調整する必要がある。

## 参考（References） (任意)
- ChatGPT stage 1: `specdock-chatgpt-first-simplified-workflow-2`
- ChatGPT stage 2: `specdock-chatgpt-first-file-level`
- ChatGPT stage 3: `specdock-chatgpt-first-template-wording`

## inference / 推測 (必須)
- 事実から推測したこと:
  - `chatgpt-use` 直実行ルートの出力品質が高かった主因は、旧 manual workflow の token-saving mechanics を強く縛らず、repository context と目的を渡して ChatGPT 側の推論余地を広く残した点にある。
  - SpecDock に組み込むべき script は、ChatGPT の作り方を細かく管理する実行器ではなく、context assembly / invocation / materialized artifact validation / adoption handoff を安定化する薄い境界になるべきである。
  - Grade は planning cost control のための全域概念ではなく、formal Issue planning で execution quality gate を選ぶための局所的な判断材料として扱う方が、ChatGPT-first route と整合する。
- 推測の根拠:
  - Stage 1 から Stage 3 までの ChatGPT 分析が、複雑な旧 workflow の再現ではなく `evidence-only`、`information_insufficient`、prompt template、status separation に収束したため。
  - 直前の比較調査で、SpecDock script route より `chatgpt-use` 直接利用の方が成果物品質が高いと観測され、差分として prompt の自由度と制約の少なさが挙がったため。
  - 旧 grade / specialist / phase mechanics は Codex token/resource control のための側面が強く、ChatGPT Pro Extended に planning reasoning を寄せる場合は同じ制約を前提にしない方が自然なため。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - 推奨された prompt asset tree と tests を実装した場合、既存 installer / update flow で consumer repo に正しく配布されるか。
  - `backend_invoke.py` の status schema を変更した場合、既存 CLI output / tests / downstream docs にどの程度の修正が必要になるか。
  - `information_insufficient` を ChatGPT が安定して返すために、prompt wording と `pack_review` validation のどちらでどこまで拘束するべきか。
  - Manual fallback skill 名、並び順、discoverability をどこまで変更すると既存利用者の混乱を最小化できるか。
- 確認できない理由:
  - 本 artifact は ChatGPT 分析結果の synthesis であり、まだ provider-side files / tests / installer behavior への patch 実装を行っていないため。

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - Manual fallback skill の表示名は、`manual`、`backup`、`classic` のどれを採用するか。
  - `information_insufficient` の返却時に、Codex が自動で clarification skill に戻すのか、人間に一度提示して判断を待つのか。
  - Stage 3 の prompt wording をどの程度そのまま prompt asset として採用し、どの程度 repo style に合わせて圧縮するか。
- pressure-test question として切り出すべき候補:
  - ChatGPT が `information_insufficient` ではなく低品質な ZIP を返した場合、`pack_review` はどこまで検出できるべきか。
  - Multi-Issue Epic で final quality Issue が例外的に不要になる条件を template / docs / reviewer gate のどこで定義するか。
  - Local-context mode で GitHub sync がない場合、どの evidence を ChatGPT に渡せば repository-state drift risk を許容できるか。
- 質問せずに解決できた候補:
  - ChatGPT-first route で Initiative / Epic planning に Issue grade を中心概念として持ち込まないこと。
  - Manual route を co-primary ではなく human-approved emergency backup にすること。
  - ChatGPT output は canonical artifact ではなく evidence-only candidate として扱うこと。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - `pass`
  - `grade`
  - `planning`
  - `draft`
  - `authoring pack`
- 既存 docs / code / tests / artifacts / primary sources での使われ方:
  - `pass` は backend invocation の成功、ZIP/tree materialization、pack review、candidate validation、adoption readiness が混同されやすい。
  - `grade` は旧 manual workflow では token/resource control と quality gate の両方に関係していたが、ChatGPT-first では主に formal Issue planning / execution quality gate の判断材料になる。
  - `planning` は Initiative / Epic / Issue で出力粒度が異なる。特に Epic planning は Issue drafts を作るが、formal Issue planning を完了するわけではない。
  - `draft` は child Issue handoff evidence であり canonical Issue requirement/design/plan ではない。
  - `authoring pack` は ChatGPT output evidence であり、SpecDock canonical docs への promotion そのものではない。
- 判断が必要な理由:
  - 用語が曖昧なまま script / skill / docs に入ると、backend 実行成功を planning 完了や review pass と誤認する危険があるため。

## edge cases / 具体シナリオ (必須)
- edge case:
  - GitHub sync が取れないが、local diff と必要 artifact を明示して local-context mode で依頼したい。
- その edge case が requirement / design / plan に与える影響:
  - sync-only hard gate ではなく、明示的な local-context mode と evidence disclosure を用意する必要がある。
- edge case:
  - ChatGPT が browser / tab 上限 / transient failure で一時的に使えない。
- その edge case が requirement / design / plan に与える影響:
  - 原則は待機・再接続・復旧であり、manual fallback は hard / unrecoverable failure + explicit human approval に限定する必要がある。
- edge case:
  - Epic planning で生成された Issue draft が、実装直前の current repo state とずれている。
- その edge case が requirement / design / plan に与える影響:
  - Issue planning の `issue-draft-adoption` mode で draft claim disposition と current-state drift を検査し、必要なら Epic repair trigger を出す必要がある。

## implications / 判断への含意 (必須)
- Requirement には、ChatGPT output を evidence-only candidate として扱い、canonical adoption は Codex / reviewer / human gate を経ることを明記する。
- Design には、prompt template assets、status separation、information-insufficient response、manual fallback boundary を入れる。
- Plan には、prompt assets → docs/skills → script status semantics → tests → dogfooding validation の順で実装する段取りを入れる。
- ADR には、ChatGPT-first route を primary、manual route を explicit human-approved emergency backup とする判断を記録する。

## リスク/制約 (任意)
- ChatGPT browser automation は profile / tab limit / Cloudflare / UI drift の影響を受けるため、workflow は recoverable failure と hard failure を分ける必要がある。
- Private local wrapper path や browser profile は SpecDock product contract にできないため、repo 側は backend command adapter contract に留める必要がある。
- Prompt template を重くしすぎると、直実行 route の品質を生んでいた自由度を失う。

## 反映先 (任意)
- reflected_to:
  - `iss-00309` requirement / design / plan
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_chatgpt_authoring_pack.md`
  - `src/spec_dock/assets/spec_dock/system/chatgpt-authoring/prompts/`

## 参考（References） (任意)
- ChatGPT stage 1: `specdock-chatgpt-first-simplified-workflow-2`
- ChatGPT stage 2: `specdock-chatgpt-first-file-level`
- ChatGPT stage 3: `specdock-chatgpt-first-template-wording`
