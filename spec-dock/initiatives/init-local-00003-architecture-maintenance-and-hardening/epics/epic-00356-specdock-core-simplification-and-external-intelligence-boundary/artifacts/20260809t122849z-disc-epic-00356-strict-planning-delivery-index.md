---
種別: Discussion / Delivery Index
対象: epic-00356
作成日: 2026-08-09
生成経路: mixed; 本文を参照
authority: evidence_only
adoption_status: partially_adopted
---

# Epic 00356 計画成果物ガイド

## まず読む資料

新しく参加したメンバーは、まず次の詳細HTMLを参照する。Epicの背景、構造境界、薄いライフサイクル、成果物の契約、4段階の文書計画、Issue 357〜360の利用者価値と担当境界、依存・統合確認、テスト、移行、残る人間判断を日本語で具体的に説明する、現在推奨する説明資料である。

- [`20260809t135756z-disc-epic-00356-detailed-onboarding-guide.html`](./20260809t135756z-disc-epic-00356-detailed-onboarding-guide.html)
- SHA-256: `d6cffa5d64ef2914c26cf33b24045d0e67240101bab08f6205f32a9e363137bb`
- 詳細HTML生成経路: Codex main orchestratorが現在の正本R/D/Pを直接読み直して作成（ChatGPT / Oracle未使用）

以下のHTMLは初版であり、Strict planning成果物を回収した履歴証跡として保持する。初版には日本語と英語が混在し、説明が短すぎる箇所があるため、新規参加者の最初の説明資料としては上記の詳細HTMLを用いる。既存のFull planning ZIPには、この初版HTMLが収録されており、詳細HTMLは収録されていない。初版とZIPはChatGPT-use-strictによる完全コピーの履歴証跡であり、上記の詳細HTMLは正本を読み直した別の説明資料です。

- [`20260809t122849z-disc-epic-00356-vertical-slice-planning-guide.html`](./20260809t122849z-disc-epic-00356-vertical-slice-planning-guide.html)

このHTMLは、次を一つの資料で説明する。

- Currentのworkflow-heavyなSpecDockから、Storage Core / Authoring Kit / External Intelligenceへ責務を分ける理由
- Epicの要件、設計、実施順序
- Issue 357〜360の目的、担当範囲、依存、並行作業時の境界
- 人間承認待ちの品質・統合・deliverable handoff Issue候補
- 図解したproduct boundary、責務handoff、dependency graph

この初版HTMLはself-containedで、3個のinline SVGを含む。PlantUMLで定義した構造を、人間がブラウザーで読みやすい図として表現している。現在推奨する詳細HTMLは、4個のinline SVGを含む別の説明資料です。

## 複数ファイルを含むZIP

### 人間向け説明資料を含む生成原本

- [`20260809t122849z-disc-epic-00356-vertical-slice-planning.zip`](./20260809t122849z-disc-epic-00356-vertical-slice-planning.zip)
- SHA-256: `4e506696a007bf6c19237f5f598685d1b19274d7b60a80819e6af922756f6406`

Epic R/D/P候補、Issue 357〜360 draft R/D/P、最終Issue候補、adoption資料、summary、HTMLを含むChatGPT-use-strictの最初の完全成果物である。HTMLの原本保持に使用する。ZIP pack validatorの入力には使用しない。

### SpecDock validator合格版

- [`20260809t122849z-disc-epic-00356-authoring-pack-validated.zip`](./20260809t122849z-disc-epic-00356-authoring-pack-validated.zip)
- SHA-256: `073bbe7dc9bc7b95ef6ea04f5e85d0219b6e522076799799f3ab8ffcffabf9de`
- Pack tree digest: `e5cabfb7c41d2436b753a237b6ce035e5218a012eb9b454243c7a58be35fa223`

このZIPはSpecDockのauthoring pack contractに合わせた検証用成果物である。

- pack review: `pass`
- source manifest: `13910ad351ee8e1b2da6277893c0988fee68f2ccc7a849f49c2ba88ac25534ba`
- evidence mode: `github-synced`
- GitHub repository / branch / SHA: `chemitaro/spec-dock` / `main` / `2c75e0c02cb65a6e74040a72dc161d342d661091`
- Issue candidate validation: `5 / 5 pass`
- Candidates: `iss-00357`, `iss-00358`, `iss-00359`, `iss-00360`, `proposed-final-quality-integration-delivery`

## 正本への反映状態

- Epic `requirement.md`: main orchestratorが再記述し、fresh requirement review `pass`
- Epic `design.md`: main orchestratorが再記述し、fresh design review `pass`
- Epic `plan.md`: main orchestratorが再記述し、fresh plan review `pass`
- Issue 357〜360 draft R/D/P: 各Issueのscope-local Artifactへbyte-exact copy済み。各Issue planningで正本への採否を判断する。
- 最終Issue候補: 人間承認前のためnode未作成。候補はvalidator合格ZIP内に保持する。

非推奨の`spec-dock-epic-planning-manual`は使用していない。ChatGPT-use-strict、SpecDock pack review / candidate validation、main orchestratorによる正本統合、fresh reviewer gateだけを用いた。

## Integrity

| File | SHA-256 |
|---|---|
| 初版HTMLガイド | `44df426758031bbf870fecb0ed5b9dca051ff3c39a98098fe716af3688256f58` |
| Full planning ZIP | `4e506696a007bf6c19237f5f598685d1b19274d7b60a80819e6af922756f6406` |
| Validator-compatible ZIP | `073bbe7dc9bc7b95ef6ea04f5e85d0219b6e522076799799f3ab8ffcffabf9de` |

初版HTMLと二つのZIPはChatGPT-use-strictで生成・回収した原本から`cp`し、`cmp`とSHA-256で一致を確認した。現在推奨する詳細HTMLはこの完全コピーには含めず、現在の正本を読み直して別途作成している。
