---
種別: 計画書（Epic）
ID: "epic-00283"
タイトル: "ChatGPT ZIP 仕様作成パック自動化"
関連GitHub: ["#283"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
依存: ["requirement.md", "design.md"]
親: ["init-local-00003"]
---

# epic-00283 ChatGPT ZIP 仕様作成パック自動化 — 計画（Issue と実施順序）

## 結論

この計画では、ZIP 仕様作成パックのワークフローを 9 件の Issue に分割する。実施順序は、事前確認 -> 安全検査 / スキーマ検証 -> 差分 / 段階配置 / プロファイル検証 -> ドッグフード A/B/C -> 文書化 / 指標評価である。

すべての Issue は、ChatGPT 出力を証跡として扱う。正本昇格やレビュアー通過は、このパックの生成だけでは成立しない。

## 分割方針

1. 制御プレーンとデータプレーンを混ぜない。
2. ZIP 安全検査とプロファイル制御は、独立した高リスク slice にする。
3. ドッグフードは validator 実装後に行い、必ず不一致・期限切れの negative probe を含める。
4. 文書化、命名、採用台帳例は実装スクリプトと分ける。
5. 指標評価とランタイム昇格判断は、ドッグフード証跡が出た後に行う。
6. Epic から Issue 候補を作る pack は、プロファイル推奨だけを返し、プロファイル別の正本テンプレート本文を出さない。

## 実施単位と依存順序

```text
T0: C01 事前確認 / プロンプト基盤
T1: C02 安全検査 / スキーマ検証 + C04 プロファイル制御検証
T2: C03 差分 / 段階配置 + C05 ドッグフード A + C06 ドッグフード B + C07 ドッグフード C
T3: C08 ワークフロー文書 / 採用台帳例
T4: C09 指標評価 / ランタイム昇格判断材料
```

依存関係:

```text
C01 -> C02 -> C03 -> C06 -> C09
C01 -> C04 -> C06 -> C09
C02 -> C05 -> C09
C02 -> C07 -> C09
C04 -> C07 -> C09
C03 -> C08 -> C09
```

## 並列化できるレーン

- レーン A: 制御プレーン。C01 の後に C04 を進める。
- レーン B: データプレーン安全性。C02 の後に C03 を進める。
- レーン C: ドッグフード。validator が揃った後に C05 / C06 / C07 を進める。
- レーン D: 文書化と命名。C01 / C02 の出力が安定した後に C08 を進める。
- レーン E: 指標評価。ドッグフード証跡が揃った後に C09 を進める。

共有スキーマ、期限切れ条件、プロファイル権威境界が固定されている場合だけ、並列実行を許可する。

## Issue readiness contract

`authorized_profile` の権威は各 Issue の `.assurance.json` / `assurance classify` にあります。現時点の local assurance は全 Issue `standard` / `provisional` です。これは ChatGPT 推奨や Epic 側のリスク判断によって上書きしません。

一方で、ZIP 受け入れ、安全検査、差分・段階配置、プロファイル制御、選択済みスケルトン、不一致 probe に関わる Issue は、実行前の Issue planning で **strict 相当の追加 obligation** を満たす必要があります。これは `authorized_profile` を変更するものではなく、manual escalation として reviewer / specialist / failure-mode evidence を強める運用判断です。

| Issue | local authorized_profile | 追加 obligation | 理由 |
|---|---|---|---|
| `iss-00284` | `standard` / `provisional` | strict 相当 | branch/ref/source/stale_if を固定する制御プレーン入口であり、以降の ZIP 生成の信頼性を左右するため。 |
| `iss-00285` | `standard` / `provisional` | strict 相当 | 危険 ZIP の拒否と unsafe authority claim の検査を担うため。 |
| `iss-00286` | `standard` / `provisional` | strict 相当 | 正本直接上書きを防ぎ、EAL へ採用候補を渡すため。 |
| `iss-00287` | `standard` / `provisional` | strict 相当 | selected skeleton / profile authority を守るため。 |
| `iss-00288` | `standard` / `provisional` | standard | candidate-only の dogfood であり、profile-specific canonical template を出さない範囲に限定するため。 |
| `iss-00289` | `standard` / `provisional` | strict 相当 | 既存 Issue の selected-profile skeleton fill を扱い、canonical adoption と混同しやすいため。 |
| `iss-00290` | `standard` / `provisional` | strict 相当 | stale / mismatch / unsafe claim を fail-closed にブロックするため。 |
| `iss-00291` | `standard` / `provisional` | standard | 文書化と EAL 例が中心であり、配布ランタイムや正本採用を行わないため。 |
| `iss-00292` | `standard` / `provisional` | standard | 指標評価と昇格判断材料の作成に留め、昇格自体は後続判断に残すため。 |

strict 相当の追加 obligation を持つ Issue は、Issue planning 時に specialist evidence または manual fallback evidence、failure-mode record、fresh `spec-reviewer` pass を `report.md` に残すまで execution-ready と扱いません。

## Issue 一覧
- `iss-00284` / GitHub `#284`: 仕様作成パックの事前確認とプロンプトパックを作る
  - 現在のタイトル: `Build Authoring Pack Preflight And Prompt Pack`
  - 推奨グレード: `strict`
  - ディレクトリ: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00284-build-authoring-pack-preflight-and-prompt-pack`

- `iss-00285` / GitHub `#285`: 安全な仕様作成パック検査とスキーマ検証を実装する
  - 現在のタイトル: `Implement Safe Authoring Pack Review And Schema Validation`
  - 推奨グレード: `strict`
  - ディレクトリ: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00285-implement-safe-authoring-pack-review-and-schema-validation`

- `iss-00286` / GitHub `#286`: 仕様作成パックの差分表示と段階配置を実装する
  - 現在のタイトル: `Implement Authoring Pack Diff And Staged Artifact Rendering`
  - 推奨グレード: `strict`
  - ディレクトリ: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00286-implement-authoring-pack-diff-and-staged-artifact-rendering`

- `iss-00287` / GitHub `#287`: プロファイル制御されたスケルトン記入検証を実装する
  - 現在のタイトル: `Implement Profile Controlled Selected Skeleton Fill Validation`
  - 推奨グレード: `strict`
  - ディレクトリ: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00287-implement-profile-controlled-selected-skeleton-fill-validation`

- `iss-00288` / GitHub `#288`: Epic から Issue 候補を作る候補専用パックをドッグフードする
  - 現在のタイトル: `Dogfood Candidate Only Epic To Issue Authoring Pack`
  - 推奨グレード: `standard`
  - ディレクトリ: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00288-dogfood-candidate-only-epic-to-issue-authoring-pack`

- `iss-00289` / GitHub `#289`: 既存 Issue の選択済みプロファイル向けパックをドッグフードする
  - 現在のタイトル: `Dogfood Existing Issue Selected Profile Authoring Pack`
  - 推奨グレード: `strict`
  - ディレクトリ: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00289-dogfood-existing-issue-selected-profile-authoring-pack`

- `iss-00290` / GitHub `#290`: 不一致・期限切れパックをブロックできるか検証する
  - 現在のタイトル: `Dogfood Authoring Pack Mismatch And Stale Probe`
  - 推奨グレード: `strict`
  - ディレクトリ: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00290-dogfood-authoring-pack-mismatch-and-stale-probe`

- `iss-00291` / GitHub `#291`: 仕様作成パックのワークフローと採用台帳例を文書化する
  - 現在のタイトル: `Document Authoring Pack Workflow And Adoption Ledger Examples`
  - 推奨グレード: `standard`
  - ディレクトリ: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00291-document-authoring-pack-workflow-and-adoption-ledger-examples`

- `iss-00292` / GitHub `#292`: ドッグフード指標とランタイム昇格基準を評価する
  - 現在のタイトル: `Evaluate Dogfood Metrics And Runtime Promotion Criteria`
  - 推奨グレード: `standard`
  - ディレクトリ: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00292-evaluate-dogfood-metrics-and-runtime-promotion-criteria`

## 統合チェックポイント

- G1: 9 件の Issue が E-RQ / E-AC に対応している。
- G2: ZIP root、ファイル種別、パス安全性、スキーマ、ソース一覧、期限切れ条件、危険な権威主張、プロファイル検証が fail-closed で定義されている。
- G3: valid ZIP からドライラン差分と段階配置証跡を作れても、正本を直接上書きしない。
- G4: ドッグフード A/B/C が、それぞれ候補生成、選択済みプロファイル記入、不一致ブロックを確認する。
- G9: ランタイム昇格、保留、却下の判断材料が揃い、手動フォールバックが維持されている。

## ドッグフードシナリオ

### A: Epic から Issue 候補を作る

目的: Epic レベルの ZIP から複数 Issue 候補を作り、プロファイル推奨だけを返し、プロファイル別テンプレート本文を出さないことを確認する。

証跡:

- Issue 候補数と境界レビュー。
- `profile.json` が推奨専用であること。
- ドラフト要件、ドラフト設計、ドラフト実装計画が存在すること。
- all-profile variants が存在しないこと。

### B: 既存 Issue の選択済みプロファイルを埋める

目的: レビュー済みの Issue 要件から、ローカル assurance が選択済みプロファイルとスケルトンを作り、そのセクションだけを ChatGPT が埋められることを確認する。

証跡:

- プロファイル解決 snapshot。
- テンプレートハッシュ。
- スケルトンのセクション一覧。
- セクション対応表と未記入セクション報告。
- 段階的採用のドライラン。

### C: 不一致・期限切れ probe

目的: stale profile、profile mismatch、source hash mismatch、危険な権威主張を validator がブロックできることを確認する。

証跡:

- negative fixture 一覧。
- fixture ごとの検証結果。
- ブロックされた内容に段階配置 artifact が作られないこと。
- 手動フォールバックの記録。

## 指標と昇格判断

測定する指標:

- 検証失敗率。
- ローカル採用後に残った有効 claim の比率。
- 正本再記述後のレビュアー修正ループ数。
- 人間 / メインオーケストレーターの手直し量。
- プロファイル不一致のブロック率。
- 正本直接上書き防止の成功確認。
- 手動フォールバック成功率。
- ドッグフード実行コストと運用摩擦。

ランタイム昇格はこの Epic 内では決めない。この計画は、その判断材料を作る。

## 文書化への影響

- v1 文書では、ドッグフード専用かつ証跡専用であることを明記する。
- プロンプト指針では、リポジトリ内の instruction-like text を「データ」として扱わせる。
- ユーザー向け命名では provider detail を前面に出さず、`authoring-pack-*` 系を優先する。
- Issue 作成コマンドは提案に留め、実行済みの権威として扱わない。
- 実装されるまで、配布ランタイムコマンドが存在するような書き方をしない。

## 未解決だがブロックしない判断

- raw ZIP / 展開済みツリーを repo 外だけに残すか、将来 artifact-pack 契約を作るか。
- ランタイム昇格の正確なしきい値。
- ChatGPT のプロファイル推奨と local classify が食い違った場合の salvage 方針。
- Strict / Critical で ChatGPT Use を named specialist evidence として扱う将来経路。

## 最終品質ゲート

- 必須ファイルが存在する。
- ZIP 内は Markdown / JSON 中心で、危険なファイル種別を含まない。
- 禁止パスが存在しない。
- Issue 数は 9 件である。
- 候補の `profile.json` は `authorized_profile: null` を維持する。
- 候補専用 pack は all-profile variants を含まない。
- branch / repo provenance が宣言されている。
- ローカル検証が引き続き必須である。

## Issue 引き渡しパッケージのパス一覧

この一覧は、ChatGPT 仕様作成パック由来のドラフト artifact を Issue-local `artifacts/` へ配置した結果である。各 draft は証跡専用の planning input であり、Issue の正本 `design.md` / `plan.md` へ採用するには、個別の Issue planning と fresh `spec-reviewer` gate が必要である。

- `iss-00284` / GitHub `#284`: 仕様作成パックの事前確認とプロンプトパックを作る
  - `draft-requirement`: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00284-build-authoring-pack-preflight-and-prompt-pack/artifacts/20260706t150659z-draft-requirement-draft-requirement-from-authoring-pack.md`
  - `draft-design`: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00284-build-authoring-pack-preflight-and-prompt-pack/artifacts/20260706t151018z-draft-design-draft-design-from-authoring-pack.md`
  - `draft-plan`: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00284-build-authoring-pack-preflight-and-prompt-pack/artifacts/20260706t151018z-01-draft-plan-draft-plan-from-authoring-pack.md`
  - local_assurance_profile: `standard`
- `iss-00285` / GitHub `#285`: 安全な仕様作成パック検査とスキーマ検証を実装する
  - `draft-requirement`: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00285-implement-safe-authoring-pack-review-and-schema-validation/artifacts/20260706t151018z-draft-requirement-draft-requirement-from-authoring-pack.md`
  - `draft-design`: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00285-implement-safe-authoring-pack-review-and-schema-validation/artifacts/20260706t151018z-01-draft-design-draft-design-from-authoring-pack.md`
  - `draft-plan`: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00285-implement-safe-authoring-pack-review-and-schema-validation/artifacts/20260706t151019z-draft-plan-draft-plan-from-authoring-pack.md`
  - local_assurance_profile: `standard`
- `iss-00286` / GitHub `#286`: 仕様作成パックの差分表示と段階配置を実装する
  - `draft-requirement`: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00286-implement-authoring-pack-diff-and-staged-artifact-rendering/artifacts/20260706t151019z-draft-requirement-draft-requirement-from-authoring-pack.md`
  - `draft-design`: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00286-implement-authoring-pack-diff-and-staged-artifact-rendering/artifacts/20260706t151019z-01-draft-design-draft-design-from-authoring-pack.md`
  - `draft-plan`: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00286-implement-authoring-pack-diff-and-staged-artifact-rendering/artifacts/20260706t151019z-02-draft-plan-draft-plan-from-authoring-pack.md`
  - local_assurance_profile: `standard`
- `iss-00287` / GitHub `#287`: プロファイル制御されたスケルトン記入検証を実装する
  - `draft-requirement`: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00287-implement-profile-controlled-selected-skeleton-fill-validation/artifacts/20260706t151019z-draft-requirement-draft-requirement-from-authoring-pack.md`
  - `draft-design`: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00287-implement-profile-controlled-selected-skeleton-fill-validation/artifacts/20260706t151019z-01-draft-design-draft-design-from-authoring-pack.md`
  - `draft-plan`: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00287-implement-profile-controlled-selected-skeleton-fill-validation/artifacts/20260706t151019z-02-draft-plan-draft-plan-from-authoring-pack.md`
  - local_assurance_profile: `standard`
- `iss-00288` / GitHub `#288`: Epic から Issue 候補を作る候補専用パックをドッグフードする
  - `draft-requirement`: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00288-dogfood-candidate-only-epic-to-issue-authoring-pack/artifacts/20260706t151020z-draft-requirement-draft-requirement-from-authoring-pack.md`
  - `draft-design`: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00288-dogfood-candidate-only-epic-to-issue-authoring-pack/artifacts/20260706t151020z-01-draft-design-draft-design-from-authoring-pack.md`
  - `draft-plan`: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00288-dogfood-candidate-only-epic-to-issue-authoring-pack/artifacts/20260706t151020z-02-draft-plan-draft-plan-from-authoring-pack.md`
  - local_assurance_profile: `standard`
- `iss-00289` / GitHub `#289`: 既存 Issue の選択済みプロファイル向けパックをドッグフードする
  - `draft-requirement`: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00289-dogfood-existing-issue-selected-profile-authoring-pack/artifacts/20260706t151020z-draft-requirement-draft-requirement-from-authoring-pack.md`
  - `draft-design`: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00289-dogfood-existing-issue-selected-profile-authoring-pack/artifacts/20260706t151020z-01-draft-design-draft-design-from-authoring-pack.md`
  - `draft-plan`: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00289-dogfood-existing-issue-selected-profile-authoring-pack/artifacts/20260706t151020z-02-draft-plan-draft-plan-from-authoring-pack.md`
  - local_assurance_profile: `standard`
- `iss-00290` / GitHub `#290`: 不一致・期限切れパックをブロックできるか検証する
  - `draft-requirement`: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00290-dogfood-authoring-pack-mismatch-and-stale-probe/artifacts/20260706t151020z-draft-requirement-draft-requirement-from-authoring-pack.md`
  - `draft-design`: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00290-dogfood-authoring-pack-mismatch-and-stale-probe/artifacts/20260706t151021z-draft-design-draft-design-from-authoring-pack.md`
  - `draft-plan`: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00290-dogfood-authoring-pack-mismatch-and-stale-probe/artifacts/20260706t151021z-01-draft-plan-draft-plan-from-authoring-pack.md`
  - local_assurance_profile: `standard`
- `iss-00291` / GitHub `#291`: 仕様作成パックのワークフローと採用台帳例を文書化する
  - `draft-requirement`: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00291-document-authoring-pack-workflow-and-adoption-ledger-examples/artifacts/20260706t151021z-draft-requirement-draft-requirement-from-authoring-pack.md`
  - `draft-design`: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00291-document-authoring-pack-workflow-and-adoption-ledger-examples/artifacts/20260706t151021z-01-draft-design-draft-design-from-authoring-pack.md`
  - `draft-plan`: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00291-document-authoring-pack-workflow-and-adoption-ledger-examples/artifacts/20260706t151021z-02-draft-plan-draft-plan-from-authoring-pack.md`
  - local_assurance_profile: `standard`
- `iss-00292` / GitHub `#292`: ドッグフード指標とランタイム昇格基準を評価する
  - `draft-requirement`: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00292-evaluate-dogfood-metrics-and-runtime-promotion-criteria/artifacts/20260706t151021z-draft-requirement-draft-requirement-from-authoring-pack.md`
  - `draft-design`: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00292-evaluate-dogfood-metrics-and-runtime-promotion-criteria/artifacts/20260706t151021z-01-draft-design-draft-design-from-authoring-pack.md`
  - `draft-plan`: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00292-evaluate-dogfood-metrics-and-runtime-promotion-criteria/artifacts/20260706t151022z-draft-plan-draft-plan-from-authoring-pack.md`
  - local_assurance_profile: `standard`
