---
種別: research
ID: "20260707t164856z-research"
タイトル: "ChatGPT final ZIP authoring pack adoption"
状態: "draft | completed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
親: ["epic-00295"]
関連: []
authority: "synthesized"
derived_from: []
reflected_to: []
---

# 20260707t164856z-research ChatGPT final ZIP authoring pack adoption

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約、用語衝突、edge case など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は artifact type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は source-grounded research evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- 事実、推測、未検証事項、用語衝突、edge case、判断への含意を混ぜない。
- local context で解ける疑問は人間に聞かず、この artifact に source-grounding を残す。

## 調査目的 (必須)
- ChatGPT-Use / GPT-5.5 Pro Extended に依頼した ZIP authoring pack が、Epic 正本候補および Issue draft handoff evidence として採用できるかを確認する。
- ZIP 内の Epic `requirement.md` / `design.md` / `plan.md` と 12 Issue draft pack を、SpecDock の authority boundary を壊さずに保存・採用する方法を整理する。

## sources / 調査方法 (必須)
- 参照先:
  - Oracle ZIP artifact: `/Users/iwasawayuuta/.oracle/sessions/epic00295-final-pack-zip/artifacts/epic-00295-chatgpt-authoring-final-pack.zip`
  - Extracted evidence pack: `artifacts/20260707t164532z-chatgpt-final-authoring-pack/`
  - ChatGPT transcript: `/Users/iwasawayuuta/.oracle/sessions/epic00295-final-pack-zip/artifacts/transcript.md`
  - Prompt: `/private/tmp/codex-agent-work/501/session-20260707t162117z-epic00295-chatgpt-zip-pack-382f9dea/prompt.md`
- 検証手順:
  - ZIP を Oracle artifact directory から確認した。
  - ZIP を `/private/tmp/codex-agent-work/...` へ展開し、41 ファイルの pack 構成を確認した。
  - ZIP の SHA-256 を計算した。
  - Epic 正本 3 本は既存 front matter を維持したまま、ChatGPT 生成本文を採用した。
  - Issue draft pack は Issue node 作成前のため canonical Issue docs ではなく、Epic-local evidence pack として保存した。
- 実験条件:
  - Repository: `chemitaro/spec-dock`
  - Branch: `codex/authoring-pack-installed-runtime`
  - 事前 commit: `4cc193a3c0fb69a860108c9c3f61f0a4a24d1757`
  - 事前 push: `origin/codex/authoring-pack-installed-runtime`
  - ZIP SHA-256: `683187d765b12c4abeafb99cfe0662f3620d61c1fb8bdccc6867d85dd561e4e7`

## facts / 観測できた事実 (必須)
- ChatGPT は `epic-00295-chatgpt-authoring-final-pack.zip` を生成し、Oracle wrapper は artifact directory へ保存できた。
- ZIP は `epic-00295-chatgpt-authoring-final-pack/` root を持ち、合計 41 ファイルを含む。
- ZIP には `manifest.json`、`README.md`、Epic 正本候補 3 本、12 Issue 候補それぞれの `draft-requirement.md` / `draft-design.md` / `draft-plan.md` が含まれる。
- `manifest.json` の adoption boundary は `authority: evidence_only`、`adoption_status: unreviewed`、`bundle_generation_not_promotion: true` を明示している。
- Issue 候補は以下の 12 件:
  - `01-promote-authoring-pack-assets`
  - `02-add-authoring-command-skeleton`
  - `03-implement-github-sync-preflight`
  - `04-prepare-prompt-pack-and-safe-output-constraints`
  - `05-implement-backend-invocation-adapter`
  - `06-promote-zip-review-and-staging`
  - `07-validate-initiative-epic-and-epic-issue-candidates`
  - `08-validate-issue-draft-adoption-and-selected-skeleton`
  - `09-add-chatgpt-authoring-skill-and-update-planning-skills`
  - `10-implement-approval-check-and-stop-gate-reports`
  - `11-update-runtime-docs-and-workflow-guidance`
  - `12-final-quality-gate-and-mergeable-pr-delivery`

## inference / 推測 (必須)
- 事実から推測したこと:
  - ZIP 生成を前提にすると、ChatGPT は Epic 正本候補と多数の Issue draft pack を一括で作れるため、Codex 側の役割は「正本化判断」「保存先制御」「検証」「Issue node 作成前 gate」に集中できる。
  - Issue draft pack を Epic artifact 内の raw evidence として保存することで、Issue 作成前に `draft-*` artifact type を誤って Epic scope へ昇格するリスクを避けられる。
- 推測の根拠:
  - `artifacts/rules.md` は Epic scope の typed `draft-requirement` / `draft-design` / `draft-plan` を unsupported としている。
  - `workflow_epic.md` は Issue draft handoff を Issue 作成後の adoption 対象として扱う。
  - ChatGPT generated pack 自体も canonical adoption ではなく evidence-only であることを manifest に明示している。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - 12 Issue 候補を実際に Issue node として作成するかどうかの人間承認。
  - 各 Issue draft pack の内容が、そのまま Issue planning の正本化入力として十分かどうか。
  - ZIP pack を将来の runtime `authoring stage` command が同じ形で受理できるかどうか。
- 確認できない理由:
  - Issue Decomposition Approval Gate はこの時点では未実施。
  - Runtime command はまだ実装前であり、今回の ZIP は dogfood simulation output である。

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - 12 Issue 候補をこの順序・粒度で承認してよいか。
  - Issue candidate ID を正式 Issue 作成時に `iss-*` へどのように map するか。
- pressure-test question として切り出すべき候補:
  - `local-context` evidence mode の UX 名称と misuse prevention は十分か。
  - final quality gate / PR delivery Issue の完了条件は、実装修正と PR repair をどこまで含むべきか。
- 質問せずに解決できた候補:
  - Issue draft pack は Epic scope typed draft artifact ではなく raw evidence pack として保存する。
  - Epic 正本 3 本は main orchestrator が front matter を維持して本文採用する。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - `final pack` と `canonical final`
  - `draft-*` と Epic scope artifact type
- 既存 docs / code / tests / artifacts / primary sources での使われ方:
  - ChatGPT の `final pack` は ZIP 出力として完成しているが、SpecDock 正本としての final / accepted を意味しない。
  - `draft-requirement` / `draft-design` / `draft-plan` は Issue scope で扱う artifact type であり、Epic scope では unsupported。
- 判断が必要な理由:
  - ZIP を直接正本展開すると、ChatGPT が authority boundary を越えたように見えるため。
  - Issue node 作成前に Issue draft を canonical path へ置くと、human approval checkpoint を飛ばしたように見えるため。

## edge cases / 具体シナリオ (必須)
- edge case:
  - ChatGPT ZIP が正しい構造でも、manifest が `authority: accepted` や reviewer pass を self-claim する。
  - GitHub sync preflight が満たせない状況で `local-context` evidence mode を使い、source bundle の不足により stale evidence が生成される。
  - Issue 候補を人間承認前に自動作成してしまい、Issue Decomposition Approval Gate が形骸化する。
- その edge case が requirement / design / plan に与える影響:
  - ZIP review / stage は forbidden authority claim を fail-closed にする必要がある。
  - `local-context` evidence mode は明示 opt-in、低 authority、EAL disposition 必須にする必要がある。
  - Runtime 初期版は Issue node creation / canonical adoption / reviewer pass claim を対象外にする必要がある。

## implications / 判断への含意 (必須)
- Epic `requirement.md` / `design.md` / `plan.md` は ChatGPT 生成本文を採用し、installed runtime / skill surface、GitHub sync preflight、`local-context` evidence mode、relay PR delivery policy、12 Issue sequence を明示する。
- Issue draft pack は `artifacts/20260707t164532z-chatgpt-final-authoring-pack/issues/` に evidence-only として保存し、Issue Decomposition Approval Gate 後に各 Issue の `spec-dock-issue-planning draft-adoption` 入力として使う。
- Report の Evidence Adoption Ledger には、ChatGPT ZIP pack を `partially_adopted` として記録する。

## リスク/制約 (任意)
- ZIP pack は ChatGPT output であり、SpecDock validator / reviewer pass ではない。
- ChatGPT manifest の GitHub branch compare details は connector 側観測であり、Codex 側の local git verification とは別に扱う。
- `artifacts/20260707t164532z-chatgpt-final-authoring-pack/` は raw evidence pack directory であり、typed artifact file ではない。

## 反映先 (任意)
- reflected_to:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md` Evidence Adoption Ledger

## 参考（References） (任意)
- `artifacts/20260707t164532z-chatgpt-final-authoring-pack/manifest.json`
- `artifacts/20260707t164532z-chatgpt-final-authoring-pack/README.md`
- `artifacts/20260707t164532z-chatgpt-final-authoring-pack/issues/`
