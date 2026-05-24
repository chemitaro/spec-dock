---
種別: ADR（Architecture Decision Record）
ID: "20260524t133442z-adr"
タイトル: "Flat Scope Local Discussion Drafts"
状態: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-05-25"
親: ["iss-00127"]
authority: "accepted"
derived_from:
  - "20260524t131259z-research-scoped-discussion-draft-authoring-model-analysis.md"
  - "user decision 2026-05-24"
  - "user decision 2026-05-25"
intended_targets:
  - "iss-00127 requirement.md"
  - "iss-00127 design.md"
  - "iss-00127 plan.md"
reflected_to:
  - "iss-00127 requirement.md"
  - "iss-00127 design.md"
  - "iss-00127 plan.md"
---

# 20260524t133442z-adr Flat Scope Local Discussion Drafts

## 位置づけ
- この ADR は、delegated authoring の draft / analysis 成果物を `discussions/` 配下でどのように管理するかを固定する。
- この ADR は、`iss-00127` の要件・設計・実装計画で採用するファイル配置と運用ルールの根拠である。

## 結論（Decision） (必須)
- Scope-local `discussions/` は、既存の timestamp-prefixed naming rule に従う flat Markdown document collection として運用する。
- `discussions/system-architect/`、`discussions/implementation-planner/`、`discussions/<run>/` のような delegated authoring 専用サブディレクトリは採用しない。
- system-architect / implementation-planner / consultant / reviewer などの sub-agent 成果物も、対象 initiative / epic / issue の `discussions/` 直下に 1 doc = 1 Markdown file として置く。
- File name は `<ts>-<kind>-<slug>.md` を維持し、slug は role-first / run-first ではなく canonical target と論点を表す。
- `discussions/` 配下の draft / research / disc は phase authority / implementation authority を持たない。一方で、accepted ADR は architecture decision authority を持ち得る。
- 実行可能な仕様 authority は、main orchestrator が accepted ADR や discussion draft を読み、`requirement.md` / `design.md` / `plan.md` / `report.md` に再記述した時点で成立する。
- sub-agent は canonical docs を直接編集しない。
- sub-agent は、対象 initiative / epic / issue の scope-local `discussions/` 直下に flat Markdown draft / analysis / report を直接作成・編集できる。これは、agent context に残る揮発的な情報ではなく、設計上の情報伝達と意思決定材料をファイルベースで永続化するための許可である。
- main orchestrator は `discussions/` の draft / research / disc / adr を読んで採用・部分採用・却下・延期・stale を判断し、採用部分だけ canonical docs に再記述する。

## 背景（Context） (必須)
- `epic-00112` の v2 implementation は、write-capable delegated draft authoring を実現するために manifest / Permission Profile / session-invocation / input authority / EAL などを導入した。
- しかしユーザーは、sub-agent が canonical `design.md` / `plan.md` を直接編集することは権限過多であり、draft は `discussions/` 配下に置くべきだと再判断した。
- 2026-05-25 の追加判断では、sub-agent を proposal-only に落とす案は採用しない。安全性だけを最大化するよりも、harness engineering / context engineering として、sub-agent が自分の分析・draft を scope-local `discussions/` に直接保存できる方が、コンテキスト圧縮で失われる情報を減らし、協働効率を高められるためである。
- さらに、agent 別 directory や run/task directory を作ると、既存の `discussions/` 命名規則とずれ、どの文書が時系列・論点上どこにあるかが読みづらくなる。
- spec-dock の既存 discussion rule は、`<ts>-<kind>-<slug>.md` を `discussions/` 直下に置く flat model を標準としている。
- delegated authoring でもこの既存 model を拡張し、別体系を作らないことを優先する。

## 選択肢（Options considered） (必須)
- 選択肢 A: flat topic-first files under `discussions/`
  - 概要:
    - `discussions/20260524t140000z-draft-design-scope-local-authoring.md` のように、既存 naming rule に従って直下へ置く。
  - 良い点（Pros）:
    - 既存の `spec-dock new doc` model と一致する。
    - `ls` / `rg` / Git diff で時系列に追いやすい。
    - agent-first ではなく topic-first で読める。
    - issue / epic / initiative に同じルールを適用できる。
    - migration が軽い。
  - 悪い点 / 制約（Cons）:
    - 大量の discussion docs がある scope では一覧が長くなる。
    - status / role / target canonical doc は front matter と本文で補う必要がある。
  - 採否:
    - 採用。
- 選択肢 B: per-agent directories
  - 概要:
    - `discussions/system-architect/` や `discussions/implementation-planner/` を作り、その配下に draft を置く。
  - 良い点（Pros）:
    - agent ごとの成果物は見つけやすい。
  - 悪い点 / 制約（Cons）:
    - 作者中心の構造になり、canonical artifact や論点との対応が弱くなる。
    - 同じ論点を複数 agent が扱うと読むべき場所が分散する。
    - reviewer / orchestrator が全体像を得るために agent directory を巡回する必要が出る。
  - 棄却理由（棄却する場合）:
    - delegated authoring の成果物は agent ではなく scope / topic / canonical target を中心に読むべきであるため棄却。
- 選択肢 C: run/task directories
  - 概要:
    - `discussions/20260524t160000z-system-architect-design/` のようなディレクトリを作り、`draft.md` / `questions.md` / `evidence.md` を束ねる。
  - 良い点（Pros）:
    - 1 回の実行に複数成果物がある場合の監査性は高い。
  - 悪い点 / 制約（Cons）:
    - 探索が深くなり、既存の flat discussion rule とずれる。
    - 通常の draft authoring には構造が重い。
    - run が増えると最新論点を探しにくい。
  - 棄却理由（棄却する場合）:
    - 今回はシンプルな単一運用ルールを優先するため、例外としても採用しない。
- 選択肢 D: sub-agent proposal-only / orchestrator-only file write
  - 概要:
    - sub-agent は Markdown proposal を返すだけにし、main orchestrator だけが `discussions/` にファイルを作る。
  - 良い点（Pros）:
    - write boundary は最も単純で、host permission が狭くなる。
  - 悪い点 / 制約（Cons）:
    - sub-agent の作業結果が一度 conversation context に滞留し、context compaction や伝言ゲームで情報が失われやすい。
    - agentic collaboration の中間成果物が file-based source of context にならず、orchestrator の転記負荷が増える。
    - harness engineering / context engineering の目的である「自律的な specialist が persistent evidence を残す」性質が弱くなる。
  - 棄却理由（棄却する場合）:
    - canonical docs への直接 write 禁止で主要な authority risk は抑えられるため、`discussions/` への直接 draft write は許容する。安全性を最大化する proposal-only より、ファイルベースの協働効率とコンテキスト永続化を優先する。

## 判断理由（Rationale） (必須)
- spec-dock は docs を source of truth とするため、discussion docs も人間と agent が同じ規則で探索できることが重要である。
- 既存の discussion rules は flat timestamp-prefixed docs を標準としており、delegated authoring だけ別体系にすると学習コストと運用分岐が増える。
- agent-first directory は、agentic engineering の内部都合を文書構造に持ち込みすぎる。
- run/task directory は、重い manifest / probe / session-invocation を退役する方向と相性が悪い。
- flat timestamp-prefixed docs と lightweight Markdown front matter で、必要な provenance / status / intended target は十分に表現できる。
- sub-agent に scope-local `discussions/` write を許すことで、agent が持つ一時的な分析・設計判断を会話 context から persistent project context へ移せる。
- proposal-only は安全だが、sub-agent の専門的な分析を main orchestrator が再転記する伝言ゲームを増やす。今回の目的は、安全性を保ちながらも agentic engineering の協働効率を高めることである。

## 影響（Consequences） (必須)
- 良い影響（Positive）:
  - `discussions/` を時系列で読めば、論点・draft・調査の流れを追える。
  - sub-agent 出力の置き場が単純になり、`.agents` / `.codex` / global draft store を使わずに済む。
  - canonical docs と discussion drafts の境界が明確になる。
  - sub-agent の中間成果物が conversation context ではなく file-based context として残る。
  - issue / epic / initiative で同じ運用ルールを使える。
- 悪い影響 / 将来負債（Negative / Debt）:
  - 1 scope に大量の discussion docs がある場合、一覧が長くなる。
  - 複数ファイルを束ねる機能は directory ではなく naming / front matter / future list command に頼る。
  - draft status の整理を怠ると、flat directory 内に stale docs が残り続ける。
  - proposal-only より write boundary は広い。sub-agent output の diff guard と adoption ledger で補完する必要がある。
- 影響範囲（コード/テスト/運用/データ）:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-implementation-planner/SKILL.md`
  - `.agents/skills/spec-dock-system-architect/SKILL.md`
  - `.agents/skills/spec-dock-implementation-planner/SKILL.md`
  - `src/spec_dock/assets/install_root/.codex/agents/*.toml`
  - `.codex/agents/*.toml`
  - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
  - `src/spec_dock/assets/spec_dock/docs/rules/*/discussions.md`
  - discussion templates / managed asset tests
- 移行/ロールバック:
  - 既存 `iss-00126` の manifest / profile / probe 証跡は削除せず、historical evidence として残す。
  - 新規 delegated authoring output から flat discussion docs に切り替える。
  - 問題があれば canonical docs は main orchestrator だけが編集する原則を維持したまま、front matter / list helper を調整する。
- 追加対応（Follow-ups / Epic / Issue / ADR）:
  - `iss-00127` requirement / design / plan へ反映する。
  - 必要なら future issue で `spec-dock new doc` に `draft-requirement` / `draft-design` / `draft-plan` kind を追加する。

## 参考（References） (任意)
- 関連仕様（requirement/design/plan/report）:
  - `iss-00127/requirement.md`
  - `iss-00127/design.md`
  - `iss-00127/plan.md`
- 元になった discussion docs（derived_from）:
  - `20260524t131259z-research-scoped-discussion-draft-authoring-model-analysis.md`
- 反映先（reflected_to）:
  - `iss-00127/requirement.md`
  - `iss-00127/design.md`
  - `iss-00127/plan.md`
- PR/実装:
  - `epic-00112` PR #119 historical implementation context
