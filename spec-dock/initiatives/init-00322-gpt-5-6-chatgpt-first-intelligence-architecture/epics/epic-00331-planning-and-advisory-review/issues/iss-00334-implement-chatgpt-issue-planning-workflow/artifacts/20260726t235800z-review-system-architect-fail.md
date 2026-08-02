---
種別: "architecture specialist review"
Issue: "iss-00334"
reviewer_role: "system-architect"
specialist_status: "fail"
source_head: "eadbfa544ad972c799162552f5684482d26e89b5"
created_at_utc: "2026-07-26T23:58:00Z"
authority: "read-only specialist evidence"
---

# iss-00334 architecture specialist review — FAIL

## Scope

Canonical Issue `requirement.md`、`design.md`、`plan.md`、既存の GitHub preflight、ChatGPT backend invocation、archive review、runbook transaction、binary artifact publication の実装を read-only で確認した。

## Verdict

- `specialist_status: fail`
- lifecycle 後半の公開入口、multi-file adoption の transaction semantics、REQ-022 の archive safety closure が実装開始を止める。
- canonical spec-reviewer pass、promotion、implementation readiness は主張しない。

## Blocking findings

### ARCH-ISS00334-001 — Public lifecycle route

`REQ-009`〜`REQ-013` が要求する Human Gate、adoption、publication、readiness を official Skill または利用者から呼び出す公開契約がなかった。create、revise、review の内部 service だけでは walking skeleton を実行できず、Design と Plan が supported callable surface、handler、help、positive／negative E2E を所有する必要がある。

### ARCH-ISS00334-002 — Crash-safe adoption transaction

三文書置換について stage、backup、commit、途中 crash、rollback failure、commit 後の push failure、same-operation retry の意味論が未確定だった。既存 `runbook_store.py` の stage／backup／restore pattern を shared scoped transaction primitive へ抽出し、fault injection で閉じる必要がある。

### ARCH-ISS00334-003 — Complete archive safety closure

`REQ-022` が列挙する path、special type、collision、encryption、nested archive、binary、CRC、resource limit の各拒否 class に独立した planned verification と partial-output absence が必要である。

## Reusable foundations

- `run_github_sync_preflight` は branch、clean tree、origin、fetch、local／remote equality を提供する。
- `backend_invoke.invoke_backend` は direct argv、timeout、bounded diagnostics の基盤になる。
- `review_pack_input(input_path)` は named data-only contract へ bounded extension できるが、generic default semantics の characterization test が必要である。
- installer は `spec-dock-chatgpt` executable bit を明示的に検証する必要がある。

## Required disposition

Design／Plan amendment へ戻し、公開 `planning apply` route、transaction／recovery state machine、REQ-022 全拒否 class の closure matrix を確定する。その後、fresh specialist evidence と fresh canonical `spec-reviewer` を取得する。

この artifact は read-only specialist result であり、canonical 文書を変更しない。
