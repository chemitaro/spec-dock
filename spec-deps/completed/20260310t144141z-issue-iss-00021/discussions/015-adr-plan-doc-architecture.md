---
種別: ADR（Architecture Decision Record）
ID: "015-adr-plan-doc-architecture"
タイトル: "plan 文書体系の責務分離"
状態: "accepted"
作成者: "Codex"
最終更新: "2026-03-10"
親: ["iss-00021"]
---

# 015-adr plan 文書体系の責務分離

## 結論（Decision） (必須)
- `phase_plan.md` は shared axiom のみを持つ。
- `phase_plan_<scope>.md` は scope ごとの plan authoring rule の正本とする。
- `workflow_<scope>.md` は lifecycle / governance / policy の正本とする。
- `templates/<scope>/plan.md` は output schema の正本とし、運用ルールや長い説明は持たせない。
- shared に固定する plan 軸は `target / decomposition / sequence / gate / dependency / exit` の 6 つとする。

## 背景（Context） (必須)
- `plan` 関連文書には、shared な執筆規約、scope 固有の gate、lifecycle、template の器が混在しやすく、同じ論点が複数文書へ重複しやすかった。
- とくに `phase_plan.md` が shared と issue 固有の意味論を併せ持つと、initiative / epic / issue の読者にとって責務境界が曖昧になる。
- 今回の再設計では、LLM / coding agent が最短で正本へ到達でき、かつ drift を防げる構成を固定する必要があった。
- 本 ADR は一時検討資料 `002 / 003 / 009 / 010 / 011 / 012 / 014` の結論を統合した恒久判断である。

## 選択肢（Options considered） (必須)
- Option A:
  - 概要:
    - `phase_plan.md` を shared のまま厚く保ち、scope 差分は template や workflow 側で吸収する。
  - Pros:
    - 文書数が少なく見える。
    - shared doc だけ読めば一見わかりやすい。
  - Cons:
    - issue 固有の execution semantics が shared に混入する。
    - workflow / template と責務が重なりやすい。
    - scope ごとの差分が見えにくい。
  - 棄却理由（棄却する場合）:
    - drift と誤読のコストが高く、長期運用に向かない。
- Option B:
  - 概要:
    - `plan` を 4 層に分け、shared axiom / scope-specific playbook / workflow / template を明示分離する。
  - Pros:
    - 正本の所在が明確になる。
    - shared と scope 固有の責務が分離される。
    - template を軽く保ったまま、plan の意味論を強くできる。
  - Cons:
    - 文書数は増える。
    - 導線設計が弱いと参照先が増えて見える。
  - 棄却理由（棄却する場合）:
    - 採用。

## 判断理由（Rationale） (必須)
- `plan` で恒久的に残したいのは「どの文書が何を正本として持つか」であり、個別の検討過程ではない。
- shared は最小の共通契約だけを持ち、scope 固有の粒度や gate は `phase_plan_<scope>.md` に逃がす方が、initiative / epic / issue の三者を一貫して扱いやすい。
- lifecycle / governance / execution policy は workflow に置き、template は出力 schema に徹することで、同じルールの再説明を防げる。

## 影響（Consequences） (必須)
- Positive（良い点）:
  - `plan` の責務境界が固定され、どこを読めばよいかが明確になる。
  - shared doc の肥大化を防げる。
  - template を軽量化しつつ、scope 別の authoring quality を上げられる。
- Negative / Debt（悪い点 / 将来負債）:
  - 文書間リンクや導線が弱いと分散して見える。
  - scope 別 playbook と workflow の重複監視は継続的に必要。
- 影響範囲（コード/テスト/運用/データ）:
  - `src/spec_dock/assets/spec_dock/docs/phase_plan.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_initiative.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_epic.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_*.md`
  - `src/spec_dock/assets/spec_dock/templates/*/plan.md`
- 移行/ロールバック:
  - 今後 `plan` の責務を再変更する場合は、この ADR を supersede する新 ADR で扱う。
- Follow-ups（追加の Epic/Issue/ADR）:
  - scope 別 playbook と workflow の責務重複が再発した場合は follow-up issue で調整する。

## 参考（References） (任意)
- 関連仕様（requirement/design/plan/report）:
  - `src/spec_dock/assets/spec_dock/docs/phase_plan.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_initiative.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_epic.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
- PR/実装:
  - `#22`
- 外部資料:
  - `009-disc-plan-playbook-scope-splitting-analysis.md`
  - `010-disc-phase-plan-shrink-proposal.md`
  - `011-disc-scope-specific-plan-playbook-drafts.md`
  - `012-disc-plan-playbook-responsibility-redistribution.md`
  - `014-disc-issue-plan-tdd-production-change-proposal.md`
