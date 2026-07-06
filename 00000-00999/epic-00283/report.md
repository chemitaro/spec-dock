---
種別: レポート（Epic）
ID: "epic-00283"
タイトル: "ChatGPT Zip Authoring Pack Automation"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-06"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["init-local-00003"]
---

# epic-00283 ChatGPT Zip Authoring Pack Automation — レポート（進捗 / 決定 / 結果）

## 進捗サマリー

- 現在地:
  - `init-local-00003 Architecture Maintenance and Hardening` 配下に `epic-00283` を作成済み。
  - ここまでの ChatGPT Use / GPT-5.5 Pro Extended による調査・議論 artifact を `epic-00283/artifacts/` へ集約済み。
  - `spec-dock-clarification` の source-grounded grill loop と ChatGPT Use manual dogfood により、追加の blocking interview は不要と判断した。
  - `requirement.md` は具体化済み。ただし fresh `spec-reviewer` は未実施のため、phase promotion はまだ成立していない。
- 次のマイルストーン:
  - `requirement.md` を fresh `spec-reviewer` に通す。
  - requirement gate pass 後、同じ manual ChatGPT Use dogfood 方針を使って `design.md` を具体化する。
- ブロッカー:
  - requirement phase promotion には fresh `spec-reviewer` pass が必要。

## 証跡採用台帳（Evidence Adoption Ledger）

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | 部分採用（`partially_adopted`） | research | `requirement.md` | ChatGPT Use / GPT-5.5 Pro Extended を SpecDock authoring backend として使う方向性、evidence-only boundary、reviewer gate 非置換を要件へ採用した。初期配置が `init-local-00002` だった前提は後続判断で superseded。 | `artifacts/20260706t090820z-research-chatgpt-oracle-advanced-analysis.md` | requirement reviewer gate で妥当性を確認する |
| EAL-002 | 部分採用（`partially_adopted`） | discussion | `requirement.md` | Spec Authoring Batch の workflow redesign、bundle generation と staged adoption の分離、candidate Issue slicing の方向性を要件へ採用した。 | `artifacts/20260706t103820z-disc-chatgpt-spec-authoring-batch-workflow-redesign.md` | design phase で batch/ZIP lifecycle へ再整理する |
| EAL-003 | 部分採用（`partially_adopted`） | research | `requirement.md` | Reviewer gate の即時置換は行わず、ChatGPT output を advisory / shadow / authoring evidence として扱う制約を採用した。 | `artifacts/20260706t111806z-research-chatgpt-reviewer-gate-script-analysis.md` | reviewer replacement は v1 scope 外として維持する |
| EAL-004 | 採用（`adopted`） | research | `requirement.md` | Epic -> Issue / Issue bundle authoring automation の script candidates、dogfood-only placement、manual fallback、metrics を要件へ採用した。 | `artifacts/20260706t114128z-research-chatgpt-spec-authoring-automation-best-practices.md` | design / plan で Issue slicing へ具体化する |
| EAL-005 | 採用（`adopted`） | research | `requirement.md` | ZIP は first-class delivery format だが authority format ではないこと、profile は local assurance authority に残すこと、safe intake / validation / staged adoption を要件へ採用した。 | `artifacts/20260706t131838z-research-chatgpt-zip-authoring-pack-issue-grade-control.md` | design phase で ZIP schema / validator contract を固定する |
| EAL-006 | 部分採用（`partially_adopted`） | artifact | `requirement.md` | 新メンバー向けオンボーディング資料の要約・用語整理を requirement wording の補助 evidence として使った。canonical requirement には要件として再記述した。 | `artifacts/20260706t133043z-chatgpt-zip-authoring-onboarding-brief.md` | design / docs phase で正式 onboarding docs が必要か再判断する |
| EAL-007 | 採用（`adopted`） | chatgpt-use research | `requirement.md` | Manual ChatGPT Use dogfood により `unresolved_user_questions: none`、requirement draft、candidate Issue seeds、dogfood observations が得られたため、要件具体化へ採用した。 | `artifacts/20260706t140325z-research-epic-requirement-clarification-dogfood.md` | requirement reviewer gate へ進める |

## 目的整合台帳（Objective Alignment Ledger）

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | `requirement.md` は ChatGPT ZIP authoring pack を evidence-only delivery として扱い、SpecDock local authority を維持することを主目的にした。 | manual-tests dogfood、future runtime promotion、Issue seeds を副次要件として分離した。 | 低。reviewer gate replacement / shipped runtime 化を v1 scope 外に明記した。 | 未実施（fresh `spec-reviewer` pending） |

## 仕様 authoring ゲート（Spec Authoring Gate）

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | Parent initiative docs、workflow docs、`epic-00283/artifacts/`、ChatGPT Use manual dogfood output | Blocking question: none。Non-blocking design questions は raw ZIP storage、runtime promotion threshold、profile mismatch salvage、Strict/Critical specialist evidence path。 | EAL-001〜EAL-007 を採用 / 部分採用し、`requirement.md` へ再記述した。 | 未実施（not_run） | はい。phase promotion には fresh `spec-reviewer` pass が必要。 | fresh `spec-reviewer` を実行する。 |
| design | 未実施 | requirement reviewer gate 後に開始する | なし | 未実施 | はい。requirement gate pending。 | requirement pass 後に design authoring を開始する。 |
| plan | 未実施 | design reviewer gate 後に開始する | なし | 未実施 | はい。requirement / design gate pending。 | design pass 後に plan authoring を開始する。 |

## 委任ドラフト証跡（Delegated Draft Evidence）

- 委任 authoring の使用:
  - not used
- 未使用の場合:
  - 今回は main orchestrator が `spec-dock-clarification` と `chatgpt-use` を使って requirement clarification / authoring を実施した。
  - ChatGPT Use output は delegated draft ではなく advisory research evidence として `artifacts/20260706t140325z-research-epic-requirement-clarification-dogfood.md` に保存した。
- lifecycle state:
  - `produced` 相当の research evidence はあるが、delegated draft workflow としては not used。
- 昇格判断:
  - canonical `requirement.md` へ採用した内容は EAL-007 として記録した。

## 決定事項（ADRリンク）

- 該当なし。

## 完了した Issue / PR / Release

- 該当なし。

## 受け入れ条件（E-AC）の達成状況

- E-AC-001〜E-AC-012:
  - 未実施。Requirement authoring phase であり、implementation / dogfood scripts は未着手。

## フォローアップ（別Issue化）

- 未作成:
  - Dogfood Oracle ZIP Authoring Preflight And Prompt Pack
  - Implement Safe ZIP Intake And Schema Validation
  - Implement Oracle ZIP Diff And Staged Artifact Rendering
  - Implement Profile Controlled Selected Skeleton Fill Validation
  - Dogfood Candidate Only Epic To Issue ZIP Pack
  - Dogfood Existing Issue Selected Profile ZIP Pack
  - Dogfood ZIP Mismatch And Stale Probe
  - Document ZIP Authoring Pack Workflow And Adoption Ledger Examples
  - Evaluate Dogfood Metrics And Runtime Promotion Criteria

## 省略/例外メモ

- `epic-00283` の作成時、runtime が GitHub issue `#283` を自動作成した。
- ChatGPT manual dogfood run では、GitHub connector が current branch を `unavailable` と扱い、default branch `main` を検査した。したがって ChatGPT output は branch-sensitive authority ではなく、attached local sources と照合した advisory evidence として扱う。
