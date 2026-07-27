---
種別: disc
ID: "20260727t060629z-disc-init-00322-defect-only-spec-review-charter"
タイトル: "init-00322限定 Defect-Only Spec Review Charter"
状態: "provisional-active"
作成者: "Codex Main"
最終更新: "2026-07-27"
親: ["init-00322"]
関連: ["epic-00331", "iss-00334"]
scope: "initiative"
scope_id: "init-00322"
authority: "explicit-latest-human-direction"
adoption_status: "provisional-working-agreement"
canonical_status: "non-authoritative-operating-evidence"
supersedes: "20260726t135536z-disc-init-00322-temporary-review-perspective-and-scope-charter.md"
effective_from: "2026-07-27"
expires_when:
  - "init-00322 is completed"
  - "the Human explicitly supersedes or withdraws this direction"
disposition_at_expiry: "abandoned-as-operating-authority; retained only as historical evidence"
reuse_outside_scope: "prohibited unless separately reviewed and explicitly adopted"
source_repository: "chemitaro/spec-dock"
source_branch: "iss-00334-implement-chatgpt-issue-planning-workflow"
source_commit: "a0e273ac94ae71207bc4ecc188028022b2acfdc4"
---

# init-00322限定 Defect-Only Spec Review Charter

## 1. 判断

`init-00322`のChatGPT Spec Reviewは、Blue Teamが作成した計画を尊重する欠陥検査である。

Reviewは設計、再設計、改善提案、一般化、理想architectureの提案を行わない。Blue Teamが採用したarchitecture、scope、責務分離、用語、実装方針を固定前提として扱い、その前提の内側にある実在する問題だけを報告する。

ChatGPTによる計画作成能力への信頼をdefaultとし、Red Teamが新しい設計を追加する必要性を証明する運用にはしない。

## 2. 有効範囲

- 対象: `init-00322`
- 現在の適用対象: `epic-00331`、`iss-00334`
- 対象活動: Requirement／Design／Plan／ReportのSpec Review
- 失効: Initiative完了、Human撤回、後継方針による置換
- 他Initiativeへの自動適用: 禁止

## 3. Reviewの対象

Red Teamが確認するのは次だけである。

1. 明示された要件の抜け漏れ。
2. Requirement／Design／Plan間の直接的な矛盾。
3. 同じ責務、step、test、IDの重複または衝突。
4. 記載内容、status、path、command、owner、依存順序のズレ。
5. 文書どおりに実装すると具体的に誤動作する箇所。
6. 文書どおりでは実装または検証を一意に進められない重大な曖昧さ。
7. 明示済みのsecurity、Human authority、不可逆mutation境界への直接違反。
8. 修正対象箇所が既に閉じた契約を再び壊していないか。

## 4. Reviewで行わないこと

Red Teamは次をfindingまたは修正要求にしない。

- より良いarchitecture、schema、interface、state machineの提案。
- reviewerが好む別設計への置換。
- 将来拡張、汎用化、追加hardening。
- 現在のOutcomeに不要な網羅性の追加。
- 新しいcommand、type、registry、proof、matrix、ledgerの提案。
- 「あると良い」「より完全になる」「best practiceである」という理由だけの指摘。
- sibling Issue、後続Epic、shared workflowが所有する設計。
- Blue Teamの設計前提を覆す指摘。
- 問題が存在しない箇所への改善案。
- replacement text、patch、修正版文書、修正版ZIPの生成。

architecture前提そのものに疑問がある場合、Red TeamはFAILや再設計案を出さず、`scope_owner=human_architecture_decision`としてMainへ一行でrouteする。Humanが明示的に再設計を承認しない限り、現在のarchitectureを維持する。

## 5. Finding成立条件

findingは次をすべて満たす場合だけ成立する。

1. exactな文書箇所が示される。
2. 違反している既存要件または同一Candidate内の矛盾が示される。
3. 現在のIssueで生じる具体的な悪影響が示される。
4. 問題がBlue Teamの設計前提を維持したまま修正可能である。
5. 単なる改善提案、将来リスク、好みではない。

一つでも満たさない場合、findingとして出力しない。

## 6. PriorityとGate

- P0: 現設計のまま進むと、明示されたHuman authorityまたは不可逆な安全境界を直接破る実証済み欠陥。
- P1: 現設計の内側にある直接的な矛盾または必須事項の欠落により、現在のIssueを正しく実装・検証できない欠陥。
- P2: 実装は進められるが、実在する記載ズレ、重複、追跡ミス。
- P3: 意味を誤読させる実在する軽微な欠陥。

改善提案にはpriorityを付けない。P0／P1が0件なら`review_status=pass`とする。

## 7. Review Scope

各ReviewはMainが指定した対象だけを確認する。

- 初回Review: Blue Teamが完成させた対象文書と、その直接の親要件。
- 修正後Review: admit済みfindingの閉鎖と、変更箇所による直接regressionだけ。
- 修正後Reviewで未変更領域をゼロベース再設計しない。
- 「その他の問題をすべて探す」「任意のmaterial ambiguity」「architecture全体を再評価する」というopen-ended scopeを禁止する。

新しい問題を認められるのは、変更箇所から直接発生した欠陥、またはP0相当の具体的な既存違反だけである。それ以外は今回のReview結果へ含めない。

## 8. 出力契約

ChatGPT Red Teamはrepo-local `spec-reviewer`と同等の簡潔なJSONだけを返す。

```json
{
  "findings": [
    {
      "title": "[P1] 問題を簡潔に記載",
      "body": "問題、既存契約への違反、具体的影響だけを一段落で記載する。改善案やreplacement designは書かない。",
      "confidence_score": 0.0,
      "priority": 1,
      "artifact_location": {
        "absolute_file_path": "...",
        "section_or_line": "..."
      }
    }
  ],
  "review_scope_summary": "...",
  "review_status": "pass",
  "review_status_reason": "...",
  "overall_confidence_score": 0.0
}
```

- Markdown report、設計案、traceability table、replacement blockを返さない。
- findingごとに修正方向を設計しない。
- 問題がなければ`findings=[]`と`review_status=pass`を返す。
- P2／P3は実在する問題だけを残し、改善提案は省略する。

## 9. Main Admission

Red結果はBlueへの直接命令ではない。Mainは各findingについてSection 5を確認する。

- 成立する欠陥: Blueへ最小修正対象として渡す。
- architecture提案、一般化、future feature: 棄却する。
- scope ownerが別: owning scopeへrouteし、現在のReviewをFAILにしない。
- Human判断が必要: 修正を開始せずHumanへ戻す。

Blueへ渡すのはadmit済みの問題記述だけである。Redが提案した設計、schema、replacement textは渡さない。

## 10. Blue Revision

- Blueはadmit済み欠陥だけを現在の設計前提内で最小修正する。
- unrelated cleanup、追加architecture、追加proofを行わない。
- complete-file置換が必要な場合も、意味差分はadmit済み欠陥へ限定する。
- 修正後ReviewはSection 7の限定scopeを使う。

## 11. 現在のサイクルへの適用

exact HEAD `a0e273ac94ae71207bc4ecc188028022b2acfdc4`に対するRed reviewと、その後の85 KB Blue proposalは、このCharter適用前のopen-ended promptで生成された。

- Red findingは自動的にadmitしない。
- Blue proposalは正本へ採用しない。
- `P1-17`、`P1-20`、`P1-21`、`P1-22`は、Section 5に基づいてMain／Humanが再判定する。
- 再判定でadmitされなかった内容を修正サイクルへ戻さない。
- 次のReview promptはこのCharterをtask contractとして使用する。

## 12. Prompt最小契約

次回以降のRed promptには、少なくとも次を明記する。

```text
Blue Teamのarchitectureと設計判断を固定前提として尊重する。
設計、再設計、改善提案、一般化を行わない。
指定scope内の実在する欠陥だけを確認する。
findingはexact evidence、既存契約違反、現在Issueへの具体的影響をすべて必要とする。
修正案、replacement text、新しいschema／interfaceを出力しない。
repo-local spec-reviewer互換のJSONだけを返す。
P0/P1が0件ならPASSとする。
```

## 13. Authority

衝突時の優先順位:

```text
explicit latest Human direction
→ accepted Initiative／Epic／Issue authority
→ this provisional Charter
→ Red／Blue output
```

本Charterは現在のReview運用を制御するが、canonical product architectureを変更しない。
