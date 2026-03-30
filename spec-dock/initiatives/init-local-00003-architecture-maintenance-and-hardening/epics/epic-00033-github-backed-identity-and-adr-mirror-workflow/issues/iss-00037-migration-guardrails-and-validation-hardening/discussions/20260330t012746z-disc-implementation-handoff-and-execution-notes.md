---
種別: disc
ID: "20260330t012746z-disc"
タイトル: "implementation-handoff-and-execution-notes"
状態: "completed"
作成者: "Codex CLI"
最終更新: "2026-03-30"
親: ["iss-00037"]
関連: []
---

# 20260330t012746z-disc implementation-handoff-and-execution-notes

## 議題 (必須)
- `iss-00037` の実装担当者が、仕様確定済みの前提で迷わず着手できるように、開始条件・責務境界・優先順・証跡要件を明文化する。

## 背景 (必須)
- active context は `init-local-00003` / `epic-00033` / `iss-00037` である。
- `iss-00034` / `iss-00035` / `iss-00036` / `iss-00040` は current contract をすでに実装済みで、`iss-00037` は migration boundary の final closure owner である。
- `iss-00038` は full docs parity / final close-out を担当するため、今回の docs scope は minimal boundary docs diff に限定する。
- 現在の正本:
  - `requirement.md`
  - `design.md`
  - `plan.md`
- 現時点の確認結果:
  - `python -m unittest tests.cli_runtime.test_validate -v` は pass
  - `./spec-dock/scripts/spec-dock validate` は pass
  - current spec review は `pass`

## 選択肢 (必須)
- Option A:
  - 内容:
    - `iss-00037` でも新しい migration 用 runtime behavior や self-healing path を追加して閉じる。
  - Pros:
    - reviewer 向けの見かけ上の専用証跡は作りやすい。
  - Cons:
    - epic requirement の「自動移行非目標」に反する。
    - issue scope が evidence hardening から逸脱する。
- Option B:
  - 内容:
    - 既存 contract を正本として、docs / validate / tests / report を clause-by-clause に束ね、必要最小差分だけ補う。
  - Pros:
    - epic-00033 と整合する。
    - `iss-00038` / `iss-00040` との ownership boundary を保てる。
    - 実装担当者が「何を増やさないべきか」を判断しやすい。
  - Cons:
    - gap の有無を慎重に見極める必要がある。

## 推奨案 (必須)
- Option B を採る。
- 理由:
  - `iss-00037` の役割は新規機能追加ではなく、migration boundary 3 条項の最終契約化だからである。
  - 既存の tests / docs / reports で多くの根拠は揃っており、今回は reviewer が再判定しやすい evidence bundle を作ることが主目的である。

## 実装担当者へのメッセージ (必須)
- まず [requirement.md](../requirement.md) と [design.md](../design.md) と [plan.md](../plan.md) を正本として読んでください。今回の成功条件は「新しい migration 機能を足すこと」ではなく、「clause-1/2/3 の evidence を reviewer が再判定できる形に閉じること」です。
- 変更の優先順は plan の `S01 -> S02 -> S03 -> S04` に従うのが安全です。特に `S02` は clause-1 / clause-2、`S03` は clause-3 に集中してください。
- 今回の scope では次をやらないでください。
  - old workspace 自動移行 tooling の追加
  - self-healing / silent auto-repair path の追加
  - `iss-00038` の full docs parity を先回りして閉じること
  - `iss-00040` の stale-contract cluster realignment を再度やり直すこと
- まず確認すべき実装・テストの正本は以下です。
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py`
  - `tests/cli_runtime/test_validate.py`
  - 必要に応じて `tests/cli_runtime/test_sync.py`
  - 必要に応じて `src/spec_dock/assets/spec_dock/docs/reference_github.md`
  - 必要に応じて `src/spec_dock/assets/spec_dock/docs/reference_naming.md`
- 最低限の開始確認として、次の green はすでに確認済みです。
  - `python -m unittest tests.cli_runtime.test_validate -v`
  - `./spec-dock/scripts/spec-dock validate`
- 実装中に true runtime defect を見つけたら、この issue の中で暗黙に scope を広げず、`report.md` に所見を残して stop / escalate してください。

## 次アクション (必須)
- `S01` で clause inventory と ownership boundary を report に残す。
- `S02` で clause-1 / clause-2 の docs / validate gap を最小差分で閉じる。
- `S03` で clause-3 の no-auto-repair / fail-fast / warning evidence を閉じる。
- `S04` で final closure bundle を `report.md` にまとめる。
- `S99` で required validation と final review を通す。
