---
種別: interview
ID: "20260617t000842z-interview"
タイトル: "Node Dependency Validation Boundary Interview"
状態: "draft | answered | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-17"
親: ["iss-00193"]
関連: []
scope: "<initiative | epic | issue | local-topic>"
scope_id: "iss-00193"
created_at: "2026-06-17T00:08:42Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "20260617t000620z-research"
reflected_to:
  - "requirement.md"
---

# 20260617t000842z-interview Node Dependency Validation Boundary Interview

## 位置づけ
- 用途: 重要判断に関わる一つの質問を、回答前の source-grounded 正式質問シートとして作成し、回答後に同じ artifact を完成 record にする。
- authority default: `proposed`。ユーザー回答と採用判断を反映した後は、必要に応じて `user-approved` または `synthesized` に更新する。
- この artifact は answer capture / adoption target / reflection の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 技術的に調べられることは先に docs / code / tests / ADR / discussions / primary source を確認する。
- 一つの `interview` artifact には one essential question / 一つの本質的な質問だけを書く。回答によって新しい高影響な曖昧さが見つかった場合は、追加質問をこの file に増やさず、次の unanswered `interview` を作成する。
- trivial な yes/no は、重要な判断、後続反映、回答証跡が必要なら `interview` を使い、そうでなければ issue comment や `scratch` で足りる。
- 回答から複数質問の synthesis が必要になったら `disc`、追加調査が必要になったら `research`、長期判断が固まったら `adr` を新規作成する。

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - self / descendant / cycle rejection の意味、empty parent node への direct dependency 保存可否、acceptance criteria の具体条件が変わる。
  - `design.md`:
    - raw node-level validation helper を導入するか、既存 issue-level compiled validation に寄せるかが変わる。
  - `plan.md`:
    - test obligation と実装ステップ分割が変わる。raw graph validation を採用する場合は専用 red tests が必要になる。
  - `ADR`:
    - 現時点では不要。既存 Epic の `.meta.json` SoT / command-first policy の範囲内で閉じる見込み。
- chat 上の軽微な一問では足りない理由:
  - 回答が複数 canonical artifacts と regression strategy に反映されるため、回答前 artifact と採用証跡が必要。

## 質問の目的 (必須)
- 対象者:
  - SpecDock maintainer / product owner。
- 何を明確にする質問か:
  - `deps add/remove` を node-level に広げるとき、mutation 時点でどの graph consistency を必須にするか。
- 回答が後続判断へ与える影響:
  - 要件の acceptance criteria、design の validation boundary、plan の test matrix と implementation order が決まる。

## 質問 (必須)
- pressure-test question:
  - Should node-level dependency mutation validate the raw initiative/epic/issue dependency graph itself, even when the current issue-level compiled graph would be empty or non-blocking?
- 質問:
  - `deps add/remove` が initiative / epic / issue を受け付けるようになった後、保存前 validation は「raw node-level direct dependency graph」まで正本として検査しますか？
- 回答してほしいこと:
  - A / B / C のどれを採用するか、または別案を指定してください。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - GitHub Issue #193 body。
  - `spec-dock/active/epic/{requirement,design,plan}.md`。
  - `spec-dock/docs/reference_deps.md`。
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/deps_reader.py`。
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/mutate_deps.py`。
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py`。
  - `tests/cli_runtime/test_deps.py`。
  - `20260617t000620z-research-issue-193-node-dependency-mutation-research.md`。
- local context で解決できたこと:
  - Reader はすでに initiative / epic / issue `.meta.json.depends_on` を読み、配下 issue へ展開できる。
  - 現行 mutation path は `from` / `to` が issue でなければ `unsupported_node_kind` を返す。
  - 現行 duplicate/remove 判定は direct raw refs を解決できる構造を持つ。
  - `reference_deps.md` の mutation contract と help text は issue-only 前提なので更新対象。
- まだ人間判断が必要な理由:
  - Issue #193 は "cycle は拒否" と書くが、raw node graph cycle と compiled issue graph cycle のどちらを必須 reject にするかは明示していない。
  - Empty epic / empty initiative の direct dependency 保存を許す場合、compiled issue graph だけでは検出できない raw cycle が存在する。

## 回答案 (必須)
- Option A:
  - Raw node-level graph も mutation-time validation の正本にする。
  - `epic-a -> epic-b -> epic-a` のような raw cycle は、配下 issue が空でも拒否する。
  - `issue -> own parent epic` や `epic -> descendant issue` など、compiled self-edge や descendant edge を生む入力は保存前に拒否する。
- Option B:
  - 既存 issue-level compiled graph validation を主に維持し、raw node-level graph は最小限の self / descendant だけ見る。
  - Empty parent cycles は、現時点で issue-level blocker を生まない限り保存可能にする。
- Option C:
  - Mutation は保存だけ行い、`sync/check/validate` 側で後から警告または失敗させる。
  - Command-first safety より、planning 段階の自由度を優先する。

## Codex の分析 (必須)
- 判断軸:
  - command-first safety、future issue追加時の爆発防止、existing reader contract との整合、実装/テストの単純さ。
- tradeoff:
  - Option A は実装が少し増えるが、後から issue を追加した瞬間に既存 raw dependency が壊れるリスクを防げる。
  - Option B は差分が小さいが、empty epic/initiative 間の循環を保存できる余地が残る。
  - Option C は最も自由だが、親 Epic の fail-closed / no partial invalid state 方針と衝突しやすい。
- リスク:
  - Option A で raw node-level validation を強くしすぎると、planning 段階の粗い dependency intent を拒否しすぎる可能性がある。
  - Option B/C は `depends_on` が将来 issue-level graph へ展開されたとき、突然 `sync/check` が壊れる可能性がある。
- 具体シナリオ / edge case:
  - Empty `epic-a` depends on empty `epic-b`, then `epic-b` depends on `epic-a`: raw cycle だが compiled issue graph は空。
  - `iss-x` depends on its parent `epic-a`: parent expansion includes `iss-x` and produces self-edge。
  - `epic-a` depends on child `iss-x`: descendant dependency。
  - `epic-a` depends on `epic-b` where `epic-b` has no issues yet: valid metadata plus warning/no blocker behavior is expected by Issue #193。

## Codex の推奨案 (必須)
- 推奨:
  - Option A。
- 理由:
  - Issue #193 の "self dependency / descendant dependency / cycle は拒否" を最も素直に満たせる。
  - 親 Epic の fail-closed mutation contract と一致する。
  - Empty parent dependency metadata を保存できる要件と、将来壊れる raw cycle を防ぐ要件を両立できる。
  - Existing issue->issue behavior は raw graph validation を通しても維持できる。
- 未回答時の影響:
  - requirement / design / plan の validation boundary を確定できず、implementation-ready には進めない。

## ユーザー回答 (回答後に必須)
- answer capture:
  - Option A を採用する。
  - 依存が循環しないようにする必要がある。
  - 現時点で issue 範囲では矛盾が発生しない場合でも、空だった epic / initiative に後から issue を追加した途端に問題が発生し得る。
  - そのため、raw node-level graph の循環依存は保存前にブロックする。
- 回答:
  - Option A: raw node-level graph も mutation-time validation の正本にする。
- 回答日時:
  - 2026-06-17

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - no
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - N/A

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - ユーザー回答が Issue #193 の cycle rejection boundary を具体化したため採用する。
  - 空 epic / initiative に対する direct dependency metadata を許可しつつ、将来 child issue 追加で循環が顕在化する invalid state を保存しない requirement として扱う。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - `deps add/remove` は initiative / epic / issue node id を受け付ける。
  - Mutation は保存前に raw node-level direct dependency graph の self / descendant / cycle を拒否する。
  - Empty epic / initiative でも valid な direct dependency metadata は保存できるが、raw cycle は配下 issue の有無に関係なく拒否する。
- `design.md`:
  - Existing issue-level compiled validation に加え、raw node-level graph validation helper または同等の validation path を設計する。
- `plan.md`:
  - Raw cycle rejection、empty parent valid edge、descendant/self rejection、existing issue->issue regression を test obligation に含める。
- `ADR`:
  - 現時点では不要。親 Epic の command-first / fail-closed policy 内の具体化として扱う。
- reflected_to 更新方針:
  - Canonical docs へ採用した section を `reflected_to` に追加する。
- adoption reflection:
  - この interview は `requirement.md` の未確定事項解消と受け入れ条件に反映する。

## 条件付き補足 (必要な場合だけ)
- PlantUML 図:
  - N/A: 質問回答は requirement boundary の文章化で足りるため、この interview では図を追加しない。
- 詳細 tradeoff:
  - N/A: tradeoff は `Codex の分析` に記録済み。
- 後続 reflection proposal:
  - `requirement.md` の non-negotiable constraint と acceptance criteria に反映済み。
- 追加で作る discussion docs:
  - なし。
