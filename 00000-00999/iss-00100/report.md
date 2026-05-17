---
種別: 実装報告書（Issue）
ID: "iss-00100"
タイトル: "Discussion template hearing sheet and flexible note expansion"
関連GitHub: ["#100"]
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-05-17"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00067", "init-local-00003"]
---

# iss-00100 Discussion template hearing sheet and flexible note expansion — 実装報告（LOG）

## 実装サマリー (任意)
- `discussions/` template taxonomy を再整理し、要件定義フェーズで `interview`（ヒアリング記録）と `scratch`（作業メモ）を中心にした初期 catalog 方針を固定した。
- 2026-05-17 時点では requirement gate を通過済み。次に design / plan gate を通し、各 implementation step ごとの delegated implementation、review、commit に進む。

## 実装記録（セッションログ） (必須)

### 2026-05-17 19:30 - 20:16 JST

#### 対象
- Phase: requirement authoring / requirement review gate
- AC/EC: AC-001〜AC-010, EC-001〜EC-007

#### 実施内容
- ユーザー回答を反映し、Q3 は `authority` を doc type default + optional front matter override として固定した。
- Q4 は文書そのものの昇格や `promotion-record` type を採用せず、discussion context から新しい `adr` / `requirement.md` / `design.md` / `plan.md` を作成・修正する方針に固定した。
- `interview` は人間の回答負荷を下げる意思決定支援シートとして、複数回答案、選択肢比較、メリット/デメリット、リスク、ベストプラクティス分析、推奨案を必須にした。
- `scratch` は low-friction raw capture とし、本文構造の強制を最小限にした。
- requirement phase の fresh `spec-reviewer` review を実施し、`review_status: pass` を得た。
- reviewer の P2 補助指摘に従い、catalog proposal の `interview` 必須項目と authority 既定値を requirement に揃えた。

#### 実行コマンド / 結果
```bash
git diff --check
# pass

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=43
```

#### Step Contract Closure
| step | closure ids | close condition | evidence | result | notes |
|---|---|---|---|---|---|
| S01 | tc-001 | ... | ... | pass / approved-no-op / fail / blocked | ... |

#### Test Contract Closure
| closure id / test id | step | required | evidence level | pre-implementation evidence | verification command | result | notes |
|---|---|---|---|---|---|---|---|
| tc-001 | S01 | yes | red-required | ... | ... | pass / approved-no-op / fail / blocked | ... |

- `closure id / test id` は Central index の `id` を指す。別 alias を使う場合は `Closure Delta` で対応を記録する。

#### Closure Coverage
| closure id | step | verification evidence | result | notes |
|---|---|---|---|---|
| tc-001 | S01 | ... | pass / approved-no-op / fail / blocked | ... |

#### Closure Delta
| change | closure id | test id alias | resolves to closure id | reason | re-review required |
|---|---|---|---|---|---|
| none / added / removed / changed / alias-mapped | tc-001 | tc-001 / test-name | tc-001 | ... | yes / no |

#### Implementation Delegation Gate
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records evidence only.

| step | decision | required reason | delegated role | delegated scope | source of truth | allowed changes | forbidden changes | required verification | stop conditions | output required | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | delegated / approved-local-execution / degraded mode | multi-layer / shipped scaffold / pattern analysis / integration / large worker scope / none | repo-analyst / dev-coder / doc-writer / N/A | ... | ... | ... | ... | ... | ... | worker summary / changed files / verification / risks / integration decision | pass / fail / blocked |

#### Delegated Worker Evidence
| step | delegated role | delegated worker summary | changed files | tests run or docs-only verification | reviewer verdict | unresolved risks | parent integration decision |
|---|---|---|---|---|---|---|---|
| S01 | dev-coder / doc-writer / repo-analyst | ... | `path/to/file` | `command` -> pass / docs-only inspection -> pass | pass / fail / unavailable / denied / waived / provisional | none / ... | accepted / rejected / needs follow-up |

#### Parent Implementation Exception
| step | delegation unavailable/impossible reason | user approval / risk acceptance | allowed files | allowed operation | rollback plan | post-change verification | reviewer gate | unavailable / denied / host conflict / waiver handling |
|---|---|---|---|---|---|---|---|---|
| S01 | unavailable / denied / host conflict / impossible because ... | approval source / risk accepted: yes / no | `path/to/file` | ... | ... | `command` -> pass / docs-only inspection -> pass | reviewer role + passed / failed / unavailable / denied / waived / provisional | blocked / incomplete / waived with explicit risk acceptance / next action |

#### Workflow Delegation Consent
This table is for reviewer / read-only specialist workflow-scoped consent. Write-capable delegation such as `dev-coder` or `doc-writer` is recorded in `Implementation Delegation Gate` and `Delegated Worker Evidence`, not as generic workflow-scoped consent.

| consent source | repo / worktree | active issue | session | named roles | boundary | expires / invalidation condition | denied / unavailable reason | next action |
|---|---|---|---|---|---|---|---|---|
| user message 2026-05-17「スペックドックのissueの取り進め方のワークフローに則って」 | `/Users/iwasawayuuta/workspace/tools/spec-dock` | iss-00100 | current Codex session | spec-reviewer / code-reviewer / qa-reviewer / consultant / deep-consultant / read-only specialist | reviewer / read-only specialist scope only; destructive action, external publishing, credentialed access, scope expansion, write-capable delegation are excluded unless separately authorized | active issue changes, repo/worktree changes, session end, or user revocation | none | continue phase gates under workflow_issue.md |

#### Reviewer Gate Status
| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| requirement | requirement phase review | spec-reviewer | fresh | passed | N/A | proceed to design | reviewer `019e35a5-0758-7771-a072-2abf66edc6d7`; no P0/P1 blockers; P2 supporting-doc drift fixed after pass |

#### Code Review Gate
| step | reviewer | review scope | review_status | findings / fixes | re-review count | result |
|---|---|---|---|---|---|---|
| S01 | code-reviewer | step diff / tests / docs-report updates | pass / fail | ... | 0 | pass / blocked |

#### Step Commit Gate
| step | closure state | commit scope | commit hash / final ledger | post-commit clean check | no-op rationale | no-op checked contracts / files | no-op diff-clean command | no-op read-only confirmation |
|---|---|---|---|---|---|---|---|---|
| S01 | committed / approved-no-op | ... | <hash or final ledger reference> | `git status --short` -> clean | ... | ... | ... | ... |

#### 変更したファイル
- `spec-dock/active/issue/requirement.md` - 要件、AC/EC、authority、interview、scratch、note grandfathering 方針を具体化
- `spec-dock/.../discussions/20260517t075915z-disc-discussion-template-taxonomy-guide.md` - taxonomy / lifecycle の説明資料
- `spec-dock/.../discussions/20260517t103746z-disc-discussion-template-catalog-design-proposal.md` - 採用候補 catalog と項目案
- `spec-dock/.../discussions/20260517t104954z-disc-question-authority-level-placement.md` - Q3 の質問シートと回答
- `spec-dock/.../discussions/20260517t104958z-disc-question-promotion-record-type.md` - Q4 の質問シートと回答
- `spec-dock/active/issue/report.md` - requirement gate evidence

#### コミット
- 未作成。implementation step の commit gate とは分け、design / plan gate 通過後の step commit で記録する。

#### メモ
- requirement gate は pass。design phase では P2 の「interview authority default は一値」「interview 必須項目は requirement と一致」を採用済みの前提として扱う。

---

### 2026-05-17 HH:MM - HH:MM

#### 対象
- Phase: design authoring / design review gate
- AC/EC: AC-001〜AC-010, EC-001〜EC-007

#### 実施内容
- `design.md` をテンプレート状態から issue-specific design に更新した。
- 採用 catalog を `scratch` / `interview` / `research` / `disc` / `adr` とし、`note` は新規作成不可・既存 artifact grandfathered として設計に固定した。
- `commands/new.py` の parser、`application/create_node.py`、`domain/validation.py`、`app.py`、provider docs/templates、dogfooding mirror、stale scan、必須 test closure を file-change plan に含めた。
- `interview` は 1 file 1 ヒアリング主題、複数質問は repeatable question block とし、各質問ブロックに必須分析項目を持たせる設計にした。
- design phase の `spec-reviewer` loop を回し、最終 re-review で `review_status: pass` を得た。

#### 実行コマンド / 結果
```bash
git diff --check
# pass

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=43
```

#### Reviewer Gate Status
| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| design | design phase review | spec-reviewer | fresh | passed | N/A | proceed to plan | reviewer `019e35b9-4132-7ba2-b8b5-a0069af4c651`; prior design findings closed |

#### 変更したファイル
- `spec-dock/active/issue/design.md` - implementation-ready design、dependency analysis、module diagram、file-change plan、test strategy
- `spec-dock/.../discussions/20260517t075915z-disc-discussion-template-taxonomy-guide.md` - `interview` authority を `raw` default に整合
- `spec-dock/active/issue/report.md` - design gate evidence

---

### 2026-05-17 HH:MM - HH:MM

#### 対象
- Phase: plan authoring / plan review gate
- AC/EC: AC-001〜AC-010, EC-001〜EC-007

#### 実施内容
- `plan.md` をテンプレート状態から implementation-ready plan に更新した。
- `Spec-Locked Closure Index` に cl-001〜cl-010 を定義し、docs/templates、runtime/tests、installer/update、dogfooding mirror、stale docs、S90/S99 final gate を closure として固定した。
- S01〜S03、S90、S99 に delegation contract、具体テストケース、step closure contract、reviewer/commit/no-op gate を定義した。
- plan phase の `spec-reviewer` loop を回し、最終 re-review で `review_status: pass` を得た。
- reviewer の P2 指摘に従い、installer/update scaffold behavior は S02 で完全に閉じ、S03 は dogfooding mirror と stale-doc scan に限定する文言へ修正した。

#### 実行コマンド / 結果
```bash
git diff --check
# pass

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=43
```

#### Reviewer Gate Status
| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| plan | plan phase review | spec-reviewer | fresh | passed | N/A | proceed to implementation | reviewer `019e35c2-2796-77b0-92b1-2a8e17558648`; P2 wording ambiguity fixed after pass |

#### 変更したファイル
- `spec-dock/active/issue/plan.md` - Spec-Locked Closure Index、S01〜S03/S90/S99 implementation plan
- `spec-dock/active/issue/report.md` - plan gate evidence

---

### 2026-05-17 HH:MM - HH:MM

#### 対象
- Step: S01 provider docs/templates catalog
- AC/EC: AC-001, AC-002, AC-003, AC-004, AC-005, AC-008, AC-009, AC-010, EC-001, EC-002, EC-003, EC-004, EC-005, EC-006

#### 実施内容
- `doc-writer` に S01 を委任し、provider-side shipped docs/templates catalog を `scratch` / `interview` / `research` / `disc` / `adr` に更新した。
- `interview.md` と `scratch.md` を provider template catalog に追加し、provider-side `note.md` を削除した。
- `adr` / `disc` / `research` templates と shipped docs / README / workflow / rules docs に authority、reflection、retired `note`、`interview` / `scratch` の使い分けを追加した。
- 親側で S01 diff、template inventory、label assertion、stale scan、uppercase path check、`git diff --check` を確認した。

#### 実行コマンド / 結果
```bash
git diff --check
# pass

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=43

for label in 質問主題 回答してほしいこと なぜ質問するのか 背景 詳細説明 事前分析 回答案 選択肢比較 メリット デメリット リスク ベストプラクティス分析 推奨案 未回答時の影響 回答欄 回答後フォローアップ; do rg -q -- "$label" src/spec_dock/assets/spec_dock/templates/discussions/interview.md || exit 1; done; printf 'all interview labels present\n'
# all interview labels present

rg -n "new doc note|adr\|disc\|research\|note" src/spec_dock/assets/spec_dock/docs src/spec_dock/assets/spec_dock/templates src/spec_dock/assets/spec_dock/scripts/README.md
# no matches

ls src/spec_dock/assets/spec_dock/templates/discussions
# adr.md
# disc.md
# interview.md
# research.md
# scratch.md
```

#### Step Contract Closure
| step | closure ids | close condition | evidence | result | notes |
|---|---|---|---|---|---|
| S01 | cl-001, cl-002, cl-003 | S01 files changed, verification passes, report updated, spec-reviewer pass, commit created | verification evidence recorded; reviewer `019e35d0-11a1-7d71-8a49-dd79b796ab16` pass; commit pending | pass | runtime/tests and dogfooding mirror intentionally untouched |

#### Test Contract Closure
| closure id / test id | step | required | evidence level | pre-implementation evidence | verification command | result | notes |
|---|---|---|---|---|---|---|---|
| cl-001 | S01 | yes | inspect-only | old `note` catalog existed; no `interview.md` / `scratch.md` | stale scan over provider docs/templates/scripts README | pass | no current `new doc note` / old catalog examples found |
| cl-002 | S01 | yes | red-required | provider `interview.md` absent before S01 | interview label assertion | pass | required question-block labels present |
| cl-003 | S01 | yes | inspect-only | provider `scratch.md` absent before S01 | template inspection | pass | required body centered on `メモ`; organization fields optional |

#### Closure Coverage
| closure id | step | verification evidence | result | notes |
|---|---|---|---|---|
| cl-001 | S01 | stale scan + changed docs/templates inventory | pass | reviewer pending |
| cl-002 | S01 | label assertion command | pass | reviewer pending |
| cl-003 | S01 | `scratch.md` inspection | pass | reviewer pending |

#### Implementation Delegation Gate
| step | decision | required reason | delegated role | delegated scope | source of truth | allowed changes | forbidden changes | required verification | stop conditions | output required | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | delegated | shipped docs/templates / workflow text | doc-writer | provider-side docs/templates catalog only | requirement/design/plan S01 | S01 target files under `src/spec_dock/assets/spec_dock/{templates,docs,scripts}` | runtime/tests, dogfooding mirror, active issue docs/report, existing discussion artifact migration | `git diff --check`, interview label assertion, stale scan | path outside allowed scope, required label set cannot fit template, target docs contradict design | changed files, summary, verification result, risks | pass |

#### Delegated Worker Evidence
| step | delegated role | delegated worker summary | changed files | tests run or docs-only verification | reviewer verdict | unresolved risks | parent integration decision |
|---|---|---|---|---|---|---|---|
| S01 | doc-writer | provider-side shipped docs/templates catalog updated; runtime/tests/dogfooding mirror untouched | provider docs/templates listed below | `git diff --check` pass; label assertion pass; stale scan no matches | pending | S02 runtime and S03 dogfooding still pending | accepted for S01 review |

#### Reviewer Gate Status
| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| S01 | step reviewer | spec-reviewer | fresh | passed | N/A | proceed to commit | reviewer `019e35d0-11a1-7d71-8a49-dd79b796ab16`; no findings |

#### Step Commit Gate
| step | closure state | commit scope | commit hash / final ledger | post-commit clean check | no-op rationale | no-op checked contracts / files | no-op diff-clean command | no-op read-only confirmation |
|---|---|---|---|---|---|---|---|---|
| S01 | committed | provider docs/templates + S01 report evidence | pending until commit command completes | pending until post-commit check | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/templates/discussions/adr.md` - authority/reflection guidance
- `src/spec_dock/assets/spec_dock/templates/discussions/disc.md` - framing boundary and split guidance
- `src/spec_dock/assets/spec_dock/templates/discussions/research.md` - facts/uncertainty/decision implication guidance
- `src/spec_dock/assets/spec_dock/templates/discussions/interview.md` - new hearing/interview template
- `src/spec_dock/assets/spec_dock/templates/discussions/scratch.md` - new raw capture template
- `src/spec_dock/assets/spec_dock/templates/discussions/note.md` - retired from provider template catalog
- `src/spec_dock/assets/spec_dock/docs/*` and `src/spec_dock/assets/spec_dock/docs/rules/*/discussions.md` - shipped lifecycle/selection guidance
- `src/spec_dock/assets/spec_dock/templates/README.md` - template inventory
- `src/spec_dock/assets/spec_dock/scripts/README.md` - command catalog guidance

---

### 2026-05-17 HH:MM - HH:MM

#### 対象
- Step: S02 runtime allowlist, parser, validation, tests
- AC/EC: AC-006, AC-007, EC-007

#### 実施内容
- `dev-coder` に S02 を委任し、creatable discussion doc type を `adr` / `disc` / `research` / `interview` / `scratch` に更新した。
- `note` は parser の generic invalid choice ではなく use case 側の retired guidance で失敗するようにした。
- validation / legacy runtime constants は `note` を grandfathered type として許容しつつ、`interview` / `scratch` filenames も受けるように更新した。
- runtime tests と installer/update tests を更新し、new type creation、retired `note`、validation grandfathering、managed template prune を固定した。
- code-reviewer の P2 指摘を受け、grandfathered legacy sequence filename は既存系の `adr` / `disc` / `research` / `note` のみに限定した。新規 type の `interview` / `scratch` は timestamp 形式のみ validation で許容する。

#### 実行コマンド / 結果
```bash
python -m unittest tests.cli_runtime.test_new tests.cli_runtime.test_runtime_new_doc_s09 tests.cli_runtime.test_validate tests.test_init_update.TestInitUpdate.test_init_creates_expected_structure tests.test_init_update.TestInitUpdate.test_update_preserves_legacy_artifacts_inside_existing_node_trees
# Ran 97 tests in 116.426s
# OK

python -m unittest tests.cli_runtime.test_validate.TestCliValidate.test_validate_rejects_legacy_sequence_for_new_discussion_types tests.cli_runtime.test_validate.TestCliValidate.test_validate_accepts_research_discussion_docs
# Ran 2 tests in 1.961s
# OK

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=43

git diff --check
# pass
```

#### Step Contract Closure
| step | closure ids | close condition | evidence | result | notes |
|---|---|---|---|---|---|
| S02 | cl-004, cl-005, cl-006, cl-007 | targeted tests pass, validate pass, report updated, code-reviewer pass, commit created | tests/validate/diff-check pass; reviewer pass with P2 fixed; commit pending | in_progress | broader dogfooding mirror intentionally deferred to S03 |

#### Test Contract Closure
| closure id / test id | step | required | evidence level | pre-implementation evidence | verification command | result | notes |
|---|---|---|---|---|---|---|---|
| cl-004 | S02 | yes | red-required | parser/use case previously lacked `interview` / `scratch` creatable support | targeted unittest suite | pass | `new doc scratch/interview` covered |
| cl-005 | S02 | yes | red-required | `note` previously creatable / parser constrained choices | targeted unittest suite | pass | retired guidance suggests `scratch`, no generic invalid choice |
| cl-006 | S02 | yes | red-required | validation type set lacked `interview` / `scratch` | targeted unittest suite | pass | grandfathered timestamp/legacy `note` remains valid |
| cl-007 | S02 | yes | red-required | init/update scaffold previously shipped managed `note.md` | targeted init/update tests | pass | `interview.md` / `scratch.md` installed, managed `note.md` pruned |

#### Closure Coverage
| closure id | step | verification evidence | result | notes |
|---|---|---|---|---|
| cl-004 | S02 | targeted runtime tests | pass | code-reviewer pass |
| cl-005 | S02 | targeted retired note negative test | pass | code-reviewer pass |
| cl-006 | S02 | targeted validation tests | pass | code-reviewer pass; P2 legacy-sequence looseness fixed |
| cl-007 | S02 | targeted init/update tests | pass | code-reviewer pass |

#### Implementation Delegation Gate
| step | decision | required reason | delegated role | delegated scope | source of truth | allowed changes | forbidden changes | required verification | stop conditions | output required | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S02 | delegated | runtime / tests / scaffold behavior | dev-coder | runtime allowlist/parser/validation/tests only | requirement/design/plan S02 | S02 target runtime/test files | shipped docs/templates except test fixtures, dogfooding mirror, active issue docs/report, existing discussion artifact migration | targeted unittest suite, validate, diff-check | type policy requires design change, parser cannot route retired error, broad unrelated rewrite needed | changed files, tests, summary, risks | pass |

#### Delegated Worker Evidence
| step | delegated role | delegated worker summary | changed files | tests run or docs-only verification | reviewer verdict | unresolved risks | parent integration decision |
|---|---|---|---|---|---|---|---|
| S02 | dev-coder | creatable/current doc types and validation grandfathering split; tests updated | runtime/test files listed below | targeted unittest suite -> OK; validate -> pass; diff-check -> pass | pass | full `tests.test_init_update` expected to fail until S03 dogfooding mirror update | accepted; reviewer P2 fixed before commit |

#### Reviewer Gate Status
| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| S02 | step reviewer | code-reviewer | fresh | passed | P2 fixed before commit and re-reviewed | proceed to S02 commit | reviewer `019e35e8-b4db-7f71-b46e-ac4f92ab40c6`; no findings |

#### Step Commit Gate
| step | closure state | commit scope | commit hash / final ledger | post-commit clean check | no-op rationale | no-op checked contracts / files | no-op diff-clean command | no-op read-only confirmation |
|---|---|---|---|---|---|---|---|---|
| S02 | pending | runtime/tests + S02 report evidence | pending | pending | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py` - parser doc_type choices removal / help update
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py` - request type literal update
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py` - creatable/retired type split and new placeholders
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py` - accepted filename types include `interview` / `scratch` / grandfathered `note`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py` - legacy compatibility regex update
- `tests/cli_runtime/test_new.py` - CLI creation/retired note tests
- `tests/cli_runtime/test_runtime_new_doc_s09.py` - use case creation/filename tests
- `tests/cli_runtime/test_validate.py` - validation grandfathering and new-type legacy-sequence rejection tests
- `tests/test_init_update.py` - scaffold inventory/prune tests

---

### 2026-05-17 21:18 - 21:34 JST

#### 対象
- Step: S03 dogfooding mirror, stale-doc scan, report evidence
- AC/EC: AC-001, AC-003, AC-005, AC-006, AC-008, AC-009, AC-010, EC-006, EC-007

#### 実施内容
- 指定どおり最初に repo root で `uvx --from . spec-dock update .` を実行した。
- update command は `spec-dock: ok (update)` を返したが、packaged asset resolution が provider working tree と一致せず、`spec-dock/templates/discussions` は旧 `note.md` のままで、dogfooding docs に `new doc note` / `adr|disc|research|note` が残った。
- 上記を S03 の documented blocker として扱い、失敗した broad update 差分を戻したうえで、S03 許可範囲だけを local provider assets から直接同期した。
- 同期対象は `spec-dock/docs/`、`spec-dock/templates/`、stale scan 対象の `spec-dock/scripts/README.md` に限定した。provider source、runtime/tests、既存 issue discussion artifacts は変更していない。
- dogfooding `templates/discussions` は `adr.md` / `disc.md` / `interview.md` / `research.md` / `scratch.md` となり、managed `note.md` は削除された。
- 既存 `*-note-*.md` historical discussion artifacts は rename / migration せず維持した。

#### 実行コマンド / 結果
```bash
uvx --from . spec-dock update .
# spec-dock: (warn) repo-root shortcut already exists (skipped): /Users/iwasawayuuta/workspace/tools/spec-dock/spec
# spec-dock: ok (update) -> /Users/iwasawayuuta/workspace/tools/spec-dock
# blocker: dogfooding docs/templates still contained stale note catalog, so S03 used direct source-asset sync.

rsync -a --delete src/spec_dock/assets/spec_dock/docs/ spec-dock/docs/
rsync -a --delete src/spec_dock/assets/spec_dock/templates/ spec-dock/templates/
cp src/spec_dock/assets/spec_dock/scripts/README.md spec-dock/scripts/README.md
# pass

find spec-dock/templates/discussions -maxdepth 1 -type f -name '*.md' -print | sort
# spec-dock/templates/discussions/adr.md
# spec-dock/templates/discussions/disc.md
# spec-dock/templates/discussions/interview.md
# spec-dock/templates/discussions/research.md
# spec-dock/templates/discussions/scratch.md

rg -n "new doc note|adr\|disc\|research\|note|\{adr\|disc\|research\|note\}|note\.md|doc type.*note|note.*doc type" spec-dock/docs spec-dock/templates spec-dock/scripts/README.md
# no matches

diff -qr src/spec_dock/assets/spec_dock/templates/discussions spec-dock/templates/discussions
# no output

diff -qr src/spec_dock/assets/spec_dock/docs spec-dock/docs
# no output

diff -q src/spec_dock/assets/spec_dock/scripts/README.md spec-dock/scripts/README.md
# no output

find spec-dock/initiatives -path '*/discussions/*note*.md' -print | sort
# existing historical note artifacts remain present; no migration/rename was performed.

git diff --name-status -- 'spec-dock/initiatives/**/discussions/**'
# no output

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=43

git diff --check
# pass

rg --files | rg '[A-Z]'
# existing uppercase contract paths only, including README.md / AGENTS.md / LICENSE.
```

#### Step Contract Closure
| step | closure ids | close condition | evidence | result | notes |
|---|---|---|---|---|---|
| S03 | cl-008, cl-009 | dogfooding mirror updated, stale scan clear, historical note artifacts preserved, validate/diff-check pass, report updated | inventory, stale scan, provider/mirror diff, validate, diff-check | pass | preferred update command was attempted first but produced stale packaged content; direct source-asset sync used as safest repo-local alternative |

#### Test Contract Closure
| closure id / test id | step | required | evidence level | pre-implementation evidence | verification command | result | notes |
|---|---|---|---|---|---|---|---|
| cl-008 | S03 | yes | manual-required | dogfooding `templates/discussions` had managed `note.md` and lacked `interview.md` / `scratch.md` | inventory + provider/mirror `diff -qr` + validate | pass | existing historical `*-note-*.md` artifacts remain in node trees |
| cl-009 | S03 | yes | inspect-only | update attempt left stale `new doc note` / old catalog references in dogfooding docs | stale `rg` scan over dogfooding docs/templates/scripts README | pass | no current old-catalog command advertisement remains |

#### Closure Coverage
| closure id | step | verification evidence | result | notes |
|---|---|---|---|---|
| cl-008 | S03 | template inventory, provider/mirror diff, validate | pass | managed `note.md` pruned; no node tree migration |
| cl-009 | S03 | stale scan | pass | grandfathered note wording remains only outside stale patterns |

#### Implementation Delegation Gate
| step | decision | required reason | delegated role | delegated scope | source of truth | allowed changes | forbidden changes | required verification | stop conditions | output required | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S03 | delegated | dogfooding mirror / stale scan only | doc-writer | local provider asset sync for dogfooding docs/templates and report evidence | requirement/design/plan S03 | `spec-dock/docs/**`, `spec-dock/templates/**`, `spec-dock/scripts/README.md`, active issue `report.md` | `src/spec_dock/**`, `tests/**`, existing discussion artifact migration/rename, broad unrelated formatting | inventory, stale scan, provider/mirror diff, validate, diff-check | provider source/runtime/test blocker, update cannot be safely scoped, stale references remain | changed files, evidence, residual risks | pass |

#### Delegated Worker Evidence
| step | delegated role | delegated worker summary | changed files | tests run or docs-only verification | reviewer verdict | unresolved risks | parent integration decision |
|---|---|---|---|---|---|---|---|
| S03 | doc-writer | dogfooding mirror refreshed from local provider assets after preferred update command left stale catalog content | dogfooding docs/templates/scripts README + report | inventory/stale scan/provider diff/validate/diff-check -> pass | pending | `uvx --from . spec-dock update .` packaging result was stale; S03 did not edit provider source to fix packaging behavior | accepted for S03 review; scope closed by direct source-asset sync |

#### Reviewer Gate Status
| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| S03 | step reviewer | spec-reviewer | fresh | passed | P2 evidence wording fixed before commit | proceed to S03 commit | reviewer `019e35f0-3328-7af1-b662-0348a1ccc7a3`; functional contract satisfied |

#### Step Commit Gate
| step | closure state | commit scope | commit hash / final ledger | post-commit clean check | no-op rationale | no-op checked contracts / files | no-op diff-clean command | no-op read-only confirmation |
|---|---|---|---|---|---|---|---|---|
| S03 | pass | dogfooding docs/templates/scripts README + S03 report evidence | `bc9546a` | clean | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `spec-dock/docs/guide.md` - dogfooding lifecycle / discussion catalog guidance
- `spec-dock/docs/phase_design.md` - `scratch` / `interview` guidance
- `spec-dock/docs/phase_requirement.md` - `scratch` / `interview` guidance
- `spec-dock/docs/reference_naming.md` - current discussion type set and `note` grandfathering
- `spec-dock/docs/rules/{initiative,epic,issue}/discussions.md` - selection guide and current create commands
- `spec-dock/docs/workflow_{initiative,epic,issue}.md` - current `new doc` examples and retired `note` guidance
- `spec-dock/docs/workflow_spec_authoring.md` - discussion externalization/fixation guidance
- `spec-dock/scripts/README.md` - current `new doc` command catalog and retired `note` guidance
- `spec-dock/templates/README.md` - dogfooding template inventory
- `spec-dock/templates/discussions/{adr,disc,research,interview,scratch}.md` - dogfooding discussion templates
- `spec-dock/templates/discussions/note.md` - removed managed retired template
- `spec-dock/active/issue/report.md` - S03 evidence

---

### 2026-05-17 HH:MM - HH:MM

#### 対象
- Remediation after final QA/code/spec review failures
- AC/EC: AC-001, AC-002, AC-006, AC-009, AC-010, EC-007

#### 実施内容
- stale だった dogfooding runtime mirror を provider runtime から同期し、`spec-dock/scripts/spec_dock_runtime/**` と `spec-dock/scripts/spec-dock` を provider `src/spec_dock/assets/spec_dock/scripts/**` と整合させた。
- dogfooding CLI の `new doc --help` が `interview` / `scratch` を表示し、`note` retired guidance を示すことを確認した。
- `_assert_discussion_guidance_contract` の stale expectation を、current catalog の `interview` / `scratch` と `new doc note` absence に更新した。
- provider/installed `interview.md` が必須 label set を持つ contract test を追加した。
- shipped guidance rationale と dogfooding mirror に、`note` を `scratch` へ統合した理由として raw capture type の重複回避と認知的曖昧さの低減を明記した。

#### 実行コマンド / 結果
```bash
rsync -a --delete --exclude __pycache__ src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/ spec-dock/scripts/spec_dock_runtime/
cp src/spec_dock/assets/spec_dock/scripts/spec-dock spec-dock/scripts/spec-dock
# pass

diff -qr --exclude __pycache__ src/spec_dock/assets/spec_dock/scripts spec-dock/scripts
# no output

./spec-dock/scripts/spec-dock new doc --help
# doc_type help lists adr, disc, research, interview, scratch
# note is retired; use scratch for new raw capture docs

python -m unittest tests.test_init_update.TestInitUpdate.test_init_scaffolds_discussion_guidance_without_legacy_examples_across_asset_set tests.test_init_update.TestInitUpdate.test_update_refreshes_discussion_guidance_without_legacy_examples_across_asset_set tests.test_init_update.TestInitUpdate.test_init_creates_expected_structure
# Ran 3 tests in 0.277s
# OK

python -m unittest tests.cli_runtime.test_new.TestCliNew.test_new_help_exposes_only_doc_discussion_entrypoint tests.cli_runtime.test_new.TestCliNew.test_new_doc_note_is_retired_with_scratch_guidance tests.cli_runtime.test_validate.TestCliValidate.test_validate_rejects_legacy_sequence_for_new_discussion_types
# Ran 3 tests in 2.096s
# OK

python -m unittest tests.cli_runtime.test_new tests.cli_runtime.test_runtime_new_doc_s09 tests.cli_runtime.test_validate tests.test_init_update.TestInitUpdate.test_init_creates_expected_structure tests.test_init_update.TestInitUpdate.test_update_preserves_legacy_artifacts_inside_existing_node_trees tests.test_init_update.TestInitUpdate.test_init_scaffolds_discussion_guidance_without_legacy_examples_across_asset_set tests.test_init_update.TestInitUpdate.test_update_refreshes_discussion_guidance_without_legacy_examples_across_asset_set
# Ran 99 tests in 132.386s
# OK

rg -n "new doc note|adr\|disc\|research\|note|\{adr\|disc\|research\|note\}|note\.md|doc type.*note|note.*doc type" src/spec_dock/assets/spec_dock/docs src/spec_dock/assets/spec_dock/templates src/spec_dock/assets/spec_dock/scripts/README.md spec-dock/docs spec-dock/templates spec-dock/scripts/README.md
# no matches

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=43

git diff --check
# pass
```

#### Closure Coverage
| closure id | step | verification evidence | result | notes |
|---|---|---|---|---|
| cl-002 | remediation | provider/installed interview label contract tests added | pass | final targeted suite and integrated 99-test suite pass |
| cl-004 | remediation | dogfooding runtime help exposes `interview` / `scratch` | pass | provider/mirror runtime diff clean excluding pycache |
| cl-005 | remediation | dogfooding runtime help routes `note` to retired guidance | pass | use-case negative behavior covered by existing runtime tests |
| cl-008 | remediation | dogfooding runtime mirror synced from provider runtime | pass | docs/templates mirror had already been refreshed |
| cl-009 | remediation | guidance contract expects no current `new doc note` | pass | stale scan and guidance contract tests pass |

## Final Quality Gate (必須)

### S90 Docs Impact Resolution
| target | update required | owner | evidence | spec-reviewer result |
|---|---|---|---|---|
| docs / templates / README / workflow / skill / migration notes | yes | doc-writer + remediation | S01 provider docs/templates, S03 dogfooding mirror, remediation guide rationale, stale scan no matches, provider/dogfooding mirror diff clean | pass (`019e35fd-7734-7880-a255-676ebdf94d99`) |

### Final QA Gate
| reviewer | scope | integration test decision | evidence | result |
|---|---|---|---|---|
| qa-reviewer | whole issue test adequacy | added | first review found stale guidance contract and missing interview label contract; remediation added/updated tests; 99-test suite pass | pass (`019e35fd-7606-7dc1-82f8-c910d70ad26a`) |

### Final Code Review Gate
| reviewer | scope | findings / fixes | re-review count | result |
|---|---|---|---|---|
| code-reviewer | issue-wide integrated diff | first review found stale dogfooding runtime; remediation synced dogfooding runtime from provider and verified local help/new catalog | 1 | pass (`019e35fd-7688-77c3-9ad3-e49269102085`) |

### Final Spec Review Gate
| reviewer | scope | findings / fixes | re-review count | result |
|---|---|---|---|---|
| spec-reviewer | requirement / design / plan / report / implementation / tests / docs alignment | first review found final gate placeholders, update/dogfooding alignment risk, and missing note-to-scratch rationale; remediation and final ledger addressed these | 1 | pass (`019e35fd-7734-7880-a255-676ebdf94d99`) |

### Final Commit
| final report ledger | final commit scope | post-commit external evidence destination | result |
|---|---|---|---|
| final gates closed in report; post-commit hash to be added by final response ledger | remediation: dogfooding runtime mirror, guidance contract tests, interview label contract test, note-to-scratch rationale, final gate ledger | final response | ready |

## 遭遇した問題と解決 (任意)
- 問題: final review で dogfooding runtime mirror が provider runtime より古く、local `./spec-dock/scripts/spec-dock new doc --help` が旧 catalog を表示することが判明した。
  - 解決: provider `src/spec_dock/assets/spec_dock/scripts/**` から dogfooding `spec-dock/scripts/**` を同期し、local runtime help と provider/mirror diff を確認した。
- 問題: guidance contract tests が retired `note` を current command として期待していた。
  - 解決: `interview` / `scratch` を期待し、`new doc note` を current guidance から除外する contract へ更新した。

## 学んだこと (任意)
- docs/templates だけでなく dogfooding runtime mirror も scaffold-affecting change の検証対象に含める必要がある。
- `note` retired のような catalog change は、help text、guidance contract、installed scaffold content、validation grandfathering を同時に確認する必要がある。
- ...

## 今後の推奨事項 (任意)
- follow-up: `uvx --from . spec-dock update .` が作業ツリー provider asset ではなく stale packaged content を使った経路を別 issue で調査すると、dogfooding mirror 更新の手動同期を減らせる。
- ...

## 省略/例外メモ (必須)
- 該当なし
