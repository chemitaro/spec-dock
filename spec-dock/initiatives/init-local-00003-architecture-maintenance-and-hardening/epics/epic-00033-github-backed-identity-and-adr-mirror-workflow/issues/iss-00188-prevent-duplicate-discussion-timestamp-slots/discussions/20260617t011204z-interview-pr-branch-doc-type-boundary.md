---
種別: interview
ID: "20260617t011204z-interview"
タイトル: "PR Repair Batch Doc Type Boundary"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-06-17"
親: ["iss-00188"]
関連:
  - "20260617t003432z-interview"
scope: "issue"
scope_id: "iss-00188"
created_at: "2026-06-17T01:12:04Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "20260617t003432z-interview"
reflected_to: []
---

# 20260617t011204z-interview PR Repair Batch Doc Type Boundary

## 正式質問として扱う理由
- 影響する artifact:
  - `requirement.md`:
    - New doc type の名前と対象用途を固定する。
  - `design.md`:
    - Doc type catalog, template path, filename kind, validation/parser behavior を決める。
  - `plan.md`:
    - Tests and asset updates の対象を決める。
- chat 上の軽微な一問では足りない理由:
  - Doc type identifier は CLI input / filename / template / tests に現れる durable literal であり、誤ると後続の rename cost が高い。

## 質問の目的
- 対象者:
  - User / product owner
- 何を明確にする質問か:
  - User が追加したい "PR repair batch" related doc type の exact identifier と semantic boundary。
- 回答が後続判断へ与える影響:
  - `new doc <doc_type>` catalog に追加する literal と template design を確定する。

## 質問
- pressure-test question:
  - "PR branch" は音声入力誤りであり、実際には PR repair batch doc type を追加する理解でよいか。
- 質問:
  - 新しい doc type 名は `pr-repair-batch` でよいですか。意味は「PR repair workflow の batch artifact を runtime-generated path として作成する専用 doc type」とし、repair unit は別途 `disc` または将来の別 doc type で扱う、という理解でよいですか。
- 回答してほしいこと:
  - `pr-repair-batch` でよいか。
  - もし違う場合、望む doc type literal と対象用途。

## source-grounded context
- 確認済み:
  - 現行 doc type catalog: `scratch` / `interview` / `research` / `disc` / `adr` / `draft-requirement` / `draft-design` / `draft-plan`
  - User answer: `new doc` interface shape remains, no body/template option, but add PR repair batch related doc type.
- local context で解決できたこと:
  - Existing `disc` でも PR repair artifact は作れるが、user requested a type addition.
  - Filename kind と template catalog に durable literal が必要。
- まだ人間判断が必要な理由:
  - Initial "PR branch" wording was likely speech-to-text drift. Exact literal confirmation is required before changing CLI catalog.

## 回答案
- Option A:
  - `pr-repair-batch`
  - PR repair workflow の batch artifact 専用。Runtime-generated path を取得し、その後 skill/workflow が batch template sections を本文へ反映する。
- Option B:
  - `pr-repair`
  - PR repair workflow 全般の artifact。Batch/unit は本文 metadata で区別する。
- Option C:
  - `disc`
  - Doc type は増やさず、既存 `disc` を使い続ける。

## Codex の分析
- 判断軸:
  - User wording alignment, workflow specificity, catalog bloat, filename readability.
- tradeoff:
  - `pr-repair-batch` は今回の correction に合っており、batch artifact の用途が明確。
  - `pr-repair` は unit / batch を混ぜやすく、template semantics が曖昧。
  - `disc` 継続は catalog bloat を避けるが、user requested type addition を満たさない。
- リスク:
  - Doc type を増やすと parser/validator/docs/templates/tests の contract が増える。
  - `pr-repair-batch` 専用にすると、repair unit をどう扱うかは別途明記が必要。

## Codex の推奨案
- 推奨:
  - Option A: `pr-repair-batch`
- 理由:
  - User corrected the STT drift and explicitly stated `pr-repair-batch` is correct.
  - It matches the existing `github-pr-merge-preparer` batch template and avoids over-generalizing the artifact type.
- 未回答時の影響:
  - 未回答では canonical docs に doc type literal を固定しない。

## ユーザー回答
- answer capture:
  - User corrected the prior "PR branch" phrase as speech-to-text error. Correct doc type is `pr-repair-batch`.
- 回答:
  - `pr-repair-batch`
- 回答日時:
  - 2026-06-17T01:15:00Z

## 採用判断
- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - User explicitly corrected the intended literal to `pr-repair-batch`.
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes
