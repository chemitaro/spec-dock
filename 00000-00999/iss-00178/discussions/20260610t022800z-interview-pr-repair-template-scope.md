---
種別: interview
ID: "20260610t022800z-interview"
タイトル: "PR Repair Template Scope"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-06-10"
親: ["iss-00178"]
関連:
  - "20260609t151424z-research-review-feedback-triage-policy.md"
  - "20260609t152616z-research-historical-p2-p3-review-analysis.md"
  - "20260609t154515z-disc-pr-repair-triage-workflow-proposal.md"
  - "github-pr-merge-preparer"
  - "github-pr-observation"
scope: "issue"
scope_id: "iss-00178"
created_at: "2026-06-10T02:28:00Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "proposed"
adoption_status: "unreviewed"
derived_from:
  - "spec-dock/active/issue/requirement.md"
  - "spec-dock/active/issue/discussions/20260609t154515z-disc-pr-repair-triage-workflow-proposal.md"
  - "spec-dock/docs/rules/issue/discussions.md"
  - "spec-dock/docs/reference_naming.md"
  - "Deep Consultant: 019eaf82-3fe3-7a82-a610-7084e43ddcf9"
reflected_to: []
---

# 20260610t022800z-interview PR Repair Template Scope

## 正式質問として扱う理由

- 影響する artifact:
  - `requirement.md`: この issue の必須スコープに runtime command / template variant 実装を含めるか、skill / docs / skeleton guidance に限定するかが変わる。
  - `design.md`: `github-pr-merge-preparer` skill の workflow 変更だけで閉じる設計か、`new doc` runtime / template registry / shipped templates / tests まで設計するかが変わる。
  - `plan.md`: 変更対象、テスト範囲、受け入れ条件、リスクが大きく変わる。
  - ADR: 現時点では ADR までは必須ではないが、discussion artifact catalog や runtime template extension を恒久方針にする場合は ADR 候補になり得る。
- chat 上の軽微な一問では足りない理由:
  - ユーザーは「専用シート」「テンプレート」「ディスカッションディレクトリに配置するコマンド」を求めている。
  - 一方で、現行提案は初期実装では既存 `disc` を使い、first-class doc type や runtime template variant は作らない方針を推奨している。
  - どちらを採用するかで実装範囲と spec-reviewer の評価基準が変わる。

## 質問の目的

- 対象者:
  - iwasawayuuta
- 何を明確にする質問か:
  - `iss-00178` で実装する PR repair triage artifact の作成支援を、skill / docs 内の専用 skeleton として扱うのか、SpecDock runtime command の template support として扱うのか。
- 回答が後続判断へ与える影響:
  - `requirement.md` の必須 / 対象外 / 受け入れ条件を確定する。
  - `design.md` で runtime layer まで扱うか、agent-tooling asset だけを扱うかを確定する。
  - `plan.md` のテスト対象が skill text inspection 中心か、CLI/runtime unit test まで含むかを確定する。

## 質問

- pressure-test question:
  - この issue では、PR repair batch / repair unit の専用シート作成を **runtime command として実装** しますか、それとも **既存 `disc` を使う skill / docs 上の専用 skeleton** としてまず実装しますか。
- 質問:
  - `./spec-dock/scripts/spec-dock new doc disc --template pr-repair-batch` / `--template pr-repair-unit` のような runtime template option まで、この issue の必須スコープに含めますか。
- 回答してほしいこと:
  - A または B のどちらを今回の要件に採用するか。
  - B を採用する場合、`--template` option 名までこの issue で固定するか。

## source-grounded context

- 確認済みの docs / code / discussions:
  - `spec-dock/active/issue/requirement.md`: 現在はテンプレート状態で、スコープ未確定。
  - `20260609t154515z-disc-pr-repair-triage-workflow-proposal.md`: 初期実装では既存 `disc` を使うが、通常の自由記述ではなく PR repair batch 専用テンプレートとして扱う案を推奨している。将来の理想として `new doc disc --template pr-repair-batch` も記載している。
  - `20260609t152616z-research-historical-p2-p3-review-analysis.md`: P2 / P3 finding の多くは対処価値があり、修正前 triage gate の必要性を支持している。
  - `spec-dock/docs/rules/issue/discussions.md`: 現行 discussion catalog は `scratch` / `interview` / `research` / `disc` / `adr` / `draft-requirement` / `draft-design` / `draft-plan`。
  - `spec-dock/docs/reference_naming.md`: `new doc <type>` は現行 catalog に基づく。`--template` variant は現行 contract としては確認できない。
- local context で解決できたこと:
  - 新しい first-class doc type を作らなくても、既存 `disc` の flat Markdown として batch / unit artifact を保存できる。
  - skill に skeleton と作成コマンド例を置けば、PR repair triage workflow 自体は runtime 変更なしに実装できる。
  - runtime `--template` を追加する場合は、CLI/parser/template rendering/docs/tests まで scope が広がる。
- まだ人間判断が必要な理由:
  - ユーザーはシンプルさを重視しつつ、AI agent が迷わない deterministic な作成支援も重視している。
  - runtime command support は ergonomics と再現性を上げるが、この issue の初期目的である PR repair triage workflow hardening より実装範囲が広がる。

## 回答案

- Option A: skill / docs / skeleton only
  - この issue では `github-pr-merge-preparer` skill に PR Repair Triage Gate を追加する。
  - PR repair batch / repair unit は既存 `disc` として作成する。
  - skill 内に専用 skeleton、分類値、作成コマンド例、必須記入項目を埋め込む。
  - runtime `new doc --template ...` は対象外または follow-up とする。
- Option B: runtime template option まで含める
  - この issue で `new doc disc --template pr-repair-batch` と `new doc disc --template pr-repair-unit` を実装する。
  - provider-side runtime / template assets / docs / tests / dogfooding workspace update まで含める。
  - `github-pr-merge-preparer` skill はその command を使うように更新する。
- Option C: first-class doc type まで含める
  - `pr-repair-batch` / `pr-repair-unit` を discussion catalog の新 doc type として追加する。
  - 現時点では catalog 増加と validation / naming / docs 影響が大きいため非推奨。

## Codex の分析

- 判断軸:
  - 実装範囲をこの issue の目的に閉じるか。
  - agent が迷わない deterministic workflow をどこまで runtime に持たせるか。
  - SpecDock discussion catalog / runtime contract を増やす必要が今あるか。
- tradeoff:
  - Option A は小さく実装でき、すぐに PR repair triage の運用を改善できる。ただし skeleton の転記は skill 依存になり、CLI だけで専用シートを生成する体験にはならない。
  - Option B は agent の作成手順がより決定的になり、テンプレート欠落を減らせる。ただし runtime 変更、テスト、dogfooding update が増え、この issue のサイズが大きくなる。
  - Option C は概念上はきれいだが、catalog 増加の恒久コストがあり、現時点では過剰。
- リスク:
  - Option A で進める場合、skill 内 skeleton と将来 template が乖離する可能性がある。
  - Option B で進める場合、PR repair triage workflow の本題に加えて runtime template variant の設計・テストが必要になり、issue が膨らむ。
  - Option C で進める場合、discussion doc taxonomy が増えてシンプルさを損なう。
- 具体シナリオ / edge case:
  - PR に CI failure と review finding が複数同時に出たとき、batch artifact は `disc` として十分に保存できる。
  - ただし agent が command だけで専用 skeleton を得たい場合は、Option B の方がミスが少ない。

## Codex の推奨案

- 推奨:
  - Option A を今回の要件に採用する。
- 理由:
  - 現行 proposal と整合しており、`github-pr-merge-preparer` の workflow hardening という issue 目的に集中できる。
  - 既存 `disc` catalog の範囲内で、batch report と unit discussion の dedicated sheet を実現できる。
  - runtime `--template` support は有用だが、設計対象が CLI/runtime/template registry へ広がるため、必要性が実運用で確認できてから follow-up で扱う方が安全。
- 未回答時の影響:
  - 要件定義書の必須スコープを確定できない。
  - 設計書・実装計画書の対象ファイルと検証コマンドが決まらない。

## ユーザー回答

- answer capture:
  - 複数の review / CI review 結果 / ログを分析し、review の妥当性、修正必要性、修正案を複数の関心ごととして 1 枚にまとめる用途では、既存の通常 `disc` template では不十分。
  - 少なくとも PR repair batch については専用シートが必要。
  - 一方で repair unit については、既存の discussion sheet / `disc` template で対応できる可能性がある。
  - この考えについて客観的な分析、Deep Consultant の分析を求める。
- 回答:
  - batch は専用シートが必要ではないか。unit は既存 `disc` で対応できるのではないか。
- 回答日時:
  - 2026-06-10

## 追加確認の要否

- 追加確認が必要か:
  - no
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - なし

## 採用判断

- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - Deep Consultant 分析と runtime 確認の両方で、batch 専用 structured sheet と unit 既存 `disc` の分離は妥当と判断した。
  - `new doc` runtime に `--template` はなく、今回 runtime 拡張まで含めるとスコープが広がるため、初期実装では skill / docs 内 skeleton を採用する。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意

- `requirement.md`:
  - PR repair batch は existing `disc` として作成するが、専用 structured skeleton を必須にする。
  - repair unit は existing `disc` として扱い、必須チェックリストで補強する。
  - runtime `--template` は対象外 / follow-up として明記する。
- `design.md`:
  - `github-pr-merge-preparer` skill に PR Repair Triage Gate、batch skeleton、repair unit checklist、merge-prepared gate を設計する。
  - `github-pr-observation` は evidence collection 境界を維持する。
- `plan.md`:
  - skill/docs inspection と scenario validation が中心。
  - runtime CLI test / generated artifact assertion は今回の必須検証に含めない。
- `ADR`:
  - 今回は必須ではない。
  - 将来 first-class doc type または runtime template support を追加する場合は ADR 候補。
- reflected_to 更新方針:
  - `requirement.md` 作成時に反映する。
- adoption reflection:
  - `report.md` Evidence Adoption Ledger へ反映する。
