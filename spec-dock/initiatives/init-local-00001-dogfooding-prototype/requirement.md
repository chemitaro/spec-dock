---
種別: 要件定義書（Initiative）
ID: "init-local-00001"
タイトル: "Dogfooding Prototype"
関連GitHub: []
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-03-25"
---

# init-local-00001 Dogfooding Prototype — 要件定義（WHAT / WHY）

## 目的（Outcome）
- Primary:
  - `spec-dock` 自身を `spec-dock` で運用できる、実用可能な dogfooding prototype を維持し、残課題を次の投資判断へ切り分けられる状態にする。
  - provider 側実装と consumer/generated workspace を一貫した contract でつなぎ、repo docs を正本として継続運用できるようにする。
- Secondary:
  - dogfooding で得た durable lesson を initiative 文書へ昇格し、会話や一時的 issue trace へ依存しない判断基盤を整える。
  - repo-scope exact resolution、fail-closed ambiguity、no-origin continuity、diagnostics、parity discipline を prototype の基盤契約として固定する。
  - 残る manual remediation / operator guidance / lifecycle expansion を、次の epic / initiative へ無理なく handoff できるようにする。

## 背景と Why now
- 現状の課題:
  - 2026-03-14 時点の initiative 文書は roadmap planning 前提で止まっており、現在の runtime contract と運用 reality を十分に反映していない。
  - その後の dogfooding と corrective work により、`doctor`、repo-aware exact targeting、checked-in parity、create/recovery guardrail、manual rerun baseline が成立した。
  - 一方で legacy unscoped metadata の manual remediation や、operator guidance の不足はまだ残っている。
- 影響:
  - initiative 文書が stale なままだと、すでに成立した contract と remaining work の境界が読めず、次の投資判断がぶれる。
  - roadmap だけを読むと、現在の runtime が「まだ使えない」ように誤解される一方、残課題の位置づけも曖昧になる。
- なぜ今やるか:
  - manual rerun を含む再検証で major path の usability が確認できたため、initiative 正本を current reality へ同期するタイミングに入った。
  - `spec-deps` から durable lesson を新しい initiative discussion へ移したため、いまなら issue-28 micro-history を持ち込まずに文書更新できる。
- 情報源:
  - `discussions/004-adr-runtime-cli-layered-architecture.md`
  - `discussions/005-disc-review-loop-and-outcome-matrix-lessons.md`
  - `discussions/006-disc-repo-scope-and-create-state-lessons.md`
  - `discussions/007-disc-manual-rerun-current-state.md`
  - `discussions/009-disc-initiative-doc-drift-analysis.md`

## 成功指標
- Metric-001:
  - Baseline:
    - initiative requirement/design/plan は roadmap 寄りで、現在の usable runtime contract と remaining gaps を明確に区別できていない。
  - Target:
    - initiative 正本を読めば、dogfooding runtime が「通常利用可能だが caveat を伴う prototype」であること、そしてその caveat が何かを判断できる。
  - 計測方法:
    - requirement/design/plan が exact repo-scoped resolution、fail-closed ambiguity、no-origin continuity、doctor / parity discipline、manual remediation gap を明示していること。
  - 判定時期:
    - initiative refresh 完了時。
- Metric-002:
  - Baseline:
    - 残課題が roadmap と corrective trace に分散しており、何が done / ongoing / remaining なのか読み取りにくい。
  - Target:
    - initiative plan が established capability と remaining investment を分けて表現し、次の epic / initiative の切り出し判断ができる。
  - 計測方法:
    - plan.md に established baseline、remaining follow-up、exit / handoff 条件が整理されていること。
  - 判定時期:
    - initiative refresh 完了時、および次の epic 分解時。

## スコープ
- MUST:
  - `spec-dock` 自身を `spec-dock` で管理する dogfooding prototype を正本として維持する。
  - provider/source と consumer/generated workspace の責務分離を継続する。
  - runtime の current baseline を次の契約として固定する:
    - canonical GitHub URL と `--id` による repo-scoped exact resolution
    - overlap 下の bare numeric / `--github-issue` ambiguity fail-closed
    - already-normalized metadata の no-origin continuity
    - `doctor` / `validate` / `sync` を中心とした diagnostics / recovery 導線
    - provider/check-in parity を explicit guardrail として維持すること
  - legacy unscoped current-repo metadata は automatic self-heal の対象ではなく、manual remediation gap として扱う。
  - additive migration、fail-safe / fail-closed posture、repo-safe external mutation を維持する。
  - dogfooding で見つかった durable lesson と remaining work を、継続的に backlog 化できるようにする。
- MUST NOT:
  - GitHub issue を必須化して local-only path を排除しない。
  - overlap や no-origin の曖昧さを silent mutation で自動解消しない。
  - provider/check-in parity を optional quality concern として扱わない。
  - existing artifact / metadata の意味を破壊的に置き換えない。
- OUT OF SCOPE:
  - issue-28 の個別 corrective trace を initiative 正本へ再掲すること
  - legacy unscoped metadata に対する automatic persistence upgrade
  - overlap-heavy workspace における bare numeric selector の convenience path 復活
  - 日常運用を超えた viewer extras / dashboard extras / naming extras
  - 本 initiative の外で管理すべき広範な metadata automation や PR helper

## 境界
- Always:
  - provider 側の source of truth は `src/spec_dock/` に置く。
  - `spec-dock/` は consumer/generated workspace と active docs の正本として扱う。
  - `1 issue = 1 authority` を維持する。
  - artifact は authority ではなく projection/cache として扱う。
  - 曖昧さがあるときは silent correction ではなく fail-closed を優先する。
  - dogfooding で得た durable lesson は initiative / epic / issue docs へ昇格する。
- Ask:
  - manual remediation を current initiative の scope に含めるか、別 initiative に分離するか
  - GitHub close/reopen や authority transfer を次の主要投資に据えるか
  - warning から hard error への hardening 切り替え
- Never:
  - hidden local history への自動巻き戻し
  - authority transfer に伴う id/path rename
  - overlap / no-origin / legacy metadata を silent remote mutation で修復すること

## ステークホルダー / 影響範囲
- 利用者:
  - `spec-dock` を使う coding agent
  - `spec-dock` を repo docs 正本として運用する開発者
- 運用者:
  - この repo の maintainer
  - dogfooding workspace の active docs と issue state を扱う人
- 開発者:
  - installer を保守する開発者
  - runtime CLI と shipped scaffold を保守する開発者
- 影響システム / 領域:
  - `src/spec_dock/cli.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`
  - shipped scaffold docs/templates/system
  - local dogfooding workspace `spec-dock/`
  - manual test artifacts と initiative discussions

## 非交渉制約
- 互換性:
  - additive migration を優先し、existing artifact と existing consumer behavior を壊さない。
  - already-normalized metadata continuity を壊さず、legacy gap は explicit に扱う。
- セキュリティ / 監査:
  - external mutation は opt-in でのみ許可する。
  - wrong-repo risk を避ける repo-aware targeting / preflight を維持する。
- 性能 / 可用性:
  - sync/update/validate/doctor の信頼性を落とさない。
  - partial/stale/ambiguous failure を説明可能にする。
- 運用:
  - repo docs を正本とし、会話ログは正本にしない。
  - provider/source と generated workspace の役割を混同しない。
  - bare numeric selector より canonical URL / `--id` を優先する運用 guidance を維持する。

## リスク / 依存
- R-001:
  - parity drift が再発すると、provider/source と checked-in runtime の contract が乖離し、dogfooding で誤検証が起きる。
- R-002:
  - legacy unscoped metadata と no-origin 運用を誤って理解すると、runtime bug ではなく fail-closed behavior を障害と誤認しやすい。
- R-003:
  - remaining work と established capability の境界が曖昧だと、不要な自動化や unsafe remediation へ投資が戻る。

## 未確定事項
- Q-001:
  - 質問:
    - legacy unscoped current-repo metadata 向けの manual remediation を、この initiative の remaining work として扱うか、次 initiative に分離するか。
  - 選択肢:
    - A:
      - current initiative の remaining work として保持する。
    - B:
      - current initiative は usable prototype までで閉じ、manual remediation は別 initiative に切り出す。
  - 推奨案:
    - B。現在の主要 contract は成立しており、残課題は correctness bug より operator remediation / guidance の投資判断に寄っている。
  - 影響範囲:
    - plan の remaining follow-up ownership
    - prototype completion 判定の仕方
