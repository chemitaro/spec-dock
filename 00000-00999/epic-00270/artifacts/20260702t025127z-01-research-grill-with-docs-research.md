---
種別: research
ID: "20260702t025127z-01-research"
タイトル: "Grill With Docs Research"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["epic-00270"]
関連:
  - "20260702t025127z-adr"
authority: "synthesized"
derived_from:
  - "ChatGPT GPT-5.5 Pro browser synthesis session: grill-with-docs-synthesis"
  - "https://www.aihero.dev/grill-with-docs"
  - "https://www.aihero.dev/skills-grill-me"
  - "https://www.aihero.dev/things-people-get-wrong-with-grill-me-and-grill-with-docs"
  - "https://www.aihero.dev/skills/skills-changelog-v1-announcement"
  - "https://raw.githubusercontent.com/mattpocock/skills/main/README.md"
  - "https://raw.githubusercontent.com/mattpocock/skills/main/skills/productivity/grilling/SKILL.md"
  - "https://raw.githubusercontent.com/mattpocock/skills/main/skills/engineering/domain-modeling/SKILL.md"
reflected_to:
  - "artifacts/20260702t025127z-adr-complete-understanding-before-canonical-authoring.md"
  - "report.md"
---

# 20260702t025127z-01-research Grill With Docs Research

## 調査目的
- Matt Pocock 氏の `/grill-me` / `/grill-with-docs` の狙い、手順、失敗モードを理解する。
- SpecDock へそのまま file layout を移植するのではなく、SpecDock の artifacts / canonical docs / ADR / report ledger に合う形へ写像する。
- この Epic の clarification / authoring 方針として、完全理解・自力調査・ユーザーへの一問ずつの確認・知識外部化をどう扱うべきかを整理する。

## sources / 調査方法
- 参照先:
  - ChatGPT GPT-5.5 Pro browser synthesis:
    - session slug: `grill-with-docs-synthesis`
    - Deep Research wrapper は UI に `Deep research` option がなく実行不可だったため、通常の ChatGPT browser wrapper で代替した。
  - Primary / near-primary public sources:
    - `https://www.aihero.dev/grill-with-docs`
    - `https://www.aihero.dev/skills-grill-me`
    - `https://www.aihero.dev/things-people-get-wrong-with-grill-me-and-grill-with-docs`
    - `https://www.aihero.dev/skills/skills-changelog-v1-announcement`
    - `https://raw.githubusercontent.com/mattpocock/skills/main/README.md`
    - `https://raw.githubusercontent.com/mattpocock/skills/main/skills/productivity/grilling/SKILL.md`
    - `https://raw.githubusercontent.com/mattpocock/skills/main/skills/engineering/domain-modeling/SKILL.md`
    - `https://raw.githubusercontent.com/mattpocock/skills/main/skills/engineering/grill-with-docs/SKILL.md`
- 検証手順:
  - ChatGPT に primary source 優先、URL/date/caveat 付きの調査を依頼した。
  - 主要URLを web open で再確認し、`grill-with-docs`、`grilling`、`domain-modeling`、README、失敗モード記事、v1 changelog の内容を照合した。
- 実験条件:
  - 調査日: 2026-07-02
  - Public web research。SpecDock への写像は local artifact authority model に基づく推論。

## facts / 観測できた事実
- `/grill-with-docs` は、plan/design について one question at a time で user と agent の shared understanding を作り、その過程で vocabulary と decisions を書き残す workflow と説明されている。
- `/grill-me` は、decision tree が解決するまで plan/design を一問ずつ pressure-test し、各質問に recommended answer を付け、codebase から分かることはユーザーに聞かずコードを調べる、と説明されている。
- 現行の Matt Pocock skills repo では、`/grill-with-docs` は `/grilling` と `/domain-modeling` を組み合わせる薄い user-invoked workflow になっている。
- `/grilling` の core loop は、shared understanding、decision tree、one question at a time、recommended answer、codebase exploration instead of asking user で構成される。
- `/domain-modeling` は、fuzzy / overloaded terms の明確化、concrete scenario での edge-case probing、code との矛盾確認、resolved terms の `CONTEXT.md` への inline capture、ADR の sparing use を扱う。
- Matt Pocock 氏の `CONTEXT.md` は glossary であり、implementation details / spec / scratch pad / implementation decisions の置き場ではないとされている。
- ADR は、hard to reverse、surprising without context、real tradeoff の三条件が揃う場合にだけ作る、という運用が示されている。
- `/grill-with-docs` の失敗モードとして、high-fidelity question を低 fidelity interview で答えようとすること、scope が大きすぎること、受け身すぎる/能動的すぎること、design decisions を保存せず context を捨てること、model 選択、parallel sessions の扱いが挙げられている。

## inference / 推測
- 事実から推測したこと:
  - SpecDock で取り込むべき本質は、`CONTEXT.md` や slash command 名ではなく、pre-implementation / pre-canonical authoring の alignment discipline である。
  - SpecDock の既存 authority model では、Matt Pocock 氏の `CONTEXT.md` 直書きに相当するものを raw authority にしてはいけない。まず `research` / `disc` / `interview` に evidence として残し、採用後に canonical docs / accepted ADR / report ledger へ反映するのが自然である。
  - `spec-dock-clarification` は、SpecDock 版の `grill-with-docs` を実施する skill として位置づけられる。ただし、SpecDock では source-grounded research、artifact capture、Evidence Adoption Ledger、Spec Authoring Gate が追加される。
  - `domain-modeling` の DDD寄り語彙は useful optional model であり、SpecDock 側では DDD / EDA を前提にせず、既存または明確化された architecture / design language に合わせるべきである。
- 推測の根拠:
  - 既存 ADR `20260702t025127z-adr-complete-understanding-before-canonical-authoring.md` は、完全理解・自力調査・必要最小限のユーザー質問・知識外部化を採用している。
  - 既存 ADR `20260702t024118z-adr-architecture-neutral-template-authoring-policy.md` は、DDD/EDA を標準前提にしない architecture-neutral / architecture-aware 方針を採用している。
  - V3 planning pack と current `report.md` は raw evidence と canonical authority を分ける。

## unverified / 未検証事項
- まだ確認していないこと:
  - Matt Pocock skills repo の全 commit history / issue discussion。
  - AI Hero 記事に書かれた publication date の完全な machine-readable 確認。
  - Skills registry metadata の詳細。
- 確認できない理由:
  - この Epic では workflow principle の理解と SpecDock への写像が目的であり、全履歴調査は現時点の design decision に必須ではない。

## question candidates / 質問候補
- source-grounded に解けず、人間判断が必要な候補:
  - SpecDock の user-facing workflow 名として、Matt Pocock 氏の用語をそのまま参照するか、`spec-dock-clarification` / `source-grounded grill` のような SpecDock-native 用語にするか。
  - Canonical authoring 前の gate を、必ず `research` artifact 作成まで要求するか、既存 sources で十分な場合は `report.md` Spec Authoring Gate 記録だけで足りるとするか。
- pressure-test question として切り出すべき候補:
  - 「SpecDock版の Grill With Docs を、ユーザー向けにどの名前/表現で扱うか」。ただし、これは実装 UI/API に影響する段階まで deferred 可能。
- 質問せずに解決できた候補:
  - `spec-dock-clarification` が interview / source-grounded grill loop を担う skill であること。
  - SpecDock では `CONTEXT.md` をそのまま authority にしないこと。

## terminology conflicts / 用語衝突
- 衝突している用語:
  - `grill-with-docs` vs `spec-dock-clarification`
  - `CONTEXT.md` glossary vs SpecDock `artifacts/` / canonical docs / ADR
  - `domain-modeling` / ubiquitous language vs architecture-neutral / architecture-aware templates
- 既存 docs / code / tests / artifacts / primary sources での使われ方:
  - Matt Pocock sources:
    - `grill-with-docs`: one-question grill + glossary / ADR capture.
    - `CONTEXT.md`: pure glossary.
    - `domain-modeling`: active domain model sharpening.
  - SpecDock sources:
    - `spec-dock-clarification`: source-grounded grill loop; create `research` / `interview` / `disc` artifacts; adopt evidence into canonical docs/report.
    - `artifacts/`: working evidence surface, not canonical authority.
    - accepted ADR: durable decision authority.
- 判断が必要な理由:
  - External inspiration をそのまま名前・構造として取り込むと、SpecDock の authority model と tool identity が曖昧になる。

## edge cases / 具体シナリオ
- edge case:
  - Codebase から答えられる質問をユーザーに聞いてしまう。
- 影響:
  - ユーザー認知負荷が上がり、`spec-dock-clarification` の価値が落ちる。Human question には local sources checked / why human judgment required を残すべき。
- edge case:
  - Raw `research` artifact の vocabulary を canonical decision として実装者が読んでしまう。
- 影響:
  - Authority leak が起きる。Adopted terms / decisions は canonical docs / accepted ADR / report EAL に反映する。
- edge case:
  - UI feel や prototype なしでは答えられない high-fidelity question を interview で詰め続ける。
- 影響:
  - Over-grilling が起きる。`research` / prototype / separate issue / deferred decision に切り出す必要がある。
- edge case:
  - Scope が大きすぎて一つの interview で収まらない。
- 影響:
  - Context が肥大化し、質問品質が下がる。Initiative / Epic / Issue scope に分割して grillable chunk にする。

## implications / 判断への含意
- `requirement.md`:
  - User-visible goals / constraints / accepted vocabulary だけを、evidence から採用して記述する。
- `design.md`:
  - Clarification workflow は「source-grounded self-investigation -> artifact capture -> one-question user interview -> ADR/canonical adoption」という流れで設計する。
  - `CONTEXT.md` 直移植ではなく、Scope Vocabulary Ledger 相当の情報を `research` / `disc` から canonical docs へ採用する。
- `plan.md`:
  - Canonical authoring 前に Spec Authoring Gate を通し、未解決 high-impact question / ADR candidate / evidence adoption status を確認する。
  - Large scope は grillable chunks へ分割する。
- `ADR`:
  - 「Complete Understanding Before Canonical Authoring」は Grill With Docs の SpecDock adaptation と整合する accepted ADR として妥当。
- `report.md`:
  - ChatGPT research とこの artifact を EAL に採用し、canonical docs への反映時に adoption target を追記する。

## リスク/制約
- Matt Pocock 氏の workflow は tool-specific file layout を持つため、`CONTEXT.md` / `docs/adr/` をそのまま SpecDock に移植すると authority model が壊れる。
- `grill` という語はユーザー向けには刺激が強い可能性があるため、SpecDock docs では `source-grounded clarification` / `pre-canonical spec grill` などの補助表現に留める判断もありうる。
- Research が public sources に基づくため、将来 Matt Pocock skills repo が変わる可能性がある。将来実装時には current sources を再確認する。

## 反映先
- reflected_to:
  - `artifacts/20260702t025127z-adr-complete-understanding-before-canonical-authoring.md`
  - `report.md` EAL-011
  - Future `design.md` clarification workflow section
  - Future `plan.md` Spec Authoring Gate / planning skill guidance

## 参考（References）
- Matt Pocock / AI Hero:
  - `https://www.aihero.dev/grill-with-docs`
  - `https://www.aihero.dev/skills-grill-me`
  - `https://www.aihero.dev/things-people-get-wrong-with-grill-me-and-grill-with-docs`
  - `https://www.aihero.dev/skills/skills-changelog-v1-announcement`
- Matt Pocock skills repo:
  - `https://raw.githubusercontent.com/mattpocock/skills/main/README.md`
  - `https://raw.githubusercontent.com/mattpocock/skills/main/skills/productivity/grilling/SKILL.md`
  - `https://raw.githubusercontent.com/mattpocock/skills/main/skills/engineering/domain-modeling/SKILL.md`
  - `https://raw.githubusercontent.com/mattpocock/skills/main/skills/engineering/grill-with-docs/SKILL.md`
