---
種別: 実装報告書（Issue）
ID: "iss-00063"
タイトル: "Final regression parity and cutover closure"
関連GitHub: ["#63"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-04-11"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00059", "init-local-00003"]
---

# iss-00063 Final regression parity and cutover closure — 実装報告（LOG）

## 実装サマリー (任意)
- active initiative / epic / issue、`iss-00060`、`iss-00062` の docs / report / current runtime 状態を読み合わせ、T4 closure issue の実装準備に必要な前提を整理した。
- `iss-00063` の requirement / design / plan を current repo reality に合わせて補正し、review-only inherited regression suite、fail-closed blocker semantics、canonical graph extraction 手順、same-snapshot parity discipline を固定した。
- あわせて upstream prerequisite である `iss-00062/report.md` の frontmatter / `target_id` / exit code 記録を T4 前提 shape に整え、spec review pass を取得した。

## 実装記録（セッションログ） (必須)

### 2026-04-11 00:00 - 00:00

#### 対象
- Step: S01
- AC/EC: baseline lock, implementation readiness

#### 実施内容
- active `initiative` / `epic` / `issue`、`iss-00060` requirement / design / plan / report、`iss-00062` report、epic requirement / design / plan、`workflow_issue.md` を確認し、T4 close-out の責務分界を再確認した。
- `iss-00063` の spec を現状実装に合わせて補正し、`iss-00062/report.md` の実測証跡に追従した inherited regression suite と fail-closed blocker policy を固定した。
- spec reviewer の初回 fail 指摘に従い、status mismatch の blocker semantics、review-only evidence と rerun-required commands の境界、ancillary flaky-check subset の扱い、canonical `.meta.json` graph 抽出と same-snapshot parity discipline を追加した。
- `iss-00062/report.md` も T4 prerequisite shape に合わせて補正し、frontmatter `状態` を `approved` へ更新し、`active parity target_id` と `validate` / `sync` の exit code を明示した。

#### 実行コマンド / 結果
```bash
sed -n '1,240p' spec-dock/active/context-pack.md
sed -n '1,220p' spec-dock/active/{initiative,epic,issue}/{requirement,design,plan,report}.md
sed -n '1,240p' spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00060-meta-json-dependency-schema-and-reader-alignment/{requirement,design,plan,report}.md
sed -n '1,240p' spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00062-downstream-parity-and-cutover-readiness/report.md
sed -n '1,260p' spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00063-final-regression-parity-and-cutover-closure/{requirement,design,plan}.md
git --no-pager diff -- spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00063-final-regression-parity-and-cutover-closure/{requirement,design,plan}.md
git status --short

- active context: initiative=`init-local-00003`, epic=`epic-00059`, issue=`iss-00063`
- current implementation: `.meta.json` 単一 SoT、shared topology reader、dogfooding cutover 完了を確認
- 初回 spec review: fail（status mismatch semantics / inherited-vs-rerun ambiguity / parity procedure不足）
- 補正後: `iss-00063` docs と `iss-00062/report.md` prerequisite shape を更新
- 最終 spec review: pass（non-blocking P2: single-snapshot parity procedure を requirement/design にも昇格するとより堅い）
```

#### 変更したファイル
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00063-final-regression-parity-and-cutover-closure/requirement.md` - T4 fail-closed blocker semantics、inherited regression contract、ancillary subset の扱いを current reality に合わせて補正
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00063-final-regression-parity-and-cutover-closure/design.md` - prerequisite / escalation / substitution rule を current repo reality と同一 snapshot parity discipline に整合
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00063-final-regression-parity-and-cutover-closure/plan.md` - S02 に canonical graph extraction、no-intervening-change ルール、review-only / rerun-required 境界を追加
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00062-downstream-parity-and-cutover-readiness/report.md` - upstream prerequisite shape として `状態` / `active parity target_id` / exit code を明示
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00063-final-regression-parity-and-cutover-closure/report.md` - S01 実装準備ログを正本化

#### コミット
- なし（実装準備のみ。コミット未作成）

#### メモ
- `iss-00063` は code change issue ではなく close-out / evidence issue なので、S01 では docs と upstream prerequisite shape の整合だけを扱った。
- `iss-00062/report.md` の prerequisite shape を揃えたため、T4 は spec 上の blocker semantics と upstream report reality が一致した状態で再 review に出せる。
- SG1 spec review は pass 済みのため S02 以降へ進めるが、現時点では command rerun や epic close summary 更新はまだ未着手である。

---

## 遭遇した問題と解決 (任意)
- 問題: `iss-00063` の inherited regression suite が `iss-00062/report.md` の実測証跡と一致せず、さらに `iss-00062/report.md` の frontmatter/status が `draft` のままだった。
  - 解決: current spec を actual T3 evidence に合わせて補正し、`iss-00062/report.md` も T4 prerequisite shape に合わせて記録粒度を補った。

## 学んだこと (任意)
- T4 close-out issue は code 変更がなくても、T3 report の shape と evidence grammar がずれていると spec review で止まる。
- parity contract は command 出力の見比べだけでは不十分で、canonical graph 抽出元と same-snapshot discipline まで plan に落とす必要がある。

## 今後の推奨事項 (任意)
- S02 着手時は、まず `iss-00062/report.md` の prerequisite shape が維持されていることを再確認してから canonical tuple 抽出に入る。
- S02 の report 記録は command 実行の途中で `report.md` を更新せず、same-snapshot 観測を取り切った後にまとめて残す。
- non-blocking 改善として、S02 の single-snapshot parity procedure を requirement/design にも持ち上げると cross-artifact contract がさらに明確になる。

## 省略/例外メモ (必須)
- `sync` / `validate` / `active set` の rerun はまだ未実施。S01 は実装準備と spec review loop のみを対象とした。
