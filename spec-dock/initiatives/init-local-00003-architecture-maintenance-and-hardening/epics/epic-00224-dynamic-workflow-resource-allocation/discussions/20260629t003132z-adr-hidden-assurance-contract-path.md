---
種別: ADR（Architecture Decision Record）
ID: "20260629t003132z-adr"
タイトル: "Hidden Assurance Contract Path"
状態: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-06-29"
親: ["epic-00224"]
authority: "accepted"
supersedes:
  - "issue-local assurance.json visible canonical path"
amends:
  - "20260623t074443z-adr"
derived_from:
  - "../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/discussions/20260628t052300z-research-hidden-assurance-contract-path.md"
  - "../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/report.md"
reflected_to:
  - "../requirement.md"
  - "../design.md"
  - "../plan.md"
  - "../report.md"
  - "../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/requirement.md"
  - "../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/design.md"
  - "../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/plan.md"
---

# 20260629t003132z-adr Hidden Assurance Contract Path

## ADR 化基準

- hard to reverse: yes
- surprising without context: yes
- real tradeoff: yes
- ADR として残す理由:
  - Assurance Contract の path は、agent が何を primary document として読むか、runtime が source binding をどこに保存するか、legacy issue をどう扱うかに影響する。
  - 旧 Epic ADR / docs には `assurance.json` を issue root の visible canonical artifact とする表現が残っているため、`.assurance.json` への変更を accepted decision として明示する必要がある。

## 結論（Decision）

- Issue-local Assurance Contract の canonical path は `<issue>/.assurance.json` とする。
- `assurance.json` は current authority として新規 write しない。
- `.assurance.json` は runtime-managed metadata contract であり、agent-facing primary docs ではない。
- `requirement.md` / `design.md` / `plan.md` / `report.md` が agent-facing canonical planning artifacts であり、`.assurance.json` はそれらの source binding、authorized profile、stale detection、obligation metadata を保持する machine-readable contract である。
- `.assurance.json` が missing で旧 `assurance.json` だけが存在する場合は、current authority として silently accept しない。migration-required diagnostics を返す。
- Existing dogfooding Issue-local `assurance.json` artifacts は `.assurance.json` へ rename する。
- Historical discussions / completed issue docs に残る `assurance.json` wording は、変更済み historical wording として扱う。必要最小限を超える bulk rewrite は行わない。

## 背景（Context）

- 初期 Epic 設計では、Issue root の `assurance.json` を tracked canonical artifact として扱っていた。
- Dogfooding 中、`assurance.json` が `requirement.md` / `design.md` / `plan.md` / `report.md` と同列に見えるため、agent が直接編集・読解すべき primary artifact と誤認し得ることが分かった。
- 実際には Assurance Contract は machine-readable metadata であり、human / agent が authoring する本文文書ではない。
- Hidden-style path にすることで、metadata 的な位置づけを file name からも示しつつ、Git tracked contract としての性質は維持できる。

## 選択肢（Options considered）

- Option A: `assurance.json` を維持する。
  - Pros: 既存実装・docs・tests の変更が小さい。
  - Cons: primary planning docs と同列に見え、agent が authority を誤読しやすい。
  - 判断: 棄却する。
- Option B: `.agent/` など ignored generated state に移す。
  - Pros: agent-facing docs からは隠れる。
  - Cons: tracked canonical contract / source binding としての性質が弱まり、generated projection と混同される。
  - 判断: 採用しない。
- Option C: issue root の `.assurance.json` に hard cutover する。
  - Pros: tracked metadata contract として残しながら、primary docs ではないことを示せる。source binding と stale detection の authority も維持できる。
  - Cons: 既存 issue artifacts と tests を rename / update する必要がある。
  - 判断: 採用する。

## 判断理由（Rationale）

- Assurance Contract は runtime が読み書きする machine-readable metadata であり、agent が手で編集する作業文書ではない。
- `.` prefix は完全な secrecy ではないが、planning docs と metadata contract の境界を名前で示せる。
- ignored projection へ移すと、contract が source of truth なのか generated state なのかが曖昧になる。したがって tracked issue-local file として残す。
- 旧 `assurance.json` を silently accept すると、current authority が二重化する。hard cutover では migration-required diagnostics に倒す方が安全である。

## 影響（Consequences）

- Positive:
  - Agent-facing primary docs と runtime metadata contract の境界が明確になる。
  - Source binding / stale detection の tracked authority は維持される。
  - Legacy path の誤使用を structured diagnostics で検出できる。
- Negative / Debt:
  - CLI help、docs、tests、dogfooding artifacts の path 更新が必要である。
  - Historical documents には旧 wording が残るため、ADR と変更済み注記で current authority を示す必要がある。
- 影響範囲:
  - `assurance classify/show/verify/compose`
  - workflow guidance / stale source binding
  - `AssuranceStore`
  - tests and dogfooding issue artifacts
  - authoring docs / CLI help
- 移行/ロールバック:
  - `.assurance.json` への hard cutover を採用する。
  - 旧 `assurance.json` のみ存在する issue は migration-required として扱う。
  - 旧 path を再度 authority に戻す場合は、この ADR を supersede する新 ADR が必要である。

## 旧決定との関係（Supersession / Amendment）

- `20260623t074443z-adr Adaptive Assurance Contract Lite Authorization And Monotonic Escalation`:
  - 維持: Assurance Contract が `authorized_profile` authority を持ち、`lite_candidate` は telemetry / recommendation であり、automatic Lite default は有効化しない。
  - 変更済み: Contract の issue-local path は `assurance.json` ではなく `.assurance.json` とする。
  - 変更済み: `assurance.json` がない既存 Issue を strict-legacy とみなす historical wording は、current hidden path migration 後は「`.assurance.json` がない Issue」の扱いに読み替える。旧 `assurance.json` だけが存在する場合は strict-legacy ではなく migration-required diagnostics である。

## 非目標（Non-goals）

- Assurance Contract を Git 管理外にしない。
- Human / agent が `.assurance.json` を直接編集する workflow を標準化しない。
- Historical discussions の全 `assurance.json` wording を一括 rewrite しない。
- Automatic Lite default を有効化しない。

## 参考（References）

- `../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/discussions/20260628t052300z-research-hidden-assurance-contract-path.md`
- `../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/requirement.md`
- `../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/design.md`
- `../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/plan.md`
- `20260623t074443z-adr-adaptive-assurance-lite-authorization-monotonic-escalation.md`
