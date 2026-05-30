---
種別: interview
ID: "20260530t081243z-interview"
タイトル: "Node Creation No Github Surface Policy"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-05-30"
親: ["iss-00141"]
関連: []
scope: "issue"
scope_id: "iss-00141"
created_at: "2026-05-30T08:12:43Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - spec-dock/active/issue/discussions/20260529t153534z-disc-handoff-scratch.md
  - spec-dock/active/issue/discussions/20260530t081132z-research-local-only-node-creation-option-surface-research.md
  - spec-dock/active/epic/discussions/20260327t093000z-adr-github-mandatory-node-linkage.md
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py
  - tests/cli_runtime/test_new.py
  - src/spec_dock/assets/spec_dock/docs/reference_github.md
reflected_to:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/report.md
---

# 20260530t081243z-interview Node Creation No Github Surface Policy

## 位置づけ
- 用途: 重要判断に関わる一つの質問を、回答前の正式質問シートとして作成し、回答後に同じ artifact を完成 record にする。
- authority default: `proposed`。ユーザー回答と採用判断を反映した後は、必要に応じて `user-approved` または `synthesized` に更新する。
- 技術的に調べられることは先に docs / code / tests / ADR / discussions / primary source を確認する。
- 一つの `interview` artifact には一つの本質的な質問だけを書く。回答によって新しい高影響な曖昧さが見つかった場合は、追加質問をこの file に増やさず、次の unanswered `interview` を作成する。
- trivial な yes/no は、重要な判断、後続反映、回答証跡が必要なら `interview` を使い、そうでなければ issue comment や `scratch` で足りる。
- 回答から複数質問の synthesis が必要になったら `disc`、追加調査が必要になったら `research`、長期判断が固まったら `adr` を新規作成する。

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - AC / EC で `new ... --no-github` の期待結果を parser-level unknown option に固定するか、dedicated contract error の残存を許すかが変わる。
  - `design.md`:
    - parser から option を削除するか、help/docs から隠して handler-level reject を残すかが変わる。
  - `plan.md`:
    - red/green test obligation と docs drift removal 範囲が変わる。
  - `ADR`:
    - 新 ADR は不要見込み。accepted ADR の GitHub mandatory policy の具体化として扱う。
- chat 上の軽微な一問では足りない理由:
  - explicit `--no-github` invocation の扱いは CLI UX、互換性、テスト期待値、docs の複数 artifact に影響するため。

## 質問の目的 (必須)
- 対象者:
  - spec-dock maintainer / product owner。
- 何を明確にする質問か:
  - node creation における `--no-github` を「完全に option surface から削除する」のか、「help/docs からは消すが dedicated rejection path は残す」のかを決める。
- 回答が後続判断へ与える影響:
  - requirement の MUST / AC、design の変更方針、plan のテスト義務、docs 更新範囲が確定する。

## 質問 (必須)
- 質問:
  - `new initiative` / `new epic` / `new issue` に渡された `--no-github` は、今後どの挙動にしたいですか。
- 回答してほしいこと:
  - Option A / B / C のどれを採用するか。別案があれば、その意図と成功条件。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - accepted ADR は `initiative` / `epic` / `issue` の GitHub issue linkage mandatory と local-only / local fallback 廃止を決定済み。
  - current parser は `new initiative` / `new epic` / `new issue` に `--no-github` を登録している。
  - current handler は `--no-github` を dedicated contract error として reject している。
  - current tests は dedicated contract error と mutually-exclusive flag error を期待している。
  - current docs は `--no-github` を compatibility option として残るが reject される、と説明している。
  - issue scratch は「local-only option surface 自体を除去する」方向を示唆している。
- local context で解決できたこと:
  - GitHub mandatory policy そのものは再確認不要。
  - 削除対象は node creation の `new initiative` / `new epic` / `new issue` surface であり、`sync` / `deps` / `active` の cache/local `--no-github` ではない。
- まだ人間判断が必要な理由:
  - CLI 互換性と error UX のどちらを優先するかは運用判断であり、コードだけでは一意に決まらない。

## 回答案 (必須)
- Option A:
  - Parser-level removal。`new initiative|epic|issue --no-github` は unrecognized option として失敗し、help/docs/tests から node creation `--no-github` surface を消す。
- Option B:
  - Help/docs surface removal only。help/docs/tests からは消すが、hidden compatibility として explicit invocation は dedicated contract error を返し続ける。
- Option C:
  - 現状維持。`--no-github` は compatibility option として help/docs に残し、contract error として reject する。

## Codex の分析 (必須)
- 判断軸:
  - ユーザーが見える option surface を本当に消すか。
  - 既存利用者が誤って `--no-github` を打った場合の guidance を残すか。
  - accepted ADR の「local-only / local fallback は廃止」と docs の一貫性。
- tradeoff:
  - Option A はもっとも明確だが、エラー文は argparse の未認識オプションになり、既存 dedicated guidance は消える。
  - Option B は移行 guidance を残せるが、実装上は option surface が残るため issue title と少しずれる。
  - Option C は互換性が高いが、この issue の目的を満たさない可能性が高い。
- リスク:
  - Option A では `--no-github` が state command には残るため、docs で command context を正確に分けないと混乱する。
  - Option B / C では future maintainer が local-only creation path の復活余地と誤読する risk が残る。
- 具体シナリオ / edge case:
  - `new issue --help` に `--no-github` が表示されるか。
  - `new issue --create-github-issue --no-github` が mutually exclusive error になるか、unrecognized option になるか。
  - `sync --no-github` は引き続き valid か。

## Codex の推奨案 (必須)
- 推奨:
  - Option A。
- 理由:
  - issue title が `Remove Local Only Node Creation Option Surface` であり、scratch も「rejected path として残すのではなく surface itself を除去する」方向を示している。accepted ADR の mandatory policy とも最も整合する。
- 未回答時の影響:
  - requirement の AC が parser-level unknown option なのか dedicated contract error なのか固定できず、design / plan へ進めない。

## ユーザー回答 (回答後に必須)
- 回答:
  - Option A を採用する。
  - `new initiative` / `new epic` / `new issue` の `--no-github` は、テストを含めて完全に削除する。
  - コマンド入力部分だけではなく、内部的なロジックも整理する。
- 回答日時:
  - 2026-05-30T08:19:41Z

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - no
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - なし

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- 採用 / 棄却 / deferred の理由:
  - ユーザーが Option A を明示採用したため。
  - 追加指示として、node creation の入力 option だけでなく、`no_github` argument / handler branch / helper / tests など内部ロジックの整理も issue scope に含める。

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - `new initiative` / `new epic` / `new issue` の `--no-github` option surface を parser / help / docs / tests / internal logic から削除することを MUST とする。
  - explicit `--no-github` invocation は dedicated contract error ではなく parser-level unsupported option として扱う。
  - `sync` / `deps check` / `active set` の cache/local `--no-github` は対象外として保護する。
- `design.md`:
  - `commands/new.py` の argparse option、args dataclass、args factory、handler branch、dedicated helper の整理を扱う。
  - provider docs / dogfooding docs / tests の parity 更新を扱う。
- `plan.md`:
  - Red / Green では help からの非表示、explicit invocation の unsupported option、内部 `no_github` branch 削除、docs/tests drift removal を検証する。
- `ADR`:
  - 新 ADR は不要。accepted ADR `20260327t093000z-adr-github-mandatory-node-linkage.md` の具体化として扱う。
- reflected_to 更新方針:
  - `reflected_to` へ `spec-dock/active/issue/requirement.md` と `spec-dock/active/issue/report.md` を追加済み。

## 条件付き補足 (必要な場合だけ)
- PlantUML 図:
  - なし
- 詳細 tradeoff:
  - なし
- 後続 reflection proposal:
  - なし
- 追加で作る discussion docs:
  - なし
