---
種別: 要件定義書（Issue）
ID: "iss-00230"
タイトル: "Compile Step Assurance Agent Routing And Context Policy"
関連GitHub: ["#230"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
親: ["epic-00224", "init-local-00003"]
---

# iss-00230 Compile Step Assurance Agent Routing And Context Policy — 要件定義

## 目的
- Issue-wide Assurance と step-local facts から、実行 step ごとの worker、reasoning effort、context mode、verification、reviewer obligation を決定できる runtime capability を追加する。
- Worker には必要十分な継続 context を渡しつつ、reviewer / consultant には clean-room independence を保証し、main orchestrator へ返る payload を bounded evidence に制限する。
- Current Runbook へ step assurance / context routing contract を展開し、agent が固定 skill kernel から動的な実行指示を取得できるようにする。

## 背景・現状
- `iss-00227` で Issue-local `assurance.json` と Profile / Complexity classification が導入された。
- `iss-00228` で fixed Skill kernel と current Runbook projection が導入された。
- `iss-00229` で Assurance profile に応じた planning artifact composition と source binding invalidation が導入された。
- しかし現状の Runbook は Issue-wide authority の表示に留まり、個別 step の task kind、risk、role に応じた agent routing / context transfer / review independence を表現できない。
- そのため軽量 step でも過剰な context / reviewer cycle になり、重い step では reviewer clean-room や return payload 制限が機械的に保証されない。

## スコープ
- 必須:
  - Step Assurance policy / schema を runtime source として追加する。
  - Step facts と Issue Assurance から effective obligation を決定する domain model を追加する。
  - Role / task / risk に応じた context routing policy を追加し、`recent_fork`、`bounded_packet`、`clean_room`、`minimal_packet` を決定する。
  - Context Packet と Reviewer Evidence Packet を generated projection として作成する。
  - `workflow next issue-execution` の Runbook JSON / Markdown に、active issue の step routing summary と context contract を含める。
  - Worker continuation は same source binding / same source revision / same goal / same scope / same allowed paths / compatible risk のときだけ許可する。
  - Worker continuation の前に current HEAD、worktree cleanliness、対象 files の bounded revalidation を行い、古い fork / packet の再利用を拒否する。
  - Invocation observability として、role、reasoning effort、context mode、policy version、packet hash、source hashes、fork turn count、include / exclude categories、returned evidence refs を machine-readable event として残す。
  - Reviewer / consultant 用 packet から author self-assessment、implementation transcript、previous reviewer verdict、private reasoning、raw full logs を除外する。
  - Main orchestrator への return contract は summary、changed files、verification result、evidence refs、unresolved risks、ledger note に制限する。
- 禁止:
  - Profile authority を `lite_candidate` で弱めること。
  - clean-room を生成できない reviewer invocation を silently allow すること。
  - Raw shell transcript、private reasoning、full test log を context packet や return payload の標準項目に含めること。
  - GitHub PR review trigger / blocker policy をこの Issue で変更すること。
- 対象外:
  - GitHub PR review policy compiler。
  - PR blocker / re-review semantics。
  - Cross-provider agent context transfer。
  - Private reasoning の保存または転送。

## 受け入れ条件
- AC-001:
  - docs-only、runtime behavior、migration、security-sensitive の各 step facts で、worker、reasoning effort、context mode、verification、reviewers が policy どおりに異なる。
- AC-002:
  - `dev-coder` は same source binding / same source revision / same goal / same scope / same allowed paths / compatible risk の範囲で `recent_fork` を利用でき、bounded current HEAD / worktree / file revalidation 後に継続できる。
- AC-003:
  - `code-reviewer`、`qa-reviewer`、`spec-reviewer` は常に `clean_room` を要求され、clean-room packet を生成できない場合は fail-closed になる。
- AC-004:
  - Reviewer packet へ author self-assessment、implementation transcript、previous reviewer verdict、private reasoning、raw full logs が含まれない。
- AC-005:
  - Consultant first pass は main / architect の推奨案を含まない clean-room packet を要求する。
- AC-006:
  - Source binding、source revision、goal、scope、allowed paths、risk が変更された場合、worker continuation は拒否される。
- AC-007:
  - Current Runbook JSON / Markdown は selected step の context contract、packet refs、reasoning / verification / reviewer obligation を表示する。
- AC-008:
  - Context packet / routing projection は ignored generated state に書かれ、tracked worktree に差分を残さない。
- AC-009:
  - Returned evidence refs は path / hash / missing reason を machine-readable に表現できる。
- AC-011:
  - Invocation event は role、reasoning effort、context mode、policy version、packet hash、source hashes、fork turn count、include / exclude categories、returned evidence refs を machine-readable に含む。
- AC-010:
  - Existing assurance / workflow behavior は backward compatible であり、assurance contract が missing / invalid の場合は既存の classification-required gate が優先される。

## 例外・エッジケース
- EC-001:
  - active issue が missing、requirement scaffold、assurance missing / invalid の場合、step assurance を生成せず既存 Runbook state を返す。
- EC-002:
  - policy file が missing / invalid JSON / schema mismatch の場合、reviewer clean-room は fail-closed、worker は strict bounded packet へ degrade する。
- EC-004:
  - current HEAD、worktree cleanliness、対象 files の bounded revalidation が失敗した場合、worker continuation は拒否され `bounded_packet` へ fallback する。
- EC-003:
  - selected step が指定されない場合、Runbook は plan から最初の未完了 implementation step を best-effort で選ぶ。判定不能なら issue-wide default を返し、implementation start を促さない。

## 用語
- Step Assurance:
  - Issue-wide Assurance と step-local facts を合成した step 単位の workflow obligation。
- Context Mode:
  - Agent invocation に渡せる context 形態。`recent_fork`、`bounded_packet`、`clean_room`、`minimal_packet`。
- Context Packet:
  - source binding と policy decision に紐づく generated invocation payload。
- Reviewer Evidence Packet:
  - clean-room reviewer に渡すため、implementation transcript や previous verdict を除外した evidence-only packet。
- Bounded Return Contract:
  - sub-agent から main orchestrator へ戻せる項目を制限する契約。

## 未確定事項
- なし。
