---
種別: research
ID: "20260707t155254z-research"
タイトル: "ChatGPT requirement design plan concretization"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
親: ["epic-00295"]
関連: []
scope: "epic"
scope_id: "epic-00295"
created_at: "2026-07-07T15:52:54Z"
created_by: "codex"
status: "proposed"
authority: "evidence_only"
adoption_status: "unreviewed"
derived_from:
  - "ChatGPT Use session: specdock-epic00295-rdp-concretization-solo"
  - "artifacts/20260707t152834z-research-chatgpt-multi-skill-authoring-workflow-analysis.md"
  - "artifacts/20260707t150325z-research-chatgpt-workflow-best-practices-final-analysis.md"
reflected_to:
  - "requirement.md"
  - "design.md"
  - "plan.md"
  - "report.md#Evidence Adoption Ledger EAL-008"
---

# ChatGPT requirement design plan concretization

## 位置づけ

この research は、追加インタビュー不要と判断した後、ChatGPT-Use / GPT-5.5 Pro Extended に `epic-00295` の要件定義書、設計書、実装計画書の具体化を依頼した結果の採用候補である。

## ChatGPT 実行メモ

- session: `specdock-epic00295-rdp-concretization-solo`
- model: `gpt-5.5-pro`
- mode: Pro Extended
- prompt: solo prompt 1 file
- GitHub connector:
  - `chemitaro/spec-dock` へのアクセスは成功。
  - current branch `codex/authoring-pack-installed-runtime` は解決できず、default branch `main` を確認。
  - GitHub Issue `#295` は open と確認。
- caveat:
  - current branch 固有の untracked Epic artifact は GitHub connector からは見えていない。
  - この artifact は evidence-only であり、正本反映は Codex が採否判断して行う。

## 採用候補サマリー

### 要件

- `scripts/authoring-pack/` dogfood helper を、provider-side installed runtime / installed skill / shipped docs へ昇格する。
- ChatGPT output は evidence-only とし、canonical adoption、`.assurance.json` mutation、`authorized_profile`、fresh reviewer pass、execution-ready、PR-ready を主張させない。
- `spec-dock-initiative-planning` / `spec-dock-epic-planning` / `spec-dock-issue-planning` は既存名を維持し、scope-specific human-facing workflow entrypoint とする。
- `spec-dock-chatgpt-authoring` を shared evidence lane skill として追加する。
- `./spec-dock/scripts/spec-dock authoring ...` を installed runtime command group とする。
- `authoring preflight github-sync` は repo-aware ChatGPT invocation 前の block-first gate とする。
- dirty tracked changes、staged changes、untracked files、unpushed commits、behind、diverged、branch missing、origin mismatch、source hash mismatch、connector failure、unknown default branch は block する。
- ZIP root は `specdock-authoring-pack/` とし、metadata、source manifest、stale-if、safe constraints、EAL candidates を必須化する。

### 設計

- Runtime command group は repo / GitHub / ZIP / filesystem / backend invocation を deterministic に扱う control plane。
- Skills は人間が scope と gate を選ぶ workflow entrypoints。
- ChatGPT output は draft / candidate / reviewer-focus / risk evidence を返す data plane。
- Canonical adoption は planning skills と main orchestrator が reviewer gate を通して行う authority plane。
- Provider-side source of truth は `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/` と `src/spec_dock/assets/install_root/.agents/skills/`。
- root `scripts/authoring-pack/` は移行後に standalone helper / compatibility surface とし、正本ではない。

### 計画

推奨 Issue sequence:

1. provider-side installed layout への authoring pack asset 移設。
2. runtime `authoring` command group skeleton。
3. block-first GitHub sync preflight。
4. prompt pack prepare と safe output constraints。
5. configurable backend invocation adapter。
6. ZIP/tree review and staging runtime commands。
7. Initiative/Epic and Epic/Issue candidate validators。
8. Issue draft adoption and selected skeleton validation。
9. `spec-dock-chatgpt-authoring` installed skill と既存 planning skills 更新。
10. approval check と stop-gate evidence reports。
11. runtime docs / reference docs / workflow guidance。
12. dogfood installed runtime and final quality gate。

## 採用方針

直接採用する:

- 既存 planning skill 名維持 + `spec-dock-chatgpt-authoring` 追加。
- `authoring` runtime command group。
- GitHub sync preflight の block-first 方針。
- ChatGPT output evidence-only boundary。
- ZIP root / metadata / unsafe rejection categories。
- 初期 scope で `authoring adopt` と自動 Issue 作成 command を作らない方針。

evidence-only のまま残す:

- ChatGPT の exact wording。
- current branch に関する GitHub connector 観測。
- `scripts/authoring-pack/` dogfood helper の現状分析。
- Issue sequence の番号と title は正本 plan で再調整する。

## 未解決

- current branch が GitHub connector から見えない理由。
- default branch fallback の flag 名。
- `spec-dock-chatgpt-authoring` を managed skill list のどの位置に入れるか。
- `ORACLE_CHATGPT_COMMAND` fallback の廃止時期。
- Initiative/Epic candidate schema の詳細。
- approval evidence の保存場所と署名強度。
