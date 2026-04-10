---
種別: disc
ID: "20260410t013236z-disc"
タイトル: "Epic 00059 cutover entry criteria and remove response"
状態: "completed"
作成者: "Codex CLI"
最終更新: "2026-04-10"
親: ["epic-00059"]
関連: ["#59"]
---

# 20260410t013236z-disc Epic 00059 cutover entry criteria and remove response

## 背景
- `epic-00059` は dependency metadata の source-of-truth を `.meta.json` に統一し、command mutation を導入する architecture epic である。
- 既存 draft では `deps.json` dual-read を含む移行案が残っていたが、architecture initiative guardrail は dual-mode より SoT 単純化を優先する。
- ユーザー回答として、`deps.json` backward compatibility は持たず、初回リリースで hard cutover し、dogfooding 側は manual fix で追従する方針が確定した。
- そのうえで、command UX と cutover gate の閉じ方だけが未確定である。
- spec review follow-up で、`deps add` duplicate-edge semantics と cutover evidence artifact contract の明文化が追加で必要になった。

## すでに確定した事項
- dependency metadata の SoT は `.meta.json` に固定する。
- `deps.json` の dual-read / backward compatibility は導入しない。
- hard cutover は初回リリースで一括実施する。
- dogfooding workspace は manual fix で追従し、互換維持よりロジックの単純化を優先する。
- 説明は architecture initiative の guardrail に沿って、SoT / persistence boundary / migration を簡潔に明示する。

## 今回決めたい質問
- Q1. `spec-dock deps remove --from <node> --to <node>` で edge が存在しない場合、warning と error のどちらに固定するか。
- Q2. hard cutover の判断をどの implementation tranche で固定するか。
- Q3. hard cutover の entry 条件として、どの docs / dogfooding manual fix / validation を必須にするか。

## それぞれの選択肢
- Q1 Option A:
  - edge 不在は warning に固定する。
- Q1 Option B:
  - edge 不在は error に固定する。
- Q2 Option A:
  - T2 mutation 完了時に cutover judgment を固定する。
- Q2 Option B:
  - T3 integration 完了時に cutover judgment を固定する。
- Q2 Option C:
  - T4 final review で cutover judgment を固定する。
- Q3 Option A:
  - entry 条件は docs 更新のみ必須にする。
- Q3 Option B:
  - entry 条件は docs 更新 + dogfooding checked-in data manual fix を必須にする。
- Q3 Option C:
  - entry 条件は docs 更新 + dogfooding checked-in data manual fix + `./spec-dock/scripts/spec-dock validate` / `sync` evidence を必須にする。

## 各選択肢のメリット / デメリット
- Q1 Option A:
  - メリット:
    - remove を idempotent に扱いやすい。
    - script から再実行しても停止しにくい。
  - デメリット:
    - state drift や対象指定ミスを見逃しやすい。
    - fail-closed を重視する architecture hardening と少しずれる。
- Q1 Option B:
  - メリット:
    - mutation contract を明示 error で固定できる。
    - 想定外の対象指定や graph drift を検出しやすい。
  - デメリット:
    - idempotent delete を期待する script は調整が必要になる。
- Q2 Option A:
  - メリット:
    - 実装序盤で contract が固定され、後続 issue がぶれにくい。
  - デメリット:
    - downstream parity と dogfooding 条件がまだ揃わず、判断材料が薄い。
- Q2 Option B:
  - メリット:
    - downstream parity、manual fix scope、validation 観点が揃った段階で gate を閉じられる。
    - T4 を証跡確認に集中させやすい。
  - デメリット:
    - T2 時点では運用詳細が未確定のまま進む。
- Q2 Option C:
  - メリット:
    - 最終 evidence を見てから判断できる。
  - デメリット:
    - T4 まで contract が揺れ、docs / tests / issue 分解の手戻りが増えやすい。
- Q3 Option A:
  - メリット:
    - 文書更新を先行しやすく、最小コストで進められる。
  - デメリット:
    - 実データ修正と validation が gate に入らず、cutover readiness が弱い。
- Q3 Option B:
  - メリット:
    - checked-in data の追従までは担保できる。
  - デメリット:
    - validate / sync の実測がないまま cutover することになる。
- Q3 Option C:
  - メリット:
    - docs、manual fix、runtime validation が揃い、entry 条件が最も明確になる。
    - architecture initiative の observability / docs parity guardrail に沿う。
  - デメリット:
    - dogfooding 側の事前作業が最も増える。

## 推奨案
- Q1:
  - Option B を推奨する。
  - 理由:
    - 今回は backward compatibility より state boundary の単純さを優先しており、remove も fail-closed contract で揃えた方が説明と test が簡潔になる。
- Q2:
  - Option B を推奨する。
  - 理由:
    - T3 なら downstream parity と manual fix scope が出揃っており、T4 を単なる最終確認にできる。
- Q3:
  - Option C を推奨する。
  - 理由:
    - docs だけでなく dogfooding checked-in data と validation evidence まで cutover gate に含めた方が、初回リリース hard cutover の根拠を明確にできる。

## 確定事項
- Q1:
  - `spec-dock deps remove --from <node> --to <node>` で edge が存在しない場合は error に固定する。
- Q2:
  - hard cutover judgment は T3 integration 完了時点で固定する。
- Q3:
  - hard cutover entry 条件は docs 更新 + dogfooding checked-in data manual fix + `./spec-dock/scripts/spec-dock validate` / `sync` evidence を必須にする。

## spec review follow-up で追加固定した事項
- Q4:
  - `spec-dock deps add --from <node> --to <node>` は current graph validation を先に実施し、graph が破損・不整合なら fail-closed error に固定する。
  - current graph が正常で edge が既に存在する場合は success/no-op に固定し、`.meta.json` の dependency 配列へ重複 edge を保存しない。
- Q5:
  - cutover evidence artifact の正本は issue-level `report.md` に置く。
  - T3 integration owner が hard cutover judgment / entry 条件充足を記録し、T4 closure owner が final parity / final spec review を記録する。
  - E-AC-005 の final closure owner は T4 closure owner に固定し、T3 は judgment 固定と entry 条件充足の記録までを担当する。
  - epic `report.md` は close summary だけを保持する。

## 回答記入欄
- Q1:
  - 回答:
    - Option B
  - 補足:
    - remove not-found は warning/no-op にせず error 契約に固定する。
- Q2:
  - 回答:
    - Option B
  - 補足:
    - T3 integration 完了時に cutover judgment を固定し、T4 は証跡確認と最終回帰に限定する。
- Q3:
  - 回答:
    - Option C
  - 補足:
    - docs 更新、dogfooding checked-in data manual fix、`./spec-dock/scripts/spec-dock validate` / `sync` evidence を entry 条件にする。
