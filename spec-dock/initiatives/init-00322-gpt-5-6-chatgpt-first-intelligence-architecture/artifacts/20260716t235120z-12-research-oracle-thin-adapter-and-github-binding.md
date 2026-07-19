---
種別: research
ID: "20260716t235120z-12-research-oracle-thin-adapter-and-github-binding"
タイトル: "Oracle Thin Adapter／GitHub Exact Binding調査"
状態: "completed"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-16"
親: ["init-00322"]
関連:
  - "artifacts/20260716t235120z-06-interview-skill-agent-oracle-and-model-policy.md"
  - "artifacts/20260716t235120z-10-disc-skill-topology-and-global-cutover-rationale.md"
  - "artifacts/20260716t123423z-03-adr-thin-chatgpt-oracle-adapter-and-github-binding.md"
authority: "synthesized"
derived_from:
  - "source inspection performed during the ChatGPT interview"
  - "artifacts/20260716t054458z-disc-gpt56-chatgpt-delegation-vnext-decision-registry.md"
reflected_to:
  - "initiative/requirement.md"
  - "initiative/design.md"
  - "initiative/plan.md"
  - "artifacts/20260716t123423z-03-adr-thin-chatgpt-oracle-adapter-and-github-binding.md"
---

# 20260716t235120z-12-research-oracle-thin-adapter-and-github-binding Oracle Thin Adapter／GitHub Exact Binding調査

## 位置づけ

- このArtifactは、外部仕様・公開実装・現行repositoryの観測事実を、判断根拠として再利用できるよう整理する。
- 事実、推測、未検証事項、用語衝突、edge case、canonical文書への含意を分離する。
- 本文はsource-grounded evidenceであり、accepted ADRまたはcanonical三文書を上書きしない。

## 調査目的

- Oracleとローカル`chatgpt-use`の既存能力を再実装せず、SpecDockが所有すべきpreflight、prompt binding、output handoffの最小境界を明確にする。

## sources／調査方法

- 参照先:
  - `steipete/oracle` public repository
  - ユーザー提供のlocal `chatgpt-use` Skill
  - local `oracle-chatgpt` wrapper contract
  - Oracle session artifactの既知構造: `prompt.md`、`response.md`、`log.jsonl`、`artifacts/`
  - SpecDock PR #323 Workbench導入
- 検証手順:
  - wrapperが固定するengine、Project、model default、login profile、API禁止を確認した
  - Oracleへ委ねられるsession／reattach／artifact保存を整理した
  - GitHub Connector contextの自動注入とfallback挙動を確認した
  - SpecDock vNextのfail-closed exact branch／HEAD要件との差分を抽出した
- 実験条件:
  - Oracleはoperator-owned local toolとして扱う
  - SpecDockはOracle versionやprivate pathをproduct dependencyへ固定しない
  - 正式workflowはbrowser modeのみを使用する

## facts／観測できた事実

- local wrapperはOracleをbrowser modeへ固定し、API modeやprovider credential引き渡しを拒否する
- modelを明示しなければoperator-configured current Proを利用できる
- Oracleはsession status、reattach、render、response保存、downloadable artifactを既に所有する
- 長いpromptはfile添付と短い`-p`を組み合わせる契約がある
- local wrapperはcurrent repository／branchを検出してGitHub Connector contextを注入できる
- 現行wrapperのGitHub contextにはcurrent branch失敗時のdefault branch fallbackが含まれるが、vNext formal workflowではこれを許可しない
- Oracle output formはinline、Markdown file、ZIP／tree等で揺れ得る
- WorkbenchはGit非管理の候補／context置き場として既に利用可能

## inference／推測

- 事実から推測したこと:
  - `spec-dock-chatgpt`はOracleをさらに抽象化するbackend frameworkではなく、薄いdomain-specific adapterにすべき
  - SpecDockが所有するのはGit同期preflight、target path、exact repository／branch／HEAD、prompt composition、Oracle argvだけでよい
  - Oracle sessionの既存artifactを正本として使い、wrapper独自result／log copy／manifestを作る必要はない
  - Formal workflowではdefault branch fallbackを無効にし、exact branch／SHA未確認ならfail closedにする必要がある
  - 出力variationへの対応はRuntime合成ではなくCodexの通常file操作でcanonical pathへcopyするのが単純
- 推測の根拠:
  - 上記factsと、Current Effective Decision Snapshotで承認済みのauthority／YAGNI原則を組み合わせた。
  - 推測はexact implementationを固定せず、Epic Planningで再検証する前提である。

## unverified／未検証事項

- まだ確認していないこと:
  - ChatGPT UIでplain-text `@GitHub`が常にConnector起動へ結び付くか
  - exact HEAD SHAをChatGPT側が安定して表示・確認できるか
  - GPT-5.6 Proがcomplete Markdown file／Protocol JSONをどの程度安定してdownloadable artifactとして返すか
  - Oracleの将来versionでsession artifact pathやmodel labelが変わる可能性
- 確認できない理由:
  - browser／hosted service／operator environmentに依存する挙動、または実装Epicで初めて作られるsurfaceであるため。
  - 未検証事項を事実としてcanonical文書へ昇格させない。

## question candidates／質問候補

- source-groundedに解けず、人間判断が必要な候補:
  - なし。thin adapterとfail-closedは承認済み
- pressure-test questionとして切り出すべき候補:
  - live smokeでGitHub Connector未起動時に明確なfailure outputを返せるか
- 質問せずに解決できた候補:
  - Oracle API fallbackは使わない
  - follow-upを正式workflowのdefaultにしない
  - tracked repository fileを自動添付しない
  - Oracle障害時に旧Codex-only Planningへ戻らない

## terminology conflicts／用語衝突

- `wrapper`:
  - local `chatgpt-use` wrapperはoperator tool
  - `spec-dock-chatgpt`はSpecDock domain adapter
  - 両者を一つのproduct-owned runtimeへ統合しない
- `output`:
  - Oracle session artifactがprovider／browser実行記録
  - canonical fileはCodexが採用後にrepositoryへ配置
- `GitHub synced`:
  - local HEADとremote HEADの一致だけでなくChatGPT Connector側のexact repository／branch／HEAD確認を含む

## edge cases／具体シナリオ

- Oracle timeout／disconnect:
  - 同一promptを即再実行せずstatus／session render／reattachを確認する
- GitHub branchがConnectorから見えない:
  - default branchへfallbackせずformal taskを拒否する
- outputがZIP:
  - 既存ZIP safety laneまたは通常file inspectionで識別し、text合成Runtimeを作らない
- Oracleが長期間利用不能:
  - 人間copy/pasteまたは別browserで同じprompt／output contractを維持する

## implications／判断への含意

- `requirement.md`:
  - browser-only、exact GitHub binding、Human Relay、変更容易性
- `design.md`:
  - thin adapter、Oracle responsibility、preflight、output discovery
- `plan.md`:
  - Epic 1とEpic 7のlive smoke
- `ADR`:
  - Thin ChatGPT Oracle Adapter and GitHub Binding

## リスク／制約

- Oracle private local pathやversionをSpecDock product contractへ埋め込まない
- UI selectorやmodel labelへ過度に結合しない
- Connector確認前に添付やmemoryだけで回答させない

## 反映先

- reflected_to:
  - initiative/requirement.md
  - initiative/design.md
  - initiative/plan.md
  - artifacts/20260716t123423z-03-adr-thin-chatgpt-oracle-adapter-and-github-binding.md

## 参考

- `steipete/oracle` public repository
- ユーザー提供のlocal `chatgpt-use` Skill
- local `oracle-chatgpt` wrapper contract
- Oracle session artifactの既知構造: `prompt.md`、`response.md`、`log.jsonl`、`artifacts/`
- SpecDock PR #323 Workbench導入
