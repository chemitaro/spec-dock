---
種別: ADR（Architecture Decision Record）
ID: "20260623t074443z-adr"
タイトル: "Adaptive Assurance Contract Lite Authorization And Monotonic Escalation"
状態: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
親: ["epic-00224"]
authority: "accepted"
amended_by:
  - "20260629t003132z-adr"
derived_from:
  - "20260623t074452z-disc-adr-decision-synthesis-after-issue-226-closure.md"
  - "20260623t012043z-research-deep-consultant-lite-rollout-report.md"
reflected_to:
  - "../requirement.md"
  - "../design.md"
  - "../plan.md"
  - "../report.md"
---

# 20260623t074443z-adr Adaptive Assurance Contract Lite Authorization And Monotonic Escalation

## 変更履歴（Supersession / Amendment）

- 2026-06-29: `20260629t003132z-adr Hidden Assurance Contract Path` により、Issue-local Assurance Contract の canonical path は `assurance.json` から `.assurance.json` へ変更済み。
- 維持: `authorized_profile` だけが workflow obligation を減らせる authority であり、`lite_candidate` は telemetry / recommendation である。
- 変更済み: 旧 `assurance.json` だけが存在する状態は current authority ではなく、migration-required diagnostics として扱う。

## ADR 化基準
- hard to reverse: yes
- surprising without context: yes
- real tradeoff: yes
- ADR として残す理由:
  - 軽量 task の cost 削減と安全 gate 維持の境界は、この Epic の中心的 tradeoff であり、複数 downstream Issue が同じ authority model を共有する必要がある。

## 結論（Decision）
- Adaptive workflow の実行 authority は tracked `assurance.json` 相当の Assurance Contract とする。
- `authorized_profile` だけが workflow obligation を減らせる。`lite_candidate` は telemetry / recommendation であり、runtime obligation を減らさない。
- 初期 rollout は Standard default とする。Lite は明示 opt-in、全 required predicate true、unknown required predicate なし、hard trigger なし、fresh source binding、policy / telemetry evaluation available の場合にだけ `lite_authorized` になれる。
- Automatic Lite default はこの Epic の初期 scope では有効化しない。将来有効化する場合は、別の accepted ADR、policy version bump、rollout Issue の 3 点を必須とする。policy version bump だけでは不十分とする。
- Escalation は単調追加である。hard trigger、stale source binding、unknown required predicate、protected domain、manual override は profile を強める方向にだけ働く。model confidence、token pressure、agent preference は profile を弱める理由にならない。
- Repository-specific hard trigger extension は additive-only、tracked、schema-validated、source-bound とし、provider default を弱められない。環境変数や untracked local override は policy authority ではない。

## 背景（Context）
- 現行 workflow は軽量 task にも重い gate / review cycle を課しやすい。
- 一方で、agent が軽量と判断しただけで gate を減らすと、設計判断、migration、security、review policy、data contract の事故につながる。
- Deep-consultant 分析では、candidate と authorized を分け、initial automatic Lite default を避ける方針が推奨された。

## 選択肢（Options considered）
- Option A: 自動分類で Lite を即時 default にする。
  - Pros: token / time cost 削減が最も大きい。
  - Cons: 誤分類時の安全余裕が小さい。telemetry がない段階で risk を引き受ける。
  - 棄却理由: 初期 architecture migration として強すぎる。
- Option B: Standard default + explicit Lite opt-in + evidence gate。
  - Pros: 安全側に倒しつつ Lite path を検証できる。
  - Cons: 自動削減の効果は初期には限定される。
  - 採用理由: dogfooding と telemetry で学習しながら安全に進められる。
- Option C: Strict-only を維持する。
  - Pros: 既存 safety model を保てる。
  - Cons: Epic の主目的である軽量 task の waste 削減に届かない。
  - 棄却理由: 問題を解決しない。

## 判断理由（Rationale）
- `lite_candidate` と `lite_authorized` を分離すると、classification の学習と実行 authority を混同しない。
- Unknown は fail-closed とすることで、metadata や source binding の欠落が軽量化に転じる事故を防ぐ。
- MyPy / Ruff baseline は ADR の tuning 対象ではないが、Assurance Contract / classification result / predicate evaluation は typed model と schema validation を持つべきである。

## 影響（Consequences）
- Positive:
  - 軽量化の候補を telemetry で観測しながら、実行 authority は安全側に維持できる。
  - Strict legacy fallback と compatible に段階 rollout できる。
- Negative / Debt:
  - schema、classification matrix、source binding、override validation が必要になる。
  - 初期段階では Lite の自動効果は限定される。
- 影響範囲:
  - Assurance Contract model / storage
  - workflow profile selection
  - planning artifact composition
  - rollout / telemetry report
- 移行/ロールバック:
  - Contract がない既存 Issue は strict-legacy path として扱う。
  - Lite authorization に問題が出た場合は policy version を Standard-only に戻せる。
- Follow-ups:
  - `iss-00227` が contract / classification / strict-legacy detection を実装する。
  - `iss-00233` が rollout / telemetry / future Auto-Lite readiness を実装する。

## 非目標（Non-goals）
- 初期 automatic Lite default は行わない。
- model confidence で gate を弱めない。
- 既存 Issue の全量 backfill を必須にしない。
- MyPy / Ruff rule の定義や tuning はこの ADR の scope にしない。

## 未確定事項（Open Questions）
- exact hard-trigger taxonomy と repo-specific override key は `iss-00227` / `iss-00233` の実装設計で確定する。ただし additive-only / tracked / source-bound / no weakening はこの ADR で固定済み。

## 参考（References）
- `requirement.md`
- `design.md`
- `20260623t012043z-research-deep-consultant-lite-rollout-report.md`
- `20260623t074452z-disc-adr-decision-synthesis-after-issue-226-closure.md`
