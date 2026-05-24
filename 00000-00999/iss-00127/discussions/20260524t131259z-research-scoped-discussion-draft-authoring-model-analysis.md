---
種別: research
ID: "20260524t131259z-research"
タイトル: "Scoped Discussion Draft Authoring Model Analysis"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-05-24"
親: ["iss-00127"]
関連: []
authority: "synthesized"
derived_from:
  - "user correction discussion 2026-05-24"
  - "deep-consultant Hubble analysis"
  - "deep-consultant Ohm analysis"
  - "deep-consultant Copernicus analysis"
reflected_to:
  - "iss-00127 requirement/design/plan (pending)"
---

# 20260524t131259z-research Scoped Discussion Draft Authoring Model Analysis

## 位置づけ
- この research は、`epic-00112` の delegated authoring 実装に対するユーザー補正と、複数 deep-consultant の分析結果を `iss-00127` の入力証跡として固定する。
- この文書は正本要件ではない。`requirement.md` / `design.md` / `plan.md` へ反映する前の調査・判断材料である。
- ここでいう `discussions/` は、対象 initiative / epic / issue の scope-local `discussions/` を指す。

## 調査目的 (必須)
- 現行 v2 の write-capable delegated draft authoring 実装が、ユーザーの意図した運用モデルとどこでずれているかを明らかにする。
- system-architect / implementation-planner が canonical `design.md` / `plan.md` を直接編集するべきか、scope-local `discussions/` に template-based draft を作るべきかを比較する。
- `iss-00127` で修正すべき最小契約、退役すべき過剰な権限機構、残すべき安全装置を整理する。

## 調査方法 (必須)
- ユーザー補正の要点を整理した。
  - canonical requirement/design/plan/report は main orchestrator が責任を持つ。
  - sub-agent は canonical 本体を直接編集しない。
  - sub-agent は対象 scope の `discussions/` 配下に、template-based draft requirement/design/plan や分析資料を作成できる。
  - `.agents` / `.codex` / cross-issue global directory に issue/epic ごとの draft を集約しない。
  - 現行の JSON authority / manifest / session-invocation / EAL 中心の契約は複雑すぎる可能性がある。
- deep-consultant 3 名に別観点で分析を依頼した。
  - Hubble: 要件・authority model。
  - Ohm: 実装・ファイル配置・Permission Profile・テスト。
  - Copernicus: workflow / dogfooding / UX / phase gate。
- 現行リポジトリの関連実装を確認した。
  - `.codex/agents/system-architect.toml`
  - `.codex/agents/implementation-planner.toml`
  - `.agents/skills/spec-dock-system-architect/SKILL.md`
  - `.agents/skills/spec-dock-implementation-planner/SKILL.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/delegated_authoring.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authority.py`
  - active issue `iss-00126` の `discussions/delegated-authoring/` 証跡

## 調査結果 (必須)
- deep-consultant 3 名の結論は一致した。
  - 改訂モデルを採用すべき。
  - sub-agent は canonical author ではなく、draft / analysis contributor として扱うべき。
  - canonical docs の direct writer は main orchestrator に限定すべき。
  - sub-agent output は対象 node の scope-local `discussions/` に閉じるべき。
  - 重い JSON authority / manifest / session-invocation / EAL を user-facing workflow contract の中心に置くのは過剰。
- 現行 v2 実装は、安全性を実行時 ACL / manifest / probe / hash に寄せすぎている。
  - `iss-00126` では `discussions/delegated-authoring/<task-id>/` に manifest / permission-profile / probe-plan / session-invocation / input-authority JSON が生成される。
  - 生成物は scope-local ではあるが、draft 文書そのものより権限検証の機械証跡が主役になっている。
  - system-architect / implementation-planner の skill と adapter には、条件付きで canonical `design.md` / `plan.md` を直接 draft 更新できる契約が残っている。
- ユーザー意図に近いモデルは、Discussion Draft Model である。
  - canonical authority: `requirement.md` / `design.md` / `plan.md` / `report.md`。
  - draft/evidence authority: 対象 scope の `discussions/` 配下。
  - promotion authority: main orchestrator が draft を読み、採用・部分採用・却下を判断し、canonical docs へ反映する。
  - validation / finish authority: canonical docs を基準に判定し、draft だけにある決定は未反映として扱う。
- draft は無規律にしてはいけない。
  - draft 冒頭に status、scope、scope_id、target canonical doc、author_role、based_on、promotion status を持たせる必要がある。
  - draft は create-only を原則にし、既存 draft の上書き・削除は main orchestrator の明示判断なしに行わない方がよい。
  - 子 issue の draft が epic-level decision を提案する場合は、親 epic の `discussions/` に synthesis draft を置くべき。
- `.agents` は agent 定義・skill・host adapter の置き場であり、issue / epic ごとの draft 成果物置き場ではない。
- `.codex/permission-probe-evidence` のような横断的 probe/evidence directory は、作業成果物の自然な置き場としては不適切である。

## 推測 / 未検証事項 (必須)
- 推測:
  - 現行の `domain/delegated_authoring.py` と `domain/authority.py` のすべてを即時削除する必要はない。内部安全装置として一部を path guard / diff guard に縮退できる可能性がある。
  - `spec-dock new doc` を拡張して `draft-requirement` / `draft-design` / `draft-plan` 相当の template-based discussion を作れるようにすると、workflow と実装が自然に揃う可能性が高い。
  - runtime helper を残す場合も、重い manifest ではなく `spec-dock discussion new --target <id> --role <role> --kind <draft-kind>` 程度の軽い helper で十分な可能性が高い。
- 未検証:
  - Codex Permission Profile で実行時に target `discussions/<run>/` だけを writable に絞る具体方式。
  - 既存 `iss-00126` 証跡を deprecated として残すか、新方針に合わせてどこまで整理するか。
  - `spec-dock validate` / `issue finish` が draft-only discussion の未反映判断をどこまで機械検出すべきか。
  - issue / epic / initiative すべてに共通する discussion draft template の最小 field set。

## 判断への含意 (必須)
- `iss-00127` は、現行 v2 を完成させる issue ではなく、v2 の過剰な write-capable canonical authoring モデルを scope-local discussion draft authoring へ修正する issue として扱う。
- requirement では、次を非交渉制約にするべき。
  - sub-agent は canonical `requirement.md` / `design.md` / `plan.md` / `report.md` を直接編集しない。
  - sub-agent は対象 node の `discussions/` 配下にだけ draft/evidence を作成・編集できる。
  - `.agents` / `.codex` / repo-wide global draft directory を issue/epic ごとの draft 置き場にしない。
  - main orchestrator が draft の採否と canonical 反映責任を持つ。
- design では、次の構造へ寄せるべき。
  - scoped discussion drafts + explicit promotion gate。
  - lightweight Markdown header。
  - path guard / diff guard。
  - provider asset と dogfooding copy の両方で role skill / adapter / docs を更新。
- plan では、次の順序が妥当である。
  1. canonical / discussion draft boundary を docs と skill に明記する。
  2. system-architect / implementation-planner から canonical edit 成功パスを削除する。
  3. discussion draft template と命名規則を追加する。
  4. Permission Profile / path policy を target `discussions/<run>/` write に単純化する。
  5. tests で canonical docs 非変更、target discussions 以外の変更拒否、global draft/evidence 非生成を固定する。
  6. 既存 `iss-00126` の重い証跡は historical / deprecated として残し、新規生成を止める。

## リスク/制約 (任意)
- draft が事実上の第二正本になるリスクがある。
  - 対策: validation / finish / review は canonical docs を基準にし、draft にしかない判断は未反映として扱う。
- discussions が増えて探索しにくくなるリスクがある。
  - 対策: 命名規則、最小 header、将来の `discussions list` / promote helper を検討する。
- Permission Profile を単純化しすぎると実行時安全境界が prompt-only になるリスクがある。
  - 対策: runtime ACL に頼りすぎず、実行後 diff guard と tests で forbidden path 変更を検出する。
- 既存 v2 実装の退役範囲を誤ると、現在の PR #119 の証跡や検証が読みにくくなる。
  - 対策: 既存証跡は削除せず、new issue で superseded / deprecated として整理する。

## 反映先 (任意)
- reflected_to:
  - `iss-00127/requirement.md`
  - `iss-00127/design.md`
  - `iss-00127/plan.md`
  - `epic-00112/report.md` if Epic-level corrective status needs update

## 参考（References） (任意)
- User correction discussion, 2026-05-24.
- Deep-consultant Hubble: requirements / authority model analysis.
- Deep-consultant Ohm: implementation / file layout / permission profile analysis.
- Deep-consultant Copernicus: workflow / dogfooding / phase gate analysis.
- Current implementation references:
  - `.codex/agents/system-architect.toml`
  - `.codex/agents/implementation-planner.toml`
  - `.agents/skills/spec-dock-system-architect/SKILL.md`
  - `.agents/skills/spec-dock-implementation-planner/SKILL.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/delegated_authoring.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authority.py`
