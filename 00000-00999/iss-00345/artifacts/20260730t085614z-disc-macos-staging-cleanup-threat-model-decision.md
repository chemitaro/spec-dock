---
種別: disc
ID: "20260730t085614z-disc"
タイトル: "macOS staging cleanup threat model decision"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-07-30"
親: ["iss-00345"]
関連: []
authority: "proposed"
derived_from:
  - "report.md D-022 / EAL-004"
  - "ChatGPT Use session iss345-macos-staging-safety"
  - "fresh code-reviewer S02 findings"
reflected_to: []
---

# 20260730t085614z-disc macOS staging cleanup threat model decision

## 位置づけ
- 用途: 集まった質問回答や調査をもとに、意思決定前の synthesis、選択肢、tradeoff、reflection proposal、ADR candidate triage、推奨反映先を整理する。
- authority default: `proposed`。通常は artifact type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は synthesis / reflection proposal / adoption target / ADR triage の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 人間から回答を引き出し、回答欄や未回答事項を管理する場合は `interview` を使う。
- 生ログや未整理の思考は `blank`、事実確認や外部根拠は `research`、長期判断の固定は `adr` に分ける。
- この doc は proposal / synthesis であり、issue `report.md` の observed evidence ledger ではない。採否の最終証跡は canonical docs / ADR / `report.md` Evidence Adoption Ledger に昇格する。
- doc が大きくなりすぎたら、質問回答は `interview`、事実調査は `research`、raw capture は `blank`、長期決定は `adr` へ分割する。

## 対象論点 (必須)
- 今回整理する論点:
  - macOSのdestination-side named stagingで、same-UID非協調processがidentity確認後から`unlink`前にtemp pathnameを置換するraceを、supported contractとして防御するか。
  - macOS clone-capable success、cross-filesystem source、normal cleanup、non-owned entry非削除を同時に維持できるか。
- この synthesis が必要な理由:
  - S02実装とfresh code reviewで、公開macOS APIにFD-conditional unlinkまたは`O_TMPFILE`相当がないため、承認済み契約が同時充足不能と判明した。

## derived question sheets / research (必須)
- `interview`:
  - 未作成。architecture owner / userの採用判断が必要。
- `research`:
  - local runtime probe: `sys.platform=darwin`, `hasattr(os, "O_TMPFILE")==False`。
  - repo analysis: parent Epicの明示的threat-model除外はsource最終検証後、parent最終検証後、commit後の3窓であり、staging cleanup replacementは除外されていない。
- その他の根拠:
  - fresh code-reviewerはcheck→unlink raceによるnon-owned entry削除をP1として再現した。
  - ChatGPT Pro advisoryは、通常権限の公開APIでは7制約を同時充足できないと分析した。
  - deep-consultantはreviewer failを契約内と判断し、macOS successを維持する最小案としてEpic-level threat-model amendmentを推奨した。

## synthesis (必須)
- 合意済みのこと:
  - 現行`stat/fstat`→`unlink`は最終race windowを閉じられない。
  - random name、token、digest、追加identity checkだけでは絶対保証にならない。
  - Issue単独でmacOS supported guaranteeを縮小したり、same-UID actorを除外したりできない。
- 未合意 / 未確定のこと:
  - macOS成功を維持してsame-UIDの悪意ある内部temp置換をthreat model外にするか。
  - 絶対保証を維持してmacOS generic importを`publication_unsupported`にするか。
- source-grounded に解決できたこと:
  - macOS successはparent Epic designが所有し、変更はEpic design/planとaccepted ADRのamendmentを要する。
  - reviewer P1を無文書で過剰指摘として退けることはできない。

## 選択肢 / tradeoff (必須)
- Option A: Epicでsame-UIDの悪意ある内部staging置換を明示的にthreat model外とする。
  - Pros:
    - macOS clone-capable successとcross-filesystem sourceを維持できる。
    - trusted helperを新設せず、Issue 345のPRゴールへ最短で戻れる。
  - Cons:
    - non-owned entry非削除の絶対保証を狭めるsecurity contract変更である。
    - 残存TOCTOUをADRと運用文書へ明示する必要がある。
- Option B: macOS generic importを`publication_unsupported`にする。
  - Pros:
    - non-owned entry削除の絶対禁止を維持できる。
    - Linuxは`O_TMPFILE` + `linkat`でanonymous stagingを実装できる。
  - Cons:
    - parent Epicが明示するmacOS clone-capable successを失う。
    - 現在の主要開発platformでgeneric importが利用できない。
- Option C: trusted helper / distinct security principalを新設する。
  - Pros:
    - macOS successと強いadversarial safetyを両立できる可能性がある。
  - Cons:
    - daemon packaging、権限、FD transfer、upgrade、recoveryを伴う新Epic級の拡張である。
- Option D: normal successでもtempをretainedにする。
  - Pros:
    - non-owned deletionを避けながらmacOS publicationを維持できる。
  - Cons:
    - 毎回warningとpersistent tempを残し、承認済みnormal cleanup契約を壊すため非推奨。

## reflection proposal (必須)
- canonical docs / workflow / template / skill guidance へ反映すべき候補:
  - Option A採用時はEpic requirement/design/plan、accepted ADR、Issue requirement/design/planの順にthreat actorと保証境界を明記する。
  - cleanupはhigh-entropy name、`O_CREAT|O_EXCL|O_NOFOLLOW`、held FD、unlink直前identity check、不一致時retainedを維持する。
- まだ proposal に留める理由:
  - security/platform contractの変更であり、architecture owner / userの明示承認が必要。

## adoption target / 採用先候補 (必須)
- `requirement.md`:
  - Epic supported guaranteeとthreat actor、Issue cleanup safety boundary。
- `design.md`:
  - macOS named stagingの残存TOCTOU、mitigation、非対象actor。
- `plan.md`:
  - deterministic testsを「対象内race」と「明示除外race」に分離し、reviewer focusを固定。
- `ADR`:
  - macOS publicationのpublic-API限界とsame-UID trust boundary。
- `report.md` Evidence Adoption Ledger:
  - `EAL-004`を採用案に応じて`adopted`または`rejected`へ解消する。

## ADR triage / ADR candidate triage (必須)
- ADR candidate か:
  - yes
- hard to reverse:
  - yes
- surprising without context:
  - yes
- real tradeoff:
  - yes
- ADR 化しない場合の反映先:
  - not applicable

## 推奨案 (必須)
- Option Aを推奨する。
- 一般的なOS trust boundaryでは同一UID processを同一主体として扱うことが多く、macOS successを失わず、新Epic級のhelperを回避できるため。
- ただし無文書のwaiverにはせず、Epic/ADRで「内部temp名を監視してfinal identity check後に意図的置換するsame-UID actor」を明示的に除外する。

## 推奨反映先 (必須)
- `requirement.md`:
  - parent EpicとIssueのthreat-model / cleanup safety requirement。
- `design.md`:
  - supported platform matrix、macOS residual TOCTOU、mitigation。
- `plan.md`:
  - S02 cleanup tests、reviewer focus、platform evidence。
- `ADR`:
  - accepted architecture decisionとしてsame-UID trust boundaryを固定。
- `report.md` Evidence Adoption Ledger:
  - user approval後に`EAL-004 adopted`、D-022 resolvedへ更新。

## 未採用 / deferred 理由 (必須)
- 未採用:
  - なし。現時点では全案が未決定。
- deferred:
  - trusted helperはOption A/Bが不採用で、macOS successと絶対保証を両立する必要が確定した場合だけ別Epicで検討する。

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - userがOption A/B/Cを選択する。
  - owning Epic/ADRを先にamendし、Issue R/D/Pを追従させる。
  - fresh `spec-reviewer` passとexecution guidance readyを回復してS02を再開する。
- 追加で作る artifacts:
  - Option A/B採用時のEpic-level ADR amendment。
