---
種別: 実装報告書（Issue）
ID: "iss-00082"
タイトル: "Fail fast on malformed node metadata"
関連GitHub: ["#82"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-04-20"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00080", "init-00079"]
---

# iss-00082 Fail fast on malformed node metadata — 実装報告（LOG）

## 実装サマリー (任意)
- 本セッションでは `epic-00080` 配下に `iss-00082` を作成し、minor bug bucket と issue spec を具体化した。
- 実装修正そのものは未着手で、scope は malformed metadata fail-fast に固定した。

## 実装記録（セッションログ） (必須)

### 2026-04-17 11:37 - 11:45

#### 対象
- Step: issue bootstrap, spec authoring
- AC/EC: AC-004, EC-002, EC-003

#### 実施内容
- `epic-00080` 配下に GitHub-backed issue `iss-00082` / `#82` を作成した。
- active issue を `iss-00082` へ切り替え、research / requirement / design / plan を malformed metadata fail-fast に閉じて作成した。
- `active set --checkout` は untracked diff があるため safety guard で停止したので、active set は no-checkout で確定した。

#### 実行コマンド / 結果
```bash
./spec-dock/scripts/spec-dock new issue --epic epic-00080 --title "Fail fast on malformed node metadata" --slug fail-fast-on-malformed-node-metadata
spec-dock: ok (new issue) id=iss-00082 epic=epic-00080 initiative=init-00079 ... github=#82

./spec-dock/scripts/spec-dock deps check iss-00082 --github
spec-dock: ok (deps check) target=iss-00082 ... ready=true blockers=0

./spec-dock/scripts/spec-dock sync --github
spec-dock: ok (sync) wrote=spec-dock/.agent/index-all.json,...

./spec-dock/scripts/spec-dock active set iss-00082 --checkout
error: Working tree is not clean; aborting checkout for safety.

./spec-dock/scripts/spec-dock active set iss-00082
spec-dock: ok (active set) target=iss-00082 initiative=init-00079 epic=epic-00080 issue=iss-00082

./spec-dock/scripts/spec-dock new doc research --issue iss-00082 --title "pr review and staging failure analysis"
spec-dock: ok (new doc) type=research id=20260417t023838z-research ...
```

#### 変更したファイル
- `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/requirement.md` - initiative bucket boundary を具体化
- `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/design.md` - initiative guardrail を具体化
- `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/plan.md` - first issue creation までの roadmap を固定
- `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/epics/epic-00080-minor-bug-fixes/{requirement,design,plan}.md` - epic boundary と first issue tranche を具体化
- `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/epics/epic-00080-minor-bug-fixes/issues/iss-00082-fail-fast-on-malformed-node-metadata/{requirement,design,plan,report}.md` - issue spec を作成
- `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/epics/epic-00080-minor-bug-fixes/issues/iss-00082-fail-fast-on-malformed-node-metadata/discussions/20260417t023838z-research-pr-review-and-staging-failure-analysis.md` - evidence note を作成

#### コミット
- なし

#### メモ
- issue readiness は `deps check` 上 ready=true を確認済み
- checkout blocker は environment / safety guard であり、issue spec completeness そのものの blocker ではない

### 2026-04-17 11:45 - 11:49

#### 対象
- Step: spec closure, state validation
- AC/EC: AC-004

#### 実施内容
- issue docs の placeholder 取り残しを確認した。
- `validate` と `sync --github` を実行し、state projection を更新した。
- `sync --github` が current branch 由来で active を `iss-00078` 側へ戻したため、最後に `iss-00082` を no-checkout で再設定し、active show で確認した。

#### 実行コマンド / 結果
```bash
./spec-dock/scripts/spec-dock validate
spec-dock: ok (validate) nodes=36

./spec-dock/scripts/spec-dock sync --github
spec-dock: sync: active updated (matched id in branch: iss-00078)
spec-dock: ok (sync) wrote=spec-dock/.agent/index-all.json,...

./spec-dock/scripts/spec-dock active set iss-00082
spec-dock: ok (active set) target=iss-00082 initiative=init-00079 epic=epic-00080 issue=iss-00082

./spec-dock/scripts/spec-dock active show
initiative: init-00079 (...)
epic: epic-00080 (...)
issue: iss-00082 (...)
```

#### 変更したファイル
- `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/epics/epic-00080-minor-bug-fixes/issues/iss-00082-fail-fast-on-malformed-node-metadata/report.md` - validate / sync / active state の最終証跡を追記

#### コミット
- なし

#### メモ
- branch 名が `iss-00078` のままなので、`sync --github` は branch-to-active reconciliation により active を戻しうる
- issue active state の最終値は `iss-00082` に再設定済み

## 遭遇した問題と解決 (任意)
- 問題: `active set --checkout` が dirty worktree safety guard で失敗
  - 解決: `active set` を no-checkout で実行し、issue active state を確定した

## 学んだこと (任意)
- issue creation 直後の untracked diff がある状態では `--checkout` は安全装置に止められる
- reusable bucket を運用するには、親 initiative / epic docs の最小 guardrail を先に具体化しておくと routing が安定する
- branch-driven active reconciliation があるため、no-checkout 運用では `sync --github` 後に active を再確認した方が安全

## 今後の推奨事項 (任意)
- 実装着手時は S01 red test から始め、provider-side source of truth を先に修正する
- commit 後に branch 移動が必要なら `active set iss-00082 --checkout` を再実行する

## 省略/例外メモ (必須)
- `--checkout` は working tree safety guard により未完了。active issue 自体は no-checkout で設定済み。

### 2026-04-20 15:20 - 15:45

#### 対象
- Step: SG1 spec review fix / re-review
- AC/EC: AC-001, AC-002, AC-004, EC-002, EC-003

#### 実施内容
- spec reviewer から 2 件の P1 と 1 件の P2 を受領した。
- P1-1 に対応して、`malformed` の定義を欠落だけでなく `missing / blank / whitespace-only / non-string` まで明文化し、requirement / design / plan の AC と test strategy を揃えた。
- P1-2 に対応して、pre-implementation readiness gate を `S00` として分離し、red test を含む実装 step は SG1 pass 後に進む構成へ計画を組み替えた。
- P2 に対応して、`sync --github` を optional operational evidence へ格下げし、この issue の required completion gate から切り離した。
- requirement / design / plan の frontmatter `状態` を `approved` に更新し、issue docs を implementation-ready として固定した。

#### 実行コマンド / 結果
```text
spec review (SG1)

review_status=fail
findings:
- malformed 判定が欠落だけに閉じており、blank / whitespace-only / non-string が漏れている
- pre-implementation readiness gate が red test 作成後にしか判定できない
- sync --github を required gate から外すべき

spec review (SG1 re-review)

review_status=pass
findings=[]
focus:
- malformed metadata boundary
- pre-implementation SG1 gate
- optional sync evidence boundary
```

#### 変更したファイル
- `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/epics/epic-00080-minor-bug-fixes/issues/iss-00082-fail-fast-on-malformed-node-metadata/requirement.md` - malformed 定義と AC を閉じた
- `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/epics/epic-00080-minor-bug-fixes/issues/iss-00082-fail-fast-on-malformed-node-metadata/design.md` - interface / test strategy / verification mapping を更新した
- `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/epics/epic-00080-minor-bug-fixes/issues/iss-00082-fail-fast-on-malformed-node-metadata/plan.md` - `S00` / `S90` / `final exit contract` を追加し、required gate を整理した
- `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/epics/epic-00080-minor-bug-fixes/issues/iss-00082-fail-fast-on-malformed-node-metadata/report.md` - SG1 fail / fix / re-review / pass の証跡を追記した

#### コミット
- なし

#### メモ
- report 自体は実装未着手のため `draft` のままとし、spec readiness の証跡のみを追加した

### 2026-04-20 15:45 - 15:55

#### 対象
- Step: SG1 spec re-review after plan gate clarification
- AC/EC: AC-001, AC-002, AC-004

#### 実施内容
- spec reviewer から、`S01` が red baseline step なのに `QG1 targeted tests pass` を要求している矛盾が P1 として指摘された。
- `S01` を「failing baseline を固定して `report.md` に残す step」と明示し、QG1 は `S02` 以降の green 状態 test / final validation に限定した。
- あわせて `S99` の step boundary から `sync --github` 必須含みを除去し、required evidence と optional operational evidence を文言上も分離した。
- 修正後に SG1 を再レビューし、implementation-ready の最終 `pass` を確認した。

#### 実行コマンド / 結果
```text
spec review (SG1 re-review 2)

review_status=fail
findings:
- S01 が red baseline なのか QG1 pass gate なのか矛盾している
- S99 の step boundary が sync required に読める

spec review (SG1 final re-review)

review_status=pass
findings=[]
focus:
- S01 red baseline contract
- QG1 timing
- S99 required vs optional evidence wording
```

#### 変更したファイル
- `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/epics/epic-00080-minor-bug-fixes/issues/iss-00082-fail-fast-on-malformed-node-metadata/plan.md` - S01/QG1/S99 の gate 文言を整合させた
- `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/epics/epic-00080-minor-bug-fixes/issues/iss-00082-fail-fast-on-malformed-node-metadata/report.md` - final re-review pass を追記した

#### コミット
- なし

#### メモ
- SG1 final re-review の `review_status=pass` をもって、issue docs は実装着手可能な spec と判断する
