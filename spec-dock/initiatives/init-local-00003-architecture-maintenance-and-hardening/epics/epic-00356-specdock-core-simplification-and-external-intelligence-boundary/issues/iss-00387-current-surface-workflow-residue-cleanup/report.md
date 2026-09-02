---
種別: レポート（Issue）
ID: "iss-00387"
タイトル: "Current Surface Workflow Residue Cleanup"
関連GitHub: ["#387"]
最終更新: "2026-08-31"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00356", "init-local-00003"]
---

# Result Summary

詳細: [Report Guide](../../../../../../docs/authoring/report.md)

## Outcome

Issue #387 の Current surface 残滓を、承認済み Requirement / Design / Plan に従って撤去した。`active set --checkout` の内部compatibility seam、旧Profile / Assurance / EAL / delegated review語彙、retirement-only scanner・mutation・absence assertion・fixture copyを、対応するCurrent docs、runtime、config、ledger/timing参照と一体で削除した。新規test、absence scanner、helper、安全装置、依存は追加していない。

変更は72 approved pathsに限定され、差分は210 additions / 7479 deletions。`tests/**` は64 additions / 6991 deletionsで、削除test LOC / 削除production・docs・config LOCは `6991 / 488 = 14.33`（情報値）となった。candidate decision coverageとremovable closureはいずれも1.0である。Current structural behavior、issue-start checkout ordering、二つのinstalled skill、consumer CI、authoritative Historical evidence、Epic #384所有領域は保持した。

## Verification

- Admission: branch `iss-00387-current-surface-workflow-residue-cleanup-v5`、implementation baseline `7e1c1fe8b25b8062405a62f467be55689a589ca7`、active `iss-00387`、dependency ready=true。baseline metricsは2710 collected、tracked Python LOC 97524、tracked test files 113、fixtures 27。
- Blue / Red: Luna Max coderがsix Current discussions filesをexact canonical rewriteへ修復し、独立Red verifierがC10〜C40をblocking finding 0でPASS判定した。provider/dogfood parity、deleted-node refs 0、current Issue R/D/P/Report差分0を確認した。
- Baseline positive observers: `test_set_active.py` 47 passed、issue lifecycle 38 passed、storage core 4 passed。post-changeは46 / 26 / 2 passedで、retired casesだけが減少した。
- Focused C50 repair replay: set-active + authoring 242 passed、storage/lifecycle/doctor shard 29 passed、init/update shard 201 passed in 25:49。
- Static / ordinary post-P1 replay: `make lint`でRuff check、Ruff format、mypyが全PASS。ordinary `uv run pytest`は1435 passed / 1075 policy-skipped in 57.41s。
- C40-09: collection 2513、full-regression ledger 15 rows、timing 243 nodes、deleted-node refs 0、verifier CLI help PASS。exact full verifier本体はPlanどおりpre-commitでは実行せず、clean final SHAへ延期した。
- Package / consumer repair replay: clean buildでone wheel / one sdistを生成し、wheel SHA-256 `d72f6b68d1d38d4647a32e4cc52b286327da41c284d47946980bcbbf3b371390`、sdist SHA-256 `d52dc4f292cc42e365cdd89d5fb1caef9368fee51a2251854064c452d079a6a1`を前後一致確認した。同じwheelからfresh initし、empty tree validateはexpected status 1 / exact `error: No nodes found.`、help、二skill、CI、`.codex`不在、Current provider parityを確認した。保持した二temporary directoryはC90-04でexact path照合後に削除し、不在を確認した。
- Test budget after P1 repair: 2510 collected、tracked Python LOC 93661、tracked test files 91、fixtures 6。deltaは -200 collected、-3863 LOC、-22 files、-21 fixturesで、全指標純増なし。
- SpecDock integrity: `validate` 230 nodes、`sync --no-github`、再`validate` 230 nodesが成功し、sync後のunstaged/non-ignored untracked差分は0。
- class=OTHER_SUBSTANTIVE_OR_AMBIGUOUS; repair_paths=tests/cli_runtime/test_active.py; invalidated=C50-01..C90-05; preimplementation=C00-01..C40-09 retained; temp_cleanup=/var/folders/0v/jkf8ysk1621277d4xmr584cc0000gn/T/tmp.GIijwM9Y9x,/var/folders/0v/jkf8ysk1621277d4xmr584cc0000gn/T/tmp.SvBxmwuPwV
- P1 repair decision ledger (8 items; decision coverage=1.0; removable closure=1.0):

  | Candidate | Decision | Retained consumer |
  |---|---|---|
  | `tests/cli_runtime/test_active.py::test_active_set_without_github_local_issue_without_deps_is_ready` | remove: 完全委譲済みskipで観測ゼロ | `TestSetActiveApplication.test_set_active_resolves_id_and_repo_scoped_github_target_without_cli` |
  | `tests/unit/infra/test_artifact_templates.py::HISTORICAL_ROUTE_MARKERS` | remove: 旧route marker専用定数 | 現行physical catalog/content/parity tests |
  | `tests/unit/infra/test_artifact_templates.py::test_historical_routes_are_not_current_and_retired_template_is_absent` | remove: 旧route/template不在専用test | `test_physical_catalog_current_catalog_is_exact_six`、current template/parity tests |
  | `test_templates_readme_stays_thin_without_restoring_legacy_artifact_workflow` | split: Guide参照positiveを `test_templates_readme_explains_template_guide_usage` としてretain、legacy marker loopをremove | template README navigation/catalog/link tests |
  | `test_current_initiative_and_epic_artifact_rules_keep_historical_types_non_creatable` | split: Historical-only typesとauthority flowをretain、旧profile/template/command不在assertionをremove | 同testのHistorical/current content assertions |
  | `test_current_issue_artifact_rules_keep_profile_routes_historical_only` | split: Historical-only typesとauthority flowをretain、旧profile/template/command不在assertionをremove | 同testのHistorical/current content assertions |
  | `tests/unit/infra/test_authoring_kit_assets.py::test_s90_retained_repository_guidelines_match_current_distribution_surface` | split: 現行 `.agents/**` / `.github/**` consumerをretain、`.codex/**`・`.github/agents/**`・host adapter不在assertionをremove | 同testの現行distribution path assertions |
  | `test_template_readme_navigation_catalogs_exact_scope_docs_and_current_artifacts` | split: scope/artifact catalogとlink resolverをretain、`analysis`・`repair`・`draft-` 不在assertionをremove | 同testのcatalog/link assertions |

## Residual Risks / Follow-ups

- C60-02 exact full-regression verifierは、Planどおりcommit/push後にHEAD・configured upstream・remote tipが一致するclean `FINAL_SHA`上で一度だけ実行する。version管理ledgerのN/A/deferred行は変更しない。
- 同じfixed `FINAL_SHA`へChatGPT Code Review StrictとChatGPT Final Quality Gate Strictを束縛し、P0/P1=0、`review_status=pass`、PR checks passをhuman merge前に確認する。
- human merge前のため`issue finish`は実行しない。
