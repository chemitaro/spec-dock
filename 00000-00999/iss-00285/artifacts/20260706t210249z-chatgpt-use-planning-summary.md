# ChatGPT Use planning summary for iss-00285

## 実行概要

- 実行方式: `chatgpt-use` skill / GPT-5.5 Pro Extended / browser mode
- セッション slug: `specdock-iss-00285-planning`
- 目的: current branch と Issue / Epic docs、`iss-00284` の実装済み preflight helper を参照し、`iss-00285` の要件・設計・実装計画を具体化する
- GitHub connector: current branch を参照できたことを ChatGPT 回答内で確認
- 採用状態: `adopted`。ただし ChatGPT output は evidence-only であり、canonical authority / reviewer pass ではない。

## 採用した結論

`iss-00285` は、`scripts/authoring-pack/` 配下に dogfood-only の ZIP / tree validator を追加する最小スライスとして実装する。

- 主経路: actual `.zip` を入力し、central directory を展開前に検査する。
- 補助経路: すでに隔離済みの extracted directory tree を検査する。ただし tree input は ZIP central directory safety evidence の代替にしない。
- 出力: `validation-report.json` と `validation-summary.md`。
- status taxonomy: `pass` / `fail` / `blocked` / `stale` / `rejected` / `deferred` / `unreviewed` を `iss-00284` と揃える。
- 実装先: `scripts/authoring-pack/authoring_pack_review.py` と `scripts/authoring-pack/review_chatgpt_authoring_pack.py`。
- テスト先: `tests/manual_tests/test_review_chatgpt_authoring_pack.py`。

## 採用した設計境界

- ChatGPT output、ZIP、tree、validation report は evidence-only candidate。
- canonical docs の直接上書き、`.assurance.json` mutation、reviewer pass claim、PR 作成 claim は禁止。
- runtime command 追加は対象外。
- unsafe path / symlink / nested archive / binary / secret-looking entry / unsafe authority claim は `rejected`。
- mandatory metadata 欠落は `fail`。
- source hash mismatch は `stale`。
- preflight missing / unreadable は `blocked`。
- staged diff rendering、profile-controlled skeleton fill、EAL final adoption は後続 Issue へ `deferred`。

## 採用した検証方針

- valid ZIP / valid tree の report 生成。
- path traversal / absolute path / hidden path / symlink / nested archive / binary の rejected。
- manifest / provenance / adoption-map 欠落の fail。
- source hash mismatch の stale。
- reviewer pass / adopted / canonical overwrite / `.assurance.json updated` claim の rejected。
- private key / token / host-local absolute path の redaction。
- canonical docs / `.assurance.json` no-mutation。
- unowned output dir preservation。

## 未採用または後続に送った内容

- tracked binary ZIP fixture の大量配置は採用しない。pytest 内生成を優先し、repo の fixture churn を抑える。
- exact `adoption/adoption-map.json` schema の拡張は `iss-00286` 以降で扱う。
- runtime promotion と配布 command 化はこの Issue では扱わない。

## 採用先

- `requirement.md`: scope、non-scope、input/output、status taxonomy、AC を具体化。
- `design.md`: module split、schema model、path / ZIP / content rules、report shape を具体化。
- `plan.md`: files to create、S01〜S99、test cases、reviewer obligations を具体化。
- `report.md`: EAL / Delegated Draft Evidence / Grade Specialist Evidence / Reviewer Gate Status / Closure Evidence に反映。
