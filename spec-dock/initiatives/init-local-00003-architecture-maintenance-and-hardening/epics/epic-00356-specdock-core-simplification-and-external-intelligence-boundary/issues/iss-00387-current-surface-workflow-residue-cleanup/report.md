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

変更は70 approved pathsに限定され、差分は187 additions / 7353 deletions。`tests/**` は107 additions / 6900 deletionsで、削除test LOC / 削除production・docs・config LOCは `6900 / 453 = 15.23`（情報値）となった。candidate decision coverageとremovable closureはいずれも1.0である。Current structural behavior、issue-start checkout ordering、二つのinstalled skill、consumer CI、authoritative Historical evidence、Epic #384所有領域は保持した。

## Verification

- Admission: branch `iss-00387-current-surface-workflow-residue-cleanup-v5`、implementation baseline `7e1c1fe8b25b8062405a62f467be55689a589ca7`、active `iss-00387`、dependency ready=true。baseline metricsは2710 collected、tracked Python LOC 97524、tracked test files 113、fixtures 27。
- Blue / Red: Luna Max coderがsix Current discussions filesをexact canonical rewriteへ修復し、独立Red verifierがC10〜C40をblocking finding 0でPASS判定した。provider/dogfood parity、deleted-node refs 0、current Issue R/D/P/Report差分0を確認した。
- Baseline positive observers: `test_set_active.py` 47 passed、issue lifecycle 38 passed、storage core 4 passed。post-changeは46 / 26 / 2 passedで、retired casesだけが減少した。
- Focused C50: set-active + authoring 242 passed、storage/lifecycle/doctor shard 29 passed、init/update shard 201 passed in 24:59。
- Static / ordinary: `make lint`でRuff check、Ruff format、mypyが全PASS。ordinary `uv run pytest`は1436 passed / 1077 policy-skipped in 56.89s。
- C40-09: collection 2513、full-regression ledger 15 rows、timing 243 nodes、deleted-node refs 0、verifier CLI help PASS。exact full verifier本体はPlanどおりpre-commitでは実行せず、clean final SHAへ延期した。
- Package / consumer: clean buildでone wheel / one sdistを生成し、wheel SHA-256 `80752167f3ad68492bf9a29bd381687d2637e61cd0197b1d223eca05b3c207dd`、sdist SHA-256 `a3c2361c6f8a9432925a78414d1993e92eda1ed3e3c3c63e12c8f6abad7f2172`を前後一致確認した。同じwheelからfresh initし、empty tree validateはexpected status 1 / exact `error: No nodes found.`、help、二skill、CI、`.codex`不在、Current provider parityを確認した。保持した二temporary directoryはC90-04でexact path照合後に削除し、不在を確認した。
- Test budget after: 2513 collected、tracked Python LOC 93795、tracked test files 91、fixtures 6。deltaは -197 collected、-3729 LOC、-22 files、-21 fixturesで、全指標純増なし。
- SpecDock integrity: `validate` 230 nodes、`sync --no-github`、再`validate` 230 nodesが成功し、sync後のunstaged/non-ignored untracked差分は0。

## Residual Risks / Follow-ups

- C60-02 exact full-regression verifierは、Planどおりcommit/push後にHEAD・configured upstream・remote tipが一致するclean `FINAL_SHA`上で一度だけ実行する。version管理ledgerのN/A/deferred行は変更しない。
- 同じfixed `FINAL_SHA`へChatGPT Code Review StrictとChatGPT Final Quality Gate Strictを束縛し、P0/P1=0、`review_status=pass`、PR checks passをhuman merge前に確認する。
- human merge前のため`issue finish`は実行しない。
