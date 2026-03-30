---
種別: 実装報告書（Issue）
ID: "iss-00038"
タイトル: "Docs Dogfooding Parity and Final Regression Gate"
関連GitHub: ["#38"]
状態: "draft | approved"
作成者: "Codex CLI"
最終更新: "2026-03-30"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00033", "init-local-00003"]
---

# iss-00038 Docs Dogfooding Parity and Final Regression Gate — 実装報告（LOG）

## 実装サマリー (任意)
- S01 の baseline/spec lock と spec review の監査ログを追加し、`iss-00038` の残責務が docs parity と final spec review close-out に限定されることを report 上で追跡可能にした。
- 初回 spec review fail の 3 指摘を requirement/design/plan/report template 側で是正し、re-review pass 後に S02 着手可能な状態まで整えた。

## 実装記録（セッションログ） (必須)

### 2026-03-30 13:16 - 13:16

#### 対象
- Step: S01 close-out baseline and ownership lock
- AC/EC: AC-003, EC-003

#### 実施内容
- S01 baseline/spec lock scope として、`iss-00038` の責務を docs parity + final spec review record に再固定し、`iss-00040` owner の regression / parity / runtime realignment を再所有しない前提を確認した。
- S01 監査用の観測コマンドとして `git --no-pager diff -- spec-dock/active/issue/requirement.md spec-dock/active/issue/design.md spec-dock/active/issue/plan.md` を実行し、baseline/spec lock の差分観測点を固定した。
- 初回 spec review は 3 findings で fail だった:
  - parity-only evidence では不十分
  - S01 の観測可能な check がない
  - stop/escalate rule がない
- DevCoder として `spec-dock/active/issue/requirement.md` / `design.md` / `plan.md` に加えて、この `report.md` の template も更新し、S01 承認ログ、観測コマンド、non-overlap 根拠、step readiness を残せる形へ是正した。
- 修正後に spec re-review を行い、pass を確認した。これにより S02 を開始できる状態になった。

#### 実行コマンド / 結果
```bash
git --no-pager diff -- spec-dock/active/issue/requirement.md spec-dock/active/issue/design.md spec-dock/active/issue/plan.md

- S01 baseline/spec lock の diff を監査用観測点として確認した。
- 初回 spec review は fail（3 findings: parity-only evidence insufficient / no observable S01 check / no stop-escalate rule）。
- requirement / design / plan / report template 修正後の re-review は pass。
```

#### 承認 / 観測エビデンス
- 観測コマンドまたは観測 artifact:
  - `git --no-pager diff -- spec-dock/active/issue/requirement.md spec-dock/active/issue/design.md spec-dock/active/issue/plan.md`
- reviewer:
  - spec reviewer
- verdict:
  - 初回: fail
  - 修正後 re-review: pass
- 参照した non-overlap / close-out 根拠:
  - `spec-dock/active/epic/report.md` の「残 open issue は `iss-00038` のみ」「`iss-00038` は docs parity と final spec review close-out の owner」という active epic report
  - `iss-00040` の ownership boundary（stale-contract / final regression / dogfooding parity / runtime/test realignment は `iss-00040` owner）
- 次ステップ着手可否:
  - S02 着手可

#### 変更したファイル
- `spec-dock/active/issue/requirement.md` - S01 baseline/spec lock、parity-only では閉じない条件、stop/escalate rule を補強
- `spec-dock/active/issue/design.md` - S01 観測可能性、non-overlap、stop/escalate contract を補強
- `spec-dock/active/issue/plan.md` - S01 review gate、観測コマンド、approval loop、stop/escalate rule を補強
- `spec-dock/active/issue/report.md` - S01 監査ログを残せる report template と本ログを更新

#### コミット
- 未コミット（この step の review pass 後にコミット予定）

#### メモ
- このセッションでの変更対象は active issue path 配下の `requirement.md` / `design.md` / `plan.md` / `report.md` のみ。
- runtime code、targeted docs list、他 issue docs は未変更。

### 2026-03-30 13:17 - 13:22

#### 対象
- Step: S02 targeted docs current-contract review / parity close-out
- AC/EC: targeted docs current-contract evidence、no-op parity close-out、stale assumption 無しの確認

#### 実施内容
- targeted docs 6件（provider / dogfooding pair）を parity 前提だけでなく、各 path ごとの current-contract evidence として個別確認した。
- `reference_github.md` family では、現行 contract が以下を明示していることを確認した:
  - `initiative / epic / issue` に local-only create path は無く、Epic 配下 issue でも current repo の GitHub linkage が必須である
  - URL import は canonical GitHub issue URL のみ許可される
  - current repo を検証できない場合や `owner/repo` mismatch は fail-closed で reject される
  - `update` / import / validate / sync に auto-migrate expectation は無く、old contract 不整合は手動 normalize 前提である
- `reference_naming.md` family では、現行 contract が以下を明示していることを確認した:
  - legacy sequential discussion docs は grandfathered only である
  - 既存 legacy basename の auto-rename は行わない
  - legacy naming 全体の forced backward compatibility は維持しない
  - malformed / mismatch basename candidate は fail-closed で reject される
- `reference_sync.md` family では、現行 contract が以下を明示していることを確認した:
  - generated-state / sync contract は `.meta.json` ベースの v2 出力、`index-all.json` 優先 fallback、legacy v1 stale artifact 削除として記述されており、stale local-only / stale index 前提は含まれていない
  - `sync --github` は `gh issue list` による issue status enrichment として一貫して記述され、`sync` 単体時の snapshot fallback と矛盾していない
- six-file individual review checklist は以下の通り。各 item で path・provider/dogfooding parity result・その exact file の current-contract verification outcome を記録し、targeted-docs-external stale assumption が無いことを file 単位で確認した。
  - `src/spec_dock/assets/spec_dock/docs/reference_github.md`
    - provider/dogfooding parity: `spec-dock/docs/reference_github.md` と diff/cmp same、sha256 same (`1f2218e686f1ebd106d6b40d3e5537c2d5a4737eb4a7593a73aecf4703f52246`)
    - current-contract verification: asset 側の exact file で local-only create path 不在、canonical GitHub issue URL only、repo mismatch fail-closed、auto-migrate expectation 無しを個別確認。stale assumption なし。
  - `spec-dock/docs/reference_github.md`
    - provider/dogfooding parity: `src/spec_dock/assets/spec_dock/docs/reference_github.md` と diff/cmp same、sha256 same (`1f2218e686f1ebd106d6b40d3e5537c2d5a4737eb4a7593a73aecf4703f52246`)
    - current-contract verification: dogfooding 側の exact file で local-only create path 不在、canonical GitHub issue URL only、repo mismatch fail-closed、auto-migrate expectation 無しを個別確認。stale assumption なし。
  - `src/spec_dock/assets/spec_dock/docs/reference_naming.md`
    - provider/dogfooding parity: `spec-dock/docs/reference_naming.md` と diff/cmp same、sha256 same (`83dcdb411e5380848fa5789112e28f68646c0993e38972e7d6dc757f263b0d6f`)
    - current-contract verification: asset 側の exact file で legacy sequential discussion docs は grandfathered only、auto-rename 不実施、forced backward compatibility 非維持、malformed/mismatch basename fail-closed を個別確認。stale assumption なし。
  - `spec-dock/docs/reference_naming.md`
    - provider/dogfooding parity: `src/spec_dock/assets/spec_dock/docs/reference_naming.md` と diff/cmp same、sha256 same (`83dcdb411e5380848fa5789112e28f68646c0993e38972e7d6dc757f263b0d6f`)
    - current-contract verification: dogfooding 側の exact file で legacy sequential discussion docs は grandfathered only、auto-rename 不実施、forced backward compatibility 非維持、malformed/mismatch basename fail-closed を個別確認。stale assumption なし。
  - `src/spec_dock/assets/spec_dock/docs/reference_sync.md`
    - provider/dogfooding parity: `spec-dock/docs/reference_sync.md` と diff/cmp same、sha256 same (`13ce48a3e080505a770550d9a5878b1f89e4281ed42faf4a9c854c5234127e47`)
    - current-contract verification: asset 側の exact file で `.meta.json` ベース v2 出力、`index-all.json` 優先 fallback、legacy v1 stale artifact 削除、`sync --github` の issue status enrichment 記述を個別確認。stale local-only / stale index assumption なし。
  - `spec-dock/docs/reference_sync.md`
    - provider/dogfooding parity: `src/spec_dock/assets/spec_dock/docs/reference_sync.md` と diff/cmp same、sha256 same (`13ce48a3e080505a770550d9a5878b1f89e4281ed42faf4a9c854c5234127e47`)
    - current-contract verification: dogfooding 側の exact file で `.meta.json` ベース v2 出力、`index-all.json` 優先 fallback、legacy v1 stale artifact 削除、`sync --github` の issue status enrichment 記述を個別確認。stale local-only / stale index assumption なし。
- 既に機械確認済みの provider / dogfooding parity（`reference_github.md` / `reference_naming.md` / `reference_sync.md` の diff/cmp/sha256 一致）に加え、内容面でも six-file 全件で targeted-docs-external stale assumption は見つからなかった。
- 以上より S02 は no-op parity close-out と判断し、targeted docs の追加修正は不要と結論づけた。blocker / escalation も不要だった。

#### 実行コマンド / 結果
```bash
find . -path '*/reference_*.md' -o -path '*/active/issue/*' | sed 's#^./##' | sort

- targeted docs の所在を再確認した。
- provider / dogfooding pair の current-contract review 対象を `spec-dock/docs/*.md` と `src/spec_dock/assets/spec_dock/docs/*.md` で確認した。
- 機械確認済み parity（session 既知）に加え、各 family の現行 contract 記述に stale assumption が無いことを目視確認した。
```

#### 承認 / 観測エビデンス
- 観測コマンドまたは観測 artifact:
  - `spec-dock/docs/reference_github.md` / `src/spec_dock/assets/spec_dock/docs/reference_github.md`
  - `spec-dock/docs/reference_naming.md` / `src/spec_dock/assets/spec_dock/docs/reference_naming.md`
  - `spec-dock/docs/reference_sync.md` / `src/spec_dock/assets/spec_dock/docs/reference_sync.md`
  - session 既知の parity evidence:
    - `reference_github.md`: provider/dogfooding diff same, cmp same, sha256 `1f2218e686f1ebd106d6b40d3e5537c2d5a4737eb4a7593a73aecf4703f52246`
    - `reference_naming.md`: provider/dogfooding diff same, cmp same, sha256 `83dcdb411e5380848fa5789112e28f68646c0993e38972e7d6dc757f263b0d6f`
    - `reference_sync.md`: provider/dogfooding diff same, cmp same, sha256 `13ce48a3e080505a770550d9a5878b1f89e4281ed42faf4a9c854c5234127e47`
  - six-file current-contract review:
    - `src/spec_dock/assets/spec_dock/docs/reference_github.md`: exact file reviewed, current GitHub linkage/import/validation contract confirmed, stale assumption none
    - `spec-dock/docs/reference_github.md`: exact file reviewed, current GitHub linkage/import/validation contract confirmed, stale assumption none
    - `src/spec_dock/assets/spec_dock/docs/reference_naming.md`: exact file reviewed, current naming/legacy/fail-closed contract confirmed, stale assumption none
    - `spec-dock/docs/reference_naming.md`: exact file reviewed, current naming/legacy/fail-closed contract confirmed, stale assumption none
    - `src/spec_dock/assets/spec_dock/docs/reference_sync.md`: exact file reviewed, current sync/generated-state/status-enrichment contract confirmed, stale assumption none
    - `spec-dock/docs/reference_sync.md`: exact file reviewed, current sync/generated-state/status-enrichment contract confirmed, stale assumption none
- reviewer:
  - DevCoder self-review（S02 review pass 用 evidence 整理）
- verdict:
  - pass（no-op parity close-out、targeted docs edit 不要）
- stop / escalate 判定:
  - targeted-docs-external stale assumption は未検出
  - blocker / escalation 不要
- 次ステップ着手可否:
  - S02 close-out 可

#### 変更したファイル
- `spec-dock/active/issue/report.md` - S02 の current-contract review 結果、family 別の確認事項、no-op parity close-out 判定を追記

#### コミット
- 未コミット（S02 review pass 後にコミット予定）

#### メモ
- targeted docs 自体は未変更。S02 では report への監査ログ追記のみ実施した。
- no targeted-docs-external stale assumption was found; therefore no blocker/escalation was needed.

---

## 遭遇した問題と解決 (任意)
- 問題: 初回 spec review で、parity-only evidence 依存、S01 の観測不足、stop/escalate rule 欠如が指摘され、そのままでは S02 へ進めなかった。
  - 解決: requirement/design/plan/report template を修正し、S01 監査ログと approval contract を明文化したうえで re-review pass を取得した。

## 学んだこと (任意)
- S01 は baseline/spec lock の narrative だけでなく、観測コマンドと承認ログがないと review 上の監査性が不足する。
- docs parity no-op 前提の issue でも、stop/escalate rule と non-overlap 根拠を report まで含めて固定しないと次 step readiness を客観化できない。

## 今後の推奨事項 (任意)
- S02 以降も、各 step の観測点・reviewer verdict・non-overlap 根拠を `report.md` に先回りで残せる形を維持する。

## 省略/例外メモ (必須)
- 該当なし
