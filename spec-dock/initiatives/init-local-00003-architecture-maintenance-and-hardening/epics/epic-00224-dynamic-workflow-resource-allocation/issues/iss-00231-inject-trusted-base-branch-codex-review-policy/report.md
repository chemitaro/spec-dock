---
種別: 実装報告書（Issue）
ID: "iss-00231"
タイトル: "Inject Trusted Base Branch Codex Review Policy"
関連GitHub: ["#231"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00231 Inject Trusted Base Branch Codex Review Policy — 実装報告

## 仕様解釈・判断台帳
| ID | 状態 | 種別 | 起票元 | 判断 | 根拠 | 処置 | 証跡 | フォローアップ |
|---|---|---|---|---|---|---|---|---|
| D-231-001 | resolved | compatibility | orchestrator | `baseRefOid` が無い既存 fixture / older metadata では従来の exact `@codex review` body を維持する | Existing trigger helper tests が fixed body 前提で広く張られており、base SHA evidence が無い場合に policy fetch はできない | applied | `trigger_codex_review.sh`; `test_issue_176_s01_trigger_helper_posts_fixed_review_comment_once` | none |
| D-231-002 | resolved | implementation | orchestrator | base SHA がある場合だけ contents API から `.github/codex/review-policy.md` を取得し、multiline body を runtime が合成する | PR head policy を当該 PR review に使わない trust boundary が E-RQ-009 の中核 | applied | `test_issue_231_trigger_helper_uses_trusted_base_review_policy` | none |
| D-231-003 | resolved | scope | orchestrator | blocker-centric finding triage は iss-00232 へ残す | I05 は trigger / policy source / evidence が対象であり、finding disposition は I06 | applied | `plan.md`; Epic plan I05 / I06 | iss-00232 |
| D-231-004 | resolved | test-strategy | qa-reviewer | base SHA がある状態の policy missing / invalid fallback branches が未テストだった | happy path only; add fallback branch tests | policy fetch failure と empty/invalid decoded content の両方で fixed `@codex review` fallback と limitation を検証する | AC-003 / EC-002 の明示 obligation であり、security-sensitive compatibility branch | applied | qa-reviewer P1; `test_issue_231_trigger_helper_falls_back_when_base_policy_is_missing`; `test_issue_231_trigger_helper_falls_back_when_base_policy_is_invalid`; focused tests -> 19 passed | none |
| D-231-005 | resolved | implementation | code-reviewer | `baseRefOid` が無い場合も policy limitation を記録する | reviewer P1; fallback body だけでは machine-readable policy evidence が欠ける | applied | `review_policy_base_sha_missing`; fixed-body trigger helper test; focused tests -> 21 passed | none |
| D-231-006 | resolved | assurance | spec-reviewer | Parent I05 の trusted policy surface は strict / complex assurance として扱う | reviewer P1; trust boundary と GitHub write surface に関わる | applied | persisted risk facts `public_contract_change=true` / `rollback_difficulty_high=true`; `assurance verify` -> strict / complex pass | none |
| D-231-007 | resolved | scope-trace | spec-reviewer | I05 の policy schema / max size / doctor を明示的に回収または後続へ送る | reviewer P1; Epic plan I05 deliverables trace が曖昧だった | applied | max size runtime validation; fixed Markdown path validation; doctor capability deferred to rollout / operationalization | rollout / operationalization issue |
| D-231-008 | resolved | test-strategy | code-reviewer | `tc-231-001` は red capture ではなく green regression として扱う | reviewer P2; test was added with implementation and no separate red run was preserved | applied | plan evidence level changed to `covered-existing + green-regression`; focused tests -> 21 passed | none |
| D-231-009 | resolved | test-strategy | qa-reviewer | policy invalid fallback は empty content だけでなく UTF-8 decode failure も検証する | reviewer P2; EC-002 includes decode failure | applied | `test_issue_231_trigger_helper_falls_back_when_base_policy_is_not_utf8`; focused tests -> 22 passed | none |

## 証跡採用台帳
| ID | 採用状態 | 出所 | 対象 | 判断理由 | 証跡 | 次アクション |
|---|---|---|---|---|---|---|
| EAL-231-001 | adopted | Epic requirement / design / plan | requirement / design / plan / implementation | E-RQ-009 と E-AC-009〜010 を I05 の vertical slice として採用した | `spec-dock/active/epic/requirement.md`; `spec-dock/active/epic/design.md`; `spec-dock/active/epic/plan.md` | implementation |
| EAL-231-002 | adopted | focused tests | report / final gate | fixed-body compatibility、trusted base policy path、policy missing / invalid / non-UTF-8 / too-large fallback が通ることを確認した | `uv run pytest tests/unit/infra/test_init_update.py -k 'trigger_helper or wait_maps_trigger_comment_permission_denied_to_human_gate'` -> 22 passed | reviewer gate |

## 目的整合台帳
| 対象 | 主要目的の証跡 | 副次要件の証跡 | 逆転リスク | レビュアー判定 |
|---|---|---|---|---|
| trusted base policy trigger | base SHA contents API endpoint、policy hash、reviewed head SHA を body / JSON に含める | fixed-body compatibility fallback、policy limitation、permission limitation を維持 | low | pending re-review |

## 仕様 authoring ゲート
| フェーズ | 調査証跡 | 未確定事項 / 回答 | 採用判断 | レビュアー判定 | ブロック有無 | 昇格 / 次アクション |
|---|---|---|---|---|---|---|
| requirement / design / plan | Epic E-RQ-009、I05 plan、既存 `trigger_codex_review.sh`、既存 trigger helper tests | human decision required な未確定事項なし。Doctor capability は rollout / operationalization issue へ defer | adopted | pending final spec review | no | implementation complete; reviewer gates |

## 実装サマリー
- `.github/codex/review-policy.md` を bootstrap asset として追加した。
- `trigger_codex_review.sh` は PR metadata の `baseRefOid` がある場合、base SHA の policy file を読み、policy source / policy hash / reviewed head SHA を含む deterministic multiline `@codex review` body を投稿する。
- Base SHA が無い既存 path、policy missing / invalid / too-large、stale head、draft / non-open PR、permission denied、post recovery の既存 behavior は fail-closed fallback として維持した。

## セッションログ

### セッションログ（2026-06-23 S01）
#### 対象
- Step: S01
- AC/EC: AC-001, AC-002, AC-003, EC-001, EC-002, EC-003
- closure ids: tc-231-001〜tc-231-004

#### 実施内容
- Provider-side `trigger_codex_review.sh` に base SHA policy fetch と deterministic multiline body composition を追加した。
- Provider-side `.github/codex/review-policy.md` を追加した。
- Dogfooding mirror の `.agents/skills/github-pr-observation/scripts/trigger_codex_review.sh` と `.github/codex/review-policy.md` を同期した。
- Existing trigger helper fake を `baseRefOid` / policy contents / multiline POST body に対応させた。

#### 実行コマンド / 結果
```bash
uv run pytest tests/unit/infra/test_init_update.py -k 'trigger_helper'
# initial: 17 passed, 478 deselected
# after reviewer fallback / size / non-UTF-8 tests: 22 passed, 477 deselected
```

#### クロージャ網羅
| closure id | step | 検証証跡 | 結果 | メモ |
|---|---|---|---|---|
| tc-231-001 | S01 | `test_issue_231_trigger_helper_uses_trusted_base_review_policy` | pass | base SHA policy body / payload; no separate red run preserved |
| tc-231-002 | S01 | base SHA contents endpoint assertion / no caller body argument accepted by existing invalid-input test | pass | head policy は使用しない |
| tc-231-003 | S01 | existing fixed-body trigger helper tests | pass | baseRefOid absent path remains compatible |
| tc-231-004 | S01 | existing stale / draft / non-open / permission denied / recovery tests; policy missing / invalid / too-large fallback tests | pass | fail-closed behavior maintained |
| tc-231-004a | S01 | `test_issue_231_trigger_helper_falls_back_when_base_policy_is_missing`; `test_issue_231_trigger_helper_falls_back_when_base_policy_is_invalid`; `test_issue_231_trigger_helper_falls_back_when_base_policy_is_not_utf8`; `test_issue_231_trigger_helper_falls_back_when_base_policy_is_too_large` | pass | fixed body fallback with limitation |

### セッションログ（2026-06-23 S90/S99）
#### 実行コマンド / 結果
```bash
diff -u src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/trigger_codex_review.sh .agents/skills/github-pr-observation/scripts/trigger_codex_review.sh
# pass

diff -u src/spec_dock/assets/install_root/.github/codex/review-policy.md .github/codex/review-policy.md
# pass
```

## 最終品質ゲート
| gate | reviewer / command | evidence | result |
|---|---|---|---|
| focused tests | command | `uv run pytest tests/unit/infra/test_init_update.py -k 'trigger_helper'` -> 19 passed | pass |
| focused reviewer tests | command | `uv run pytest tests/unit/infra/test_init_update.py -k 'trigger_helper or wait_maps_trigger_comment_permission_denied_to_human_gate'` -> 22 passed | pass |
| parity | command | provider / dogfooding trigger script and review policy diffs -> pass | pass |
| lint | command | `make lint` -> ruff check pass; ruff format pass; mypy pass | pass |
| validate | command | `./spec-dock/scripts/spec-dock validate` -> ok nodes=148 | pass |
| assurance verify | command | `./spec-dock/scripts/spec-dock assurance verify --format json` -> strict / complex valid | pass |
| code review | code-reviewer | `review_status: pass`; previous P1/P2 closure verified | pass |
| QA review | qa-reviewer | `review_status: pass`; D-231-009 non-UTF-8 fallback added after P2 | pass |
| spec review | spec-reviewer | `review_status: pass`; remaining P2 stale E-RQ-009 summary row fixed in parent Epic plan | pass |
| final commit | git commit | this report and implementation change will be captured by the iss-00231 final commit | ready |

## 省略/例外メモ
- Real GitHub review trigger は network / external latency を含むため、Epic rollout / PR preparation で確認する。
- Finding blocker policy と re-review loop は iss-00232 の対象。
