---
種別: disc
ID: "20260601t092641z-disc"
タイトル: "Deep consultant lifecycle transition decision"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-06-01"
親: ["iss-00149"]
関連: ["#149"]
authority: "synthesized"
derived_from:
  - "discussions/20260601t091408z-research-issue-finish-synthetic-approval-source-analysis.md"
  - "discussions/20260601t091408z-01-interview-closeout-recovery-path-preference.md"
  - "deep-consultant Planck 019e827d-7518-7310-92b8-207a9fda2d37"
reflected_to:
  - "requirement.md"
  - "report.md"
---

# 20260601t092641z-disc Deep consultant lifecycle transition decision

## 対象論点
- 今回整理する論点:
  - `issue start` が作る synthetic active selection と、`issue finish` が要求する lifecycle approval の間に supported transition がない問題を、ユーザー選択ではなく technical decision としてどう解くか。
- この synthesis が必要な理由:
  - `workflow_issue.md` は primary lifecycle を `issue start` -> `issue finish` と定義している。
  - しかし runtime は `runtime_active_selection` を lifecycle grants で拒否するため、primary lifecycle が自己矛盾している。
  - この判断は authority model と UX の整合問題であり、ユーザーに option 選択の負荷をかけるより、source-grounded analysis で決めるべきである。

## derived question sheets / research
- `interview`:
  - `20260601t091408z-01-interview-closeout-recovery-path-preference.md`
    - 当初は user interview として作成したが、ユーザー指摘により human preference question ではなく technical decision として扱う方針に変更した。
- `research`:
  - `20260601t091408z-research-issue-finish-synthetic-approval-source-analysis.md`
- その他の根拠:
  - deep-consultant Planck output (`019e827d-7518-7310-92b8-207a9fda2d37`)
  - `workflow_issue.md`
  - `workflow_spec_authoring.md`
  - `authority.py`
  - `set_active.py`
  - `issue_lifecycle.py`
  - `tests/domain_runtime/test_authority.py`
  - `tests/cli_runtime/test_issue_lifecycle.py`

## synthesis
- 合意済みのこと:
  - 根本原因は UI / guidance 不足だけではなく、state transition / authority model の欠落である。
  - `issue start` は作業対象を選ぶ synthetic approval を作り、`issue finish` は lifecycle closure を許可する approval を要求する。この区別自体は正しい。
  - 問題は、その正しい区別の間に official transition path がなく、手動 `active.json` 編集だけが実質 workaround になっていることである。
- 未合意 / 未確定のこと:
  - なし。ユーザーは option 選択ではなく deep-consultant analysis に基づく合理判断を求めた。
- source-grounded に解決できたこと:
  - Option A を採用する。ただし synthetic approval を domain gate で許可するのではなく、`issue finish` 内で finish-scoped lifecycle transition を作る。

## 選択肢 / tradeoff
- Option A: `issue finish` が finish-scoped lifecycle transition を内部生成する
  - Pros:
    - `issue start` -> `issue finish` の primary lifecycle を回復できる。
    - operator が追加 command を覚える必要がない。
    - transition 前に local preconditions を fail-closed で検査すれば authority boundary を維持できる。
  - Cons:
    - 実装を雑にすると `runtime_active_selection` を lifecycle approval と同一視する regression になり得る。
    - `issue finish` が active state mutation と closeout を兼ねるため、失敗時の再実行性と guidance を明確にする必要がある。
- Option B: 明示 command を追加する
  - Pros:
    - approval transition が明示的になる。
  - Cons:
    - 独立した人間承認イベントが必要という証拠がない現状では過剰。
    - primary lifecycle が `issue start` -> extra command -> `issue finish` になり、docs と運用の乖離を再発させやすい。
- Option C: guidance 改善のみ
  - Pros:
    - 小さい変更で diagnostics は改善する。
  - Cons:
    - supported transition 不在という root cause を解決しない。
    - GitHub #149 の expected behavior を満たさない。

## reflection proposal
- canonical docs / workflow / template / skill guidance へ反映すべき候補:
  - `workflow_issue.md` は、`issue finish` が supported finish-scoped lifecycle transition を内部で行う条件と、PR delivery / review / test completion の非保証を明記する。
  - CLI error guidance は、manual `active.json` 編集ではなく official path を示す。
  - active/context-pack 表示は、synthetic selection と lifecycle-ready state の差を operator が理解できる表現へ調整する。
- まだ proposal に留める理由:
  - design phase で具体的な state persistence timing、promotion decision token、test boundaries を確定する必要がある。

## ADR candidate triage
- ADR candidate か:
  - no
- hard to reverse:
  - no
- surprising without context:
  - medium
- real tradeoff:
  - yes
- ADR 化しない場合の反映先:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `workflow_issue.md`
  - `report.md`

## 推奨案
- Option A を採用する。
- ただし、domain authority gate の invariant は変えない。
- `issue finish` は active issue の synthetic record を検出した場合、close / active clear の前に existing local preconditions を fail-closed で検査し、成立時だけ issue-finish-scoped lifecycle transition を内部生成する。
- その後、既存の `issue_finish` authority gate を通してから GitHub close / active clear / lifecycle-owned post-mutation sync へ進む。
- transition は `issue_finish` に限定し、`implementation_start` / `issue_ready` / `phase_completion` を同時に自動昇格しない。

## 推奨反映先
- `requirement.md`:
  - Q-001 を未確定事項から決定事項へ移す。
  - Option A を採用し、B / C を単独解として棄却する。
  - non-goals と成立条件 / 失敗条件を追加する。
- `design.md`:
  - finish-scoped lifecycle transition の責務境界、persistence timing、promotion decision token を設計する。
- `plan.md`:
  - Red: `issue start` 後の `issue finish` が現状 fail する characterization。
  - Green: supported transition 後に close / already-closed / active clear が通る。
  - Negative: stale record / unresolved EAL / proposed delegated artifacts は close 前に fail-closed。
- `ADR`:
  - 不要。issue-local lifecycle repair として扱える。
- `report.md` Evidence Adoption Ledger:
  - deep-consultant decision を adopted として記録する。

## 未採用 / deferred 理由
- 未採用:
  - Option B:
    - 独立した人間承認イベントが必要という証拠がないため過剰。
  - Option C:
    - guidance 改善は補助施策として有効だが、root cause を解決しない。
- deferred:
  - `implementation_start` / `issue_ready` / `phase_completion` の broader transition UX はこの issue の対象外。必要なら follow-up。

## 次アクション
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - `requirement.md` の `未確定事項` を `決定事項` に置き換える。
  - `report.md` の D-001 / EAL-003 / Spec Authoring Gate を user-question blocked から consultant decision adopted へ更新する。
- 追加で作る discussion docs:
  - なし。
