---
種別: artifact
ID: "20260729t062209z"
タイトル: "S08 ChatGPT Compatibility Decision"
状態: "archived"
作成者: "ChatGPT Pro / Codex Main"
最終更新: "2026-07-29"
親: ["iss-00334"]
template: "blank"
authority: "execution-input"
derived_from:
  - "artifacts/20260729t054034z-s08-chatgpt-implementation-work-packet.md"
  - "uncommitted S08 bounded implementation"
  - "GitHub chemitaro/spec-dock@ff5264689c192781d82ed05b4f02909042f3f47a"
reflected_to: ["report.md"]
---

# S08 ChatGPT Compatibility Decision

## Trigger

S08のtyped Planner ZIP／Reviewer JSONを導入した中間実装はfocused tests 107件を通過したが、既存application testsは`PlanningInvocationResult(..., transient_payload=...)`を使うため30件が`TypeError`となった。S10はapplicationのZIP-to-Candidate移行を所有する一方、各milestoneはS01〜S07 behaviorを壊さずGreenで閉じる必要がある。

最初のChatGPT follow-upはexisting conversationのmode判定不能でpre-submit error、次のfresh runは`prompt-commit-timeout`となった。exact targetを`--harvest --no-recover`で確認し、conversation IDなし、assistant turn 0、new user turnなし、live leaseなしであることからdefinitely-not-committedと判定した。attachmentを4点へ限定した新規session `iss00334-s08-compatibil-decision-r1`で再実行した。model evidenceは`requested=Pro`、`resolved=Pro`、`verified=yes`。

## Verdict

`GO`。これはcanonical sequencing defectではなく、S08からS10までのimplementation-boundary compatibility issueである。Plan amendmentは不要。

## S08 Bounded Compatibility Contract

1. `PlanningInvocationResult`はdeprecated、non-serializedな`transient_payload=bytes` constructor compatibilityを一時的に維持できる。
2. read-only compatibility viewは、typed `authoring_zip`なら`zip_bytes`、typed `review_json`なら`json_bytes`、legacy-only fakeならsupplied bytesを返す。
3. `pass/transport_received`で許されるauthorityは、typed output exactly one、またはlegacy-only payload exactly oneのどちらか一方。
4. both typed outputs、typed＋explicit legacy、pass＋no output、blocked／rejected＋any output、size／SHA mismatchを拒否する。
5. compatibility bytesは`to_dict()`、`repr`、equality、diagnostic、persistenceへ含めない。
6. production `invoke_issue_planning_chatgpt`はrole-correct typed outputだけを返し、legacy-only successを構築しない。
7. missing／ambiguous／cross-kind／invalid Oracle artifactをgeneric-only successへ変換しない。
8. S10完了時にapplication／test callersをtyped outputへ移行し、legacy-only constructor laneを削除する。

## Required Tests

- unchanged `tests/unit/application/test_issue_planning.py` 66件Green。
- legacy constructor positiveとnon-serialization。
- typed ZIP／JSON positiveとderived compatibility view。
- no output、both typed、typed＋legacy、failure＋payload、size／SHA mismatch、cross-kind negative。
- production adapterが`transient_payload=`でsuccessを構築しないfocused assertion。
- Planner ZIPをlegacy marker payloadとして誤解釈せず、S10前はCandidate publication 0でfail closed。
- 既存single-submit、same-session recovery、redaction、artifact integrityを維持。

## S10 Exclusive Ownership

- create／Semantic Revisionが`OracleAuthoringZipSnapshot`を直接consumeする。
- authoring ZIP validation／extractとCandidate builder接続。
- Planner／Semantic Revisionのlegacy marker path除去。
- Reviewが`OracleReviewJsonPayload`を直接consumeする。
- application／integration fakesのtyped migration。
- legacy compatibility laneの最終削除。

## Forbidden Shortcuts

- production direct Oracle adapterのgeneric-only success。
- arbitrary payload bytesからroleを推定する。
- adapter内でZIPをlegacy marker textへ変換する。
- S08でapplication／Candidate／Prompt／CLI／installer／projectionを変更する。
- S08でapplication testsをtyped fixtureへ書き換えて回帰を隠す。
- personal wrapper、API、shell、`--write-output` fallbackを戻す。
- compatibility laneをS10後も保持する。
